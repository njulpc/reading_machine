# WAM-OPD: On-Policy Distillation for World Action Models

> arXiv: [2608.22364](https://arxiv.org/abs/2608.22364) · v1: 2026-08-23 · 主分类: cs.AI
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：世界动作模型的 on-policy 蒸馏修复。
**一句话总结**：让加速 student 自己决定状态分布，再由 frozen teacher 为这些 history 生成视频与动作监督，可缓解离线蒸馏的分布偏移；Flash-WAM 在 RoboTwin 两任务从 0.0%→58.3% 和 16.7%→33.3%。

## 2. 研究背景与动机

视频优先 WAM 的 student 虽然推理更快，却会进入离线数据未覆盖的状态；继续模仿固定离线轨迹不能修复自己造成的错误。稀疏奖励 RL 又昂贵且难稳定。

## 3. 核心方法与创新点

- student 在环境中行动，训练分布与部署分布一致。
- frozen teacher 对 student history 产生一致的视频计划与动作 target。
- action branch 在 student 自己生成的视频计划下训练，避免 train-test conditioning mismatch。
- 联合 video/action loss、action flow-matching regularizer，只更新 shared backbone 的轻量 adapter。

## 4. 实验设计与结果

RoboTwin 2.0 仅选两个任务：HANDOVER MIC 从 0.0% 提升到 58.3%，PUT OBJECT CABINET 从 16.7% 到 33.3%。结果证明 on-policy dense supervision 能恢复能力，但作者主动把它界定为 task-specific capability proof，而不是广泛泛化结论。

## 5. 局限性与未来展望

任务数、rollout 数和模型覆盖都很小；teacher 在线标注成本以及错误 teacher target 的累积影响未被充分量化。未来应扩展多任务、多 seed，并比较同等 teacher-query 预算下的离线蒸馏和 RL。

## 6. 学术启发

蒸馏不只压模型，还要匹配 student 会访问的状态分布。对具身模型，评价应报告“压缩后速度 + student-induced distribution 上的成功率”，而非只在 teacher 数据上测 imitation loss。
