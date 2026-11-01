# Read, Allocate, Route: Role-Coupled Tokenization for Pixel-Space Generative Transformers

- arXiv：[官方详情](https://arxiv.org/abs/2610.40647)；[v1全文](https://arxiv.org/html/2610.40647v1)。
- v1提交：UTC 2026-10-29T17:59:21+00:00；北京时间 2026-10-30T01:59:21+08:00。归档以北京时间提交月份为准。
- 官方分类：Computer Vision and Pattern Recognition (cs.CV) ; Artificial Intelligence (cs.AI); Machine Learning (cs.LG); Neural and Evolutionary Computing (cs.NE)。分析归类：other。
- 证据：官方摘要、Submission history及全文方法/实验相关段落；全文HTML缺失信息不补造。论文报告数字与本机结果分开标注。

## 1. 核心速览

研究主题：按频域角色压缩全局注意力通信。

一句话总结：SpecSlot 仅让低频槽参与全局注意力，在 ImageNet-512 以少38.2%的FLOPs接近 JiT-B/16 的FID。

## 2. 研究背景与动机

像素空间生成器通常把每个图像patch作为一个全局token，缩小patch以增加细节会同步抬高注意力的平方成本。本文把“输出细节容量”和“全局通信序列长度”分开：低频结构需要远程交互，高频细节可以主要依靠局部处理。它属于重新训练架构后的计算压缩，而不是对已有检查点做无损后处理。

## 3. 核心方法与创新点

- 将总槽数写成 N=W×K：W个空间anchor，每个anchor扩展K个槽；槽拥有互不重叠的DCT径向频段。每个系数恰好预测一次，所有槽在每个流时间均计算，并非动态丢弃高频槽。
- 输入先经patch投影与零初始化的深度卷积混合，再扩展为槽。输出通过逆DCT、平方根Hann窗及50%重叠相加重建；另加零初始化空间修正头，仍直接在像素空间计算rectified-flow速度损失。
- 固定slot 0为低频carrier。GGLL调度重复3次：两层全局通信、两层anchor内局部通信。W=256、K=4、32个条件token时，全局长度由1056降至288，但投影和局部计算仍有开销。

## 4. 实验设计与结果

§4、表1–3：ImageNet训练120 epochs、有效batch512，主结果5个独立种子；以50段Heun采样，在H800 BF16上统计全网络FLOPs。ImageNet-512的SpecSlot-K4为135.64 GFLOPs、FID9.14、12.69 img/s；JiT-B/16为219.56、8.45、7.93，因此FLOPs少38.2%，FID差0.69，吞吐约1.60倍。算力匹配JiT-CM为141.21 GFLOPs、FID11.98，SpecSlot改善FID2.84。文生图DPG由61.15至62.21，但GenEval26.99低于JiT-B/8的29.78，不能声称各项质量全面领先。

压缩口径：ImageNet-512前向FLOPs少38.2%，对应约1.62倍计算比；非权重文件压缩。

本次未执行该论文的训练或硬件测量，以上为论文报告，不是本机重测。

## 5. 局限性与未来展望

主对照经过统一重训，结论依赖120-epoch预算与各模型各自扫描的CFG。ImageNet-256相对算力匹配模型的FID差异落在五种子区间内；不能把全局二次项缩小比例当作端到端速度或文件压缩率。未来应测试更大分辨率、其他生成骨干，以及相同墙钟训练预算下的收益。

## 6. 学术启发

先给token分配明确输出职责，再据职责确定通信范围，是比统一token稀疏率更结构化的设计。实验应同时报告等FLOPs、等质量和吞吐，避免仅以注意力理论复杂度代替部署成本。
