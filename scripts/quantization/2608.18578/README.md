# 2608.18578：Compress and Forget 行为评测复现

本目录复现论文 [Compress and Forget: bitsandbytes Quantization Amplifies Proactive Interference in LLMs](https://arxiv.org/abs/2608.18578) 的主动干扰（proactive interference, PI）评测，并用本机缓存的真实 Qwen3-0.6B 检查量化扰动后的完整生成路径。论文提出的是量化行为评测，不是新的量化器。

## 算法与数据流

1. 为同一人物和属性按时间顺序生成 `k` 条更新，最后一条的值是唯一正确答案。论文层级为 `k ∈ {1,2,4,8,16,32,64,96}`。
2. 主条件包含 mood、favorite color、favorite animal、occupation 四个语义相似属性；控制条件包含 temperature、stock price、page count 三个数字属性。
3. 语义候选在实际句子中用 tokenizer 的字符 offset 检查，只保留恰好覆盖一个 token 的词；数字从固定的 3–998、5–998 或 10–998 范围采样。
4. 每个 prompt 作为无 system prompt 的单个 user message 经过模型原生 chat template。模型用 greedy decoding 自由生成至多 12 个 token，再用论文的首个字母串/有符号整数正则做严格匹配。
5. 同一 seed 的 trials 只构造一次，FP32、INT8 和 NF4 收到字节相同的 prompt；错误答案若命中同一 key 的旧值，则计为 intrusion。
6. 输出按 `mode,attribute,kind,level,trials,accuracy,intrusion_rate` 汇总；`--compact` 输出 CSV 风格记录，否则输出 JSON。

## 量化配置与证据边界

论文在 RTX 3090 上使用 bitsandbytes：FP16；默认 `LLM.int8()`（W8A16、激活异常值阈值 6.0）；以及 NF4 W4、64-weight block、double quantization、FP16 compute。无需校准集，论文也没有 group-size 搜索、混合精度分配或额外异常权重处理；INT4 默认保持 `lm_head` 浮点。

本机为 CPU-only，未安装 bitsandbytes，因此当前数值路径是明确标注的工程替代：

- `fp32`：CPU FP32 基线，不冒充论文 FP16；
- `int8`：backbone Linear 的逐输出通道对称 W8 fake quant；没有 LLM.int8 的激活量化和异常值分解；
- `nf4`：论文 NF4 16 值 codebook、64-weight block absmax，并用每 256 个 scale 的线性 INT8 近似 double quant；
- embedding 与 `lm_head` 保持浮点；量化值反量化回 FP32 后执行，因此不代表 4/8-bit 存储、CUDA kernel 或吞吐；不支持保存/导出量化 checkpoint。

## 运行

快速真实模型验证（默认每个属性/层级 2 次）：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py --self-test --compact
```

论文层级和逐层级 trial budget（每个属性分别为 15/15/20/25/60/50/60/60 次）可用：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py \
  --levels 1,2,4,8,16,32,64,96 --trials 0 --compact
```

这仍是 Qwen3-0.6B 的移植实验，不等于论文三个 3.8–7B instruct 模型、5 seeds、69,225 trials 的统计复现。

## 代码审查与验证（2026-08-21）

### 一致性结论：部分一致

已逐项核对 arXiv v1 HTML/PDF 方法和作者公开源码。行为任务的核心问题、同 key 重绑定、语义/数字对照、旧值 intrusion 归因、backbone-only NF4 方向一致；修正后，任务生成、chat 输入、自由生成和评分流程与公开实现一致。

仍不一致的部分是模型规模/家族、实验预算、硬件和量化 kernel：本目录用 Qwen3-0.6B，而论文用 Qwen2.5-7B-Instruct、Mistral-7B-Instruct-v0.3、Phi-3.5-mini-instruct；本次只做路径级小样本验证；CPU fake quant 不能替代 bitsandbytes LLM.int8/NF4。因此不得用本次数值声称复现论文效应量、显著性或性能。

### 审查发现与修复

- 原实现把层级解释为“旧值数量”，实际生成 `level + 1` 条更新，并额外使用论文不存在的 level 0；现改为论文定义的总更新数 `k`，只接受 1/2/4/8/16/32/64/96。
- 原实现把所有语义词混成一个池、数字限制为 0–9；现恢复作者的 4 个语义属性、3 个数字属性、各自模板和取值范围。
- 原实现对候选 token 做单步受限 logits argmax；现改为原生 chat template、greedy 自由生成最多 12 token、正则提取和 exact match。
- 原实现只对孤立字符串做单 token 检查；现按真实模板中的字符 offset 过滤，并去除候选重复项。
- trials 现只生成一次并跨精度复用，确保逐样本配对；结果按属性和层级报告，不再把不同属性混合。
- INT8 说明修正为 W8 weight-only surrogate，不再暗示等价于含 activation outlier decomposition 的 LLM.int8；FP32 CPU 基线也不再标成 FP16。
- 增加参数合法性检查、真实环境报告、量化层数/元素数、权重 MAE、原始生成样例和高层级跳过说明。

### 实际验证

环境：Apple arm64 CPU，macOS 26.5.2；CUDA/MPS 均不可用；Python 3.9.6、PyTorch 2.8.0、Transformers 4.57.6；`accelerate` 和 `bitsandbytes` 未安装。本机 Hugging Face 缓存中有完整 Qwen/Qwen3-0.6B。

语法、导入、算子与任务生成：

```bash
PYTHONPYCACHEPREFIX=/private/tmp/pycache_quant_20260821 \
/private/tmp/arxiv_tilemix_venv/bin/python -m compileall -q demo.py
```

`fake_int8`、`fake_nf4` 的 shape/finite/误差断言、word/numeric 评分，以及 k=1/4 的更新行数、旧值数和配对 trial 数断言均通过；与作者源码逐项比较的 subjects、7 个模板/问题、候选集合、数字池和 level trial budget 完全一致；`git diff --check` 通过。

真实 Qwen3-0.6B 三精度端到端命令：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
PYTHONPYCACHEPREFIX=/private/tmp/pycache_quant_20260821 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py \
  --self-test --modes fp32,int8,nf4 --levels 1,2,4 \
  --trials 1 --batch-size 4 --compact
```

退出码 0，墙钟 18.37 秒。真实加载 596,049,920 参数；每种模式实际生成 21 个配对 prompt。INT8/NF4 均量化 196 个 backbone Linear、440,401,920 个权重元素，平均绝对权重误差分别为 0.00021444 和 0.00200510；三种模式内部计时分别为 5.46、5.21、5.90 秒。模型加载、词表过滤、trial 构造、整模权重替换、量化后前向/KV-cache 贪心生成和评分均通过。

高干扰 NF4 命令：

```bash
HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
/private/tmp/arxiv_tilemix_venv/bin/python demo.py \
  --modes nf4 --attributes mood,temperature --levels 64,96 \
  --trials 1 --batch-size 1 --compact
```

退出码 0，墙钟 8.93 秒；mood k=64、temperature k=64/96 均完成自由生成。mood k=96 因 Qwen3 实际 offset 过滤后只有 76 个唯一单 token 候选而被明确跳过。该极小样本中三条均答错，mood k=64 和 temperature k=64 命中旧值；这是路径验证结果，不具备统计解释力。

**真实 Qwen3-0.6B：已跑通（FP32 与 CPU INT8/NF4 数值参考路径）。原生 bitsandbytes LLM.int8/NF4：未跑通，真实原因是本机无 CUDA/MPS 且未安装 bitsandbytes；不能声称论文原生量化 kernel 已验证。**
