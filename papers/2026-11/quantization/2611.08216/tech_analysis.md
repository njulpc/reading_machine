# ProQuant: Progressive Quantization-aware Training for Edge MLLMs

> arXiv: 2611.08216；v1：2026-11-05T16:04:31+00:00（UTC） / 2026-11-06T00:04:31+08:00（北京时间）。
> 分类：Computer Vision and Pattern Recognition (cs.CV) ; Computation and Language (cs.CL)。归档以 v1 北京时间月份为准。
> 证据：[官方摘要与提交历史](https://arxiv.org/abs/2611.08216)；[官方HTML全文](https://arxiv.org/html/2611.08216v1)。以下论文结果均为作者报告，本地结果另行标注。

## 1. 核心速览

**研究主题**：quantization / ProQuant。

**一句话总结**：ProQuant先用模型自生成标签对齐数据分布，再优先量化视觉敏感层；W4A8 Qwen3-VL-2B均分72.54，距BF16为1.09个百分点。

## 2. 研究背景与动机

小型MLLM在低比特下跨模态理解比语言先验更易失效。有限微调语料的标签风格又可能偏离待量化模型分布，直接QAT同时修复两种能力会使优化更困难。论文把训练目标数据与量化层激活次序联合设计。

## 3. 核心方法与创新点

1. Self-Relabeling：丢弃原响应，用待量化模型对原图文prompt重新随机采样。Qwen3-VL-2B参数temperature0.7、top_p0.8、top_k20、最长512tokens，避免greedy标签缺少多样性。
2. 视觉敏感度 `τ_i = mean_visual ||G_i(token)||_1 / mean_all ||G_i(token)||_1`，G为block输出梯度。优先为高τ层启用量化，让视觉理解先恢复。
3. Algorithm1在总训练步0%、30%、40%、50%启用约50%、75%、88%、100% blocks；其余层暂时高精度，后半程做全部量化恢复。
4. 静态per-channel对称权重量化、动态per-token对称激活，STE处理round；学习原权重及scale。式A2为α KL(Ps||Pt)+(1−α)KL(Pt||Ps)+βCE(Y_SRL,Ps)。冻结ViT，其余模块QAT；α初始估计，β调到相近损失量级。

## 4. 实验设计与结果

LLaVA-680K重标注后训练5epochs，单节点8×H200、per-device batch32、accumulation2、最大长度8192、AdamW、zero decay、clip grad1.0。2B模型SRL约2.5GPU-days，QAT约2GPU-days。

表1：Qwen3-VL-2B七任务均分BF16 73.63、LLM-QAT W4A8 65.94、ProQuant72.54：提升6.60个百分点、距BF16低1.09点。W4A4 ProQuant59.83，仍比BF16低13.80点；该结果含SmoothQuant初始化，附录A1未初始化仅50.87。LLM-QAT W4A4对照27.29还保留down_proj激活8bit，须标明混合精度。扩展到InternVL3.5-1B与LLaVA-OV-0.5B，W4A8分别63.93/52.29，仍低于BF16 69.92/57.95。

芯片效率来自22nm测试芯片实测与DRAMPower仿真组合，decode约3.74–3.98倍加速，不是整套设备墙插能耗。理论16/4=4倍只适用被量化权重有效载荷，ViT、scale、其他buffer未计。

**本地组件验证**：`scripts/quantization/2611.08216/`实现SRL、可学习scale、式A2、式1、PBA调度，使用真实Qwen3-0.6B做2提示、10步、前2block W4A8 QAT；实际280.32秒完成；5项数值/梯度断言及10步有限损失检查通过。最终两个训练样本forward KL为0.02160/0.01550（无held-out任务结论）。日志及结果JSON给出真实损失。视觉公式用小张量验证，文本运行明确使用prompt-token代理，不宣称等价于视觉敏感度。

## 5. 局限性与未来展望

Qwen3-0.6B没有视觉token，无法在该指定模型上复现论文的多模态恢复机制；本地是标明边界的文本组件适配，不是完整ProQuant复现。没有图像语料/8×H200规模训练、打包低比特内核或held-out多模态评测。SRL可能继承原模型错误，少数幻觉/偏见测试不能保证全部域安全；视觉与语言敏感度排序的跨架构稳定性仍需验证。

## 6. 学术启发

QAT层次调度可以按能力脆弱性设计，而非统一按层号或权重幅度。复现前先核对目标模型是否具备方法依赖的模态；缺失视觉输入时应保留公式单测并公开适配差异。量化实验还应同时记录教师生成成本、训练成本及真实硬件计量边界。

**四维评分（1–10，编辑判断而非客观排名）**：精度效果 8/10；压缩倍率 8/10；创新性 8/10；可复现性 6/10。

精度8：跨小型MLLM和多个基准，W4A4仍明显落后BF16；压缩8：4bit权重理论有效载荷4倍但ViT等仍BF16；创新8：视觉敏感度驱动渐进QAT；复现6：真实Qwen文本组件训练通过，视觉机制受指定纯文本模型约束未验证。
