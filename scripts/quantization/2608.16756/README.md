# 2608.16756 BinRVR / DAB-Conv Qwen3-0.6B 复现

脚本把 DAB-Conv 的 distribution-aware scale 思想迁移到 Qwen3-0.6B `gate_proj`：权重与激活均为 1-bit sign；小型 ScaleNet 根据每个输入通道的 mean、absolute mean、std 学习激活尺度，并与只用 absolute mean 的基线比较校准输出 MSE。

```bash
python demo.py --model-dir /path/to/Qwen3-0.6B/snapshot --steps 100
```

该验证使用真实 Qwen 权重与 64 个校准激活。它不包含 RAW 视频、卷积、BIIM 或 recurrent window，因此只声称复现 DAB 的多统计量尺度机制。

**2026-08-19 实测**：absolute-mean scale MSE `0.280924`，100 步 distribution-aware 校准后 `0.280409`；语法检查通过。
