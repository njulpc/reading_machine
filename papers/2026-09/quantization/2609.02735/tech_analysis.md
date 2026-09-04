# Choosing a PEFT Variant for Per-Patient Dysarthric ASR: A Single-Speaker Case Study on Two ASR Bases

- arXiv ID：2609.02735
- 作者：Bernard Muller, László Tóth, LaVonne Roberts
- v1实际提交：2026-09-02T15:42:48Z（UTC）；2026-09-02T23:42:48+08:00（Asia/Shanghai）
- 主分类：Computation and Language (cs.CL)；全部分类：Computation and Language (cs.CL) ; Sound (cs.SD)
- 本次归类：量化；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.02735)；[官方HTML全文](https://arxiv.org/html/2609.02735)；[PDF](https://arxiv.org/pdf/2609.02735)

## 1. 核心速览

研究主题：量化。低秩适配可改善个体构音障碍识别，但真实NF4 QLoRA在小规模实验中未表现出稳定内存优势。

## 2. 研究背景与动机

个体化语音数据少且训练资源有限，需要比较适配质量与量化代价。

## 3. 核心方法与创新点

- 对LoRA、DoRA及NF4双重量化QLoRA做个体适配
- 单受试者409条约55分钟语音分成262/40/107条训练验证测试，rank16、alpha32。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.02735)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

两种模型上的LoRA CER为13.86/28.10，真正量化的QLoRA为14.56/30.09；该规模未观察到显存节省。表1带†的QLoRA关闭量化，不能当NF4结果。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 6 | 两种模型上的LoRA CER为13.86/28.10，真正量化的QLoRA为14.56/30.09；该规模未观察到显存节省。表1带†的QLoRA关闭量化，不能当NF4结果。 |
| 压缩倍率 | 5 | 两种模型上的LoRA CER为13.86/28.10，真正量化的QLoRA为14.56/30.09；该规模未观察到显存节省。表1带†的QLoRA关闭量化，不能当NF4结果。 |
| 创新性 | 5 | 对LoRA、DoRA及NF4双重量化QLoRA做个体适配；单受试者409条约55分钟语音分成262/40/107条训练验证测试，rank16、alpha32。 |
| 可复现性 | 4 | 语音及部分基础检查点不可公开取得，且单个体和测试集反复选择限制泛化。Qwen默认只验证真实NF4码本；原生QLoRA路径已写但依赖未安装，未执行。 |

本地验证：以真实Qwen3-0.6B权重运行数值组件，结果状态`executed`，`full_paper_reproduced=false`。详见[README](../../../../scripts/quantization/2609.02735/README.md)及[原始结果](../../../../scripts/quantization/2609.02735/results.json)。

peft and bitsandbytes are absent; --native is provided but not executed. CPU test validates NF4 codebook on real Qwen weights only. Private ASR checkpoint/audio unavailable; no CER or adapter-memory claim.

## 5. 局限性与未来展望

语音及部分基础检查点不可公开取得，且单个体和测试集反复选择限制泛化。Qwen默认只验证真实NF4码本；原生QLoRA路径已写但依赖未安装，未执行。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

应先确认配置实际启用了量化，再讨论QLoRA质量或显存；方法名称不能代替运行证据。
