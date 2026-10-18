# FALCON 数值PTQ机制的 Qwen3-0.6B 转移验证

来源：[官方论文](https://arxiv.org/abs/2610.22143)，[全文§3.3式8–9](https://arxiv.org/html/2610.22143v1)。

本目录包含真实可执行实现和本轮实测结果。目标是检验固定裁剪、每张量min-max和二次幂INT8量化的数值机制；不是FlashOcc/FPGA完整移植。

## 实现与边界

- `paper_relu`严格执行a_hat=min(max(a,0),32)，然后round(a_hat/2^k)并饱和到[-128,127]。
- `unclipped`是不裁剪INT8对照；`signed`用[-32,32]，是为Qwen明确修改的转移消融，不能称论文原算法。
- 固定激活scale来自4段各128token校准；权重为每张量INT8。k取能覆盖min/max的最小二次幂步长；论文未提供Vitis内部tie/search细节，本实现用PyTorch round ties-to-even与保守范围覆盖，未宣称与Vitis逐位一致。
- 只替换`model.layers.0.mlp.down_proj`，其余模型BF16；INT8权重以int8 buffer保存，矩阵乘先反量化再浮点运算。没有整数kernel或速度承诺。
- Qwen SiLU-gated激活有负值，FALCON的BEV非负假设不成立。校准负值780351/1572864，abs>32为0，signed上限在本实验未触发；这直接限制了实验结论。
- 原文固定C=32的BEV规则保留；校准文本数/长度、所选Qwen层、权重范围和scale规则为本地适配选择，不能冒充原文设置。

## 运行

环境：Python3.9.6，torch2.8.0，transformers4.57.6，CPU 4线程，BF16 eager attention。使用已缓存Qwen3-0.6B revision `c1899de289a04d12100db370d81485cdf75e47ca`，`local_files_only=True`，不下载权重。

```sh
python3 demo.py --output results.json
python3 demo.py --test-only --output tests.json
PYTHONPYCACHEPREFIX=/private/tmp/arxiv_20261019_pycache python3 -m py_compile demo.py
# 其他机器可用 --model 指定相同revision的本地快照路径
```

本轮实际模型运行18.785秒（加载和12次完整前向的总时长，不是量化层提速）。4条校准、2条独立评估文本全在代码和JSON中；重复短文本是smoke test，不是标准语言建模PPL。

|模式|评估1/2 loss|KL(base→quant)1/2|top1一致率1/2|
|---|---|---|---|
|BF16原层|0.702692 / 0.507775|0 / 0|1 / 1|
|未裁剪INT8|0.689747 / 0.504653|0.002777 / 0.001103|0.976563 / 0.976563|
|论文非负裁剪|0.768807 / 0.482808|0.033270 / 0.020533|0.945313 / 0.921875|
|signed适配|0.689747 / 0.504653|0.002777 / 0.001103|0.976563 / 0.976563|

激活k=-4，权重k=-8；一个权重矩阵的int8 payload=3145728bytes，原BF16=6291456bytes。实验仍持有原层和反量化临时矩阵用于对比，不能说进程峰值显存/内存下降2倍。小样本某段loss下降不证明量化提高精度；KL更清楚地暴露了非负裁剪迁移失配。

已完成六项小张量验证：式8–9已知向量、饱和、二次幂scale、零张量、signed边界、已知答案量化线性运算；语法/导入通过。未完成：整模INT8、真实文本基准、多seed、原占据网络训练/数据、Vitis bit-exact、KR260硬件及时延界验证。本机缺原硬件/数据/模型与对应运行环境；本轮仅本地CPU Qwen机制实验，不伪造原论文复现。
