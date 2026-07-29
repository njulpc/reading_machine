#!/usr/bin/env python3
"""
================================================================================
AI Analyzer Module
================================================================================

Provides AI-powered deep analysis generation for arXiv papers.

Two modes:
1. OpenAI API (requires OPENAI_API_KEY)
2. Local LLM via Ollama (requires ollama installed)
3. Template-based fallback (no AI needed, rule-based)

Usage:
    from ai_analyzer import AIAnalyzer
    
    analyzer = AIAnalyzer(method="openai", model="gpt-4")
    analysis = analyzer.analyze(paper_text, paper_metadata)
    
    # Or use local model
    analyzer = AIAnalyzer(method="ollama", model="llama3")
    analysis = analyzer.analyze(paper_text, paper_metadata)

Requirements:
    pip install openai  # for OpenAI mode
    # or
    pip install ollama  # for local mode
================================================================================
"""

import os
import re
import json
import logging
from typing import Optional, Dict, List
from pathlib import Path


# =============================================================================
# Deep Analysis Prompt Template (same as today's manual analysis)
# =============================================================================

ANALYSIS_PROMPT_TEMPLATE = """你是一位资深的学术研究员和同行评审专家。我已经上传了一篇学术论文，请帮我进行深度剖析。

请严格按照以下结构输出中文分析报告：

## 一、核心速览

### 研究主题
这篇论文试图解决什么核心领域的问题？

### 一句话总结
用精炼的语言总结这篇论文的核心贡献或主要结论。

## 二、研究背景与动机

### 现有研究的痛点
现有研究存在什么痛点、空白或局限性？

### 为什么要做这项研究
作者为什么要开展这项研究？

## 三、核心方法与创新点

### 方法概述
作者提出了什么新模型、新框架或新理论？

### 核心创新（分点列出）
1. **创新1**: [描述]
2. **创新2**: [描述]
3. **创新3**: [描述]

## 四、实验设计与结果

### 数据集与配置
作者使用了什么数据集、基准（Benchmark）或评估指标？

### 核心实验结果
核心实验结果表现如何？是否有足够的证据支撑其结论？

## 五、局限性与未来展望

### 局限性
这项研究还存在哪些明显的不足、假设限制或未解决的问题？

### 未来展望
对未来相关研究有什么启发？

## 六、学术启发

### 可直接迁移的研究思路
这篇论文的思路、方法或实验设计，有哪些可以直接迁移或借鉴到我的研究中？

### 实验设计借鉴
有哪些可借鉴的实验设计元素？

---

论文标题: {title}
论文作者: {authors}
arXiv ID: {arxiv_id}
论文摘要:
{abstract}

论文正文（前15000字符）:
{text}

请基于上述内容撰写深度分析报告。要求：
- 分析必须基于论文实际内容，不要虚构数据
- 每个部分都要具体、深入，不要泛泛而谈
- 实验结果部分请包含具体数字和对比
- 学术启发部分要有可操作性
- 总字数3000-5000字
"""


# =============================================================================
# Code Generation Prompt Template
# =============================================================================

CODE_PROMPT_TEMPLATE = """你是一位PyTorch深度学习专家。基于以下论文的描述，请生成一个完整的、可运行的PyTorch演示代码。

要求：
1. 代码必须是完整可运行的，不能缺少任何类或函数
2. 包含 `if __name__ == "__main__": demo()` 入口
3. 代码顶部包含论文信息注释
4. 代码要有清晰的注释说明
5. 使用标准的PyTorch API，不依赖特殊硬件

论文标题: {title}
arXiv ID: {arxiv_id}

论文核心方法描述:
{text}

请生成一个简化的PyTorch实现，展示论文的核心思想。不需要完全复现论文的所有实验，但要展示关键算法或技术。
"""


# =============================================================================
# AI Analyzer
# =============================================================================

class AIAnalyzer:
    """
    AI-powered paper analyzer.
    
    Supports multiple backends:
    - openai: GPT-4/Claude via API
    - ollama: Local models (llama3, qwen2, etc.)
    - template: Rule-based fallback (no AI needed)
    """
    
    def __init__(self, method: str = "template", model: str = "gpt-4"):
        self.method = method
        self.model = model
        self._client = None
        
        if method == "openai":
            self._init_openai()
        elif method == "ollama":
            self._init_ollama()
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            self._client = OpenAI(api_key=api_key)
            logging.info(f"OpenAI client initialized (model: {self.model})")
        except ImportError:
            logging.error("openai package not installed. Run: pip install openai")
            raise
    
    def _init_ollama(self):
        """Initialize Ollama client."""
        try:
            import ollama
            self._client = ollama
            # Test connection
            self._client.list()
            logging.info(f"Ollama client initialized (model: {self.model})")
        except ImportError:
            logging.error("ollama package not installed. Run: pip install ollama")
            raise
        except Exception as e:
            logging.error(f"Ollama connection failed: {e}")
            raise
    
    def analyze(self, paper: Dict) -> str:
        """
        Generate deep analysis for a paper.
        
        Args:
            paper: Dict with keys: title, authors, arxiv_id, abstract, text
        
        Returns:
            Markdown analysis string
        """
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            title=paper.get("title", ""),
            authors=paper.get("authors", ""),
            arxiv_id=paper.get("arxiv_id", ""),
            abstract=paper.get("abstract", "")[:2000],
            text=paper.get("text", "")[:15000]
        )
        
        if self.method == "openai":
            return self._call_openai(prompt)
        elif self.method == "ollama":
            return self._call_ollama(prompt)
        else:
            return self._template_analysis(paper)
    
    def generate_code(self, paper: Dict) -> Optional[str]:
        """
        Generate standalone PyTorch code for a paper.
        
        Returns None if paper doesn't match <=4bit/<=8bit criteria.
        """
        # Check if paper is about quantization
        text = f"{paper.get('title', '')} {paper.get('abstract', '')}".lower()
        
        weight_4bit = ['int4', 'fp4', '4-bit', '4bit', 'nf4', 'mxfp4', 'one-bit', '1-bit', 'binary']
        activation_8bit = ['int8', '8-bit', '8bit', 'integer-only', 'fixed-point']
        
        is_quant = any(kw in text for kw in weight_4bit + activation_8bit)
        
        if not is_quant:
            return None
        
        prompt = CODE_PROMPT_TEMPLATE.format(
            title=paper.get("title", ""),
            arxiv_id=paper.get("arxiv_id", ""),
            text=paper.get("text", "")[:8000]
        )
        
        if self.method == "openai":
            code = self._call_openai(prompt, max_tokens=4000)
        elif self.method == "ollama":
            code = self._call_ollama(prompt)
        else:
            code = self._template_code(paper)
        
        # Clean up code block markers
        code = re.sub(r'^```python\n', '', code)
        code = re.sub(r'\n```$', '', code)
        
        return code
    
    def _call_openai(self, prompt: str, max_tokens: int = 4000) -> str:
        """Call OpenAI API."""
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert academic researcher and PyTorch developer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama local model."""
        response = self._client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert academic researcher."},
                {"role": "user", "content": prompt}
            ]
        )
        return response['message']['content']
    
    def _template_analysis(self, paper: Dict) -> str:
        """
        Rule-based analysis template (fallback when no AI available).
        
        This generates a structured but less detailed analysis.
        """
        title = paper.get("title", "")
        arxiv_id = paper.get("arxiv_id", "")
        authors = paper.get("authors", "")
        abstract = paper.get("abstract", "")
        
        # Extract keywords from text
        text_lower = f"{title} {abstract}".lower()
        
        techniques = []
        if "quantization" in text_lower or "quantized" in text_lower:
            techniques.append("量化 (Quantization)")
        if "pruning" in text_lower or "sparse" in text_lower:
            techniques.append("剪枝 (Pruning)")
        if "distillation" in text_lower:
            techniques.append("知识蒸馏 (Knowledge Distillation)")
        if "efficient" in text_lower or "edge" in text_lower:
            techniques.append("高效推理 (Efficient Inference)")
        
        # Determine precision
        precision = []
        if "int4" in text_lower or "fp4" in text_lower or "4-bit" in text_lower:
            precision.append("4-bit")
        if "int8" in text_lower or "8-bit" in text_lower:
            precision.append("8-bit")
        
        return f"""# 技术深度分析：{title} (arXiv:{arxiv_id})

> **论文**: {title}
> **作者**: {authors}
> **arXiv**: https://arxiv.org/abs/{arxiv_id}

---

## 一、核心速览

### 研究主题

本文研究{'量化和模型压缩' if techniques else '深度学习模型优化'}领域的问题，{'重点探索' + '、'.join(techniques) if techniques else '探索提升模型效率的新方法'}。

### 一句话总结

{abstract[:150]}...

---

## 二、研究背景与动机

### 现有研究的痛点

- 当前大模型部署面临内存和计算资源的双重挑战
- 现有压缩方法往往在精度和效率之间存在trade-off
- 缺乏系统性的{'、'.join(techniques) if techniques else '模型优化'}联合优化方案

### 为什么要做这项研究

作者旨在解决{'、'.join(techniques) if techniques else '模型压缩'}在实际部署中的瓶颈问题，提出更高效、更实用的解决方案。

---

## 三、核心方法与创新点

### 方法概述

基于论文摘要和标题，本文提出了针对{'、'.join(techniques) if techniques else '深度学习模型'}的新方法。

### 核心创新

1. **{'、'.join(techniques) if techniques else '新的优化方法'}**: 针对现有方法的局限性提出改进
2. **效率与精度的平衡**: 在保持模型性能的同时降低资源消耗
{f"3. **低比特量化**: 探索{precision[0] if precision else '低比特'}量化策略" if precision else ""}

---

## 四、实验设计与结果

### 数据集与配置

- 使用了标准基准数据集进行评估
- 在多种硬件配置下验证方法有效性

### 核心实验结果

- 相比基线方法在效率和精度方面均有提升
- {'在低比特量化下（' + '、'.join(precision) + '）保持了较好的模型性能' if precision else '在不同压缩比下均表现出色'}

---

## 五、局限性与未来展望

### 局限性

- 实验主要在特定数据集上进行，泛化能力有待验证
- 方法可能需要针对特定硬件进行优化
- 某些极端场景下的性能未充分探索

### 未来展望

- 扩展到更大规模的模型
- 结合更多压缩技术进行联合优化
- 在实际边缘设备上进行更广泛的部署验证

---

## 六、学术启发

### 可直接迁移的研究思路

1. **{'、'.join(techniques) if techniques else '压缩技术'}的应用**: 可将本文方法迁移到其他视觉/语言任务
2. **低比特训练策略**: 对量化感知训练（QAT）和训练后量化（PTQ）的改进思路值得借鉴

### 实验设计借鉴

- 严格的跨域评估协议
- 多硬件平台验证
- 详细的消融实验设计

---

> **注意**: 本分析为自动生成的模板版本。如需更深入的分析，请配置 OpenAI API 或本地 LLM。

*分析时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}*
*分析人: AI Assistant (Auto-generated)*
"""
    
    def _template_code(self, paper: Dict) -> str:
        """Generate template code based on paper keywords."""
        arxiv_id = paper.get("arxiv_id", "")
        title = paper.get("title", "")
        text_lower = f"{title} {paper.get('abstract', '')}".lower()
        
        # Determine code template based on keywords
        if "fp4" in text_lower or "2d block" in text_lower:
            return self._fp4_template(arxiv_id, title)
        elif "angle" in text_lower or "self-distill" in text_lower:
            return self._qat_template(arxiv_id, title)
        elif "integer" in text_lower or "int8" in text_lower:
            return self._int8_template(arxiv_id, title)
        elif "pruning" in text_lower:
            return self._pruning_template(arxiv_id, title)
        else:
            return self._generic_quant_template(arxiv_id, title)
    
    def _fp4_template(self, arxiv_id: str, title: str) -> str:
        return f'''#!/usr/bin/env python3
"""
Paper: {arxiv_id} - {title[:50]}
Auto-generated FP4 quantization demo
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class FP4Quantizer:
    """Simple FP4 block quantizer (simplified version)."""
    def __init__(self, block_size=32):
        self.block_size = block_size
    
    def quantize(self, x):
        # Simplified: use per-channel scaling
        scale = x.abs().max() / 6.0
        scale = scale.clamp_min(1e-8)
        x_q = torch.clamp(torch.round(x / scale), -6, 6)
        return x_q * scale

class FP4Linear(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features))
        self.quantizer = FP4Quantizer()
    
    def forward(self, x):
        w_q = self.quantizer.quantize(self.weight)
        return F.linear(x, w_q, self.bias)

def demo():
    layer = FP4Linear(512, 256)
    x = torch.randn(4, 512)
    out = layer(x)
    print(f"Input: {{x.shape}} -> Output: {{out.shape}}")
    print(f"FP4 quantized layer works!")

if __name__ == "__main__":
    demo()
'''
    
    def _qat_template(self, arxiv_id: str, title: str) -> str:
        return f'''#!/usr/bin/env python3
"""
Paper: {arxiv_id} - {title[:50]}
Auto-generated QAT demo
"""

import torch
import torch.nn as nn

class QATLinear(nn.Module):
    """Linear layer with fake quantization for QAT."""
    def __init__(self, in_features, out_features, bits=4):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bits = bits
        self.qmax = 2 ** (bits - 1) - 1
    
    def fake_quantize(self, w):
        scale = w.abs().max() / self.qmax
        w_q = torch.clamp(torch.round(w / scale), -self.qmax, self.qmax)
        # STE: straight-through estimator
        return w + (w_q * scale - w).detach()
    
    def forward(self, x):
        w_q = self.fake_quantize(self.weight)
        return torch.matmul(x, w_q.t())

def demo():
    layer = QATLinear(512, 256, bits=4)
    x = torch.randn(4, 512, requires_grad=True)
    out = layer(x)
    loss = out.sum()
    loss.backward()
    print(f"QAT layer with gradient: {{layer.weight.grad is not None}}")

if __name__ == "__main__":
    demo()
'''
    
    def _int8_template(self, arxiv_id: str, title: str) -> str:
        return f'''#!/usr/bin/env python3
"""
Paper: {arxiv_id} - {title[:50]}
Auto-generated INT8 quantization demo
"""

import torch
import torch.nn as nn

class INT8Quantizer:
    def quantize(self, x):
        scale = x.abs().max() / 127.0
        x_q = torch.clamp(torch.round(x / scale), -128, 127)
        return x_q * scale

class INT8Linear(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features))
    
    def forward(self, x):
        quantizer = INT8Quantizer()
        w_q = quantizer.quantize(self.weight)
        return torch.matmul(x, w_q.t()) + self.bias

def demo():
    layer = INT8Linear(512, 256)
    x = torch.randn(4, 512)
    out = layer(x)
    print(f"INT8 quantized output: {{out.shape}}")

if __name__ == "__main__":
    demo()
'''
    
    def _pruning_template(self, arxiv_id: str, title: str) -> str:
        return f'''#!/usr/bin/env python3
"""
Paper: {arxiv_id} - {title[:50]}
Auto-generated pruning demo
"""

import torch
import torch.nn as nn

def structured_prune(weight, pruning_ratio=0.5):
    """Structured channel pruning."""
    importance = weight.abs().sum(dim=1)
    num_keep = int(len(importance) * (1 - pruning_ratio))
    keep_idx = torch.argsort(importance, descending=True)[:num_keep]
    return weight[keep_idx], keep_idx

class PrunedLinear(nn.Module):
    def __init__(self, in_features, out_features, prune_ratio=0.5):
        super().__init__()
        self.full_weight = nn.Parameter(torch.randn(out_features, in_features))
        self.prune_ratio = prune_ratio
        self.mask = torch.ones(out_features, 1)
    
    def forward(self, x):
        if self.training:
            w = self.full_weight * self.mask
        else:
            w, _ = structured_prune(self.full_weight, self.prune_ratio)
        return torch.matmul(x, w.t())

def demo():
    layer = PrunedLinear(512, 256, prune_ratio=0.5)
    x = torch.randn(4, 512)
    out = layer(x)
    print(f"Pruned output: {{out.shape}}")

if __name__ == "__main__":
    demo()
'''
    
    def _generic_quant_template(self, arxiv_id: str, title: str) -> str:
        return f'''#!/usr/bin/env python3
"""
Paper: {arxiv_id} - {title[:50]}
Auto-generated quantization demo
"""

import torch
import torch.nn as nn

class QuantizedLinear(nn.Module):
    """Generic quantized linear layer."""
    def __init__(self, in_features, out_features, bits=8):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bits = bits
        self.qmax = 2 ** (bits - 1) - 1
    
    def quantize(self, w):
        scale = w.abs().max() / self.qmax
        w_q = torch.clamp(torch.round(w / scale), -self.qmax, self.qmax)
        return w_q * scale
    
    def forward(self, x):
        w_q = self.quantize(self.weight)
        return torch.matmul(x, w_q.t())

def demo():
    layer = QuantizedLinear(512, 256, bits=8)
    x = torch.randn(4, 512)
    out = layer(x)
    print(f"Quantized ({{layer.bits}}-bit) output: {{out.shape}}")

if __name__ == "__main__":
    demo()
'''


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """Test the analyzer."""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["openai", "ollama", "template"], default="template")
    parser.add_argument("--model", default="gpt-4")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    
    analyzer = AIAnalyzer(method=args.method, model=args.model)
    
    if args.test:
        # Test with a sample paper
        paper = {
            "title": "Stable FP4 Training via Transposition-Invariant Block Quantization",
            "authors": "Rahimifar et al.",
            "arxiv_id": "2607.24953",
            "abstract": "We propose 2D block FP4 quantization...",
            "text": "FP4 quantization is challenging due to limited dynamic range..."
        }
        
        print("Testing analysis generation...")
        analysis = analyzer.analyze(paper)
        print(analysis[:1000])
        
        print("\nTesting code generation...")
        code = analyzer.generate_code(paper)
        print(code[:500] if code else "No code generated")


if __name__ == "__main__":
    main()
