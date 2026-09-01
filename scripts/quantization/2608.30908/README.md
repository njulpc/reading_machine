# 2608.30908 — GradCodes 量化码空间微调

## 实现范围

固定 4-bit scale，在整数 code 上用 surrogate gradient 与投影搜索逼近目标更新。

## 运行

```bash
python3 scripts/quantization/2608.30908/demo.py
```

环境：macOS CPU、PyTorch、safetensors；模型为本地 Hugging Face `Qwen/Qwen3-0.6B` checkpoint。脚本固定随机种子，直接读取真实 `model.safetensors`，不下载权重。

## 证据边界

小切片和合成目标更新只验证 code-space 优化，不代表论文完整微调基准。

## 本次验证结果

实际执行命令：`python3 scripts/quantization/2608.30908/demo.py`

```json
{
  "paper_id": "2608.30908",
  "model": "Qwen3-0.6B",
  "checkpoint": "/Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/model.safetensors",
  "algorithm": "4-bit code-surrogate gradient with guided integer projection",
  "steps": 12,
  "initial_target_mse": 0.0012729353038594127,
  "final_target_mse": 4.052614895044826e-05,
  "changed_code_fraction": 0.90228271484375
}
```

## 代码审查与验证（2026-09-02）

本节覆盖上方初始自报结果。对照官方 PDF Definition 1、Algorithm 1、Eq.（3）–（5）和 Appendix A/B，结论为**部分一致**。

- 原实现没有真实 task gradient、scale update、candidate sampling 或 realized-loss selection，只在 synthetic target 上逐 code 朝目标移动。
- 修复：全部 196 个 Transformer Linear 进入 deployable symmetric W4 状态；在首个完整 q_proj 上用真实 next-token cross-entropy 求 weight/code surrogate gradient，执行 projected scale update、4-candidate guided sampling、完整模型 loss evaluate/select，共 2 次迭代。
- 实际命令：`python3 scripts/quantization/2608.30908/demo.py --steps 2 --output-json /private/tmp/arxiv_quant_review_20260902/2608.30908.json`；loss `5.445165 -> 5.135525`，code change `0.20504%`，整模 logits MSE `1.456633`，生成 `这`，退出码 0，3.48 秒。
- **真实 Qwen3-0.6B：已跑通**全模型 W4 + 单矩阵 code-search 路径；未跑通全部矩阵/LoRA parameterization、GSM8K/Alpaca/MASSIVE 训练、三 seed 或 NF4/MXFP4 实验。
- 环境同批次公共环境；JSON 导出已验证。
