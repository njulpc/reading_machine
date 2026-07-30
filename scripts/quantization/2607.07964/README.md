# Paper: 2607.07964 — KronQ: LLM Quantization via Kronecker-Factored Hessian

Run: `python3 demo.py`

## 复现内容
- Kronecker 分解 Hessian（G⊗X）下的量化目标；
- 双向不相干处理：输入侧 + 输出侧随机旋转后量化再旋回；
- 梯度/激活 Hessian 迹驱动的层敏感度与混合精度分配；
- 以 Qwen3-0.6B 为目标模型的 4-bit 权重量化演示。

## 验证方式
- 真实 Qwen/Qwen3-0.6B 上量化前 2 个线性层并比较 logits 余弦相似度；无模型时用同维度 mock 验证代码路径；
- [1] 节在含重尾输出通道的合成权重上对比 2-bit 量化 MSE（KronQ 双向 vs 输入侧）。
