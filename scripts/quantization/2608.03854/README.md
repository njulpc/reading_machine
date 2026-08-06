# Quantization Effects on Biomedical LLM Reliability

## 论文信息
- **标题**: Quantization Effects on Biomedical LLM Reliability
- **arXiv**: 2608.03854
- **作者**: Anton Rasmussen, Hong Qin
- **发表日期**: 2026-08-04
- **类别**: cs.LG
- **URL**: https://arxiv.org/abs/2608.03854

## 问题背景

当 decoder 语言模型被用作分类器时, 预测的类别概率依赖于多个实现选择:
- **prompt template** (提示模板)
- **verbalizer** (标签到 token 的映射)
- **scoring rule** (评分规则)

这些选择很少被当作实验变量来控制。论文对三个 Mistral-7B 变体 (Base, BioMistral, Instruct) 在 PubMed RCT 句子分类任务上 (n=2000) 进行了受控评估, 在 FP16/INT8/INT4 精度下使用四种 prompt 模板, 揭示了一个被忽视的问题: **概率提取协议主导了表观校准**。

## 方法概述

### 1. 两种 Scoring Rule
- **Summed token log-likelihood**: 对标签 token 的 log-likelihood 求和
  `score = sum_{t in label} log P(token_t | context, token_{<t})`
- **Mean token log-likelihood**: 对标签 token 的 log-likelihood 求平均
  `score = (1/|label|) * sum_{t in label} log P(token_t | ...)`

切换 scoring rule 会**反转模型间的校准排名**: BioMistral 的平均 ECE 从 0.097 升到 0.289, 而 Instruct 从 0.237 降到 0.096, 准确率变化不到 1 个百分点。

### 2. Prompt Template 效应
四种 answer-text prompt 模板产生 7-24 个百分点的准确率差异, 与模型级效应相当或更大。在某个模板上 BioMistral 超过 Instruct, 尽管总体均值仅差 1.3 个百分点。

### 3. 量化精度效应
- **INT8**: 对专用模型 (BioMistral, Instruct) 仅改变 1-2 个百分点的准确率/F1
- **INT4**: 产生异质但非灾难性的影响
- 基础模型在某些模板上显示更大的 INT8 效应 (最高 +4.2 个百分点)

### 4. Temperature Scaling
- 在 summed scoring 下降低 ECE
- 但仅对该评分规则有效, 对 mean scoring 无效

### 5. 校准度量: ECE
期望校准误差 (Expected Calibration Error):
```
ECE = sum_b (|B_b| / N) * |acc(B_b) - conf(B_b)|
```
将样本按置信度分箱, 每个 bin 内比较准确率与平均置信度。

## 代码使用说明

### 运行
```bash
cd scripts/quantization/2608.03854
python3 demo.py
```

### 核心组件
- `quantize_weights_per_channel`: per-channel 对称权重量化 (INT8/INT4)
- `quantize_model_weights`: 对模型所有 Linear 层执行权重量化
- `PROMPT_TEMPLATES`: 4 种 prompt 模板 (A_direct, B_instruction, C_context, D_completion)
- `classify_sample`: 对样本执行分类, 同时返回 summed 和 mean 两种 scoring 结果
- `score_label`: 计算 label token 的 log-likelihood
- `compute_ece`: 期望校准误差计算
- `TemperatureScaler`: Temperature scaling 后处理校准
- `generate_synthetic_dataset`: 生成模拟 PubMed RCT 句子分类数据集 (5 类)

### 实验设计
1. **实验1**: 量化精度 (FP16/INT8/INT4) x Scoring Rule (summed/mean) -> 准确率/F1/ECE
2. **实验2**: 4 种 Prompt Template 对准确率的影响 (量化 template 效应)
3. **实验3**: Scoring Rule 对校准的主导效应 + Temperature scaling 验证

脚本会自动尝试加载 Qwen3-0.6B; 若无法下载则使用 MockTransformer 保证可运行。

## 依赖项
- Python >= 3.8
- PyTorch >= 1.10
- transformers (用于加载 Qwen3-0.6B, 可选)
- 共享工具包 `quantization_toolkit.py` (上级目录)

## 文件列表
- `demo.py` - 论文核心方法实现与验证脚本
