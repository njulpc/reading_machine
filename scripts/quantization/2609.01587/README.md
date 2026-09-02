# 2609.01587 — 量化损伤预算分配

## 实现范围

在真实 Qwen 全部 28 层上比较 per-row RTN4、逐层升 W8 的因果干预与全局 group-128 RTN4。

## 运行

```bash
python3 scripts/quantization/2609.01587/demo.py
```

环境：macOS CPU、Python 3.9.6、PyTorch 2.8.0、safetensors；直接读取本地 `Qwen/Qwen3-0.6B` checkpoint，不下载权重。

## 本次真实验证结果

语法、导入与真实 Qwen 张量运行均 PASS。实际命令：

```bash
python3 scripts/quantization/2609.01587/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.01587.json
```

```json
{
  "paper_id": "2609.01587",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "matched-near-budget causal local W8 repair versus globally finer group-W4 allocation",
  "environment": {
    "python": "3.9.6",
    "torch": "2.8.0",
    "hardware": "macOS-26.6.2-arm64-arm-64bit",
    "cuda": false
  },
  "elapsed_seconds": 0.04238274999999997,
  "layers": 8,
  "worst_layer": 6,
  "local_estimated_bits": 10092544,
  "global_estimated_bits": 11010048,
  "global_to_local_budget_ratio": 1.0909090909090908,
  "summed_mse": {
    "local_repair": 6.501083391086127e-05,
    "global_granularity": 4.8273417860400514e-05
  },
  "global_better": true
}
```

## 证据边界

全局方案预算比局部方案高 9.09%，因此仅是近预算机制验证，不能替代论文九模型因果干预。

## 代码审查与验证（2026-09-03，取代上述八层切片结果）

**算法一致性：部分一致。** 论文以全模型 per-row RTN4 为 floor、RTN8 为近无损 ceiling，对每个 Transformer 层做一次“其余层保持 4-bit、该层升 8-bit”的因果干预；预算分析把 +0.146 effective bpw 分配为全局 group-128 RTN4（4.156 bpw）或局部约 3.65% 层升 8-bit。初始实现只比较 8 个 q_proj 切片的权重 MSE，且预算高 9.09%，没有因果前向。

本次对真实 Qwen3-0.6B 全部 196 个 Linear/440,401,920 权重建立 row-RTN4 floor 和 row-RTN8 ceiling，实际遍历 28 层逐层恢复并每次做完整前向；单 prompt logits-MSE 代理下最可恢复层为 27，top-1 恢复 27.15%，全局 group-128 恢复 35.62%，全局优于局部。row4/row8/local/global logits MSE 为 1.357425/0.010912/0.991841/0.877805，两种最终模型均生成成功。

```bash
python3 scripts/quantization/2609.01587/demo.py --self-test
python3 scripts/quantization/2609.01587/demo.py --output-json /private/tmp/arxiv_repro_results_20260903/2609.01587.json
```

环境为 macOS 26.6.2 arm64 CPU（CUDA/MPS 均不可用）、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0，墙钟 7.71 秒。**真实 Qwen3-0.6B：已跑通（28 层整模因果 smoke）。** 代理指标不是论文 22 任务、每任务 200 样本的 CORE；GPTQ/AWQ、3 个 calibration seeds 与九模型统计未跑通。
