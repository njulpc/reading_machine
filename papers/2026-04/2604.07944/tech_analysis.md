# 深度技术分析：On-Policy Distillation of Language Models for Autonomous Vehicle Motion Planning

## 1. 核心速览

**研究主题**：自动驾驶运动规划中 LLM 的在线策略蒸馏（GKD）。

**一句话总结**：基于 GPT-Driver 框架比较两种学生训练范式：在线策略广义知识蒸馏（学生自生成输出 + 教师稠密 token 反馈）与教师 log-prob 作 per-token 奖励的策略梯度 RL 基线；nuScenes 上 GKD 显著优于 RL 基线，5 倍模型缩减下接近教师水平。

## 2. 研究背景与动机

LLM 运动规划有潜力，但车载系统资源受限，需要把大教师的能力迁移到小可部署学生。

## 3. 核心方法与创新点

- **GKD 用于规划**：on-policy 蒸馏首次系统应用于 AV 运动规划。
- **与 RL 基线受控对比**：同教师信号、不同利用方式，证明蒸馏框架的优越性。

## 4. 实验设计与结果

nuScenes：GKD 显著优于稠密反馈 RL 基线；5× 模型缩减下接近教师表现。

## 5. 局限性与未来展望

局限：开环评估为主，闭环安全性未验证；nuScenes 规模有限；对长尾场景的教师-学生能力差距未细化分析。未来方向：闭环评估、与安全约束结合、多模态教师。

## 6. 学术启发

- on-policy 蒸馏在安全攸关的小模型部署中值得优先考虑——token 级稠密反馈比奖励信号更高效。

---

*论文信息：arXiv:2604.07944，Afsharrad Amirhossein 等，cs.RO*