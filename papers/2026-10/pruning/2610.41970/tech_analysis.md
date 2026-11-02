# When Does Test-Time Search Help World Action Models? An Empirical Audit of Candidate Selection and Simulator Integrity

- arXiv：[2610.41970](https://arxiv.org/abs/2610.41970)；[官方 HTML v1](https://arxiv.org/html/2610.41970v1)
- v1 实际提交：2026-10-30T16:21:07+00:00（UTC）；2026-10-31T00:21:07+08:00（Asia/Shanghai）。
- 官方分类（主分类在前）：Artificial Intelligence (cs.AI)
- 压缩归类：pruning。证据为官方摘要与上述全文方法、实验及相关附录；以下数字均为论文报告，非本机复现。

## 1. 核心速览

研究主题：pruning / When Does Test-Time Search Help World Action Models? An Empirical Audit of Candidate Selection and Simulator Integrity。

一句话总结：Cosmos Policy 的token剪枝虽减少47.9%单前向FLOPs，部署整路径仅快1.152×，且该测量未验证剪枝动作质量。

## 2. 研究背景与动机

机器人world-action模型的test-time scaling依赖候选差异、选择器信号、真实速度及模拟器可靠性。仅展示FLOPs削减或成功率波动，会把不可利用的候选差异和渲染错误当作优化收益。本文是剪枝效率审计，不是已完成质量验证的部署压缩方案。

## 3. 核心方法与创新点

1. **预先验证前提**：固定候选与continuation policy，snapshot replay测量每个候选结局，以hindsight oracle给出不可部署的选择上限。
2. **整帧token剪枝测时**：依次去除未来图像、未来帧及value token，分别实测部署完整路径和去掉future-image decode的路径；不把组件耗时相加冒充端到端值。
3. **统计与完整性**：预注册门槛，按state/episode分别bootstrap，并用power gate判断是否值得继续实验。检测OpenGL上下文导致的静默渲染损坏；修复针对具体栈，不是所有模拟器的通解。

## 4. 实验设计与结果

主表1和补充表3：Cosmos Policy/RoboCasa，RTX A6000、BF16 eager、batch1、5个denoising步骤，每格30次计时。2156→1176 tokens，单前向8.535→4.446 TFLOP，减少47.9%。完整路径1254.9→1088.9ms，1.152×；排除future-image decode后812.7→648.6ms，1.253×，均未到预注册1.5×目标。注意百分比省时应按时间差计算，不能把1.152×误写为省时15.2%。

该测时把被删帧输出置零，**没有评测剪枝后的动作质量**。候选审计263个states中215个无结局变化，只有20个(7.6%)稳定可分；value selector比随机低1.66个百分点，oracle仅高1.40且episode置信区间跨零。

## 5. 局限性与未来展望

结论限定Cosmos Policy/RoboCasa及此eager路径，不能推广到所有world models。剪枝实验是latency-only；自适应分配受power gate限制，结论不确定。无质量保持压缩率可报告。本轮未运行机器人模拟、修复或剪枝测时。

## 6. 学术启发

压缩收益须经过“算子→完整请求→控制质量”的逐层验证。部署含VAE编解码等固定成本，先测分解再选压缩对象；预注册与渲染完整性检查应早于昂贵的闭环扩展实验。

评分（1–10）：精度效果3，压缩倍率/资源削减4，创新性8，可复现性8。

准确率3：剪枝动作质量未评测；压缩4：FLOPs减半但端到端仅1.152×；创新8：前提优先的负面审计；复现8：硬件、计时与统计细节明确，本轮未执行。

本轮为非量化论文精读，未执行论文训练或运行时基准；可复现性评分衡量公开方法的可操作程度，不表示本轮已复现。分析日期：2026-11-03。
