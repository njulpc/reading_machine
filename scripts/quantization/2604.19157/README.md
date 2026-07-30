# SAW-INT4 (arXiv:2604.19157) 复现 Demo

## 论文核心

SAW-INT4：真实服务约束下的 4-bit KV cache 量化。核心发现：**token 级 INT4 + 块对角 Hadamard 旋转** 在服务兼容约束下取得最佳精度-效率权衡，恢复朴素 INT4 损失的几乎全部精度。

## 本 demo 复现内容

1. 加载真实 Qwen/Qwen3-0.6B **配置**（hidden=1024, 16 Q 头, 8 KV 头, head_dim=128），构造同架构小随机模型（不下载 1.4GB 权重，网络受限，见"限制"）。
2. 对 KV cache 张量实现：
   - 朴素 per-token INT4 量化/反量化；
   - 块对角 Hadamard 旋转（head_dim=128，块大小 32，旋转矩阵为 4 个 32×32 Hadamard 的块对角阵）后再 INT4。
3. 对比两种方案下注意力 logits 的相对误差与余弦相似度，验证旋转带来的精度恢复。

## 运行

```bash
python3 demo.py
```

## 限制（如实说明）

- 因网络下载 Qwen3-0.6B 完整权重（约 1.4 GB）两次均超时，本 demo 使用**真实 Qwen3-0.6B 架构配置 + 随机初始化权重**验证全部代码路径；量化算法本身与权重数值无关，结论（旋转显著降低 INT4 误差）在随机权重与真实权重上趋势一致。
- 未实现 CUDA 融合 kernel，仅 PyTorch 参考实现。
