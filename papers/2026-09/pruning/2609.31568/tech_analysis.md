# DeepEdu-v1: Efficient and Scalable Agentic LLMs for Vietnamese Education

- arXiv：[2609.31568](https://arxiv.org/abs/2609.31568)；[官方全文](https://arxiv.org/html/2609.31568)
- v1 UTC：2026-09-25T17:33:41+00:00；北京时间：2026-09-26T01:33:41+08:00
- 官方分类（主分类在前）：Artificial Intelligence (cs.AI)
- 证据范围：官方abs与HTML正文/所列附录；数字为论文报告，另明确标记本次实测。

## 1. 核心速览

研究主题：长上下文稀疏注意力中检索开销摊销。

一句话总结：DeepEdu-v1/SCALE的SCR将相似连续query子块聚类，按簇执行一次top-k检索，减少重复选择开销；核心长上下文实验是BF16，不是一项新的AWQ/GPTQ量化算法。

## 2. 研究背景与动机

选择少量KV参与注意力可以省计算，但若每个子块都重新对完整缓存检索，选择本身会成为瓶颈。仅压缩静态权重也不能消除长上下文的动态开销。论文的另一个agentic playbook部分涉及经验整理，不能与模型压缩收益混为一谈。

## 3. 核心方法与创新点

1. 将子块query作均值指纹并L2归一化。簇中每个新子块必须与固定首块anchor达到余弦阈值，而非只比较前一块，防止链式漂移。
2. anchor按各头softmax归一化后求和的TokenSelect soft-voting规则，对KV选择共享top-k。
3. 选中集合还包括attention sinks和覆盖整个簇的local window；去重后施加因果mask。只近似远处上下文，簇内先前token注意力保持完整。
4. L=512、Lmax最多4096即8子块；θ=.95/.97/.99，outer chunk8192，k8192、基础local512、sinks128。选择复杂度由O(MNd)变O(|P|Nd)，这是检索摊销，而非证明KV缓存被永久删除。

## 4. 实验设计与结果

单H100-80GB、Qwen2-7B-Instruct、BF16、SGLang+FlashInfer，模型配置最大上下文1,048,576、RoPE base10^6。InfiniteBench六任务完整测试集，RULER八类×每类100样本，4K–128K。

θ=.95、Lmax4096时，R.KV准确率91.0→98.0，TTFT13.2→8.3秒；Code.D同一配置准确率26.7→24.9、延迟8.8→5.7秒，不能拿θ=.99/Lmax1024的28.8精度搭配最快配置耗时。独立n=30剖析检索调用8959→1165（约7.7倍减少），TTFT13.1→8.3秒，检索耗时4.5→0.9秒贡献77%节省。RULER128K准确率64.78→65.28。

本次阅读官方算法和表VI–IX，未运行H100长上下文系统。

## 5. 局限性与未来展望

精度提升部分来自更宽簇内local window，不能全归因于共享检索；完整缓存仍需支撑后续选择，不能把少访问KV等同于常驻KV显存同比缩小。短上下文收益小，且个别任务掉点。部署配置相对vLLM近2倍的总收益还包含其他系统因素。

未来应匹配local window、分开统计峰值显存/检索字节/注意力FLOPs，并报告不同token分布下聚类长度。

## 6. 学术启发

稀疏算法的选择成本应单独剖析；“减少计算”常常需要先减少决定计算哪些元素的开销。固定anchor比相邻链式相似更容易控制误差，同时保留簇内精确计算可缓解共享选择造成的信息损失。

## 阅读评分（1–10，越高越强）

- accuracy：7/10；有长上下文基准，但配置间精度不能拼接
- compression：5/10；减少检索调用和稀疏计算，不证明常驻KV压缩
- innovation：7/10；固定anchor共享检索并保留簇内因果注意力
- reproducibility：6/10；算法预算完整，H100/SGLang/FlashInfer环境未运行
