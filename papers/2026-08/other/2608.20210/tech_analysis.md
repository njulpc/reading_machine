# 技术精读：Daedalus-150M

> arXiv: [2608.20210](https://arxiv.org/abs/2608.20210)；v1 提交：2026-08-20；主分类：cs.IR。

## 1. 核心速览

**研究主题**：为 CPU 单用户 4-bit decode 反向设计的 150M 级语言模型。
**一句话总结**：18 个 block 中仅 6 个保留 full attention、12 个改为两步状态短卷积；同数据参数匹配消融中，4-bit 文件小 6.3%，2048 context decode 快 1.76×，但 4-bit 仍带来约 6% perplexity 代价。

## 2. 研究背景与动机

小语言模型常照搬大 Transformer，再被动压到 CPU。单用户 token-by-token decode 主要受权重与 KV 内存流量限制，越长 context 越明显。作者先固定“普通 CPU、4-bit、batch=1”部署目标，再选择 attention/卷积比例和宽深配置。

## 3. 核心方法与创新点（分点）

1. 160.49M 参数、18 blocks；6 个 full attention，12 个短卷积，卷积状态长度恒为 2，不随 context 增长。
2. attention 层与卷积层交错，使需要全局检索的层保留表达力，而三分之二层不重复扫描 KV cache。
3. 训练从零开始用 59.9B token，并预注册与同参数全 attention 消融的胜负条件，减少事后选择偏差。
4. 以实际 CPU 4-bit 导出和 8 threads decode 为主评测，而不是只报告 FLOP。

## 4. 实验设计与结果

五任务总分 47.31，高于训练前设定的 42.20 门槛，并超过 GPT-2 124M、Pythia-160M、OPT-125M、GPT-Neo-125M。与同数据同规模 all-attention 消融相比，质量指标高 0.81%、下游基本持平，4-bit 文件小 6.3%；2048 context 解码快 1.76×，对外部相近模型为 2.08×。导出文件 95.56 MiB。量化使 perplexity 约恶化 6%（至 9.18），约一半卷积通道处于 inert 状态却无法安全剪掉，形成 8.5% 参数低效。

## 5. 局限性与未来展望

只训练一个主 run，预注册 margin 不是置信区间；模型只验证到训练 context，不保证外推。量化为训练后部署格式、未做 QAT，且架构仍存在大量 inert channel。CPU 结果依赖特定 runtime、线程和词表；49,152 词 embedding 占 37.7M 参数（23%），作者也承认过大。

## 6. 学术启发

面向端侧的模型压缩应先写出内存流量模型，再选结构。固定状态卷积与少量 attention 的组合说明：减少随 context 增长的状态读取，可能比单纯缩小 FFN 更能改善 batch=1 体验；同时必须公开量化质量损失和“剪不掉的死容量”。
