# FairyFuse (arXiv:2604.20913) 复现 Demo

## 论文核心

FairyFuse：三值权重 {-1,0,+1} 把 GEMV 中的浮点乘法替换为条件加/减/空操作，在 CPU 上实现**无乘法** LLM 推理；kernel 加速 29.6×，端到端 32.4 tok/s（Xeon 8558P），质量近无损。

## 本 demo 复现内容

1. 用真实 Qwen3-0.6B 配置的线性层维度（随机权重），做 Fairy2i 风格三值化：`W ≈ γ·T`，T∈{-1,0,+1}。
2. 实现**无乘法三值 GEMV**：只用掩码加/减累加（模拟 AVX-512 masked add/sub 语义），并断言计算全程零浮点乘法。
3. 与标准浮点 matmul 对比输出误差（验证正确性）与 CPU 时延（说明性对比）。
4. roofline 估算：16× 权重压缩下的理论带宽收益。

## 运行

```bash
python3 demo.py
```

## 限制（如实说明）

- Qwen3-0.6B 权重未下载，用真实维度 + 随机权重验证；三值化方法为 Fairy2i 风格的均值阈值法。
- PyTorch 无法真正 emit AVX-512 指令，"无乘法"以代码路径保证（仅用 add/sub/where），时延对比为 CPU 上的说明性数据，非论文的 29.6×。
