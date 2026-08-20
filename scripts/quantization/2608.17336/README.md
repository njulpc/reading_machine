# TileMix（arXiv:2608.17336）Qwen3-0.6B 复现

本目录复现论文的核心数值机制：把 causal attention 的 QK score 矩阵划为硬件对齐 tile group，用静态 bitmask 为每组选择浮点或 INT8 QK 路径；全部合法 token 连接保留，V/PV 保持浮点。脚本从本机 Hugging Face 缓存读取 **Qwen3-0.6B 的真实权重**，提取第 0 层真实 Q/K/V，并相对全浮点 attention 报告误差。

## 对应论文设置

- 粒度：`tile_size × (tile_size × group_factor)` score tile group。
- INT8：Q/K 按 token、head 在 head_dim 上做对称 scale，code 范围 `[-127,127]`；浮点与 INT8 score 回到共同浮点域后共享 causal softmax。
- 路由：论文主实验是 data-free 静态空间模板。本复现使用 SpTrans-inspired 模板，优先把远历史 tile 量化，分别测 25/50/75/100% coverage。
- 校准：算法本身**不需要数据校准或训练**；固定中英 prompt 只用来取得 Qwen3 的真实激活并测量数值误差。
- 关键边界：这是可移植的参考实现，会显式物化 score 矩阵；没有复刻论文 A100 Triton 的 packed 64-bit mask、online-softmax kernel 或吞吐数字。

## 运行

```bash
HF_HUB_OFFLINE=1 python demo.py --model Qwen/Qwen3-0.6B --seq-len 96 --tile-size 16
```

无 Transformers/权重时可先验证核心算子：

```bash
python demo.py --self-test --seq-len 96
```

## 本次验证

运行环境：Apple Silicon CPU、PyTorch 2.8.0、Transformers 4.57.6；从本机完整缓存读取 596,049,920 参数的 Qwen3-0.6B，并提取第 0 层 `(1,16,96,128)` Q/K/V。

| 请求 INT8 coverage | 实际 causal cell coverage | MAE vs FP | 最大绝对误差 | cosine |
|---:|---:|---:|---:|---:|
| 25% | 28.87% | 0.00062068 | 0.12546974 | 0.99978173 |
| 50% | 57.73% | 0.00177458 | 0.22155227 | 0.99898285 |
| 75% | 84.66% | 0.00540970 | 0.61864328 | 0.99184644 |
| 100% | 100.00% | 0.01488368 | 0.85039097 | 0.96480840 |

真实权重运行与 deterministic synthetic self-test 均输出 `validation=PASS`。coverage 的差异来自 causal 三角区域与 tile 分组离散性；不把 CPU 参考实现耗时伪装成论文的 A100 kernel 加速。
