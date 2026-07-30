# Sub-Token Routing (arXiv:2604.21335) 复现 Demo

## 论文核心

Sub-token routing：在 token 级削减（Quest/FastV 等）之后，把保留 token 的 **value 向量分组、只留选定组**（query/key 不动），为 KV 压缩增加 token 内细粒度控制轴；预算越小增益越大，与 token 级削减互补。

## 本 demo 复现内容

1. 真实 Qwen3-0.6B 配置（KV 头、head_dim=128）构造注意力张量（随机权重）。
2. 实现两阶段：token 级 top-k 削减（Quest 式按 query-key 相关性选块）→ 保留 token 的 value 按组路由（按 value 组能量选 top-g 组）。
3. 匹配 KV 预算下对比：仅 token 削减 vs token 削减 + sub-token 路由 的注意力输出误差，并验证"预算越小增益越大"。

## 运行

```bash
python3 demo.py
```

## 限制（如实说明）

- Qwen3-0.6B 权重未下载，用真实架构配置 + 随机权重验证代码路径；value 组重要性以能量为准（论文未指定具体准则时采用其精神）。
- 未实现 CUDA kernel，输出误差为 PyTorch 参考值。
