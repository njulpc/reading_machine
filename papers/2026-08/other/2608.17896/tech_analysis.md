# Dynamic Compression in Recurrent Networks

- arXiv: [2608.17896](https://arxiv.org/abs/2608.17896)
- 提交日期（v1）：2026-08-18
- 作者：Jyothish Pari, Ryan Bahlous-Boldi, Pulkit Agrawal
- 分类：cs.LG
- 证据边界：基于 arXiv 摘要与 13 页 v1 PDF；这是 recurrent state/上下文压缩，不是权重压缩，实验为受控合成矩阵回归。

## 1. 核心速览

**研究主题：** 让固定大小 recurrent state 在知道当前任务后选择性重扫历史 token，动态重写过去信息的表示精度。

**一句话总结：** 在 K=3 的合成 in-context function reuse 中，oracle dynamic re-scan 用约 111k state elements 就优于 3.1M state 的单次模型；无标签 codebook 版本 MSE 为 `4.91±1.53e-3`，显著低于 single-pass 的 `67.06±95.99e-3`。

## 2. 研究背景与动机

RNN/linear attention 把不断增长的上下文写入固定 state。单次因果写入时，模型尚不知道哪段历史稍后重要，只能平均分配有限容量。Transformer retrieval 可以无损读过去，而 RNN 重访 token 会再次写 state，因此有机会在任务揭示后重新压缩历史。

## 3. 核心方法与创新点

1. **selective re-scanning。** 在 few-shot block 结束时，selection head 预测所需 basis；模型把该 basis 的 token 再送入同一 recurrence，随后回答 query。
2. **状态需求分解。** 识别 K 个 basis 中哪一个相关只需约 3k state elements，而同时高保真存储 3 个 basis 需约 3.1M；先识别再重扫能利用这一差距。
3. **自监督 re-scan codebook。** 训练一个重复整段 prefix 的 repeat model，读取二次写入时的 GatedDeltaNet write strength `β`；对最终层 52 维 β pattern 做 k-means（C=3），每个 centroid 选 top-21 token 形成 code。
4. **推理时无重复全上下文。** dynamic model 先预测 code，只重扫对应 21 个 token，再回答；无需 ground-truth basis label。

## 4. 实验设计与结果

- 模型：4-layer GatedDeltaNet、6 heads、embedding 256、value expansion 2；state size 为 `4·6·d_head²·2`。
- 状态扫描：`d_head={8,48,256}` 对应 3,072、110,592、3,145,728 state elements；K=3，训练 150k steps、batch 512、3 seeds。
- 结果：动态 111k state 的错误低于单次 3.1M state。固定 `d_head=12` 时，误差随 basis 数 K 增长的幂律指数，single-pass 约 6.1，dynamic 约 2.3。
- codebook 比较（`d_head=16`, 50k steps）：single-pass `67.06±95.99`、repeat `1.38±0.44`、oracle dynamic `2.30±2.44`、codebook dynamic `4.91±1.53`，单位均为 `1e-3` MSE。
- 注意 single-pass 均值被一个高方差 seed 拉高，其中位数为 `17.4e-3`；K=6 也有一个 dynamic seed 优化失败。

## 5. 局限性与未来展望

- 仅合成矩阵函数复用，任务边界、basis block 和 query 结构都很明确；自然语言中如何定义可重扫区域仍未知。
- codebook、C=3 和固定 21 token 都针对该合成环境，不能直接迁移。
- 保留 raw context 作为无损后备存储，减少 state 的同时并未消除原上下文内存；本质是 computation-memory trade-off。
- 训练集极大（codebook dynamic 使用预生成 `5×10^7` sequences），且存在 seed 失败和高方差。

## 6. 学术启发

上下文压缩不必是 token 首次到达时的一次性决定。把 raw context 当冷存储、固定 recurrent state 当可重写工作内存，可在任务到来后按需增加局部保真度。该思想与 KV cache eviction 的区别在于：它不只是找回旧信息，而是用旧信息重构当前状态，值得在自然语言 post-training 与 agent memory 中继续探索。

