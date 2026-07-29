# 技术深度分析：Bits and Memories (arXiv:2607.25451)

> **论文**: Bits and Memories: Measuring Verbatim Extraction Across LLM Quantization  
> **作者**: Akshay Sasi (Independent Researcher)  
> **核心贡献**: 首次系统测量LLM量化对逐字记忆提取的影响，发现量化是"选择性遗忘者"——记忆比能力遗忘更快，但不足以作为隐私防御

---

## 一、研究动机与核心问题

### 1.1 两个已知事实

1. **LLM会记忆训练数据**: 给定正确前缀，模型会逐字继续训练集中的段落
2. **几乎所有部署模型都被量化**: 8-bit、4-bit甚至更低，使大模型能在消费级GPU上运行

### 1.2 核心问题

> **量化后，模型记忆的数据去哪了？**

- 如果记忆被抹去 → 量化是免费的隐私保护
- 如果记忆保留 → "压缩模型更安全"的假设是错的

### 1.3 现有工作的局限

已有工作通过**成员推断攻击(MIA)**衡量量化对隐私的影响，但：
- MIA只能判断某文档是否在训练集中
- 而真正的威胁是**逐字提取(verbatim extraction)**——能完整打印出文档内容
- 两者响应不同：知道在训练集 ≠ 能打印出来

---

## 二、实验方法

### 2.1 测量协议

```
┌─────────────────────────────────────────────────────────┐
│  逐字提取测量协议                                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 已知记忆序列 (64 tokens, 来自Pile训练集)             │
│     ├─ 前32 tokens → Prompt                             │
│     └─ 后32 tokens → Target                             │
│                                                         │
│  2. 将Prompt输入量化模型                                 │
│     → 贪婪解码生成32个新tokens                           │
│                                                         │
│  3. 检查生成的32 tokens是否与Target完全匹配               │
│     → 精确匹配率 = 成功提取率                            │
│                                                         │
│  4. 同时测量困惑度(perplexity)作为能力控制                │
│     → 区分"遗忘记忆" vs "模型坏了"                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 2.2 实验设置

| 组件 | 配置 |
|------|------|
| **模型** | Pythia 160M, 410M, 1B (去重版本) |
| **训练数据** | The Pile (公开，可验证) |
| **记忆序列** | 官方发布的已知记忆集合 (64-token序列) |
| **精度等级** | FP32 → FP16 → INT8 → NF4/FP4/RTN4 |
| **量化方法** | bitsandbytes (NF4, FP4) + 自研RTN (独立验证) |
| **能力评估** | WikiText-2 (OOD) + Pile样本 (ID) |

### 2.3 核心度量：选择性 (Selectivity)

定义保留分数：
```
m(q) = extraction(q) / extraction(ref)      # 记忆保留率
c(q) = perplexity(ref) / perplexity(q)      # 能力保留率
```

选择性：
```python
# 伪代码: 选择性计算
def compute_selectivity(extraction_rate, perplexity, ref_extraction, ref_perplexity):
    """
    extraction_rate: 量化模型的精确匹配率
    perplexity: 量化模型的困惑度 (越低越好)
    ref_extraction: 全精度参考模型的精确匹配率
    ref_perplexity: 全精度参考模型的困惑度
    """
    m = extraction_rate / ref_extraction  # 记忆保留率 [0, 1]
    c = ref_perplexity / perplexity       # 能力保留率 [0, 1]
    
    # 选择性: log(m) / log(c)
    # > 1: 记忆比能力遗忘更快 (选择性遗忘)
    # = 1: 两者同步遗忘
    # < 1: 能力比记忆遗忘更快
    import math
    selectivity = math.log(m) / math.log(c)
    
    return m, c, selectivity
```

---

## 三、核心发现

### 3.1 发现一：量化是选择性遗忘者

**记忆遗忘比能力遗忘更快**。

| 模型 | 精度 | 精确匹配率 | Pile PPL | 记忆保留m | 能力保留c | **选择性s** |
|------|------|-----------|---------|----------|----------|------------|
| 160M | FP32 | 75.6% | 12.27 | 1.000 | 1.000 | — |
| | FP16 | 74.6% | 12.37 | 0.987 | 0.992 | — |
| | INT8 | 73.4% | 12.48 | 0.971 | 0.983 | **1.7** |
| | NF4 | 29.4% | 17.33 | 0.389 | 0.708 | **2.7** |
| | FP4 | 17.6% | 21.22 | 0.233 | 0.578 | **2.7** |
| 410M | FP32 | 83.4% | 8.88 | 1.000 | 1.000 | — |
| | FP16 | 82.2% | 8.89 | 0.986 | 0.999 | — |
| | INT8 | 81.0% | 8.98 | 0.971 | 0.989 | **2.6** |
| | NF4 | 22.8% | 15.35 | 0.273 | 0.579 | **2.4** |
| | RTN4 | 17.6% | 18.49 | 0.211 | 0.480 | **2.1** |
| | FP4 | 13.2% | 20.59 | 0.158 | 0.431 | **2.2** |
| 1B | FP16 | 83.0% | 7.58 | 1.000 | 1.000 | — |
| | INT8 | 82.6% | 7.60 | 0.995 | 0.997 | **1.5** |
| | NF4 | 59.6% | 7.90 | 0.718 | 0.959 | **8.0** |
| | RTN4 | 49.8% | 8.32 | 0.600 | 0.910 | **5.4** |
| | FP4 | 46.0% | 8.32 | 0.554 | 0.911 | **6.3** |

**关键观察**:
- 所有量化配置的选择性 **s > 1**，即记忆总是比能力遗忘更快
- 1B模型的选择性最高（~8），但也是最危险的

### 3.2 发现二：但量化不是隐私防御

**1B模型在4-bit时仍然提取了72%的记忆内容，而只损失了4%的能力**。

```
┌────────────────────────────────────────────────────────────┐
│  1B模型量化后的隐私状态                                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  精度: NF4 (4-bit)                                         │
│  能力损失: ~4% (PPL 7.58 → 7.90, 几乎无损)                  │
│  记忆保留: 72% (仍能提取近3/4的记忆序列)                     │
│  选择性: 8.0 (记忆遗忘很快，但基数太高)                      │
│                                                            │
│  结论: 压缩后模型几乎没变差，但大多数记忆仍在                 │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**规模趋势**（最令人担忧）:
- NF4下记忆保留率：160M为39% → 410M为27% → **1B为72%**
- **更大的模型吸收量化噪声更好，记忆内容几乎完好无损**
- 实际部署的模型比1B大1-2个数量级

### 3.3 发现三：量化不是翻转边界序列，而是缩短忠实复现长度

- 全精度时：平均正确前缀长度 ~28/32 tokens
- NF4时：平均正确前缀长度 ~12/32 tokens
- 说明量化系统性破坏记忆的精细权重配置

---

## 四、可复现的评估代码

```python
"""
Bits and Memories: 量化对逐字记忆提取的影响评估
基于论文 arXiv:2607.25451 的方法复现
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
from pathlib import Path
from typing import List, Tuple


class MemorizationEvaluator:
    """
    评估LLM量化后的逐字记忆提取能力
    
    方法:
    1. 使用已知记忆序列（前32 tokens为prompt，后32 tokens为target）
    2. 模型贪婪解码32 tokens
    3. 检查精确匹配率
    4. 同时测量困惑度作为能力控制
    """
    
    def __init__(self, model_name: str, device: str = "cuda"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            device_map=device
        )
        self.model.eval()
    
    def load_memorized_sequences(self, path: str, sample_size: int = 1000) -> List[dict]:
        """
        加载已知记忆序列
        
        格式: [{"text": "64-token sequence", "source": "..."}, ...]
        """
        with open(path) as f:
            sequences = json.load(f)
        
        import random
        random.seed(42)
        return random.sample(sequences, min(sample_size, len(sequences)))
    
    def split_sequence(self, text: str, prompt_len: int = 32) -> Tuple[List[int], List[int]]:
        """
        将64-token序列分为prompt (32) 和 target (32)
        
        返回: (prompt_ids, target_ids)
        """
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        
        # 确保有64个tokens
        if len(tokens) < 64:
            return None, None
        
        prompt_ids = tokens[:prompt_len]
        target_ids = tokens[prompt_len:prompt_len + 32]
        
        return prompt_ids, target_ids
    
    def extract_continuation(self, prompt_ids: List[int], gen_len: int = 32) -> List[int]:
        """
        贪婪解码生成continuation
        
        Args:
            prompt_ids: 输入token IDs
            gen_len: 生成长度
        
        Returns:
            生成的token IDs
        """
        input_ids = torch.tensor([prompt_ids], device=self.device)
        
        with torch.no_grad():
            output = self.model.generate(
                input_ids,
                max_new_tokens=gen_len,
                do_sample=False,  # 贪婪解码
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # 提取新生成的部分
        generated_ids = output[0][len(prompt_ids):].tolist()
        return generated_ids
    
    def evaluate_extraction(self, sequences: List[dict]) -> dict:
        """
        评估逐字记忆提取率
        
        返回: {
            "exact_match_rate": float,
            "mean_correct_prefix": float,
            "per_token_accuracy": float,
            "total_sequences": int
        }
        """
        exact_matches = 0
        total = 0
        prefix_lengths = []
        token_correct = 0
        token_total = 0
        
        for seq in sequences:
            prompt_ids, target_ids = self.split_sequence(seq["text"])
            if prompt_ids is None:
                continue
            
            # 生成continuation
            generated_ids = self.extract_continuation(prompt_ids)
            
            # 检查精确匹配
            if len(generated_ids) >= len(target_ids):
                match = (generated_ids[:len(target_ids)] == target_ids)
                if match:
                    exact_matches += 1
                
                # 计算正确前缀长度
                prefix_len = 0
                for g, t in zip(generated_ids, target_ids):
                    if g == t:
                        prefix_len += 1
                    else:
                        break
                prefix_lengths.append(prefix_len)
                
                # 逐token准确率
                for g, t in zip(generated_ids[:len(target_ids)], target_ids):
                    token_total += 1
                    if g == t:
                        token_correct += 1
            
            total += 1
        
        return {
            "exact_match_rate": exact_matches / total if total > 0 else 0,
            "mean_correct_prefix": sum(prefix_lengths) / len(prefix_lengths) if prefix_lengths else 0,
            "per_token_accuracy": token_correct / token_total if token_total > 0 else 0,
            "total_sequences": total
        }
    
    def evaluate_perplexity(self, texts: List[str], max_length: int = 512) -> float:
        """
        评估困惑度
        
        使用滑动窗口计算
        """
        total_loss = 0
        total_tokens = 0
        
        for text in texts:
            tokens = self.tokenizer.encode(text, return_tensors="pt").to(self.device)
            
            # 滑动窗口
            stride = 512
            seq_len = tokens.size(1)
            
            for begin in range(0, seq_len, stride):
                end = min(begin + max_length, seq_len)
                chunk = tokens[:, begin:end]
                
                with torch.no_grad():
                    outputs = self.model(chunk, labels=chunk)
                    loss = outputs.loss
                    num_tokens = (chunk != self.tokenizer.pad_token_id).sum().item()
                    
                    total_loss += loss.item() * num_tokens
                    total_tokens += num_tokens
        
        avg_loss = total_loss / total_tokens if total_tokens > 0 else float('inf')
        perplexity = torch.exp(torch.tensor(avg_loss)).item()
        
        return perplexity
    
    def compute_selectivity(
        self,
        extraction_q: float,
        perplexity_q: float,
        extraction_ref: float,
        perplexity_ref: float
    ) -> Tuple[float, float, float]:
        """
        计算选择性
        
        返回: (m, c, s)
        m: 记忆保留率
        c: 能力保留率
        s: 选择性 (log(m) / log(c))
        """
        import math
        
        m = extraction_q / extraction_ref if extraction_ref > 0 else 0
        c = perplexity_ref / perplexity_q if perplexity_q > 0 else 0
        
        if m > 0 and c > 0 and c != 1:
            s = math.log(m) / math.log(c)
        else:
            s = float('nan')
        
        return m, c, s


# === 量化模型评估 ===

def evaluate_quantized_model(
    model_name: str,
    quant_config: dict,
    memorized_sequences: List[dict],
    eval_texts: List[str]
) -> dict:
    """
    评估量化后的模型的记忆提取和能力
    
    Args:
        model_name: 基础模型名称
        quant_config: 量化配置
        memorized_sequences: 已知记忆序列
        eval_texts: 用于困惑度评估的文本
    
    返回:
        {
            "extraction": {...},
            "perplexity": float,
            "m": float,
            "c": float,
            "s": float
        }
    """
    
    # 加载并量化模型
    from transformers import BitsAndBytesConfig
    
    if quant_config["type"] == "nf4":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
    elif quant_config["type"] == "int8":
        bnb_config = BitsAndBytesConfig(load_in_8bit=True)
    elif quant_config["type"] == "fp4":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="fp4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
    else:
        bnb_config = None
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.float32 if bnb_config is None else None
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # 评估记忆提取
    evaluator = MemorizationEvaluator(model_name)
    evaluator.model = model
    evaluator.tokenizer = tokenizer
    
    extraction_results = evaluator.evaluate_extraction(memorized_sequences)
    perplexity = evaluator.evaluate_perplexity(eval_texts)
    
    return {
        "extraction": extraction_results,
        "perplexity": perplexity
    }


# === RTN量化器 (论文中的独立验证方法) ===

class RTNQuantizer:
    """
    组-wise对称Round-to-Nearest量化器
    
    论文中的独立实现，不依赖bitsandbytes
    """
    
    def __init__(self, bits: int = 4, group_size: int = 128):
        self.bits = bits
        self.group_size = group_size
        self.qmax = 2 ** (bits - 1) - 1
        self.qmin = -(2 ** (bits - 1))
    
    def quantize(self, weight: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        对权重进行RTN量化
        
        返回: (quantized_weight, scales)
        """
        orig_shape = weight.shape
        
        # 重塑为 [num_groups, group_size]
        if weight.numel() % self.group_size != 0:
            # 填充
            pad_size = self.group_size - (weight.numel() % self.group_size)
            weight = torch.nn.functional.pad(weight.flatten(), (0, pad_size))
        
        w = weight.reshape(-1, self.group_size)
        
        # 计算每组的尺度
        w_max = w.abs().amax(dim=1, keepdim=True)
        scales = w_max / self.qmax
        
        # 量化
        w_quant = torch.clamp(
            torch.round(w / scales),
            self.qmin,
            self.qmax
        )
        
        # 反量化 (用于推理)
        w_dequant = w_quant * scales
        
        # 重塑回原始形状
        w_dequant = w_dequant.flatten()[:orig_shape.numel()].reshape(orig_shape)
        
        return w_dequant, scales
    
    def quantize_model(self, model: torch.nn.Module):
        """量化模型中的所有线性层"""
        for name, module in model.named_modules():
            if isinstance(module, torch.nn.Linear):
                w_dequant, _ = self.quantize(module.weight.data)
                module.weight.data = w_dequant


# === 主评估流程 ===

def main():
    """
    主评估流程示例
    """
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="EleutherAI/pythia-160m-deduped")
    parser.add_argument("--precision", choices=["fp32", "fp16", "int8", "nf4", "fp4", "rtn4"])
    parser.add_argument("--memorized_seqs", required=True, help="Path to memorized sequences JSON")
    parser.add_argument("--eval_corpus", required=True, help="Path to evaluation corpus")
    args = parser.parse_args()
    
    # 加载记忆序列
    with open(args.memorized_seqs) as f:
        memorized_sequences = json.load(f)
    
    # 加载评估文本
    with open(args.eval_corpus) as f:
        eval_texts = [line.strip() for line in f if line.strip()]
    
    # 评估
    if args.precision == "rtn4":
        # 自研RTN量化
        model = AutoModelForCausalLM.from_pretrained(args.model)
        quantizer = RTNQuantizer(bits=4, group_size=128)
        quantizer.quantize_model(model)
        
        evaluator = MemorizationEvaluator(args.model)
        evaluator.model = model.to(evaluator.device)
        
        extraction = evaluator.evaluate_extraction(memorized_sequences)
        perplexity = evaluator.evaluate_perplexity(eval_texts[:100])
    else:
        # bitsandbytes量化
        quant_config = {"type": args.precision if args.precision != "fp32" else None}
        results = evaluate_quantized_model(
            args.model, quant_config,
            memorized_sequences, eval_texts[:100]
        )
        extraction = results["extraction"]
        perplexity = results["perplexity"]
    
    print(f"Model: {args.model}")
    print(f"Precision: {args.precision}")
    print(f"Exact Match Rate: {extraction['exact_match_rate']:.3f}")
    print(f"Mean Correct Prefix: {extraction['mean_correct_prefix']:.1f}")
    print(f"Per-token Accuracy: {extraction['per_token_accuracy']:.3f}")
    print(f"Perplexity: {perplexity:.2f}")


if __name__ == "__main__":
    main()
```

---

## 五、关键发现总结

### 5.1 选择性遗忘的可视化

```
能力保留(c) →
  1.0 ┤ ●──●──● (FP32→FP16→INT8, 几乎无损)
      │     \
  0.9 ┤      ● (1B INT8)
      │       \
  0.8 ┤        ● (1B NF4: 能力只损失4%!)
      │         ╲
  0.7 ┤    ●     (160M/410M NF4)
      │     ╲
  0.6 ┤      ╲   ● (1B FP4)
      │       ╲  │
  0.5 ┤        ╲ │
      │     ●   ╲│ (160M NF4)
  0.4 ┤      ╲   ●
      │       ╲  │
  0.3 ┤    ●   ╲ │ (410M NF4)
      │     ╲   ╲│
  0.2 ┤      ╲   ●
      │       ╲  │
  0.1 ┤    ●   ╲ │ (410M FP4)
      │     ╲   ╲│
  0.0 ┼─────┴───┴─┴──┴──┴──┴──┴── 记忆保留(m) →
       0.0  0.2  0.4  0.6  0.8  1.0
       
  所有点都在对角线下方 → s > 1 (选择性遗忘)
  但1B NF4在右上角: 能力强、记忆也多 → 不安全的隐私状态
```

### 5.2 规模效应的恐怖含义

```
部署模型规模: ~70B-100B+ (比1B大70-100倍)

根据趋势推断:
  - 4-bit量化后能力损失: <1%
  - 4-bit量化后记忆保留: >90%
  
  → 压缩后的模型几乎和新的一样好，
    但也几乎和新的一样会泄露训练数据
```

### 5.3 对实践的建议

| 建议 | 理由 |
|------|------|
| **不要指望量化保护隐私** | 记忆内容大部分保留 |
| **关注提取率而非MIA** | 提取才是真正的法律/声誉威胁 |
| **量化+unlearning不够** | Zhang et al. 2024: 量化可恢复已unlearn的知识 |
| **需要专门的记忆删除方法** | 量化不能替代targeted unlearning |

---

## 六、科学启示

> **记忆似乎存储在权重的更"精度脆弱"区域，而能力分布更冗余。**

- 逐字记忆依赖**精细调谐的权重配置**，量化噪声会破坏这些配置
- 一般能力**分布更冗余**，能在舍入中存活
- 更大模型的**冗余度足以保护甚至精细配置**
- 暗示记忆和泛化在权重中是**物理可分离**的

---

*分析时间: 2026-07-29*  
*分析人: AI Assistant*
