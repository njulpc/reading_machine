# Score Centering Stabilizes Off-policy Reinforcement Learning

- arXiv：[2609.20807](https://arxiv.org/abs/2609.20807)
- 全文：[官方 HTML v1](https://arxiv.org/html/2609.20807v1)
- v1 提交：2026-09-17T17:58:17Z；北京时间 2026-09-18T01:58:17+08:00
- 分类：Machine Learning (cs.LG)；归档：quantization
- 证据范围：已阅读官方摘要及HTML方法、实验、局限；原论文结果与本机结果明确分开。

## 1. 核心速览

一句话总结：Score Centering 抵消量化采样器导致的梯度漂移；重度W8A8/KV4的30B实验训练准确率30%，高于TIS的12%。

研究主题：量化推理采样器与高精度RL训练器之间的数值不匹配校正。它是支持低精度采样训练的算法，不是新量化网格。

## 2. 研究背景与动机

采样分布q与训练分布p不同，策略梯度可拆成奖励均值乘以E_q[grad log p]的漂移项和协方差信号。即使reward恒定，漂移仍可能非零；训练器再同步到采样器形成误差反馈。重要性权重截断/屏蔽虽然降方差，却会重新引入偏差。

## 3. 核心方法与创新点

1. 将score s_y换成s_y-E_q[s]，消除每个prefix的漂移；剩余协方差仍在q下计算，不等于完全无偏on-policy梯度。
2. 仅保存采样器top-k（默认128，消融32）概率；尾部用训练器分布按rho=(1-sum_H q)/(1-sum_H p)重标度。损失为 -R[log p_y-sum_H stopgrad(q-rho*p)log p]。所有概率系数必须detach。
3. 可与TIS（ratio上截2）、MIS（0.5–5内保留）组合：head系数改为 q*f(p/q)-alpha*p，alpha=rho*f(1/rho)。
4. 官方代码W8A8用输出通道权重absmax、token激活absmax/127，四舍五入对称INT8；KV按token/head、head维absmax，scale下限1e-9。不是GPTQ，也没有外部静态校准集；每次权重同步重新量化，激活/KV运行时动态定标。

## 4. 实验设计与结果

官方§5、附录A/B：Qwen3-0.6B Countdown，64prompt×8 completion、长512；30B-A3B Base INTELLECT-2数学，16×8、长1024；SGD lr=.01，每batch一步。训练器bf16，仅采样器量化。

30B轻FP8采样时普通PG仍稳定，训练准确率58%；FP8+KV FP4时SC52%、TIS51%；INT8+KV INT4时SC30%、TIS12%、其他<5%。这些是平滑训练准确率，不是独立测试准确率。0.6B使用3种子，30B各方法1–5种子不齐，整套约6180 H100-hours。刻意放大TIM以在短序列/有限步数中观察崩溃，不能据此承诺常规部署同样大收益。top128在同硬件作者JAX实现开销<1%，并未测vLLM/SGLang开销。

## 5. 局限性与未来展望

本次Qwen复现位于 scripts/quantization/2609.20807/。实现真实INT8权重存储、逐token激活量化及写入KV前的逐头量化误差，并移植top-k SC/TIS/MIS和SGD。CPU矩阵乘先反量化为FP32，KV保存反量化结果，训练器也为FP32；因此不宣称原生INT8加速或KV内存压缩。使用缓存0.6B权重、极小采样/一次更新及小张量验证；精确运行结果、环境与限制见README/results.json。没有复现Countdown长期训练、30B、多种子或GPU内核。

## 6. 学术启发

验证量化训练算法应检查梯度而非只看前向误差：恒定reward下精确SC期望梯度为零；top-k简式应与重建完整q后的梯度一致；on-policy及精确IS时校正消失。评分：精度8（重TIM改善且有多规模证据）；压缩5（采样器W8/KV低位，训练器仍高精度，无整机倍率）；创新8（漂移分解与可组合加性校正）；可复现8（官方代码加本机数值/真实模型验证，非完整基准）。
