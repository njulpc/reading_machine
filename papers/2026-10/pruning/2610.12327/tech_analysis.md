# SparseDecoding: Decoding-Aware Pruning for Accurate and Efficient LLM Inference

[官方摘要](https://arxiv.org/abs/2610.12327) · [官方 v1 全文](https://arxiv.org/html/2610.12327v1)

v1 UTC：2026-10-08T17:06:32+00:00；北京时间：2026-10-09T01:06:32+08:00。主分类及交叉分类：Machine Learning (cs.LG) ; Computation and Language (cs.CL)。

证据范围：已读完整摘要和官方全文 §3–5；不声称逐页通读全部附录。下列实验数字来自论文，本地复现另行标注。

## 1. 核心速览

研究主题：LLM解码分布感知的训练后剪枝与稀疏SpMV。

一句话总结：SparseDecoding 用dense模型自身生成时的激活校准剪枝，并用bitmask稀疏内核把50%稀疏转成解码加速。

## 2. 研究背景与动机

固定自然文本校准近似teacher forcing，而长生成时状态由模型自己的输出决定；同时常见Sparse Tensor Core针对矩阵乘，batch1解码却以矩阵向量乘为主。算法分布与内核形状都可能失配。

## 3. 核心方法与创新点

1. 由目标任务prompt让dense模型生成，逐层收集decode位置激活，丢弃prefill；形成X_AR与H=2XXᵀ。
2. 仍用SparseGPT/OBS最小化||(W−Ŵ)X_AR||²，固定保留率；不是新增反向训练。写作和代码校准均计1M个decode token。
3. 50% N:M以32bit mask定位16个非零，用固定16步bit-scan遍历；每非零2bit索引，低于int32索引的32bit，面向小batch SpMV。

## 4. 实验设计与结果

四模型Llama3.1-8B、3.3-70B和Qwen3-14B/32B；A10080GB。Qwen3-32B在2:4下WritingBench C4 2.99→5.31，dense6.48；ClassEval Pass@1 9→24%，dense34%。表3 context512、50 warmup+50测量：32B 19.15→27.69 tok/s（2:4，1.45×）；70B最大1.48×是16:32配置，2:4只有1.39×，不能说全部稀疏模式相同峰值。

## 5. 局限性与未来展望

仍存在对dense明显精度差距，尤其较小模型。1M生成校准成本不低，校准与部署任务不同可能减弱收益。WritingBench使用自动judge；速度限特定GPU、context和小batch。非零权重50%对应理论2倍value压缩，还需索引及未剪枝层，不等于整模2倍。

## 6. 学术启发

部署时实际到达的状态分布应进入压缩目标；在相同token预算与剪枝器下比较自生成/跨模型/固定文本，才能拆分“任务数据”与“自回归状态”的贡献。

评分（1–10，高分更优；压缩评分只评价实际压缩对象）：

- 精度效果 7/10：比C4显著提升但未恢复dense
- 压缩倍率 6/10：50%稀疏带来1.34–1.48倍实速
- 创新性 8/10：解码激活校准与SpMV联合
- 可复现性 7/10：公式、预算和速度协议齐全
