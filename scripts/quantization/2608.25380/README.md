# APT（arXiv:2608.25380）Qwen3-0.6B 验证

脚本在真实 Qwen3-0.6B 首层捕获 prompt hidden states，使用真实 Q/K/V projection 重建 causal attention。随后按论文 APDT 的双阈值思想：低概率边剪除，中概率边使用 INT4 V，高概率边使用 INT8 V，并报告实际稀疏率、有效位宽与 attention output relative-L2。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

验证边界：论文对象是 DiT、跨 timestep 的 TAFA 预测和专用双精度稀疏加速器；Qwen 没有 diffusion timestep，脚本仅真实验证 APDT 的联合 mask/precision 数值路径。没有声称复现 A100 的 8.16× 或 14.98× 能效，也没有伪造定制硬件。

本次实跑：真实 12-token、16-head、head-dim 128 attention 中保留 27.0833% 边，高精度边占 8.1597%，保留边有效位宽 5.205128 bit；相对全精度 attention output 的 relative-L2 为 0.37098974。该误差说明默认阈值较激进，结果保留为真实限制。
