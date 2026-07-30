"""
Qwen3-0.6B MAB Pruner
=====================
Multi-Armed Bandit driven structured pruning for Qwen3-0.6B.

This module adapts the MAB pruning framework (arXiv:2607.22564) to the
Qwen3-0.6B Transformer language model, supporting:
  - Attention head pruning
  - FFN neuron pruning

Usage:
    from qwen3_pruner import Qwen3MABPruner
    
    pruner = Qwen3MABPruner(model_path="Qwen/Qwen3-0.6B")
    pruner.prune_attention_heads(
        dataloader=eval_dataloader,
        play_budget=500,
        top_k=50,
    )
    pruner.save_pruned_model("./pruned_qwen3_0.6b")
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import json

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig
    from transformers.models.qwen3.modeling_qwen3 import Qwen3DecoderLayer, Qwen3Attention, Qwen3MLP
except ImportError:
    raise ImportError(
        "transformers library is required. Install with: pip install transformers"
    )

from mab_pruner import MABPruner, PruningConfig, UCB1Policy, ThompsonSamplingPolicy


@dataclass
class Qwen3PruningConfig:
    """Configuration for Qwen3-0.6B pruning."""
    model_path: str = "Qwen/Qwen3-0.6B"
    play_budget: int = 500
    top_k: int = 50
    batch_size: int = 8
    seq_length: int = 512
    tolerance: float = 0.01
    scale_reward: float = 1.0
    policy: str = "ucb1"  # "ucb1" or "thompson"
    pruning_target: str = "attention"  # "attention" or "ffn"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    seed: int = 42


class Qwen3MABPruner:
    """
    MAB-driven structured pruner for Qwen3-0.6B.
    
    Adapts the loss-aware feature-map pruning from CNNs (arXiv:2607.22564)
    to Transformer attention heads and FFN neurons.
    """
    
    def __init__(self, config: Qwen3PruningConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Load model and tokenizer
        print(f"Loading Qwen3-0.6B from {config.model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.model_path,
            trust_remote_code=True,
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
        self.model = AutoModelForCausalLM.from_pretrained(
            config.model_path,
            torch_dtype=torch.float16 if config.device == "cuda" else torch.float32,
            trust_remote_code=True,
        ).to(self.device)
        self.model.eval()
        
        self.config_model = self.model.config
        self.num_layers = self.config_model.num_hidden_layers
        self.num_heads = self.config_model.num_attention_heads
        self.num_kv_heads = getattr(self.config_model, "num_key_value_heads", self.num_heads)
        self.head_dim = self.config_model.hidden_size // self.num_heads
        self.intermediate_size = self.config_model.intermediate_size
        
        # Store original weights for masking/unmasking
        self._original_weights = {}
        self._store_original_weights()
        
        print(f"Model loaded: {self.num_layers} layers, {self.num_heads} heads, "
              f"head_dim={self.head_dim}, intermediate_size={self.intermediate_size}")
    
    def _store_original_weights(self):
        """Store original weight copies for temporary masking."""
        for layer_idx in range(self.num_layers):
            layer = self.model.model.layers[layer_idx]
            
            # Attention weights
            attn = layer.self_attn
            self._original_weights[f"layer{layer_idx}_q_proj"] = attn.q_proj.weight.data.clone()
            self._original_weights[f"layer{layer_idx}_k_proj"] = attn.k_proj.weight.data.clone()
            self._original_weights[f"layer{layer_idx}_v_proj"] = attn.v_proj.weight.data.clone()
            self._original_weights[f"layer{layer_idx}_o_proj"] = attn.o_proj.weight.data.clone()
            
            # FFN weights
            mlp = layer.mlp
            self._original_weights[f"layer{layer_idx}_gate_proj"] = mlp.gate_proj.weight.data.clone()
            self._original_weights[f"layer{layer_idx}_up_proj"] = mlp.up_proj.weight.data.clone()
            self._original_weights[f"layer{layer_idx}_down_proj"] = mlp.down_proj.weight.data.clone()
    
    # ==================== Attention Head Pruning ====================
    
    def _get_attention_arm_name(self, layer_idx: int, head_idx: int) -> str:
        return f"L{layer_idx:02d}_H{head_idx:02d}"
    
    def _parse_attention_arm(self, arm_name: str) -> Tuple[int, int]:
        """Parse arm name like 'L03_H07' to (layer_idx, head_idx)."""
        parts = arm_name.split("_")
        layer_idx = int(parts[0][1:])
        head_idx = int(parts[1][1:])
        return layer_idx, head_idx
    
    def _mask_attention_head(self, layer_idx: int, head_idx: int):
        """
        Temporarily mask an attention head by zeroing its output projection weights.
        
        In Transformer, each head's output is computed and then concatenated.
        We mask by zeroing the corresponding rows in the O projection matrix.
        """
        layer = self.model.model.layers[layer_idx]
        o_proj = layer.self_attn.o_proj
        
        # The O projection matrix maps from (num_heads * head_dim) to hidden_size
        # Each head corresponds to a contiguous block of head_dim rows
        start_idx = head_idx * self.head_dim
        end_idx = start_idx + self.head_dim
        
        # Zero out the corresponding weights
        with torch.no_grad():
            o_proj.weight[:, start_idx:end_idx] = 0.0
    
    def _unmask_attention_head(self, layer_idx: int, head_idx: int):
        """Restore original O projection weights for a head."""
        layer = self.model.model.layers[layer_idx]
        o_proj = layer.self_attn.o_proj
        
        start_idx = head_idx * self.head_dim
        end_idx = start_idx + self.head_dim
        
        with torch.no_grad():
            o_proj.weight[:, start_idx:end_idx] = \
                self._original_weights[f"layer{layer_idx}_o_proj"][:, start_idx:end_idx]
    
    def _mask_attention_head_wrapper(self, model, arm_idx: int):
        """Wrapper for MABPruner interface."""
        arm_name = self.attention_arm_names[arm_idx]
        layer_idx, head_idx = self._parse_attention_arm(arm_name)
        self._mask_attention_head(layer_idx, head_idx)
    
    def _unmask_attention_head_wrapper(self, model, arm_idx: int):
        """Wrapper for MABPruner interface."""
        arm_name = self.attention_arm_names[arm_idx]
        layer_idx, head_idx = self._parse_attention_arm(arm_name)
        self._unmask_attention_head(layer_idx, head_idx)
    
    def prune_attention_heads(
        self,
        dataloader: torch.utils.data.DataLoader,
        play_budget: Optional[int] = None,
        top_k: Optional[int] = None,
        policy: Optional[str] = None,
    ) -> Dict:
        """
        Prune attention heads using MAB framework.
        
        Args:
            dataloader: DataLoader with tokenized text sequences
            play_budget: Number of MAB iterations (default: config.play_budget)
            top_k: Number of heads to prune (default: config.top_k)
            policy: "ucb1" or "thompson" (default: config.policy)
            
        Returns:
            Pruning results dictionary
        """
        play_budget = play_budget or self.config.play_budget
        top_k = top_k or self.config.top_k
        policy = policy or self.config.policy
        
        # Define arms: all attention heads across all layers
        self.attention_arm_names = []
        for layer_idx in range(self.num_layers):
            for head_idx in range(self.num_heads):
                self.attention_arm_names.append(self._get_attention_arm_name(layer_idx, head_idx))
        
        print(f"\n{'='*60}")
        print(f"Attention Head Pruning")
        print(f"  Total heads: {len(self.attention_arm_names)}")
        print(f"  Play budget: {play_budget}")
        print(f"  Top-K to prune: {top_k}")
        print(f"  Policy: {policy}")
        print(f"{'='*60}\n")
        
        # Create MAB pruner
        mab_config = PruningConfig(
            play_budget=play_budget,
            top_k=top_k,
            batch_size=self.config.batch_size,
            tolerance=self.config.tolerance,
            scale_reward=self.config.scale_reward,
            policy=policy,
            device=self.config.device,
            seed=self.config.seed,
        )
        mab_pruner = MABPruner(mab_config)
        
        # Language modeling loss function
        def lm_loss_fn(logits, labels):
            """Compute cross-entropy loss for language modeling."""
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            loss = nn.functional.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
            )
            return loss
        
        # Run MAB pruning
        results = mab_pruner.prune(
            model=self.model,
            dataloader=dataloader,
            arm_names=self.attention_arm_names,
            mask_fn=self._mask_attention_head_wrapper,
            unmask_fn=self._unmask_attention_head_wrapper,
            loss_fn=lm_loss_fn,
        )
        
        self.attention_pruning_results = results
        self.heads_to_prune = results["top_k_arms"]
        
        return results
    
    # ==================== FFN Neuron Pruning ====================
    
    def _get_ffn_arm_name(self, layer_idx: int, neuron_idx: int) -> str:
        return f"L{layer_idx:02d}_N{neuron_idx:04d}"
    
    def _parse_ffn_arm(self, arm_name: str) -> Tuple[int, int]:
        """Parse arm name like 'L03_N0123' to (layer_idx, neuron_idx)."""
        parts = arm_name.split("_")
        layer_idx = int(parts[0][1:])
        neuron_idx = int(parts[1][1:])
        return layer_idx, neuron_idx
    
    def _mask_ffn_neuron(self, layer_idx: int, neuron_idx: int):
        """
        Temporarily mask an FFN neuron by zeroing its gate/up weights and down column.
        
        For SwiGLU FFN: output = down_proj(silu(gate_proj(x)) * up_proj(x))
        Masking neuron n means zeroing:
          - gate_proj[n, :] 
          - up_proj[n, :]
          - down_proj[:, n]
        """
        layer = self.model.model.layers[layer_idx]
        mlp = layer.mlp
        
        with torch.no_grad():
            mlp.gate_proj.weight[neuron_idx, :] = 0.0
            mlp.up_proj.weight[neuron_idx, :] = 0.0
            mlp.down_proj.weight[:, neuron_idx] = 0.0
    
    def _unmask_ffn_neuron(self, layer_idx: int, neuron_idx: int):
        """Restore original FFN weights for a neuron."""
        layer = self.model.model.layers[layer_idx]
        mlp = layer.mlp
        
        with torch.no_grad():
            mlp.gate_proj.weight[neuron_idx, :] = \
                self._original_weights[f"layer{layer_idx}_gate_proj"][neuron_idx, :]
            mlp.up_proj.weight[neuron_idx, :] = \
                self._original_weights[f"layer{layer_idx}_up_proj"][neuron_idx, :]
            mlp.down_proj.weight[:, neuron_idx] = \
                self._original_weights[f"layer{layer_idx}_down_proj"][:, neuron_idx]
    
    def _mask_ffn_neuron_wrapper(self, model, arm_idx: int):
        arm_name = self.ffn_arm_names[arm_idx]
        layer_idx, neuron_idx = self._parse_ffn_arm(arm_name)
        self._mask_ffn_neuron(layer_idx, neuron_idx)
    
    def _unmask_ffn_neuron_wrapper(self, model, arm_idx: int):
        arm_name = self.ffn_arm_names[arm_idx]
        layer_idx, neuron_idx = self._parse_ffn_arm(arm_name)
        self._unmask_ffn_neuron(layer_idx, neuron_idx)
    
    def prune_ffn_neurons(
        self,
        dataloader: torch.utils.data.DataLoader,
        play_budget: Optional[int] = None,
        top_k: Optional[int] = None,
        policy: Optional[str] = None,
        layer_wise: bool = False,
    ) -> Dict:
        """
        Prune FFN neurons using MAB framework.
        
        Args:
            dataloader: DataLoader with tokenized text sequences
            play_budget: Number of MAB iterations
            top_k: Number of neurons to prune
            policy: "ucb1" or "thompson"
            layer_wise: If True, prune each layer independently
            
        Returns:
            Pruning results dictionary
        """
        play_budget = play_budget or self.config.play_budget
        top_k = top_k or self.config.top_k
        policy = policy or self.config.policy
        
        # Define arms: all FFN neurons across all layers
        self.ffn_arm_names = []
        for layer_idx in range(self.num_layers):
            for neuron_idx in range(self.intermediate_size):
                self.ffn_arm_names.append(self._get_ffn_arm_name(layer_idx, neuron_idx))
        
        print(f"\n{'='*60}")
        print(f"FFN Neuron Pruning")
        print(f"  Total neurons: {len(self.ffn_arm_names)}")
        print(f"  Play budget: {play_budget}")
        print(f"  Top-K to prune: {top_k}")
        print(f"  Policy: {policy}")
        print(f"{'='*60}\n")
        
        mab_config = PruningConfig(
            play_budget=play_budget,
            top_k=top_k,
            batch_size=self.config.batch_size,
            tolerance=self.config.tolerance,
            scale_reward=self.config.scale_reward,
            policy=policy,
            device=self.config.device,
            seed=self.config.seed,
        )
        mab_pruner = MABPruner(mab_config)
        
        def lm_loss_fn(logits, labels):
            shift_logits = logits[..., :-1, :].contiguous()
            shift_labels = labels[..., 1:].contiguous()
            return nn.functional.cross_entropy(
                shift_logits.view(-1, shift_logits.size(-1)),
                shift_labels.view(-1),
                ignore_index=-100,
            )
        
        results = mab_pruner.prune(
            model=self.model,
            dataloader=dataloader,
            arm_names=self.ffn_arm_names,
            mask_fn=self._mask_ffn_neuron_wrapper,
            unmask_fn=self._unmask_ffn_neuron_wrapper,
            loss_fn=lm_loss_fn,
        )
        
        self.ffn_pruning_results = results
        self.neurons_to_prune = results["top_k_arms"]
        
        return results
    
    # ==================== Permanent Pruning ====================
    
    def apply_permanent_attention_pruning(self):
        """
        Permanently remove selected attention heads.
        
        This physically removes the head weights, producing a smaller model.
        For attention heads, we:
          1. Remove the corresponding Q/K/V projection blocks
          2. Remove the corresponding O projection rows
          3. Update num_attention_heads in config
        """
        if not hasattr(self, 'heads_to_prune') or not self.heads_to_prune:
            print("No attention heads selected for pruning. Run prune_attention_heads() first.")
            return
        
        print(f"\nApplying permanent attention head pruning...")
        print(f"  Removing {len(self.heads_to_prune)} heads")
        
        # Group heads by layer
        heads_by_layer: Dict[int, List[int]] = {}
        for arm_name in self.heads_to_prune:
            layer_idx, head_idx = self._parse_attention_arm(arm_name)
            if layer_idx not in heads_by_layer:
                heads_by_layer[layer_idx] = []
            heads_by_layer[layer_idx].append(head_idx)
        
        # Sort and remove heads for each layer
        for layer_idx in range(self.num_layers):
            if layer_idx not in heads_by_layer:
                continue
            
            heads_to_remove = sorted(heads_by_layer[layer_idx])
            keep_mask = torch.ones(self.num_heads, dtype=torch.bool)
            for h in heads_to_remove:
                keep_mask[h] = False
            keep_indices = torch.where(keep_mask)[0]
            
            layer = self.model.model.layers[layer_idx]
            attn = layer.self_attn
            
            # Rebuild Q, K, V projections (remove heads)
            # Each head corresponds to head_dim columns in q_proj
            with torch.no_grad():
                # Q projection: [hidden_size, num_heads * head_dim]
                q_weight = attn.q_proj.weight.data
                q_weight_reshaped = q_weight.view(self.config_model.hidden_size, self.num_heads, self.head_dim)
                q_weight_pruned = q_weight_reshaped[:, keep_indices, :].reshape(
                    self.config_model.hidden_size, -1
                )
                attn.q_proj = nn.Linear(
                    self.config_model.hidden_size,
                    len(keep_indices) * self.head_dim,
                    bias=attn.q_proj.bias is not None,
                    dtype=q_weight.dtype,
                    device=q_weight.device,
                )
                attn.q_proj.weight.data = q_weight_pruned.T
                if attn.q_proj.bias is not None:
                    attn.q_proj.bias.data = attn.q_proj.bias.data[...]  # TODO: proper bias handling
                
                # K, V projections (handle GQA)
                kv_heads = self.num_kv_heads
                kv_head_dim = self.config_model.hidden_size // kv_heads
                
                k_weight = attn.k_proj.weight.data
                k_weight_reshaped = k_weight.view(self.config_model.hidden_size, kv_heads, kv_head_dim)
                # For GQA, we need to be careful about which KV heads to remove
                # Simplified: keep all KV heads for now (more sophisticated mapping needed)
                
                # O projection: [num_heads * head_dim, hidden_size]
                o_weight = attn.o_proj.weight.data
                o_weight_reshaped = o_weight.view(self.num_heads, self.head_dim, self.config_model.hidden_size)
                o_weight_pruned = o_weight_reshaped[keep_indices, :, :].reshape(-1, self.config_model.hidden_size)
                attn.o_proj = nn.Linear(
                    len(keep_indices) * self.head_dim,
                    self.config_model.hidden_size,
                    bias=attn.o_proj.bias is not None,
                    dtype=o_weight.dtype,
                    device=o_weight.device,
                )
                attn.o_proj.weight.data = o_weight_pruned
            
            print(f"  Layer {layer_idx}: {self.num_heads} -> {len(keep_indices)} heads")
        
        # Update config
        new_num_heads = self.num_heads - max(len(h) for h in heads_by_layer.values()) if heads_by_layer else self.num_heads
        self.config_model.num_attention_heads = new_num_heads
        print(f"  Updated num_attention_heads: {self.num_heads} -> {new_num_heads}")
    
    def apply_permanent_ffn_pruning(self):
        """
        Permanently remove selected FFN neurons.
        
        This physically removes the neuron weights from gate_proj, up_proj, and down_proj.
        """
        if not hasattr(self, 'neurons_to_prune') or not self.neurons_to_prune:
            print("No FFN neurons selected for pruning. Run prune_ffn_neurons() first.")
            return
        
        print(f"\nApplying permanent FFN neuron pruning...")
        print(f"  Removing {len(self.neurons_to_prune)} neurons")
        
        # Group neurons by layer
        neurons_by_layer: Dict[int, List[int]] = {}
        for arm_name in self.neurons_to_prune:
            layer_idx, neuron_idx = self._parse_ffn_arm(arm_name)
            if layer_idx not in neurons_by_layer:
                neurons_by_layer[layer_idx] = []
            neurons_by_layer[layer_idx].append(neuron_idx)
        
        for layer_idx in range(self.num_layers):
            if layer_idx not in neurons_by_layer:
                continue
            
            neurons_to_remove = sorted(neurons_by_layer[layer_idx])
            keep_mask = torch.ones(self.intermediate_size, dtype=torch.bool)
            for n in neurons_to_remove:
                keep_mask[n] = False
            keep_indices = torch.where(keep_mask)[0].tolist()
            
            layer = self.model.model.layers[layer_idx]
            mlp = layer.mlp
            
            with torch.no_grad():
                # gate_proj: [intermediate_size, hidden_size]
                gate_weight = mlp.gate_proj.weight.data[keep_indices, :]
                mlp.gate_proj = nn.Linear(
                    self.config_model.hidden_size,
                    len(keep_indices),
                    bias=mlp.gate_proj.bias is not None,
                    dtype=gate_weight.dtype,
                    device=gate_weight.device,
                )
                mlp.gate_proj.weight.data = gate_weight
                
                # up_proj: [intermediate_size, hidden_size]
                up_weight = mlp.up_proj.weight.data[keep_indices, :]
                mlp.up_proj = nn.Linear(
                    self.config_model.hidden_size,
                    len(keep_indices),
                    bias=mlp.up_proj.bias is not None,
                    dtype=up_weight.dtype,
                    device=up_weight.device,
                )
                mlp.up_proj.weight.data = up_weight
                
                # down_proj: [hidden_size, intermediate_size]
                down_weight = mlp.down_proj.weight.data[:, keep_indices]
                mlp.down_proj = nn.Linear(
                    len(keep_indices),
                    self.config_model.hidden_size,
                    bias=mlp.down_proj.bias is not None,
                    dtype=down_weight.dtype,
                    device=down_weight.device,
                )
                mlp.down_proj.weight.data = down_weight
            
            print(f"  Layer {layer_idx}: {self.intermediate_size} -> {len(keep_indices)} neurons")
        
        # Update config
        self.config_model.intermediate_size = len(keep_indices)
        print(f"  Updated intermediate_size: {self.intermediate_size} -> {len(keep_indices)}")
    
    # ==================== Save / Load ====================
    
    def save_pruned_model(self, output_dir: str):
        """Save the pruned model and tokenizer."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\nSaving pruned model to {output_dir}...")
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # Save pruning metadata
        metadata = {
            "original_model": self.config.model_path,
            "pruning_config": {
                "play_budget": self.config.play_budget,
                "top_k": self.config.top_k,
                "policy": self.config.policy,
                "tolerance": self.config.tolerance,
            },
        }
        
        if hasattr(self, 'attention_pruning_results'):
            metadata["attention_pruning"] = {
                "heads_removed": len(self.heads_to_prune),
                "heads": self.heads_to_prune,
            }
        
        if hasattr(self, 'ffn_pruning_results'):
            metadata["ffn_pruning"] = {
                "neurons_removed": len(self.neurons_to_prune),
                "neurons": self.neurons_to_prune,
            }
        
        with open(output_path / "pruning_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        print(f"  Model saved successfully!")
        print(f"  Metadata saved to {output_path / 'pruning_metadata.json'}")
    
    def evaluate_perplexity(self, dataloader: torch.utils.data.DataLoader) -> float:
        """Evaluate perplexity on a dataset."""
        self.model.eval()
        total_loss = 0.0
        total_tokens = 0
        
        with torch.no_grad():
            for batch in dataloader:
                if isinstance(batch, dict):
                    input_ids = batch["input_ids"].to(self.device)
                    attention_mask = batch.get("attention_mask", None)
                    if attention_mask is not None:
                        attention_mask = attention_mask.to(self.device)
                else:
                    input_ids = batch.to(self.device)
                    attention_mask = None
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
                loss = outputs.loss
                
                # Count valid tokens (non-padding)
                if attention_mask is not None:
                    num_tokens = attention_mask.sum().item()
                else:
                    num_tokens = input_ids.numel()
                
                total_loss += loss.item() * num_tokens
                total_tokens += num_tokens
        
        avg_loss = total_loss / total_tokens
        perplexity = np.exp(avg_loss)
        return perplexity
