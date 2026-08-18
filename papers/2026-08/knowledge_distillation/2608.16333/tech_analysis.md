# Step-Level On-Policy Distillation：技术精读

> arXiv: [2608.16333](https://arxiv.org/abs/2608.16333) · submitted 2026-08-17 · Changhui Sun 等 · cs.CL / cs.AI

## 1. 核心速览

**研究主题**：连接 SFT 与 token-level OPD 的 step-level 蒸馏。
**一句话总结**：SOPD 让学生先生成完整轨迹，再从每个学生 step 前缀请求教师续写一个完整 step，既覆盖学生真实状态又给出长程修复路径。

## 2. 研究背景与动机

token OPD 在错误轨迹上只能给碎片化局部校正，无法展示从当前状态回到正确解的完整路径；SFT 有完整路径却不一定覆盖学生会访问的状态。

## 3. 核心方法与创新点

- step 是 agent 的一次环境交互或推理中的自然边界。
- step 数趋近 1 时退化为 SFT；step 长度趋近 1 token 时近似 forward-KL OPD。
- 对每个学生 prefix 独立生成教师 step，提供 on-policy 的长程目标。

## 4. 实验设计与结果

ALFWorld 用 Qwen2.5-7B teacher 蒸馏 Qwen2.5-3B student，评估 Seen-140、Unseen-134、Hard-121。相对 vanilla OPD，Seen 从 **65.72→84.29**，Unseen 从 **60.45→82.09**，平均轮数分别少 **3.53/4.33**；Hard 为 **10.74%**。四个数学基准平均 **57.7%**，对 OPD **47.7%**，各题采样 32 个解。

## 5. 局限性与未来展望

每个学生 step 都调用教师，标注成本高；step 边界依赖任务结构，错误切分会改变监督粒度。可研究自适应边界、缓存教师目标和低成本 verifier。

## 6. 学术启发

蒸馏粒度是连续旋钮而非 SFT/OPD 二选一；“学生状态覆盖”和“完整纠错跨度”可以用 step 长度显式权衡。

**证据边界**：已核对官方 HTML 全文的 ALFWorld 与数学表格。
