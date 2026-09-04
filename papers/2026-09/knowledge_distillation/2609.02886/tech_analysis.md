# SolarWM: Open Data and Scalable Training for Long-Horizon Video World Models

- arXiv ID：2609.02886
- 作者：Junchao Huang, Guian Fang, Shengju Qian, Xianghao Kong, Zhuoran Zhao, Wei Huang, Yihua Du, Zixin Zhang, Justin Cui, Yuchao Gu, Yukang Chen, Xinting Hu, Tianyu He, Shaoshuai Shi, Zhuotao Tian, Xin Wang, Mike Zheng Shou, Li Jiang
- v1实际提交：2026-09-02T17:59:41Z（UTC）；2026-09-03T01:59:41+08:00（Asia/Shanghai）
- 主分类：Computer Vision and Pattern Recognition (cs.CV)；全部分类：Computer Vision and Pattern Recognition (cs.CV)
- 本次归类：知识蒸馏；阅读依据：官方摘要及可读HTML全文。
- 来源：[arXiv摘要与v1提交历史](https://arxiv.org/abs/2609.02886)；[官方HTML全文](https://arxiv.org/html/2609.02886)；[PDF](https://arxiv.org/pdf/2609.02886)

## 1. 核心速览

研究主题：知识蒸馏。SolarWM 以统一动作数据和分阶段蒸馏，把视频基础模型转为实时自回归世界模型。

## 2. 研究背景与动机

长时交互需要因果、连续的视频生成，双向多步扩散模型难以直接满足实时控制。

## 3. 核心方法与创新点

- 整合10个数据集约1.43M样本
- 对5–33B模型依次进行双向适配、教师强制自回归初始化和分布匹配蒸馏，从短片训练迁移到连续滚动。

方法及实验证据见[官方全文](https://arxiv.org/html/2609.02886)；下述局限和学术启发包含本次评读判断。

## 4. 实验设计与结果

覆盖Wan2.2、LTX2.5、MiniMax H3等骨干；使用约5秒训练片段展示分钟乃至小时级运行。

论文报告的效果与下面的本地验证是不同证据。不同骨干、数据、硬件或预算下的指标不合并计算；未提供统一压缩率时不从参数规模或采样步数推算整机收益。

| 维度 | 评分（1–10） | 依据 |
|---|---:|---|
| 精度效果 | 8 | 覆盖Wan2.2、LTX2.5、MiniMax H3等骨干；使用约5秒训练片段展示分钟乃至小时级运行。 |
| 压缩倍率 | 8 | 能持续生成不等于长期物理一致；步数压缩和实时性需对应具体硬件及分辨率，本文不虚构统一FPS。 |
| 创新性 | 8 | 整合10个数据集约1.43M样本；对5–33B模型依次进行双向适配、教师强制自回归初始化和分布匹配蒸馏，从短片训练迁移到连续滚动。 |
| 可复现性 | 7 | 能持续生成不等于长期物理一致；步数压缩和实时性需对应具体硬件及分辨率，本文不虚构统一FPS。 |

本次未执行该论文训练或基准测试；以上实验数字均为作者报告，评分是阅读判断，不是独立复现实验得分。

## 5. 局限性与未来展望

能持续生成不等于长期物理一致；步数压缩和实时性需对应具体硬件及分辨率，本文不虚构统一FPS。

可行的后续验证：围绕这一限制设置保持模型、数据与推理预算一致的对照，分开测量质量、实际内存、延迟与前期训练/校准成本。

## 6. 学术启发

先解决因果接口再做分布匹配，能把蒸馏目标对齐实际交互时的状态分布。
