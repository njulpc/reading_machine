# 技术精读：Swift-Image

> arXiv: [2608.20334](https://arxiv.org/abs/2608.20334)；v1 提交：2026-08-20；主分类：cs.CV。

## 1. 核心速览

**研究主题**：统一图像生成/编辑模型的结构剪枝与少步蒸馏。
**一句话总结**：Swift-Image 从 6B 统一 DiT 剪到 3B（attention heads 32→24），再用 6B 教师恢复能力；另用 DMD 将 50 步压到 8 步，3B 模型在五项编辑总分仍达 4.15，配 Prompt Enhancer 为 4.31。

## 2. 研究背景与动机

统一文本生成、单图编辑、多图编辑会产生任务冲突，常见大模型既贵又难压。单纯剪枝损失生成能力，少步蒸馏又可能分别偏向 T2I 或编辑。作者把 progressive training、专家 RL、multi-teacher OPD 与部署压缩串成一条恢复链。

## 3. 核心方法与创新点（分点）

1. 6B single-stream DiT 采用层间连接、Qwen3-VL 条件和逐阶段 generation→editing curriculum。
2. 并行训练 T2I、通用编辑和细分专家，再用 multi-teacher on-policy distillation 合并，避免一次混合 RL 的梯度跷跷板。
3. 结构剪枝把 attention heads 从 32 降到 24，直接继承存活参数；3B 学生重走 coarse-to-fine curriculum，并用同噪声/时刻/条件下的 6B velocity 做 L2 KD。
4. DMD/CDM 少步蒸馏从学生自身轨迹取状态，动态 backward simulation 在 {2,4,8,16,28} 步预算间采样，最终部署 8 步；T2I/编辑 few-step experts 再做一次 MOPD。

## 4. 实验设计与结果

基础 6B 训练约 243K GPU-hours。部署压缩将 50 步降至 8 步，参数降至 3B。五项编辑 benchmark 的 3B overall 为 4.15，加入本地 Prompt Enhancer 为 4.31、API PE 为 4.40；GEdit/ImgEdit/REDEdit 分别为 8.10/4.56/4.29。论文称压缩 3B 相对 6B 几乎无损，few-step 版本 overall 4.20，说明采样压缩并未简单牺牲编辑质量。

## 5. 局限性与未来展望

243K GPU-hours 使完整复现门槛极高；大量内部数据、reward model、专家路由与 PE API 影响可比性。3B 的“近乎无损”依赖长恢复 curriculum，不是廉价 one-shot pruning。公开表格以自动/模型 judge 为主，真实用户偏好和硬件延迟仍需独立验证。

## 6. 学术启发

大生成模型压缩更像“剪枝后重新教育”，而非删完做短暂 recovery。参数剪枝和步数蒸馏影响不同维度，最好分阶段优化，并用任务路由教师避免一个教师在生成质量与编辑一致性之间折中。
