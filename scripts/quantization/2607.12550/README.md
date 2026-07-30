# Paper: 2607.12550 — A JoLT for the KV Cache: Near-Lossless KV Cache Compression via Joint Tucker and JL-Residual

Run: `python3 demo.py`

## 复现内容
- KV 张量低秩主体（Tucker/SVD）与残差尾部的能量分解演示；
- JoLT 编解码：SVD 主体 + Johnson-Lindenstrauss 随机投影残差，等存储下与 Tucker-only 对比；
- 以 Qwen3-0.6B 第 0 层真实 K cache 做 JoLT 重建验证。

## 验证方式
- [1][2] 合成 KV 张量上的能量谱与重建余弦对比（核心机理）；
- [4] 真实 Qwen/Qwen3-0.6B 前向取 K cache，JoLT 压缩-解压后报告余弦相似度（无模型时跳过并注明）。
