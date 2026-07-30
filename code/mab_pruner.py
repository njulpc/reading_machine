"""
MAB Pruner Core Framework
=========================
Core implementation of Multi-Armed Bandit driven structured pruning.
Adapted from: arXiv:2607.22564
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple, Dict, Callable, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
import copy


@dataclass
class PruningConfig:
    """Configuration for MAB-based pruning."""
    play_budget: int = 1000              # Total number of MAB iterations (T)
    top_k: int = 100                     # Number of arms to permanently prune
    batch_size: int = 32                 # Mini-batch size for evaluation
    tolerance: float = 0.01              # Reward tolerance parameter (tau)
    scale_reward: float = 1.0            # Reward scaling constant (sr)
    policy: str = "ucb1"                 # "ucb1" or "thompson"
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    seed: int = 42


class BanditPolicy(ABC):
    """Abstract base class for bandit policies."""
    
    def __init__(self, num_arms: int):
        self.num_arms = num_arms
    
    @abstractmethod
    def select_arm(self) -> int:
        """Select the next arm to evaluate."""
        pass
    
    @abstractmethod
    def update(self, arm: int, reward: float):
        """Update the policy after observing a reward."""
        pass
    
    @abstractmethod
    def get_scores(self) -> np.ndarray:
        """Get final safe-removal scores for all arms."""
        pass


class UCB1Policy(BanditPolicy):
    """UCB1 policy for feature-map pruning."""
    
    def __init__(self, num_arms: int):
        super().__init__(num_arms)
        self.counts = np.zeros(num_arms, dtype=np.int64)
        self.values = np.zeros(num_arms, dtype=np.float64)
        self.t = 0
    
    def select_arm(self) -> int:
        self.t += 1
        
        # First, ensure every arm is played at least once
        unplayed = np.where(self.counts == 0)[0]
        if len(unplayed) > 0:
            return unplayed[0]
        
        # UCB1 formula: value + sqrt(2 * ln(t) / count)
        exploration = np.sqrt(2 * np.log(self.t) / self.counts)
        ucb_scores = self.values + exploration
        return int(np.argmax(ucb_scores))
    
    def update(self, arm: int, reward: float):
        self.counts[arm] += 1
        n = self.counts[arm]
        # Incremental mean update
        self.values[arm] += (reward - self.values[arm]) / n
    
    def get_scores(self) -> np.ndarray:
        # Final safe-removal score is the empirical mean reward
        return self.values.copy()


class ThompsonSamplingPolicy(BanditPolicy):
    """Thompson Sampling policy with Beta posterior."""
    
    def __init__(self, num_arms: int):
        super().__init__(num_arms)
        # Beta(1, 1) uniform prior
        self.alpha = np.ones(num_arms, dtype=np.float64)
        self.beta = np.ones(num_arms, dtype=np.float64)
    
    def select_arm(self) -> int:
        # Sample from posterior for each arm
        samples = np.random.beta(self.alpha, self.beta)
        return int(np.argmax(samples))
    
    def update(self, arm: int, reward: float):
        # Binary reward
        if reward >= 0.5:
            self.alpha[arm] += 1
        else:
            self.beta[arm] += 1
    
    def get_scores(self) -> np.ndarray:
        # Posterior mean as final safe-removal score
        return self.alpha / (self.alpha + self.beta)


class MABPruner:
    """
    Multi-Armed Bandit driven structured pruning.
    
    This class implements the core MAB pruning framework from the paper,
    generalized to work with any neural network architecture.
    """
    
    def __init__(self, config: PruningConfig):
        self.config = config
        torch.manual_seed(config.seed)
        np.random.seed(config.seed)
    
    def compute_reward(self, loss_original: float, loss_masked: float) -> float:
        """
        Compute reward from loss change.
        
        Args:
            loss_original: Loss of the unmasked model
            loss_masked: Loss of the masked model
            
        Returns:
            Bounded reward in [0, 1]
        """
        delta = loss_original - loss_masked  # Positive = masking reduces loss (good for pruning)
        
        if self.config.policy == "ucb1":
            # Bounded reward with tolerance
            reward = self.config.tolerance + delta / self.config.scale_reward
            return float(np.clip(reward, 0.0, 1.0))
        else:  # thompson
            # Binary reward
            return 1.0 if delta + self.config.tolerance >= 0 else 0.0
    
    def prune(
        self,
        model: nn.Module,
        dataloader: torch.utils.data.DataLoader,
        arm_names: List[str],
        mask_fn: Callable[[nn.Module, int], None],
        unmask_fn: Callable[[nn.Module, int], None],
        loss_fn: Optional[Callable] = None,
    ) -> Dict:
        """
        Perform MAB-driven pruning.
        
        Args:
            model: The neural network to prune
            dataloader: DataLoader for evaluation
            arm_names: List of arm identifiers (e.g., ["layer0_head0", ...])
            mask_fn: Function to temporarily mask an arm (model, arm_idx) -> None
            unmask_fn: Function to unmask an arm (model, arm_idx) -> None
            loss_fn: Optional custom loss function. Defaults to cross-entropy.
            
        Returns:
            Dictionary with pruning results
        """
        model.eval()
        num_arms = len(arm_names)
        
        # Initialize policy
        if self.config.policy == "ucb1":
            policy = UCB1Policy(num_arms)
        elif self.config.policy == "thompson":
            policy = ThompsonSamplingPolicy(num_arms)
        else:
            raise ValueError(f"Unknown policy: {self.config.policy}")
        
        # Default loss function
        if loss_fn is None:
            loss_fn = nn.CrossEntropyLoss()
        
        print(f"Starting MAB pruning with {self.config.policy.upper()} policy")
        print(f"  Arms: {num_arms}, Budget: {self.config.play_budget}, Top-K: {self.config.top_k}")
        
        # MAB Search Phase
        for t in range(self.config.play_budget):
            # Select arm
            arm_idx = policy.select_arm()
            
            # Sample mini-batch
            batch = next(iter(dataloader))
            if isinstance(batch, (list, tuple)):
                inputs, labels = batch
                inputs = inputs.to(self.config.device)
                labels = labels.to(self.config.device)
            else:
                inputs = batch.to(self.config.device)
                labels = None
            
            # Compute original loss
            with torch.no_grad():
                outputs = model(inputs)
                if labels is not None:
                    loss_original = loss_fn(outputs, labels).item()
                else:
                    loss_original = outputs.mean().item()
            
            # Mask selected arm
            mask_fn(model, arm_idx)
            
            # Compute masked loss
            with torch.no_grad():
                outputs_masked = model(inputs)
                if labels is not None:
                    loss_masked = loss_fn(outputs_masked, labels).item()
                else:
                    loss_masked = outputs_masked.mean().item()
            
            # Unmask
            unmask_fn(model, arm_idx)
            
            # Compute reward and update policy
            reward = self.compute_reward(loss_original, loss_masked)
            policy.update(arm_idx, reward)
            
            if (t + 1) % 100 == 0 or t == 0:
                print(f"  Iteration {t+1}/{self.config.play_budget}: arm={arm_names[arm_idx]}, "
                      f"loss_orig={loss_original:.4f}, loss_masked={loss_masked:.4f}, "
                      f"reward={reward:.4f}")
        
        # Final Selection Phase
        scores = policy.get_scores()
        top_k_indices = np.argsort(scores)[-self.config.top_k:][::-1]
        top_k_arms = [arm_names[i] for i in top_k_indices]
        top_k_scores = scores[top_k_indices]
        
        results = {
            "policy": self.config.policy,
            "num_arms": num_arms,
            "play_budget": self.config.play_budget,
            "top_k": self.config.top_k,
            "top_k_arms": top_k_arms,
            "top_k_scores": top_k_scores.tolist(),
            "all_scores": scores.tolist(),
            "arm_names": arm_names,
        }
        
        print(f"\nPruning complete. Top {self.config.top_k} arms selected for removal:")
        for i, (arm, score) in enumerate(zip(top_k_arms[:10], top_k_scores[:10])):
            print(f"  {i+1}. {arm}: score={score:.4f}")
        if len(top_k_arms) > 10:
            print(f"  ... and {len(top_k_arms) - 10} more")
        
        return results


def direct_evaluation_pruning(
    model: nn.Module,
    dataloader: torch.utils.data.DataLoader,
    arm_names: List[str],
    mask_fn: Callable[[nn.Module, int], None],
    unmask_fn: Callable[[nn.Module, int], None],
    top_k: int = 100,
    loss_fn: Optional[Callable] = None,
    device: str = "cuda" if torch.cuda.is_available() else "cpu",
) -> Dict:
    """
    Direct/oracle-style evaluation for comparison.
    Evaluates every candidate arm once (expensive but accurate).
    
    Args:
        model: The neural network
        dataloader: DataLoader
        arm_names: List of arm identifiers
        mask_fn: Mask function
        unmask_fn: Unmask function
        top_k: Number of arms to select
        loss_fn: Loss function
        device: Device
        
    Returns:
        Dictionary with evaluation results
    """
    model.eval()
    num_arms = len(arm_names)
    
    if loss_fn is None:
        loss_fn = nn.CrossEntropyLoss()
    
    print(f"Starting direct evaluation of {num_arms} arms...")
    
    # Get baseline loss
    batch = next(iter(dataloader))
    if isinstance(batch, (list, tuple)):
        inputs, labels = batch
        inputs = inputs.to(device)
        labels = labels.to(device)
    else:
        inputs = batch.to(device)
        labels = None
    
    with torch.no_grad():
        outputs = model(inputs)
        if labels is not None:
            baseline_loss = loss_fn(outputs, labels).item()
        else:
            baseline_loss = outputs.mean().item()
    
    # Evaluate each arm
    scores = np.zeros(num_arms)
    for arm_idx in range(num_arms):
        mask_fn(model, arm_idx)
        
        with torch.no_grad():
            outputs_masked = model(inputs)
            if labels is not None:
                loss_masked = loss_fn(outputs_masked, labels).item()
            else:
                loss_masked = outputs_masked.mean().item()
        
        unmask_fn(model, arm_idx)
        
        # Score = loss reduction (higher = more safe to remove)
        scores[arm_idx] = baseline_loss - loss_masked
        
        if (arm_idx + 1) % 50 == 0:
            print(f"  Evaluated {arm_idx + 1}/{num_arms} arms")
    
    top_k_indices = np.argsort(scores)[-top_k:][::-1]
    top_k_arms = [arm_names[i] for i in top_k_indices]
    top_k_scores = scores[top_k_indices]
    
    return {
        "policy": "direct",
        "num_arms": num_arms,
        "top_k": top_k,
        "top_k_arms": top_k_arms,
        "top_k_scores": top_k_scores.tolist(),
        "all_scores": scores.tolist(),
        "arm_names": arm_names,
    }
