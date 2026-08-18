# SQuad：技术精读

> arXiv: [2608.16585](https://arxiv.org/abs/2608.16585) · submitted 2026-08-17 · Animesh Karnewar 等 · cs.CV

## 1. 核心速览

**研究主题**：视频 DiT 的次二次注意力蒸馏。
**一句话总结**：SQuad 把全 softmax 注意力教师拟合为复杂度 `O(n√n)` 的注意力，并用 flow-matching SFT + 改进 DMD2 两阶段同时压缩单步注意力和采样 NFE。

## 2. 研究背景与动机

视频 token 很多，标准 self-attention 为 `O(n²)`；纯线性或低秩替代虽快但表达不足。重新训练视频 DiT 又成本过高，因此需要从预训练 quadratic teacher 直接迁移。

## 3. 核心方法与创新点

- 设计 `O(n√n)` SQuad-Attention，在线性与全注意力之间保留更强交互。
- 第一阶段 flow-matching SFT 对齐预训练 Wan2.2-5B。
- 第二阶段 improved DMD2 进一步做分布匹配并减少采样步数。

## 4. 实验设计与结果

在 Wan2.2-5B text-to-video 上，SQuad 的 VBench **83.20**，教师为 **83.08**；每步每 block attention FLOPs 约降 **67×**，attention latency 约 **11×**，端到端 DiT latency **2×**。采样从教师默认 **100 NFE** 降至 **6 NFE**。

## 5. 局限性与未来展望

两阶段视频蒸馏仍昂贵，验证集中在单一 5B 主干；FLOPs 大降但端到端仅 2×，说明其他模块和 kernel 是明显瓶颈。需验证更长视频、其他 DiT 与部署显存。

## 6. 学术启发

结构蒸馏和采样蒸馏可乘法叠加，但最终必须看端到端而非局部 FLOPs；次二次中间点值得优先探索。

**证据边界**：官方 HTML 不可用，已下载并视觉核验 25 页官方 PDF；数字来自首页摘要和正文。
