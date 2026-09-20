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

实际执行第二条。4条×8 token实际采样，额外含10token prefill比较；197层线性模块合计6501次量化调用，每条rollout 28层×8次=224次KV写入。prefill logits相对L2为0.227216、argmax一致率0.80。SGD梯度范数2.703324，最后一层down_proj权重实际更新L2=0.00422262；采样/训练及同步阶段约13.14秒，不包含初始加载。一次计时不作性能结论。

奖励是**输出字符中数字的比例**，仅用于验证带正负group-centered advantage的真实梯度路径，绝不是Countdown得分：4条奖励0.153846、0.142857、0.333333、0.142857。输出未证明算术正确，更未证明长期稳定性提高。完整原始结果在 `results.json`。

小张量验证包括：INT8类型/零值/半量化步长误差界；SC/TIS/MIS/精确IS的top-k简式与重建完整q分布的梯度一致（最大误差6.60e-17）；on-policy校正=0；恒定reward精确中心化后的期望梯度最大6.60e-17，未校正漂移范数0.541095。注意：top-k近似只对重建的q消除漂移，不保证对真实截断尾部分布精确抵消。

## 真实限制

没有NVIDIA GPU，未运行论文Countdown 64×8 batch、1200step sweep、30B INTELLECT-2或多种子长期崩溃对照；未复现原生INT8/BF16累加、FP8/KV4设置。没有从toy reward推断论文训练准确率，也不把INT8权重buffer容量误算成整机内存压缩。本目录为可运行算法移植和真实0.6B小规模验证，`full_paper_reproduction=false`。
