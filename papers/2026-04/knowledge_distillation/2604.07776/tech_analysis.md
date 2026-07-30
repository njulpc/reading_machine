# 深度技术分析：Structured Distillation of Web Agent Capabilities Enables Generalization

## 1. 核心速览

**研究主题**：以人类标注角色为类比结构化合成轨迹，蒸馏前沿教师为可本地部署的 web agent。

**一句话总结**：Agent-as-Annotators 用模块化 LLM 组件替代 Task Designer/Annotator/Supervisor 角色，以 Gemini 3 Pro 为教师生成 3,000 条轨迹（六 web 环境）、2,322 条过质量筛选后纯 SFT 训练 9B 学生；WebArena 41.5% 超 Claude 3.5 Sonnet（36.0%）与 GPT-4o（31.5%），近乎翻倍此前最佳开源（21.7%），未见环境 WorkArena L1 +18.2 点。

## 2. 研究背景与动机

前沿 LLM 能操作复杂网站，但成本与 API 依赖使本地部署不现实。轨迹合成的质量决定蒸馏上限，需要结构化的数据生产管线。

## 3. 核心方法与创新点

- **角色化合成管线**：任务设计、标注、监督解耦为模块化 LLM 组件。
- **质量筛选 + 纯 SFT**：简单训练配方配合强筛选即可超越闭源。
- **泛化验证**：未见环境上仍有显著提升，证明能力而非环境记忆被蒸馏。

## 4. 实验设计与结果

WebArena 41.5%（同协议超 Claude 3.5 Sonnet 36.0%、GPT-4o 31.5%、此前开源最佳 Go-Browse 21.7%）；WorkArena L1 +18.2 点；消融证实 Judge 过滤、评估提示、推理轨迹各有显著贡献。

## 5. 局限性与未来展望

局限：依赖单一前沿教师，教师偏差被继承；9B 模型对复杂长程任务仍有限；轨迹合成的成本/多样性强依赖于教师 API。未来方向：多教师混合、在线环境交互蒸馏、更小学生极限。

## 6. 学术启发

- 蒸馏数据工程（角色化管线 + 筛选）比训练算法更决定 agent 蒸馏成败。
- 结构化合成可使小模型在 agent 任务上超越通用闭源大模型。

---

*论文信息：arXiv:2604.07776，Lù Xing Han, Reddy Siva，cs.LG*