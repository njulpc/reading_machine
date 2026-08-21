# 技术精读：ReCache

> arXiv: [2608.19662](https://arxiv.org/abs/2608.19662)；v1 提交：2026-08-20；主分类：cs.CL。

## 1. 核心速览

**研究主题**：工具型 Agent 的资源级 KV cache 复用与压缩。
**一句话总结**：ReCache 把每个 tool/skill schema 编成可组合的独立 KV block，再做 layer-head-group 路由和字段剪枝；Inv-F1 由 dense 的 82.4% 仅降至 82.3%，TTFT 加速 3.655×、KV 内存降 92.43%。

## 2. 研究背景与动机

Agent 请求会反复携带相同工具 schema，但顺序与组合改变使普通 prefix cache 失效。完整 schema 还会增加 prefill、KV 内存和 decode attention。摘要式压缩可能丢掉调用参数，而整段保留则浪费大量层/头计算。

## 3. 核心方法与创新点（分点）

1. resource-wise attention 禁止不同资源在编码时互相作用，并赋予资源局部位置，使每个 KV block 与组合/顺序无关。
2. contribution-based routing 选择资源在哪些 layer、KV head group 可见，形成多维结构稀疏。
3. structural pruning 保留工具名、参数等调用关键字段；semantic pruning 再删除低贡献文本。
4. 独立资源 KV 可跨请求缓存和重排，在线只拼装需要的块，不重复 prefill。

## 4. 实验设计与结果

基准汇集 7 个公开 tool/skill-use 数据集并含 resource-disjoint 测试。resource-wise attention 的 Inv-F1 为 82.3%，dense 为 82.4%，同时 TTFT 加速 3.655×。完整 ReCache 将 allocated KV-tensor memory 降低 92.43%，attention 加速 1.423×；在论文设定中内存可限制到约 0.03 GiB。逐项消融显示局部位置、路由和字段压缩分别贡献复用性与内存收益。

## 5. 局限性与未来展望

需要改变 attention mask/position 和资源编码方式，不能无缝套到所有闭源 API；schema 之间真实依赖被隔离后可能损失跨资源推理。Inv-F1 主要衡量调用，不覆盖长链 Agent 成功率或恶意 schema。未来应研究依赖感知的有限跨资源连接、cache 失效策略和多租户安全隔离。

## 6. 学术启发

KV 压缩可以利用“静态资源”这一语义边界，而不只按 token 重要度裁剪。先让表示具有组合不变性，再缓存和稀疏路由，比对任意 prompt 做通用 prefix matching 更接近结构化软件复用。
