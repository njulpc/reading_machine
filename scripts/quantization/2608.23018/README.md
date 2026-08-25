# 2608.23018 复现：SplitLite temporal residual compression

本目录复现论文 [SplitLite: Low-Rank Residual Compression for Split Learning](https://arxiv.org/abs/2608.23018) 的 Algorithm 2，并用真实 Qwen3-0.6B 验证切分层激活/梯度缓存路径。

## 算法与数据流

1. 首次出现的样本完整发送切分层张量，并在发送端/接收端建立相同缓存。
2. 后续计算当前张量相对最近重构缓存的 temporal residual。
3. 激活 residual 截断到 rank-2r，梯度 residual 截断到 rank-4r；奇异值吸收到左因子。
4. 两个因子独立使用无偏随机均匀量化：激活 4-bit、梯度 8-bit。
5. 接收端重构 residual 并与发送端同步更新缓存。

## 运行

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --full-model \
  --save-packet /private/tmp/arxiv_quant_review_20260826/2608.23018-packet.pt
```

依赖：Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6。验证机器为 Apple arm64 CPU，CUDA/MPS 均不可用。

## 代码审查与验证（2026-08-26）

**算法一致性：部分一致。** 初始 demo 压缩的是两个合成 LoRA **权重更新**之差，只做 rank-2r 和确定性对称 INT8，也没有样本缓存、激活、梯度或双向通信；这与论文 Algorithm 2 的对象和流程不一致。现改为激活 rank-2r/Q4、梯度 rank-4r/Q8、首轮完整发送、相邻状态 residual、因子量化和同步缓存。论文只规定量化器须无偏且方差有界，当前随机均匀实现是满足该假设的工程实现。

验证结果：

- 64x256、LoRA rank 4 的确定性算子路径退出码 0；激活 Q4 和梯度 Q8 reconstruction relative L2 为 0.24615535/0.01846021，稳态双向通信估算从 1,048,576 bit 降到 51,328 bit（20.429x）。
- 真实 Qwen 加载 596,049,920 参数，在 layer 3 切分，同一 9-token 样本使用相邻低秩 adapter 状态；取得真实 loss 梯度，执行激活 rank 8/Q4 和梯度 rank 9（受序列长度限制）/Q8，再把重构激活注入完整服务端后半模型。
- baseline/current loss 为 8.62512970/8.62835884；激活/梯度 reconstruction relative L2 为 0.00001821/0.00129022；重构前向 logits MAE 0.00245636、last-token cosine 1.0，生成成功。packet 保存/重载成功；最终复测脚本内部耗时 0.926 秒，命令墙钟 2.64 秒。

**真实 Qwen3-0.6B：已跑通（单客户端、单样本、两个相邻 adapter 状态的端到端核心通信路径）。** 未跑论文 6 客户端、10 epoch、GLUE、LoRA rank 16、128-token 序列、Jetson/RTX4090/gRPC、随机化 SVD、缓存离线存储、联邦聚合或论文通信/准确率，因此不能宣称复现 93.5%/83.7% 的完整实验结果。
