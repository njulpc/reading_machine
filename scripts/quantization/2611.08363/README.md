# StrataFlux：Qwen3-0.6B 数值组件验证

论文：[arXiv:2611.08363](https://arxiv.org/abs/2611.08363)。本目录包含真实可执行代码、实际运行结果；范围是数值组件，不是整篇论文系统复现。

## 环境与命令

本次使用 macOS CPU 4线程、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6。真实Qwen3-0.6B权重revision为 `c1899de289a04d12100db370d81485cdf75e47ca`，模型BF16；权重从已存在本机Hugging Face缓存读取，`local_files_only=True`，无随机初始化冒充预训练模型。

从仓库根目录执行：

```bash
python3 scripts/quantization/2611.08363/demo.py --model /Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca --output scripts/quantization/2611.08363/results.json
```

其他机器替换 `--model` 为已下载的同revision模型目录。程序不会自动下载权重；缺缓存会明确失败。结果写到 `results.json`，不保存大型训练权重。

## 实现、校准与结果

实现式2–4：1024通道分块、每块top-|x|选择32通道、保留输入符号；求解带残差先验的ridge正规方程，λ=M平均对角线；将拟合补偿按输入列量化为4bit。真实首层q_proj完整2048×1024权重，3bit per-output-channel对称RTN作为常驻底座。论文允许底座量化器与补偿分离，但本例RTN不等于YAQA/AWQ。

校准为两个手写文本各64token，留出为另外两个文本各64token，原文和形状全部写入JSON。CPU FP64数值运算；实际λ=0.02010618，正规方程相对误差9.66e-16。

| 集合 | RTN底座MSE | 原残差4bit补偿MSE | 拟合4bit补偿MSE |
|---|---:|---:|---:|
| 校准 | 0.00605559 | 0.00375904 | 0.00055355 |
| 留出 | 0.00605701 | 0.00372963 | 0.00372121 |

6项assert通过：正规方程、目标函数下降、全选择退化到残差、chunk预算、KV修正式等价于直接替换、GQA组预算。式7–8在小张量上覆盖group attention求和、跨query head取max、同时修正softmax分子分母以及大score数值稳定性；最大绝对差2.56e-12。4.37秒完成，退出码0。

## 未复现部分

没有KVarN编码、嵌套低比特打包、neuron bundle、真实Qwen KV压缩、跨层fetch lead/lag、LRU/SSD后台传输、CUDA/Metal内核、全模型PPL或吞吐测量。原论文系统需要专用运行时和硬件集成，本次仅CPU数值路径；浮点仿真并不节省本机实际权重内存。小校准集产生的训练收益明显超过留出收益，不应把校准MSE当任务准确率。
