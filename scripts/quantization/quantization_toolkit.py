"""
Quantization Toolkit for arXiv Papers Analysis
================================================
A unified PyTorch-based quantization framework implementing methods from:
- 2607.25870: Angle-aware QAT with structured pruning
- 2607.24953: Transposition-Invariant 2D Block FP4
- 2607.24981: Integer-Only DETR (I-LW-DETR components)
- 2607.25451: RTN quantization for memorization study
- 2607.25180: INT8 row-wise embedding quantization
- 2607.24568: PTQ/QAT FPGA evaluation
- 2607.24377: MXFP4 Attention
- 2607.25583: LoRA + Quantization trade-offs

Validation target: Qwen3-0.6B
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, List, Dict
import math


# =============================================================================
# 1. Base Quantizer
# =============================================================================

class BaseQuantizer(nn.Module):
    """基础量化器接口"""
    
    def __init__(self, bits: int = 8, group_size: int = 128):
        super().__init__()
        self.bits = bits
        self.group_size = group_size
        self.qmax = 2 ** (bits - 1) - 1
        self.qmin = -(2 ** (bits - 1))
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        量化张量
        
        Returns:
            x_quant: 量化后的张量
            scale: 尺度因子
        """
        raise NotImplementedError
    
    def dequantize(self, x_quant: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        """反量化"""
        return x_quant * scale


# =============================================================================
# 2. RTN Quantizer (2607.25451)
# =============================================================================

class RTNQuantizer(BaseQuantizer):
    """
    Round-to-Nearest 量化器
    论文: Bits and Memories (arXiv:2607.25451)
    
    特点:
    - 组-wise对称量化
    - 简单的round-to-nearest舍入
    - 无需校准数据
    """
    
    def __init__(self, bits: int = 4, group_size: int = 128):
        super().__init__(bits, group_size)
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        对权重进行RTN量化
        
        Args:
            x: 输入权重张量 [out_features, in_features]
        
        Returns:
            x_quant: 量化后的权重 (与x同shape)
            scales: 每组尺度 [num_groups]
            zeros: 零点 (对称量化时为0)
        """
        orig_shape = x.shape
        
        # 重塑为 [num_groups, group_size]
        if x.numel() % self.group_size != 0:
            pad_size = self.group_size - (x.numel() % self.group_size)
            x_flat = F.pad(x.flatten(), (0, pad_size))
        else:
            x_flat = x.flatten()
        
        x_blocks = x_flat.reshape(-1, self.group_size)
        
        # 计算每组的尺度和零点 (对称量化)
        w_max = x_blocks.abs().amax(dim=1, keepdim=True)
        scales = w_max / self.qmax
        scales = scales.clamp_min(1e-8)  # 防止除零
        
        # 量化
        x_q = torch.clamp(
            torch.round(x_blocks / scales),
            self.qmin, self.qmax
        )
        
        # 反量化 (用于模拟量化效果)
        x_dq = x_q * scales
        
        # 重塑回原始形状
        x_dq = x_dq.flatten()[:x.numel()].reshape(orig_shape)
        
        return x_dq, scales.squeeze(), torch.zeros_like(scales.squeeze())
    
    def quantize_model(self, model: nn.Module):
        """量化模型中的所有nn.Linear层"""
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                w_dq, scales, zeros = self.quantize(module.weight.data)
                module.weight.data = w_dq
                # 保存尺度和零点供后续使用
                module.register_buffer('quant_scales', scales)
                module.register_buffer('quant_zeros', zeros)
                print(f"Quantized {name}: {scales.shape[0]} groups, {self.bits}-bit")


# =============================================================================
# 3. INT8 Symmetric Quantizer (2607.25180, 2607.24981)
# =============================================================================

class INT8Quantizer(BaseQuantizer):
    """
    INT8 对称量化
    论文: Bekko Embedding (2607.25180), I-LW-DETR (2607.24981)
    
    特点:
    - 每行/每通道独立尺度
    - 适合嵌入层和线性层
    """
    
    def __init__(self, per_channel: bool = True, channel_dim: int = 0):
        super().__init__(bits=8, group_size=-1)
        self.per_channel = per_channel
        self.channel_dim = channel_dim
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        INT8量化
        
        Args:
            x: 输入张量
        
        Returns:
            x_quant: 量化后张量 (保持float，但值在[-128, 127])
            scale: 尺度因子
        """
        if self.per_channel:
            # 沿channel_dim计算每个通道的尺度
            dims = list(range(x.ndim))
            dims.remove(self.channel_dim)
            w_max = x.abs().amax(dim=dims, keepdim=True)
        else:
            w_max = x.abs().max()
        
        scale = w_max / 127.0
        scale = scale.clamp_min(1e-8)
        
        x_q = torch.clamp(torch.round(x / scale), -128, 127)
        x_dq = x_q * scale
        
        return x_dq, scale
    
    def fake_quantize(self, x: torch.Tensor) -> torch.Tensor:
        """
        Fake Quantization (用于QAT)
        前向时模拟量化效果，反向时STE直通
        """
        x_q, scale = self.quantize(x)
        # STE: 梯度直接穿过
        return x + (x_q - x).detach()


# =============================================================================
# 4. 2D Block FP4 Quantizer (2607.24953)
# =============================================================================

class FP4Quantizer(BaseQuantizer):
    """
    2D Block FP4 量化器 (转置不变)
    论文: Stable FP4 Training via Transposition-Invariant Block Quantization (2607.24953)
    
    特点:
    - 2D方形块结构 (如32x32)
    - 转置后块结构保持不变 → 前后向尺度一致
    - 无截断缩放 + 随机舍入
    """
    
    def __init__(self, bits: int = 4, block_size: int = 32, use_stochastic_rounding: bool = True):
        # FP4 E2M1 format
        super().__init__(bits=4, group_size=block_size)
        self.block_size = block_size
        self.use_stochastic_rounding = use_stochastic_rounding
        # FP4 E2M1 range: 约 [-6.0, 6.0] (含非规格化数)
        self.fp4_range = 6.0
    
    def _stochastic_round(self, x: torch.Tensor) -> torch.Tensor:
        """随机舍入: E[round(x)] = x"""
        floor = torch.floor(x)
        prob = x - floor
        rand = torch.rand_like(x)
        return floor + (rand < prob).float()
    
    def quantize(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        2D块FP4量化
        
        Args:
            x: 输入张量 [m, n] (至少2D)
        
        Returns:
            x_dq: 反量化后的张量
            scales: 块尺度
        """
        assert x.ndim >= 2, "2D block quantization requires at least 2D tensor"
        
        orig_shape = x.shape
        m, n = x.shape[0], x.shape[1]
        
        # 填充到block_size的倍数
        pad_m = (self.block_size - m % self.block_size) % self.block_size
        pad_n = (self.block_size - n % self.block_size) % self.block_size
        
        if pad_m > 0 or pad_n > 0:
            x_pad = F.pad(x, (0, pad_n, 0, pad_m))
        else:
            x_pad = x
        
        m_p, n_p = x_pad.shape[0], x_pad.shape[1]
        num_b_m = m_p // self.block_size
        num_b_n = n_p // self.block_size
        
        # 重塑为 [num_b_m, block_size, num_b_n, block_size]
        x_blocks = x_pad.reshape(
            num_b_m, self.block_size,
            num_b_n, self.block_size
        ).permute(0, 2, 1, 3)  # [num_b_m, num_b_n, block_size, block_size]
        
        # === 无截断缩放 ===
        # S = 2^ceil(log2(2*M / Q_range))
        M = x_blocks.abs().amax(dim=(-2, -1), keepdim=True)
        
        # 无截断: 确保所有值在范围内
        log_scale = torch.ceil(torch.log2(2 * M / self.fp4_range))
        log_scale = torch.clamp(log_scale, min=-126, max=127)  # 防止极端值
        scales = 2 ** log_scale
        scales = scales.clamp_min(1e-8)
        
        # === 量化 ===
        x_scaled = x_blocks / scales
        
        if self.use_stochastic_rounding:
            x_q = self._stochastic_round(x_scaled)
        else:
            x_q = torch.round(x_scaled)
        
        # 裁剪到FP4范围
        x_q = torch.clamp(x_q, -self.fp4_range, self.fp4_range)
        
        # 反量化
        x_dq = x_q * scales
        
        # 重塑回原始形状
        x_out = x_dq.permute(0, 2, 1, 3).reshape(m_p, n_p)[:m, :n]
        
        return x_out, scales.squeeze()
    
    def forward_backward_consistent(self, x: torch.Tensor) -> bool:
        """验证转置不变性: S(X) == S(X^T)"""
        _, s1 = self.quantize(x)
        _, s2 = self.quantize(x.t())
        return torch.allclose(s1, s2, atol=1e-5)


# =============================================================================
# 5. Angle-Aware QAT (2607.25870)
# =============================================================================

class AngleAwareQATLoss(nn.Module):
    """
    角度感知自蒸馏损失
    论文: VAD to the Bone (arXiv:2607.25870)
    
    核心思想: 冻结全精度分类器权重作为原型，优化特征与原型间的角度几何
    """
    
    def __init__(self, lambda_repel: float = 1.0, num_classes: int = 2):
        super().__init__()
        self.lambda_repel = lambda_repel
        self.num_classes = num_classes
    
    def forward(
        self,
        features: torch.Tensor,        # [B, d] 量化骨干输出的penultimate特征
        targets: torch.Tensor,         # [B] 类别标签
        frozen_classifier: torch.Tensor  # [C, d] 冻结的全精度分类器权重
    ) -> torch.Tensor:
        """
        角度对齐-排斥损失
        
        L = align(f, w_target) + lambda * repel(f, w_non-target)
        """
        B = features.size(0)
        
        # 归一化
        f_norm = F.normalize(features, p=2, dim=1)          # [B, d]
        w_norm = F.normalize(frozen_classifier, p=2, dim=1)  # [C, d]
        
        # 计算所有特征与所有原型的cosine similarity
        similarities = torch.mm(f_norm, w_norm.t())  # [B, C]
        
        total_loss = 0.0
        for i in range(B):
            f_i = f_norm[i]      # [d]
            y_i = targets[i].item()
            
            # === Term 1: 对齐目标类原型 ===
            w_target = w_norm[y_i]
            cos_target = torch.dot(f_i, w_target)
            align_loss = 1.0 - cos_target
            
            # === Term 2: 排斥非目标类原型 ===
            non_target_sims = []
            for c in range(self.num_classes):
                if c != y_i:
                    non_target_sims.append(similarities[i, c])
            
            if non_target_sims:
                max_non_target = max(non_target_sims)
                repel_loss = torch.clamp(max_non_target, min=0.0)
            else:
                repel_loss = torch.tensor(0.0, device=features.device)
            
            loss_i = align_loss + self.lambda_repel * repel_loss
            total_loss += loss_i
        
        return total_loss / B


class AngleAwareQAT(nn.Module):
    """
    角度感知QAT训练包装器
    """
    
    def __init__(self, model: nn.Module, bits: int = 4):
        super().__init__()
        self.model = model
        self.bits = bits
        
        # 冻结分类器权重作为原型
        self._freeze_classifier()
        
        # 准备QAT
        self.quantizer = INT8Quantizer(bits=bits) if bits == 8 else RTNQuantizer(bits=bits)
        self.model = self._prepare_qat(model)
    
    def _freeze_classifier(self):
        """冻结最后的分类层权重"""
        # 找到最后一层线性层
        last_linear = None
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                last_linear = module
        
        if last_linear:
            self.classifier_weight = last_linear.weight.data.clone().detach()
            last_linear.weight.requires_grad = False
            print(f"Frozen classifier: {last_linear}")
    
    def _prepare_qat(self, model: nn.Module) -> nn.Module:
        """插入FakeQuantize层"""
        # 简化: 对线性层应用fake quantization
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear) and module.weight.requires_grad:
                # 包装为QAT线性层
                module.weight.data = self.quantizer.quantize(module.weight.data)[0]
        return model
    
    def forward(self, x):
        return self.model(x)


# =============================================================================
# 6. Integer-Only Operations (2607.24981)
# =============================================================================

class IntegerGELU(nn.Module):
    """
    整数GELU近似 (I-LW-DETR)
    论文: Enabling Fully Integer-Only Inference for Lightweight Detection Transformers (2607.24981)
    
    GELU(x) ≈ x * Φ(x) where Φ is CDF of standard normal
    整数近似: 使用查找表或分段线性
    """
    
    def __init__(self, num_bits: int = 8, use_lookup_table: bool = True):
        super().__init__()
        self.num_bits = num_bits
        self.qmax = 2 ** (num_bits - 1) - 1
        self.use_lookup_table = use_lookup_table
        
        if use_lookup_table:
            # 预计算GELU查找表
            self.register_buffer('lut', self._build_lut())
    
    def _build_lut(self) -> torch.Tensor:
        """构建GELU查找表"""
        # 覆盖整数范围 [-128, 127]
        x_vals = torch.arange(-128, 128, dtype=torch.float32)
        # 浮点GELU
        gelu_vals = 0.5 * x_vals * (1 + torch.erf(x_vals / math.sqrt(2)))
        # 量化回整数范围
        scale = gelu_vals.abs().max() / self.qmax
        gelu_q = torch.clamp(torch.round(gelu_vals / scale), -self.qmax-1, self.qmax)
        return gelu_q
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.use_lookup_table:
            # 使用查找表 (需要缩放到表索引范围)
            x_idx = torch.clamp(x + 128, 0, 255).long()
            return self.lut[x_idx]
        else:
            # 分段线性近似
            return self._piecewise_approx(x)
    
    def _piecewise_approx(self, x: torch.Tensor) -> torch.Tensor:
        """分段线性整数GELU近似"""
        # 简单近似:
        # x > 0: GELU(x) ≈ x
        # x <= 0: GELU(x) ≈ 0 (或很小的负值)
        out = torch.where(x > 0, x, torch.zeros_like(x))
        return torch.clamp(out, -self.qmax-1, self.qmax)


class IntegerSoftmax(nn.Module):
    """
    整数Softmax近似 (Shiftmax)
    论文: I-LW-DETR (2607.24981)
    
    使用位移近似指数: exp(x) ≈ 2^(x / scale)
    """
    
    def __init__(self, dim: int = -1, num_bits: int = 8):
        super().__init__()
        self.dim = dim
        self.num_bits = num_bits
        self.scale = 8  # 可调节的移位因子
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: 整数输入
        
        # 减去最大值防止溢出
        x_max = x.amax(dim=self.dim, keepdim=True)
        x_shifted = x - x_max
        
        # exp(x) ≈ 2^(x / scale)
        # Use torch.pow for float-compatible computation
        exp_shift = x_shifted.long() // self.scale
        exp_shift = exp_shift.clamp(0, self.num_bits - 1)
        exp_approx = torch.clamp(torch.pow(torch.tensor(2.0, device=x.device), exp_shift.float()), 1, 2**self.num_bits - 1)
        
        # 归一化
        sum_exp = exp_approx.sum(dim=self.dim, keepdim=True)
        sum_exp = sum_exp.clamp_min(1)
        
        # 整数除法归一化
        out = (exp_approx * (2**self.num_bits - 1)) // sum_exp
        
        return out


class IntegerLayerNorm(nn.Module):
    """
    整数LayerNorm
    论文: I-LW-DETR (2607.24981)
    
    LayerNorm(x) = (x - mean) / sqrt(var + eps) * gamma + beta
    整数版本: 使用整数均值、方差计算
    """
    
    def __init__(self, normalized_shape: int, num_bits: int = 8, eps: float = 1e-5):
        super().__init__()
        self.normalized_shape = normalized_shape
        self.num_bits = num_bits
        self.eps = eps
        
        self.gamma = nn.Parameter(torch.ones(normalized_shape))
        self.beta = nn.Parameter(torch.zeros(normalized_shape))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: 整数输入 [B, seq, features]
        
        # 整数均值
        mean = x.mean(dim=-1, keepdim=True).round()
        
        # 整数方差 (简化: 使用绝对偏差)
        var = ((x - mean) ** 2).mean(dim=-1, keepdim=True)
        
        # 整数标准差近似 (使用整数平方根)
        std = torch.sqrt(var + self.eps)
        
        # 归一化
        x_norm = (x - mean) / std
        
        # 缩放和平移 (gamma/beta可能需要量化)
        out = x_norm * self.gamma + self.beta
        
        # 重新量化
        out = torch.clamp(torch.round(out), -(2**(self.num_bits-1)), 2**(self.num_bits-1)-1)
        
        return out


# =============================================================================
# 7. GPTQ-style Quantization (4-bit)
# =============================================================================

class GPTQQuantizer:
    """
    GPTQ-style 4-bit 量化
    基于OBS (Optimal Brain Surgeon) 的逐层量化
    
    特点:
    - 使用Hessian矩阵的逆进行最优补偿
    - 顺序量化：量化一个权重，更新剩余权重
    """
    
    def __init__(self, bits: int = 4, group_size: int = 128, actorder: bool = False):
        self.bits = bits
        self.group_size = group_size
        self.actorder = actorder  # 是否按激活大小排序
        self.qmax = 2 ** (bits - 1) - 1
    
    def quantize_layer(
        self,
        W: torch.Tensor,      # [out_features, in_features] 权重
        H: torch.Tensor,      # [in_features, in_features] Hessian矩阵
        X: torch.Tensor       # 校准数据 [N, in_features]
    ) -> torch.Tensor:
        """
        GPTQ量化一层
        
        Args:
            W: 权重矩阵
            H: 激活的Hessian近似 (X^T @ X / N)
            X: 校准输入数据
        
        Returns:
            W_quant: 量化后的权重
        """
        # 添加阻尼
        damp = 0.01 * torch.diag(H).mean()
        H += torch.eye(H.shape[0], device=H.device) * damp
        
        # Cholesky分解
        try:
            H_inv = torch.cholesky_inverse(torch.linalg.cholesky(H))
        except:
            H_inv = torch.linalg.pinv(H)
        
        W_quant = W.clone()
        
        # 逐列量化
        for i in range(W.shape[1]):
            w_col = W[:, i]
            
            # 计算量化误差
            scale = w_col.abs().max() / self.qmax
            scale = scale.clamp_min(1e-8)
            
            w_q = torch.clamp(torch.round(w_col / scale), -self.qmax-1, self.qmax)
            w_dq = w_q * scale
            
            # 量化误差
            err = (w_col - w_dq).unsqueeze(1)  # [out_features, 1]
            
            # 更新剩余列 (OBS补偿)
            if i < W.shape[1] - 1:
                W[:, i+1:] -= err @ H_inv[i, i+1:].unsqueeze(0)
            
            W_quant[:, i] = w_dq
        
        return W_quant


# =============================================================================
# 8. 量化模型评估器
# =============================================================================

class QuantizedModelEvaluator:
    """
    量化模型评估器
    支持多种量化方法的评估
    """
    
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B", device: str = "cuda"):
        self.device = device
        self.model_name = model_name
        
        # 尝试加载模型
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map=device,
                trust_remote_code=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            print(f"Loaded model: {model_name}")
        except Exception as e:
            print(f"Could not load model: {e}")
            self.model = None
            self.tokenizer = None
    
    def evaluate_perplexity(self, texts: List[str], max_length: int = 512) -> float:
        """评估困惑度"""
        if self.model is None:
            return float('inf')
        
        self.model.eval()
        total_loss = 0
        total_tokens = 0
        
        for text in texts:
            tokens = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
            input_ids = tokens.input_ids.to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_ids, labels=input_ids)
                loss = outputs.loss
                num_tokens = (input_ids != self.tokenizer.pad_token_id).sum().item()
                
                total_loss += loss.item() * num_tokens
                total_tokens += num_tokens
        
        avg_loss = total_loss / total_tokens if total_tokens > 0 else float('inf')
        perplexity = math.exp(avg_loss)
        
        return perplexity
    
    def quantize_and_evaluate(self, quantizer: BaseQuantizer, eval_texts: List[str]) -> Dict:
        """
        量化模型并评估
        
        Returns:
            {
                "quantizer": str,
                "bits": int,
                "perplexity": float,
                "model_size_mb": float
            }
        """
        if self.model is None:
            return {"error": "Model not loaded"}
        
        # 量化
        if isinstance(quantizer, RTNQuantizer):
            quantizer.quantize_model(self.model)
        
        # 评估
        ppl = self.evaluate_perplexity(eval_texts)
        
        # 计算模型大小
        param_bytes = sum(p.numel() * p.element_size() for p in self.model.parameters())
        size_mb = param_bytes / (1024 ** 2)
        
        return {
            "quantizer": quantizer.__class__.__name__,
            "bits": quantizer.bits,
            "perplexity": ppl,
            "model_size_mb": size_mb
        }


# =============================================================================
# 9. 主评估脚本
# =============================================================================

def main():
    """
    主评估流程
    验证Qwen3-0.6B在不同量化方法下的性能
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Quantization Evaluation on Qwen3-0.6B")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="Model name")
    parser.add_argument("--method", choices=["rtn4", "rtn8", "fp4", "int8", "gptq4"], 
                        default="rtn4", help="Quantization method")
    parser.add_argument("--eval_texts", nargs="+", default=["Hello world", "The quick brown fox"],
                        help="Evaluation texts")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()
    
    # 创建评估器
    evaluator = QuantizedModelEvaluator(args.model, args.device)
    
    if evaluator.model is None:
        print("Model not available. Running in demo mode.")
        return
    
    # 选择量化器
    quantizers = {
        "rtn4": RTNQuantizer(bits=4, group_size=128),
        "rtn8": RTNQuantizer(bits=8, group_size=128),
        "fp4": FP4Quantizer(bits=4, block_size=32),
        "int8": INT8Quantizer(per_channel=True),
    }
    
    quantizer = quantizers.get(args.method)
    if quantizer is None:
        print(f"Unknown method: {args.method}")
        return
    
    # 评估
    print(f"\nEvaluating {args.method} on {args.model}...")
    results = evaluator.quantize_and_evaluate(quantizer, args.eval_texts)
    
    print("\n=== Results ===")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
