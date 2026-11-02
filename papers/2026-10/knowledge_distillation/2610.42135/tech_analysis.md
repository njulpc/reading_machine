# A Better Critic Matters for Distribution Matching Distillation

- arXiv：[2610.42135](https://arxiv.org/abs/2610.42135)；[官方 HTML v1](https://arxiv.org/html/2610.42135v1)
- v1 实际提交：2026-10-30T17:58:26+00:00（UTC）；2026-10-31T01:58:26+08:00（Asia/Shanghai）。
- 官方分类（主分类在前）：Computer Vision and Pattern Recognition (cs.CV) ; Machine Learning (cs.LG)
- 压缩归类：knowledge_distillation。证据为官方摘要与上述全文方法、实验及相关附录；以下数字均为论文报告，非本机复现。

## 1. 核心速览

研究主题：knowledge_distillation / A Better Critic Matters for Distribution Matching Distillation。

一句话总结：DMD 蒸馏需要匹配教师规模的 critic，并让 critic 感知生成步，才能稳定获得高质量少步学生。

## 2. 研究背景与动机

DMD 用教师 score 与在线学生分布 critic 的 score 差指导生成器。增大教师并不必然改善学生：critic 容量不足会误估学生分布；多步输出混为一个分布也会给各步错误监督。本文直接研究蒸馏训练信号，而非只扩大教师。

## 3. 核心方法与创新点

1. **联合扩容**：固定学生，对教师与 critic 做二维规模实验，采用匹配容量的 teacher/critic，而不是让 critic 始终等于小学生。
2. **STAC**：critic 额外接收生成步对应噪声级的可学习上下文 token，区分“score评估噪声 t”和“学生第 k 步”。同一 critic 估计各步条件分布，DMD2 的主体损失、教师和采样器不变；推理只保留学生，STAC 不增加部署开销。
3. **机制控制**：比较共享常数 token、冻结随机步 token、AdaLN 条件，以及增加 critic 更新频次等替代方案。ImageNet 默认学生/critic 学习率 8e-6/1e-6，一次 critic 更新对应一次学生更新，batch 64；学生 4 步日程为 999/666/333/124。

## 4. 实验设计与结果

§3、表1–2：ImageNet 256×256、无 CFG，七档 SiT 从 33M 到 951M。1-step B 学生在 200k 更新时，B/B 的 FID 为16.82，XL/B 为41.75，XL/XL 为13.50，说明更大教师搭配小 critic 反而会退化。4-step B 学生、100k 更新，XL/XL 加 STAC 后 FID 8.08→6.90；B/B 为13.91→11.77。常数token、冻结token、AdaLN 分别为7.95、7.76、7.68，均弱于6.90。

表3–5：FLUX.2 的4B、4步学生由32B teacher/critic蒸馏，STAC后 HPSv3=12.32、DPG=85.28；32B、50步基座为12.14、86.79，两项不能合并成全面超越。SDXL 4步 COCO 10k评测，官方DMD2 FID18.95，继续训练无STAC19.49，有STAC16.88。Wan2.1 1.3B学生、14B/14B加STAC的VBench Total84.32，对照14B/1.3B为83.94。

## 5. 局限性与未来展望

强 critic 增加训练显存和计算；联合容量匹配是经验规律，尚无普适理论。50→4是采样次数12.5×，并非测得端到端或权重压缩率；32B→4B仅可称名义参数8×。不同任务表格协议不同，不宜跨表比较绝对分数。本次未执行扩散蒸馏训练。

## 6. 学术启发

知识蒸馏不仅要匹配教师与学生的输出，还要检查估计训练信号的中间模型是否足够强。少步生成的“步身份”是一个低成本条件变量；可优先验证其是否减少不同生成步的score偏差，再讨论更昂贵的联合扩容。

评分（1–10）：精度效果8，压缩倍率/资源削减8，创新性8，可复现性7。

准确率8：多架构少步质量改善；压缩8：参数和采样步有明确削减，非实测同倍加速；创新8：critic容量与步条件的控制实验；复现7：超参数充分，但多模型蒸馏成本高。

本轮为非量化论文精读，未执行论文训练或运行时基准；可复现性评分衡量公开方法的可操作程度，不表示本轮已复现。分析日期：2026-11-03。
