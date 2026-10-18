# Which Tokens to Merge? Diffusion Dynamics for Efficient Image Generation

- arXiv：[2610.22370](https://arxiv.org/abs/2610.22370)；[官方全文 v1](https://arxiv.org/html/2610.22370v1)
- v1 UTC：2026-10-15T17:59:35+00:00；北京时间：2026-10-16T01:59:35+08:00
- 主分类及交叉分类：Computer Vision and Pattern Recognition (cs.CV)
- 本轮证据：官方abs本轮刷新，标题/摘要/分类/history与缓存一致；全文来自10月18日保存的官方HTML v1，本轮阅读方法、主要实验及相关局限段落，未声称逐行审计全部附录。

## 1. 核心速览

研究主题：other。

一句话总结：DaTMe 用去噪动态和局部结构共同决定token合并，改善高合并率下的图像保真，但实测加速较温和。

## 2. 研究背景与动机

按prompt相关性保护前景的合并会忽略背景边界。直接用score变化又混入噪声schedule的尺度项，因此需要更贴近clean图像状态的token重要度。

## 3. 核心方法与创新点

1. 将score投到Tweedie clean估计，以相邻步差构成temporal信号，再结合局部高频结构信号；避免直接score slope的晚期尺度放大。
2. source是两轴最低r比例交集，constraint anchor是最高1-r交集。交集不足时按空间grid补足floor(rN) source，避免局部集中删除。
3. anchor不作source/destination，其他destination接收空间最近source，合并后剩N-floor(rN) token；r是合并掉的比例，非保留比例。

## 4. 实验设计与结果

PixArt-α、r=0.5：base FID42.1001、1.9417s、183.45TFLOPs；DaTMe43.4155、1.6884s、170.410，实际约1.15×加速、FLOPs约1.077×缩减。CFG同r FID52.2912、1.6445s；DaTMe质量更好但稍慢。r=0.7时FID47.0519、1.6426s，仍不能称3.33×整模加速。FLUX结果同样显示结构保真优势，评价对象是特定生成/seed设定。

## 5. 局限性与未来展望

构造重要度、补齐和局部路由有成本；理论信号更干净不保证最优token分配。背景细节保护与预算冲突、网格随机性、更多schedule和分辨率仍需测试。未运行原生成模型。

## 6. 学术启发

压缩论文应同时给token比例、实际被作用层、总FLOPs和wall time。用matched latency而非仅matched r比较，有助判断质量收益是否值得附加路由开销。

## 四维评分（1–10，主观研究评估）

|维度|分数|依据|
|---|---:|---|
|精度效果|8|r=.5 FID接近base且强于CFG|
|压缩倍率|5|50%token合并仅1.15×实际加速|
|创新性|8|时间/空间双信号与局部anchor|
|可复现性|8|步骤和表格充分，本轮无GPU重跑|

所有原论文实验数字来自上述官方全文，非本机重跑结果。仅FALCON条目的Qwen转移实验为本轮实际运行；速度、token预算、缓存份数与权重字节不可互换。
