# 2609.02652 — Leech/Planes14 多壳权重布局

## 方法与实现范围

论文的 LLVQ 每 24 个权重编码为 `Λ24(12)` 的 47-bit index 加 1-bit gain（磁盘 2 bit/weight）；加载时将 301 个类的索引转码为 Planes14：`class:9 | gain:1 | sign:24 | plane0:24 | plane1:24 | plane2:24 | pad:6`，固定 14 byte/块，即布局流 `112/24=4.6667 bpw`。论文 4B 整模 kernel accounting 为 4.804 bpw，另含 row scale/tail；二者不可混用。

本 demo 只验证上述 LSB-first pack/shift/mask 位几何。输入字段由真实 Qwen 权重产生，但不是 Leech encoder 输出，也不经过 301-class table；因此不报告伪造的模型量化误差。

## 运行

```bash
python3 scripts/quantization/2609.02652/demo.py --self-test
python3 scripts/quantization/2609.02652/demo.py --output-json /tmp/2609.02652.json
```

## 代码审查与验证（2026-09-04）

- **算法一致性：部分一致。** Planes14 字段宽度、offset、LSB-first、6-bit 零 padding、14-byte stride 和位率边界一致；Leech 最近邻搜索、47-bit bijection、301 类、gain centroids、KOTMS、row scale、KeepExact tail 与 CUDA GEMV 未实现。
- **修复：** 删除把四种稀疏 sign-shell 向量称为 Leech 多壳并错误报告 `1.2348 bpw` 的路径；改为 106-bit payload/112-bit record 的真实布局往返，并分别报告 `4.6667` 布局 bpw、论文 `4.804` kernel bpw 与 `2.07` 有效磁盘 bpw。
- **证据：** 官方源码 `pjmalandrino/llvq@8a808f9e` 的 `runtime.rs` 与 `planes14_format.rs` 只读核对字段和金值；本机未安装 Cargo，未执行 Rust 全空间测试。
- **结果：** 5,462 个 24D 记录 pack/unpack 全部一致，padding 全零，退出码 0，1.52 s。
- **真实 Qwen3-0.6B：未跑通量化。** 官方密封工件是 Qwen3-4B，服务路径依赖 CUDA；本 demo 只有真实 Qwen 权重驱动的布局 smoke test。

环境：macOS 26.6.2 arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；本地完整 Qwen3-0.6B checkpoint。
