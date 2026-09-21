# Score Centering：Qwen3-0.6B 真实数值复现

论文：[2609.20807](https://arxiv.org/abs/2609.20807)，[官方全文附录A/B](https://arxiv.org/html/2609.20807v1)。对照作者[量化实现](https://github.com/martin-marek/score-centering/blob/7c56e9ee2972aa57f446cf564de1a1658d14b321/models/quant.py)和[0.6B实验配置](https://github.com/martin-marek/score-centering/blob/7c56e9ee2972aa57f446cf564de1a1658d14b321/sweeps/06b_quant_stale.yaml)。作者代码在本次只读克隆的SHA为 `7c56e9ee2972aa57f446cf564de1a1658d14b321`。

## 实现范围

- 197个线性模块及词嵌入使用逐输出行/通道 absmax/127、round-to-nearest 对称 INT8 权重。权重以真实int8 buffer保存，含FP32尺度，范数参数不量化。为共享同一模型做训练对照，原FP32权重也保留，因此本进程没有实现压缩后峰值内存收益。
- 线性输入按token在收缩维上动态absmax量化为A8，无离线校准数据集、无GPTQ/Hessian优化；o_proj展平head维后按完整输入收缩维处理。
- KV经Q/K norm和RoPE后、进入cache前按token/head做INT8量化，scale=max(absmax/127,1e-9)，后续解码读取已含量化误差的历史缓存。缓存存的是反量化FP32值，不是打包INT8缓存。
- 实现论文Eq.8/14的top-k Score Centering，rho尾部分布重建、全部系数stop-gradient；支持SC、TIS+SC（上限2）、MIS+SC（0.5–5），默认k=128。
- 真实量化采样4条、每条8 token，保存top-k及实际采样token logprob；恢复训练路径，对全部596,049,920参数反传并执行一次SGD（lr=.01），再同步重新量化权重。
- CPU GEMM使用INT8量化后反量化到FP32的数值参考，不是论文JAX原生低精度硬件内核；训练器FP32而论文bf16。Qwen原始注意力/因果mask/GQA/RoPE保持由Transformers实现。

## 运行与验证

本机Python3.9、torch2.8.0、transformers4.57.6、macOS26.6.2 arm64、CPU4线程，seed17。模型缓存revision `c1899de289a04d12100db370d81485cdf75e47ca`，脚本强制`local_files_only=True`。在本目录执行：

```sh
python3 demo.py --self-test-only --output tensor_results.json
python3 demo.py --model /Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca --output results.json
```

实际执行第二条。4条×8 token实际采样，额外含10token prefill比较；197层线性模块合计6698次量化调用（含更新后复查），每条rollout 28层×8次=224次KV写入。prefill logits相对L2为0.227216、argmax一致率0.80。SGD梯度范数2.764644，最后一层down_proj权重实际更新L2=0.00506849；采样/训练及同步阶段约12.16秒，不包含初始加载。一次计时不作性能结论。

奖励是**输出字符中数字的比例**，仅用于验证带正负group-centered advantage的真实梯度路径，绝不是Countdown得分：4条奖励0、0、0.117647、0.142857。输出未证明算术正确，更未证明长期稳定性提高。完整原始结果在 `results.json`。

小张量验证包括：INT8类型/零值/半量化步长误差界；SC/TIS/MIS/精确IS的top-k简式与重建完整q分布的梯度一致（最大误差6.60e-17）；on-policy校正=0；恒定reward精确中心化后的期望梯度最大6.60e-17，未校正漂移范数0.541095。注意：top-k近似只对重建的q消除漂移，不保证对真实截断尾部分布精确抵消。

## 真实限制

没有NVIDIA GPU，未运行论文Countdown 64×8 batch、1200step sweep、30B INTELLECT-2或多种子长期崩溃对照；未复现原生INT8/BF16累加、FP8/KV4设置。没有从toy reward推断论文训练准确率，也不把INT8权重buffer容量误算成整机内存压缩。本目录为可运行算法移植和真实0.6B小规模验证，`full_paper_reproduction=false`。


## 代码审查与验证（2026-09-21）

**算法一致性：部分一致。真实 Qwen3-0.6B：已跑通（CPU 数值参考路径，非完整论文实验）。**

完整检查本目录 README、demo.py、两份 JSON，以及 `papers/2026-09/quantization/2609.20807/tech_analysis.md`；核对上文官方 HTML 的 §4、附录 A/B，以及固定 SHA 的作者 quant.py 和 0.6B sweep 配置。目录没有其他附属脚本。

| 核查项 | 结论与证据边界 |
| --- | --- |
| SC Eq.8/14 | 一致：保存 top-128 与实际采样 token logprob，rho 重建尾部，采样权重及校正系数均 stop-gradient。TIS 上限2，MIS闭区间[0.5,5]；修正后 eps=1e-6 与附录A.3示例一致。 |
| 权重/激活 | 数值网格一致：197个Linear和Embedding，W8逐输出行、A8逐token，对称absmax/127、round；没有zero-point、固定group size、异常值分支或混合位宽策略。o_proj收缩完整展平head维。 |
| KV | 逐token/head KV8，RoPE后在cache.update入口定标，scale下限1e-9；历史缓存保存反量化值。与作者INT8网格一致，但不是打包INT8缓存。 |
| 校准/优化 | 无静态校准集（样本数不适用），激活和KV运行时动态定标；一次全参数SGD lr=.01后重新量化。SC统计来自本次4×8 token采样，非离线校准。 |
| 计算与训练设置 | 部分一致：CPU FP32反量化GEMM、FP32训练器；论文使用JAX低精度计算、BF16训练器及Countdown。这里只用数字字符比例奖励和单步更新。 |
| 全论文范围 | 未完成64×8、512长度、1200步训练、staleness=64、多种子与30B/FP8/KV4基准；本机CPU无CUDA，当前脚本也没有这些完整训练/内核实现。不得据此推断论文准确率、加速或内存收益。 |

本次修复：

1. MIS原先用`r * mask`，FP32概率比溢出时`inf * 0`产生NaN；复现后改用`where`，增加极端logprob下的损失和梯度有限性回归。
2. head概率比改为`exp(logp-logq)`，避免对q设下限改变权重；尾部概率下限从1e-9对齐论文示例1e-6。
3. 自测原先重置全局随机种子为17并消耗采样状态，使`--seed`失效；隔离自测RNG，验证运行前后状态完全相同。本次采样文本因此与旧记录不同。
4. 拒绝非正threads/rollouts/new-tokens/topk及超过词表的topk；重新量化后启用全部198个模块做真实前向，确认logits有限。

验证环境：Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、macOS 26.6.2 arm64，CPU四线程，CUDA/MPS不可用。复用上文完整Hugging Face缓存，不下载模型、不使用mock。

以下命令均从仓库根目录执行：

```sh
PYTHONPYCACHEPREFIX=/private/tmp/quant-review-20260921-pycache python3 -m py_compile scripts/quantization/2609.20807/demo.py
python3 scripts/quantization/2609.20807/demo.py --self-test-only --output scripts/quantization/2609.20807/tensor_results.json
python3 scripts/quantization/2609.20807/demo.py --model /Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca --mode sc --output scripts/quantization/2609.20807/results.json
python3 scripts/quantization/2609.20807/demo.py --model /Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca --mode tis --output /private/tmp/quant-review-20260921-tis.json
python3 scripts/quantization/2609.20807/demo.py --model /Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca --mode mis --output /private/tmp/quant-review-20260921-mis.json
```

初次py_compile因默认缓存目录写权限退出1；改为上述临时缓存路径后通过。语法、实际导入、INT8/逐头KV误差界、SC/TIS/MIS/IS梯度等价、on-policy零校正、MIS溢出和种子保持检查均通过；梯度等价最大误差6.60e-17。模型/Tokenizer加载、动态统计、整模量化替换、自回归采样、596,049,920参数反传、SGD、重新量化和更新后前向均纳入验证。脚本支持JSON结果保存，已读回验证；不支持模型权重导出，未声称已验证模型保存/重载。

| 真实模型模式 | 退出码 | 采样至更新后前向耗时（秒） | 梯度范数 | 最后down_proj更新L2 | 更新后有限logits |
| --- | --- | --- | --- | --- | --- |
| sc | 0 | 12.162 | 2.764644 | 0.00506849 | 通过 |
| tis | 0 | 9.466 | 2.894093 | 0.00526819 | 通过 |
| mis | 0 | 9.067 | 2.920637 | 0.00522844 | 通过 |

三模式均为4条×8 token，每条224次KV写入，共6698次量化Linear调用；计时不含模型加载及首次定标，不作性能比较。SC原始结果与小张量结果更新在既有JSON文件中；TIS/MIS关键指标汇总在此，临时日志不提交。
