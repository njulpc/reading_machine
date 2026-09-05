# 2609.02735 — Qwen3-0.6B 数值验证

论文：[Choosing a PEFT Variant for Per-Patient Dysarthric ASR: A Single-Speaker Case Study on Two ASR Bases](https://arxiv.org/abs/2609.02735)。

低秩适配可改善个体构音障碍识别，但真实NF4 QLoRA在小规模实验中未表现出稳定内存优势。

## 实现范围

对LoRA、DoRA及NF4双重量化QLoRA做个体适配；单受试者409条约55分钟语音分成262/40/107条训练验证测试，rank16、alpha32。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

peft and bitsandbytes are absent; --native is provided but not executed. The CPU fallback covers all real Qwen3-0.6B backbone Linear weights with block-64 NF4 and a groupwise INT8 nested-scale proxy, then runs forward/generation; this is not native bitsandbytes QLoRA and does not train adapters. Private ASR checkpoint/audio unavailable; no CER or adapter-memory claim.

所有低比特张量均以FP32反量化值计算，未输出压缩检查点；因此不声称显存、吞吐或部署速度收益。误差指标与论文任务指标不同，单条文本的logit误差不能代替困惑度或准确率。

## 环境与运行

实测：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，macOS arm64 CPU（CUDA不可用）；随机种子42、CPU线程4。本次使用缓存的官方Qwen3-0.6B快照`c1899de289a04d12100db370d81485cdf75e47ca`。

通用依赖为`torch`、`transformers`及其分词器依赖。通过`snapshot_download(local_files_only=True)`先解析本地缓存路径，再加载分词器/权重，避免Transformers按模型名称触发额外网络元数据查询。先准备模型缓存；也可设置`QWEN_MODEL_PATH`指向本地模型目录。

从仓库根目录执行（本次同命令已执行，结果保存路径随后归档到本目录）：

```sh
python3 scripts/quantization/2609.02735/demo.py --output-json /tmp/2609.02735.json
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
  "linears": 196,
  "quantized_elements": 440401920,
  "native_QLoRA": false,
  "NF4_block": 64,
  "scale_block": 256,
  "cpu_nested_scale_quantization_tested": true,
  "heldout_logits": {
    "mse": 0.625730574131012,
    "relative_l2": 0.2469577193260193,
    "cosine": 0.9725313782691956
  },
  "generation": {"new_token_id": 104949, "new_token_text": "模型", "use_cache": false},
  "double_quantization_backend": "groupwise signed INT8 CPU proxy; not bitsandbytes",
  "boundary": "Native QLoRA was not executed; CPU nested-scale quantization is an engineering proxy.",
  "full_paper_reproduced": false,
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。

## 原生QLoRA可选路径

`python3 scripts/quantization/2609.02735/demo.py --native`启用bitsandbytes NF4双重量化与PEFT LoRA，使用本地四条文本做烟雾训练。该路径本次未执行：环境缺少`bitsandbytes`与`peft`，也没有论文的私有ASR检查点及语音。代码中的学习率 1e-4 与论文一致，但四条文本不等于论文的 5 epoch、约 80 步语音训练；不报告 CER 复现或显存收益。

## 代码审查与验证（2026-09-05）

- 一致性结论：**部分一致**。官方 v1 使用 rank 16、alpha 32、真实 4-bit NF4、double quantization、AdamW 1e-4、5 epoch，并在私有单说话人 ASR 数据上评估 CER/WER；本目录只能复核数值量化与可选 QLoRA 接口。
- 修复：默认路径由“仅量化第一层 q_proj、未测试二次量化”扩展为全部 196 个 backbone Linear（440,401,920 权重）的 block-64 NF4 和 scale-block-256 嵌套量化代理，并补量化后前向与生成。嵌套 scale 使用 signed INT8 工程代理，未冒充 bitsandbytes 原生格式。
- 实测命令：`python3 scripts/quantization/2609.02735/demo.py --output-json /private/tmp/2609.02735.review.json`；退出码 0，墙钟 3.23 秒；held-out logits cosine 0.972531，单 token 生成为“模型”。
- 真实 Qwen3-0.6B：**CPU 工程量化路径已跑通**；原生 bitsandbytes+PEFT QLoRA **未跑通**，原因是当前 macOS CPU 环境没有这两个依赖、无 CUDA，且论文 Qwen3-ASR-1.7B 检查点与患者语音均不公开。
