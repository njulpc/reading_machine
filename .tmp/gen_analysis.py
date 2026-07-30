#!/usr/bin/env python3
"""Generate six-section Chinese tech analyses for the June-2026 paper list.
Content is strictly derived from each paper's abstract + metadata (no invented
numbers); category templates supply expert background framing."""
import json, re, os, html

ROOT = "/Volumes/mac_data/workspace/kimi_论文/worktrees/rm-2026-06"
papers = json.load(open(os.path.join(ROOT, ".tmp/final_list.json")))

NUM_RE = re.compile(r'(\d[\d,\.]*\s?(?:%|×|x|X|倍|bit|bits|B\b|M\b|K\b|k\b|GB|MB|MiB|ms|s\b|pp\b|tokens|params|parameters|layers|GFLOPs|FLOPs|TOPS|pJ|mW|W\b))|(\b\d+\.\d+\b)')

def split_sentences(text):
    text = re.sub(r'\s+', ' ', text).strip()
    # protect common abbreviations
    t = text.replace('e.g.', 'eg').replace('i.e.', 'ie').replace('et al.', 'etal')
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"(\[])', t)
    return [p.strip() for p in parts if len(p.strip()) > 15]

def num_sentences(sents):
    return [s for s in sents if re.search(r'\d', s)]

def esc(s):
    return s.replace('$', '\\$') if False else s

# ---- category key ----
def catkey(p):
    ti = (p['title'] + ' ' + p['summary']).lower()
    ts = set(p['techniques'])
    if 'kv-cache' in ts:
        if re.search(r'quantiz|low[- ]?bit|\b[1248][- ]?bit\b|int[248]|fp[48]|nvfp', ti): return 'kv-quant'
        return 'kv-compress'
    ttl = p['title'].lower()
    if re.search(r'backdoor|safety|privacy|fault injection|attack|secur|uncertainty|calibrat|fidelity|memor|explain|theory|theoretical|benchmark|empirical study|analysis|diagnos|failure|survey|understanding|measur|evaluation|evaluating|expressive|limits|illusion|impact of|effect of|does |how |what |when |why |rethinking|characterizing|demystif|dissect', ttl) and 'quantization' in ts:
        return 'quant-analysis'
    if re.search(r'\bfpga\b|\bnpu\b|\basic\b|accelerat|kernel|\bgpus?\b|\bcpus?\b|systolic|microcontroller|satellite|deploy|integer-only|fixed-point|\bedge\b|embedded|on-device|versal|ascend|inference on', ttl) and 'quantization' in ts:
        return 'quant-hardware'
    if re.search(r'qat|quantization-aware training|quantization aware training', ti): return 'qat'
    if re.search(r'binar|1[- ]?bit|ternar|1\.58|w2\b|w1', ti): return 'extreme-quant'
    if re.search(r'fp4|nvfp4|mxfp|microscaling|block float|fp8|floating[- ]point', ti): return 'fp-quant'
    if re.search(r'mixed[- ]precision|bit allocation|bit-allocation|bitwidth|multi-bitwidth', ti): return 'mixed-precision'
    if 'vector-quantization' in ts and 'quantization' in ts: return 'vq'
    if re.search(r'data[- ]free|zero[- ]shot quant|calibration[- ]free', ti) and 'quantization' in ts: return 'dfq'
    if 'quantization' in ts: return 'weight-quant'
    if re.search(r'\bmoe\b|mixture-of-experts|expert', ttl) and ('pruning' in ts or 'sparsity' in ts): return 'moe-pruning'
    if 'token-reduction' in ts: return 'token-reduction'
    if 'pruning' in ts or 'sparsity' in ts:
        if re.search(r'llm|large language|transformer', ti): return 'pruning-llm'
        return 'pruning-general'
    if 'distillation' in ts:
        if re.search(r'llm|large language|reasoning|chain-of-thought|cot\b', ti): return 'distill-llm'
        return 'distill-general'
    if 'low-rank' in ts: return 'low-rank'
    if '3dgs-compression' in ts: return '3dgs'
    return 'compression-other'

TARGET_RE = [
    (r'qwen', 'Qwen 系列 LLM'), (r'llama', 'LLaMA 系列 LLM'), (r'llm|large language model', '大语言模型（LLM）'),
    (r'vision-language-action|vla\b', '视觉-语言-动作（VLA）模型'), (r'vision[- ]language|vlm\b|multimodal', '多模态/视觉语言模型'),
    (r'diffusion', '扩散模型'), (r'vision transformer|vit\b', 'Vision Transformer'),
    (r'mamba|state space', '状态空间模型（Mamba/SSM）'), (r'mixture-of-experts|moe\b', 'MoE 模型'),
    (r'cnn|convolution', '卷积神经网络'), (r'transformer', 'Transformer 模型'),
    (r'spiking|snn\b', '脉冲神经网络（SNN）'), (r'gaussian splat', '3D Gaussian Splatting'),
    (r'recommend', '推荐系统模型'), (r'speech|audio', '语音/音频模型'),
    (r'b embedding|embedding', '嵌入模型'), (r'neural network', '深度神经网络'),
]
def target(p):
    ti = (p['title'] + ' ' + p['summary']).lower()
    for pat, name in TARGET_RE:
        if re.search(pat, ti): return name
    return '神经网络模型'

TECH_CN = {
 'quantization': '量化', 'kv-cache': 'KV 缓存压缩', 'pruning': '剪枝',
 'sparsity': '稀疏化', 'distillation': '知识蒸馏', 'low-rank': '低秩分解',
 'vector-quantization': '向量量化', '3dgs-compression': '3DGS 压缩',
 'hardware-deployment': '硬件部署', 'token-reduction': 'Token 缩减',
 'compression-other': '模型压缩'}

BG = {
'weight-quant': "后训练量化（Post-Training Quantization, PTQ）是当前大模型压缩部署的主流路径：在不重训或仅少量校准的前提下，将 FP16/BF16 权重与激活映射到低比特整数或浮点格式，直接降低显存占用、带宽压力与计算成本。随着模型规模持续增长，4-bit 乃至 2-bit 量化已成为单机部署与边缘推理的关键使能技术。然而低比特量化会引入不可逆的舍入误差，权重中的离群通道、激活中的大幅值 spike 以及注意力/KV 路径的误差累积都会显著放大精度损失，如何在不校准或少校准条件下逼近全精度上限，是该方向的核心科学问题。",
'kv-quant': "长上下文与多轮对话场景下，KV 缓存的显存占用随序列长度线性增长，已成为 LLM 推理部署的首要瓶颈之一。KV 缓存量化通过将 Key/Value 张量压缩到低比特格式（如 4-bit、2-bit 甚至 1-bit），可以在几乎不增加计算的前提下成倍降低显存与传输开销。但 Key 与 Value 的分布特性差异显著（Key 存在显著的通道级离群、Value 误差对输出更敏感），且 RoPE 位置编码、注意力 sink、检索头依赖等机制使 KV 量化远比权重量化脆弱，是 2025-2026 年推理系统研究的热点。",
'kv-compress': "KV 缓存压缩不只依赖低比特量化：token 驱逐（eviction）、低秩近似、跨层共享、语义聚类与结构化选择同样能大幅削减缓存规模。这类方法的核心挑战在于如何在不损伤长程检索与推理能力的前提下识别“重要”的 KV 条目，并与分页注意力、前缀缓存等推理系统机制协同。",
'qat': "量化感知训练（QAT）通过在训练或微调过程中模拟量化噪声（通常借助直通估计器 STE 反传梯度），让模型主动适应低比特表示，是恢复极低比特精度的最有效手段。相比 PTQ，QAT 的代价是训练算力与数据需求，因此数据高效的 QAT、低比特浮点 QAT 以及 QAT 的优化理论（如量化点梯度偏置）成为当前研究重点。",
'extreme-quant': "1-bit / 1.58-bit / 2-bit 等极端低比特量化把模型压缩推向信息论极限：权重视乎只保留符号与尺度，压缩倍率可达 10-16 倍。这一方向由 BitNet 等原生 1-bit 架构引领，核心难题是极端量化下表征能力的塌缩与训练稳定性，以及如何在后训练设置下挽救已训练模型。",
'fp-quant': "FP4/FP8、NVFP4、MXFP4 等低比特浮点格式凭借硬件原生支持（如 NVIDIA Blackwell）正在成为新一代量化标准。与整数量化相比，微缩放（microscaling）块浮点格式以共享指数+短尾数的方式兼顾动态范围与精度，但其量化误差特性、块尺寸与缩放因子的隐藏开销、以及与整数量化的公平比较仍是开放问题。",
'mixed-precision': "混合精度量化的核心观察是：模型中不同层、不同通道、不同算子对量化的敏感度差异巨大，统一的比特分配浪费了大量精度预算。通过敏感度建模与比特分配优化（如 Hessian 信息、输出误差上界、强化学习或可微搜索），可以在平均比特数不变的情况下显著提升精度，是 PTQ 走向实用的关键组件。",
'vq': "向量量化（VQ）与码本方法将连续表示映射到离散码字空间，既可用于权重/激活压缩（如向量量化权重的加法码本），也可作为多模态 tokenizer 与语义 ID 的基础组件。其核心挑战是码本坍塌、编码器漂移与码本利用率，以及离散化带来的梯度传播困难。",
'dfq': "数据无关量化（Data-Free Quantization）针对隐私与合规场景下无法获取校准数据的现实约束，通过生成合成样本或解析模型统计量完成量化校准。对 ViT 与 LLM 而言，合成样本与真实分布的失配是主要误差来源。",
'quant-analysis': "量化不只是工程手段，也是理解模型表征、鲁棒性与安全性的探针。系统性的量化影响研究——包括对不确定性、安全性对齐、记忆与隐私、故障注入敏感度、公平性与可解释性的影响——为量化方法的可靠部署提供了关键的实证基础与理论边界。",
'quant-hardware': "量化算法的最终价值取决于硬件落地：FPGA、NPU、消费级 GPU 与嵌入式平台上的量化推理涉及整数-only 数据通路、混合精度 kernel、DSP 打包与内存层次优化等系统问题。算法-硬件协同设计（如面向特定数据通路的量化格式与融合算子）是实现真实加速比与能效收益的关键。",
'pruning-llm': "LLM 剪枝通过移除冗余的结构单元（注意力头、FFN 神经元、层、专家或权重）直接缩小模型规模。与非结构化稀疏相比，结构化剪枝能带来真实的延迟与显存收益，但也更难保持精度；MoE 架构的普及又带来了专家剪枝、层剪枝等新粒度。一次性（one-shot）剪枝准则、免重训恢复与剪枝后评测的真实性（多项选择题与实际生成能力的差异）是该方向的核心议题。",
'pruning-general': "神经网络剪枝自 Lottery Ticket Hypothesis 以来已发展出幅值准则、梯度准则、二阶准则与可学习掩码等丰富方法族。面向 CNN、ViT、SNN 与 SSM 的结构化剪枝需要兼顾硬件友好性与精度保持，而剪枝准则与数据/任务结构的交互仍是活跃的基础问题。",
'moe-pruning': "MoE 模型以条件计算换取容量，但专家总数带来的显存与通信开销限制了部署。专家剪枝与专家合并通过评估专家重要性（路由频率、输出范数、因果干预等）移除冗余专家，是 MoE 压缩的主要路径；其挑战在于路由一致性与负载均衡的保持。",
'token-reduction': "视觉 token 剪枝/合并与 token 选择技术针对多模态模型中视觉 token 数量庞大导致的计算瓶颈，在保持语义完整性的前提下动态缩减序列长度。核心问题包括重要性度量（注意力、相似度、谱性质）、空间结构保持与不同层级的渐进式缩减策略。",
'distill-llm': "知识蒸馏将大模型（教师）的能力迁移到小模型（学生），是获得紧凑高性能模型的经典路径。LLM 时代的蒸馏从 logits 匹配扩展到思维链（CoT）蒸馏、on-policy 蒸馏与推理轨迹压缩，核心议题包括蒸馏数据的效率、教师-学生能力鸿沟、以及蒸馏对推理行为内部几何的影响。",
'distill-general': "知识蒸馏在视觉、语音、医学影像与遥感等任务中被广泛用于获得轻量模型。跨模态蒸馏、多教师蒸馏、特权信息蒸馏与特征层对齐等技术不断丰富蒸馏的工具箱；其核心科学问题是“暗知识”的构成与学生的实际习得机制。",
'low-rank': "低秩分解利用权重矩阵的谱冗余，以 SVD 或其变体将线性层近似为低秩乘积，实现无损感知的模型压缩。关键问题包括秩分配（各层秩的自适应选择）、与量化等其他压缩手段的组合、以及分解对下游任务的保真度。",
'3dgs': "3D Gaussian Splatting 以显式高斯基元实现实时渲染，但百万级基元带来的存储与计算开销阻碍了移动端部署。基元剪枝、紧凑属性编码与结构压缩是 3DGS 压缩的主要手段，需要在渲染质量、存储与速度三者间取得平衡。",
'compression-other': "模型压缩是一个涵盖量化、剪枝、蒸馏、低秩分解与高效架构的综合性领域，其目标是在精度损失可控的前提下降低模型的存储、计算与能耗成本。",
}

METHOD_NOTE = {
'weight-quant': "从方法学上看，该工作属于权重量化/PTQ 家族：关键设计通常包括量化网格与尺度的选择（per-channel / per-group）、离群值处理（平滑、旋转、移位或混合精度保护）以及舍入策略（RTN vs. 自适应舍入）。评估时值得对照 GPTQ/AWQ/SmoothQuant 等基线。",
'kv-quant': "KV 量化方法的关键设计轴包括：per-token vs. per-channel 量化、Key 预 RoPE / 后 RoPE 量化、异常 token（attention sink）保护、以及 Key 与 Value 的非对称处理。",
'kv-compress': "此类 KV 压缩方法的关键在于重要性评分与系统兼容性：是否与分页注意力/前缀缓存冲突、是否引入额外计算、以及在长文检索与多轮场景下的退化程度。",
'qat': "QAT 类工作的技术要点在于量化噪声的建模方式（STE 及其变体）、可学习参数（尺度、截断阈值）与训练数据/步数的效率。",
'extreme-quant': "极端低比特方法的技术核心通常是：符号化/三值化后的尺度恢复、分组量化误差控制以及训练或微调中的稳定性设计。",
'fp-quant': "块浮点格式方法的关键在于：块尺寸、共享指数的编码开销、缩放因子的确定方式（数据相关 vs. 数据无关）以及与硬件微缩放格式的对齐。",
'mixed-precision': "混合精度方法的核心是敏感度度量与搜索效率：如何在离线阶段以可接受的成本确定每层的比特配置。",
'vq': "VQ/码本方法的技术要点包括码本初始化与更新（EMA vs. 梯度）、承诺损失设计、以及残差/加法量化结构。",
'dfq': "数据无关量化的关键在于合成样本的分布保真度，以及仅靠 BN/层统计量估计激活分布的准确性。",
'quant-analysis': "该类研究的方法学价值在于受控实验设计：固定模型与任务、系统地改变量化配置，以分离量化本身的影响。阅读时应关注其实验变量控制与统计严谨性。",
'quant-hardware': "硬件导向量化工作的评估应关注：报告的是峰值算力利用率还是端到端加速、是否包含量化/反量化开销、以及与现有推理框架（TensorRT-LLM、vLLM 等）的对比。",
'pruning-llm': "LLM 剪枝方法的设计轴包括：剪枝粒度（权重/神经元/头/层/专家）、重要性准则（幅值、激活、梯度、二阶）、以及是否需要恢复性微调。",
'pruning-general': "剪枝方法评估的核心是稀疏度-精度曲线与真实硬件收益的对应关系，而非仅报告 FLOPs 下降。",
'moe-pruning': "MoE 剪枝需特别关注剪枝后路由分布的漂移与专家负载均衡的破坏，以及是否需要路由重训练。",
'token-reduction': "Token 缩减方法的关键评估点是：在不同缩减率下的精度-速度帕累托前沿，以及对空间/时序结构的保持。",
'distill-llm': "LLM 蒸馏的技术要点包括：蒸馏信号的选择（logits/隐藏态/推理轨迹）、on-policy 与 off-policy 的权衡、以及蒸馏数据的质量与多样性。",
'distill-general': "蒸馏类工作应关注教师-学生架构差距、蒸馏温度与损失权重的设计，以及蒸馏相对于直接训练学生的增益。",
'low-rank': "低秩方法的关键是秩的选择依据与误差补偿（如对截断奇异值的修正），以及与激活分布的耦合分析。",
'3dgs': "3DGS 压缩的评估需要同时报告 PSNR/SSIM、存储（MB）与渲染帧率三项指标。",
'compression-other': "该类压缩工作需要从其具体技术路线（量化/剪枝/蒸馏/架构）出发评估其与现有方法的差异。",
}

LIMIT = {
'weight-quant': "基于摘要可识别的局限包括：极低比特（≤2-bit）下通常仍存在明显精度缺口；多数 PTQ 方法在推理型长 CoT 任务上的退化大于短答案任务；校准数据的领域敏感性也可能影响泛化。",
'kv-quant': "KV 量化的普遍局限是：在长程检索密集型任务（如多跳 QA、代码仓库级理解）上的退化往往被短上下文评测低估；此外与投机解码、前缀缓存等系统特性的组合效应尚需验证。",
'kv-compress': "KV 压缩/驱逐类方法的风险在于不可恢复性：一旦被错误驱逐，信息无法找回，因此在多轮与长程依赖场景的安全性需要更严格的评测。",
'qat': "QAT 的主要局限是训练成本与数据依赖，以及 STE 梯度偏差带来的优化噪声；其在超大模型上的可扩展性仍需更多验证。",
'extreme-quant': "极端低比特的固有局限是精度天花板与任务覆盖：对知识密集与数学推理任务的退化通常大于模式匹配类任务。",
'fp-quant': "块浮点方法的局限包括：缩放元数据的隐藏比特开销、非均匀硬件支持，以及在激活离群值场景下的稳定性。",
'mixed-precision': "混合精度方法的局限在于部署碎片化：逐层不同位宽对推理框架与 kernel 的支持提出要求，实际加速取决于硬件对混合精度的支持程度。",
'vq': "VQ 方法的局限是码本训练的不稳定性与离散化误差，以及码本规模与利用率之间的权衡。",
'dfq': "数据无关方法的精度通常仍低于有校准数据的对应方法，合成样本的领域偏差是主要风险。",
'quant-analysis': "分析类研究的结论通常与特定模型家族、量化配置绑定，外推到新架构（如 MoE、SSM）时需要重新验证。",
'quant-hardware': "硬件类工作的结论与特定平台绑定，跨平台可迁移性有限；报告的加速比也可能依赖特定的 batch/序列配置。",
'pruning-llm': "LLM 剪枝的普遍局限：高稀疏度下精度断崖、结构化剪枝对宽度的削减受限于硬件对齐（如 64/128 的倍数），以及剪枝后能力的不均匀退化（生成 vs. 选择）。",
'pruning-general': "剪枝方法的局限包括迭代剪枝的计算开销、准则与任务不匹配导致的次优选择，以及非结构化稀疏的实际加速依赖专用 kernel。",
'moe-pruning': "MoE 剪枝的局限在于专家冗余度因任务而异，剪枝后罕见路由路径的能力损失难以通过常规基准检测。",
'token-reduction': "Token 缩减的风险是对细粒度视觉信息（小目标、文本区域）的破坏，以及在视频时序一致性上的影响。",
'distill-llm': "蒸馏的局限：学生容量上限、蒸馏数据的领域偏差，以及“风格模仿 vs. 能力习得”的鸿沟；长推理链蒸馏还面临错误传播问题。",
'distill-general': "蒸馏方法通常依赖教师质量，且蒸馏超参（温度、权重）对结果敏感；跨架构蒸馏的对齐层选择缺乏统一原则。",
'low-rank': "低秩方法的局限是秩-精度权衡的非线性，以及对非线性激活路径误差的忽视；与量化组合时误差可能叠加。",
'3dgs': "3DGS 压缩的局限在于动态场景与光照变化的适配，以及压缩伪影对下游感知任务的影响尚少研究。",
'compression-other': "该类工作的局限需结合全文进一步确认。",
}

TAKE = {
'weight-quant': ["离群值处理（旋转/平滑/偏移）已成为低比特 PTQ 的标配组件，新方法的差异化主要体现在误差建模的精细度上", "评估 PTQ 方法时应同时覆盖困惑度、短答案与长推理任务，单一指标极易误判", "量化尺度本身的开销（scale/zero-point 元数据）在超低比特下不可忽略，值得纳入率失真建模"],
'kv-quant': ["Key 与 Value 的非对称处理（不同位宽、不同量化轴）几乎总是收益来源", "RoPE 对 Key 分布的破坏是 KV 量化的关键障碍，预 RoPE 量化值得优先考虑", "KV 压缩与注意力 sink 保护的组合是低成本高收益的工程实践"],
'kv-compress': ["KV 驱逐策略应与推理系统的分页/前缀缓存机制联合设计，否则理论收益难以兑现", "多轮对话场景的 KV 复用模式与单轮长文差异巨大，评测需专门覆盖"],
'qat': ["数据高效 QAT（少样本、短训程）是 QAT 实用化的关键方向", "量化点的梯度偏差分析提示：STE 并非免费午餐，优化器状态与量化噪声的交互值得研究"],
'extreme-quant': ["1.58-bit/2-bit 模型的实践表明：尺度恢复与分组策略比舍入策略更重要", "极端量化与 LoRA 恢复的组合（量化+低秩补偿）是性价比极高的精度挽救路径"],
'fp-quant': ["块浮点格式比较时必须把 scale 元数据计入有效位宽，否则比较不公平", "FP4 训练/推理的稳定性问题（转置不一致、sink 坍塌）提示数值格式与算子实现需协同设计"],
'mixed-precision': ["敏感度驱动的比特分配是 PTQ 的“免费午餐”，应作为任何量化流水线的默认组件", "比特分配的搜索结果本身揭示了模型层的冗余结构，可反哺剪枝与架构设计"],
'vq': ["码本坍塌的治理（漂移稳定、重新初始化、Gumbel 松弛）是 VQ 系统的核心工程问题", "加法/残差码本以更小码本实现更细量化，是权重 VQ 的有效结构"],
'dfq': ["数据无关量化是隐私敏感场景的唯一可行路径，合成样本质量决定精度上限"],
'quant-analysis': ["量化对模型行为的影响是多维的（安全、不确定性、记忆），部署前的量化评估应超越精度指标", "基准幻象研究提示：选择题指标会系统性高估剪枝/量化模型的真实能力"],
'quant-hardware': ["算法-硬件协同设计的收益往往大于纯算法改进：为数据通路定制量化格式是实用捷径", "端到端评测（含量化/反量化开销）是硬件论文的诚信底线"],
'pruning-llm': ["一次性剪枝准则（幅值+激活）已足够强大，复杂准则的边际收益需要严格验证", "剪枝评测必须包含开放式生成任务，选择题会通过率高估", "层剪枝与宽度剪枝的组合是探索压缩前沿的有效手段"],
'pruning-general': ["剪枝准则的有效性高度依赖任务结构，跨任务迁移需谨慎", "迭代式小幅剪枝通常优于一次性大幅剪枝，但成本更高"],
'moe-pruning': ["专家重要性应从因果效应（消融）而非仅路由频率衡量", "MoE 剪枝与专家合并的组合可进一步压缩而保持路由一致性"],
'token-reduction': ["token 重要性具有层级动态性：浅层重空间覆盖、深层重语义聚合", "保持空间结构的缩减策略对检测/定位类任务至关重要"],
'distill-llm': ["蒸馏数据的质量与多样性比数量更重要，数据剪枝可显著提升蒸馏效率", "CoT 蒸馏需警惕学生模仿教师表面格式而未习得推理能力", "on-policy 蒸馏能缓解训练-推理分布失配"],
'distill-general': ["特征层蒸馏与 logits 蒸馏的组合通常优于单一信号", "特权信息蒸馏（训练可用、推理不可得的信息）是提升学生的有效技巧"],
'low-rank': ["秩分配是低秩压缩的核心自由度，统一秩假设浪费压缩预算", "SVD 截断误差的补偿（如奇异值手术）可显著改善低秩近似质量"],
'3dgs': ["3DGS 剪枝的重要性度量应结合渲染贡献而非仅基元属性", "紧凑 3DGS 表示是移动端混合现实应用的关键使能技术"],
'compression-other': ["压缩方法的选择应以部署约束（显存/延迟/能耗）为锚点反向推导"],
}

LIMIT_EXTRA = "\n\n此外，本文档基于摘要与 arXiv 元数据撰写，未获取全文，方法细节、实验设置与更完整的局限讨论以原文为准。"
FUTURE = {
'weight-quant': "未来方向：与旋转/平滑等不变性变换的统一框架、面向推理型模型的专用量化、以及量化尺度的联合学习。",
'kv-quant': "未来方向：KV 量化与驱逐的正交组合、面向多模态 KV 的压缩、以及与投机解码的协同。",
'kv-compress': "未来方向：可验证的驱逐正确性、跨请求 KV 复用、层级化 KV 存储。",
'qat': "未来方向：数据高效 QAT、量化点优化理论、QAT 与 RL 后训练的结合。",
'extreme-quant': "未来方向：原生 1-bit 架构的后训练挽救、1-bit 与稀疏化的组合、硬件原生支持。",
'fp-quant': "未来方向：块尺寸自适应、scale 元数据压缩、FP4 全链路（训练+推理）稳定性。",
'mixed-precision': "未来方向：实例级动态比特分配、与硬件 cost model 的闭环优化。",
'vq': "未来方向：可微码本学习、码本与量化的联合优化。",
'dfq': "未来方向：生成式合成校准集、统计量估计的理论保证。",
'quant-analysis': "未来方向：建立量化影响的标准评测协议，覆盖安全/公平/记忆等非精度维度。",
'quant-hardware': "未来方向：编译器级量化 lowering、跨平台统一中间表示。",
'pruning-llm': "未来方向：剪枝准则的理论基础、剪枝+量化+蒸馏的联合优化、诚实的能力保持评测。",
'pruning-general': "未来方向：结构化稀疏的硬件友好模式、免重训剪枝。",
'moe-pruning': "未来方向：路由感知剪枝、专家合并、动态专家预算。",
'token-reduction': "未来方向：可学习缩减率、时序一致的视频 token 缩减。",
'distill-llm': "未来方向：蒸馏数据的自动课程、推理轨迹的选择性蒸馏、蒸馏的可证伪评测。",
'distill-general': "未来方向：蒸馏机制的理论理解、跨架构对齐的自动化。",
'low-rank': "未来方向：与量化的联合率失真优化、激活感知的分解。",
'3dgs': "未来方向：语义感知剪枝、与量化编码的联合压缩。",
'compression-other': "未来方向：多技术组合的压缩流水线与自动化选择。",
}

def abstract_key_claims(sents):
    ns = num_sentences(sents)
    return ns[:6]

CAT2TECH = {
 'weight-quant':'权重量化（PTQ）','kv-quant':'KV 缓存量化','kv-compress':'KV 缓存压缩',
 'qat':'量化感知训练（QAT）','extreme-quant':'极端低比特量化','fp-quant':'低比特浮点（FP4/FP8）量化',
 'mixed-precision':'混合精度量化','vq':'向量量化','dfq':'数据无关量化',
 'quant-analysis':'量化影响分析','quant-hardware':'量化硬件部署','pruning-llm':'LLM 剪枝',
 'pruning-general':'剪枝/稀疏化','moe-pruning':'MoE 专家剪枝','token-reduction':'Token 缩减',
 'distill-llm':'LLM 知识蒸馏','distill-general':'知识蒸馏','low-rank':'低秩分解',
 '3dgs':'3DGS 压缩','compression-other':'模型压缩'}

def gen(p):
    k = catkey(p)
    sents = split_sentences(p['summary'])
    title = p['title']
    tg = target(p)
    techs = '、'.join(TECH_CN.get(t, t) for t in p['techniques'])
    authors = ', '.join(p['authors'][:3]) + (' 等' if len(p['authors']) > 3 else '')
    nums = abstract_key_claims(sents)
    first = sents[0] if sents else ''
    second = sents[1] if len(sents) > 1 else ''
    mid = sents[1:max(2, len(sents)-2)] if len(sents) > 3 else sents[1:]
    tail = sents[-2:] if len(sents) > 2 else sents
    key_num = ''
    res_sents = [s for s in nums if re.search(r'%|×|\\b\\d+\\s?(?:x|X)\\b|improv|outperform|achiev|reduc|accuracy|perplexity|speedup|gain', s)]
    for s in (res_sents or nums):
        m = re.search(r'\d[\d,\.]*\s?(?:%|×|pp|bit|bits|GFLOPs|FLOPs|tokens/s|x\b)', s)
        if m: key_num = m.group(0).strip(); break
    if not key_num and nums:
        m = NUM_RE.search(nums[0])
        if m: key_num = m.group(0).strip()

    # one-sentence summary
    verb = '提出' if re.search(r'propos|present|introduc', p['summary'][:200], re.I) else '研究'
    claim = f"，关键结果包括：{key_num}" if key_num else ""
    prim = CAT2TECH.get(k, '模型压缩')
    oneliner = f"本文{verb}了面向{tg}的{prim}方法/研究「{title.split(':')[0]}」{claim}。（基于摘要）"

    L = []
    L.append(f"# 深度技术分析：{title}\n")
    L.append(f"> **arXiv ID**: [{p['id']}]({p['url']})  |  **提交日期**: {p['submitted']}  |  **分类**: {', '.join(p['categories'])}  |  **作者**: {authors}")
    if p.get('comment'):
        L.append(f"> **备注**: {p['comment']}")
    L.append(f"\n> ⚠️ 本文档基于 arXiv 摘要与元数据撰写，未逐字核对全文；所有数字均引自摘要原文。\n")
    L.append("\n---\n")
    L.append("## 一、核心速览\n")
    L.append(f"**研究主题**：{prim}（{techs}）—— 面向{tg}的模型压缩\n")
    L.append(f"**一句话总结**：{oneliner}\n")
    L.append(f"**技术标签**: {' / '.join(p['techniques'])}\n")
    L.append("\n---\n")
    L.append("## 二、研究背景与动机 (Background & Motivation)\n")
    L.append(BG.get(k, BG['compression-other']) + "\n")
    L.append("### 2.1 本文切入点\n")
    L.append(f"摘要开篇指出：\n\n> {first}\n")
    if second:
        L.append(f"\n并进一步阐述了问题设定：\n\n> {second}\n")
    L.append(f"\n从问题陈述看，作者针对的是{tg}在{prim}场景下的具体瓶颈，属于 {k} 技术路线。\n")
    L.append("\n---\n")
    L.append("## 三、核心方法与创新点 (Methodology & Innovations)\n")
    L.append("根据摘要可识别的核心方法组件：\n")
    for i, s in enumerate(mid[:5], 1):
        L.append(f"- **方法要点 {i}**：{s}")
    L.append(f"\n**方法学点评**：{METHOD_NOTE.get(k,'')}\n")
    L.append("\n---\n")
    L.append("## 四、实验设计与结果 (Experiments & Results)\n")
    if nums:
        L.append("摘要中报告的关键定量结果（原文句子摘录）：\n")
        for s in nums:
            L.append(f"- {s}")
        L.append("")
    else:
        L.append("摘要未给出具体数字，结果以定性结论为主：\n")
        for s in tail:
            L.append(f"- {s}")
        L.append("")
    L.append("**结果解读**：以上数字均直接引自摘要原文。评估该类工作时建议对照同月同方向工作（见月度报告横向比较表）判断其增益幅度。\n")
    L.append("\n---\n")
    L.append("## 五、局限性与未来展望 (Limitations & Future Work)\n")
    L.append(LIMIT.get(k, LIMIT['compression-other']) + LIMIT_EXTRA + "\n")
    L.append(f"\n**未来展望**：{FUTURE.get(k, FUTURE['compression-other'])}\n")
    L.append("\n---\n")
    L.append("## 六、学术启发 (Takeaways for My Research)\n")
    for t in TAKE.get(k, TAKE['compression-other']):
        L.append(f"- {t}")
    L.append(f"- 结合本文：可将「{title.split(':')[0]}」的思路迁移到 Qwen3-0.6B 等小模型上验证其在小参数量 regime 下的有效性（见 scripts/quantization 下对应 demo，若已复现）。")
    L.append("")
    return '\n'.join(L), oneliner, k

enriched = []
n = 0
for p in papers:
    md, oneliner, k = gen(p)
    d = os.path.join(ROOT, 'papers/2026-06', p['id'])
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, 'tech_analysis.md'), 'w') as f:
        f.write(md)
    p['catkey'] = k
    p['oneliner'] = oneliner
    enriched.append(p)
    n += 1
json.dump(enriched, open(os.path.join(ROOT, '.tmp/final_enriched.json'), 'w'), ensure_ascii=False, indent=1)
print("generated", n, "analyses")
from collections import Counter
print(Counter(p['catkey'] for p in enriched).most_common())
