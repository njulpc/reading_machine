# Pricing the Risk of Runtime Compression：技术精读

> arXiv: [2608.15810](https://arxiv.org/abs/2608.15810) · submitted 2026-08-16 · Fanzhe Wei, Li Liu · cs.AI

## 1. 核心速览

**研究主题**：动态压缩 serving state 的 anytime-valid 风险核算。
**一句话总结**：论文把“负载高时降精度”从经验门控改造成可随时审计的风险账本，并用可机检设计律把内部 witness 与用户实际输出差异连接起来。

## 2. 研究背景与动机

现有运行时压缩常按负载自适应，却没有逐请求 soundness；用预先声明事件数的 union bound 又会在长请求上耗尽预算。即使内部状态有证书，也可能离用户看到的 served output 很远。

## 3. 核心方法与创新点

- anytime-valid ledger 在每次 admission 都维护有效风险界，不依赖预知请求长度。
- 设计律 `TV <= tanh(a_q w_thr)` 把 served-TV 目标转成阈值旋钮，并分解 query envelope、ellipsoid 和 operating point 三层松弛。
- 对 80 条 serving history 做 exchangeable extrapolation；228 个概率核在 Lean 4 中导出检查且无 `sorry`。

## 4. 实验设计与结果

union budget 在生产栈的长请求上 **100%** 耗尽；新账本在 **352,333** 次 admission 上持续有效。预注册 held-out 轮中，匹配风险下 exact fallback 从 **0.30** 降到 **0.14**。三层审计把总计 **1064×** 的松弛定位到约 **700×** 的 operating point，而 measured ellipsoid 替换仅 **0.89×**、没有带来收益；80 histories 的 order-statistic 风险界能区分 **0.41 vs 0.51**。

## 5. 局限性与未来展望

证书依赖 exchangeability、实现中的 operator envelope 与门控对象；巨大的 operating-point gap 说明理论界仍较保守。Lean 检查保证推导实现一致，不保证建模假设适合新流量。

## 6. 学术启发

运行时混合精度/状态压缩可借鉴“风险可消费账户”，并应把证书松弛逐层归因，而不是只给一个最终上界。

**证据边界**：官方 HTML 全文可用；该文没有公开适合 Qwen 的具体量化器，因此归为 other 而非量化复现。
