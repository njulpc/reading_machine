# M³ISR: A Multi-Modal Multi-View Benchmark for 3D/4D Gaussian Splatting and Feedforward Compression

> arXiv: [2608.22465](https://arxiv.org/abs/2608.22465) · v1: 2026-08-23 · 主分类: cs.CV
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：3D/4D Gaussian Splatting 压缩与流式传输的受控 benchmark。
**一句话总结**：M³ISR 用 25 个场景、5 类室内外组、两种相机/运动配置和 6 路同步 1080p 视图，建立合成、流式、3DGS 压缩、4DGS 压缩五条赛道，并把 rate-distortion 与训练/重建成本一起纳入评价。

## 2. 研究背景与动机

现有多视角视频数据集难以分离相机几何、动态冗余和表示大小的影响，导致不同 GS 压缩方法的结果不可比。作者用可控合成数据补足真实数据集的变量混杂。

## 3. 核心方法与创新点

- 共享中心相机设计隔离角度变化，便于研究 novel-view 与表示效率。
- 提供 RGB、相机参数、深度、语义/实例分割及静动态 mask 的密集真值。
- 五赛道统一覆盖静态/动态合成、streaming 和 feedforward compression。
- 为 3DGS/4DGS 定义参考 rate-distortion 目标与初步基线。

## 4. 实验设计与结果

数据包含 25 场景、6 个同步 1080p 视图。代表性基线在静态重建质量上差异较小，但存储差异明显；动态 streaming 方法的训练或重建成本显著高于对应 offline baseline。论文重点是评价基础设施，不宣称单一压缩算法胜出。

## 5. 局限性与未来展望

合成场景的纹理、传感器噪声和动态复杂度与真实采集仍有域差；初步基线不足以形成稳定排行榜。后续应加入真实多机数据、解码能耗和网络抖动下的流式指标。

## 6. 学术启发

压缩 benchmark 不能只看 PSNR/SSIM 和文件大小；训练成本、动态更新、随机访问与 streaming 延迟同样决定可部署性。受控几何可以帮助归因，但需真实数据验证外部效度。
