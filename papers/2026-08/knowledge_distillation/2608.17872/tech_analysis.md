# DistillPath: An Efficient 22M Distilled Pathology Encoder Approaching Large Foundation Model Performance

- arXiv: [2608.17872](https://arxiv.org/abs/2608.17872)
- 提交日期（v1）：2026-08-18
- 作者：Ramon Kaspar, Andrey Ignatov, Valentina Boeva
- 分类：cs.CV
- 证据边界：基于 arXiv 摘要与 26 页 v1 PDF；每个 teacher 的蒸馏只运行一次，EVA 的多次方差来自下游 probe，而非独立蒸馏种子。

## 1. 核心速览

**研究主题：** 仅访问已发布病理 foundation encoder 的最终 class/patch tokens，将 86M–1.1B teacher 压入 22M ViT-S/16。

**一句话总结：** 最佳 DistillPath-KS16-Virchow2 在七任务 EVA mean 达到 0.795，距 632M Virchow2 的 0.810 仅 0.015，参数少约 29×，RTX 4090 tile throughput 快 26.6×。

## 2. 研究背景与动机

数字病理 whole-slide image 含数千 tile，使用数亿到十亿参数的 encoder 预编码和存储特征成本很高。现有大规模蒸馏往往需要 teacher 的 DINO/iBOT heads 或十亿 tile 训练集，难以应用到只公开 backbone 的模型。论文目标是设计一个只需要最终 token 的通用 recipe。

## 3. 核心方法与创新点

1. **固定 22M student。** 从 pathology-pretrained kaiko ViT-S/16 初始化，384 维输出；teacher 包括 H0-mini 86M、Virchow2 632M、UNI2-h 681M、H-optimus-0 1.1B。
2. **class token 双重约束。** 经 MLP projector 后用 cosine 做点对点对齐；同时用 RKD 匹配 batch 内距离与三元角度，不要求 teacher/student 同维。
3. **patch token 空间对齐。** 将 patch-14 teacher 的 16×16 token grid bicubic resize 到 student 的 14×14，再做 cosine；register tokens 被忽略。
4. **统一损失配比。** `L = L_cos + γ_T L_RKD + λ_T L_patch`；按 teacher 调整 `γ/λ`，使训练后期 RKD 约占 class loss 25%、patch loss 约占总损失 25%。
5. **公开数据在线采样。** 6,000 张 TCGA slide、32 cohorts，在线采 256×256 tile，50k steps、batch 256，共 12.8M accepted views。

## 4. 实验设计与结果

- 训练：AdamW、lr `1e-4`、weight decay 0.05、500 warmup、bf16；单 RTX 4090 每个 run 24–29 GPU·h。
- EVA：kaiko baseline 0.764；四个 distilled variants 全部提升。Virchow2 student 0.795，teacher 0.810；BreakHis 从 0.720 到 0.849，但它在 7 个任务中仍有 5 个落后 H0-mini，优势并非均匀。
- HEST：最佳反而是 H0-mini student 0.387，Virchow2 student 只有 0.371；PLISM 最佳同样是 H0-mini student 0.495，说明 teacher 大小不能预测迁移效果。
- 效率：22M student 在 RTX 4090 达 7,994 tiles/s，Virchow2 300 tiles/s；CUDA peak 374 MiB vs 4,551 MiB，fp32 特征存储 1.43 vs 4.77 GiB/百万 tile。
- 泛化：ImageNet-21k 初始化的 22M student 也从 EVA 0.729 提升至 0.754–0.768，但仍明显低于 pathology 初始化的 0.795。

## 5. 局限性与未来展望

- 只有 ViT-S/16 student，未区分容量瓶颈、teacher-student 维度差异和优化 recipe 的影响；未测试随机初始化或 ViT-B student。
- 每个 teacher 仅单次蒸馏，缺少训练方差；主损失配比没有对所有 teacher 做完整网格消融。
- 训练 slide 全来自 TCGA，域与扫描分布不及 teacher 原始训练集多样；多 teacher 蒸馏未测试。
- 固定 class-token 接口可能低估推荐使用 class+patch pooling 的 teacher。

## 6. 学术启发

teacher 越大不代表越适合某个固定 student。可蒸馏性取决于表示维度、目标任务和 student 初始化的匹配。DistillPath 还说明 backbone-only token 是一种实用“最小开放接口”：不要求训练 heads，即可把闭合的预训练 recipe 转化为可部署的小 encoder。

