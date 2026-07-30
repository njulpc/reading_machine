# 技术深度分析：Benchmarking Post-Training Quantization of Large Language Models under Microscaling Floating Point Formats (arXiv:2601.09555)

> **论文**: Benchmarking Post-Training Quantization of Large Language Models under Microscaling Floating Point Formats
> **作者**: Manyi Zhang, Ji-Fu Li, Zhongao Sun 等
> **arXiv**: https://arxiv.org/abs/2601.09555 ｜ 提交: 2026-01-14 ｜ 分类: cs.CL, cs.AI

---

## 一、核心速览

### 研究主题

MXFP（微缩放浮点）格式下 LLM 后训练量化的系统基准：7+ PTQ 算法×15 评估基准×3 个 LLM 家族，填补现有 PTQ 研究集中于整数量化的空白。

### 一句话总结

核心发现：(1) MXFP8 一致接近无损，MXFP4 退化显著仍具挑战；(2) PTQ 有效性强烈依赖格式兼容性，某些算法范式持续更优；(3) PTQ 表现跨模型家族与模态高度一致，量化敏感度由语言模型主导而非视觉部分。

---

## 二、研究背景与动机

MXFP（如 MXFP8/MXFP4，块级共享指数的浮点格式）正成为新硬件原生支持的低精度格式，但 PTQ 算法大多针对整数量化设计与验证，在 MXFP 下的适用性与行为完全未知。算法结论能否从 INT 迁移到 MXFP，需要系统基准回答。

---

## 三、核心方法与创新点

- **大规模矩阵实验**：7+ 算法、15 基准、3 模型家族的全面交叉。
- **格式兼容性分析**：识别哪些算法范式与 MXFP 天然契合。
- **跨家族/模态一致性**：发现量化敏感度由语言模型主导，VLM 中视觉塔不是瓶颈。

---

## 四、实验设计与结果

- MXFP8 一致**接近无损**；MXFP4 **退化显著**、仍具挑战。
- PTQ 效果强烈依赖格式兼容性；部分范式持续占优。
- 结论跨模型家族与模态高度一致。

---

## 五、局限性与未来展望

局限：基准覆盖的算法以 PTQ 为主，QAT 在 MXFP 下的表现未测；未含 2-3bit 等更极端 MX 变体；具体每算法的提升数字需读正文。未来方向：MXFP 原生 PTQ 算法设计、MXFP4 的误差补偿（如 ARCQuant 类）、训练侧 MXFP。

---

## 六、学术启发

- **格式基准先行于算法创新**：MXFP 时代的量化研究应以格式兼容性为第一设计约束。
- **"语言模型主导敏感度"**是 VLM 量化的重要先验：把位宽预算多分给语言侧。

---

*分析时间: 2026-01 月度回填 ｜ 分析人: AI Assistant*
