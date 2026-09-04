# LLaDA-Image: Building Strong Image Generators with Fully Open Training Recipes

- arXiv ID：2609.03796
- 作者：Chuyan Chen, Haoxing Chen, Kun Chen, Zhenglin Cheng, Long Cui, Ruishan Fang, Zhangxuan Gu, Zhicheng Huang, Zhenzhong Lan, Yuanting Lei, Haoquan Li, Jianguo Li, Rongchuan Li, Sidu Li, Tao Lin, Deyuan Liu, Jiacheng Liu, Lin Liu, Yuxuan Lou, Zhisheng Lu, Yuxin Ma, Shuheng Shen, Peng Sun, Chaoyang Wang, Hongjun Wang, Xiaomei Wang, Yongxin Wang, Chengzhang Wu, Hongru Wu, Jun Xie
- v1实际提交：2026-09-03T13:02:40Z（UTC）；2026-09-03T21:02:40+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV) ; Artificial Intelligence (cs.AI)
- 本次归类：知识蒸馏；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.03796)；[官方HTML全文](https://arxiv.org/html/2609.03796)；[PDF](https://arxiv.org/pdf/2609.03796)

## 1. 核心速览

研究主题：知识蒸馏。LLaDA-Image 使用原生掩码语言模型并以Turbo蒸馏获得2至4步生成。

## 2. 研究背景与动机

自回归语言模型不天然适合图像扩散所需的双向语义条件，少步生成又可能损失质量。

## 3. 核心方法与创新点

- 冻结LLaDA2.0-mini作为理解编码器，从头训练6B DiT
- 图像预训练和中期训练结合无参数RMSNorm与Muon，另训练Turbo少步版本。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.03796)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

使用约220M训练样本；基础版本在Qwen-Image-Bench英语/中文为53.53/53.38，Turbo支持2–4步。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | 使用约220M训练样本；基础版本在Qwen-Image-Bench英语/中文为53.53/53.38，Turbo支持2–4步。 |
| 压缩倍率 | 8 | 上述质量分数属于对应主模型设置，不能直接归给Turbo；训练数据和算力需求较大，采样步数减少不是权重压缩。 |
| 创新性 | 8 | 冻结LLaDA2.0-mini作为理解编码器，从头训练6B DiT；图像预训练和中期训练结合无参数RMSNorm与Muon，另训练Turbo少步版本。 |
| 可复现性 | 8 | 上述质量分数属于对应主模型设置，不能直接归给Turbo；训练数据和算力需求较大，采样步数减少不是权重压缩。 |

本次未执行该论文训练或基准测试；以上实验数字均为作者报告，评分是阅读判断，不是独立复现实验得分。

## 5. 局限性与未来展望

上述质量分数属于对应主模型设置，不能直接归给Turbo；训练数据和算力需求较大，采样步数减少不是权重压缩。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

理解编码器的双向归纳偏置与少步蒸馏可分别优化，评估时应拆开质量来源。
