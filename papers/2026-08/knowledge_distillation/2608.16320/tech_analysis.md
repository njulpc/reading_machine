# StreamOPD：技术精读

> arXiv: [2608.16320](https://arxiv.org/abs/2608.16320) · submitted 2026-08-17 · Keming Wu 等 · cs.CV

## 1. 核心速览

**研究主题**：流式视频理解的 on-policy / self distillation。
**一句话总结**：在固定 recent-4-frame、无额外 memory/retrieval/compression 的推理协议下，StreamOPD 用 thinking-mode OPD 训练、instruct-mode 部署；ST-CueGate 再按教师是否可见时空 cue 的似然差重加权。

## 2. 研究背景与动机

复杂流式记忆系统常未胜过 sliding-window 基线；RLVR 又会鼓励不适合实时流的长思考。作者因此固定推理开销，只研究 post-training 能把 4B 学生推近 9B 教师多少。

## 3. 核心方法与创新点

- 用可验证流式视频数据进行 thinking-mode OPD，部署时切回 instruct mode。
- ST-CueGate 比较 cue/no-cue 教师 likelihood ratio，形成 group-relative response score 重加权蒸馏。
- 冻结初始学生可充当 self-distillation teacher，测试收益是否必须来自大教师。

## 4. 实验设计与结果

每个配置 3 seeds；StreamingBench/OVO-Bench 用 1 fps 最近 4 帧。StreamingBench 从 **77.9%** 提到 **83.9%**，距 9B 教师仅 **0.3 点**；OVO-Bench（去 HLD）提高 **9.1 点**。ST-CueGate 达 OVO-Bench **71.9%**、Video-MME **64.9%**；self-distillation 将 HLD 提到 **57.0%**。

## 5. 局限性与未来展望

固定窗口有利于公平归因，但不解决极长依赖；CueGate 需要教师特权 cue，训练成本高。未来可与显式 memory compression 联合，并报告实时端到端延迟。

## 6. 学术启发

评估蒸馏型压缩时，应先锁死 inference protocol，避免把更大记忆或额外检索带来的收益误归因于学生能力。

**证据边界**：已核对官方 HTML 全文的三 seed 协议与主要结果。
