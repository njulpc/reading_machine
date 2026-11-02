# Any Forcing: Any-Step Generality and One-Step Stability for Autoregressive Video Generation

- arXiv：[2610.42031](https://arxiv.org/abs/2610.42031)；[官方 HTML v1](https://arxiv.org/html/2610.42031v1)
- v1 实际提交：2026-10-30T16:56:42+00:00（UTC）；2026-10-31T00:56:42+08:00（Asia/Shanghai）。
- 官方分类（主分类在前）：Computer Vision and Pattern Recognition (cs.CV)
- 压缩归类：knowledge_distillation。证据为官方摘要与上述全文方法、实验及相关附录；以下数字均为论文报告，非本机复现。

## 1. 核心速览

研究主题：knowledge_distillation / Any Forcing: Any-Step Generality and One-Step Stability for Autoregressive Video Generation。

一句话总结：Any Forcing 联合步间一致性、首帧增强和历史缓存选择，稳定少步自回归视频生成。

## 2. 研究背景与动机

将多步扩散压到单步后，第一帧不稳定会污染后续条件，长视频还会因有限历史和位置外推发生漂移。本文同时处理蒸馏训练目标和有限缓存选取，不把单步质量问题完全归因于生成器容量。

## 3. 核心方法与创新点

1. **统一判别器**：复用fake-score特征，三个分类头分别做real alignment、不同采样步数间consistency alignment和首帧enhancement；步间正样本为同噪声下更多一步的stop-gradient输出。
2. **蒸馏稳定化**：DMD损失叠加统一对抗损失；前200步用冻结教师ODE终点MSE，权重0.05。学生从Causal Forcing ODE checkpoint初始化，训练1000步，每次生成器更新配5次fake-score更新。
3. **长程记忆**：从干净历史状态比较全局sink相关性和近期value贡献，候选须同时通过两项才替换最低相关的记忆；重映射RoPE位置时保持时间顺序。配置为3个sink、2个长期记忆、1个近期上下文帧。
4. **运行设置**：16×A100、有效batch64，AdamW beta=(0,0.999)，生成器lr2e-6，fake-score/heads为4e-7；EMA从200步开始，0.99。

## 4. 实验设计与结果

表1–4：480p、5秒视频，1*表示首latent帧4步，后续1步；1†为首帧2步。因此不能把整段都称“一次前向”。Any Forcing在1*的VBench Total85.06，对照One Forcing84.35、Causal Forcing83.06；2步84.89，4步85.09。30/60秒、1*分别84.56/84.46。

删去首帧增强，1* Total从85.06降至83.52；删real alignment降至83.78，说明改进来自多组件。短长视频实测吞吐分别20.9/24.7 FPS，单H100；主比较946 prompts、每prompt五次独立采样，长视频消融只128 prompts。

## 5. 局限性与未来展望

50步基座到后续单步的名义NFE变化，不等于50×整体加速；首帧仍多步，VAE与缓存开销仍存在。固定记忆可能损失稀有远程事件；训练依赖ODE轨迹和多GPU。未执行视频蒸馏或GPU吞吐复测。

## 6. 学术启发

当压缩引入递归误差时，应把“初始条件质量”列为单独干预变量。记忆选择必须避免使用纯噪声当前query作为可靠信号；可把首帧预算与后续帧预算分开优化。

评分（1–10）：精度效果8，压缩倍率/资源削减8，创新性7，可复现性7。

准确率8：短长视频与消融支撑；压缩8：少步生成和有界历史，FPS可核验；创新7：统一判别任务与记忆选择；复现7：配置清楚但训练资源重。

本轮为非量化论文精读，未执行论文训练或运行时基准；可复现性评分衡量公开方法的可操作程度，不表示本轮已复现。分析日期：2026-11-03。
