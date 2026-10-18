# MMSearch-OPD: Easy Made Hard, Hard Made Learnable for Long-Horizon Multimodal Search Agents

- arXiv：[2610.22240](https://arxiv.org/abs/2610.22240)；[官方全文 v1](https://arxiv.org/html/2610.22240v1)
- v1 UTC：2026-10-15T17:16:18+00:00；北京时间：2026-10-16T01:16:18+08:00
- 主分类及交叉分类：Computer Vision and Pattern Recognition (cs.CV)
- 本轮证据：官方abs本轮刷新，标题/摘要/分类/history与缓存一致；全文来自10月18日保存的官方HTML v1，本轮阅读方法、主要实验及相关局限段落，未声称逐行审计全部附录。

## 1. 核心速览

研究主题：knowledge_distillation。

一句话总结：MMSearch-OPD 用27B教师对9B学生的失败搜索轨迹提供选择性token指导，联合RL后七基准均分60.2。

## 2. 研究背景与动机

长程多模态搜索既缺难题也缺中间反馈。仅终局奖励不能指出哪次检索错误，持续模仿教师又可能限制学生探索，因而需要按成功程度控制监督。

## 3. 核心方法与创新点

1. BuildLink从已知易题构造实体链，Expand/Blur/Visualize分别增加跳数、实体歧义和视觉证据，验证指定证据链的必要性。
2. Qwen3.5-27B在全部成功轨迹上SFT并冻结；Qwen3.5-9B在较易子集SFT后，针对更难题联合GRPO与OPD。
3. 仅正确度c<1且教师评分有效时启用OPD，权重[1-R]_+；对采样token的教师/学生log概率比裁剪，stop-gradient作为反馈。OPD系数从0.05起每10步衰减100倍，KL系数0.01。

## 4. 实验设计与结果

MMSearch、LiveVQA、BC-VL、MM-BC、MMSearch+、BC-V3和VisBrowse七项等权：9B基础agent44.9→SFT57.9→RL+OPD60.2；27B SFT教师63.2，未调27B agent56.7。9B学生相对教师参数数目约3×缩减，但仍低3.0均分；不能把15.3点提升全部归因OPD，因为SFT已贡献13.0点。最多50交互轮，final answer由Qwen3.6-35B-A3B判断三次取均值。

## 5. 局限性与未来展望

网页环境和自动judge会引入可复现差异，检索工具成本可能主导整套系统。参数比不等于3×真实延迟或内存收益；没有本轮在线服务或训练复现。

## 6. 学术启发

压缩agent时，按失败程度分配token监督可避免对已正确轨迹的过度模仿。应增加纯RL、恒定OPD和同数据SFT控制，以区分数据难度、蒸馏与在线探索的贡献。

## 四维评分（1–10，主观研究评估）

|维度|分数|依据|
|---|---:|---|
|精度效果|8|学生60.2但教师63.2|
|压缩倍率|7|27B→9B约3×参数而非系统成本|
|创新性|7|奖励缺口门控及衰减教师指导|
|可复现性|7|框架明确但动态检索与judge影响复跑|

所有原论文实验数字来自上述官方全文，非本机重跑结果。仅FALCON条目的Qwen转移实验为本轮实际运行；速度、token预算、缓存份数与权重字节不可互换。
