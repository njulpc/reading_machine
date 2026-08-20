# 2608.18578：Qwen3-0.6B 主动干扰量化复现

本目录复现论文的核心评测问题：同一 key 被连续改写后，低精度模型是否更容易回答旧值。实验使用本机缓存的真实 **Qwen3-0.6B（596,049,920 参数）**，同时构造语义相似 word-type 和数字控制任务，并按干扰级别报告最新值准确率与旧值 intrusion rate。

## 数值路径与论文边界

论文使用 CUDA bitsandbytes 的 FP16、`LLM.int8()` 和 NF4+double quantization。本机没有 CUDA/MPS 和 bitsandbytes，因此：

- FP16 标签表示未 fake-quant 的 FP32 CPU 基线，避免 CPU 半精度算子不支持；
- INT8 是 backbone `Linear` 权重的 per-output-channel 对称 fake quant；
- NF4 使用 bitsandbytes NF4 16 值 codebook、64-weight block absmax，并对 scale 做 256-block INT8 double-quant 近似；
- embedding 与 `lm_head` 保持浮点，和论文“主要效应来自 backbone、默认 lm_head 未量化”的主条件一致；
- fake-quant 权重立即反量化到 FP32，因此验证的是数值扰动，不声称模型文件压缩、INT8/NF4 kernel 或吞吐复现。

这篇论文提出的是行为评测而非新量化器，所以代码重点实现同 key 重绑定、逐样本候选评分、word/numeric 对照与 intrusion 归因。默认每种精度对干扰级别 0/1/2/4/8 各做 12 次，seed=42。

## 运行

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py --self-test
```

快速小规模真实模型验证：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py \
  --levels 0,2,4 --trials 4 --batch-size 4
```

完整默认验证：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py
```

如需便于日志审计的一行一结果输出，可追加 `--compact`。

## 验证记录（2026-08-21）

实际执行：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py \
  --self-test --levels 0,1,2,4,8 --trials 12 --batch-size 12 --compact
```

- `self_test=PASS`；真实加载 Qwen3-0.6B 的 596,049,920 个参数。
- INT8 与 NF4 均量化 440,401,920 个 backbone `Linear` 权重元素；平均绝对权重误差分别为 0.00021444 和 0.00200510。
- word-type 最新值准确率（干扰 0/1/2/4/8）：FP32 基线 `1.000/0.917/0.500/0.417/0.250`，INT8 `1.000/0.917/0.583/0.333/0.333`，NF4 `1.000/0.833/0.333/0.333/0.167`。
- word-type intrusion rate：FP32 基线 `0.000/0.083/0.500/0.583/0.750`，INT8 `0.000/0.083/0.417/0.667/0.667`，NF4 `0.000/0.167/0.667/0.667/0.833`。
- numeric 控制准确率：FP32 基线 `1.000/1.000/0.917/0.917/0.500`，INT8 `1.000/1.000/1.000/1.000/0.500`，NF4 `1.000/0.833/0.833/0.417/0.250`。
- 三种模式的量化加评测用时分别为 9.58、9.67、9.35 秒（CPU；不宜解读为推理速度）。

结果在这个小样本上复现了论文的方向性观察：干扰增强时旧值侵入率上升，NF4 的 word-type 退化最明显。不过，准确率只代表 Qwen3-0.6B、12 次/格、候选受限评分和可移植 fake-quant；本机没有 CUDA/MPS 与 bitsandbytes，因此不与论文 4–7B 的原生 kernel 数字等同，也不据此声称精确复现其效应量。
