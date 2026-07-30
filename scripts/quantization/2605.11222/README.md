# Paper: 2605.11222

**ADMM-Q: An Improved Hessian-based Weight Quantizer for PTQ of LLMs**

复现内容：共识形式组合 ADMM：W 连续更新（锚定 FP 层输出的 Hessian 预条件最小二乘）+ Z 网格投影 + 对偶上升 + 罚因子调度（rho×1.6）。

验证方式：真实 Qwen3-0.6B 权重，3-bit group=128。实测 ADMM-Q 输出重构相对误差 0.0933，优于 RTN 的 0.1344（3-bit 激进位宽下改善明显，与论文趋势一致）。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
