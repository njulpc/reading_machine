# 深度技术分析：Displacement Is Not Direction: Evaluating Fidelity Metrics for Quantized LLM Deployment

> **arXiv ID**: [2606.19558](https://arxiv.org/abs/2606.19558)  |  **提交日期**: 2026-06-17  |  **分类**: cs.LG, cs.CL  |  **作者**: Miloš Nikolić, Ali Hadi Zadeh, Enrique Torres Sanchez 等

> ⚠️ 本文档基于 arXiv 摘要与元数据撰写，未逐字核对全文；所有数字均引自摘要原文。


---

## 一、核心速览

**研究主题**：量化影响分析（低秩分解、量化）—— 面向Qwen 系列 LLM的模型压缩

**一句话总结**：本文研究了面向Qwen 系列 LLM的量化影响分析方法/研究「Displacement Is Not Direction」，关键结果包括：35B。（基于摘要）

**技术标签**: low-rank / quantization


---

## 二、研究背景与动机 (Background & Motivation)

量化不只是工程手段，也是理解模型表征、鲁棒性与安全性的探针。系统性的量化影响研究——包括对不确定性、安全性对齐、记忆与隐私、故障注入敏感度、公平性与可解释性的影响——为量化方法的可靠部署提供了关键的实证基础与理论边界。

### 2.1 本文切入点

摘要开篇指出：

> Fidelity metrics, such as per-token KL divergence (KLD) against a high-precision reference, are often used in practice as low-cost proxies for benchmark quality.


并进一步阐述了问题设定：

> We test this practice on a 28-quant cohort of Qwen3.6-35B-A3B and a 41-quant cohort of Devstral-Small-2-24B, evaluated across a suite of downstream benchmarks.


从问题陈述看，作者针对的是Qwen 系列 LLM在量化影响分析场景下的具体瓶颈，属于 quant-analysis 技术路线。


---

## 三、核心方法与创新点 (Methodology & Innovations)

根据摘要可识别的核心方法组件：

- **方法要点 1**：We test this practice on a 28-quant cohort of Qwen3.6-35B-A3B and a 41-quant cohort of Devstral-Small-2-24B, evaluated across a suite of downstream benchmarks.
- **方法要点 2**：We find that KLD is strongly correlated with benchmark score over the full cohort ($ρ=-0.72$ on Qwen and $ρ=-0.86$ on Devstral, both with $p<0.001$).
- **方法要点 3**：However, this relationship collapses to non-significance in the near-baseline silent zone ($ρ=+0.00$ on Qwen and $ρ=-0.24$, $p=0.36$, on Devstral).
- **方法要点 4**：This collapse persists across 14 measurement variants, including different KLD aggregations, perplexity formulations, top-1 agreement, calibration corpora, and context lengths.

**方法学点评**：该类研究的方法学价值在于受控实验设计：固定模型与任务、系统地改变量化配置，以分离量化本身的影响。阅读时应关注其实验变量控制与统计严谨性。


---

## 四、实验设计与结果 (Experiments & Results)

摘要中报告的关键定量结果（原文句子摘录）：

- We test this practice on a 28-quant cohort of Qwen3.6-35B-A3B and a 41-quant cohort of Devstral-Small-2-24B, evaluated across a suite of downstream benchmarks.
- We find that KLD is strongly correlated with benchmark score over the full cohort ($ρ=-0.72$ on Qwen and $ρ=-0.86$ on Devstral, both with $p<0.001$).
- However, this relationship collapses to non-significance in the near-baseline silent zone ($ρ=+0.00$ on Qwen and $ρ=-0.24$, $p=0.36$, on Devstral).
- This collapse persists across 14 measurement variants, including different KLD aggregations, perplexity formulations, top-1 agreement, calibration corpora, and context lengths.
- At the per-prompt level, KLD has only weak failure-prediction power on code, with failed-vs-passed geometric-mean ratios in $[1.08,1.22]$ across five models on LiveCodeBench, and fails as a cross-model router, achieving only $42.3\%-49.4\%$ accuracy on disagreement prompts.
- We trace the collapse to a structural decomposition: KLD primarily measures the volume of disagreement with the reference, with silent-zone composite $ρ=+0.94$ ($p<0.001$) on Qwen and $+0.55$ ($p=0.03$) on Devstral, while its relationship to the direction of those disagreements is weak and task-conditional.

**结果解读**：以上数字均直接引自摘要原文。评估该类工作时建议对照同月同方向工作（见月度报告横向比较表）判断其增益幅度。


---

## 五、局限性与未来展望 (Limitations & Future Work)

分析类研究的结论通常与特定模型家族、量化配置绑定，外推到新架构（如 MoE、SSM）时需要重新验证。

此外，本文档基于摘要与 arXiv 元数据撰写，未获取全文，方法细节、实验设置与更完整的局限讨论以原文为准。


**未来展望**：未来方向：建立量化影响的标准评测协议，覆盖安全/公平/记忆等非精度维度。


---

## 六、学术启发 (Takeaways for My Research)

- 量化对模型行为的影响是多维的（安全、不确定性、记忆），部署前的量化评估应超越精度指标
- 基准幻象研究提示：选择题指标会系统性高估剪枝/量化模型的真实能力
- 结合本文：可将「Displacement Is Not Direction」的思路迁移到 Qwen3-0.6B 等小模型上验证其在小参数量 regime 下的有效性（见 scripts/quantization 下对应 demo，若已复现）。
