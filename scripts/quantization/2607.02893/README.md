# Paper: 2607.02893 — Variable Bit-width Quantization: Learning Per-Group Precision

Run: `python3 demo.py`

## 复现内容
- 可微分的逐组比特宽度学习（候选比特 softmax + 预算正则 + 直通估计）；
- 等平均比特下 variable vs uniform 的重建误差对比；
- 以 Qwen3-0.6B 真实层做逐组 2/4-bit 量化演示。

## 验证方式
- [1][2] 合成权重上运行 200 步比特学习并对比均匀量化（核心机理：高能量组自动分配更多比特）；
- [3] 真实 Qwen/Qwen3-0.6B 第一个线性层按组能量分配 2/4-bit 并比较 logits 余弦相似度（无模型时跳过并注明）。
