# 技术深度分析：DLite: History-free Speculative Decoding for Agentic AI (arXiv:2610.23787)

> 官方摘要与提交历史：[arXiv abs](https://arxiv.org/abs/2610.23787)；[官方HTML v1全文](https://arxiv.org/html/2610.23787v1)。
> v1提交：2026-10-16T17:18:54+00:00（UTC），2026-10-17T01:18:54+08:00（Asia/Shanghai）。
> 主分类与交叉分类（官方顺序）：Computation and Language (cs.CL)。
> 分析日期：2026-10-20；已阅读全文中的方法、实验及相关附录，没有逐项审计所有附录证明。实验数字属原文报告，除FuTransformer本地记录外均未独立重跑。

## 一、核心速览

研究主题：长上下文agent推理的草稿模型缓存消除与蒸馏。

一句话总结：DLite把历史建模交给目标模型，草稿只根据目标隐藏状态和局部token预测，通过两阶段蒸馏学会无历史draft KV的推测解码。按运行态缓存压缩归入other，训练中也使用知识蒸馏。

## 二、研究背景与动机

Agent上下文持续扩展，传统drafter既要维护自己的历史KV，又要根据长历史进行预测；论文观察接受长度可退化80%。目标模型已经编码全局信息，草稿重复建模既增开销又增加学习难度。本文所删的是draft历史缓存，不是目标模型的全部KV。

## 三、核心方法与创新点

1. 取目标模型多个层的隐藏状态，加可学习depth/source embedding，按序列维度组合；用局部而非全局累积position。草稿每轮由最新隐藏状态、anchor token、K个placeholder重新构建。
2. 并行backbone预测K位置后，用低秩RNN式head恢复block内部因果依赖：s_T=g(s_{T-1},E(x_{t+T-1}))，避免每个中间表示重复投影到整个词表。
3. 先训练同构、保留历史KV的中间教师，再用forward KL预热无历史学生；稳定阶段丢弃中间教师，优化对目标模型的0.1×CE+1×L1 distribution discrepancy。位置权重exp(-(i-1)/4)。这种结构桥梁降低直接对齐异构目标模型的难度。
4. 目标模型按标准speculative procedure验证草稿，保留原target KV。收益不是少运行一次完整目标模型，更不能写成把4B/8B压缩成无缓存模型。

## 四、实验设计与结果

全文§5和附录A：Qwen3-4B/8B目标，draft backbone均5层、hidden=2560/4096；选12/14个目标层隐藏状态，序列头rank=320/512；K=7。1.3M Open-PerfectBlend+600K Nemotron prompt，由目标重生成response；最大序列4096。32 H800训练，AdamW lr4e-4、batch32、clip1、warmup .04；同构教师CE 8epoch、KL预热2epoch、稳定训练6epoch。

表2 LongBench-v2长对话：4B DLite 3.88倍AR速度、接受长度4.62，对比DSpark 3.16倍/3.93；8B为3.96倍/4.77，对比3.02倍/4.01。表3 SWE-bench，8B DLite 2.74倍AR，对比DSpark1.60倍，速度倍率相对提高约71.25%；这不是直接“额外2.74倍”。

表4并发64、8B LCB吞吐5758 TPS，对比DSpark5621，增益约2.44%；低并发优势不能直接外推高并发。一般任务4B GSM8K接受长度6.38对比DSpark6.27，差距远小于agent长上下文。论文消融中128/512 sliding-window drafter在充分训练后与无历史方案接受长度相近。

本轮未训练或运行H800 serving；没有独立的总显存字节测量，故不提供整系统压缩倍率。

## 五、局限性与未来展望

直接复用目标hidden states增加数据通路和模型接口耦合；中间教师8epoch、学生8epoch以及目标response生成有明显离线成本。部分DFlash2/DFlow数字引用外部来源而非同平台重跑。5层drafter和target隐藏状态依然消耗内存，删除历史KV不等于零draft开销。还需报告请求调度、极长上下文和系统总峰值显存。

## 六、学术启发

可以把压缩对象从“所有上下文”改为“重复持有的上下文”：保留能力最强模块的历史状态，用学生学习短接口。对异构小模型蒸馏，先构造同构教师作为桥梁，可能比直接KL更稳；验证时应同时测接受长度和端到端TPS。

四维主观评分（精度效果/压缩倍率/创新性/可复现性，1–10）：7/6/8/7。评分依据见本次日报；不同压缩对象的倍率不可直接排序。
