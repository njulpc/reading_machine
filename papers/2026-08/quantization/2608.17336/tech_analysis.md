# TileMix: Tile-Centric Mixed-Precision Attention for LLM Inference Acceleration

- arXiv: [2608.17336](https://arxiv.org/abs/2608.17336)
- 提交日期（v1）：2026-08-18
- 作者：Hanzhi Zhang, Qiao Zhang, Qinglei Cao, Heng Fan, Yan Huang, Kewei Sha, Yunhe Feng
- 分类：cs.AI
- 证据边界：基于 arXiv 摘要与 23 页 v1 PDF；速度数据来自 A100 40GB 的 Triton kernel，本文复现只验证数值机制，不伪造 A100 kernel 吞吐。

## 1. 核心速览

**研究主题：** 在 FlashAttention 风格融合 kernel 内按 score tile group 路由 FP16 或 INT8 计算，同时保持完整注意力连接和共享 online softmax。

**一句话总结：** TileMix 用紧凑 bitmask 让每个硬件对齐的 QK score tile group 选择精度；LLaMA-3.2-3B 在 4k prefill 时 SpTrans75 达到 31.80 K token/s，对 FlashAttention 的 14.33 K token/s 为 2.22×，并比统一 INT8 更好地恢复长上下文质量。

## 2. 研究背景与动机

长上下文 prefill 的 QK 计算与内存流量随序列长度二次增长。统一 INT8 虽快，却会在检索和长文本问答上损失精度；稀疏注意力通过删除 token 交互提速，又可能永久丢失远程依赖。作者关注一个中间设计空间：不删边，而是在二维 attention score 平面上选择哪些 tile 值得保留 FP16。

## 3. 核心方法与创新点

1. **tile-group 精度路由。** 将 `Lq×Lk` score 矩阵划分为硬件对齐的 `BLOCK_M×BLOCK_N` tile；相邻 key tiles 可用 group factor `g` 合并，由一个路由 bit 共同控制。
2. **64-bit bitmask。** 每个 KV head、query tile row 用一个 64-bit word 保存最多 64 个 group 决策，kernel 内通过 shift-and-mask 常数时间读取；元数据规模为 `O(H_k T_m)`。
3. **两条算术路径、一个 softmax 状态。** FP16 tile 直接算 QK；INT8 tile 对 Q/K 做 blockwise 对称量化、INT32 累积并恢复 scale。两者回到同一浮点域，更新共享 running max、normalizer 与 output accumulator；V 与 PV 保持 FP16。
4. **密集连接不变。** 所有合法 tile 都执行，只改变算术精度。实现支持 GQA、变长 batch，并提供 INT8 K/V cache 接口。
5. **无训练、无数据校准的路由。** 主实验使用静态 data-free spatial templates（如 SpTrans、BigBird 风格布局）与 25/50/75% INT8 coverage，强调 layout 与 coverage 是两个独立旋钮。

## 4. 实验设计与结果

- 模型/数据：主模型 LLaMA-3.2-3B，并扩展 Vicuna-7B、Qwen-2-7B、Qwen-2.5-7B；LongEval 3.1k–38.7k 检索，LV-Eval 16k/32k/64k 共 11 个中英文数据集。
- 硬件：A100 40GB，batch 8，3 次 warmup、5 次计时；端到端计时包含量化、scale 恢复、路由、数据搬运和调度。
- 速度：4k 时 FlashAttention 14.33 K token/s，统一 INT8（One）29.80 K，SpTrans75 31.80 K；8k 时 FlashAttention OOM，而 TileMix 仍为 22.81–26.61 K token/s。
- 质量：LV-Eval 多数任务中，25/50% 的 SpTrans 或 BigBird 布局接近或超过 FP16；统一 INT8 经常显著落后，证明“INT8 放在哪里”与比例同样重要。
- 数值误差：相对固定 Torch FP16，1k 序列在 0/5/10/25% INT8 coverage 下平均绝对误差约 `7.27e-5/7.47e-4/1.19e-3/2.03e-3`；8k 时 10% 后跃升到 `6.32e-3`，显示长序列更敏感。

## 5. 局限性与未来展望

- kernel 只验证 NVIDIA A100、FP16/INT8 和 prefill；结果不能直接外推到 Hopper、消费级 GPU、其他低比特格式或 decode 主导负载。
- 主路由模板是静态、data-free 的，并未学习 query/task 自适应路由；不同布局在不同数据集上的波动说明自动路由仍是核心问题。
- 论文保留所有注意力边，因此理论 FLOPs 并未像稀疏方法那样下降；收益依赖 INT8 Tensor Core 与融合实现。
- 质量评估集中在少数长上下文模型，尚缺更大 Qwen/Llama、真实服务流量和端到端模型延迟/能耗。

## 6. 学术启发

量化粒度可以从“层/通道/token”继续推进到“二维算子空间的 tile”。TileMix 表明同一层内不同空间位置的数值精度也应被视为可调资源。其 bitmask 路由抽象兼顾硬件可执行性和精度控制，未来可与 learned saliency、KV eviction 或请求级 SLO 联合优化，而不是继续把整层统一量化。

