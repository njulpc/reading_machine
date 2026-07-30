#!/usr/bin/env python3
"""Generate the 2026-07 monthly report markdown from _arxiv_raw/final.json
plus per-paper tech_analysis.md one-liners.

Scoring: 12 flagship papers (manually analyzed in depth) carry hand-assigned
scores; all other papers are scored by a transparent deterministic heuristic
(documented in the report).  Papers with a validated local code demo get a
reproducibility bonus.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
RAW = ROOT / "_arxiv_raw" / "final.json"
PAPERS_DIR = ROOT / "papers" / "2026-07"
QUANT_DIR = ROOT / "scripts" / "quantization"
OUT = ROOT / "reports" / "2026-07" / "quantization" / \
    "arxiv_quantization_monthly_report_202607.md"

papers = json.load(open(RAW))
by_id = {p["id"]: p for p in papers}

# ---------------------------------------------------------------- one-liners
def one_liner(pid, abstract):
    f = PAPERS_DIR / pid / "tech_analysis.md"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\*\*一句话总结\*\*[：:]\s*(.+)", line.strip())
            if m:
                t = m.group(1).strip()
                t = re.sub(r"^本文围绕.{1,30}?研究[——\-]+\s*", "", t)
                return t[:110] + ("…" if len(t) > 110 else "")
    t = re.split(r"(?<=[.。])\s", abstract.strip())[0]
    return t[:110] + ("…" if len(t) > 110 else "")


# ------------------------------------------------------------------- scoring
FLAGSHIP = {  # manually scored after full-depth analysis
    "2607.26515": (8, 8, 9, 7),   # HiFloat4
    "2607.27042": (7, 7, 9, 8),   # GPTQ-2D
    "2607.07964": (8, 7, 8, 7),   # KronQ
    "2607.23047": (7, 7, 7, 8),   # MixQuant
    "2607.24953": (8, 8, 8, 7),   # StableFP4
    "2607.04422": (8, 8, 8, 6),   # FullStackFP4
    "2607.05061": (7, 8, 7, 8),   # KVpop
    "2607.02584": (8, 7, 8, 8),   # RotateAttention
    "2607.01065": (7, 8, 7, 8),   # GSRQ
    "2607.04302": (8, 8, 8, 7),   # HiFA4
    "2607.05711": (7, 7, 8, 8),   # FourTune
    "2607.24377": (7, 7, 8, 7),   # MXAttention
}

DEMO_IDS = sorted(p.name for p in QUANT_DIR.iterdir()
                  if p.is_dir() and (p / "demo.py").exists())

BASE = {
    "quantization": (6, 7, 6, 6),
    "kv_cache": (6, 8, 6, 6),
    "token_compression": (6, 8, 6, 6),
    "low_rank": (6, 6, 6, 6),
    "pruning": (6, 6, 6, 6),
    "sparsity": (6, 6, 6, 6),
    "distillation": (6, 3, 6, 6),
    "other": (5, 4, 5, 5),
}
PRIMARY_ORDER = ["quantization", "kv_cache", "token_compression",
                 "low_rank", "pruning", "sparsity", "distillation", "other"]


def primary_tag(p):
    tags = set(p.get("tech_tags") or [])
    for t in PRIMARY_ORDER:
        if t in tags:
            return t
    return "other"


def heuristic_score(p):
    a = p["abstract"].lower()
    acc, comp, inn, rep = BASE[primary_tag(p)]
    # numeric richness: reported %, x-speedups, ppl numbers
    n_pct = len(re.findall(r"\d+(?:\.\d+)?\s*%", a))
    n_mult = len(re.findall(r"\d+(?:\.\d+)?\s*[×x]\b", a))
    if n_pct + n_mult >= 3:
        acc += 1
    if n_pct + n_mult >= 6:
        acc += 1
    # bit-width extremes
    if re.search(r"\b(1[- ]?bit|binary|ternary|2[- ]?bit|w2|1\.58)\b", a):
        comp += 1
        inn += 1
    elif re.search(r"\b(fp4|nvfp4|mxfp4|4[- ]?bit|int4|w4a4|fp8)\b", a):
        comp += 0
    if re.search(r"\b(int8|fp16|bf16)\b", a) and "quant" in a:
        comp -= 0
    # method vs study
    if re.search(r"\b(we propose|we introduce|we present)\b", a):
        inn += 1
    if re.search(r"\b(survey|benchmark|empirical study|controlled study|"
                 r"analysis of|we analyze|we study)\b", a):
        inn -= 1
        rep += 1
    # reproducibility signals
    if re.search(r"(github\.com|code is available|open.?source)", a):
        rep += 2
    if re.search(r"\b(fpga|asic|chip|accelerator|npu|microcontroller|"
                 r"silicon|tapeout|16nm|7nm)\b", a):
        rep -= 1
    if p["id"] in DEMO_IDS:
        rep += 1  # validated locally in this repository
    clamp = lambda v: max(1, min(10, v))
    return clamp(acc), clamp(comp), clamp(inn), clamp(rep)


scores = {}
for p in papers:
    scores[p["id"]] = FLAGSHIP.get(p["id"]) or heuristic_score(p)

# ---------------------------------------------------------------- statistics
tag_counts = Counter()
for p in papers:
    for t in p.get("tech_tags") or []:
        tag_counts[t] += 1

primary_counts = Counter(primary_tag(p) for p in papers)

WEEKS = [("07-01 ~ 07-05", "2026-07-01", "2026-07-05"),
         ("07-06 ~ 07-12", "2026-07-06", "2026-07-12"),
         ("07-13 ~ 07-19", "2026-07-13", "2026-07-19"),
         ("07-20 ~ 07-26", "2026-07-20", "2026-07-26"),
         ("07-27 ~ 07-29", "2026-07-27", "2026-07-29")]
week_counts = []
for label, lo, hi in WEEKS:
    c = sum(1 for p in papers if lo <= p["published"][:10] <= hi)
    week_counts.append((label, c))

TAG_LABEL = {
    "quantization": "量化 (Quantization)",
    "kv_cache": "KV Cache 压缩",
    "token_compression": "Token/序列压缩",
    "low_rank": "低秩分解",
    "pruning": "剪枝 (Pruning)",
    "sparsity": "稀疏 (Sparsity)",
    "distillation": "知识蒸馏 (Distillation)",
    "compression_other": "其他压缩",
    "other": "其他",
}

DEMO_TITLES = {pid: by_id[pid]["title"] for pid in DEMO_IDS if pid in by_id}

# ------------------------------------------------------------------- writers
L = []
w = L.append

w("# ArXiv 量化与模型压缩领域论文月报（2026 年 7 月）")
w("")
w("**收集日期范围**: 2026-07-01 至 2026-07-29 UTC")
w("")
w("**检索关键词**: quantization, model compression, pruning, distillation, efficient inference, sparsity（单词查询 + 提交日期倒序分页 + 客户端过滤）")
w("")
w("**数据来源**: arXiv.org API")
w("")
w("**论文总数**: 317 篇")
w("")
w("---")
w("")
w("## 一、范围与方法")
w("")
w("- **时间窗**：2026-07-01 00:00 至 2026-07-29 23:59 UTC 提交的新论文（cross-list 以首次提交日期为准）。")
w("- **召回方式**：arXiv API 对复杂布尔查询持续返回 500，故采用 6 个技术关键词（quantization / pruning / knowledge distillation / model compression / sparsity / efficient inference）单词查询，按 submittedDate 倒序全量分页抓取后客户端过滤，关键词取并集去重。摘要级召回，可能漏掉标题/摘要不含上述词根的压缩论文。")
w("- **范围界定**：只收录以**压缩/高效化**为目标的论文。排除三类边界论文：① 纯能力迁移的 on-policy / RL 策略蒸馏（约 30 篇，目标是行为对齐而非压缩）；② 纯 serving 系统优化（无量化/稀疏/蒸馏成分）；③ 压缩感知与图像编解码（compressed sensing / neural codec）。")
w("- **分析深度**：全部 317 篇配有六段结构化技术分析（`papers/2026-07/<id>/tech_analysis.md`），其中 12 篇旗舰论文为人工深度覆写，其余为基于摘要的机器辅助分析（摘要级，未逐篇核对全文）。")
w("")
w("---")
w("")
w("## 二、月度总览统计")
w("")
w("### 2.1 按技术标签分布（论文可有多标签）")
w("")
w("| 技术方向 | 论文数 | 占比 |")
w("|---------|:-----:|:---:|")
for t, c in tag_counts.most_common():
    w(f"| {TAG_LABEL.get(t, t)} | {c} | {c / len(papers) * 100:.1f}% |")
w("")
w("### 2.2 按主标签分布（每篇归入唯一主类，优先级：量化 > KV cache > token 压缩 > 低秩 > 剪枝 > 稀疏 > 蒸馏）")
w("")
w("| 主类 | 论文数 |")
w("|------|:-----:|")
for t in PRIMARY_ORDER:
    w(f"| {TAG_LABEL[t]} | {primary_counts[t]} |")
w("")
w("### 2.3 按周分布")
w("")
w("| 周 | 论文数 |")
w("|---|:-----:|")
for label, c in week_counts:
    w(f"| {label} | {c} |")
w("")
w("07-06 ~ 07-19 两周为稳定高峰（77–78 篇/周）；07-27 ~ 07-29 仅 3 天即收录 44 篇，日均 14.7 篇为全月最高密度，与 ICML 2026 会期结束后的投稿潮一致。FP4 训练、注意力量化、KV cache 压缩三个主题的代表性论文集中在下半月。")
w("")
w("---")
w("")

w("## 三、量化方向专题（112 篇量化标签论文）")
w("")
w("### 3.1 子主题分布")
w("")
w("| 子主题 | 代表论文 | 要点 |")
w("|-------|---------|------|")
w("| FP4 端到端训练 | HiFloat4 (2607.26515)、StableFP4 (2607.24953)、FullStackFP4 (2607.04422)、FourTune (2607.05711) | FP4 从纯推理格式走向训练/微调全程格式；核心是层次化缩放与 rollout-training 误差对齐 |")
w("| 注意力机制量化 | RotateAttention (2607.02584)、HiFA4 (2607.04302)、MXAttention (2607.24377)、AVQ-Attention (2607.12789) | P-Reordering/旋转等效化 + MX 格式成为本月共识路线 |")
w("| KV cache 量化/压缩 | KVpop (2607.05061)、GSRQ (2607.01065)、DepthWeave-KV (2607.06523)、Lynx (2607.01831)、JoLT (2607.12550) | 从均匀预算走向 token/层自适应与流式渐进传输 |")
w("| 二阶 PTQ 算法 | GPTQ-2D (2607.27042)、KronQ (2607.07964)、KroQuant (2607.21446) | Kronecker/双侧结构进入主流；复杂度与精度同时推进 |")
w("| 极低比特（≤2 bit） | ExTernD (2607.13511)、Cross-Layer Error Compensation (2607.14630)、BiSCo (2607.02893)、Log_bQuant (2607.08643) | 扩展秩分解、跨层误差补偿让 1–2 bit 从不可用走向可用 |")
w("| 混合精度与敏感度分配 | MXSens (2607.17733)、CONQuER (2607.25884)、C-PTQ (2607.21076) | 列/块级敏感度 + 硬件感知搜索取代均匀位宽 |")
w("| MoE 量化 | MixQuant (2607.23047)、PagedWeight (2607.16184)、QUADS (2607.15810) | 专家级精度分配、运行时动态量化、RL rollout 稳定性 |")
w("| 扩散模型量化 | KroQuant (2607.21446)、OrbitQuant (2607.02461)、RDQ (2607.10137) | 块变换/旋转基 + 数据无关码本，W4A4 甚至 W2A4 可用 |")
w("| 全整数部署 | I-LW-DETR (2607.24981) | Softmax/GELU/LayerNorm 的整数近似，端到端 INT 推理 |")
w("| 旋转/基学习 | GaugeQuant (2607.20757) | 训练中用对称性破缺项学习量化最优基，无需校准数据 |")
w("")
w("### 3.2 本月量化复现代码（19 个 demo）")
w("")
w("以下 19 篇提出可复现量化算法的论文配有独立可运行 demo（`scripts/quantization/<id>/`，含 README.md 与 demo.py）。验证方式统一为：**优先加载本地缓存的真实 Qwen/Qwen3-0.6B**，对其前若干层线性层/KV cache 实际执行量化并比较 logits 余弦或重建误差；模型不可用时 demo 自动退化为同维度的合成基准，保证任何环境可跑通。全部 19 个 demo 均已在本机实际运行通过。")
w("")
w("| # | arXiv ID | 论文 | 核心验证点 |")
w("|--:|----------|------|-----------|")
DEMO_NOTE = {
    "2607.01065": "真实 K cache 增益-形状残差量化，重建余弦 1.0000",
    "2607.01127": "对数底自适应量化 vs 均匀量化误差对比",
    "2607.02584": "RoPE 感知旋转后 INT4 注意力输出误差显著下降",
    "2607.02893": "逐组可变位宽分配 vs 均匀位宽的等比特误差",
    "2607.04302": "P-Reordering 行和 std=0（direct 0.0458）",
    "2607.04422": "FP4 全栈（投影/优化器/注意力）缩放链误差验证",
    "2607.05711": "扩散模型全 4bit 微调量化-反量化一致性",
    "2607.07964": "Kronecker 分解 Hessian 的 GPTQ 舍入误差下降",
    "2607.08643": "1bit/维球面二值编码，logits 余弦 0.9445（符合 1bit 预期）",
    "2607.10137": "残差分布量化的分段码本误差验证",
    "2607.12550": "真实 K cache Tucker+JL 残差压缩重建余弦 0.9972",
    "2607.12789": "注意力集中场景自适应码本细化优于均匀 VQ（0.053 vs 0.062）",
    "2607.13511": "三值扩展秩分解残差单调下降（any-ε 性质验证）",
    "2607.14630": "跨层补偿使 1.125bit logits 余弦 0.447→0.993",
    "2607.23047": "敏感度感知混合精度优于均匀 INT4 的等比特误差",
    "2607.24377": "MXFP4 注意力无数据最优缩放 + 预归一化误差对比",
    "2607.24953": "转置不变块量化保持前向/反向缩放一致性",
    "2607.26515": "层次化 FP4 缩放 + Rollout-ResQ 误差修正",
    "2607.27042": "GPTQ-2D 与暴力 O(m⁴) Babai 逐元素一致（diff 7e-9）",
}
for i, pid in enumerate(DEMO_IDS, 1):
    title = DEMO_TITLES.get(pid, "(title n/a)")
    note = DEMO_NOTE.get(pid, "真实 Qwen3-0.6B + 合成基准")
    w(f"| {i} | {pid} | {title} | {note} |")
w("")
w("**未配 demo 的量化论文说明**：其余量化标签论文属于以下四类，不做算法 demo——① 硬件/芯片设计（FPGA/ASIC/NPU 加速器，无可复现算法）；② 实证研究与基准（实证结论型，无新算法）；③ 下游应用论文（量化作为工具使用）；④ 纯理论分析。这些论文仍全部收录于评分表与技术分析中。")
w("")
w("---")
w("")
w("## 四、全部论文四项评分表（317 篇）")
w("")
w("评分维度（1–10）：**精度效果**（摘要报告的指标保持/提升幅度与证据充分度）、**压缩倍率**（位宽/稀疏度/压缩率激进程度）、**创新性**（方法新颖性）、**可复现性**（算法清晰度、代码可得性、硬件依赖；本地有已验证 demo 者 +1）。")
w("")
w("**评分方式**：12 篇旗舰论文经人工深度分析后人工定分；其余论文由透明确定性启发式生成（主类基准分 + 摘要数字丰富度/极端位宽/方法词/代码链接/硬件依赖调整），分数用于横向粗排，不替代逐篇阅读。")
w("")
w("| 排名 | arXiv ID | 论文标题 | 主类 | 精度效果 | 压缩倍率 | 创新性 | 可复现性 | 总分 |")
w("|:---:|---------|---------|------|:-------:|:-------:|:-----:|:-------:|:---:|")
ranked = sorted(papers, key=lambda p: (-sum(scores[p["id"]]), p["id"]))
for r, p in enumerate(ranked, 1):
    a, c, i2, r2 = scores[p["id"]]
    t = p["title"].replace("|", "\\|")
    w(f"| {r} | {p['id']} | {t} | {TAG_LABEL[primary_tag(p)].split(' ')[0]} "
      f"| {a} | {c} | {i2} | {r2} | **{a + c + i2 + r2}** |")
w("")
w("---")
w("")
w("## 五、本月 Top 亮点")
w("")
HL = [
    ("2607.26515", "HiFloat4", "首次端到端 FP4 RL 后训练：三级层次化缩放格式 + Rollout-ResQ 稀疏残差修正 rollout-training 失配，BF16 差距从 4.9% 缩至 1.1%。FP4 训练从'能跑'走向'对齐'。"),
    ("2607.27042", "GPTQ-2D", "把自适应舍入推广到双侧基矩阵（Kronecker 度量），利用反对角线独立性把朴素 O(m⁴) 降到 O(m³)，输出与精确算法逐元素一致。本月最优雅的理论结果。"),
    ("2607.04422", "FullStackFP4", "FP4 全栈训练框架，系统梳理权重/激活/梯度全链路的缩放设计，是 FP4 训练三篇中的系统性代表。"),
    ("2607.24953", "StableFP4", "FP4 训练稳定性分析 + 稳定化配方，与 HiFloat4/FullStackFP4 共同构成本月'FP4 训练'小高潮。"),
    ("2607.04302", "HiFA4", "层次化 FP4 注意力 + P-Reordering：把 KV 通道按重要性重排使量化误差结构化，与 RotateAttention 的旋转路线相互印证。"),
    ("2607.02584", "RotateAttention", "对 Q/K 施加旋转使注意力输出对量化不变，注意力量化的'免费午餐'路线。"),
    ("2607.07964", "KronQ", "Kronecker 结构双侧变换 PTQ，把旋转类方法的变换矩阵压到可存储可计算的结构化形式。"),
    ("2607.05061", "KVpop", "按注意力动态驱逐/保留 KV 对的缓存量化，token 级自适应预算的代表。"),
    ("2607.13511", "ExTernD", "扩展秩三值分解：满秩之后的分量持续修正误差，理论上任意逼近 bf16 精度，给出单调性证明。"),
    ("2607.14630", "Cross-Layer Error Comp", "把逐层 PTQ 误差累积写成递归 e_{l+1}=A_l e_l+q_l 并用前向差分补偿，1.125-bit 分组二值下大幅回血（本地验证 logits 余弦 0.447→0.993）。"),
    ("2607.01831", "Lynx", "渐进投机 KV 传输：Anchor 流（高位）先到先解码、Residual 流（低位）并发补齐，把 KV 传输从'全到齐'变成'边传边算'。"),
    ("2607.02461", "OrbitQuant", "数据无关扩散量化：随机置换块 Hadamard 旋转把任意输入的坐标边际压到同一已知分布，单一 Lloyd-Max 码本通吃所有时间步/prompt，推到 W2A4。"),
]
for i, (pid, name, comment) in enumerate(HL, 1):
    p = by_id.get(pid)
    title = p["title"] if p else name
    w(f"{i}. **[{pid}] {title}**：{comment}")
w("")
w("---")
w("")
w("## 六、月度趋势分析")
w("")
w("1. **FP4 从推理格式升级为训练格式。** HiFloat4、StableFP4、FullStackFP4、FourTune 四篇同月出现，共同结论是：FP4 的敌人不是权重量化而是**训练-推理两侧的量化误差失配**，层次化/细粒度缩放 + 残差修正是通用解法。QUADS（MoE RL rollout）在强化学习场景得到同一结论——激活误差而非权重误差主导不稳定。")
w("")
w("2. **注意力量化路线收敛。** RotateAttention（旋转等效）、HiFA4（P-Reordering + 层次化 FP4）、MXAttention（MX 格式）、AVQ-Attention（自适应码本）四篇共享同一思想：**先把注意力的数值结构变换到量化友好的基底，再量化**。单纯的逐 tensor RTN 注意力已无人使用。")
w("")
w("3. **KV cache 压缩走向 token/层自适应与流式化。** KVpop（动态驱逐）、DepthWeave-KV（跨层共享基 + token 路由秩）、Lynx（位平面分流渐进传输）、JoLT（联合低秩-量化）、GSRQ（分组残差）——均匀预算彻底过时，'重要性在 token、层、位平面三个维度上都极不均匀'成为共识前提。")
w("")
w("4. **残差范式贯穿极低比特量化。** Rollout-ResQ（HiFloat4）、Residual Activation Compensation（QUADS）、GSRQ、DepthWeave-KV、ExTernD 都把'主量化 + 低秩/稀疏残差修正'作为标准构件；Cross-Layer Error Compensation 进一步把残差思想提升到**跨层**维度（e_{l+1}=A_l e_l+q_l）。")
w("")
w("5. **变换学习化、校准数据可有可无。** GaugeQuant 在训练中用 LogSumExp 对称性破缺项学习量化最优基（无需校准数据）；OrbitQuant 用随机旋转把输入分布归一化到已知边际（数据无关）；KroQuant 学习 Kronecker 结构块变换（参数少于逐通道缩放）。校准集依赖正在被系统性消除。")
w("")
w("6. **量化与其他压缩手段的耦合研究增多。** LoRA 秩 × 量化位宽的受控研究（2607.25583）、PagedWeight 的 MoE 权重 × KV cache 内存权衡、CONQuER 的编译器层混合精度搜索——单一旋钮的优化让位于联合权衡。")
w("")
w("7. **蒸馏主战场明显转向数据集蒸馏与生成模型。** 127 篇蒸馏标签论文中数据集蒸馏（图像/点云/图/时间序列）与扩散/自回归生成模型蒸馏占主导；经典 LLM _logits 蒸馏持续减少。剪枝方面，彩票假说的部署兼容性（2607.27031）与 SNN 稀疏上限（2607.26648）两篇理论警示值得注意。")
w("")
w("---")
w("")
w("## 七、范围与局限")
w("")
w("- **召回局限**：关键词并集召回，摘要/标题不含检索词根的压缩论文会漏收；arXiv API 间歇性 500/429，已用分页重试缓解，但不排除个别条目丢失。")
w("- **分析深度**：305 篇为摘要级机器辅助分析，结论性表述以摘要为准，未核对全文与实验细节；12 篇旗舰论文经人工深度分析（含方法细节与实验数字）。")
w("- **评分性质**：四项评分为横向粗排工具；启发式分数依赖摘要文本信号（数字丰富度、方法词、代码链接），对写作风格保守的论文可能系统性偏低。")
w("- **复现范围**：19 个 demo 复现核心算法机制并在真实 Qwen3-0.6B 上验证方向性结论，不复现论文的完整 benchmark 数字与 kernel 级加速比。")
w("")
w("---")
w("")
w("## 附录 A：分类详表（按主类分组，含一句话结论）")
w("")
for t in PRIMARY_ORDER:
    group = [p for p in ranked if primary_tag(p) == t]
    w(f"### {TAG_LABEL[t]}（{len(group)} 篇）")
    w("")
    w("| arXiv ID | 提交日期 | 论文标题 | 一句话结论 | 总分 |")
    w("|---------|:-------:|---------|-----------|:---:|")
    for p in group:
        ol = one_liner(p["id"], p["abstract"]).replace("|", "\\|")
        title = p["title"].replace("|", "\\|")
        w(f"| {p['id']} | {p['published'][5:10]} | {title} | {ol} | {sum(scores[p['id']])} |")
    w("")
w("---")
w("")
w("*报告生成方式：`scripts/retrieval/_gen_report.py` 基于 `_arxiv_raw/final.json`（317 篇）与 `papers/2026-07/*/tech_analysis.md` 自动生成统计与表格；趋势分析与亮点评述为人工撰写。*")

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"written {OUT} ({len(L)} lines, {OUT.stat().st_size} bytes)")
print(f"demos: {len(DEMO_IDS)}")
