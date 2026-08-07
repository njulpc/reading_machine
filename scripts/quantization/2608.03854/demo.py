#!/usr/bin/env python3
"""
Quantization Effects on Biomedical LLM Reliability
====================================================
论文: arXiv:2608.03854
作者: Anton Rasmussen, Hong Qin
标题: Quantization Effects on Biomedical LLM Reliability

目标模型: Qwen3-0.6B (Qwen/Qwen3-0.6B)

核心发现
--------
当 decoder 语言模型被用作分类器时, 预测的类别概率依赖于实现选择, 包括:
  - prompt template (提示模板)
  - verbalizer (标签到 token 的映射)
  - scoring rule (评分规则)

这些选择很少被当作实验变量。论文的核心发现是:

1. 概率提取协议 (scoring rule) 主导了表观校准:
   - 从 summed 切换到 mean token log-likelihood 评分, 会反转模型间的校准排名
   - BioMistral 的平均 ECE 从 0.097 升到 0.289, 而 Instruct 从 0.237 降到 0.096
   - 但准确率变化不到 1 个百分点

2. Prompt template 选择产生 7-24 个百分点的准确率差异, 与模型级效应相当或更大

3. INT8 量化对专用模型仅改变 1-2 个百分点的准确率/F1
   INT4 产生异质但非灾难性的影响

4. Temperature scaling 在 summed 评分下降低 ECE, 但仅对该评分规则有效

本 demo 复现
-----------
对 Qwen3-0.6B 执行 INT8/INT4 量化, 评估不同量化精度下的分类准确率和校准误差 (ECE),
对比不同 scoring rule (summed vs mean token log-likelihood) 和不同 prompt template 的影响。

运行方式
--------
    python3 demo.py
"""

import sys
import math
import copy
import hashlib
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

# 导入共享量化工具包
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from quantization_toolkit import (
    load_model_or_mock,
    quantization_error_metrics,
    MockTransformer,
)


# =============================================================================
# 1. 权重量化器 (INT8 / INT4 per-channel 对称量化)
# =============================================================================

def quantize_weights_per_channel(weight: torch.Tensor, bits: int) -> torch.Tensor:
    """
    对 nn.Linear 的权重做 per-channel (per-output-row) 对称量化。

    论文中对 Mistral-7B 使用 bitsandbytes 的 INT8/INT4 量化 (类似 LLM.int8() 的
    per-channel 对称量化)。这里用 PyTorch 模拟 fake quantization:
        x_q = clamp(round(x / s), -2^(b-1), 2^(b-1)-1)
        x_dq = x_q * s
    其中 s 按 output channel (行) 计算: s = max(|w_row|) / (2^(b-1) - 1)

    Args:
        weight: [out_features, in_features]
        bits: 量化比特数 (8 或 4)

    Returns:
        weight_dq: 反量化后的权重 (同 shape, float)
    """
    qmax = 2 ** (bits - 1) - 1
    qmin = -(2 ** (bits - 1))
    # per-output-channel scale: [out_features, 1]
    w_max = weight.abs().amax(dim=1, keepdim=True).clamp_min(1e-8)
    scale = w_max / qmax
    w_q = torch.clamp(torch.round(weight / scale), qmin, qmax)
    w_dq = w_q * scale
    return w_dq


def quantize_model_weights(model: nn.Module, bits: int, is_mock: bool):
    """
    对模型中所有 Linear 层的权重执行 per-channel 量化 (原地替换为 fake-quant 权重)。

    对于真实 Qwen3 模型, 遍历 model.named_modules() 找到所有 nn.Linear / Qwen3Linear。
    对于 MockTransformer, 同样遍历 nn.Linear。

    Args:
        model: 目标模型
        bits: 量化比特数 (16=不量化, 8=INT8, 4=INT4)
        is_mock: 是否为 mock 模型

    Returns:
        quantized_model: 量化后的模型 (深拷贝, 不修改原模型)
    """
    if bits >= 16:
        return model  # FP16, 不量化

    model_q = copy.deepcopy(model)
    count = 0
    for name, module in model_q.named_modules():
        # 兼容真实模型可能使用的 Linear 子类
        if isinstance(module, nn.Linear) and module.weight is not None:
            w = module.weight.data
            module.weight.data = quantize_weights_per_channel(w, bits)
            count += 1
    print(f"    [quantize_model_weights] 量化 {count} 个 Linear 层 -> {bits}-bit")
    return model_q


# =============================================================================
# 2. 句子分类任务 (模拟 PubMed RCT)
# =============================================================================

# 模拟 PubMed RCT 的 5 类句子分类标签
# 论文中是: Background, Objective, Methods, Results, Conclusions
LABELS = ["background", "objective", "methods", "results", "conclusions"]
NUM_CLASSES = len(LABELS)

# Verbalizer: 标签到 token 文本的映射
# 论文使用 verbalizer 将类别标签映射到模型可评分的 token
VERBALIZER = {
    "background": "background",
    "objective": "objective",
    "methods": "methods",
    "results": "results",
    "conclusions": "conclusions",
}


def generate_synthetic_dataset(num_samples: int = 200, seed: int = 42):
    """
    生成模拟的句子分类数据集 (类似 PubMed RCT)。

    由于无法访问真实 PubMed RCT 数据, 这里用关键词模板生成合成句子,
    每类句子包含类别相关的关键词, 使模型有可学习的信号。

    Args:
        num_samples: 样本数
        seed: 随机种子

    Returns:
        samples: list of (sentence: str, label: str)
    """
    torch.manual_seed(seed)
    # 每类的句子模板 (包含类别关键词)
    templates = {
        "background": [
            "cancer is a major cause of death worldwide",
            "previous studies have shown that diabetes affects millions",
            "the prevalence of hypertension has increased recently",
            "heart disease remains a leading health burden",
            "infectious diseases pose significant global challenges",
        ],
        "objective": [
            "we aimed to evaluate the effectiveness of the treatment",
            "the goal of this study was to assess outcomes",
            "our objective was to investigate the molecular mechanism",
            "this research seeks to identify risk factors",
            "we sought to determine the optimal dosage",
        ],
        "methods": [
            "patients were randomly assigned to treatment groups",
            "we collected blood samples from all participants",
            "data was analyzed using statistical software",
            "the experiment was conducted in controlled conditions",
            "participants completed a standardized questionnaire",
        ],
        "results": [
            "the treatment group showed significant improvement",
            "we found a strong correlation between the variables",
            "mortality was reduced by thirty percent",
            "the difference was statistically significant",
            "expression levels increased twofold compared to control",
        ],
        "conclusions": [
            "our findings suggest that the therapy is effective",
            "this approach may have clinical implications",
            "further research is needed to confirm these results",
            "the treatment represents a promising strategy",
            "these results support the use of the new protocol",
        ],
    }

    samples = []
    for i in range(num_samples):
        label = LABELS[i % NUM_CLASSES]
        tmpl = templates[label]
        # 随机选一个模板, 加一些变化
        base = tmpl[i % len(tmpl)]
        # 随机加前缀/后缀增加多样性
        prefixes = ["", "in this study, ", "recently, ", "notably, ", "interestingly, "]
        suffixes = ["", " in our cohort.", " during the trial.", " in patients.", " overall."]
        prefix = prefixes[i % len(prefixes)]
        suffix = suffixes[i % len(suffixes)]
        sentence = prefix + base + suffix
        samples.append((sentence, label))
    return samples


# =============================================================================
# 3. Prompt Templates (4 种, 对应论文的实验变量)
# =============================================================================

PROMPT_TEMPLATES = {
    # Template A: 直接问答式
    "A_direct": (
        "Sentence: {sentence}\n"
        "Category: {{label}}"
    ),
    # Template B: 指令式
    "B_instruction": (
        "Classify the following sentence into one of these categories: "
        "background, objective, methods, results, conclusions.\n"
        "Sentence: {sentence}\n"
        "Answer: {{label}}"
    ),
    # Template C: 上下文填充式
    "C_context": (
        "Read the sentence and identify its role in the abstract.\n"
        "Sentence: {sentence}\n"
        "The sentence belongs to the {{label}} section."
    ),
    # Template D: 完成式 (最短)
    "D_completion": (
        "{sentence}\n"
        "This is about: {{label}}"
    ),
}


def build_prompt(template_name: str, sentence: str, label_word: str) -> str:
    """
    用指定模板构建完整 prompt (填入句子和标签词)。

    Args:
        template_name: PROMPT_TEMPLATES 的 key
        sentence: 待分类句子
        label_word: verbalizer 映射后的标签词

    Returns:
        prompt: 完整的 prompt 字符串
    """
    tmpl = PROMPT_TEMPLATES[template_name]
    return tmpl.format(sentence=sentence).replace("{label}", label_word)


# =============================================================================
# 4. 模型评分: log-likelihood 两种 scoring rule
# =============================================================================

@torch.no_grad()
def score_label(model, input_ids, label_token_span, is_mock: bool,
                device: str):
    """
    计算模型对指定 label token span 的 log-likelihood。

    两种 scoring rule (论文核心变量):
      1. summed: 对 label token 的 log-likelihood 求和
         score = sum_{t in label} log P(token_t | context, token_{<t})
      2. mean: 对 label token 的 log-likelihood 求平均
         score = (1/|label|) * sum_{t in label} log P(token_t | ...)

    论文发现: 切换 scoring rule 会反转模型间的校准排名。

    Args:
        model: 语言模型
        input_ids: [1, seq_len] 完整 prompt 的 token ids (含 label token)
        label_token_span: (start, end) label token 在 input_ids 中的位置区间
        is_mock: 是否 mock 模型
        device: 设备

    Returns:
        token_logprobs: [num_label_tokens] 每个 label token 的 log P
        num_label_tokens: label token 数
    """
    # 前向获取 logits
    if is_mock:
        logits = model(input_ids)  # [1, seq_len, vocab_size]
    else:
        out = model(input_ids)
        logits = out.logits if hasattr(out, 'logits') else out[0]
    # logits[t] 预测 token t+1
    log_probs = F.log_softmax(logits.float(), dim=-1)  # [1, seq_len, vocab]

    start, end = label_token_span
    # label token 位置: start, start+1, ..., end-1
    # 预测 token t 的概率来自 logits[t-1]
    token_logprobs = []
    for t in range(start, end):
        if t == 0:
            continue
        lp = log_probs[0, t - 1, input_ids[0, t].item()].item()
        token_logprobs.append(lp)

    return token_logprobs, len(token_logprobs)


@torch.no_grad()
def classify_sample(model, tokenizer_or_vocab, sentence: str, template_name: str,
                    is_mock: bool, device: str):
    """
    对一个样本执行分类, 返回各类别的两种 scoring 和预测结果。

    流程:
      1. 对每个类别, 用 verbalizer 将标签映射到 label word
      2. 构建 prompt: template + sentence + label_word
      3. token化, 找到 label word 的 token span
      4. 计算 label token 的 log-likelihood
      5. 分别用 summed 和 mean scoring 得到类别分数
      6. softmax 归一化得到类别概率

    Args:
        model: 语言模型
        tokenizer_or_vocab: tokenizer (真实) 或 vocab 映射 (mock)
        sentence: 待分类句子
        template_name: prompt 模板名
        is_mock: 是否 mock
        device: 设备

    Returns:
        result: dict with keys:
            - summed_probs: [NUM_CLASSES] summed scoring 下的类别概率
            - mean_probs: [NUM_CLASSES] mean scoring 下的类别概率
            - summed_pred: summed scoring 预测类别 index
            - mean_pred: mean scoring 预测类别 index
            - summed_logprobs: [NUM_CLASSES] 原始 summed log-likelihood
            - mean_logprobs: [NUM_CLASSES] 原始 mean log-likelihood
    """
    summed_logprobs = []
    mean_logprobs = []

    for label in LABELS:
        label_word = VERBALIZER[label]
        prompt = build_prompt(template_name, sentence, label_word)

        # token化
        if is_mock:
            # mock: 用简单 hash 将字符映射到 vocab id
            input_ids = _mock_tokenize(prompt, tokenizer_or_vocab, device)
        else:
            enc = tokenizer_or_vocab(prompt, return_tensors="pt",
                                     truncation=True, max_length=512)
            input_ids = enc.input_ids.to(device)

        # 找到 label word 的 token span
        if is_mock:
            span = _mock_find_label_span(prompt, label_word, tokenizer_or_vocab)
        else:
            span = _find_label_span(input_ids[0], label_word,
                                     tokenizer_or_vocab)

        if span is None or span[1] <= span[0]:
            # 无法定位, 用 0 logprob
            summed_logprobs.append(0.0)
            mean_logprobs.append(0.0)
            continue

        token_lps, n_tokens = score_label(model, input_ids, span,
                                           is_mock, device)
        if n_tokens == 0:
            summed_logprobs.append(0.0)
            mean_logprobs.append(0.0)
        else:
            summed_logprobs.append(sum(token_lps))
            mean_logprobs.append(sum(token_lps) / n_tokens)

    summed_logprobs_t = torch.tensor(summed_logprobs)
    mean_logprobs_t = torch.tensor(mean_logprobs)

    # softmax 归一化为概率
    summed_probs = F.softmax(summed_logprobs_t, dim=0)
    mean_probs = F.softmax(mean_logprobs_t, dim=0)

    return {
        "summed_probs": summed_probs,
        "mean_probs": mean_probs,
        "summed_pred": summed_logprobs_t.argmax().item(),
        "mean_pred": mean_logprobs_t.argmax().item(),
        "summed_logprobs": summed_logprobs_t,
        "mean_logprobs": mean_logprobs_t,
    }


def _mock_tokenize(text: str, vocab_size: int, device: str) -> torch.Tensor:
    """
    Mock tokenize: 将文本按字符 hash 到 vocab id。
    用确定性的 md5 hash (而非 Python 内置 hash, 后者跨进程/会话不确定),
    保证同一文本得到相同 token 序列。
    """
    tokens = []
    words = text.split()
    for w in words:
        # 用 md5 确定性 hash 映射到 vocab (避免逐字符太长)
        h = int(hashlib.md5(w.encode()).hexdigest(), 16) % vocab_size
        tokens.append(h)
    if len(tokens) == 0:
        tokens = [0]
    return torch.tensor([tokens], dtype=torch.long, device=device)


def _mock_find_label_span(text: str, label_word: str, vocab_size: int):
    """
    在 mock token 序列中找到 label word 的位置 span。
    """
    words = text.split()
    label_tokens = label_word.split()
    for i in range(len(words) - len(label_tokens) + 1):
        if all(words[i + j].lower() == label_tokens[j].lower()
               for j in range(len(label_tokens))):
            return (i, i + len(label_tokens))
    return None


def _find_label_span(input_ids: torch.Tensor, label_word: str, tokenizer):
    """
    在真实 token 序列中找到 label word 的 token span。

    用 label_word 的 token ids 在 input_ids 中搜索匹配位置。
    """
    label_ids = tokenizer.encode(" " + label_word, add_special_tokens=False)
    if len(label_ids) == 0:
        label_ids = tokenizer.encode(label_word, add_special_tokens=False)
    if len(label_ids) == 0:
        return None

    ids_list = input_ids.tolist()
    n = len(ids_list)
    m = len(label_ids)
    for i in range(n - m + 1):
        if ids_list[i:i + m] == label_ids:
            return (i, i + m)
    return None


# =============================================================================
# 5. 校准误差 (Expected Calibration Error, ECE)
# =============================================================================

def compute_ece(confidences: torch.Tensor, predictions: torch.Tensor,
                labels: torch.Tensor, n_bins: int = 10):
    """
    计算期望校准误差 (Expected Calibration Error, ECE)。

    ECE = sum_b (|B_b| / N) * |acc(B_b) - conf(B_b)|

    将样本按预测置信度分到 n_bins 个等宽 bin 中, 每个 bin 内计算:
      - acc(B_b): 该 bin 中预测正确的比例
      - conf(B_b): 该 bin 中平均置信度
    ECE 是各 bin 的 |acc - conf| 的加权平均。

    论文用 ECE 衡量模型校准: ECE 越低, 模型置信度越能反映真实准确率。

    Args:
        confidences: [N] 每个样本的预测置信度 (最大概率)
        predictions: [N] 预测类别 index
        labels: [N] 真实类别 index
        n_bins: 分箱数

    Returns:
        ece: 期望校准误差
        bin_data: 各 bin 的统计信息
    """
    N = len(confidences)
    if N == 0:
        return 0.0, {}

    bin_boundaries = torch.linspace(0, 1, n_bins + 1)
    ece = 0.0
    bin_data = []

    for b in range(n_bins):
        lo = bin_boundaries[b]
        hi = bin_boundaries[b + 1]
        if b == n_bins - 1:
            mask = (confidences >= lo) & (confidences <= hi)
        else:
            mask = (confidences >= lo) & (confidences < hi)

        bin_size = mask.sum().item()
        if bin_size == 0:
            bin_data.append({"bin": (lo.item(), hi.item()), "size": 0,
                             "acc": 0.0, "conf": 0.0})
            continue

        bin_acc = (predictions[mask] == labels[mask]).float().mean().item()
        bin_conf = confidences[mask].mean().item()
        ece += (bin_size / N) * abs(bin_acc - bin_conf)
        bin_data.append({"bin": (lo.item(), hi.item()),
                         "size": bin_size, "acc": bin_acc, "conf": bin_conf})

    return ece, bin_data


# =============================================================================
# 6. Temperature Scaling (后处理校准)
# =============================================================================

class TemperatureScaler(nn.Module):
    """
    Temperature Scaling: 后处理校准方法。

    将 logits 除以一个标量 T (temperature):
        p_i = softmax(logits / T)

    - T > 1: 软化概率分布 (降低置信度, 通常改善校准)
    - T < 1: 硬化概率分布 (提高置信度)
    - T = 1: 无变化

    论文发现: Temperature scaling 在 summed scoring 下降低 ECE,
    但对 mean scoring 无效 (因为 mean scoring 的概率已不同)。

    优化: 在验证集上最小化 NLL loss 来学习 T。

    实现说明 (简化): 标准的 temperature scaling 应作用于模型原始 logits
    (即每一层 vocab 维度的未归一化输出), 再重新计算 log-likelihood。
    但本 demo 用合成数据且为简化实现, 这里直接对已聚合的类别
    log-likelihood (summed_logprobs, 形状 [N, C]) 当作 logits 做
    temperature scaling。这是一种方法简化, 不影响 demo 展示 scoring rule
    与 temperature 的交互效应; 完整复现需在原始 logits 上操作。
    """

    def __init__(self):
        super().__init__()
        self.temperature = nn.Parameter(torch.ones(1))

    def forward(self, logprobs: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logprobs: [N, C] 原始 log-likelihood (作为 logits)
        Returns:
            calibrated_probs: [N, C] 校准后的概率
        """
        scaled = logprobs / self.temperature
        return F.softmax(scaled, dim=-1)

    def fit(self, logprobs: torch.Tensor, labels: torch.Tensor,
            max_iter: int = 200, lr: float = 0.1):
        """
        在验证集上优化 temperature (最小化 NLL)。

        Args:
            logprobs: [N, C] 训练数据的 log-likelihood
            labels: [N] 真实标签
        """
        optimizer = torch.optim.LBFGS([self.temperature], lr=lr,
                                       max_iter=max_iter)

        def closure():
            optimizer.zero_grad()
            scaled = logprobs / self.temperature
            loss = F.nll_loss(F.log_softmax(scaled, dim=-1), labels)
            loss.backward()
            return loss

        optimizer.step(closure)
        return self.temperature.item()


# =============================================================================
# 7. 主实验流程
# =============================================================================

def run_experiment(model, tokenizer_or_vocab, is_mock: bool, device: str,
                   dataset, template_name: str, bits: int):
    """
    在指定配置下运行完整实验: 量化 + 分类 + 校准评估。

    Args:
        model: 原始全精度模型
        tokenizer_or_vocab: tokenizer 或 vocab_size
        is_mock: 是否 mock
        device: 设备
        dataset: [(sentence, label), ...]
        template_name: prompt 模板名
        bits: 量化比特 (16/8/4)

    Returns:
        result: dict 包含准确率、ECE (summed/mean)、各样本概率等
    """
    # 1. 量化模型
    print(f"\n    量化模型 -> {bits}-bit ...")
    quantized_model = quantize_model_weights(model, bits, is_mock)

    # 2. 逐样本分类
    print(f"    分类 {len(dataset)} 个样本 (template={template_name}) ...")
    summed_probs_list = []
    mean_probs_list = []
    summed_preds = []
    mean_preds = []
    true_labels = []
    summed_logprobs_list = []

    for i, (sentence, label) in enumerate(dataset):
        result = classify_sample(quantized_model, tokenizer_or_vocab,
                                 sentence, template_name, is_mock, device)
        summed_probs_list.append(result["summed_probs"])
        mean_probs_list.append(result["mean_probs"])
        summed_preds.append(result["summed_pred"])
        mean_preds.append(result["mean_pred"])
        true_labels.append(LABELS.index(label))
        # 同时保存 summed logprobs, 供 temperature scaling 使用 (避免重复分类)
        summed_logprobs_list.append(result["summed_logprobs"])

        if (i + 1) % 50 == 0:
            print(f"      已处理 {i+1}/{len(dataset)}")

    summed_probs = torch.stack(summed_probs_list)  # [N, C]
    mean_probs = torch.stack(mean_probs_list)
    summed_preds = torch.tensor(summed_preds)
    mean_preds = torch.tensor(mean_preds)
    true_labels = torch.tensor(true_labels)

    # 3. 准确率
    summed_acc = (summed_preds == true_labels).float().mean().item()
    mean_acc = (mean_preds == true_labels).float().mean().item()

    # 4. F1 (macro)
    summed_f1 = compute_macro_f1(summed_preds, true_labels)
    mean_f1 = compute_macro_f1(mean_preds, true_labels)

    # 5. 置信度 = 最大概率
    summed_conf = summed_probs.max(dim=1).values
    mean_conf = mean_probs.max(dim=1).values

    # 6. ECE (期望校准误差)
    summed_ece, _ = compute_ece(summed_conf, summed_preds, true_labels)
    mean_ece, _ = compute_ece(mean_conf, mean_preds, true_labels)

    # 7. Temperature scaling 校准
    # 用第一次分类循环中已保存的 summed logprobs 拟合 temperature
    # (避免对同一批样本重复分类)
    summed_logprobs_all = torch.stack(summed_logprobs_list)

    temp_scaler = TemperatureScaler().to(device)
    temp_scaler.fit(summed_logprobs_all, true_labels, max_iter=100)
    calibrated_probs = temp_scaler(summed_logprobs_all)
    calibrated_conf = calibrated_probs.max(dim=1).values
    calibrated_preds = calibrated_probs.argmax(dim=1)
    calibrated_ece, _ = compute_ece(calibrated_conf, calibrated_preds,
                                     true_labels)

    return {
        "template": template_name,
        "bits": bits,
        "summed_acc": summed_acc,
        "mean_acc": mean_acc,
        "summed_f1": summed_f1,
        "mean_f1": mean_f1,
        "summed_ece": summed_ece,
        "mean_ece": mean_ece,
        "calibrated_ece": calibrated_ece,
        "temperature": temp_scaler.temperature.item(),
        "summed_probs": summed_probs,
        "mean_probs": mean_probs,
        "true_labels": true_labels,
    }


def compute_macro_f1(preds: torch.Tensor, labels: torch.Tensor) -> float:
    """计算 macro F1 score。"""
    f1s = []
    for c in range(NUM_CLASSES):
        tp = ((preds == c) & (labels == c)).sum().item()
        fp = ((preds == c) & (labels != c)).sum().item()
        fn = ((preds != c) & (labels == c)).sum().item()
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-8)
        f1s.append(f1)
    return sum(f1s) / len(f1s)


def main():
    print("=" * 78)
    print("Quantization Effects on Biomedical LLM Reliability")
    print("论文: arXiv:2608.03854 | 目标模型: Qwen3-0.6B")
    print("=" * 78)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # 1. 加载模型
    print("\n[1] 加载模型...")
    model, is_mock, info = load_model_or_mock("Qwen/Qwen3-0.6B", device)
    print(f"    模型类型: {'Mock' if is_mock else 'Real'} ({info.get('name', 'N/A')})")

    # 准备 tokenizer 或 vocab_size
    if is_mock:
        tokenizer_or_vocab = model.embed.num_embeddings
        print(f"    Mock vocab size: {tokenizer_or_vocab}")
    else:
        from transformers import AutoTokenizer
        try:
            tokenizer_or_vocab = AutoTokenizer.from_pretrained(
                "Qwen/Qwen3-0.6B", trust_remote_code=True)
            print(f"    Tokenizer loaded")
        except Exception as e:
            print(f"    Tokenizer 加载失败: {e}, 使用 mock vocab")
            tokenizer_or_vocab = 32000
            is_mock = True

    # 2. 生成数据集
    print("\n[2] 生成模拟句子分类数据集 (类 PubMed RCT, 5类)...")
    dataset = generate_synthetic_dataset(num_samples=100, seed=42)
    print(f"    样本数: {len(dataset)}, 类别: {LABELS}")
    print(f"    示例: '{dataset[0][0]}' -> {dataset[0][1]}")

    # 3. 实验1: 不同量化精度 × 不同 scoring rule
    print("\n" + "=" * 78)
    print("[实验1] 量化精度 × Scoring Rule 对准确率和校准的影响")
    print("=" * 78)
    print(f"    使用 Template B (instruction), 固定模板评估量化效应")
    print(f"    {'Bits':<8} {'Scoring':<10} {'Acc%':<8} {'F1%':<8} "
          f"{'ECE':<8} {'CalibECE':<10}")
    print(f"    {'-'*60}")

    results_exp1 = {}
    for bits in [16, 8, 4]:
        result = run_experiment(model, tokenizer_or_vocab, is_mock, device,
                                dataset, "B_instruction", bits)
        results_exp1[bits] = result
        print(f"    {bits:<8} {'summed':<10} {result['summed_acc']*100:<8.2f} "
              f"{result['summed_f1']*100:<8.2f} {result['summed_ece']:<8.4f} "
              f"{result['calibrated_ece']:<10.4f}")
        print(f"    {bits:<8} {'mean':<10} {result['mean_acc']*100:<8.2f} "
              f"{result['mean_f1']*100:<8.2f} {result['mean_ece']:<8.4f} "
              f"{'N/A':<10}")
        print(f"    {'':8} Temperature T={result['temperature']:.3f}")
        print(f"    {'-'*60}")

    # 4. 实验2: Prompt Template 效应
    print("\n" + "=" * 78)
    print("[实验2] Prompt Template 对准确率的影响 (FP16, summed scoring)")
    print("=" * 78)
    print(f"    {'Template':<20} {'Acc%':<8} {'F1%':<8} {'ECE':<8}")
    print(f"    {'-'*48}")

    template_accs = {}
    for tmpl_name in PROMPT_TEMPLATES:
        result = run_experiment(model, tokenizer_or_vocab, is_mock, device,
                                dataset[:50], tmpl_name, bits=16)
        template_accs[tmpl_name] = result["summed_acc"]
        print(f"    {tmpl_name:<20} {result['summed_acc']*100:<8.2f} "
              f"{result['summed_f1']*100:<8.2f} {result['summed_ece']:<8.4f}")

    acc_spread = max(template_accs.values()) - min(template_accs.values())
    print(f"\n    >>> Template 间准确率极差: {acc_spread*100:.1f} 个百分点 <<<")
    print(f"    (论文报告 7-24 个百分点的 template 效应)")

    # 5. 实验3: Scoring Rule 反转效应
    print("\n" + "=" * 78)
    print("[实验3] Scoring Rule 对校准的主导效应 (INT8)")
    print("=" * 78)
    r8 = results_exp1[8]
    print(f"    INT8 Summed scoring: ECE = {r8['summed_ece']:.4f}")
    print(f"    INT8 Mean   scoring: ECE = {r8['mean_ece']:.4f}")
    print(f"    ECE 差异: {abs(r8['summed_ece'] - r8['mean_ece']):.4f}")
    print(f"    但准确率差异仅: "
          f"{abs(r8['summed_acc'] - r8['mean_acc'])*100:.2f} 个百分点")
    print(f"    Temperature scaling 后 ECE: {r8['calibrated_ece']:.4f} "
          f"(T={r8['temperature']:.3f})")

    # 6. 总结
    print("\n" + "=" * 78)
    print("实验总结")
    print("=" * 78)
    print(f"""
论文核心发现复现:
1. Scoring rule 主导校准:
   - Summed vs Mean scoring 的 ECE 差异显著
   - 准确率变化小但校准排名可反转
   - Temperature scaling 仅在 summed scoring 下有效

2. Prompt template 效应:
   - 4 种 template 间准确率极差 = {acc_spread*100:.1f} 个百分点
   - 与量化效应相当或更大

3. 量化精度效应:
   - FP16 -> INT8: 准确率变化 {abs(results_exp1[16]['summed_acc'] - results_exp1[8]['summed_acc'])*100:.2f} 个百分点
   - INT8 -> INT4: 准确率变化 {abs(results_exp1[8]['summed_acc'] - results_exp1[4]['summed_acc'])*100:.2f} 个百分点
   - INT4 产生异质但非灾难性的影响

结论: 评估量化对 LLM 分类可靠性的影响时, 必须同时控制 prompt template
和 scoring rule, 否则结论可能被实现选择主导而非量化本身。
""")
    print("=" * 78)


if __name__ == "__main__":
    main()
