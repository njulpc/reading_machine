# Paper: 2607.05711 — FourTune: Towards Fully 4-Bit Efficient Post-Training for Diffusion Models

Run: `python3 demo.py`

## 复现内容
- 三分支混合管线：FP4 冻结主干 + 可训练 LoRA（4-bit 前向/梯度）+ 冻结数值稳定分支（异常值通道保持高精度）；
- 块级 FP4 量化（含随机舍入的 G4 梯度路径）；
- 短训练循环验证 4-bit 下 LoRA 可学习；
- 以 Qwen3-0.6B 真实线性层验证"FP4 + 稳定分支"前向。

## 验证方式
- [1][2] 合成数据上对比 plain W4A4 vs 三分支输出 MSE，并运行 60 步 4-bit 训练循环；
- [4] 真实 Qwen/Qwen3-0.6B 第一个线性层 FP4 量化 + 异常值通道恢复，比较 logits 余弦相似度（无模型时跳过并注明）。
