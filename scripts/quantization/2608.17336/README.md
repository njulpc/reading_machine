# TileMix（arXiv:2608.17336）Qwen3-0.6B 复现

本目录复现 TileMix 的可移植数值路径：把 causal attention 的 QK score 平面划为硬件对齐 compute tile，用静态 packed bitmask 为每个 key-tile group 选择 FP16 或 INT8 QK；全部合法连接保留，两条路径进入同一个 streaming softmax，V/PV 保持浮点。实现可替换 Qwen3-0.6B 的全部 attention 层，供无 NVIDIA/Triton 环境做算法与数据流验证。

## 算法与参数

数据流为：Q/K/V 投影与 RoPE → 按合法 causal compute tile 构造 SpTrans 精度模板 → 每行打包 64-bit 路由字 → Q/K 分块对称 INT8 → 逐 tile 解码路由并计算 QK → 恢复 scale 与 `1/sqrt(d)` → 共享 online softmax → 浮点 PV → attention 输出。

- compute tile：发布实现对 256-token 路径使用 `BLOCK_M=64`、`BLOCK_N=64`。
- 路由组：`BLOCK_N_mask = group_factor × BLOCK_N`；`group_factor=0` 按论文公式自动选择，使每行最多 64 组。
- 路由：发布代码的 SpTrans 默认 `stride=min(128, L/4)`、`c=min(32, stride/4)`，再以 seed 42 将执行中的 causal compute-tile coverage 重定向到目标比例。模板广播到所有层、batch 和 KV heads。
- 量化：Q 按 `128×d`、K 按 `64×d`，每个 block/head 一个 absmax scale；有符号对称 INT8，范围 `[-127,127]`。无 zero-point、group-wise weight quantization、异常值处理或混合权重位宽。
- 校准：不需要训练或数据校准。固定中英文本只用于取得真实激活和测量误差。
- 输出：报告目标 coverage、实际 compute-tile/group/cell coverage、SpTrans 参数、相对全 FP 路径的 MAE/最大误差/cosine，以及整模 logits 和生成结果。

## 运行

核心算子与 deterministic synthetic 路径：

```bash
python demo.py --self-test --seq-len 256
```

本机缓存中的真实 Qwen3-0.6B，第 0 层 Q/K/V 数值验证：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
python demo.py --model Qwen/Qwen3-0.6B --seq-len 256
```

28 层全部替换为 TileMix attention，并完成一次全模型前向与单 token 生成：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
python demo.py --model Qwen/Qwen3-0.6B --seq-len 256 \
  --coverage 0.5 --full-model
```

## 代码审查与验证（2026-08-20）

### 证据与一致性结论

审查依据为仓库内 `papers/2026-08/quantization/2608.17336/tech_analysis.md`、[arXiv v1 HTML/PDF](https://arxiv.org/abs/2608.17336) 以及作者发布的 [TileMix 源码](https://github.com/HanzhiZhang-Ulrica/TileMix)。

**结论：部分一致。** 公开、可移植的核心数值机制已对齐：密集连接、tile-group FP16/INT8 路由、Q/K blockwise symmetric INT8、共同 score 域、共享 streaming softmax、FP V/PV、静态 data-free SpTrans、64-bit pack/shift/mask 和 GQA 后的共享路由均已实现。仍未复刻 A100 Triton kernel、真实 INT8 Tensor Core/INT32 指令、FP16 状态舍入、变长 batch、INT8 KV cache/decode、autotuner 和吞吐实验，因此不能称为论文系统的完整硬件复现。

论文正文将 25/50/75% 描述为合法 tile-group coverage；作者发布实现实际按每个 mask bit 代表的“已执行 causal compute tiles”加权重定向。此复现跟随发布实现，同时分别报告 compute-tile、group 和 causal cell coverage，避免混称。

### 发现与修复

1. 原代码按 token/head 在 `head_dim` 上取 scale；已改为论文的 Q=`128×d`、K=`64×d` block/head scale。
2. 原代码把 attention compute tile 与量化 block 混为同一尺寸；已拆分为 compute `64×64` 与 quant Q128/K64。
3. 原“远历史优先”只声称 SpTrans-inspired，并不满足论文公式；已移植作者发布代码的 stride/tail 构造与 seed-42 weighted retarget。256-token 下四种 route 与作者 `precision_maps.py` 逐 bit 完全一致。
4. 原路由按 query head 分散决策；已改为二维模板一次打包并广播到全部 heads，符合主实验跨层/batch/KV-head 共享设置。
5. 原实现仅持有 bool route；已加入每行最多 64 bit 的实际 pack 与 shift-and-mask 解码。
6. 原实现物化完整 score 后统一 softmax；已改为逐 key tile 更新 running max、normalizer 和 output accumulator。
7. 原 coverage 只报 causal cell 比例；已新增发布实现采用的 weighted compute-tile coverage与论文口径的合法 group coverage。
8. 原真实验证只抽取第 0 层 Q/K/V；已接入 Transformers AttentionInterface，使 28 个 Qwen3 attention 层全部执行 TileMix，并验证 logits 和生成。
9. 生成验证显式传入 attention mask；cosine 改用最后 token 的 FP64 汇总，避免超大 logits 张量 FP32 归约产生越界伪值。

### 功能验证结果

环境：macOS Apple ARM64 CPU；CUDA 不可用，MPS 不可用。Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0、accelerate 1.10.1、sentencepiece 0.2.2。模型和 tokenizer 从 Hugging Face 本机完整缓存离线读取；参数量 596,049,920。

- `py_compile`：退出码 0。
- 小张量：Q/K block scale、INT8 code shape/range、bitmask pack/unpack、256-token SpTrans route/权重断言全部通过。
- synthetic demo：退出码 0，四种 coverage 均为有限输出，`validation=PASS`。
- 作者源码交叉验证：256-token、25/50/75/100% 四张 route map 逐 bit 全部相等。
- 真实第 0 层：退出码 0，墙钟 2.09 秒。

| 请求 INT8 | compute-tile | group | causal cell | MAE vs FP | 最大绝对误差 | cosine |
|---:|---:|---:|---:|---:|---:|---:|
| 25% | 20.00% | 20.00% | 18.77% | 0.00392395 | 0.75334632 | 0.99043697 |
| 50% | 50.00% | 50.00% | 56.13% | 0.00633146 | 0.87165737 | 0.98519725 |
| 75% | 80.00% | 80.00% | 75.10% | 0.01891557 | 1.14493275 | 0.94303238 |
| 100% | 100.00% | 100.00% | 100.00% | 0.01960222 | 1.14493275 | 0.94119197 |

整模命令退出码 0，墙钟 4.41 秒。全精度基线前向 0.338 秒，Python TileMix 参考前向 1.091 秒；这是 CPU 功能耗时，不可与论文 A100 throughput 比较。28 层首次前向调用 28 次，随后单 token 生成累计调用 56 次；50% 请求得到 compute-tile/group 50.00%、causal cell 56.13%，全 logits MAE `0.39474556`、最大绝对误差 `10.10273170`、最后 token cosine `0.99682709`，生成 token 30440（`可`）。

**真实 Qwen3-0.6B：已跑通。** 状态仅表示真实权重下全部 28 层的 TileMix prefill 数值路径、量化、共享 softmax、前向和单 token 生成已执行成功；生成使用 `use_cache=False`，不代表论文的 INT8 KV-cache decode 接口已复现。算法不需要校准；该参考实现不支持保存/导出量化权重，因为 TileMix 量化的是每次 attention 调用的 Q/K 激活而非持久化模型权重。
