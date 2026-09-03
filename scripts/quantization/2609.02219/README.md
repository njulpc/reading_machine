# 2609.02219 — AVIS 激活方差校准

## 方法与实现范围

论文在 YOLO/Vitis-AI 流程中按 `s_i = mean_l mean_c Var_H,W(A_l,c(x_i))` 给候选图像打分，过滤非正分并确定性取 Top-K；随后做 INT8 PTQ、bias correction、XMODEL 编译和 CPU-DPU 部署，还包含辐射关键度分析。

Qwen 没有二维空间特征。本 demo 明确以 token 维替代 `H,W`，在全部 28 个 Transformer block 上打分；对 Top-4 与固定随机 4 样本分别校准全部 196 个 Linear 的逐张量非对称 A8 范围，权重采用逐输出通道对称 W8，并用校准均值做解析权重 bias correction。

## 运行

```bash
python3 scripts/quantization/2609.02219/demo.py --self-test
python3 scripts/quantization/2609.02219/demo.py --output-json /tmp/2609.02219.json
```

## 代码审查与验证（2026-09-04）

- **算法一致性：部分一致。** 分层/分通道方差聚合、正分过滤、确定性 Top-K、INT8 与 bias correction 结构一致；token 代理不等于空间方差，也未覆盖 YOLO、月球图像、Vitis-AI、XMODEL、DPU 或关键度缓解。
- **修复：** 原实现只用首层张量整体方差，且随机/AVIS 因共享最大值产生完全相同结果；现改为 28 层公式级打分、两套真实校准统计、196 层 W8A8、bias correction、独立评估文本、整模前向/生成。修复 BF16 `eps` 量化步长 bug。
- **结果：** 退出码 0，3.74 s；AVIS 选择 `[7,6,2,4]`。独立评估上 random/AVIS logits MSE 为 `23.9147/27.8985`，cosine 为 `0.443063/0.490962`；两者指标排序不一致，AVIS 没有可声称的稳定优势，负结果保留。
- **真实 Qwen3-0.6B：已跑通（W8A8 校准迁移）。** 论文视觉/DPU 方法未跑通；fake quant 未导出 XMODEL 或压缩权重。

环境：macOS 26.6.2 arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；本地完整 Qwen3-0.6B checkpoint。
