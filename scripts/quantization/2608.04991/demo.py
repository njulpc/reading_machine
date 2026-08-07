#!/usr/bin/env python3
"""
RAC: Reference-Aware Activation Compression for Communication-Efficient Split LLM Inference
===========================================================================================
论文: arXiv:2608.04991

目标模型: Qwen3-0.6B (Qwen/Qwen3-0.6B)

核心方法
--------
RAC 是面向分割推理的激活压缩编解码器。在 split inference 中, 设备端计算的部分
激活需传输到服务器端, 通信成为瓶颈。RAC 利用历史激活中的精确 token 匹配, 通过
"参考检索 + 分组仿射对齐 + 残差量化"三步将传输比特数降至最低。

三大组件:
1. 参考检索 (Reference Retrieval): 在历史激活 span 库中检索与当前 span 最相似的参考
2. 分组仿射对齐 (Grouped Affine Alignment): 逐组最小二乘计算 scale/zero, 对齐参考
3. 残差量化 (Residual Quantization): 对残差进行多级量化, 可选保留 outlier 通道

运行方式
--------
    python3 demo.py
"""

import sys
import math
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

# 导入共享量化工具包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from quantization_toolkit import (
    load_model_or_mock,
    quantization_error_metrics,
    symmetric_group_quantize,
)


# =============================================================================
# 1. 参考库: 存储与检索历史激活 span
# =============================================================================

class ReferenceStore:
    """
    历史激活 span 存储库。

    在自回归生成中, 相同 token 子序列在不同上下文中会产生相似的激活。
    RAC 将历史激活切分为固定长度的 span 并存储, 压缩新激活时先检索最佳参考。

    检索策略: 按 span 级别的余弦相似度选取 Top-1 参考。
    """

    def __init__(self, max_spans: int = 128, span_length: int = 16):
        self.max_spans = max_spans
        self.span_length = span_length
        self.spans = []          # list of [span_length, hidden_dim]

    def add(self, activation: torch.Tensor):
        """
        将激活序列切分为 span 并存入参考库。

        Args:
            activation: [seq_len, hidden_dim] 激活张量
        """
        seq_len = activation.size(0)
        step = self.span_length
        for i in range(0, seq_len - step + 1, step):
            span = activation[i:i + step].detach()
            self.spans.append(span)
            # 超过容量时淘汰最旧的 span (FIFO)
            if len(self.spans) > self.max_spans:
                self.spans.pop(0)

    def retrieve(self, query: torch.Tensor):
        """
        检索与 query span 最相似的历史 span。

        Args:
            query: [span_length, hidden_dim]

        Returns:
            best_span: 最佳匹配 span [span_length, hidden_dim], 无匹配时返回 None
            best_sim: 余弦相似度
        """
        if not self.spans:
            return None, 0.0

        q_flat = query.flatten().unsqueeze(0)         # [1, span*hidden]

        best_sim, best_span = -1.0, None
        for span in self.spans:
            s_flat = span.flatten().unsqueeze(0)
            sim = F.cosine_similarity(q_flat, s_flat).item()
            if sim > best_sim:
                best_sim = sim
                best_span = span

        return best_span, best_sim


# =============================================================================
# 2. 分组仿射对齐: 逐组最小二乘计算 scale / zero
# =============================================================================

class GroupedAffineAlignment:
    """
    分组仿射对齐。

    相同 token 在不同上下文的激活存在分布偏移, RAC 对参考 span 施加逐组仿射变换:
        ref_aligned = ref * scale + zero
    其中 scale 和 zero 通过最小二乘在每个 group 上独立求解:
        scale = cov(ref, cur) / var(ref)
        zero  = mean(cur) - scale * mean(ref)
    使得对齐后参考与当前激活的残差最小。
    """

    def __init__(self, group_size: int = 32):
        self.group_size = group_size

    def align(self, current: torch.Tensor, reference: torch.Tensor):
        """
        计算逐组仿射参数并对齐参考。

        Args:
            current:   [span_length, hidden_dim] 当前激活
            reference: [span_length, hidden_dim] 参考激活

        Returns:
            aligned_ref: 对齐后的参考 [span_length, hidden_dim]
            scales: 每组尺度 [num_groups]
            zeros:  每组零点 [num_groups]
        """
        span_len, hidden = current.shape
        g = self.group_size

        # 沿 hidden 维度分组
        pad = (g - hidden % g) % g
        cur_p = F.pad(current, (0, pad))       # [span_len, hidden+pad]
        ref_p = F.pad(reference, (0, pad))

        num_groups = cur_p.size(1) // g
        # 重塑为 [span_len, num_groups, g]
        cur_g = cur_p.reshape(span_len, num_groups, g)
        ref_g = ref_p.reshape(span_len, num_groups, g)

        # 逐组最小二乘: scale = cov(ref,cur)/var(ref), zero = mean(cur)-scale*mean(ref)
        # 每组只产生一个 scale 和一个 zero (在 span 和 group 元素上联合 reduce)
        mean_ref = ref_g.mean(dim=(0, 2))            # [num_groups]
        mean_cur = cur_g.mean(dim=(0, 2))            # [num_groups]
        ref_c = ref_g - mean_ref.view(1, -1, 1)      # [span_len, num_groups, g]
        cur_c = cur_g - mean_cur.view(1, -1, 1)

        var_ref = (ref_c ** 2).sum(dim=(0, 2))       # [num_groups]
        cov_rc = (ref_c * cur_c).sum(dim=(0, 2))     # [num_groups]
        scales = cov_rc / var_ref.clamp_min(1e-8)    # [num_groups]
        zeros = mean_cur - scales * mean_ref         # [num_groups]

        # 应用仿射变换: 每组一个 scale 和一个 zero, broadcast 到 g 维度
        aligned_g = ref_g * scales.view(1, -1, 1) + zeros.view(1, -1, 1)
        aligned_ref = aligned_g.reshape(span_len, -1)[:, :hidden]

        return aligned_ref, scales, zeros


# =============================================================================
# 3. 残差量化: 多级残差量化 + 可选 outlier 保留
# =============================================================================

class ResidualQuantizer:
    """
    校准残差量化器。

    对齐后残差 residual = current - ref_aligned 的幅值远小于原始激活,
    因此可用更少比特量化。支持多级残差量化:
        Level 1: q1 = quantize(residual, b1), residual2 = residual - q1
        Level 2: q2 = quantize(residual2, b2), ...
        重建: hat = q1 + q2 + ...

    可选 outlier 保留: prefill 阶段部分通道幅值极大, 保留 Top-k outlier 通道
    全精度传输, 其余通道量化。
    """

    def __init__(self, bits_list=(4, 2), group_size: int = 32,
                 outlier_ratio: float = 0.0):
        """
        Args:
            bits_list: 每级残差量化的比特数, 如 (4,2) 表示先用4bit再2bit
            group_size: 分组量化粒度
            outlier_ratio: 保留的 outlier 通道比例 (0=不保留)
        """
        self.bits_list = bits_list
        self.group_size = group_size
        self.outlier_ratio = outlier_ratio

    def quantize(self, x: torch.Tensor):
        """
        多级残差量化。

        Args:
            x: [span_length, hidden_dim] 残差张量

        Returns:
            x_hat: 重建后的残差
            total_bits: 估计传输比特数
        """
        orig_shape = x.shape
        residual = x.clone()
        x_hat = torch.zeros_like(x)
        total_bits = 0

        # 可选: 保留 outlier 通道全精度
        if self.outlier_ratio > 0:
            channel_abs = x.abs().mean(dim=0)  # [hidden]
            k = max(1, int(channel_abs.size(0) * self.outlier_ratio))
            _, outlier_idx = channel_abs.topk(k)
            mask = torch.ones(x.size(1), dtype=torch.bool, device=x.device)
            mask[outlier_idx] = False

            # outlier 通道直接保留 (全精度)
            x_hat[:, outlier_idx] = x[:, outlier_idx]
            residual[:, outlier_idx] = 0.0
            total_bits += k * x.size(0) * 32  # FP32 传输 outlier
        else:
            mask = torch.ones(x.size(1), dtype=torch.bool, device=x.device)
            outlier_idx = torch.tensor([], dtype=torch.long)

        # 多级残差量化 (仅在非 outlier 通道上)
        for bits in self.bits_list:
            q = symmetric_group_quantize(residual, bits, self.group_size)
            x_hat = x_hat + q
            residual = residual - q
            # 每级量化: 量化值 + 尺度开销
            n_elems = mask.sum().item() * x.size(0)
            total_bits += n_elems * bits + n_elems // self.group_size * 16

        return x_hat, total_bits


# =============================================================================
# 4. RAC 编解码器: 整合三步压缩流程
# =============================================================================

class RACCodec:
    """
    RAC 激活压缩编解码器。

    压缩流程:
        1. 检索参考 span
        2. 分组仿射对齐
        3. 残差量化
    解码流程:
        1. 取回参考 span
        2. 施加仿射对齐
        3. 加上量化残差
    """

    def __init__(self, span_length=16, group_size=32,
                 bits_list=(4, 2), outlier_ratio=0.0, use_reference=True):
        self.span_length = span_length
        self.use_reference = use_reference
        self.store = ReferenceStore(span_length=span_length)
        self.aligner = GroupedAffineAlignment(group_size=group_size)
        self.quantizer = ResidualQuantizer(
            bits_list=bits_list, group_size=group_size,
            outlier_ratio=outlier_ratio)

    def compress(self, activation: torch.Tensor):
        """
        压缩一段激活序列。

        Args:
            activation: [seq_len, hidden_dim]

        Returns:
            reconstructed: 重建的激活
            stats: 压缩统计信息 dict
        """
        seq_len = activation.size(0)
        step = self.span_length
        reconstructed = torch.zeros_like(activation)
        total_bits = 0
        n_spans = 0
        n_ref_hit = 0

        for i in range(0, seq_len, step):
            end = min(i + step, seq_len)
            span = activation[i:end]
            n_spans += 1

            # 步骤1: 检索参考 (use_reference=False 时跳过, 退化为直接量化)
            ref, sim = (self.store.retrieve(span) if self.use_reference else (None, 0.0))
            if ref is not None and sim > 0.5:
                n_ref_hit += 1
                # 步骤2: 分组仿射对齐
                aligned, scales, zeros = self.aligner.align(span, ref)
                # 步骤3: 残差量化
                residual = span - aligned
                res_hat, bits = self.quantizer.quantize(residual)
                reconstructed[i:end] = aligned + res_hat
                # 传输开销: 参考ID + 仿射参数 + 量化残差
                num_groups = scales.size(0)
                total_bits += bits + num_groups * 32 * 2 + 16  # scale+zero+ref_id
            else:
                # 无参考: 直接量化 (退化情况)
                q, bits = self.quantizer.quantize(span)
                reconstructed[i:end] = q
                total_bits += bits

        # 将当前激活加入参考库供后续使用
        self.store.add(activation)

        # 原始 FP32 传输比特数
        orig_bits = activation.numel() * 32
        stats = {
            "n_spans": n_spans,
            "ref_hit_rate": n_ref_hit / max(n_spans, 1),
            "orig_bits": orig_bits,
            "compressed_bits": total_bits,
            "compression_ratio": orig_bits / max(total_bits, 1),
        }
        return reconstructed, stats


# =============================================================================
# 5. 主流程: 加载模型, 捕获激活, 对比压缩方法
# =============================================================================

def capture_activations(model, input_ids, layer_name="layers.0.q_proj"):
    """
    通过 hook 捕获指定层的输入激活 (即分割推理的传输张量)。

    Returns:
        activation: [seq_len, hidden_dim] 捕获的激活
    """
    captured = {}

    def hook_fn(module, inp, out):
        # inp[0] 是 Linear 的输入: [batch, seq_len, hidden_dim]
        captured["act"] = inp[0].detach().squeeze(0)

    # 在 Mock 和真实模型上都能找到目标层
    target = None
    for name, module in model.named_modules():
        if layer_name in name and isinstance(module, nn.Linear):
            target = module
            break
    if target is None:
        # 退而求其次: 找第一个 Linear
        for name, module in model.named_modules():
            if isinstance(module, nn.Linear):
                target = module
                break

    handle = target.register_forward_hook(hook_fn)
    with torch.no_grad():
        model(input_ids)
    handle.remove()
    return captured["act"]


def main():
    print("=" * 70)
    print("RAC: Reference-Aware Activation Compression")
    print("论文: arXiv:2608.04991 | 目标模型: Qwen3-0.6B")
    print("=" * 70)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 生成多段输入序列 (模拟 prefill + 多轮 decode)
    # 共享前缀 token 以触发参考匹配 (相同 token 子序列产生相似激活)
    vocab_size = model.embed.num_embeddings if is_mock else 32000
    common_prefix = torch.randint(0, vocab_size, (1, 24), device=device)
    seqs = [torch.cat([common_prefix,
                       torch.randint(0, vocab_size, (1, 24), device=device)], dim=1)
            for _ in range(6)]

    # 3. 捕获每段输入的激活
    print("\n[2] 捕获层激活 (模拟分割推理传输张量)...")
    activations = []
    for idx, seq in enumerate(seqs):
        act = capture_activations(model, seq)
        activations.append(act)
        if idx == 0:
            print(f"    激活 shape: {act.shape}  (seq_len={act.size(0)}, hidden={act.size(1)})")

    # 4. 测试不同压缩配置
    configs = [
        ("直接量化 4bit (无参考)", {"bits_list": (4,), "outlier_ratio": 0.0}, False),
        ("直接量化 4+2bit (无参考)", {"bits_list": (4, 2), "outlier_ratio": 0.0}, False),
        ("RAC 4bit (参考+对齐)", {"bits_list": (4,), "outlier_ratio": 0.0}, True),
        ("RAC 4+2bit (参考+对齐)", {"bits_list": (4, 2), "outlier_ratio": 0.0}, True),
        ("RAC 4bit + outlier 1%", {"bits_list": (4,), "outlier_ratio": 0.01}, True),
    ]

    print(f"\n[3] 压缩方法对比 (共 {len(activations)} 段激活)")
    print(f"{'方法':<30} {'平均命中率':<12} {'平均MSE':<14} {'平均Cos':<10} {'压缩比':<10}")
    print("-" * 80)

    for name, cfg, use_rac in configs:
        codec = RACCodec(
            span_length=16, group_size=32,
            bits_list=cfg["bits_list"],
            outlier_ratio=cfg["outlier_ratio"],
            use_reference=use_rac,
        )
        all_metrics = []
        all_ratios = []
        all_hit_rates = []

        for act in activations:
            recon, stats = codec.compress(act)
            m = quantization_error_metrics(act, recon)
            all_metrics.append(m)
            all_ratios.append(stats["compression_ratio"])
            all_hit_rates.append(stats["ref_hit_rate"])

        avg_mse = sum(m["mse"] for m in all_metrics) / len(all_metrics)
        avg_cos = sum(m["cosine_similarity"] for m in all_metrics) / len(all_metrics)
        avg_ratio = sum(all_ratios) / len(all_ratios)
        avg_hit = sum(all_hit_rates) / len(all_hit_rates)
        hit_str = f"{avg_hit:.1%}" if use_rac else "N/A"

        print(f"{name:<30} {hit_str:<12} {avg_mse:<14.6f} {avg_cos:<10.6f} {avg_ratio:<10.1f}x")

    # 5. 详细展示: 参考对齐对残差幅值的影响
    print(f"\n[4] 参考对齐效果分析 (取第2段激活的非共享部分)")
    codec = RACCodec(span_length=16, group_size=32, bits_list=(4,), outlier_ratio=0.0)
    # 先用第1段填充参考库
    codec.compress(activations[0])
    # 取第2段的后半部分 (非共享 token, 参考匹配不完美, 更能体现对齐效果)
    act = activations[1]
    span = act[16:32]  # 非共享部分的第一个 span
    ref, sim = codec.store.retrieve(span)
    if ref is not None:
        aligned, scales, zeros = codec.aligner.align(span, ref)
        residual = span - aligned
        raw_residual = span - ref  # 未对齐的残差
        raw_norm = raw_residual.norm().item()
        res_norm = residual.norm().item()
        reduction = (1 - res_norm / max(raw_norm, 1e-8)) * 100 if raw_norm > 1e-8 else 0.0
        print(f"    参考相似度: {sim:.4f}")
        print(f"    未对齐残差 L2 范数: {raw_norm:.4f}")
        print(f"    对齐后残差 L2 范数: {res_norm:.4f}  (降低 {reduction:.1f}%)")
        print(f"    原始激活 L2 范数:   {span.norm().item():.4f}")
        print(f"    残差/原始 能量比:   {res_norm / max(span.norm().item(), 1e-8):.4f}")

    print(f"\n{'='*70}")
    print("RAC 验证完成。")
    print("核心结论: 参考检索 + 分组仿射对齐将残差幅值大幅降低,")
    print("使低比特残差量化即可达到高保真重建, 实现高压缩比。")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
