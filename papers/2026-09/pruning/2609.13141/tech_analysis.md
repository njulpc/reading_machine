# SAS: Simple Attention Sparsification via End-to-End Optimization of Context Ranking

- arXiv：[2609.13141](https://arxiv.org/abs/2609.13141)
- 全文：[官方 HTML v1](https://arxiv.org/html/2609.13141v1)
- v1：2026-09-11T17:58:06Z；北京时间 2026-09-12T01:58:06+08:00
- 主分类：Computation and Language (cs.CL)；全部分类：Computation and Language (cs.CL)
- 作者：Zhiwei Li, Lei Zhu, Hao Gu, Xiang Hu, Yan Wang, Haitao Mi, Sirui Han, Leo Liang, Zhijiang Guo
- 证据边界：本次阅读可获取官方全文，数字标明原论文或本机实测；未把作者结果声称为本机复现。

## 1. 核心速览

研究主题：预训练 Transformer 的可训练块级稀疏注意力。

一句话总结：SAS 将连续选择分数以 log gate 放入注意力 softmax，通过语言建模损失训练块排序，紧预算下胜过注意力蒸馏，但超长上下文的针状检索仍严重退化。

## 2. 研究背景与动机

普通 Top-K 选择阻断离散选择梯度，于是许多可训练稀疏注意力方法模仿密集注意力分布。然而“权重大”不总等于在固定预算下“最利于预测”。本文以最终语言建模目标优化排序；属于注意力计算剪枝，不是永久权重剪枝或把全部 KV 从内存中删除。

## 3. 核心方法与创新点

1. **区分当前块与历史块**：历史块由 selector 产生分数 s，g=softmax(s)；当前块始终保留、gate=1。选择 Top-K 历史块，再加当前块组成注意力集合。
2. **训练时门控位置**：输出为 softmax(qKᵀ + log g)V；log gate 在 softmax 内，使标准语言建模损失能沿所选块的连续分数反传到 selector。将 gate 乘在 softmax 外、用独立 sigmoid 或 STE 硬门控都在消融中较弱。
3. **稀疏训练范围**：只对当前选中块计算注意力，节约训练成本。未选中块仅通过归一化间接受梯度影响，缺少其自身内容信号；全文实验显示早期较慢但最终可接近全范围训练，并不是梯度与全范围完全相同。
4. **推理移除连续 gate**：只根据学得的分数选 Top-K，然后普通 softmax(qKᵀ)V。不能把训练公式直接当作其推理算法。
5. **工程实现**：Triton 融合块门控与在线 softmax；SGLang/FlashInfer 推理后端支持 GQA、分页 KV 与 CUDA graph。prefill 仍密集，decode 读取选中 KV；selector 仍扫描历史块摘要，因此整个系统并非严格上下文无关 O(1)。

## 4. 实验设计与结果

后训练使用 Qwen3 4B/8B/14B，冻结主干，仅训练与 SeerAttention-R 相同的 AttnGate，区分训练信号带来的收益。OpenR1-Math-220k 训练 1 epoch、max length=32768、global batch=32，AdamW lr=1e-3、cosine decay、block size=64，VeOmni/FSDP。测试覆盖数学推理、LongBench、BFCL 多轮、VitaBench，代理测试用 YaRN 扩至 65536。

表 2：Qwen3-4B、预算 2048，AIME24 从 SeerAttention-R 55.83 提高至 SAS 68.85，密集基线 71.25；GPQA 49.94→54.86，密集 56.19。预算 4096 时 AIME24 为 71.72，但标准差约 6.8，不能据小幅高于密集基线证明更强推理。表 3：Qwen3-14B、预算 2048 的 LongBench 8K+ 子集为 53.9，Seer 51.5，密集 55.0。表 4：14B、预算 4096，BFCL 44.00，密集 44.50。

第 6.3 节在单 GPU、TP=1、CUDA graph、预填充后计时 512 个生成 token 的 steady-state decode：batch=1，64K/256K/512K 上下文加速约 2.4×/4.6×/5.6×；batch=8，在 64K 达约 13×。这是 **decode 延迟**，不含 prefill，也不是文件或常驻 KV 的压缩倍率。Top-K 在 512K 时约占稀疏 decode 成本 90%，表明瓶颈转移到选择。

继续预训练实验另用 OLMo3-7B，block=64、Top-K=32，全模型与 selector 一起训练约 50B tokens（13000 steps、batch=512、length=8192，lr 2e-4→2e-5）。通用任务平均 SAS 43.28，密集原模型 43.88；LongBench 30.0 vs 29.0，说明结果随任务变化。

## 5. 局限性与未来展望

附录 B 最重要的反例：Qwen3-14B，128K RULER，4096 预算 SAS 29.95、Seer 22.36、密集 82.23。即使优于稀疏基线，仍远不等价于保留密集长文本能力。均值池化块摘要可能损失细粒度针状信息，需要更好的 selector。另有数学数据到代理任务的分布迁移、训练/推理门控差异、长上下文 Top-K 开销。

完整 KV 仍由系统维护以供后续选择；预算/上下文之比仅刻画被读取的注意力 token 数，不能直接当作 KV 容量压缩比。部分 Quest 数字从其他论文图中提取，非统一重跑。本文测试范围有误差条但并非所有指标均报告充分多种子统计。

本次核验官方 HTML、主表、decode 说明与 RULER 附录，未训练选择器或执行 SGLang 单 GPU 基准；缺少 NVIDIA GPU 和相应 selector checkpoint。无新增量化算法，不建立 Qwen 量化复现目录。

## 6. 学术启发

压缩时应对最终任务损失优化资源选择，而不是仅模仿被压缩模块的内部权重。复现需固定 selector 架构与训练预算，分别验证梯度注入位置、归一化、连续分数及训练范围。部署评价同时记录 prefill、decode、选择开销与检索失败，避免高平均速度掩盖关键长文本能力损失。
