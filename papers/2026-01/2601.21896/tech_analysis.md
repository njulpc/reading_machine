# 技术深度分析：Past- and Future-Informed KV Cache Policy with Salience Estimation in Autoregressive Video Diffusion (arXiv:2601.21896)

> **论文**: Past- and Future-Informed KV Cache Policy with Salience Estimation in Autoregressive Video Diffusion
> **作者**: Hanmo Chen, Chenghao Xu, Xu Yang, Xuan Chen
> **arXiv**: https://arxiv.org/abs/2601.21896 ｜ 提交: 2026-01-29 ｜ 分类: cs.CV

---

## 一、核心速览

### 研究主题

自回归视频扩散的过去-未来双知 KV cache 策略 PaFu-KV：轻量显著性估计头（从双向教师蒸馏）预测 token 显著性分数，保留有信息 token、丢弃低相关 token。

### 一句话总结

PaFu-KV 观察到 token 对视频生成的贡献高度时间异质，用蒸馏自双向教师的轻量显著性头估计分数指导 KV 保留——"过去信息"（已见 token）加"未来信息"（蒸馏自带的全局视角）双知决策，改善长程视频生成的质量-效率权衡。

---

## 二、研究背景与动机

自回归视频生成提升实时合成效率，但现有方法靠启发式 KV cache 策略，忽视长程生成中 token 重要性差异——关键时空信息丢失与冗余缓存累积并存。自回归的因果性使重要性判断只能看过去，而视频的全局结构（未来帧依赖）恰是判断关键。

---

## 三、方法创新

1. **时间异质性观察**：token 贡献随生成进程高度变化——静态策略必然次优。
2. **显著性估计头**：轻量头从双向教师（可见全局）蒸馏——把"未来视角"蒸馏进因果模型可用的估计器，绕开因果限制。
3. **双知策略**：显著性分数融合过去信息与（蒸馏获得的）未来信息做 KV 保留/丢弃决策。

---

## 四、实验结果

- 摘要报告更优的质量-效率权衡（摘要截断，未给出具体加速比与质量指标）。

---

## 五、局限与展望

- 显著性头的蒸馏质量决定上限（教师不可用时）。
- 头自身推理开销对极端实时场景的影响。
- 与 Dummy head（2601.20499）等头级策略的兼容性未讨论。

---

## 六、学术启发

1. "蒸馏未来视角"解决因果模型的重要性估计局限——教师提供全局/双向信息，学生保持因果部署，该模式可推广到流式 LLM。
2. 视频扩散 KV 管理本月密集产出（PaFu-KV、Dummy head、HERMES）——视频生成的推理效率正在快速成型为独立子领域。

---

*分析时间: 2026-01 ｜ 分析人: reading_machine*
