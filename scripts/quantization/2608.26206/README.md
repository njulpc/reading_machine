# Ankhdjet（arXiv:2608.26206）Qwen3-0.6B 验证

脚本把真实 Qwen3-0.6B 的浮点权重作为显式 QAT-master 工程输入，执行 b1.58 absmean 三值化；将首个 `q_proj` 转成 Ankhdjet 的 `W[input, output]` 方向，按 64×256 宏切块，写出 `+/-/0` `.wmat`、padding、SHA-256 摘要和 manifest，并用 row-sequential、one-hot wordline、8-bit bit-serial NOR oracle 验证 MVM。默认还对全部 196 个 Transformer Linear 做三值 fake quant，执行整模前向与单 token 生成；`lm_head` 按论文契约留在 fabric 外。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py \
  --output-dir /private/tmp/ankhdjet_masks
```

不传 `--output-dir` 时掩膜工件在临时目录中完成写入/读回后删除。`--no-full-model` 可只验证编译核心。

## 代码审查与验证（2026-08-29）

**算法一致性：部分一致。** 已对照 arXiv v1 官方 PDF/HTML及作者公开仓库。论文前端只自动接受 packed uint8、严格三值浮点或 group-scaled 三值检查点；非三值 master weight 必须显式请求 absmean，且论文证明这样转换旗舰 BitNet master weight 仍有约 1.5% 位置不同。Qwen3-0.6B 不是三值检查点，因此本脚本只代表明确标注的工程迁移，不是论文 BitNet 2B4T 的 bit-exact 编译。

本次修复：删除把普通 2-bit byte packing 冒充 mask program 的实现；补齐论文/作者源码的 `W[input,output]` 方向、64×256 macro tiling、ragged zero padding、`+/-/0` `.wmat`、chunk digest/manifest、逐块读回，以及硬件顺序 bit-serial NOR MVM 对 dense integer MVM 的精确校验。全模型路径覆盖浮点模型加载、显式三值化替换、量化后 logits 与生成；掩膜导出覆盖完整首个 `q_proj`，没有把局部导出写成全模型 GDS。

实际环境为 Apple M4（10 核、16 GB）arm64 CPU，Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6、safetensors 0.7.0；CUDA/MPS 均不可用。上述命令退出码 0，墙钟 6.34 秒。首个 `q_proj` 为 2,097,152 权重，零比例 0.337381，产生 128 个 64×256 宏、2,105,344 bytes `.wmat`，无 padding；所有 chunk round-trip 和 NOR MVM 均逐项一致。整模替换 196 个 Linear / 440,401,920 权重，logits MAE 为 3.32106161，量化后单 token 生成成功。

**真实 Qwen3-0.6B：已跑通（显式 absmean 工程迁移、整模三值前向/生成；首个 q_proj 的真实 mask 编译与导出）。** 未跑通论文的原生三值 checkpoint 全模型 mask bundle、SystemVerilog/Verilator、KLayout DRC、netgen LVS、OpenROAD/LibreLane、STA、寄生能耗或硅后测量；论文 0.98–1.73 pJ 是 130 nm 读原语的寄生仿真，不是本脚本测量。
