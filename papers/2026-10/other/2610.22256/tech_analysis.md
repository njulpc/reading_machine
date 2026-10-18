# BitSparse: Compact Activation Storage for ReLU Feed-Forward Networks

- arXiv：[2610.22256](https://arxiv.org/abs/2610.22256)；[官方全文 v1](https://arxiv.org/html/2610.22256v1)
- v1 UTC：2026-10-15T17:24:51+00:00；北京时间：2026-10-16T01:24:51+08:00
- 主分类及交叉分类：Machine Learning (cs.LG)
- 本轮证据：官方abs本轮刷新，标题/摘要/分类/history与缓存一致；全文来自10月18日保存的官方HTML v1，本轮阅读方法、主要实验及相关局限段落，未声称逐行审计全部附录。

## 1. 核心速览

研究主题：other。

一句话总结：BitSparse 用位图和紧凑非零值无损保存ReLU激活，避免checkpointing重算并在高稀疏度下节省训练显存。

## 2. 研究背景与动机

ReLU/ReLU²重新出现后，零激活提供无需改模型数值的存储机会。传统CSR索引成本高，通用codec吞吐有限，activation checkpointing则要重新前向。

## 3. 核心方法与创新点

1. 默认64×64tile，每位置1bit mask、非零值紧凑数组、32bit tile prefix，边界零填充；每tile4096位置，mask512字节。
2. 非负值可去sign bit，使BF16/FP8的值payload为15/7位；GPU mask/count、scan、scatter和重建kernel，反向支持ReLU mask或ReLU²数值。
3. TensorBuffer在设备端保存offset，避免主机读取非零数后动态分配；计算仍是稠密FFN，属于activation storage压缩，不是新FP8量化器。

## 4. 实验设计与结果

理论/格式表：BF1690%稀疏，BitSparse6.135×、sign-bit版6.380×，理想8.126×；75%为3.195×/3.363×。八层ReLU² MLP、ρ=0.9，dense11344MiB/1827ms，BitSparse5896MiB/1815ms；sign-bit5860MiB/1828ms。BF16ρ=0.5时checkpoint6713MiB优于BitSparse8806，压缩优势依赖稀疏度。摘要的NanoGPT/Nemotron-H每token显存减少31%/30%不是整模参数缩小。

## 5. 局限性与未来展望

适用非负且足够稀疏的激活；对Qwen SiLU不能直接删负值。FP8支持指相对于选定FP8格式可逆，不代表相对于BF16无损。buffer必须避免overflow，优化器内存未计入MLP微基准；本轮未运行GPUcodec。

## 6. 学术启发

明确“无损”的参考格式和作用张量很关键。后续可用稀疏率阈值选择checkpoint或位图codec，并将动态分配、填充和反向临时张量全部计入峰值。

## 四维评分（1–10，主观研究评估）

|维度|分数|依据|
|---|---:|---|
|精度效果|9|存储无损、梯度仅舍入差异|
|压缩倍率|7|90%稀疏payload约6.38×但模型总显存较小收益|
|创新性|7|GPU位图布局与符号位/反向融合|
|可复现性|8|kernel与公式清楚，未本轮GPU测试|

所有原论文实验数字来自上述官方全文，非本机重跑结果。仅FALCON条目的Qwen转移实验为本轮实际运行；速度、token预算、缓存份数与权重字节不可互换。
