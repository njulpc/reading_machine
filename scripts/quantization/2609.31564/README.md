# 2609.31564 — Qwen3-0.6B小规模算法验证

论文：[官方全文](https://arxiv.org/html/2609.31564)。实现依据是论文公式/附录，未运行参考分支空壳脚本。

## 运行与环境

在本目录执行：

```sh
python3 demo.py --self-test --output tensor_results.json
python3 demo.py --output results.json
```

需要Python、PyTorch、transformers、huggingface_hub（WeightPE另需NumPy）。本机版本：Python3.9.6、torch2.8.0、transformers4.57.6、CPU4线程；WeightPE NumPy2.0.2。模型Qwen/Qwen3-0.6B，固定revision c1899de289a04d12100db370d81485cdf75e47ca，使用已存在的Hugging Face本地缓存，不自动下载权重。缺少缓存会明确失败。初次用模型名加载tokenizer触发元信息联网失败，最终代码用snapshot本地路径解决。

原始命令中output使用本目录的绝对路径；上面等价命令便于迁移。实际命令和环境由本次任务工具记录，结果数值完整保存在results.json，输入文本也内嵌其中。默认固定种子42。全模型做前向采集真实激活，后续仅局部权重参与算法验证。

## 算法与粒度

首层mlp.gate_proj、up_proj各前4行（`--rows`可改），全部1024输入维，共8192个真实权重。逐行对称INT8、row-major，一份跨两个矩阵的共享语法，但任何规则不能跨行。

实现Appendix A三段算法：按展开长度分桶；频率leader、最多8T候选、ρ=τ/√N去重；对不可变原码字计算增量L2；严格局部优先级极值形成不重叠集合；按成本在τ²内改写；所有重复pair批量merge；target64、无变化/两轮停滞停止，另有64轮上限并记录停止原因。T32、最小长度2、最少出现2。符号展开保存递归语义，解码必须保留原行宽。

35个校准token、14个测试token，真实激活重构MSE，11步AdamW lr1e−5/decay.1/clip1，step0和10刷新STE扰动，部署前再次刷新；并行训练相同优化器的INT8 QAT对照。没有500步warmup或6epoch训练。

显式移植假设：τ_frac=.15映射为τ=.15×原INT8码字L2范数；正文没有给出该比例换算的独立公式，故不能声称此约定经作者代码确认。周期之间固定STE扰动位移。CPU使用带固定随机种子的微小jitter打破merge优先级平局，可能不同于GPU次序。

## 结果和检查

局部批量语法符号比0.705202，测试相对L2 0.106052；QAT为0.005041。权重真实更新L2 .009611，耗时约1.94秒（含模型/激活采集，不是控制性能实验）。观察到符号数收益与明显失真，不能宣称成功保持任务精度。

论文12码字worked example的REWRITE结果与D=2精确匹配；无损merge解码、行边界、STE恒等梯度检查通过，每次改写断言全局预算。results.json包含每轮语法大小、规则数、失真与停止原因。

## 与原论文的差异及限制

局部Qwen层的输出重构代替ViT/CIFAR-10分类；未压缩attention或所有MLP，未运行A100/H100。训练和评价均用本实现的批量merge；原论文评价用串行贪心Re-Pair及LZ78/SEQUITUR，所以本次符号比不能与论文0.43倍直接对齐。未报告实际编码字节、熵编码、解压或推理速度；共享语法总符号数不是模型文件大小。没有把τ_frac转换、平局策略和周期STE约定假冒成作者原实现。

## 代码审查与验证（2026-09-29）

**算法一致性：部分一致。真实 Qwen3-0.6B：未跑通整模；真实局部权重demo已通过。** 小型随机Qwen3完整训练/量化/部署路径通过，不等于真实0.6B整模验证。

核对 [arXiv v1 原文](https://arxiv.org/html/2609.31564v1) §3、附录A算法1–3及附录B：

| 对照项 | 结论与证据边界 |
| --- | --- |
| REWRITE与MERGE、leader、全局失真预算 | 一致；按展开长度分桶、8T候选、ρ=τ/√N、严格局部极值、增量成本及行边界均对应附录；论文worked example和预算不变量通过 |
| 量化与共享语法 | 部分一致；逐行对称W8（−127…127）、FP32激活、无零点偏移/分组/异常值分流；新增不同宽度MLP行共享同一语法，attention仅W8，embedding/norm/head高精度 |
| STE与周期 | 部分一致；10步刷新、11步AdamW训练，固定周期内位移；预算比例映射仍是显式工程假设，保留64轮上限及停止原因 |
| 模型、校准及训练目标 | 部分一致；真实局部35校准/14测试token；随机小模型24校准token改用logits MSE。原文ViT/CIFAR-10、6epoch、warmup500与任务损失未复现 |
| 评价及导出 | 部分一致；本实现统计批量语法符号数，未实现论文评价用串行Re-Pair/LZ78/SEQUITUR。可选HF导出是反量化FP32，非压缩语法文件 |

修复：原码字曾与传入NumPy数组共享内存，外部修改会破坏“不可变原码字”基准，现逐行复制并设只读；支持ragged行以纳入gate/up/down不同宽度，避免填充虚假码字；校验行数、steps、leaders、tau与INT8码域；优化器说明改为实际步数。新增整模attention INT8、跨6个MLP矩阵共享语法的随机Qwen3回归，覆盖梯度、step0/10刷新、部署前重投影、模型权重替换、生成及保存/重载。

环境为macOS26.6.2 arm64、16 GiB、10核、CPU4线程，CUDA/MPS不可用；Python3.9.6、torch2.8.0、transformers4.57.6、numpy2.0.2。真实缓存模型/tokenizer的revision同上。

以下为实际执行命令（工作目录 `/private/tmp/reading_machine_arxiv_20260929`，解释器 `/Library/Developer/CommandLineTools/usr/bin/python3`；环境 `HF_HUB_OFFLINE=1`、`PYTHONPYCACHEPREFIX=/private/tmp/quant_review_20260929/pycache`）：

```sh
python3 -m py_compile scripts/quantization/2609.31564/demo.py
python3 scripts/quantization/2609.31564/demo.py --self-test --output /private/tmp/quant_review_20260929/2609.31564_tensor.json
python3 scripts/quantization/2609.31564/demo.py --output /private/tmp/quant_review_20260929/2609.31564_real_local.json
python3 scripts/quantization/2609.31564/demo.py --mock --export /private/tmp/quant_review_20260929/2609.31564_mock_export --output /private/tmp/quant_review_20260929/2609.31564_mock.json
python3 scripts/quantization/2609.31564/demo.py --full-model --output /private/tmp/quant_review_20260929/2609.31564_real_full.json
```

前四条退出0，真实整模最后一条明确退出1，未产生成功JSON。原因：264,241,152个MLP码字在当前Python实现中保守估计至少39.38 GiB，仅语法对象已超过16 GiB物理内存及默认8 GiB工作预算；8192码字实测构造Grammar及occurrences的tracemalloc峰值2,238,621字节（273.27字节/码字，尚不含训练）。添加预分配资源检查，并尝试ragged共享表示；不能以拆成逐层独立语法降低内存后声称等价原方法，因此采用完整随机模型回归。需要紧凑/GPU语法实现或更大内存机器才可继续真实整模。

真实局部运行墙钟3.48秒，8,192权重的语法符号比0.705202、测试相对L2 0.106052（QAT0.005041），更新L2 0.009611。小型随机Qwen3（2层hidden16/intermediate32/vocab128）的14个Linear/4,608权重通过11步训练、生成及导出/重载，墙钟1.89秒，logits相对L2 0.007633、重载误差0；梯度均有限且非零。论文worked example、不可变原码字、15组ragged失真/解码、STE梯度、导入和语法检查通过，非法参数退出2。详细命令、版本与结果见 `results.json` 的 `review`。

未完成：真实0.6B整模、原论文ViT/CIFAR训练和评估、真实压缩语法文件与原生kernel。局部demo成功和随机模型成功均不能替代这些结论；没有性能或任务精度保持声明。
