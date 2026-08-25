# NeuroPrefetcher: Storage-Aware Sparse LLM Inference via Delta Prefetching

> arXiv: [2608.22643](https://arxiv.org/abs/2608.22643) · v1: 2026-08-23 · 主分类: cs.DC
> 证据：官方摘要与 v1 HTML 全文。

## 1. 核心速览

**研究主题**：模型大于内存时的稀疏 MLP 权重预取。
**一句话总结**：利用相邻 token 有约 82%–85% 活跃神经元保持不变，NeuroPrefetcher 只从 NVMe 预取新激活行；单个 GPU predictor 占基础模型参数 2.86%，真实统一内存边缘设备上比文中对照快 7.9–12.0×。

## 2. 研究背景与动机

量化、换小模型和普通 offload 都隐含“模型最终能装进某一层内存”的假设；模型始终大于 resident memory 时，存储读延迟进入关键路径。按页 reactive paging 又不了解 token 级 MLP 稀疏性。

## 3. 核心方法与创新点

- 统计 autoregressive decoding 的跨 token 稀疏激活局部性。
- layer 0 后用一个 GPU predictor 一次预测所有后续 MLP 层的活动行。
- 对预测集合与 resident buffer 做差，只发起 incoming delta rows 的 NVMe 读。
- 以应用调度预取替代 OS demand paging，把稀疏模型行为显式暴露给存储系统。

## 4. 实验设计与结果

观察到 82%–85% 活跃神经元跨 token 延续；predictor 大小为基础模型参数的 2.86%。在真实统一内存边缘硬件、不同受限预算下，报告 7.9–12.0× 加速。摘要中的对照 URL 渲染异常，因此结论保守表述为“相对论文定义的基线”，不擅自补写基线名称。

## 5. 局限性与未来展望

收益依赖 MLP 可预测稀疏性、NVMe 带宽和 miss 代价；分布外 prompt 或层 0 预测失误会形成 stall。predictor 也带来额外参数与算力。未来应报告召回率-带宽-质量三维曲线和不同 SSD 的尾延迟。

## 6. 学术启发

当模型无法“压到能装下”时，压缩问题会转化为工作集预测问题。评价需要把参数稀疏率、常驻集合、增量 IO 和错误预取一起纳入。
