# L3G-World: Real-Time Infinite World Generation with Latent 3D Gaussian Memory

- arXiv：[官方详情](https://arxiv.org/abs/2610.40614)；[v1全文](https://arxiv.org/html/2610.40614v1)。
- v1提交：UTC 2026-10-29T17:54:42+00:00；北京时间 2026-10-30T01:54:42+08:00。归档以北京时间提交月份为准。
- 官方分类：Computer Vision and Pattern Recognition (cs.CV)。分析归类：other。
- 证据：官方摘要、Submission history及全文方法/实验相关段落；全文HTML缺失信息不补造。论文报告数字与本机结果分开标注。

## 1. 核心速览

研究主题：压缩世界模型的持久3D推理记忆。

一句话总结：L3G-World按场景新增信息更新高斯记忆并直接渲染VAE特征，显著降低持久状态和重复编码成本。

## 2. 研究背景与动机

按视频帧累积3D点云会重复储存同一空间，RGB渲染后再经VAE编码则进一步增加世界模型读取成本。本文压缩的是生成系统的外部持久推理状态，同时用少步蒸馏获得实时变体；不是对DiT权重的量化。

## 3. 核心方法与创新点

- 依据已有记忆渲染的不透明度与RGB误差标出缺失区域，只在这些位置从DA3特征经K-means初始化新高斯查询；可见旧高斯由另一条refinement流更新。
- 拼接新旧查询，经几何特征cross-attention、流内self-attention和全局交互；新条目加入记忆，旧条目做残差修正，未被选中的条目保留。
- 每个高斯还存VAE潜在特征，可直接渲染为DiT条件；与噪声潜变量按通道拼接，不新增整段记忆token。Fast变体沿用AnyFlow的flow-map与on-policy distribution matching。

## 4. 实验设计与结果

§4、表2：DA3几何骨干、Cosmos-Predict2.5生成器，DL3DV/RealEstate10K训练，4张A100；评估效率在单张A100上。DL3DV中L3G-World为33K基元、11.88MiB，NeoVerse为8766K、501.57MiB，约266倍基元差和42倍记忆差；FID40.57对152.25。RealEstate10K对应25K、8.91MiB对10437K、597.21MiB。VAE条件渲染相对NeoVerse约349–359倍；这些是记忆组件指标。摘要9FPS属于包括少步生成器的实时系统，不能仅归因于记忆设计。

压缩口径：相对NeoVerse的记忆字节约42–67倍减少；不代表总模型显存同倍率下降。

本次未执行该论文的训练或硬件测量，以上为论文报告，不是本机重测。

## 5. 局限性与未来展望

压缩比高度依赖对照：相对点云Lyra2.0与高斯NeoVerse的分母不同，基元数量也不等于字节数。Fast变体在部分一致性与FID指标退化，RealEstate10K的相机误差并非最好。未来应测试动态物体、超大场景和持续误差积累，同时报告总GPU常驻内存而非仅记忆数据。

## 6. 学术启发

长期推理状态应随新信息而非输入帧数增长。压缩后若仍需昂贵的解码再编码，表示更小不一定更快；把记忆表示直接对齐下游模型输入可同时解决两项开销。
