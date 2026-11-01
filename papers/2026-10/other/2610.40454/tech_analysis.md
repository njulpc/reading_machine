# Glance: The Generator Is Its Own Reranker

- arXiv：[官方详情](https://arxiv.org/abs/2610.40454)；[v1全文](https://arxiv.org/html/2610.40454v1)。
- v1提交：UTC 2026-10-29T17:01:22+00:00；北京时间 2026-10-30T01:01:22+08:00。归档以北京时间提交月份为准。
- 官方分类：Computation and Language (cs.CL) ; Information Retrieval (cs.IR)。分析归类：other。
- 证据：官方摘要、Submission history及全文方法/实验相关段落；全文HTML缺失信息不补造。论文报告数字与本机结果分开标注。

## 1. 核心速览

研究主题：生成器与重排器共享常驻权重。

一句话总结：Glance用同一9B骨干完成RAG重排与回答，额外决策技能约0.1GiB，但缓存和端到端时延仍需单独核算。

## 2. 研究背景与动机

RAG中的独立重排模型增加常驻权重，并重复处理每个query-passage对。本文把重排决策放进生成器本身，让多条短probe共享候选上下文的prefill，以减少模型冗余。

## 3. 核心方法与创新点

- 冻结9B混合注意力骨干，仅训练rank16 LoRA与256维pointer head；probe在决策位置与选项结束位置的隐藏状态间打分，不生成自然语言判断。
- packed_all一次prefill所有候选，再并行处理约30-token的独立probe。全注意力分支复制KV，DeltaNet分支还需复制卷积窗口和递归状态。
- 主流程adapter作用于所有token，选中段落后关adapter重新prefill再回答；Activated变体只在probe启用adapter，因此能续用原始base缓存，但该缓存仍保留所有候选，并非KV裁剪。

## 4. 实验设计与结果

§3.6/4/5：4000条MS MARCO训练查询、500步、batch8、学习率LoRA5e-5/head1e-4，B200训练39分钟、峰值21GiB。SciFact/NFCorpus nDCG@10为0.741/0.345，对独立bge-reranker-v2-m3为0.721/0.326。300道HotpotQA上F1提高0.045，配对bootstrap95%CI为[0.014,0.076]。Activated单独100题实验续用缓存F1为0.750，重新prefill为0.754；答案延迟138对181ms。这与主实验训练、GPU、样本数均不同。

压缩口径：移除独立重排骨干的常驻开销；每技能约0.1GiB，无通用总内存压缩率。

本次未执行该论文的训练或硬件测量，以上为论文报告，不是本机重测。

## 5. 局限性与未来展望

仅两个BEIR数据集、一个QA数据集及一个骨干族，独立cross-encoder单查询仍更快。内存随候选数与上下文长度增长，无法保证合并模型就减少总显存。部分GPU被共享，跨实验延迟不可直接相除。未来应测多查询批处理、长上下文总缓存、不同骨干和显著性。

## 6. 学术启发

共享权重与共享上下文是两个不同优化对象。特别要检查adapter是否改变缓存，及重排后是否真的丢弃无关段落；参数驻留节省不能自动推出缓存节省。
