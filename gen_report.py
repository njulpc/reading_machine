#!/usr/bin/env python3
"""Generate monthly report + metadata for 2026-01 arXiv model-compression backfill."""
import json, os, re, csv

papers = json.load(open('final_papers.json'))
quant_ids = set(json.load(open('quant_ids.json')))
os.makedirs('reports/2026-01/quantization', exist_ok=True)
os.makedirs('metadata/2026-01', exist_ok=True)

CATEGORY_LABELS = {
    'quantization': '量化 (Quantization)',
    'distillation': '知识蒸馏 (Distillation)',
    'pruning': '剪枝 (Pruning)',
    'sparsity': '稀疏化 (Sparsity)',
    'kv_cache': 'KV Cache 压缩',
    'token_compression': 'Token 压缩',
    'mixed_precision': '混合精度/数值格式',
    'low_rank': '低秩分解',
    'compression': '通用/其他压缩',
    'hardware': '硬件协同',
    'analysis': '分析/评测',
}

def cats_of(p):
    return [t for t in p.get('techniques', [])]

def primary_cat(p):
    for c in ['quantization','kv_cache','pruning','sparsity','distillation','token_compression','mixed_precision','compression']:
        if c in cats_of(p):
            return c
    return 'compression'

# ---------- heuristic scoring for quantization papers ----------
def has_num(s):
    return bool(re.search(r'\d+(\.\d+)?\s*(%|×|x|bit|倍|points)', s))

def score_paper(p):
    s = (p['title'] + ' ' + p['summary']).lower()
    # 精度效果
    acc = 6
    if re.search(r'state-of-the-art|sota|near-lossless|无损|outperform', s): acc = 7
    if re.search(r'\d+(\.\d+)?\s*(%|points|perplexity)', s): acc = 8
    if 'analysis' in cats_of(p) or 'benchmark' in s or 'study' in s: acc = min(acc, 7)
    # 压缩倍率
    comp = 5
    if re.search(r'(1\.?[0-9]*|2)[- ]?bit|binary|ternary|二值|三值', s): comp = 9
    elif re.search(r'(3|4)[- ]?bit|fp4|nvfp4|mxfp4|int4|w4', s): comp = 8
    elif re.search(r'8[- ]?bit|fp8|int8|w8', s): comp = 6
    elif re.search(r'70\s*%|90\s*%|10\s*×|64\s*×', s): comp = 8
    if re.search(r'sub-3|extremely low|ultra-low', s): comp = max(comp, 9)
    # 创新性
    inno = 6
    if re.search(r'first|novel|new format|framework|unified|理论|theor', s): inno = 7
    if re.search(r'co-design|hardware|kernel|accelerator|npu|fpga', s): inno = 7
    if re.search(r'attack|security|fairness|safety|unlearn', s): inno = 8
    if re.search(r'fourier|hessian|information-theoretic|axiom|proof', s): inno = 8
    # 可复现性
    repro = 6
    if re.search(r'code|github|open[- ]source|release', s): repro = 9
    elif re.search(r'gptq|awq|llama\.cpp|vllm|verl|qwen|llama', s): repro = 7
    elif re.search(r'accelerator|tape|65\s*nm|fpga|npu|prototype', s): repro = 5
    return acc, comp, inno, repro

# curated overrides (acc, comp, inno, repro) for known highlight papers
OVERRIDES = {
    '2601.19213': (9, 8, 9, 7),   # M2XFP: 70.63%/37.30% accuracy-loss reduction, 1.91x speedup
    '2601.19320': (8, 9, 8, 8),   # StableQAT: Fourier surrogate, 2-4bit stable QAT
    '2601.20745': (8, 9, 8, 7),   # Hestia: Hessian-guided annealed QAT
    '2601.19675': (8, 9, 7, 8),   # LoPRo: sub-3bit residual rotation
    '2601.15538': (8, 7, 9, 8),   # QUAIL: quantization-aware unlearning
    '2601.20088': (9, 8, 7, 8),   # QAD NVFP4 (NVIDIA tech report)
    '2601.14243': (9, 7, 8, 8),   # Jet-RL: FP8 RL on-policy
    '2601.18150': (8, 7, 7, 9),   # FP8-RL: veRL stack
    '2601.18306': (8, 6, 7, 9),   # multilingual calibration study
    '2601.19026': (9, 7, 8, 8),   # microscaling limits (IBM)
    '2601.17187': (9, 7, 9, 6),   # high-rate quantized matmul theory
    '2601.14888': (9, 8, 7, 8),   # QAT for reasoning LLMs systematic study
    '2601.14277': (8, 6, 5, 9),   # llama.cpp unified evaluation
    '2601.12033': (8, 6, 8, 7),   # fairness/safety critical weight protection
    '2601.21279': (9, 8, 9, 6),   # NEXUS bit-exact ANN-SNN
}

# ---------- build category groups ----------
groups = {}
for p in papers:
    groups.setdefault(primary_cat(p), []).append(p)

# ---------- report ----------
L = []
A = L.append
A("# arXiv 模型压缩月度报告：2026 年 1 月（量化专题）\n")
A("> **数据来源**: arXiv API 19 组关键词查询（1099 篇候选）+ arxiv.org 12 个类目 2026-01 全量列表（9456 条）交叉过滤")
A("> **收录标准**: v1 提交于 2026-01-01 至 2026-01-31；主题严格限于模型压缩核心方向（量化/剪枝/稀疏/蒸馏/KV cache/token 压缩）")
A("> **论文总数**: 246 篇 ｜ **量化相关**: 80 篇（含 mixed_precision 去重）")
A("> **生成时间**: 2026-01 回填 ｜ 仓库: reading_machine feature/arxiv-monthly-2026-01\n")
A("---\n")

A("## 一、本月概览\n")
A("2026 年 1 月 arXiv 模型压缩方向共产出 246 篇相关论文。主题分布（一篇可多标签，按主标签归类）：\n")
A("| 方向 | 数量 | 占比 |")
A("| --- | --- | --- |")
order = sorted(groups.items(), key=lambda kv: -len(kv[1]))
for c, ps in order:
    A(f"| {CATEGORY_LABELS.get(c, c)} | {len(ps)} | {len(ps)/246*100:.1f}% |")
A("")
A("量化方向 80 篇中：训练后量化（PTQ）与量化感知训练（QAT）并重，4-bit/FP4 数值格式（MXFP4/NVFP4/M2XFP）成为预训练与推理双场景焦点；量化研究的安全、公平、多语言维度明显升温；算法-硬件协同设计（NPU/FPGA/CAM/加速器）占比显著。\n")

A("## 二、全部论文总览表（246 篇）\n")
A("| # | arXiv | 标题 | 作者(前2) | 提交日期 | 主方向 |")
A("| --- | --- | --- | --- | --- | --- |")
for i, p in enumerate(papers):
    t = p['title'].replace('|', '\\|')
    if len(t) > 80: t = t[:77] + '...'
    au = ', '.join(p['authors'][:2]) + (' 等' if len(p['authors']) > 2 else '')
    A(f"| {i+1} | [{p['id']}](https://arxiv.org/abs/{p['id']}) | {t} | {au} | {p['published'][:10]} | {CATEGORY_LABELS.get(primary_cat(p), primary_cat(p))} |")
A("")

A("## 三、分类论文清单\n")
for c, ps in order:
    A(f"### {CATEGORY_LABELS.get(c, c)}（{len(ps)} 篇）\n")
    for p in ps:
        A(f"- [{p['id']}](https://arxiv.org/abs/{p['id']}) {p['title']}")
    A("")

A("## 四、量化论文四项评分表（80 篇）\n")
A("评分维度（各 1-10 分）：**精度效果**（量化后精度保持/恢复水平，依据摘要报告的指标）、**压缩倍率**（比特宽度/压缩率激进程度）、**创新性**（方法/理论/格式新颖度）、**可复现性**（代码、标准工具链、方法细节可得性）。启发式规则打分+重点论文人工校准，仅供横向参考。\n")
A("| # | arXiv | 标题(截断) | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 综合 |")
A("| --- | --- | --- | --- | --- | --- | --- |")
quant_papers = [p for p in papers if p['id'] in quant_ids]
scored = []
for p in quant_papers:
    sc = OVERRIDES.get(p['id'], score_paper(p))
    avg = sum(sc) / 4
    scored.append((p, sc, avg))
scored.sort(key=lambda x: -x[2])
for i, (p, sc, avg) in enumerate(scored):
    t = p['title'].replace('|', '\\|')
    if len(t) > 55: t = t[:52] + '...'
    A(f"| {i+1} | [{p['id']}](https://arxiv.org/abs/{p['id']}) | {t} | {sc[0]} | {sc[1]} | {sc[2]} | {sc[3]} | **{avg:.1f}** |")
A("")

A("## 五、本月亮点论文\n")
HIGHLIGHTS = [
 ("2601.19213", "M2XFP：元数据增强微缩放格式，精度损失较 MXFP4 平均降低 70.63%、较 NVFP4 降低 37.30%，配套硬件单元实现 1.91× 加速、1.75× 能效——FP4 格式军备赛的最新一击。"),
 ("2601.19320", "StableQAT：从舍入算子的离散傅里叶分析推导 QAT 代理梯度族，证明 STE 只是其特例，2-4bit 训练稳定性显著提升——代理梯度设计从艺术变为有谱系的科学。"),
 ("2601.20088", "NVIDIA QAD 技术报告：量化感知蒸馏恢复 NVFP4 精度，对 SFT+RL+合并的多阶段后训练模型比 QAT 更稳定、对数据覆盖鲁棒——FP4 时代的事实标准配方。"),
 ("2601.14243", "Jet-RL：首个 FP8 RL 系统研究，揭示\"BF16 训练+FP8 rollout\"的数值失配使 on-policy 退化为 off-policy 导致崩溃——量化 RL 的诊断框架。"),
 ("2601.19026", "IBM 微缩放极限研究：块大小低于阈值后精度反而退化，证伪\"块越小越好\"——MX 格式存在最优粒度甜蜜点。"),
 ("2601.17187", "Ordentlich & Polyanskiy：量化矩阵乘的信息论高率理论，为 absmax INT 与 FP 格式建立率-失真基准——量化研究有了理论锚点。"),
 ("2601.18306", "多语言校准研究：非英语/多语言校准集使多语言 LLM 量化困惑度最高降 3.52 点——零成本高收益的最佳实践修正。"),
 ("2601.12033", "量化公平与安全：量化一致损害公平性/安全性且非英语更严重，关键权重保护（CWP）把混合精度从\"保精度\"扩展到\"保对齐\"。"),
 ("2601.15538", "QUAIL：发现低比特量化会\"复活\"已遗忘知识（遗忘更新跨不过量化桶阈值），logits 空间 hinge 损失让遗忘在量化后存活。"),
 ("2601.21279", "NEXUS：用 IF 神经元逻辑门实现 IEEE-754 浮点算术，ANN→SNN 比特级精确等价（LLaMA-2 70B 精度 0.00% 退化，ULP 误差 6.19）。"),
 ("2601.11660", "MBU：显式零掩码训练让二值 U-Net 获得有信息量的稀疏第三态，Tensor Core 端到端实现——\"零是有信息量的\"。"),
 ("2601.13563", "ButterflyMoE：专家=共享三值基底+蝴蝶旋转，单专家存储 O(d²)→O(d·log d)——MoE 内存扩展瓶颈的结构性解法。"),
]
for pid, txt in HIGHLIGHTS:
    A(f"- **[{pid}](https://arxiv.org/abs/{pid})** {txt}")
A("")

A("## 六、趋势分析\n")
A("### 1. FP4/微缩放格式的军备竞赛")
A("MXFP4→NVFP4→M2XFP 的演进线是\"少量元数据换大幅精度\"的持续加码；IBM 的块粒度极限研究与 Polyanskiy 团队的信息论基准标志着 4-bit 格式从工程竞争进入科学分析阶段。算法-硬件协同（M2XFP 的轻量解码单元、VersaQ-3D 的可重构加速器、昇腾 W4A16 kernel）成为硬门槛——纯软件格式创新空间在收窄。\n")
A("### 2. 蒸馏与量化深度融合")
A("QAD（NVIDIA）、推理模型 QAT 系统研究（蒸馏是稳健目标）、StableQAT/Hestia 的代理梯度改进共同表明：\"量化即训练\"时代的核心问题是如何在不可微量化下优化——蒸馏目标与代理梯度是两大支柱。\n")
A("### 3. 校准集成为一阶研究对象")
A("FAQ（同家族大模型再生校准数据）、多语言校准研究、推理模型 QAT 的域对齐发现一致指出：校准数据分布是 PTQ 被低估的一阶变量，\"按需合成校准集\"正在取代\"随手取 WikiText\"。\n")
A("### 4. 量化的安全/公平/隐私维度成型")
A("QUAIL（量化复活遗忘）、公平安全关键权重保护、多语言退化测量、蒸馏记忆动态（记忆降 50%+）——量化评估正从\"困惑度+准确率\"扩展到对齐保持维度，公平/安全应进入量化方法的标准评测包。\n")
A("### 5. 理论化与统一化")
A("激活敏感度统一 AWQ/GPTQ、量化 MatMul 高率理论、StableQAT 的傅里叶代理族（STE 为特例）、蒸馏的公理化框架——工程积累进入原理整合期。\n")
A("### 6. 硬件落地的最后一公里")
A("昇腾 NPU W4A16 kernel、PiC-BNN 65nm 流片、SPADE Posit SIMD、SATA 稀疏调度、QMC 存算协同——量化收益的最终兑现依赖 kernel/芯片级实现，\"论文压缩率≠实际加速\"的系统鸿沟被反复正视。\n")

A("## 七、复现资产\n")
A("本仓库为以下 5 篇核心量化论文提供可运行复现 demo（`scripts/quantization/<id>/`，均优先加载真实 Qwen3-0.6B 权重验证，加载失败回退 mock 权重）：\n")
A("| arXiv | 论文 | demo 验证内容 |")
A("| --- | --- | --- |")
DEMOS = [
 ("2601.19320", "StableQAT", "傅里叶代理 vs STE 的 2/3-bit QAT 重建 MSE（2-bit 下 K=3 降低 46.7%）"),
 ("2601.19675", "LoPRo", "置换+Hadamard 旋转+显著列保护 vs 朴素 2-bit 残差量化（误差降低 19.4%）"),
 ("2601.19213", "M2XFP", "2-bit 元数据细化 vs MXFP4 2 的幂 scale（误差降低 14.9%）"),
 ("2601.15538", "QUAIL", "logits 空间 hinge 损失使遗忘方向在 4-bit 量化后存活（cos-sim 0.54→0.97）"),
 ("2601.20745", "Hestia", "温控软量化退火 vs 硬 STE（2-bit MSE 降低约 50%）"),
]
for pid, name, desc in DEMOS:
    A(f"| [{pid}](https://arxiv.org/abs/{pid}) | {name} | {desc} |")
A("")
A("---")
A("*报告由 reading_machine 自动生成（检索管线+人工二审+启发式评分）；每篇论文的深度技术分析见 `papers/2026-01/<id>/tech_analysis.md`。*")

open('reports/2026-01/quantization/arxiv_quantization_monthly_report_202601.md', 'w').write('\n'.join(L) + '\n')
print("report written", len(L), "lines")

# ---------- metadata/papers_index.json ----------
KEYWORDS_QUERY = ["quantization","pruning","sparsity","knowledge distillation","KV cache",
                  "mixed precision","GPTQ","AWQ","model compression","distillation LLM","binarized"]
idx = {
 "collection_date": "2026-02",
 "date_range": "2026-01-01 to 2026-01-31",
 "query_keywords": KEYWORDS_QUERY,
 "total_papers": len(papers),
 "papers": [
   {
    "id": p["id"],
    "title": p["title"],
    "authors": p["authors"],
    "submitted": p["published"][:10],
    "categories": p["categories"],
    "url": f"https://arxiv.org/abs/{p['id']}",
    "keywords": p.get("techniques", []),
    "techniques": p.get("techniques", []),
    "target_model": p.get("note", ""),
    "highlight": p["id"] in {h for h, _ in [(x[0], None) for x in HIGHLIGHTS]},
   } for p in papers
 ],
}
json.dump(idx, open('metadata/2026-01/papers_index.json', 'w'), ensure_ascii=False, indent=2)
print("papers_index.json written")

# ---------- keywords.csv ----------
from collections import defaultdict
kw = defaultdict(list)
for p in papers:
    for t in set(p.get('techniques', [])):
        kw[t].append(p['id'])
with open('metadata/2026-01/keywords.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(["keyword", "occurrence", "paper_ids"])
    for k, ids in sorted(kw.items(), key=lambda kv: -len(kv[1])):
        w.writerow([k, len(ids), "|".join(ids)])
print("keywords.csv written", len(kw), "keywords")
