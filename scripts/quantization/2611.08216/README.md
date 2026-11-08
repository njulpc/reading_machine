# ProQuant：Qwen3-0.6B 数值组件验证

论文：[arXiv:2611.08216](https://arxiv.org/abs/2611.08216)。本目录包含真实可执行代码、实际运行结果；范围是数值组件，不是整篇论文系统复现。

## 环境与命令

本次使用 macOS CPU 4线程、Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6。真实Qwen3-0.6B权重revision为 `c1899de289a04d12100db370d81485cdf75e47ca`，模型BF16；权重从已存在本机Hugging Face缓存读取，`local_files_only=True`，无随机初始化冒充预训练模型。

从仓库根目录执行：

```bash
python3 scripts/quantization/2611.08216/demo.py --model /Users/lipengcheng/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca --output scripts/quantization/2611.08216/results.json
```

其他机器替换 `--model` 为已下载的同revision模型目录。程序不会自动下载权重；缺缓存会明确失败。结果写到 `results.json`，不保存大型训练权重。

## 实现、校准与结果

实现论文的对称静态per-output-channel W4与动态per-token A8，round采用STE，学习权重及log-scale；SRL从真实模型随机生成标签，采样temperature0.7/top_p0.8/top_k20、最多16新token。式A2同时使用双向KL及CE，α由初始teacher目标token平均概率估计为0.7768235；β=0.1是本例设定，不冒充论文未公开的唯一值。

AdamW，权重lr=1e-5、scale lr=1e-4、weight decay0、grad clip1；这些学习率为CPU smoke run选择。只训练前2个decoder blocks的线性层，其他层和embedding冻结；新增可训练参数FP32，模型其他参数BF16。教师logits在替换模块前缓存并固定。以两个手写prompt训练10步，响应和完整逐步日志写入JSON。

实现式1的子集梯度均值比，以及Algorithm1的0/30/40/50%步、50/75/88/100%层预算。28层单测得到14/21/25/28层；实际仅2层，因此取ceil后预算为1/2/2/2。5项数值/梯度/损失单测通过，10步损失均有限。实际280.32秒、退出0。训练结束两个原训练样本的forward KL为0.02160/0.01550，CE为0.27537/0.25404；这些不是held-out准确率，也不能证明优于原论文或全量QAT。

## 关键适配与未完成项

Qwen3-0.6B是纯文本模型，根本没有visual token。`sensitivity()`实现原视觉公式并用合成梯度验证；实际Qwen运行明确以prompt token作代理，日志命名为`prompt_proxy_tau`。这验证代码路径，不验证ProQuant的视觉优先假说，不能称完整多模态复现。

仅前2块W4A8，非全模型W4A8；没有LLaVA-680K、5epochs/8×H200训练、SmoothQuant W4A4初始化、多模态任务评测或低比特打包内核。由于指定纯文本模型与方法模态要求不匹配，视觉机制保留为未验证项。
