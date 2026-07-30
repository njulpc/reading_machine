# Paper: 2605.00422

**BWLA: Breaking the Barrier of W1AX Post-Training Quantization for LLMs**

复现内容：1-bit 权重二值化 + 6-bit 激活 PTQ。OKT（论文为 EM 学习的正交映射，此处用 Hadamard 混合作轻量近似）+ PSP（秩-8 SVD 残差补偿）。

验证方式：使用真实 Qwen3-0.6B 权重（model.layers.5.mlp.down_proj.weight，经 ModelScope 下载）；对比 RTN 二值化基线的权重相对误差与 W1A16/W1A6 输出相对误差。实测 BWLA(OKT+PSP) 将 W1 权重误差从 0.397 降至 0.349。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
