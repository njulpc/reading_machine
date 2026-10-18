# PathFM: Fast Generative Forecasting of Multivariate Trajectories

- arXiv：[2610.22358](https://arxiv.org/abs/2610.22358)；[官方全文 v1](https://arxiv.org/html/2610.22358v1)
- v1 UTC：2026-10-15T17:58:45+00:00；北京时间：2026-10-16T01:58:45+08:00
- 主分类及交叉分类：Machine Learning (cs.LG)
- 本轮证据：官方abs本轮刷新，标题/摘要/分类/history与缓存一致；全文来自10月18日保存的官方HTML v1，本轮阅读方法、主要实验及相关局限段落，未声称逐行审计全部附录。

## 1. 核心速览

研究主题：knowledge_distillation。

一句话总结：PathFM 将轨迹flow蒸馏成1–2次网络评估，并共享历史计算，126M模型可在L4上51.6ms生成32条预测路径。

## 2. 研究背景与动机

边际分位数不能确定时间/变量依赖，完整轨迹flow更灵活却通常需多次评估。本文压缩的是采样计算，同时保持联合路径分布与边际校准。

## 3. 核心方法与创新点

1. T5式时序/通道注意力，patch16；late entry使早期历史表示不依赖噪声/time，历史KV跨draw与flow步共享，训练每历史4draw约1.5×开销。
2. 冻结flow教师，将[0,1]分20区间，student每区间affine head共享特征；单block20头融合为1NFE，两block各10头为2NFE。教师在学生提出的状态给Euler速度目标，状态与target stop-gradient。
3. 以fair CRPS对单步生成反传，抑制有限ensemble校准的低方差偏差，继续保留PDD监督；分层采样改善小ensemble。

## 4. 实验设计与结果

126M模型L4生成32paths51.6ms；100个fev-bench任务上，32条stratified近似256条iid的FEV skill。匹配teacher/student比较中，1NFE学生接近10NFE教师，2NFE略超过；300M约两倍延迟而精度更好。20区间是训练head分块设计，不能混作本次10NFE教师比较的“20×实测提速”。FPS路径分数与边际CRPS需要分别读。

## 5. 局限性与未来展望

生成forecast路径质量依赖教师和校准损失，CRPS主要约束边际，不能单独保证完整联合依赖。外部quantile模型补全方式影响路径评估。没有本机预训练/蒸馏运行。

## 6. 学术启发

采样蒸馏与确定性历史缓存可正交组合，但收益不能直接相乘。应在固定draw数量、路径相关性和NFE下比较，并检查fair CRPS训练是否改变极端事件覆盖。

## 四维评分（1–10，主观研究评估）

|维度|分数|依据|
|---|---:|---|
|精度效果|8|1–2NFE接近/超过匹配10NFE教师|
|压缩倍率|8|10→1–2计算评估，实际51.6ms有条件|
|创新性|8|多headPDD与共享历史/校准结合|
|可复现性|7|方法设置详细，本轮未跑时序训练|

所有原论文实验数字来自上述官方全文，非本机重跑结果。仅FALCON条目的Qwen转移实验为本轮实际运行；速度、token预算、缓存份数与权重字节不可互换。
