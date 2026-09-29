# 2609.31560 — Qwen3-0.6B小规模算法验证

论文：[官方全文](https://arxiv.org/html/2609.31560)。实现依据是论文公式/附录，未运行参考分支空壳脚本。

## 运行与环境

在本目录执行：

```sh
python3 demo.py --self-test --output tensor_results.json
python3 demo.py --output results.json
```

需要Python、PyTorch、transformers、huggingface_hub（WeightPE另需NumPy）。本机版本：Python3.9.6、torch2.8.0、transformers4.57.6、CPU4线程；WeightPE NumPy2.0.2。模型Qwen/Qwen3-0.6B，固定revision c1899de289a04d12100db370d81485cdf75e47ca，使用已存在的Hugging Face本地缓存，不自动下载权重。缺少缓存会明确失败。初次用模型名加载tokenizer触发元信息联网失败，最终代码用snapshot本地路径解决。

原始命令中output使用本目录的绝对路径；上面等价命令便于迁移。实际命令和环境由本次任务工具记录，结果数值完整保存在results.json，输入文本也内嵌其中。默认固定种子42。默认模式全模型做前向采集真实激活，后续仅局部权重参与算法验证；新增整模入口见下方审查章节。

## 算法与粒度

首层mlp.gate_proj前32个输出通道（`--rows`可改），保留全部1024输入维。每行步长max(abs(W))/7，不跨通道共享；校准54个token，另21个token测试，m=16/54。对H=XᵀX+λI求逆Cholesky，按原顺序逐列舍入并将误差补偿到未量化列，等价于论文增广矩阵尾部最小二乘。无act-order重排，无分组近似。

对照λ=.01||X||F²/N与论文式35 β=1。无限格点确定性最近邻与随机舍入对应理论；有限对称W4（15个码字−7…7，存储可用4bit）裁剪是额外工程实验，不属于论文无裁剪定理。结果记录补偿后溢出次数。未实现原论文全部7个λ配置与30次合成数据重复。

## 结果

m54确定性测试相对L2：旧0.0910469、新0.0918231；随机旧0.123657、新0.116477。m16确定性新规则也未优于旧规则。真实权重子集32768个参数，而非596M参数完整量化。运行约5.10秒，含模型加载/前向和量化，不是性能benchmark。

独立逐尾部线性求解对照误差0；增广目标恒等式误差0；50,000次随机舍入均值误差0.00436；有限范围检查通过。

## 限制

以上默认模式只评估局部输出误差；下方新增整模logits/生成/FP32导出验证。仍无困惑度、INT4打包checkpoint、原生kernel或速度收益。δ选择和真实Qwen激活是本次移植，原论文实验是64维合成分布。不得把局部随机误差改善外推为端到端精度改善。

## 代码审查与验证（2026-09-29）

**算法一致性：部分一致。真实 Qwen3-0.6B：已跑通全部 decoder Linear 的有限 W4 数值参考路径。** 这是 CPU 反量化后的 FP32 推理及 checkpoint，不能称为原生 INT4 部署，也不能证明任务精度保持。

以 [arXiv v1 原文](https://arxiv.org/html/2609.31560v1) §2.1、式12–15、35和§4.2为依据，逐项结论：

| 对照项 | 结论与证据边界 |
| --- | --- |
| 逐坐标舍入、正则增广、尾部最小二乘 | 一致；逆 Hessian 的上三角 Cholesky 实现，通过独立尾部线性求解对照 |
| 正则 λ 与随机舍入 | 一致；式35 β=1，保留旧规则及无偏随机舍入对照；β=1不保证最优 |
| 格点、位宽与粒度 | 部分一致；理论无限格点保留；新增整模选择逐输出行 max-abs/7、−7…7 有限 W4，是裁剪工程扩展；激活FP32、零点0、整行group size，无act-order/异常值分流/混合精度搜索 |
| 校准与实验 | 部分一致；6段固定文本54 token、局部另3段21 token；原文64维合成分布、7种λ和30次重复尚未复现 |
| 整模目标与输出 | 工程迁移；28层196个Linear，440,401,920个权重；embedding、norm及绑定lm_head保留FP32。保存JSON及可选反量化HF模型，非打包W4 |

修复/补齐：原实现只有层切片，未替换模型权重；增加整模收集校准激活、逐模块量化替换、独立文本前向、确定性两token生成、保存与重载。每128列将远端尾部补偿合为矩阵乘法，数学上保持原更新；block size 1/4/16/128、确定性/随机、有界/无限格点的小张量结果差异均为0。拒绝无效行数、非有限输入和非法λ；全零激活的整模λ使用1e−12工程下限。校准取量化前模型激活，不作逐层重新校准。

实际环境：macOS 26.6.2 arm64，16 GiB、10核，CPU4线程，CUDA/MPS均不可用；Python3.9.6、torch2.8.0、transformers4.57.6、numpy2.0.2。复用上述固定revision的真实模型和tokenizer，非mock。其余依赖版本与逐模块λ/输出见 `results.json` 的 `review`。

以下为实际执行命令（工作目录 `/private/tmp/reading_machine_arxiv_20260929`，解释器 `/Library/Developer/CommandLineTools/usr/bin/python3`；环境 `HF_HUB_OFFLINE=1`、`PYTHONPYCACHEPREFIX=/private/tmp/quant_review_20260929/pycache`）：

```sh
python3 -m py_compile scripts/quantization/2609.31560/demo.py
python3 scripts/quantization/2609.31560/demo.py --self-test --output /private/tmp/quant_review_20260929/2609.31560_tensor.json
python3 scripts/quantization/2609.31560/demo.py --output /private/tmp/quant_review_20260929/2609.31560_real_local.json
python3 scripts/quantization/2609.31560/demo.py --mock --export /private/tmp/quant_review_20260929/2609.31560_mock_export --output /private/tmp/quant_review_20260929/2609.31560_mock.json
python3 scripts/quantization/2609.31560/demo.py --full-model --export /private/tmp/quant_review_20260929/2609.31560_real_export --output /private/tmp/quant_review_20260929/2609.31560_real_full.json
```

全部退出0。语法初次因系统pycache目录权限失败，重定向到临时目录后通过；导入、自测、非法参数退出2、`git diff --check`通过。真实局部运行墙钟8.54秒，局部误差与原记录一致。真实整模墙钟77.62秒（函数内76.92秒），196模块均使用54校准token；logits全部有限，与原模型相对L2为0.476894，生成token `[576,3729]`（` The night`）；FP32保存/重载最大logits差为0。明显的logits变化不应被描述为无损。

小型随机Qwen3为2层、hidden16、intermediate32、vocab128，24校准token；14个Linear/4,608权重全路径通过，墙钟1.72秒、重载误差0，仅作结构回归。模型导出位于临时目录，未纳入Git；没有原论文合成实验全集、长文本困惑度、原生INT4内核或速度/压缩率结论。
