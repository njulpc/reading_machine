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
