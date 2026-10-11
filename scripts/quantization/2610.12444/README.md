# 2610.12444：Qwen3-0.6B 优化器状态量化复现

[论文](https://arxiv.org/abs/2610.12444) · [固定 v1 全文](https://arxiv.org/html/2610.12444v1)

本目录从10月11日未提交草稿复用经公式核对的实作，本轮重新验证 ZIP-SR 与 ZE-EDEN，真实运行 Qwen3-0.6B；不是论文全量预训练或 Tulu SFT 的复现。量化的是 AdamW 的一阶/二阶矩，模型推理权重保持 BF16，所训练参数保留 FP32 master。

## 算法对应

- §2.1：解码前一步 moment → 更新工作 moment → 更新参数 → 量化存储。避免把本步存储误差提前用于本步参数更新。
- §3.1：ZIP-SR 使用零包含 Dyn4，在 `h_t(v)=1/(sqrt(v/(1−β2^t))+ε)` 坐标中对相邻重建值随机舍入；不读取未来梯度。
- §3.2：ZE-EDEN 使用去零 Dyn4-NZ（最小 .00325），RTN 后用归一化形式 `sum(y²)/max(sum(y*q),1e−12)` 校准 scale，零块尺度为0。
- §4：一阶矩采用 NF4；默认 RTN，名字含 `lm_head` 的参数在最后10%步数切换状态空间 SR。真实 Qwen smoke 仅训练 q_proj，没有覆盖这一末段 LM-head 行为；NF4-SR 的条件期望有小张量解析测试。
- 附录A/B：flatten 后每128元素一个absmax尺度（下限1e−12），两个4bit索引打包为uint8；每moment每块一个FP32 scale。仅≥4096元素且元素数能被128整除的张量量化，其他保留FP32。
- β=(.9,.95)、ε=1e−8、gradient clipping=1、weight decay=0。每步重新选尺度，无离线数据校准集；ZE-EDEN校准随当前moment更新。

## 命令

在本目录执行：

```sh
python3 demo.py --test-only --output tests.json
python3 demo.py --mode zip_sr --steps 3 --output results_zip_sr.json
python3 demo.py --mode ze_eden --steps 3 --output results_ze_eden.json
python3 demo.py --mode fp32 --steps 3 --output results_fp32.json
PYTHONPYCACHEPREFIX=/private/tmp/arxiv_20261012_pycache python3 -m py_compile demo.py
```

`--model` 可指定本地 Qwen3-0.6B 路径；默认固定缓存 revision `c1899de289a04d12100db370d81485cdf75e47ca`，`local_files_only=True`。依赖 PyTorch、Transformers 及 tokenizer 依赖；本轮 Python3.9.6、torch2.8.0、transformers4.57.6，CPU4线程，BF16 autocast，eager attention。模型全前向，只有第一层 `q_proj.weight`（2048×1024）训练。其余参数冻结，3条人工短文本，最长32tokens，固定lr1e−5，未使用论文warmup/cosine调度和Tulu数据。loss监督全部非padding序列，未模拟最终assistant-only SFT mask。

## 实测

| 模式 | 三步训练 loss（不同文本，不可视为学习曲线） | moment字节 | 最大参数变化 |
|---|---|---:|---:|
| FP32 | 5.065597 / 6.056050 / 3.187395 | 16777216 | 3.00128e−5 |
| ZIP-SR | 5.065597 / 6.056050 / 3.196646 | 2228224 | 4.34048e−5 |
| ZE-EDEN | 5.065597 / 6.056050 / 3.170836 | 2228224 | 4.15915e−5 |

双moment存储从16MiB降到2.125MiB，即7.5294×。这是实际packed缓冲区大小，不包含模型、梯度、临时解码张量或Python对象；不能称整机峰值内存减少7.53倍。本轮运行日2026-10-12；ZIP-SR/ZE-EDEN/FP32分别31.00/29.46/29.53秒，没有融合GPU内核，因此不报告加速。

验证：nibble打包解包一致、两方法零块、Dyn4码本及最小正值、ZIP-SR预条件器期望（相对误差1.89e−16）、首步参数更新与FP32逐值一致、NF4-SR解析期望、真实后续递推与参数有限性通过。

未完成：全模型优化器状态训练、LM-head真实末段SR、论文多seed大规模预训练、Tulu与下游基准、GPU吞吐及峰值显存评估。真实限制是此处仅执行CPU小规模验证，未投入论文所用多H200训练预算；权重和依赖可用，不应归因为网络下载失败。
