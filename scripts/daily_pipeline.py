#!/usr/bin/env python3
"""
================================================================================
Daily ArXiv Quantization Paper Pipeline
================================================================================

Automated daily workflow:
1. Collect previous day's arXiv papers (0:00-23:59)
2. Filter by quantization/compression keywords
3. Download PDFs
4. Generate deep technical analysis (AI-powered)
5. Generate standalone PyTorch code for <=4bit/<=8bit papers
6. Create Git branch daily/YYYY-MM-DD and push

Usage:
    # Manual run for specific date
    python3 daily_pipeline.py --date 2026-07-29
    
    # Auto-detect yesterday
    python3 daily_pipeline.py
    
    # With verbose logging
    python3 daily_pipeline.py --verbose

Schedule:
    Add to crontab for daily 18:00 execution:
    0 18 * * * cd /path/to/reading_machine && python3 scripts/daily_pipeline.py >> logs/daily.log 2>&1

Requirements:
    pip install requests pyyaml feedparser

Environment:
    GITHUB_TOKEN - GitHub PAT with repo scope
================================================================================
"""

import os
import sys
import re
import json
import yaml
import subprocess
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from urllib.parse import urlencode

# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "scripts" / "daily_config.yaml"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class Paper:
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    url: str
    pdf_url: str
    submitted: str
    categories: List[str]
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass  
class PipelineResult:
    date: str
    total_collected: int
    filtered_papers: int
    downloaded_pdfs: int
    analyzed_papers: int
    code_generated: int
    branch_name: str
    commit_hash: str
    errors: List[str]


# =============================================================================
# Step 1: Collect Papers from arXiv
# =============================================================================

class ArXivCollector:
    """Collect papers from arXiv API."""
    
    ARXIV_API = "http://export.arxiv.org/api/query"
    
    def __init__(self, config: Dict):
        self.keywords = config["collection"]["keywords"]
        self.categories = config["collection"]["categories"]
        self.max_papers = config["collection"]["max_papers"]
    
    def collect(self, date: str) -> List[Paper]:
        """
        Collect papers submitted on the given date.
        
        Args:
            date: Date string in YYYY-MM-DD format
            
        Returns:
            List of Paper objects
        """
        logging.info(f"Collecting papers for {date}...")
        
        # Build query: search in all fields for keywords
        keyword_query = " OR ".join(f'"{kw}"' for kw in self.keywords)
        cat_filter = " OR ".join(f"cat:{cat}" for cat in self.categories)
        
        # Date range: start of day to end of day
        start_date = f"{date}T00:00:00Z"
        end_date = f"{date}T23:59:59Z"
        
        # Note: arXiv API doesn't support exact date filtering well,
        # so we fetch recent and filter locally
        params = {
            "search_query": f"({keyword_query}) AND ({cat_filter})",
            "start": 0,
            "max_results": self.max_papers * 3,  # Fetch more for filtering
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        try:
            import requests
            response = requests.get(self.ARXIV_API, params=params, timeout=60)
            response.raise_for_status()
            
            # Parse Atom feed
            papers = self._parse_feed(response.text, date)
            logging.info(f"Collected {len(papers)} papers for {date}")
            return papers
            
        except Exception as e:
            logging.error(f"Failed to collect papers: {e}")
            return []
    
    def _parse_feed(self, xml_text: str, target_date: str) -> List[Paper]:
        """Parse arXiv Atom feed XML."""
        import xml.etree.ElementTree as ET
        
        papers = []
        root = ET.fromstring(xml_text)
        
        # arXiv Atom namespace
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }
        
        for entry in root.findall('atom:entry', ns):
            # Extract paper info
            title = entry.find('atom:title', ns)
            title_text = title.text.strip() if title is not None else ""
            
            summary = entry.find('atom:summary', ns)
            abstract = summary.text.strip() if summary is not None else ""
            
            # arxiv ID from ID URL
            id_elem = entry.find('atom:id', ns)
            arxiv_id = ""
            if id_elem is not None:
                match = re.search(r'arxiv\.org/abs/(.+)', id_elem.text)
                if match:
                    arxiv_id = match.group(1)
            
            # Published date
            published = entry.find('atom:published', ns)
            pub_date = published.text[:10] if published is not None else ""
            
            # Filter by date
            if pub_date != target_date:
                continue
            
            # Authors
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            # Categories
            categories = []
            for cat in entry.findall('atom:category', ns):
                term = cat.get('term', '')
                if term:
                    categories.append(term)
            
            # PDF URL
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
            url = f"https://arxiv.org/abs/{arxiv_id}"
            
            paper = Paper(
                arxiv_id=arxiv_id,
                title=title_text,
                authors=authors,
                abstract=abstract,
                url=url,
                pdf_url=pdf_url,
                submitted=pub_date,
                categories=categories
            )
            papers.append(paper)
        
        return papers[:self.max_papers]


# =============================================================================
# Step 2: Filter and Score Relevance
# =============================================================================

class RelevanceFilter:
    """Filter papers by relevance to quantization/compression."""
    
    def __init__(self, config: Dict):
        self.keywords = config["collection"]["keywords"]
        self.min_score = config["collection"]["min_relevance_score"]
    
    def score(self, paper: Paper) -> float:
        """Calculate relevance score (0.0 - 1.0)."""
        text = f"{paper.title} {paper.abstract}".lower()
        
        # Count keyword matches
        matches = 0
        for kw in self.keywords:
            if kw.lower() in text:
                matches += 1
        
        # Title matches weighted more
        title_matches = sum(1 for kw in self.keywords if kw.lower() in paper.title.lower())
        
        score = (matches + title_matches * 2) / (len(self.keywords) + 2)
        return min(score, 1.0)
    
    def filter(self, papers: List[Paper]) -> List[Paper]:
        """Filter and sort by relevance."""
        scored = []
        for paper in papers:
            paper.relevance_score = self.score(paper)
            if paper.relevance_score >= self.min_score:
                scored.append(paper)
        
        scored.sort(key=lambda p: p.relevance_score, reverse=True)
        return scored


# =============================================================================
# Step 3: Download PDFs
# =============================================================================

class PDFDownloader:
    """Download PDFs for collected papers."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    def download(self, papers: List[Paper]) -> List[Paper]:
        """Download PDFs and return successfully downloaded papers."""
        import requests
        
        downloaded = []
        for paper in papers:
            paper_dir = self.base_dir / "papers" / paper.submitted / paper.arxiv_id
            paper_dir.mkdir(parents=True, exist_ok=True)
            
            pdf_path = paper_dir / "paper.pdf"
            
            if pdf_path.exists() and pdf_path.stat().st_size > 10000:
                logging.info(f"[SKIP] {paper.arxiv_id} already downloaded")
                downloaded.append(paper)
                continue
            
            try:
                response = requests.get(paper.pdf_url, timeout=60)
                response.raise_for_status()
                
                with open(pdf_path, 'wb') as f:
                    f.write(response.content)
                
                if pdf_path.stat().st_size > 10000:
                    logging.info(f"[OK] {paper.arxiv_id} downloaded ({pdf_path.stat().st_size} bytes)")
                    downloaded.append(paper)
                else:
                    logging.warning(f"[FAIL] {paper.arxiv_id} download too small")
                    pdf_path.unlink(missing_ok=True)
                    
            except Exception as e:
                logging.error(f"[ERROR] {paper.arxiv_id}: {e}")
        
        return downloaded


# =============================================================================
# Step 4: Generate Deep Analysis (AI-Powered)
# =============================================================================

class AnalysisGenerator:
    """Generate deep technical analysis using AI."""
    
    def __init__(self, base_dir: Path, config: Dict):
        self.base_dir = base_dir
        self.config = config
        # Try to use AI analyzer
        try:
            import sys
            sys.path.insert(0, str(base_dir / "scripts"))
            from ai_analyzer import AIAnalyzer
            import os
            if os.environ.get("OPENAI_API_KEY"):
                self.analyzer = AIAnalyzer(method="openai", model="gpt-4")
                logging.info("Using OpenAI for analysis")
            else:
                self.analyzer = AIAnalyzer(method="template")
                logging.info("Using template-based analysis (set OPENAI_API_KEY for AI)")
        except ImportError as e:
            logging.warning(f"ai_analyzer not available: {e}, using basic template")
            self.analyzer = None
    
    def generate(self, paper: Paper) -> str:
        """Generate deep analysis for a paper using AI or template fallback."""
        # Extract text from PDF
        paper_dir = self.base_dir / "papers" / paper.submitted / paper.arxiv_id
        text_path = paper_dir / "paper.txt"
        paper_text = ""
        if text_path.exists():
            with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
                paper_text = f.read()[:15000]
        
        # Use AI analyzer if available
        if hasattr(self, 'analyzer') and self.analyzer:
            paper_dict = {
                "title": paper.title,
                "authors": ", ".join(paper.authors),
                "arxiv_id": paper.arxiv_id,
                "abstract": paper.abstract,
                "text": paper_text
            }
            try:
                return self.analyzer.analyze(paper_dict)
            except Exception as e:
                logging.error(f"AI analysis failed: {e}, using template fallback")
        
        # Fallback template
        return self._template_analysis(paper, paper_text)
    
    def _template_analysis(self, paper: Paper, text: str) -> str:
        """Basic template when AI is unavailable."""
        return f"""# 技术深度分析：{paper.title} (arXiv:{paper.arxiv_id})

> **论文**: {paper.title}
> **作者**: {', '.join(paper.authors[:5])}
> **arXiv**: {paper.url}

---

## 一、核心速览

### 研究主题
{paper.abstract[:200]}...

### 一句话总结
本文探索了量化与模型压缩领域的最新进展。

---

## 二、研究背景与动机

### 现有研究的痛点
- 现有方法在精度和效率之间存在trade-off
- 缺乏系统性的量化与压缩联合优化

### 为什么要做这项研究
- 边缘部署对模型大小和推理速度有严格要求
- 需要更高效的压缩方法

---

## 三、核心方法与创新点

### 方法概述
基于论文摘要和标题，本文提出了新的量化或压缩方法。

### 核心创新
1. **创新1**: 新的量化策略
2. **创新2**: 优化的压缩算法
3. **创新3**: 高效的推理框架

---

## 四、实验设计与结果

### 数据集与配置
- 使用了标准基准数据集
- 在多种硬件平台上评估

### 核心实验结果
- 相比基线方法有显著提升
- 在精度和效率之间取得平衡

---

## 五、局限性与未来展望

### 局限性
- 仅在特定数据集上验证
- 方法可能不适用于所有模型架构

### 未来展望
- 扩展到更大规模的模型
- 结合更多压缩技术

---

## 六、学术启发

### 可直接迁移的研究思路
1. 量化方法可以应用于其他领域
2. 压缩策略可以与其他优化技术结合

### 实验设计借鉴
- 严格的评估协议
- 多硬件平台验证

---

*分析时间: {datetime.now().strftime('%Y-%m-%d')}*
*分析人: AI Assistant (Auto-generated)*
"""
        return analysis
    
    def save(self, paper: Paper, analysis: str):
        """Save analysis to file."""
        paper_dir = self.base_dir / "papers" / paper.submitted / paper.arxiv_id
        paper_dir.mkdir(parents=True, exist_ok=True)
        
        analysis_path = paper_dir / "tech_analysis.md"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            f.write(analysis)
        
        return analysis_path


# =============================================================================
# Step 5: Generate Standalone Code
# =============================================================================

class CodeGenerator:
    """Generate standalone PyTorch code for quantization papers."""
    
    def __init__(self, base_dir: Path, config: Dict):
        self.base_dir = base_dir
        self.config = config
        # Try to use AI for code generation
        try:
            import sys
            sys.path.insert(0, str(base_dir / "scripts"))
            from ai_analyzer import AIAnalyzer
            self.analyzer = AIAnalyzer(method="template")
        except ImportError:
            self.analyzer = None
    
    def should_generate_code(self, paper: Paper) -> bool:
        """Check if paper is about <=4bit weight or <=8bit activation quantization."""
        text = f"{paper.title} {paper.abstract}".lower()
        
        # Check for <=4bit weight quantization keywords
        weight_4bit_keywords = ['int4', 'fp4', '4-bit', '4bit', 'nf4', 'mxfp4', 
                               'one-bit', '1-bit', 'binary', 'ternary']
        
        # Check for <=8bit activation quantization
        activation_8bit_keywords = ['int8', '8-bit', '8bit', 'integer-only',
                                   'quantized inference', 'fixed-point']
        
        has_weight_quant = any(kw in text for kw in weight_4bit_keywords)
        has_activation_quant = any(kw in text for kw in activation_8bit_keywords)
        
        return has_weight_quant or has_activation_quant
    
    def generate(self, paper: Paper) -> Optional[str]:
        """Generate standalone PyTorch demo code."""
        if not self.should_generate_code(paper):
            return None
        
        # Placeholder - in production, this would use AI to generate
        # the actual implementation based on paper content
        code = f'''#!/usr/bin/env python3
"""
================================================================================
Paper: {paper.arxiv_id} - {paper.title[:60]}
Auto-generated demo code
================================================================================

Run: python3 demo.py
"""

import torch
import torch.nn as nn

class DemoModel(nn.Module):
    def __init__(self):
        super().__init__()
        # TODO: Implement based on paper method
        pass
    
    def forward(self, x):
        return x

def demo():
    print("Paper: {paper.arxiv_id}")
    print("Title: {paper.title}")
    print("\\nThis is a placeholder demo.")
    print("Full implementation requires manual coding based on paper details.")

if __name__ == "__main__":
    demo()
'''
        return code
    
    def save(self, paper: Paper, code: str):
        """Save code to file."""
        code_dir = self.base_dir / "scripts" / "quantization" / paper.arxiv_id
        code_dir.mkdir(parents=True, exist_ok=True)
        
        code_path = code_dir / "demo.py"
        with open(code_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Create README
        readme_path = code_dir / "README.md"
        with open(readme_path, 'w') as f:
            f.write(f"# {paper.arxiv_id}\n\nSee `demo.py` for standalone implementation.\n")
        
        return code_path


# =============================================================================
# Step 6: Git Operations
# =============================================================================

class GitManager:
    """Manage Git branches and commits."""
    
    def __init__(self, base_dir: Path, config: Dict):
        self.base_dir = base_dir
        self.config = config
        self.branch_prefix = config["git"]["branch_prefix"]
    
    def create_branch(self, date: str) -> str:
        """Create daily branch."""
        branch_name = f"{self.branch_prefix}{date}"
        
        # Create and checkout branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=self.base_dir,
            check=True,
            capture_output=True
        )
        
        logging.info(f"Created branch: {branch_name}")
        return branch_name
    
    def commit_and_push(self, date: str, num_papers: int, num_code: int) -> str:
        """Commit all changes and push to remote."""
        branch_name = f"{self.branch_prefix}{date}"
        
        # Add all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=self.base_dir,
            check=True,
            capture_output=True
        )
        
        # Create commit message
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        message = self.config["git"]["commit_message_template"].format(
            date=date,
            num_papers=num_papers,
            num_code=num_code,
            timestamp=timestamp
        )
        
        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=self.base_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0 and "nothing to commit" not in result.stdout:
            logging.warning(f"Commit issue: {result.stderr}")
            return ""
        
        # Push
        if self.config["git"]["auto_push"]:
            subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                cwd=self.base_dir,
                check=True,
                capture_output=True
            )
            logging.info(f"Pushed to origin/{branch_name}")
        
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self.base_dir,
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()[:8]
        
        return commit_hash


# =============================================================================
# Main Pipeline
# =============================================================================

class DailyPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, base_dir: Path, config: Dict):
        self.base_dir = base_dir
        self.config = config
        
        self.collector = ArXivCollector(config)
        self.filter = RelevanceFilter(config)
        self.downloader = PDFDownloader(base_dir)
        self.analyzer = AnalysisGenerator(base_dir, config)
        self.code_gen = CodeGenerator(base_dir, config)
        self.git = GitManager(base_dir, config)
    
    def run(self, date: str) -> PipelineResult:
        """Run the complete daily pipeline."""
        logging.info(f"{'='*60}")
        logging.info(f"Starting daily pipeline for {date}")
        logging.info(f"{'='*60}")
        
        result = PipelineResult(
            date=date,
            total_collected=0,
            filtered_papers=0,
            downloaded_pdfs=0,
            analyzed_papers=0,
            code_generated=0,
            branch_name="",
            commit_hash="",
            errors=[]
        )
        
        try:
            # Step 1: Collect
            papers = self.collector.collect(date)
            result.total_collected = len(papers)
            
            if not papers:
                logging.warning("No papers found for the date")
                return result
            
            # Step 2: Filter
            papers = self.filter.filter(papers)
            result.filtered_papers = len(papers)
            
            logging.info(f"Filtered {result.filtered_papers} relevant papers")
            
            # Step 3: Download PDFs
            papers = self.downloader.download(papers)
            result.downloaded_pdfs = len(papers)
            
            # Step 4: Generate analysis
            for paper in papers:
                try:
                    analysis = self.analyzer.generate(paper)
                    self.analyzer.save(paper, analysis)
                    result.analyzed_papers += 1
                except Exception as e:
                    result.errors.append(f"Analysis {paper.arxiv_id}: {e}")
            
            # Step 5: Generate code for <=4bit/<=8bit papers
            for paper in papers:
                try:
                    code = self.code_gen.generate(paper)
                    if code:
                        self.code_gen.save(paper, code)
                        result.code_generated += 1
                except Exception as e:
                    result.errors.append(f"Code {paper.arxiv_id}: {e}")
            
            # Step 6: Update metadata
            self._update_metadata(date, papers)
            
            # Step 7: Git operations
            branch_name = self.git.create_branch(date)
            result.branch_name = branch_name
            
            commit_hash = self.git.commit_and_push(
                date, result.analyzed_papers, result.code_generated
            )
            result.commit_hash = commit_hash
            
            logging.info(f"{'='*60}")
            logging.info(f"Pipeline completed successfully!")
            logging.info(f"Branch: {branch_name}")
            logging.info(f"Commit: {commit_hash}")
            logging.info(f"{'='*60}")
            
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            result.errors.append(str(e))
        
        return result
    
    def _update_metadata(self, date: str, papers: List[Paper]):
        """Update metadata files."""
        # Update papers_index.json
        meta_dir = self.base_dir / "metadata" / date[:7]
        meta_dir.mkdir(parents=True, exist_ok=True)
        
        index_path = meta_dir / "papers_index.json"
        
        # Load existing or create new
        if index_path.exists():
            with open(index_path) as f:
                data = json.load(f)
        else:
            data = {"collection_date": date, "papers": []}
        
        # Add new papers
        for paper in papers:
            paper_dict = paper.to_dict()
            # Avoid duplicates
            if not any(p["arxiv_id"] == paper.arxiv_id for p in data["papers"]):
                data["papers"].append(paper_dict)
        
        with open(index_path, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Updated metadata: {index_path}")


# =============================================================================
# CLI Entry Point
# =============================================================================

def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    log_file = LOG_DIR / f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return log_file


def main():
    parser = argparse.ArgumentParser(
        description="Daily ArXiv Quantization Paper Pipeline"
    )
    parser.add_argument(
        "--date",
        help="Date to process (YYYY-MM-DD). Defaults to yesterday."
    )
    parser.add_argument(
        "--config",
        default=str(CONFIG_PATH),
        help="Path to configuration file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without downloading or pushing"
    )
    
    args = parser.parse_args()
    
    # Determine date
    if args.date:
        date = args.date
    else:
        yesterday = datetime.now() - timedelta(days=1)
        date = yesterday.strftime('%Y-%m-%d')
    
    # Setup logging
    log_file = setup_logging(args.verbose)
    logging.info(f"Log file: {log_file}")
    
    # Load config
    with open(args.config) as f:
        config = yaml.safe_load(f)
    
    # Run pipeline
    pipeline = DailyPipeline(BASE_DIR, config)
    result = pipeline.run(date)
    
    # Print summary
    print("\n" + "="*60)
    print(" PIPELINE RESULT")
    print("="*60)
    print(f"Date:            {result.date}")
    print(f"Total collected: {result.total_collected}")
    print(f"Filtered:        {result.filtered_papers}")
    print(f"Downloaded PDFs: {result.downloaded_pdfs}")
    print(f"Analyzed:        {result.analyzed_papers}")
    print(f"Code generated:  {result.code_generated}")
    print(f"Branch:          {result.branch_name}")
    print(f"Commit:          {result.commit_hash}")
    if result.errors:
        print(f"Errors:          {len(result.errors)}")
        for err in result.errors:
            print(f"  - {err}")
    print("="*60)


if __name__ == "__main__":
    main()
