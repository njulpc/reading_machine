# APT（arXiv:2608.25380）Qwen3-0.6B 验证

脚本把 APDT 的数值代理注册到真实 Qwen3-0.6B 全部 28 层 attention：先由参考概率按论文逐头标准差公式形成 pruning/precision thresholds，再对保留边执行 6/12-bit 对称量化的 QK 与 PV 路径，完成整模前向、KV-cache 单 token 生成并汇总实际边稀疏率和有效位宽。

```bash
PYTHONPATH=/private/tmp/quant_review_pydeps_20260826 python3 demo.py
```

## 代码审查与验证（2026-08-28）

**算法一致性：部分一致。** 已对照官方 arXiv v1 PDF §3.1–3.2 与图 5/16。旧版使用概率 quantile、INT4/INT8 V-only，既不符合 `threshold_h(t)=alpha*(sigma_h(t)-sigma_h,min)/(sigma_h,max-sigma_h,min)+beta`，也与论文最终 6/12-bit 配置不符；现已修正为双组 `(alpha,beta)`、quant threshold 严格高于 prune threshold、6/12-bit symmetric uniform QK/PV 和全层 attention 替换。

真实运行退出码 0、墙钟 2.48 秒；prefill + generate 共 56 次 attention 调用，保留边 0.90654452、高精度边 0.57135107、保留边有效位宽 9.78150916；相对原模型 logits MAE 2.21907687、cosine 0.60946572，生成“我”。这是明确的负面迁移结果，说明为 DiT 调好的 APDT 不能直接按默认工程阈值迁移到 Qwen。

**真实 Qwen3-0.6B：已跑通（全 28 层 6/12-bit attention 数值代理、前向与缓存生成）。** 论文方法对象是 PixArt-α/SD3/FLUX 的跨 timestep DiT；Qwen 没有 diffusion timestep。脚本用当前概率作 oracle mask，不具备论文的离线多 timestep `sigma_min/max`、前一步 mask reuse、7–10 步/5%–10% refresh、TAFA normalization-statistics 预测、tile-accurate scale 或 SD-MPU。因此论文完整 APT：未跑通，不能声称复现 8.16×/14.98×。
