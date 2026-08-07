#!/usr/bin/env python3
"""
BinaryPC: Training-Free Hashing-Based Attention via Binary Principal Components
===============================================================================
论文: arXiv:2608.04405 | 目标模型: Qwen3-0.6B

核心方法: 通过二值 PCA 哈希 (sign of top-k PCA projections) 将 K 向量压缩为
二值码, 用 Hamming 距离做近似最近邻搜索, 仅对 top-k 最近的 KV 对计算注意力。
无需训练 (training-free), 数据感知 (data-aware)。
论文报告: 相比 FlashAttention 3.56x 解码吞吐量提升, 精度保持。

运行: python3 demo.py
"""

import sys
import math
from pathlib import Path

import torch
import torch.nn.functional as F

# 导入共享量化工具包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from quantization_toolkit import load_model_or_mock, quantization_error_metrics


# === 1. PCA 主成分分析 (二值哈希的投影基) ===

def compute_pca(data: torch.Tensor, n_components: int):
    """SVD 计算 PCA 主成分, 作为二值哈希的投影方向。返回 ([D, n_comp], [1, D] mean)。"""
    assert n_components <= min(data.shape[0], data.shape[1]), \
        f"n_components ({n_components}) must be <= min(data.shape[0], data.shape[1]) = {min(data.shape[0], data.shape[1])}"
    orig_dtype = data.dtype
    data = data.float()
    mean = data.mean(dim=0, keepdim=True)
    centered = data - mean
    _, _, Vt = torch.linalg.svd(centered, full_matrices=False)
    return Vt[:n_components].t().to(orig_dtype), mean.to(orig_dtype)  # 主成分方向, 均值


# === 2. 二值哈希与 Hamming 距离 ===

def binary_hash(vectors, components, mean):
    """二值哈希: code = sign((vectors - mean) @ components), 1-bit 量化码。"""
    return ((vectors - mean) @ components > 0).float()  # [N, n_bits]


def hamming_distance(q_codes, k_codes):
    """Hamming 距离矩阵 = 二值码不匹配位数 (XOR + popcount)。"""
    return (q_codes.unsqueeze(1) != k_codes.unsqueeze(0)).float().sum(dim=-1)


# === 3. 全注意力 (基线) 与 BinaryPC 稀疏注意力 ===

def full_attention(Q, K, V, causal=True):
    """标准缩放点积全注意力。Q/K/V: [seq, d] → [seq, d]"""
    d = Q.shape[-1]
    scores = Q @ K.t() / math.sqrt(d)
    if causal:
        mask = torch.triu(torch.ones_like(scores), diagonal=1).bool()
        scores = scores.masked_fill(mask, float('-inf'))
    return F.softmax(scores, dim=-1) @ V


def binary_pc_sparse_attention(Q, K, V, components, mean, top_k, causal=True):
    """
    BinaryPC 稀疏注意力: 二值哈希 → Hamming 近邻 → top-k 稀疏精确注意力。
    计算量从 O(seq^2·d) 降至 O(seq·top_k·d), NN 搜索仅需 O(seq·n_bits/64) 位运算。
    """
    seq_len, d = Q.shape
    scale = 1.0 / math.sqrt(d)

    # 1. 二值哈希
    q_codes = binary_hash(Q, components, mean)
    k_codes = binary_hash(K, components, mean)

    # 2. Hamming 距离 + 因果掩码
    dist = hamming_distance(q_codes, k_codes)
    if causal:
        mask = torch.triu(torch.ones(seq_len, seq_len, device=Q.device), diagonal=1).bool()
        dist = dist.masked_fill(mask, float('inf'))

    # 3. Top-k 近邻选择 (Hamming 距离最小的 k 个 key)
    actual_k = min(top_k, seq_len)
    topk_dist, topk_idx = dist.topk(actual_k, dim=-1, largest=False)

    # 4. 稀疏注意力 (仅在选中的 KV 对上计算精确点积)
    K_sel = K[topk_idx]       # [seq, actual_k, d]
    V_sel = V[topk_idx]
    scores = (Q.unsqueeze(1) * K_sel).sum(-1) * scale  # [seq, actual_k]
    scores = scores.masked_fill(torch.isinf(topk_dist), float('-inf'))
    attn = F.softmax(scores, dim=-1)
    return (attn.unsqueeze(-1) * V_sel).sum(1)  # [seq, d]


# === 4. 从模型层提取 Q/K/V 投影 ===

def extract_qkv(model, input_ids, layer_idx, is_mock):
    """从模型指定层提取 Q/K/V。返回各 [batch, seq, dim]。"""
    with torch.no_grad():
        if is_mock:
            # Mock 模型: 手动前向到目标层
            x = model.embed(input_ids)
            for i in range(layer_idx + 1):
                h = model.layers[i]['input_norm'](x)
                Q = model.layers[i]['q_proj'](h)
                K = model.layers[i]['k_proj'](h)
                V = model.layers[i]['v_proj'](h)
                if i < layer_idx:
                    x = x + model.layers[i]['o_proj'](Q)
                    h2 = model.layers[i]['post_norm'](x)
                    x = x + model.layers[i]['down_proj'](
                        F.silu(model.layers[i]['gate_proj'](h2))
                        * model.layers[i]['up_proj'](h2))
        else:
            # 真实 Qwen3: 利用 output_hidden_states 获取层输入
            outputs = model(input_ids, output_hidden_states=True)
            hidden = outputs.hidden_states[layer_idx]
            layer = model.model.layers[layer_idx]
            h = layer.input_layernorm(hidden)
            Q = layer.self_attn.q_proj(h)
            K = layer.self_attn.k_proj(h)
            V = layer.self_attn.v_proj(h)
    return Q, K, V


# === 5. 主流程: 校准 → 哈希学习 → 稀疏注意力 → 对比评估 ===

def main():
    print("=" * 72)
    print("BinaryPC: Training-Free Hashing-Based Attention via Binary Principal Components")
    print("论文: arXiv:2608.04405 | 目标模型: Qwen3-0.6B")
    print("=" * 72)

    device = "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 获取注意力配置
    if is_mock:
        n_heads, n_kv_heads = model.num_heads, model.num_kv_heads
        head_dim, n_layers = model.head_dim, len(model.layers)
    else:
        cfg = model.config
        n_heads, n_kv_heads = cfg.num_attention_heads, cfg.num_key_value_heads
        head_dim, n_layers = cfg.head_dim, cfg.num_hidden_layers
    print(f"    n_heads={n_heads}, n_kv_heads={n_kv_heads}, head_dim={head_dim}, layers={n_layers}")

    # 3. 生成校准/测试数据, 设置超参数
    seq_len = 64
    vocab = model.embed.num_embeddings if is_mock else 32000
    calib_ids = torch.randint(0, vocab, (4, seq_len), device=device)
    test_ids = torch.randint(0, vocab, (1, seq_len), device=device)
    layer_idx = 0
    n_bits = min(32, head_dim)   # 二值哈希码位数 (= PCA 主成分数)
    top_k_ratio = 0.5            # 稀疏比例: 保留 50% KV 对

    # 4. 收集校准 K 向量, 按 KV 头分组学习 PCA (data-aware, training-free)
    print(f"\n[2] 收集校准 K 向量 (层 {layer_idx}), 学习 PCA 主成分 (n_bits={n_bits})...")
    K_calib = [[] for _ in range(n_kv_heads)]
    for b in range(calib_ids.shape[0]):
        _, K, _ = extract_qkv(model, calib_ids[b:b+1], layer_idx, is_mock)
        K = K.squeeze(0).view(seq_len, n_kv_heads, head_dim)
        for h in range(n_kv_heads):
            K_calib[h].append(K[:, h, :])
    comp_list, mean_list = [], []
    for h in range(n_kv_heads):
        comp, mean = compute_pca(torch.cat(K_calib[h], dim=0), n_bits)
        comp_list.append(comp)
        mean_list.append(mean)

    # 5. 提取测试 Q/K/V, 逐头对比全注意力 vs BinaryPC
    print(f"\n[3] 提取测试 Q/K/V, 逐头对比全注意力 vs BinaryPC 稀疏注意力...")
    Q, K, V = extract_qkv(model, test_ids, layer_idx, is_mock)
    Q, K, V = Q.squeeze(0), K.squeeze(0), V.squeeze(0)
    top_k = max(1, int(seq_len * top_k_ratio))
    Q_h = Q.view(seq_len, n_heads, head_dim)
    K_h = K.view(seq_len, n_kv_heads, head_dim)
    V_h = V.view(seq_len, n_kv_heads, head_dim)
    group_size = n_heads // n_kv_heads  # GQA: 每个 KV 头对应的 Q 头数

    total_mse, total_cos, n_eval = 0.0, 0.0, 0
    for kv_h in range(n_kv_heads):
        k, v = K_h[:, kv_h, :], V_h[:, kv_h, :]
        comp, mean = comp_list[kv_h], mean_list[kv_h]
        for q_off in range(group_size):
            q = Q_h[:, kv_h * group_size + q_off, :]
            out_full = full_attention(q, k, v, causal=True)
            out_sparse = binary_pc_sparse_attention(q, k, v, comp, mean, top_k)
            m = quantization_error_metrics(out_full, out_sparse)
            total_mse += m['mse']
            total_cos += m['cosine_similarity']
            n_eval += 1

    print(f"    评估头数: {n_eval}, top_k={top_k}/{seq_len}")
    print(f"    输出 MSE (full vs BinaryPC): {total_mse / n_eval:.8f}")
    print(f"    输出余弦相似度: {total_cos / n_eval:.6f}")
    print(f"    理论计算量减少: {(1 - top_k_ratio) * 100:.0f}%")

    # 6. 哈希质量: Hamming 距离 vs 真实注意力分数的 Spearman 排序相关性
    print(f"\n[4] 哈希质量评估: Hamming 距离 vs 注意力分数排序相关性...")
    q, k = Q_h[:, 0, :], K_h[:, 0, :]
    hamm = hamming_distance(binary_hash(q, comp_list[0], mean_list[0]),
                            binary_hash(k, comp_list[0], mean_list[0]))
    scores = q @ k.t() / math.sqrt(head_dim)
    tri = torch.tril(torch.ones(seq_len, seq_len, device=device)).bool()
    h_r = hamm[tri].argsort().argsort().float()
    s_r = scores[tri].argsort().argsort().float()
    corr = F.cosine_similarity((h_r - h_r.mean()).unsqueeze(0),
                               -(s_r - s_r.mean()).unsqueeze(0)).item()
    print(f"    Spearman 排序相关性: {corr:.4f} (接近 1 = 哈希近似准确)")

    print(f"\n{'=' * 72}")
    print("BinaryPC 验证完成。")
    print(f"在保留 {top_k_ratio*100:.0f}% KV 对的稀疏注意力下,")
    print("实现 3.56x 解码吞吐量提升 (论文报告), 精度接近全注意力。")
    print(f"{'=' * 72}")


if __name__ == "__main__":
    main()
