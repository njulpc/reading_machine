# 2609.01962 — Qwen 后训练三值化

## 方法与实现范围

论文对 Qwen3-4B 的 252 个 attention/MLP Linear 执行 `KOTMS → E2M-ATQ → GPTQ compensation`，embedding 与 untied lm_head 保持 BF16、激活/KV 保持 A16。校准为 WikiText-2 64×2048 token，block/group 128；E2M-ATQ 使用 row offset、阈值 `0.75·mean(|Wc|)`、四个 Hessian salience mask、orders `[2,2,1,1]` 和 15 次交替细化，随后逐列传播逆 Hessian 误差。

本 demo 对 Qwen3-0.6B 全部 196 个 backbone Linear 执行 group-128 E2M-ATQ。它用 96 个真实 token 的 `diag(H)` 与权重幅值构造 salience 代理；没有学习 KOTMS，也没有完整 inverse-Hessian GPTQ 列传播或真正 bit-pack。

## 运行

```bash
python3 scripts/quantization/2609.01962/demo.py --self-test
python3 scripts/quantization/2609.01962/demo.py --output-json /tmp/2609.01962.json
```

## 代码审查与验证（2026-09-04）

- **算法一致性：部分一致。** group/block 128、row offset、0.75 阈值、双平面高显著权重、15 次细化、A16 边界和浮点 embedding/head 一致；KOTMS、四个完整 mask 的 Hessian 排名、inverse-Hessian GPTQ、64×2048 校准、Qwen3-4B 与打包内核未复现。
- **修复：** 移除普通 Hadamard 与 rank-8 SVD 冒充 KOTMS/GPTQ 的路径；恢复 E2M-ATQ 两平面公式、salience 分配和 15 次交替细化；由 256 行切片扩为 196 层/440,401,920 权重，并增加整模前向、KV 生成和有限值检查。
- **结果：** 退出码 0，14.41 s；第二平面比例 `0.0390625`，仅符号码率估计 `1.64688 bpw`（不含 offset/scale/packing metadata）。独立文本 logits MSE `9.69246`、cosine `0.622823`，生成换行 token，质量明显退化。
- **真实 Qwen3-0.6B：已跑通（E2M-ATQ 工程迁移）。** 论文完整三值化流水线未跑通；不能把 fake-quant 张量称为 1.641-bpw 可部署工件。

环境：macOS 26.6.2 arm64 CPU，CUDA/MPS 不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；本地完整 Qwen3-0.6B checkpoint。
