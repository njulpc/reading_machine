# 技术精读：The Asymmetric Harms of LLM Compression

> arXiv: [2608.19670](https://arxiv.org/abs/2608.19670)；v1 提交：2026-08-20；主分类：cs.CL。

## 1. 核心速览

**研究主题**：量化/剪枝对知识保持、置信与社会偏差的细粒度影响。
**一句话总结**：三种 8–9B LLM、11 类压缩配置显示，平均 accuracy/PPL 稳定不代表行为稳定：常见知识的相对保持反而可能比尾部知识下降更多，且新产生的错误仍可能高置信，群体偏差还会相互抵消。

## 2. 研究背景与动机

压缩论文常以平均 perplexity 或准确率判断“基本无损”，但这无法回答丢失的是哪类知识、模型是否知道自己错了，以及总体 bias 分数是否掩盖子群体反向变化。作者建立跨量化与剪枝的一致协议，专门观察压缩前后行为位移。

## 3. 核心方法与创新点（分点）

1. 模型为 Llama-3.1-8B-Instruct、Qwen3-8B、Gemma-2-9B-it；事实基准用 PopQA、Head-to-Tail，偏差用 WinoBias、BBQ。
2. 量化覆盖 GPTQ、AWQ、OmniQuant、AQLM 的 2/3/4-bit；GPTQ group size 128，并统一用 C4 calibration。
3. 剪枝覆盖 magnitude、WANDA、SparseGPT 的 30/50/70%，4:8/2:4 半结构化，以及 ShortGPT/层删除等结构化设置。
4. 定义各 popularity group 的 retention shift；仅对压缩后新丢知识测置信，并用 isotonic regression 校准；bias 报告总体与人口子群体变化。

## 4. 实验设计与结果

温和 4-bit、30% WANDA、5% ShortGPT 多数未整体崩溃；2-bit GPTQ/AWQ/OmniQuant、70% 稀疏和 25% ShortGPT 常崩溃。Llama 的 2-bit AQLM 仍有 12.3% 准确率，而其他三种 2-bit 量化不高于 1.9%。4-bit GPTQ 下，丢失 head knowledge 的中位置信最高可为 tail 的 1.20×；2-bit OmniQuant 错误置信仍约 0.4。WinoBias 某子群体在 SparseGPT 2:4 下变化 -53.1 个百分点，但总体分数会掩盖这种位移。

## 5. 局限性与未来展望

只覆盖三个 8–9B instruct 模型、选定 PTQ/剪枝，不含蒸馏或更大模型；偏差指标无法像事实问答那样做正确性校准。结果证明“不对称存在”，但未定位权重/层面的因果机制。后续应把子群体保持和 calibrated confidence 纳入压缩搜索目标，而非仅作事后审计。

## 6. 学术启发

压缩评测需要从单一效用标量升级为“谁被损害、错误有多自信、群体变化是否抵消”的向量。尤其在模型仍能保持平均分时，按知识频度与人口子群体做 retention shift，可能比继续追求 0.1 PPL 的改进更重要。
