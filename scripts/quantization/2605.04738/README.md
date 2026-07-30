# Paper: 2605.04738

**OSAQ: Outlier Self-Absorption for Accurate Low-bit LLM Quantization**

复现内容：基于 Hessian 零空间的加性权重异常值抑制。估计 H=X^T X，取零空间基，岭回归构造加性变换抑制各行异常值，输出域贪心接受。

验证方式：真实 Qwen3-0.6B 权重 + 低秩协方差校准激活（使 Hessian 存在真实零空间，模拟论文关键观察）。实测 474/512 行被接受，W4 RTN 输出相对误差从 0.0199 降至 0.0123，且 |(dW)x| 在校准集上约等于 0（零空间性质成立）。

权重文件获取方式（可选）：`curl -L -o qwen3-0.6b.safetensors https://modelscope.cn/models/Qwen/Qwen3-0.6B/resolve/master/model.safetensors`，放置于仓库 `_work/` 目录或通过环境变量 `QWEN3_WEIGHTS` 指定路径；未提供时 demo 自动使用 mock 权重/激活并完整跑通全部代码路径。

运行: `python3 demo.py`
