# 技术精读：ArmorOCR

> arXiv: [2608.20122](https://arxiv.org/abs/2608.20122)；v1 提交：2026-08-20；主分类：cs.CV。

## 1. 核心速览

**研究主题**：用特权视觉观察做 on-policy self-distillation，提升对抗 OCR。
**一句话总结**：ArmorOCR 先把变换后更易读图像中的感知能力蒸馏回原图学生，再用四类 GRPO reward 精炼定位与识别；Qwen3-VL-8B 在 AdvSpot 的平均准确率/IoU 从 31.2/49.1 提到 55.7/63.3。

## 2. 研究背景与动机

人能读出的镜像、点线编码、低对比与图案覆盖文字会让 LMM OCR 失效。调用外部图像工具或多轮“thinking with images”增加推理延迟。作者希望训练期借用特权变换观察，推理时把能力固化进原模型参数，不增加额外视觉工具。

## 3. 核心方法与创新点（分点）

1. 构建 AdvSpot：390 张图、397 个 grounded VQA pair、5 个主类和 13 个细类，同时评估答案与 bbox IoU。
2. Stage 1 的教师看到原图、可读的特权变换图和 OCR guidance，学生只看原图；analysis token 用置信门控广义 JSD，answer token 用 forward KL。
3. response-region-aware loss 忽略结构标记，只蒸馏感知分析和最终文本，避免格式 token 稀释监督。
4. Stage 2 用 GRPO 联合 text-to-bbox IoU、bbox-to-text 编辑相似度、spotting pair-F1 和 grounded-VQA answer inclusion 四种 reward。

## 4. 实验设计与结果

Stage 1/2 分别用 50K/70K 合成样本，目标模型为 Qwen3-VL-8B，测试均为 zero-shot。AdvSpot 平均准确率由 31.2% 升至 55.7%，IoU 49.1% 升至 63.3%；完整两阶段优于任一单阶段。AdvOCR 平均准确率 56.0%，SmuggleBench 17.1%；对后者 AI Illusions 类比 235B Smuggle-CoT 高 8 个百分点。三个通用 OCR benchmark 基本保持原能力，说明蒸馏没有明显灾难性遗忘。

## 5. 局限性与未来展望

训练需要可构造的特权变换和 120K 合成样本，未知攻击与真实世界复杂文字可能不符合 taxonomy。学生与教师同源，自蒸馏受教师上限限制；Stage 2 的多 reward 也增加训练与评测成本。论文没有证明参数量或推理 FLOP 下降，压缩价值是“去掉推理期工具链”。

## 6. 学术启发

特权信息蒸馏可以被理解为把测试时工具调用离线编译进模型。关键不是让教师给一个更好答案，而是按 response region 区分中间感知与最终输出，并为不同区域选择合适散度与置信门控。
