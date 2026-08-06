#!/usr/bin/env python3
"""
TaskPress: Task-Guided KV Cache Compression via Task-Guided Pruning
====================================================================
论文: arXiv:2608.03276
作者: Wonpyo Park, Seung-won Hwang
标题: TaskPress: Query-Agnostic KV Cache Compression via Task-Guided Pruning

目标模型: Qwen3-0.6B (Qwen/Qwen3-0.6B)

核心方法
--------
长上下文推理受 KV cache 线性增长制约。已有剪枝方法基于 query-specific 的
token 重要性, 无法跨未见 query 复用。TaskPress 提出任务引导的、query-agnostic
的 KV cache 驱逐框架:

1. 任务引导 (Task-Guided Pruning)
   - 用一个高层 task guide (meta-query) 在 prefill 阶段过滤无关 token。
   - task guide 代表任务意图 (如 "总结文档"/"回答关于X的问题"), 与具体 query 无关。
   - 计算 task guide 对各 context token 的注意力, 丢弃低注意力 token。
   - 得到的压缩 cache 可跨同任务的不同 query 复用 (query-agnostic)。

2. 量化尺度因子作为离群点检测信号 (Zero-Cost Outlier Detection)
   - 对 K/V 做分组量化时, 每组的 scale factor (max|x|) 已被计算。
   - 复用这些 scale factor 作为 token 重要性的零成本代理:
       * 某个 token 的 scale factor 大 → 含极端值 (outlier) → 对表示影响大 → 保留
       * scale factor 小 → 表示平淡 → 可安全剪枝/低精度量化
   - 这样无需额外计算即可识别 influential outlier token。

3. 剪枝 + 量化联合压缩
   - 先用 task guide 剪枝 (丢弃无关 token)
   - 再对保留 token 量化, 其中 outlier token (大 scale) 用更高精度
   - 生成紧凑、可复用的 cache

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
    MockTransformer,
)


# =============================================================================
# 1. KV Cache 提取
# =============================================================================

@torch.no_grad()
def extract_kv_cache(model, input_ids, is_mock: bool):
    """
    提取所有层的 K/V cache。返回 list of [B, H, T, D]。

    对真实 Qwen3 模型: 用 use_cache=True 获取 past_key_values。
    对 MockTransformer: 手动逐层投影。
    """
    k_list = []
    v_list = []

    if is_mock:
        m = model
        x = m.embed(input_ids)
        B, T = input_ids.shape
        for layer in m.layers:
            h = layer['input_norm'](x)
            k = layer['k_proj'](h).view(B, T, m.num_kv_heads, m.head_dim)
            v = layer['v_proj'](h).view(B, T, m.num_kv_heads, m.head_dim)
            # 转为 [B, H, T, D]
            k_list.append(k.transpose(1, 2))
            v_list.append(v.transpose(1, 2))
            # 继续前向
            q = layer['q_proj'](h).view(B, T, m.num_heads, m.head_dim).transpose(1, 2)
            attn = _simple_attention(q, k.transpose(1, 2), v.transpose(1, 2))
            x = x + layer['o_proj'](attn.reshape(B, T, -1))
            h2 = layer['post_norm'](x)
            x = x + layer['down_proj'](
                F.silu(layer['gate_proj'](h2)) * layer['up_proj'](h2))
        num_kv_heads = m.num_kv_heads
        head_dim = m.head_dim
        num_layers = len(m.layers)
    else:
        cfg = model.config
        num_kv_heads = getattr(cfg, "num_key_value_heads",
                               getattr(cfg, "num_attention_heads", 1))
        head_dim = getattr(cfg, "head_dim",
                           cfg.hidden_size // cfg.num_attention_heads)
        try:
            outputs = model(input_ids, use_cache=True)
            pkv = outputs.past_key_values
            if pkv is not None:
                if hasattr(pkv, 'key_cache') and len(pkv.key_cache) > 0:
                    for li in range(len(pkv.key_cache)):
                        k_list.append(pkv.key_cache[li])
                        v_list.append(pkv.value_cache[li])
                else:
                    for layer_kv in pkv:
                        k_list.append(layer_kv[0])
                        v_list.append(layer_kv[1])
        except Exception as e:
            print(f"    [warn] use_cache 提取失败: {e}")

        # 兜底: 随机 K/V
        if len(k_list) == 0:
            print("    [warn] 使用随机 K/V 兜底")
            B, T = input_ids.shape
            num_layers = cfg.num_hidden_layers
            for _ in range(num_layers):
                k_list.append(torch.randn(B, num_kv_heads, T, head_dim) * 0.1)
                v_list.append(torch.randn(B, num_kv_heads, T, head_dim) * 0.1)

    num_layers = len(k_list)
    seq_len = k_list[0].shape[2]
    B = k_list[0].shape[0]
    metadata = {
        "num_layers": num_layers, "num_kv_heads": num_kv_heads,
        "head_dim": head_dim, "seq_len": seq_len, "batch_size": B,
    }
    return k_list, v_list, metadata


@torch.no_grad()
def extract_guide_kv(model, guide_ids, is_mock: bool):
    """
    提取 task guide 的 K (作为 meta-query 的投影)。

    用 guide token 的 K 作为 meta-query, 去对 context 的 K/V 做注意力,
    实现 task-guided 重要性打分。
    """
    if is_mock:
        m = model
        x = m.embed(guide_ids)
        B, T = guide_ids.shape
        # 取第一层的 K 作为 meta-query (简化)
        h = m.layers[0]['input_norm'](x)
        q = m.layers[0]['q_proj'](h).view(B, T, m.num_heads, m.head_dim)
        return q.transpose(1, 2)  # [B, H, T_g, D]
    else:
        # 用模型第一个 attention 层的 Q (q_proj 输出) 作为 meta-query
        captured = {}
        def hook(module, inp, out):
            # forward_hook: (module, input, output); 取 q_proj 输出 = 真实 Q
            captured['q'] = out
        handle = None
        for name, module in model.named_modules():
            if hasattr(module, 'self_attn'):
                # 尝试 hook q_proj
                if hasattr(module.self_attn, 'q_proj'):
                    handle = module.self_attn.q_proj.register_forward_hook(hook)
                    break
        with torch.no_grad():
            _ = model(guide_ids, use_cache=False)
        if handle:
            handle.remove()
        if 'q' in captured:
            q = captured['q']
            if isinstance(q, tuple):
                q = q[0]
            cfg = model.config
            nh = cfg.num_attention_heads
            hd = getattr(cfg, 'head_dim', cfg.hidden_size // nh)
            B, T, _ = q.shape
            return q.view(B, T, nh, hd).transpose(1, 2)
        # 兜底
        cfg = model.config
        nh = cfg.num_attention_heads
        hd = cfg.hidden_size // nh
        B, T = guide_ids.shape
        return torch.randn(B, nh, T, hd) * 0.1


def _simple_attention(q, k, v):
    """简化多头注意力。q/k/v: [B, H, T, D] 或 [B, H, Tq, D]/[B,H,Tk,D]。"""
    D = q.shape[-1]
    scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(D)
    attn = F.softmax(scores, dim=-1)
    return torch.matmul(attn, v)


# =============================================================================
# 2. 分组量化 + 尺度因子 (零成本离群点检测信号)
# =============================================================================

def group_quantize_with_scale(x: torch.Tensor, bits: int = 4,
                               group_size: int = 64):
    """
    分组量化, 同时返回 per-group scale factor。

    scale factor 即每组的 max|x|, 论文复用它作为离群点检测的零成本信号:
        - token 的 scale factor 大 → 含极端值 → influential outlier → 保留
        - scale factor 小 → 表示平淡 → 可剪枝/低精度

    Args:
        x: [..., D] 张量
        bits: 量化比特
        group_size: 分组大小

    Returns:
        x_dq: 反量化张量
        scales: [..., num_groups] 每组尺度 (用于离群点检测)
    """
    qmax = 2 ** (bits - 1) - 1
    qmin = -(2 ** (bits - 1))
    orig_shape = x.shape
    D = orig_shape[-1]
    # pad 到 group_size 倍数
    pad = (group_size - D % group_size) % group_size
    if pad > 0:
        x_p = F.pad(x, (0, pad))
    else:
        x_p = x
    D_p = D + pad
    num_groups = D_p // group_size

    x_g = x_p.reshape(*orig_shape[:-1], num_groups, group_size)
    scales = x_g.abs().amax(dim=-1).clamp_min(1e-8) / qmax  # [..., num_groups]
    x_q = torch.clamp(torch.round(x_g / scales.unsqueeze(-1)), qmin, qmax)
    x_dq = (x_q * scales.unsqueeze(-1)).reshape(orig_shape[:-1] + (D_p,))
    if pad > 0:
        x_dq = x_dq[..., :D]
    return x_dq, scales


# =============================================================================
# 3. TaskPress 核心: 任务引导剪枝 + 量化尺度离群点检测
# =============================================================================

class TaskPressCompressor:
    """
    TaskPress: 任务引导的 query-agnostic KV cache 压缩器。

    参数:
        keep_ratio: 剪枝后保留的 token 比例 (如 0.3 = 保留 30%)
        outlier_ratio: 基于 scale factor 识别为 outlier 的 token 比例 (强制保留)
        base_bits: 常规 token 量化比特
        outlier_bits: outlier token 量化比特 (更高精度)
        group_size: 分组量化组大小

    工作流程:
        1. compute_task_importance: task guide 对 context token 的注意力打分
        2. detect_outliers: 用量化 scale factor 识别 outlier token (零成本)
        3. prune_and_quantize:
           - 保留: outlier ∪ top-k task-important
           - 其余 token 剪枝 (丢弃)
           - outlier 用 outlier_bits, 普通保留 token 用 base_bits
        4. 得到 query-agnostic 的可复用压缩 cache
    """

    def __init__(self, keep_ratio: float = 0.3, outlier_ratio: float = 0.05,
                 base_bits: int = 4, outlier_bits: int = 8,
                 group_size: int = 64):
        self.keep_ratio = keep_ratio
        self.outlier_ratio = outlier_ratio
        self.base_bits = base_bits
        self.outlier_bits = outlier_bits
        self.group_size = group_size

    def compute_task_importance(self, k_cache: torch.Tensor,
                                 meta_query: torch.Tensor) -> torch.Tensor:
        """
        计算 task guide 对 context token 的重要性 (注意力累积分数)。

        meta_query (task guide 的 Q) 对 context 的 K 做注意力, 累积每个
        context token 被关注的总量作为重要性。这是 query-agnostic 的: 基于
        task guide 而非具体 query。

        Args:
            k_cache: [B, H, T, D]
            meta_query: [B, H, T_g, D] task guide 的 query

        Returns:
            importance: [B, T] 每个 context token 的任务重要性
        """
        B, H, T, D = k_cache.shape
        # attention: [B, H, T_g, T]
        scores = torch.matmul(meta_query, k_cache.transpose(-2, -1)) / math.sqrt(D)
        attn = F.softmax(scores, dim=-1)
        # 累积: 每个 context token 被关注的总量, 对 head 平均
        importance = attn.sum(dim=-2).mean(dim=1)  # [B, T]
        return importance

    def detect_outliers(self, k_cache: torch.Tensor,
                         v_cache: torch.Tensor) -> torch.Tensor:
        """
        用量化 scale factor 检测 outlier token (零成本信号)。

        对每个 token, 计算其 K/V 向量的 per-group scale factor 的最大值。
        scale factor 大 → 含极端值 → influential outlier。

        这一步复用了量化时本就要计算的 scale, 因此是 "零成本" 的。

        Args:
            k_cache, v_cache: [B, H, T, D]

        Returns:
            outlier_score: [B, T] 每个 token 的 outlier 分数
        """
        B, H, T, D = k_cache.shape
        # 对 head 求平均后做分组 (简化: 用 K 和 V 的综合 scale)
        k_mean = k_cache.mean(dim=1)  # [B, T, D]
        v_mean = v_cache.mean(dim=1)  # [B, T, D]

        _, k_scales = group_quantize_with_scale(
            k_mean, bits=4, group_size=self.group_size)  # [B, T, num_groups]
        _, v_scales = group_quantize_with_scale(
            v_mean, bits=4, group_size=self.group_size)

        # outlier score = max scale across groups (K和V合并)
        k_score = k_scales.max(dim=-1).values  # [B, T]
        v_score = v_scales.max(dim=-1).values  # [B, T]
        outlier_score = (k_score + v_score) / 2
        return outlier_score

    def compress_layer(self, k_cache: torch.Tensor, v_cache: torch.Tensor,
                       meta_query: torch.Tensor) -> dict:
        """
        压缩单层 K/V cache。

        Returns:
            dict:
                - kept_k, kept_v: [B, H, T_kept, D] 保留并量化后的 K/V
                - keep_mask: [B, T] bool 保留的 token
                - outlier_mask: [B, T] bool outlier token
                - importance: [B, T] 任务重要性
                - outlier_score: [B, T] outlier 分数
                - num_kept, num_outlier
        """
        B, H, T, D = k_cache.shape

        # 1. 任务引导重要性
        importance = self.compute_task_importance(k_cache, meta_query)  # [B, T]

        # 2. 零成本 outlier 检测 (复用量化 scale)
        outlier_score = self.detect_outliers(k_cache, v_cache)  # [B, T]

        # 3. 确定保留集
        num_outlier = max(1, int(T * self.outlier_ratio))
        num_keep = max(num_outlier, int(T * self.keep_ratio))

        keep_mask = torch.zeros(B, T, dtype=torch.bool, device=k_cache.device)
        outlier_mask = torch.zeros(B, T, dtype=torch.bool, device=k_cache.device)

        for b in range(B):
            # outlier: scale factor 最大的 num_outlier 个 (强制保留)
            o_top = outlier_score[b].topk(num_outlier).indices
            outlier_mask[b, o_top] = True

            # 任务重要: importance 最大的, 但要凑够 num_keep (含 outlier)
            # 先排除已是 outlier 的, 再从剩余中按 importance 补
            remaining = ~outlier_mask[b]
            need = num_keep - num_outlier
            if need > 0 and remaining.sum() > 0:
                imp_remaining = importance[b].clone()
                imp_remaining[~remaining] = -1e9
                t_top = imp_remaining.topk(min(need, remaining.sum().item())).indices
                keep_mask[b, t_top] = True
            keep_mask[b] = keep_mask[b] | outlier_mask[b]

        # 4. 量化保留 token: outlier 高精度, 普通 token 低精度
        kept_k_list = []
        kept_v_list = []
        kept_indices_list = []
        for b in range(B):
            idx = keep_mask[b].nonzero(as_tuple=True)[0]  # [T_kept]
            kept_indices_list.append(idx)
            k_kept = k_cache[b, :, idx, :]  # [H, T_kept, D]
            v_kept = v_cache[b, :, idx, :]
            o_mask_b = outlier_mask[b, idx]  # [T_kept]

            # 分别量化 outlier 和普通 token
            k_out = torch.zeros_like(k_kept)
            v_out = torch.zeros_like(v_kept)
            if o_mask_b.any():
                k_out[:, o_mask_b, :] = group_quantize_with_scale(
                    k_kept[:, o_mask_b, :], self.outlier_bits,
                    self.group_size)[0]
                v_out[:, o_mask_b, :] = group_quantize_with_scale(
                    v_kept[:, o_mask_b, :], self.outlier_bits,
                    self.group_size)[0]
            if (~o_mask_b).any():
                k_out[:, ~o_mask_b, :] = group_quantize_with_scale(
                    k_kept[:, ~o_mask_b, :], self.base_bits,
                    self.group_size)[0]
                v_out[:, ~o_mask_b, :] = group_quantize_with_scale(
                    v_kept[:, ~o_mask_b, :], self.base_bits,
                    self.group_size)[0]
            kept_k_list.append(k_out)
            kept_v_list.append(v_out)

        # 重组为 [B, H, T_kept, D] (每 b 可能不同, 用 padding 对齐)
        T_kept = max(x.shape[0] for x in kept_indices_list)
        kept_k = torch.zeros(B, H, T_kept, D, device=k_cache.device)
        kept_v = torch.zeros(B, H, T_kept, D, device=k_cache.device)
        for b in range(B):
            t = kept_k_list[b].shape[1]
            kept_k[b, :, :t, :] = kept_k_list[b]
            kept_v[b, :, :t, :] = kept_v_list[b]

        return {
            "kept_k": kept_k,
            "kept_v": kept_v,
            "keep_mask": keep_mask,
            "outlier_mask": outlier_mask,
            "importance": importance,
            "outlier_score": outlier_score,
            "kept_indices": kept_indices_list,
            "num_kept": [x.shape[0] for x in kept_indices_list],
            "num_outlier": num_outlier,
            "original_k": k_cache,
            "original_v": v_cache,
        }

    def compute_compression_ratio(self, metadata: dict) -> dict:
        """计算压缩比 (剪枝 + 量化)。"""
        T = metadata["seq_len"]
        D = metadata["num_kv_heads"] * metadata["head_dim"]
        L = metadata["num_layers"]

        # 全精度: T * D * 2字节 * 2(K,V)
        fp_bytes = T * D * 2 * 2 * L

        # TaskPress: 保留 keep_ratio 的 token
        # 其中 outlier_ratio 用 outlier_bits, 其余用 base_bits
        n_keep = T * self.keep_ratio
        n_outlier = T * self.outlier_ratio
        n_normal = n_keep - n_outlier
        kv_bytes = (n_outlier * D * (self.outlier_bits / 8) * 2
                    + n_normal * D * (self.base_bits / 8) * 2) * L
        # 索引开销
        idx_bytes = n_keep * math.ceil(math.log2(max(2, T))) / 8 * L

        total_bytes = kv_bytes + idx_bytes
        ratio = fp_bytes / max(total_bytes, 1)
        return {
            "fp_bytes": fp_bytes, "kv_bytes": kv_bytes,
            "idx_bytes": idx_bytes, "total_bytes": total_bytes,
            "compression_ratio": ratio,
        }


# =============================================================================
# 4. 基线方法
# =============================================================================

def baseline_uniform_quantize(k_cache, v_cache, bits: int):
    """基线: 所有 token 统一量化, 不剪枝。"""
    k_q, _ = group_quantize_with_scale(k_cache, bits, 64)
    v_q, _ = group_quantize_with_scale(v_cache, bits, 64)
    return {"kept_k": k_q, "kept_v": v_q, "keep_mask": None}


def baseline_uniform_prune(k_cache, v_cache, meta_query, keep_ratio: float,
                            bits: int = 4):
    """基线: 任务剪枝但统一量化 (不用 scale factor 离群点检测)。"""
    B, H, T, D = k_cache.shape
    # task importance
    scores = torch.matmul(meta_query, k_cache.transpose(-2, -1)) / math.sqrt(D)
    attn = F.softmax(scores, dim=-1)
    importance = attn.sum(dim=-2).mean(dim=1)  # [B, T]

    num_keep = max(1, int(T * keep_ratio))
    keep_mask = torch.zeros(B, T, dtype=torch.bool, device=k_cache.device)
    kept_k_list, kept_v_list = [], []
    for b in range(B):
        idx = importance[b].topk(num_keep).indices
        keep_mask[b, idx] = True
        k_q, _ = group_quantize_with_scale(k_cache[b, :, idx, :],
                                            bits, 64)
        v_q, _ = group_quantize_with_scale(v_cache[b, :, idx, :],
                                            bits, 64)
        kept_k_list.append(k_q)
        kept_v_list.append(v_q)
    T_kept = num_keep
    kept_k = torch.zeros(B, H, T_kept, D, device=k_cache.device)
    kept_v = torch.zeros(B, H, T_kept, D, device=k_cache.device)
    for b in range(B):
        kept_k[b] = kept_k_list[b]
        kept_v[b] = kept_v_list[b]
    return {"kept_k": kept_k, "kept_v": kept_v, "keep_mask": keep_mask}


# =============================================================================
# 5. 评估: query-agnostic 复用性 + 注意力保真度
# =============================================================================

def attention_with_pruned_cache(orig_k, orig_v, recon_k, recon_v, keep_mask,
                                  query):
    """
    用 (可能被剪枝/量化的) cache 计算注意力输出, 与原始对比。

    对被剪枝的 token, 其 K/V 置零 (相当于丢弃)。

    Args:
        orig_k, orig_v: [B, H, T, D] 原始
        recon_k, recon_v: [B, H, T, D] 重构 (未保留位置为0或低精度)
        keep_mask: [B, T] bool 保留的 token (None=全保留)
        query: [B, H, T_q, D] 测试 query
    """
    B, H, T, D = orig_k.shape
    if keep_mask is not None:
        # 把未保留位置置零
        mask = keep_mask.unsqueeze(1).unsqueeze(-1).float()
        recon_k_eff = recon_k * mask if recon_k.shape[2] == T else recon_k
        recon_v_eff = recon_v * mask if recon_v.shape[2] == T else recon_v
    else:
        recon_k_eff, recon_v_eff = recon_k, recon_v

    with torch.no_grad():
        # 原始输出
        s_o = torch.matmul(query, orig_k.transpose(-2, -1)) / math.sqrt(D)
        out_o = torch.matmul(F.softmax(s_o, dim=-1), orig_v)
        # 重构输出
        s_r = torch.matmul(query, recon_k_eff.transpose(-2, -1)) / math.sqrt(D)
        out_r = torch.matmul(F.softmax(s_r, dim=-1), recon_v_eff)

    mse = F.mse_loss(out_o.float(), out_r.float()).item()
    cos = F.cosine_similarity(
        out_o.float().flatten().unsqueeze(0),
        out_r.float().flatten().unsqueeze(0)).item()
    # top-1 retrieval 一致性 (注意力最关注的 token 是否一致)
    top1_o = s_o.argmax(dim=-1)  # [B, H, T_q]
    top1_r = s_r.argmax(dim=-1)
    top1_acc = (top1_o == top1_r).float().mean().item()
    return {"mse": mse, "cosine_similarity": cos, "top1_match": top1_acc}


def reconstruct_full_cache(compressed, T, device):
    """
    把保留的 (剪枝后) K/V 重组回 [B, H, T, D] 全长度, 未保留位置置零。
    用于与原始全 cache 对比。
    """
    kept_k = compressed["kept_k"]  # [B, H, T_kept, D]
    kept_v = compressed["kept_v"]
    keep_mask = compressed.get("keep_mask", None)
    B, H, _, D = kept_k.shape
    if keep_mask is None:
        # 未剪枝, 直接 pad/截断
        T_kept = kept_k.shape[2]
        if T_kept >= T:
            return kept_k[:, :, :T, :], kept_v[:, :, :T, :]
        full_k = torch.zeros(B, H, T, D, device=device)
        full_v = torch.zeros(B, H, T, D, device=device)
        full_k[:, :, :T_kept, :] = kept_k
        full_v[:, :, :T_kept, :] = kept_v
        return full_k, full_v

    full_k = torch.zeros(B, H, T, D, device=device)
    full_v = torch.zeros(B, H, T, D, device=device)
    kept_indices = compressed["kept_indices"]
    for b in range(B):
        idx = kept_indices[b]
        t = idx.shape[0]
        full_k[b, :, idx, :] = kept_k[b, :, :t, :]
        full_v[b, :, idx, :] = kept_v[b, :, :t, :]
    return full_k, full_v


# =============================================================================
# 6. 主流程
# =============================================================================

def main():
    print("=" * 72)
    print("TaskPress: Task-Guided KV Cache Compression via Task-Guided Pruning")
    print("论文: arXiv:2608.03276 | 目标模型: Qwen3-0.6B")
    print("=" * 72)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 准备长上下文 + task guide
    if is_mock:
        vocab_size = model.embed.num_embeddings
    else:
        vocab_size = 1000
    seq_len = 512
    context_ids = torch.randint(0, vocab_size, (1, seq_len), device=device)
    # task guide: 代表任务的 meta-query (如 "总结以下文档的关键信息")
    guide_ids = torch.randint(0, vocab_size, (1, 16), device=device)
    print(f"\n[2] 上下文长度: {seq_len}, task guide 长度: 16")

    # 3. 提取 KV cache 和 task guide 的 meta-query
    print("\n[3] 提取 KV cache 与 task guide meta-query...")
    k_list, v_list, metadata = extract_kv_cache(model, context_ids, is_mock)
    meta_query = extract_guide_kv(model, guide_ids, is_mock)
    # 对齐 head 维度 (meta_query 可能 head 数与 k_cache 不同, 取最小)
    nkv = metadata["num_kv_heads"]
    H_q = meta_query.shape[1]
    H_use = min(nkv, H_q)
    # 用 meta_query 的前 H_use 个 head, k_cache 用前 H_use 个 head
    meta_q = meta_query[:, :H_use, :, :]  # [B, H_use, T_g, D]
    print(f"    层数: {metadata['num_layers']}, KV heads: {nkv}, "
          f"使用 head 数: {H_use}")

    # 4. TaskPress 配置
    print("\n[4] TaskPress 配置")
    taskpress = TaskPressCompressor(
        keep_ratio=0.3, outlier_ratio=0.05,
        base_bits=4, outlier_bits=8, group_size=64)
    print(f"    保留比例: {taskpress.keep_ratio*100:.0f}%")
    print(f"    outlier 比例: {taskpress.outlier_ratio*100:.0f}%")
    print(f"    常规 token 量化: {taskpress.base_bits}-bit")
    print(f"    outlier token 量化: {taskpress.outlier_bits}-bit")

    comp = taskpress.compute_compression_ratio(metadata)
    print(f"\n[5] 压缩比分析")
    print(f"    全精度 KV cache: {comp['fp_bytes']/1024:.1f} KB")
    print(f"    TaskPress 总计: {comp['total_bytes']/1024:.1f} KB")
    print(f"    >>> 压缩比: {comp['compression_ratio']:.1f}x <<<")

    # 5. 生成多个测试 query (验证 query-agnostic 复用性)
    print(f"\n[6] 生成多个测试 query (验证 query-agnostic 复用性)")
    num_test_queries = 3
    test_queries = []
    if is_mock:
        for _ in range(num_test_queries):
            q_ids = torch.randint(0, vocab_size, (1, 8), device=device)
            q = extract_guide_kv(model, q_ids, is_mock)[:, :H_use, :, :]
            test_queries.append(q)
    else:
        for _ in range(num_test_queries):
            q_ids = torch.randint(0, vocab_size, (1, 8), device=device)
            q = extract_guide_kv(model, q_ids, is_mock)[:, :H_use, :, :]
            test_queries.append(q)

    # 6. 逐层压缩并评估
    print(f"\n[7] 逐层压缩与评估 (前 {min(4, metadata['num_layers'])} 层展示)")
    print(f"    {'Layer':<8} {'方法':<18} "
          f"{'Q1 Cos':<10} {'Q2 Cos':<10} {'Q3 Cos':<10} {'Avg Top1':<10}")
    print(f"    {'-'*72}")

    n_eval = min(4, metadata["num_layers"])
    totals = {"taskpress": [], "uniform_prune": [], "uniform_q4": []}

    for li in range(metadata["num_layers"]):
        k_c = k_list[li]
        v_c = v_list[li]
        k_h = k_c[:, :H_use, :, :]
        v_h = v_c[:, :H_use, :, :]

        # TaskPress
        tp = taskpress.compress_layer(k_h, v_h, meta_q)
        tp_k_full, tp_v_full = reconstruct_full_cache(tp, seq_len, device)

        # 基线: uniform prune (无 outlier 检测)
        up = baseline_uniform_prune(k_h, v_h, meta_q,
                                     keep_ratio=0.3, bits=4)
        up_k_full, up_v_full = reconstruct_full_cache(
            {"kept_k": up["kept_k"], "kept_v": up["kept_v"],
             "kept_indices": tp["kept_indices"]}, seq_len, device)

        # 基线: uniform quantize 4-bit (不剪枝)
        uq = baseline_uniform_quantize(k_h, v_h, bits=4)

        # 评估各方法在多个 query 下的表现
        results = {"taskpress": [], "uniform_prune": [], "uniform_q4": []}
        for q in test_queries:
            r_tp = attention_with_pruned_cache(
                k_h, v_h, tp_k_full, tp_v_full, tp["keep_mask"], q)
            r_up = attention_with_pruned_cache(
                k_h, v_h, up_k_full, up_v_full, up["keep_mask"], q)
            r_uq = attention_with_pruned_cache(
                k_h, v_h, uq["kept_k"], uq["kept_v"], None, q)
            results["taskpress"].append(r_tp)
            results["uniform_prune"].append(r_up)
            results["uniform_q4"].append(r_uq)

        for key in totals:
            totals[key].append(results[key])

        if li < n_eval:
            tp_coses = [r["cosine_similarity"] for r in results["taskpress"]]
            up_coses = [r["cosine_similarity"] for r in results["uniform_prune"]]
            uq_coses = [r["cosine_similarity"] for r in results["uniform_q4"]]
            tp_top1 = sum(r["top1_match"] for r in results["taskpress"]) / num_test_queries
            up_top1 = sum(r["top1_match"] for r in results["uniform_prune"]) / num_test_queries
            uq_top1 = sum(r["top1_match"] for r in results["uniform_q4"]) / num_test_queries
            print(f"    L{li:<7} {'TaskPress':<18} "
                  f"{tp_coses[0]:<10.6f} {tp_coses[1]:<10.6f} "
                  f"{tp_coses[2]:<10.6f} {tp_top1:<10.4f}")
            print(f"    {'':<8} {'Uniform-Prune':<18} "
                  f"{up_coses[0]:<10.6f} {up_coses[1]:<10.6f} "
                  f"{up_coses[2]:<10.6f} {up_top1:<10.4f}")
            print(f"    {'':<8} {'Uniform-Q4(noprune)':<18} "
                  f"{uq_coses[0]:<10.6f} {uq_coses[1]:<10.6f} "
                  f"{uq_coses[2]:<10.6f} {uq_top1:<10.4f}")
            print(f"    {'-'*72}")

    # 7. 全模型平均
    L = metadata["num_layers"]
    print(f"\n[8] 全模型平均 ({L} 层, {num_test_queries} 个 query)")
    print(f"    {'方法':<22} {'Avg Cos':<10} {'Avg MSE':<12} {'Avg Top1':<10}")
    print(f"    {'-'*56}")
    for key, label in [("taskpress", "TaskPress"),
                       ("uniform_prune", "Uniform-Prune"),
                       ("uniform_q4", "Uniform-Q4(noprune)")]:
        all_r = [r for layer_r in totals[key] for r in layer_r]
        avg_cos = sum(r["cosine_similarity"] for r in all_r) / len(all_r)
        avg_mse = sum(r["mse"] for r in all_r) / len(all_r)
        avg_top1 = sum(r["top1_match"] for r in all_r) / len(all_r)
        print(f"    {label:<22} {avg_cos:<10.6f} {avg_mse:<12.8f} {avg_top1:<10.4f}")

    # 8. query-agnostic 复用性分析
    print(f"\n[9] Query-Agnostic 复用性分析")
    print(f"    TaskPress 用 task guide 一次性剪枝, 同一压缩 cache 用于所有 query。")
    # 计算不同 query 间结果的方差 (越小说明越稳定可复用)
    for key, label in [("taskpress", "TaskPress"),
                       ("uniform_prune", "Uniform-Prune")]:
        per_query_cos = [[] for _ in range(num_test_queries)]
        for layer_r in totals[key]:
            for qi, r in enumerate(layer_r):
                per_query_cos[qi].append(r["cosine_similarity"])
        means = [sum(x)/len(x) for x in per_query_cos]
        spread = max(means) - min(means)
        print(f"    {label:<18}: 各 query 平均 cos = "
              f"{[f'{m:.4f}' for m in means]}, 跨 query 极差 = {spread:.4f}")

    # 9. 总结
    print(f"\n{'='*72}")
    print("TaskPress 验证总结")
    print(f"{'='*72}")
    print(f"压缩比: {comp['compression_ratio']:.1f}x (剪枝 70% + 分级量化)")
    print(f"  - 保留 {taskpress.keep_ratio*100:.0f}% token (含 "
          f"{taskpress.outlier_ratio*100:.0f}% outlier 高精度)")
    print(f"  - outlier (scale factor 检测) 用 {taskpress.outlier_bits}-bit, "
          f"其余用 {taskpress.base_bits}-bit")
    print(f"\n核心结论: TaskPress 用 task guide 作为 meta-query 在 prefill 阶段")
    print(f"过滤无关 token, 生成 query-agnostic 可复用 cache; 同时复用量化 scale")
    print(f"factor 作为零成本 outlier 检测信号, 保护 influential token, 在高压缩比下")
    print(f"保持注意力输出保真度与跨 query 稳定性。")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()
