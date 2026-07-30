# 技术深度分析：TDC-Based Resonant Compute-in-Memory for INT8 CNNs with Layer-Optimized SRAM Mapping (arXiv:2601.00434)

> **论文**: Time-to-Digital Converter (TDC)-Based Resonant Compute-in-Memory for INT8 CNNs with Layer-Optimized SRAM Mapping
> **作者**: Dhandeep Challagundla, Ignatius Bezzam, Riadul Islam
> **arXiv**: https://arxiv.org/abs/2601.00434 ｜ 提交: 2026-01-01 ｜ 分类: eess.SP

---

## 一、核心速览

### 研究主题

面向 INT8 量化 CNN 的无 ADC 时域存算一体（TDC-CiM）加速器架构：用时-数转换器（TDC）替代传统模拟 CiM 中高功耗高面积的 ADC，并配以层优化 SRAM 映射策略。

### 一句话总结

该 TDC-CiM 架构以 4-bit TDC（1 GS/s、1.25 mW）数字化模拟 MAC 结果，结合 8T SRAM 位元与自动宏选择算法，在 TSMC 28nm 8KB 阵列上实现 320 GOPS 吞吐与 38.46 TOPS/W 能效，SRAM 从 32KB 扩到 256KB 时推理能耗最多降低 8 倍。

---

## 二、研究背景与动机

存算一体通过 SRAM 内并行 MAC 消除数据搬运，是量化神经网络加速的热门路线；但传统模拟 CiM 依赖 ADC 转换 MAC 结果，ADC 带来显著的面积/功耗开销与非线性误差，成为 CiM 能效进一步跃升的瓶颈。INT8 量化 CNN 的普及使"低位宽友好的数字化读出"成为关键需求。

---

## 三、核心方法与创新点

- **TDC 替代 ADC**：以脉冲收缩延迟单元构成 4-bit TDC，1 GS/s 采样、功耗仅 1.25 mW，规避 ADC 的面积/功耗/非线性问题。
- **专用 8T SRAM 位元**：支持可靠的位级 MAC 操作。
- **权重静止映射+自动 SRAM 宏选择**：跨 CNN 工作负载可扩展、能效最优的部署。
- **28nm 硅验证**：8KB SRAM 阵列实测 320 GOPS、38.46 TOPS/W。

---

## 四、实验设计与结果

在六个 CNN 模型上评估映射算法：SRAM 容量从 32KB 扩展到 256KB 时推理能耗最多降低 **8×**，量化后精度损失最小；架构在 TSMC 28nm 工艺 8KB 阵列上验证可行，吞吐 **320 GOPS**、能效 **38.46 TOPS/W**。

---

## 五、局限性与未来展望

局限：仅验证 INT8 CNN，未覆盖 4-bit 及以下或 Transformer 工作负载；TDC 精度（4-bit）可能成为更高位宽读出的瓶颈；工艺缩放与更大阵列的良率问题未知。未来方向：时域 CiM 支持混合精度/INT4、面向 Transformer 注意力的时域 MAC 设计、与片上量化解码的协同。

---

## 六、学术启发

- **量化算法-硬件读出电路协同设计**：低位宽量化的收益会被读出电路（ADC）吞噬，本文说明压缩研究需要把"读出成本"纳入位宽选择。
- **TDC 作为低功耗数字化路径**对模拟/混合信号 NN 加速器有普适借鉴价值。

---

*分析时间: 2026-01 月度回填 ｜ 分析人: AI Assistant*
