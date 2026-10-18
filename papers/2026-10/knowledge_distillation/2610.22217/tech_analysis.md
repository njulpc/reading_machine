# Skill-Decoupled On-Policy Expert Distillation for Unified Vision-Language Models

- arXiv：[2610.22217](https://arxiv.org/abs/2610.22217)；[官方全文 v1](https://arxiv.org/html/2610.22217v1)
- v1 UTC：2026-10-15T17:01:41+00:00；北京时间：2026-10-16T01:01:41+08:00
- 主分类及交叉分类：Computer Vision and Pattern Recognition (cs.CV) ; Artificial Intelligence (cs.AI)
- 本轮证据：官方abs本轮刷新，标题/摘要/分类/history与缓存一致；全文来自10月18日保存的官方HTML v1，本轮阅读方法、主要实验及相关局限段落，未声称逐行审计全部附录。

## 1. 核心速览

研究主题：knowledge_distillation。

一句话总结：SCOPED 将四类视觉专家的程序化技能蒸馏进一个VLM，8B学生的八基准均分从67.30升至73.13。

## 2. 研究背景与动机

不同视觉任务的联合RL梯度可能冲突，独立训练专家又带来多个部署checkpoint。直接复制专家轨迹还可能继承reward hacking，需要分离技能与偏差。

## 3. 核心方法与创新点

1. 感知/定位、OCR/图表、符号、多图四类数据分别训练专家，总37,999样本，各类约9500。
2. 用奖励区分成功/失败轨迹，经反思提炼能力级skill；教师获得skill，学生不获得，形成特权信息差。
3. 在学生轨迹上做skill增强的专家蒸馏，保留一个统一模型；4B和8B均来自同规模Qwen3-VL backbone，不能把对比32B成绩称为32B教师压缩实验。

## 4. 实验设计与结果

八基准包含CountBenchQA、PixMo、CC-OCR V2、ChartQA、VisualPuzzles、We-Math、MUIR、MMSI；OCR使用micro-F1，其余准确率，整体为算术均值。SCOPED-8B73.13，base67.30，Qwen3-VL-32B72.01；4B69.96，base66.06。专家训练示例配置3epoch、rollout batch128、8responses、LR1e-6、BF16，A800。四专家到一学生约4×checkpoint份数，非单模型参数减少4倍。

## 5. 局限性与未来展望

四类任务与主干有限，skills反思质量依赖教师，训练成本包含多专家RL。混合不同metric的平均分有解释边界；4B的MMSI29.40低于base30.20，不能声称每模型每任务都提高。未实跑多专家训练。

## 6. 学术启发

多教师压缩不仅是输出分布混合，可以先把可迁移程序抽取成教师侧条件。应增设等算力联合RL、无skill蒸馏与技能质量扰动，以隔离真正的迁移来源。

## 四维评分（1–10，主观研究评估）

|维度|分数|依据|
|---|---:|---|
|精度效果|8|8B均分+5.83但4B有单项回退|
|压缩倍率|6|4→1专家份数，单学生尺寸不变|
|创新性|8|教师有技能学生无技能的非对称监督|
|可复现性|7|数据/训练框架明确，本轮未跑A800|

所有原论文实验数字来自上述官方全文，非本机重跑结果。仅FALCON条目的Qwen转移实验为本轮实际运行；速度、token预算、缓存份数与权重字节不可互换。
