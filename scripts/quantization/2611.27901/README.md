# QuantStream3D 的 Qwen3-0.6B KV 量化迁移验证

论文：[官方全文](https://arxiv.org/html/2611.27901v1)，重点 §4.1、§4.2、附录 B.4。此处是已运行的**推理量化组件迁移**，不是完整视觉几何系统复现。

## 实现范围与对应关系

`demo.py` 加载真实 Qwen3-0.6B，在各 Attention 层实际消费压缩历史缓存，并输出与原模型的数值差异；不是只打印模型名的演示。

- 按 64 token、每个 head/channel 分组，对 K 和 V 使用独立 min/max、affine RTN。
- 2/4-bit 整数实际打包到 uint8，scale/zero point 用 FP32。末尾短组用最后一个 token 填充，避免 padding 改变范围；常量组单独精确表示。
- 首个 64-token chunk 和零基层号 14 采用 4 bit，其余 2 bit。这是将原文帧/层策略直接映射至文本 chunk，**未宣称它在 Qwen 上最优**。
- RoPE 后对 Q/K 同时做 H64/8；Qwen 的更宽 head 用分块正交变换。V 不旋转。
- 当前 chunk 以浮点参与读取，仅在写入历史时量化。显式构建跨 chunk 因果 mask。
- 原生 chunked forward 与未改动全序列 forward 对照，检验位置和因果关系。

## 校准、训练与尚未复现部分

原论文量化参数由写入块在线 min/max 计算；固定保护层来自视觉数据敏感性扫描。这里实现在线统计，但没有 MVS-Synth/PointOdyssey 的几何校准。原文 QAD 用独立教师/学生历史，训练全部块和相机/深度/点云头，2000 更新、AdamW β=(0.9,0.95)、weight decay=0.05、峰值学习率 1e-5、梯度裁剪 1，并保留 clip 内 STE 历史梯度。

Qwen 没有这些几何头；本次没有把文本 KL 替代几何损失后冒称原算法。本脚本未实现或运行几何 QAD、几何头蒸馏和 Triton 融合内核。当前 Packed 路径是推理代码，不支持 STE 训练。完整方法复现仍未完成；真实原因是任务/模型结构不对应和缺少原视觉训练设置。本机为 CPU 验证，也未测 H20 性能。

## 运行

环境：Python 3.9、PyTorch 2.8.0、Transformers 4.57.6，CPU。使用已有本地权重缓存，snapshot `c1899de289a04d12100db370d81485cdf75e47ca`。代码先解析本地 snapshot 路径，避免 tokenizer 在 local_files_only 下仍请求模型信息。

```bash
python3 demo.py
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3 demo.py --qwen --tokens 256
```

需要 `torch transformers huggingface_hub` 及预先缓存的 `Qwen/Qwen3-0.6B`。这是单 batch、无 padding 文本 smoke test，默认 64-token chunk；不支持作为任意 generate/cache API 的直接替换。

## 本次实际结果

完整机器可读输出见 `results.json`。

| 指标 | 实测 |
|---|---:|
| 正交变换内积最大误差 | 1.52587890625e-5 |
| 打包/解包与独立标量参考，含常量和边界组 | 通过 |
| 原生分块 vs 原始全序列最大 logit 误差 | 0 |
| 压缩历史后的平均 KL（排除首 chunk） | 0.4427199364 |
| 同位置 top-1 一致率 | 91.1458% |
| 原生 FP32 KV 字节 | 58,720,256 |
| 打包 KV（含参数与 padding）字节 | 6,520,832 |
| 相对 FP32 缓存压缩倍数 | 9.0050 |
| 相对同形状 FP16 缓存估算倍数 | 4.5025 |

输入是代码内重复合成段落，256 token。上述一致率不等于任务准确率，KL 也不是标准语料困惑度；FP16 倍数是同形状字节口径换算，没有运行 FP16 基准。缓存存储数字不包含权重、临时解码张量或峰值 RAM。本实现解包后仍使用浮点 attention，不声称低比特计算加速。
