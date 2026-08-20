# 技术深度分析：Group-Calibrated On-Policy Distillation

> arXiv: [2608.19181](https://arxiv.org/abs/2608.19181) · v1: 2026-08-19 17:54:58 UTC · 主分类：cs.LG

## 1. 核心速览

**研究主题**：长上下文推理中，用任务 verifier 校准教师 token 似然的 on-policy 蒸馏。

**一句话总结**：GC-OPD 在 rollout group 内分别标准化 verifier reward 与轨迹 OPD 分数，以二者差形成有符号残差，再由相对优势分配到 token；Qwen3-4B/8B 五任务均分由 vanilla OPD 的 39.31/43.56 提至 40.47/44.65。

## 2. 研究背景与动机

OPD 用强教师对学生自身生成逐 token 打分，提供密集监督；但长上下文任务要求跨段聚合证据，教师对局部流畅回答可能给高似然，却遗漏全局约束。任务 verifier 能看最终完成度，却通常是稀疏或不同量纲的 response-level 信号。直接相加会重复奖励教师已经偏好的轨迹，且难以分配到 token。

## 3. 核心方法与创新点

- 在每个 8-response rollout group 中分别标准化 verifier reward R 与轨迹平均 OPD score s。
- 定义残差 ρ=R~-s~：只补偿 verifier 与教师评价的相对分歧，而非简单增加 reward。
- RACA 根据 token 的相对 OPD advantage 保留符号地分配残差；避免绝对值分配把大负优势误当高信用。
- 支持二元与连续 verifier，无需跨任务统一原始奖励量纲，也不增加额外教师/学生 forward。

## 4. 实验设计与结果

训练集是 GoLongRL 经 32K 过滤后的 9,527 条提示、9 个任务族；每步 32 prompt×8 response，共 100 step，最大 prompt 32,768、response 10,240 token。教师为 Qwen3-30B-A3B-Thinking-2507，学生为 Qwen3-4B/8B；评估 DocMath、Frames、MRCR、CorpusQA、LBv1QA，服务上下文 131,072。

Qwen3-4B 的 Raw/OPD/GC-OPD 均分为 29.08/39.31/40.47，8B 为 35.12/43.56/44.65。8B 的 CorpusQA 从 OPD 39.82 升到 43.77；增益并非每任务一致，LBv1QA 从 57.80 到 58.30。信号消融中 Additional OPD 43.60、Direct Reward 44.19、GC-OPD 44.65；信用分配消融中 Absolute OPD 43.93、Uniform 44.28、RACA 44.65，支持“残差化+保留相对符号”两个设计。

## 5. 局限性与未来展望

训练只跑 100 step，验证选择 β=0.10 的 holdout 仅含 High-Recall Retrieval，任务分布又由两大族占 82.9%。实验局限于 Qwen3 两个学生和一个教师，未给压缩倍率或推理加速；方法价值体现在更好利用固定小模型，而非改变参数规模。未来需验证多教师、无可靠 verifier 与更长训练的稳定性。

## 6. 学术启发

密集教师信号与任务级验证不是竞争关系：先测量二者分歧，再用“残差”只修正未被教师表达的部分，可以避免双重计数。对蒸馏和 RLHF，response-level 信号如何落到 token 的符号与相对尺度，可能比奖励本身更重要。
