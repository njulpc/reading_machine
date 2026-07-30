# Paper: 2607.26515 — HiFloat4 Format for End-To-End FP4 RL Post-Training

Run: `python3 demo.py`

## 复现内容
- HiF4 三级层次化缩放（张量级→块级→异常值子块级）FP4 量化器；
- Rollout-ResQ：硬件友好稀疏模式的残差修正，恢复异常值下溢丢失的精度；
- 以 Qwen3-0.6B 为目标模型的 rollout（前向）量化演示。

## 验证方式
- 真实 Qwen/Qwen3-0.6B（本地缓存）上量化前 2 个线性层并比较 logits 余弦相似度；无模型时以 Qwen3-0.6B 维度 mock 模型验证全部代码路径；
- [1][2] 节在含异常值的合成权重上对比 HiF4 vs 普通块量化、FP4 vs FP4+ResQ 的 MSE。
