# Paper: 2605.17757

**OSCAR: Offline Spectral Covariance-Aware Rotation for 2-bit KV Cache Quantization**

复现内容：离线注意力加权协方差估计 C=Σ p_i k_i k_i^T，构造'去相关+能量重散布'固定旋转（Hadamard×特征基）+ 旋转域逐通道裁剪阈值，INT2 KV 量化；GQA 头结构（16Q/8KV，head_dim=128）下的注意力误差评估。

验证方式：真实 Qwen3-0.6B q/k/v_proj 权重 + 通道异常值隐藏状态。三方对比：逐通道裁剪是主要增益来源（attn-err 1.20→1.09），协方差对齐旋转在此代理设定下与 Hadamard 相当（论文的大幅增益出现在真实长推理 KV 分布上，本代理无法完全复现，如实注明）。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
