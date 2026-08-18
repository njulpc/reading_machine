# Routing Divergence Is Not Evidence of Behavioral Influence：技术精读

> arXiv: [2608.15787](https://arxiv.org/abs/2608.15787) · submitted 2026-08-16 · Cedric Caruzzo 等 · cs.LG / cs.AI / cs.CL

## 1. 核心速览

**研究主题**：同权重 MoE 自蒸馏中 router 变化是否真正影响行为。
**一句话总结**：路由差异只说明 gate 变了；论文把上下文效应精确拆成 routing term 与 dense-like content term，发现前者通常被残差主干抑制，不能拿 router overlap 直接推断行为影响。

## 2. 研究背景与动机

demonstration-conditioned teacher 与 query-only student 可共享全部权重，却把 token 路由到不同专家。常见分析把路由差异视为蒸馏信号或因果解释，但忽略专家输出相似性和 residual stream 的稀释。

## 3. 核心方法与创新点

- 对单步冻结权重前向做精确 blockwise decomposition：固定内容只换 gate 得 routing term，其余为 content term。
- 定义 residual-stream exposure，并用 always-on backbone rescaling、merged-expert 边界与激活 patch 验证。
- 用 matched-norm noise 判断扰动是否具有方向特异性。

## 4. 实验设计与结果

覆盖 7 个开放权重 checkpoint、两个领域。routing term 占 block output 的比例只跨 **1.6×**，但 exposure 跨 **3.2×**；在三模型 PubMedQA patch 中，完整 routing term 对输出的影响不到自然上下文效应的一半，且多可被等范数噪声复现。merged-expert 边界的 routing factor 低至 **0.014/0.011**，exposure 约 **0.005–0.006**，反证“路由变化越大影响越大”的简单规则。

## 5. 局限性与未来展望

样本是家族相关的机会性 checkpoint，而非全因子架构扫描；patch 只覆盖三模型，exposure 尚不能作为行为阈值。作者明确建议把它当诊断量而非安全证书。

## 6. 学术启发

蒸馏中的中间机制指标必须经过因果 patch 或行为干预；“表示/路由不同”与“最终输出受影响”之间还隔着残差路径和共享主干。

**证据边界**：已核对官方 HTML 全文的 Discussion and limitations。
