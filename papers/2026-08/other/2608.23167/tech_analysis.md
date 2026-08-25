# Accelerating Diffusion Language Models via Structured Suffix Modeling

> arXiv: [2608.23167](https://arxiv.org/abs/2608.23167) · v1: 2026-08-24 · 主分类: cs.CL
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：Diffusion LM suffix token 的结构化保留。
**一句话总结**：把 suffix 划为 local/middle/tail 并按区域保留不同 token 数，同时复用前一步解码结果作为新表示；方法训练自由、可与其他加速叠加，长序列组合设置最高报告 72.81× speedup。

## 2. 研究背景与动机

DLM 一步并行去噪多个 token，但每步仍与全 suffix 交互。只保留 local window 虽快，却忽略不同区域的结构作用，并在每一步把 suffix 重置成同质表示，浪费已获得的去噪信息。

## 3. 核心方法与创新点

- 把 suffix 分成 local、middle、tail 三类区域。
- 按结构角色为各区配置不同 retention budget，而非固定窗口。
- 将上一 decoding step 的结果注入当前 suffix representation。
- 训练自由，和 parallel decoding、KV cache 等方法正交。

## 4. 实验设计与结果

在 3 个 DLM、多 benchmark 上，方法进一步加速且多数配置性能改善。长序列与其他技术组合时最高 72.81×；这是组合上界，不是该模块单独加速。论文的主要证据是同预算下结构化 suffix 优于纯 local window。

## 5. 局限性与未来展望

区域划分与 budget 可能依赖序列长度、语言和模型；组合加速难分离各组件贡献。未来需真实 kernel latency、独立增益和自适应 budget controller。

## 6. 学术启发

token 压缩不应默认“距离近就重要”。序列不同区域可承担不同功能，保留策略应同时利用空间位置和跨步状态。
