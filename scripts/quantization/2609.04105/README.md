# 2609.04105 — Qwen3-0.6B 数值验证

论文：[Hardware-Aware FP4 FlashAttention-4](https://arxiv.org/abs/2609.04105)。

Direct-P 直接从分数产生 FP4 概率码，并用相同表示计算归一化分母。

## 实现范围

NVFP4 Q/K 与 MXFP4 P/V；N32 概率块使用 E8M0 幅度，E2M1 仿射映射 A=1.50、B=1.20，Wan 为1.60/0.95；按表示后概率累加分母；极端 logits 使用采样锚与指数下溢保护。

本目录是基于真实Qwen3-0.6B权重的组件实现及小规模验证，**不是完整论文复现**。明确缺项：

Real first-layer projections used as noncausal operator inputs before RoPE/QK normalization. V uses block-32 power-of-two MX reconstruction. No folded K64 scales, sampled guard, TMEM packing, backward or full-model substitution. Thus not a complete FP4 attention reproduction and no speedup claimed.

所有低比特张量均以FP32反量化值计算，未输出压缩检查点；因此不声称显存、吞吐或部署速度收益。误差指标与论文任务指标不同，单条文本的logit误差不能代替困惑度或准确率。

## 环境与运行

实测：Python 3.9.6，PyTorch 2.8.0，Transformers 4.57.6，macOS arm64 CPU（CUDA不可用）；随机种子42、CPU线程4。本次使用缓存的官方Qwen3-0.6B快照`c1899de289a04d12100db370d81485cdf75e47ca`。

通用依赖为`torch`、`transformers`及其分词器依赖。通过`snapshot_download(local_files_only=True)`先解析本地缓存路径，再加载分词器/权重，避免Transformers按模型名称触发额外网络元数据查询。先准备模型缓存；也可设置`QWEN_MODEL_PATH`指向本地模型目录。

从仓库根目录执行（本次同命令已执行，结果保存路径随后归档到本目录）：

```sh
python3 scripts/quantization/2609.04105/demo.py --output-json /tmp/2609.04105.json
```

可选指定检查点：

```sh
export QWEN_MODEL_PATH=/path/to/Qwen3-0.6B
```

校准文本与独立测试文本在`../numerics.py`明示。涉及全模型前向的验证使用不同的校准/测试文本；算子与码本测试仅检验组件误差，不做泛化声称。

## 实测结果与配置

```json
{
  "model": "Qwen3-0.6B",
  "operator_shape": [
    1,
    16,
    28,
    28
  ],
  "output_error": {
    "mse": 3.2577292586211115e-05,
    "relative_l2": 0.12416517734527588,
    "cosine": 0.9922662973403931
  },
  "row_sum_max_error": 2.384185791015625e-07,
  "A": 1.5,
  "B": 1.2,
  "P_block": 32,
  "full_paper_reproduced": false,
  "boundary": "Real first-layer projections used as noncausal operator inputs before RoPE/QK normalization. V uses block-32 power-of-two MX reconstruction. No folded K64 scales, sampled guard, TMEM packing, backward or full-model substitution. Thus not a complete FP4 attention reproduction and no speedup claimed.",
  "python": "3.9.6",
  "torch": "2.8.0",
  "transformers": "4.57.6",
  "platform": "macOS-26.6.2-arm64-arm-64bit",
  "cuda": false,
  "status": "executed"
}
```

完整机器可读结果见[results.json](results.json)，实际实现见[demo.py](demo.py)。

## 代码审查与验证（2026-09-05）

- 一致性结论：**部分一致**。官方 v1 的 NVFP4 Q/K、MXFP4 P/V、N32 E8M0 amplitude、E2M1 affine map（A=1.50、B=1.20）及“用实际 P 码累加分母”均在算子路径体现；输出使用相同表示的分子和分母，row-sum 误差为 2.38e-7。
- 差异边界：当前输入来自真实 Qwen 第一层 projection，但在 RoPE 和 QK normalization 前构造非因果算子；没有论文的相邻 K64 scale MSE folding、128-row sampled guard、`M+L≤126` 下溢修复、TMEM packing、反向或整模替换。未以简化算子冒充 FlashAttention-4 kernel。
- 实测命令：`python3 scripts/quantization/2609.04105/demo.py --output-json /private/tmp/2609.04105.review.json`；退出码 0，墙钟 2.19 秒；形状 1×16×28×28，输出 cosine 0.992266。
- 真实 Qwen3-0.6B：**完整量化未跑通**。真实 Q/K/V 张量上的 Direct-P CPU 参考算子已跑通；没有整模 attention 替换、生成、GB200/B300 内核、吞吐或训练验证。
