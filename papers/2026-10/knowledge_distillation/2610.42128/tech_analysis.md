# DecisionRank: On-Policy Distillation for Decision-Model Rerankers

- arXiv：[2610.42128](https://arxiv.org/abs/2610.42128)；[官方 HTML v1](https://arxiv.org/html/2610.42128v1)
- v1 实际提交：2026-10-30T17:56:58+00:00（UTC）；2026-10-31T01:56:58+08:00（Asia/Shanghai）。
- 官方分类（主分类在前）：Computation and Language (cs.CL)
- 压缩归类：knowledge_distillation。证据为官方摘要与上述全文方法、实验及相关附录；以下数字均为论文报告，非本机复现。

## 1. 核心速览

研究主题：knowledge_distillation / DecisionRank: On-Policy Distillation for Decision-Model Rerankers。

一句话总结：DecisionRank 把生成式排序教师蒸馏成首token打分学生，以一次前向替代自回归排序。

## 2. 研究背景与动机

生成式reranker逐个输出文档ID，延迟较高。首token决策模型快，但其静态分数与教师的条件排序序列不在同一监督空间；直接对齐词表或离线排序会忽略学生实际选择形成的状态。

## 3. 核心方法与创新点

1. **item空间对齐**：为至多100个文档分配学生单token ID，以第一个输出位置的logit作为分数。教师数字ID即便分词不同，仍映射到同一个文档。
2. **on-policy条件反馈**：按学生当前分数排序取top-K，形成确定性轨迹。教师一次teacher-forced前向获得每步剩余文档的条件分布；学生每步重用同一组分数，在剩余集合做Plackett–Luce归一化，以reverse KL对齐。
3. **联合训练**：离线RankNet学习全局次序，OPD修正学生已访问的状态。K=20，仅监督第2–19步，lambda=0.1，batch32；1.7B学习率2e-5，4B/8B为6e-6。推理一次处理全部候选并排序，无自回归生成。

## 4. 实验设计与结果

表1–4：Qwen3学生由Qwen3.8-27B蒸馏。TREC DL的nDCG@10×100：1.7B学生63.89，27B教师62.97；8B学生64.34。8B在BEIR/BRIGHT/R2MED分别57.98/36.86/43.55，四基准均值50.68；教师在R2MED46.66及BRIGHT37.42仍更强，不能说学生所有任务超过教师。

8B相对RankNet-only，在TREC/BEIR/R2MED/BRIGHT分别增加0.90/0.59/0.49/0.80。三个训练种子，8B TREC由63.40±0.06升至64.21±0.14。§3效率分析在相同输入长度设定下，8B对listwise DirectRank-8B，TREC快24.5×、BRIGHT快16.7×。27/1.7≈15.9仅是名义参数比，不代表checkpoint字节或端到端速度。

## 5. 局限性与未来展望

候选文档仍须共同prefill，随着文档长度增加该成本不会消失；top-K训练反馈不等于所有排序位置均得到OPD监督。教师调用成本发生在训练阶段；闭源Jev用API评测，不能把跨服务延迟视为统一硬件比较。本轮未训练reranker或重跑检索评测。

## 6. 学术启发

蒸馏可在任务动作空间进行，而不必依赖词表一致。把序列决策压入一次前向时，应让教师评价学生当前轨迹，并保留离线全局排序约束；效率报告应固定候选集、输入长度和硬件。

评分（1–10）：精度效果8，压缩倍率/资源削减9，创新性8，可复现性8。

准确率8：稳定增益但部分任务未超教师；压缩9：1.7B学生及16.7–24.5×测得加速；创新8：item空间OPD；复现8：任务、损失及训练参数明确，本轮未实训。

本轮为非量化论文精读，未执行论文训练或运行时基准；可复现性评分衡量公开方法的可操作程度，不表示本轮已复现。分析日期：2026-11-03。
