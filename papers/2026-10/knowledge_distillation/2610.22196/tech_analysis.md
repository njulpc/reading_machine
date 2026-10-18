# Hy-Memory-30B-A3B: Attributed Reinforcement Learning for Long-Term Memory Writing

- arXiv：[2610.22196](https://arxiv.org/abs/2610.22196)；[官方全文 v1](https://arxiv.org/html/2610.22196v1)
- v1 UTC：2026-10-15T16:46:47+00:00；北京时间：2026-10-16T00:46:47+08:00
- 主分类及交叉分类：Computation and Language (cs.CL)
- 本轮证据：官方abs本轮刷新，标题/摘要/分类/history与缓存一致；全文来自10月18日保存的官方HTML v1，本轮阅读方法、主要实验及相关局限段落，未声称逐行审计全部附录。

## 1. 核心速览

研究主题：knowledge_distillation。

一句话总结：Hy-Memory 将旗舰教师的写入协议蒸馏到30B-A3B学生，再用逐chunk强化学习提升跨框架记忆质量。

## 2. 研究背景与动机

通用大模型担任memory writer成本较高，单框架提示又容易过拟合。长期记忆还会把早期错误带入后续状态，仅优化最终回答无法定位哪次写入有害。

## 3. 核心方法与创新点

1. 学生在真实harness里写入自己的bank，Hy3 flagship只对学生轨迹给top-50分布，以近似reverse-KL教协议；2 rollouts、LR1e-6、entropy0.005，OPD step375初始化RL。
2. RL每窗口最多5chunk、8个独立bank分支；冻结answer model及judge，以probe、归因结果和存储增长惩罚评分。权重1/2/0.3、γ=0，逐chunk组内归一化。
3. 总分最佳分支bank传入下一窗口，保留状态层面的on-policy性；128 H20，batch64窗口×8rollouts，LR5e-6、无KL，回放MoE routing。

## 4. 实验设计与结果

固定20%基准子样本、四harness、每harness六指标等权：55.49 vs Hy3-A3B base47.66、Claude Opus5 54.62。未训练EverMemOS为56.89 vs Opus54.04；MemOS仅50.51 vs50.50不能当作统计显著胜出。学生总30B、激活约3B；教师总规模及真实延迟/内存比未给可用量化证据，不能写10×整模压缩。

## 5. 局限性与未来展望

尚缺OPD/RL、chunk级信用分配与bank惩罚等受控消融。20%子样本和自动judge限制推广；外部记忆增长控制不是KV量化。未运行128卡训练或在线memory服务。

## 6. 学术启发

蒸馏时需要对齐部署状态分布：学生自己的错误bank也会改变未来prompt。可把这一设计迁移到agent压缩，但应独立测writer成本、memory质量和reader能力。

## 四维评分（1–10，主观研究评估）

|维度|分数|依据|
|---|---:|---|
|精度效果|7|宏平均+7.84，部分优势仅0.01点|
|压缩倍率|4|3B active不等于3B存储|
|创新性|7|状态链OPD与归因chunk奖励|
|可复现性|6|接口与超参公开但系统/算力较重|

所有原论文实验数字来自上述官方全文，非本机重跑结果。仅FALCON条目的Qwen转移实验为本轮实际运行；速度、token预算、缓存份数与权重字节不可互换。
