# 深度技术分析：Sub-Token Routing for KV Cache Compression

## 1. 核心速览

**研究主题**：KV cache 压缩的 sub-token 细粒度控制轴：保留 token 内的 value 分组路由。

**一句话总结**：在 token 级削减之后，把每个保留 token 的 value 向量分组、只保留选定组（query/key 不动），为 KV 压缩增加 token 内部的细粒度控制轴；匹配 KV 预算下与 Quest（LLaMA-2-7B、Qwen2.5-7B）及 FastV/VisionZip（LLaVA、Qwen-VL）组合均提升性能，预算越小增益越大。

## 2. 研究背景与动机

KV 压缩现有手段（选择、驱逐、量化、压缩 token 或削减视觉序列）都是 token 粒度的"整存整取"。当 token 删到不能再删时，是否还有压缩空间？答案在 token 内部：value 向量的各维度组的重要性并不均等。

## 3. 核心方法与创新点

- **sub-token 路由**：保留 token 的 value 状态分组选择，query/key 保持完整——利用 value 与 key 在注意力中的不对称角色。
- **两阶段组合设计**：先 token 级削减定留存，再 sub-token 路由压缩留存内部——正交互补而非替代。
- **跨 LLM/VLM 通用**：文本与视觉模型均验证。

## 4. 实验设计与结果

匹配 KV 预算下：Quest + sub-token 在 LLaMA-2-7B/Qwen2.5-7B 提升；FastV/VisionZip + sub-token 在 LLaVA/Qwen-VL 提升；预算越小增益越大。

## 5. 局限性与未来展望

局限：value 组选择的准则细节与额外计算开销摘要未充分披露；与 KV 量化叠加时（组选择 + 低比特）的交互未研究；不规则 value 访问对 kernel 效率的影响待实测。未来方向：与 MoE-nD 的头维轴（低秩投影）对比统一、路由策略的学习化、融合 kernel 实现。

## 6. 学术启发

- 压缩粒度不断细化：模型→层→头→token→sub-token，每一级粒度都有独立收益——多维压缩坐标系（MoE-nD 的四轴 + 本文的 sub-token 轴）正在成形。
- V 与 K 的不对称处理（V 可组选、K 需完整）与 AdaCluster 的 Q/K 非对称、MoE-nD 的 K-bits/V-bits 分离再次印证注意力组件的角色差异是压缩设计的基本自由度。

---

*论文信息：arXiv:2604.21335，Jiang Wei, Wang Wei，cs.LG*