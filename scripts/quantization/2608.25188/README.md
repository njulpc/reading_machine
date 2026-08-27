# Great Inversion（arXiv:2608.25188）Qwen3-0.6B 验证

脚本从真实 Qwen3-0.6B 首层捕获 prompt activation，执行逐 128 元素随机符号 Walsh–Hadamard 严格可逆变换，比较 uniform INT4、带任意实数 AbsMax scale 的理想 E2M1 FP4，以及 E2M1 + block-32 E8M0 scale 的 MXFP4。另把全部 196 个 Transformer Linear 量化为 INT4 或 MXFP4，执行整模前向和单 token 生成。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py --full-model-format mxfp4
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py --full-model-format int4
```

## 代码审查与验证（2026-08-28）

**算法一致性：部分一致。** 已对照官方 arXiv v1 PDF 的定义 2.8、定理 2.17、§4 与 §8。修复旧版把 E2M1 `{0,.5,1,1.5,2,3,4,6}` 和未定义的 `qmax=7.25` 拼成“MXFP4”的错误：论文明确 MXFP4 用 32 元素块、E8M0 幂次 scale，`s=2^(floor(log2 M)-2)`；理想 FP4 与 MXFP4 现已分开。测试也从单个权重 tile 改为真实 activation group，并保留负收益，不预设 Hadamard 必胜。

真实运行中，Hadamard round-trip 通过；当前 Qwen activation 的 SQNR gain 为 INT4 -0.409801 dB、理想 FP4 -0.056721 dB、MXFP4 -0.024574 dB，说明该样本上变换均轻微退化。整模 MXFP4：196 层/440,401,920 权重，logits MAE 0.41610953、cosine 0.98040766、生成“在”，退出码 0、墙钟 5.79 秒。整模 INT4：MAE 0.62787735、cosine 0.95425409、生成“这种”，退出码 0、墙钟 2.72 秒。

**真实 Qwen3-0.6B：已跑通（全模型 INT4 与 MXFP4 软件重构、前向和生成）。** 但这篇论文是理论综述；脚本未复跑 200 篇文献/43 方法、全模型 function-preserving folding、GPTQ、NVFP4、原生 Blackwell 指令或端到端 accuracy。真实 Qwen 的 raw-format 量化不能冒充论文各方法的完整复现。
