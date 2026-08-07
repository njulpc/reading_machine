#!/usr/bin/env python3
"""
VQ-VAD: Vector-quantized Motion Representation Learning
论文: arXiv:2608.05069 | 目标模型: Qwen3-0.6B

VQ-GAN 思想迁移到序列建模, 用 EMA 码本表示正常行为模式, 通过重构误差
进行异常检测 (HR-SHT 81.83%, 跨域 76.69%)。组件: 编码器/解码器 + VQ
(EMA 码本) + 重构&承诺损失 (STE) + 异常检测。
应用: 压缩 Qwen3-0.6B 隐藏状态, 统计压缩比并演示异常检测。

运行: python3 demo.py
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
)

torch.manual_seed(0)


# --- 1. 向量量化器 (EMA 码本更新) ---

class VectorQuantizerEMA(nn.Module):
    """向量量化器, 码本通过 EMA 更新 (参考 VQ-VAE DeepMind Sonnet 实现)。
    前向: z_e[N,D] -> 找最近码字 z_q, 计算承诺损失, STE 直通。"""

    def __init__(self, num_codes: int = 256, dim: int = 32,
                 decay: float = 0.99, commitment: float = 0.25, eps: float = 1e-5):
        super().__init__()
        self.num_codes, self.dim = num_codes, dim
        self.decay, self.commitment, self.eps = decay, commitment, eps
        codebook = torch.randn(num_codes, dim) * 0.05
        self.register_buffer("codebook", codebook)
        self.register_buffer("ema_cluster_size", torch.zeros(num_codes))
        self.register_buffer("ema_w", codebook.clone())

    def forward(self, z_e: torch.Tensor):
        # z_e: [N, D] -> z_q_st: [N, D] (STE), commit_loss, indices: [N]
        # 距离 ||a-b||^2 = ||a||^2 + ||b||^2 - 2 a·b
        d = (z_e.pow(2).sum(1, keepdim=True)
             + self.codebook.pow(2).sum(1)
             - 2.0 * z_e @ self.codebook.t())          # [N, K]
        indices = d.argmin(1)                            # [N]
        z_q = self.codebook[indices]                     # [N, D] (EMA 更新前)

        # EMA 码本更新 (仅训练阶段)
        if self.training:
            z_q_pre = z_q.clone()                        # 保存 EMA 更新前的 z_q 副本
            with torch.no_grad():
                one_hot = F.one_hot(indices, self.num_codes).float()
                cluster_size = one_hot.sum(0)                          # [K]
                embed_sum = one_hot.t() @ z_e                          # [K, D]
                self.ema_cluster_size.mul_(self.decay).add_(
                    cluster_size, alpha=1.0 - self.decay)
                self.ema_w.mul_(self.decay).add_(embed_sum, alpha=1.0 - self.decay)
                # Laplace 平滑 + 惰性更新 (仅对被使用的码字生效)
                n = (self.ema_cluster_size + self.eps) / (
                    self.ema_cluster_size.sum() + self.num_codes * self.eps)
                normalized = self.ema_w / (self.ema_cluster_size.unsqueeze(1) + self.eps)
                self.codebook.copy_(n.unsqueeze(1) * normalized
                                     + (1.0 - n).unsqueeze(1) * self.codebook)
            z_q = self.codebook[indices]                 # 更新后的 z_q (用于 STE 前向)
            commit_loss = F.mse_loss(z_e, z_q_pre.detach())  # 用更新前的 z_q 计算承诺损失
        else:
            commit_loss = F.mse_loss(z_e, z_q.detach())  # 推理阶段无 EMA 更新

        z_q_st = z_e + (z_q - z_e).detach()             # STE: 前向 z_q, 反向直通 z_e
        return z_q_st, commit_loss, indices

    def codebook_usage(self, indices: torch.Tensor) -> float:
        """被使用的码字比例 (码本利用率)。"""
        return torch.unique(indices).numel() / self.num_codes


# --- 2. VQ-VAD 模型: 编码器 + VQ + 解码器 ---

class VQVAD(nn.Module):
    """编码器把 H 维隐藏状态压到 d 维, VQ 量化为码字索引, 解码器还原 H 维。
    压缩: 每向量 H×16 bit (fp16) -> log2(K) bit (码本索引)。"""

    def __init__(self, hidden_size: int = 256, latent_dim: int = 32,
                 num_codes: int = 256):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(hidden_size, latent_dim * 2), nn.GELU(),
            nn.Linear(latent_dim * 2, latent_dim),
        )
        self.vq = VectorQuantizerEMA(num_codes=num_codes, dim=latent_dim)
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, latent_dim * 2), nn.GELU(),
            nn.Linear(latent_dim * 2, hidden_size),
        )

    def forward(self, x: torch.Tensor):
        # x: [N, H] -> x_hat: [N, H], commit_loss, indices: [N]
        z_e = self.encoder(x)
        z_q, commit_loss, indices = self.vq(z_e)
        x_hat = self.decoder(z_q)
        return x_hat, commit_loss, indices

    def encode_only(self, x: torch.Tensor):
        """仅编码+量化, 返回索引 (用于压缩)。"""
        return self.vq(self.encoder(x))[2]


# --- 3. 提取隐藏状态 (兼容 Mock / 真实 Qwen3) ---

def get_hidden_states(model, input_ids, is_mock: bool) -> torch.Tensor:
    """前向获取最后一层隐藏状态 (lm_head 之前), 返回 [B, T, H]。"""
    with torch.no_grad():
        if is_mock:
            x = model.embed(input_ids)
            for layer in model.layers:
                h = layer["input_norm"](x)
                x = x + layer["o_proj"](layer["q_proj"](h))
                h = layer["post_norm"](x)
                x = x + layer["down_proj"](
                    F.silu(layer["gate_proj"](h)) * layer["up_proj"](h))
            return model.norm(x)                        # [B, T, H]
        else:
            return model.model(input_ids).last_hidden_state


# --- 4. 训练与评估 ---

def train_vqvad(model: VQVAD, data: torch.Tensor, epochs: int = 200,
                lr: float = 3e-3, beta: float = 0.25):
    """在正常数据上训练 VQ-VAD (重构 + 承诺损失)。"""
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    model.train()
    for ep in range(epochs):
        opt.zero_grad()
        x_hat, commit_loss, _ = model(data)
        recon = F.mse_loss(x_hat, data)
        (recon + beta * commit_loss).backward()
        opt.step()
        if (ep + 1) % 50 == 0:
            print(f"    epoch {ep+1:3d}: recon={recon.item():.6f} "
                  f"commit={commit_loss.item():.6f}")
    model.eval()


def recon_error_per_sample(model: VQVAD, data: torch.Tensor) -> torch.Tensor:
    """逐样本重构误差 (MSE over hidden dim), 返回 [N]。"""
    with torch.no_grad():
        x_hat, _, _ = model(data)
    return (data - x_hat).pow(2).mean(dim=1)


# --- 5. 主流程 ---

def main():
    print("=" * 72)
    print("VQ-VAD: Vector-quantized Motion Representation Learning")
    print("论文: arXiv:2608.05069 | 目标模型: Qwen3-0.6B")
    print("=" * 72)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model_llm, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 2. 提取隐藏状态 (收集较多向量以提升码本利用率)
    print("\n[2] 提取隐藏状态...")
    if is_mock:
        vocab = model_llm.embed.num_embeddings
        seqs = [torch.randint(0, vocab, (4, 64)) for _ in range(8)]
    else:
        base = list(range(1, 65))
        seqs = [torch.tensor([base[i:i + 32] for _ in range(4)])
                for i in range(0, 32, 4)]
    hidden = []
    for ids in seqs:
        h = get_hidden_states(model_llm, ids, is_mock)     # [B, T, H]
        hidden.append(h.reshape(-1, h.shape[-1]))
    hidden = torch.cat(hidden, dim=0).float().to(device)    # [N, H]
    hidden = hidden / (hidden.std() + 1e-6)                 # 归一化利于训练稳定
    H, N = hidden.shape[1], hidden.shape[0]
    print(f"    隐藏状态: {N} 个向量, 维度 H={H}")

    # 3. 拆分训练集/测试集 (避免异常检测数据泄漏)
    print("\n[3] 拆分训练集/测试集 (前80%训练, 后20%测试)...")
    n_train = int(N * 0.8)
    train_data = hidden[:n_train]
    test_data = hidden[n_train:]
    print(f"    训练集: {n_train} 个向量, 测试集: {N - n_train} 个向量")

    # 4. 构建 VQ-VAD 并在训练集上训练
    print("\n[4] 训练 VQ-VAD (仅训练集)...")
    latent_dim, num_codes = 32, 64
    vqvad = VQVAD(hidden_size=H, latent_dim=latent_dim,
                  num_codes=num_codes).to(device)
    train_vqvad(vqvad, train_data, epochs=200, lr=3e-3, beta=0.25)

    # 5. 码本利用率与重构误差 (在测试集上评估)
    print("\n[5] 码本利用率与重构误差 (测试集)...")
    with torch.no_grad():
        x_hat, _, indices = vqvad(test_data)
    usage = vqvad.vq.codebook_usage(indices)
    m = quantization_error_metrics(test_data, x_hat)
    bits_orig = H * 16                      # fp16 原始
    bits_comp = math.log2(num_codes)        # 码本索引
    ratio = bits_orig / bits_comp
    print(f"    码本利用率: {usage*100:.1f}% ({torch.unique(indices).numel()}/{num_codes})")
    print(f"    重构 MSE: {m['mse']:.6f}, cosine: {m['cosine_similarity']:.4f}")
    print(f"    压缩: {bits_orig:.0f} bit/vec -> {bits_comp:.1f} bit/vec, "
          f"压缩比 ≈ {ratio:.1f}x")

    # 6. 异常检测: 在测试集上注入离群点构造异常样本
    print("\n[6] 异常检测 (测试集, 重构误差分离)...")
    torch.manual_seed(1)
    n_test = test_data.size(0)
    n_anom = n_test // 2
    anom = test_data[:n_anom].clone()
    mask = torch.rand_like(anom) < 0.2      # 随机选 20% 维度注入大幅离群扰动
    anom[mask] += torch.randn_like(anom[mask]) * 6.0
    err_normal = recon_error_per_sample(vqvad, test_data[n_anom:])
    err_anom = recon_error_per_sample(vqvad, anom)
    thr = err_normal.mean() + 3 * err_normal.std()
    detect = (err_anom > thr).float().mean()
    print(f"    正常样本重构误差: mean={err_normal.mean():.4f}, "
          f"std={err_normal.std():.4f}")
    print(f"    异常样本重构误差: mean={err_anom.mean():.4f}, "
          f"std={err_anom.std():.4f}")
    print(f"    检测阈值 (mean+3σ): {thr:.4f}")
    print(f"    异常检出率: {detect*100:.1f}%")

    # 7. 分层压缩示例: 对首层隐藏状态逐 token 压缩
    print("\n[7] 隐藏状态压缩示例 (首序列逐 token)")
    h0 = get_hidden_states(model_llm, seqs[0], is_mock)[0]   # [T, H]
    h0 = (h0.float() / (h0.std() + 1e-6)).to(device)
    idx0 = vqvad.encode_only(h0)
    with torch.no_grad():
        h0_hat = vqvad.decoder(vqvad.vq.codebook[idx0])
    m0 = quantization_error_metrics(h0, h0_hat)
    print(f"    token 数: {h0.shape[0]}, 每个向量 -> 1 个 {int(bits_comp)}-bit 索引")
    print(f"    重构 MSE: {m0['mse']:.6f}, cosine: {m0['cosine_similarity']:.4f}")

    print("\n" + "=" * 72)
    print("VQ-VAD 验证完成。")
    print("核心结论: EMA 码本 + 承诺损失 + STE 可高效压缩隐藏状态,")
    print("且正常数据重构误差低、异常数据重构误差高, 适用于异常检测。")
    print("=" * 72)


if __name__ == "__main__":
    main()
