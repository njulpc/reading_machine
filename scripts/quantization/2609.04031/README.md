# 2609.04031 — Qwen3-0.6B 数值验证

论文：[DSAQuant: Denoising-Stage-Aligned Quantization-Aware Training for Video Generation](https://arxiv.org/abs/2609.04031)。

DSA 按去噪阶段切换监督来源，并把低比特误差与CFG调度共同处理。

## 实现范围

式5/6令教师权重随t从噪声端到数据端指数衰减，原生flow目标权重互补；式11在后期关闭CFG。W4A4使用逐通道权重和逐token激活的对称量化，W3A3使用非对称设置。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

Qwen is autoregressive, has no native denoising time, video target or CFG. Exact stage functions tested independently; full Qwen forward only validates W4A4. No DSA video training or VBench reproduction; paper needs 24-64 H20 GPUs and synthetic video data.

所有低比特张量均以FP32反量化值计算，未输出压缩检查点；因此不声称显存、吞吐或部署速度收益。误差指标与论文任务指标不同，单条文本的logit误差不能代替困惑度或准确率。

## 环境与运行

实测：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，macOS arm64 CPU（CUDA不可用）；随机种子42、CPU线程4。本次使用缓存的官方Qwen3-0.6B快照`c1899de289a04d12100db370d81485cdf75e47ca`。

通用依赖为`torch`、`transformers`及其分词器依赖。通过`snapshot_download(local_files_only=True)`先解析本地缓存路径，再加载分词器/权重，避免Transformers按模型名称触发额外网络元数据查询。先准备模型缓存；也可设置`QWEN_MODEL_PATH`指向本地模型目录。

从仓库根目录执行（本次同命令已执行，结果保存路径随后归档到本目录）：

```sh
python3 scripts/quantization/2609.04031/demo.py --output-json /tmp/2609.04031.json
```

可选指定检查点：

```sh
export QWEN_MODEL_PATH=/path/to/Qwen3-0.6B
```

校准文本与独立测试文本在`../numerics.py`明示。涉及全模型前向的验证使用不同的校准/测试文本；算子与码本测试仅检验组件误差，不做泛化声称。

## 实测结果与配置

```json
{
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca",
  "parameters": 596049920,
  "linears": 196,
  "quantized_elements": 440401920,
  "heldout_logits": {
    "mse": 38.04582214355469,
    "relative_l2": 1.9256565570831299,
    "cosine": 0.7040231227874756
  },
  "generation": {"new_token_id": 220, "new_token_text": " ", "use_cache": false},
  "calibration_texts": [],
  "quantization": "symmetric W4A4",
  "storage": "FP32 dequantized reference; no physical memory reduction claimed",
  "full_paper_reproduced": false,
  "stage_equations": "5/6/11 endpoint and gradient tests PASS",
  "alpha": 5.0,
  "scheduler_steps": 50,
  "cfg_drop_steps": 9,
  "tau": 0.82,
  "hyperparameter_provenance": "paper-selected alpha=5 and final-nine-step CFG drop on the paper 50-step scheduler",
  "boundary": "Qwen is autoregressive, has no native denoising time, video target or CFG. Exact stage functions tested independently; full Qwen forward/generation only validates symmetric W4A4. No DSA video training or VBench reproduction; paper needs 24-64 H20 GPUs and synthetic video data.",
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。

## 代码审查与验证（2026-09-05）

- 一致性结论：**部分一致**。式（5）（6）的 KD/target 指数混合、式（11）的后期 CFG 关闭，以及静态逐通道 W4、动态逐 token A4 已按官方 v1 核对；Qwen 没有视频去噪时间、flow target 或 CFG，无法成为 DSAQuant 训练复现。
- 修复：把无依据的 `alpha=3`、`tau=0.9` 改为论文消融选定的 `alpha=5`，并按 50-step scheduler 的最后 9 步计算 `tau=0.82`；补齐量化后生成。端点、边界和梯度均有断言。
- 实测命令：`python3 scripts/quantization/2609.04031/demo.py --output-json /private/tmp/2609.04031.review.json`；退出码 0，墙钟 2.53 秒；196 个 Linear、440,401,920 权重完成 W4A4，held-out logits cosine 0.704023，单 token 生成成功但为空格，表明该直接迁移质量很差。
- 真实 Qwen3-0.6B：**对称 W4A4 工程路径已跑通**，覆盖权重替换、动态激活量化、前向和生成；视频 QAT、CFG 推理、VBench 和 24–64 张 H20 训练未跑通。
