#!/usr/bin/env python3
"""
================================================================================
Kimi AI Analyzer Integration
================================================================================

Integrates Kimi (kimi-coding/k2p6) into the daily pipeline via file-based queue.

Mechanism:
1. Pipeline collects papers and creates "analysis tasks" in queue directory
2. Kimi (this AI) detects pending tasks and processes them
3. Results are written back, pipeline continues

Usage in daily_pipeline.py:
    analyzer = AIAnalyzer(method="kimi")
    analysis = analyzer.analyze(paper)

Environment:
    KIMI_QUEUE_DIR - Directory for task queue (default: workspace/.kimi_queue)
================================================================================
"""

import os
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class KimiQueueManager:
    """
    Manages file-based queue for Kimi analysis tasks.
    
    Flow:
        [Pipeline] creates task file -> [Kimi] detects & processes -> writes result
    """
    
    def __init__(self, queue_dir: Optional[Path] = None):
        if queue_dir is None:
            base = Path(os.environ.get("WORKSPACE", os.path.expanduser("~/.kimi_openclaw/workspace")))
            queue_dir = base / ".kimi_queue"
        
        self.queue_dir = Path(queue_dir)
        self.pending_dir = self.queue_dir / "pending"
        self.processing_dir = self.queue_dir / "processing"
        self.completed_dir = self.queue_dir / "completed"
        
        # Create directories
        for d in [self.pending_dir, self.processing_dir, self.completed_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def submit_task(self, paper: Dict, task_type: str = "deep_analysis") -> str:
        """
        Submit a task to the queue.
        Called by daily_pipeline.py.
        
        Args:
            paper: Paper metadata
            task_type: "deep_analysis" or "code_generation"
        
        Returns:
            task_id: UUID for tracking
        """
        task_id = str(uuid.uuid4())[:8]
        
        task = {
            "task_id": task_id,
            "type": task_type,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "paper": paper,
            "priority": paper.get("relevance_score", 0.5)
        }
        
        task_file = self.pending_dir / f"{task_id}_{task_type}.json"
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        
        return task_id
    
    def get_pending_tasks(self, limit: int = 10) -> list:
        """
        Get pending tasks for processing.
        Called by Kimi (heartbeat or manual check).
        """
        tasks = []
        for task_file in sorted(self.pending_dir.glob("*.json")):
            try:
                with open(task_file) as f:
                    task = json.load(f)
                tasks.append(task)
                
                # Move to processing
                processing_file = self.processing_dir / task_file.name
                task_file.rename(processing_file)
                
                if len(tasks) >= limit:
                    break
            except Exception:
                continue
        
        return tasks
    
    def complete_task(self, task_id: str, result: Dict):
        """
        Mark task as completed with result.
        Called by Kimi after analysis.
        """
        # Find in processing (filename may have _task_type suffix)
        processing_file = None
        for f in self.processing_dir.glob(f"{task_id}*.json"):
            processing_file = f
            break
        
        if not processing_file or not processing_file.exists():
            return False
        
        # Read original task
        with open(processing_file) as f:
            task = json.load(f)
        
        # Update
        task["status"] = "completed"
        task["completed_at"] = datetime.now().isoformat()
        task["result"] = result
        
        # Save to completed
        completed_file = self.completed_dir / processing_file.name
        with open(completed_file, 'w', encoding='utf-8') as f:
            json.dump(task, f, ensure_ascii=False, indent=2)
        
        # Remove from processing
        processing_file.unlink(missing_ok=True)
        
        return True
    
    def wait_for_result(self, task_id: str, timeout: int = 3600) -> Optional[Dict]:
        """
        Wait for task completion.
        Called by daily_pipeline.py after submitting.
        """
        start = time.time()
        
        while time.time() - start < timeout:
            # Find completed file (may have _task_type suffix)
            completed_files = list(self.completed_dir.glob(f"{task_id}*.json"))
            if completed_files:
                with open(completed_files[0]) as f:
                    task = json.load(f)
                return task.get("result")
            time.sleep(10)
        
        return None


class KimiAnalyzer:
    """
    Kimi integration wrapper for daily pipeline.
    
    Modes:
    - "auto": Submit to queue, wait for Kimi processing
    - "sync": Direct call (if running within Kimi session)
    """
    
    def __init__(self, mode: str = "auto"):
        self.mode = mode
        self.queue = KimiQueueManager()
    
    def analyze(self, paper: Dict) -> str:
        """
        Generate deep analysis using Kimi.
        
        If in Kimi session: direct analysis
        If in pipeline: submit to queue and wait
        """
        if self.mode == "sync":
            return self._direct_analyze(paper)
        else:
            return self._queued_analyze(paper)
    
    def generate_code(self, paper: Dict) -> Optional[str]:
        """Generate PyTorch code using Kimi."""
        if self.mode == "sync":
            return self._direct_code(paper)
        else:
            return self._queued_code(paper)
    
    def _direct_analyze(self, paper: Dict) -> str:
        """
        Direct analysis within Kimi session.
        This would be called when Kimi itself runs the analysis.
        """
        # In actual implementation, this would use the AI model directly
        # Since we're inside the AI, we can construct the prompt and process it
        prompt = self._build_analysis_prompt(paper)
        
        # The AI (ourselves) would process this
        # This is effectively a no-op since we're already the AI
        # The caller should handle this
        return f"[KIMI_DIRECT] Analysis for {paper.get('arxiv_id')} - see prompt below\n\n{prompt[:500]}..."
    
    def _queued_analyze(self, paper: Dict) -> str:
        """
        Queue-based analysis for pipeline mode.
        Submit task and wait for Kimi to process.
        """
        task_id = self.queue.submit_task(paper, task_type="deep_analysis")
        print(f"[KimiQueue] Submitted analysis task {task_id} for {paper.get('arxiv_id')}")
        
        # Wait for result (with timeout)
        result = self.queue.wait_for_result(task_id, timeout=300)  # 5 min timeout
        
        if result and "analysis" in result:
            return result["analysis"]
        else:
            # Timeout - return placeholder with task ID
            return f"""# 技术深度分析：{paper.get('title', '')} (arXiv:{paper.get('arxiv_id', '')})

> **状态**: ⏳ 等待Kimi分析中
> **任务ID**: {task_id}
> **提交时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 待分析内容

{paper.get('abstract', '')[:500]}...

---

**注意**: 此分析已由自动化流水线提交至Kimi队列，等待AI处理。
完成后结果将自动更新至此文件。

*如需立即获取分析，请运行:*
```bash
python3 scripts/kimi_process_queue.py
```

---

*分析时间: {datetime.now().strftime('%Y-%m-%d')}*
*分析人: Kimi AI (Queued)*
"""
    
    def _build_analysis_prompt(self, paper: Dict) -> str:
        """Build analysis prompt for Kimi."""
        return f"""你是一位资深的学术研究员和同行评审专家。请对以下论文进行深度剖析。

论文标题: {paper.get('title', '')}
论文作者: {paper.get('authors', '')}
arXiv ID: {paper.get('arxiv_id', '')}

论文摘要:
{paper.get('abstract', '')}

论文正文（前15000字符）:
{paper.get('text', '')[:15000]}

请严格按照以下结构输出中文分析报告：
1. 核心速览（研究主题 + 一句话总结）
2. 研究背景与动机（现有痛点 + 研究必要性）
3. 核心方法与创新点（方法概述 + 分点创新）
4. 实验设计与结果（数据集 + 核心结果）
5. 局限性与未来展望
6. 学术启发（可迁移思路 + 实验设计借鉴）

要求：基于实际内容，具体深入，包含数字对比，3000-5000字。"""
    
    def _queued_code(self, paper: Dict) -> Optional[str]:
        """Queue-based code generation - submits to Kimi queue."""
        task_id = self.queue.submit_task(paper, task_type="code_generation")
        print(f"[KimiQueue] Submitted code generation task {task_id} for {paper.get('arxiv_id')}")
        
        # Wait for result (with shorter timeout for code)
        result = self.queue.wait_for_result(task_id, timeout=300)
        
        if result and "code" in result:
            return result["code"]
        else:
            # Timeout - use template fallback
            from ai_analyzer import AIAnalyzer
            template_analyzer = AIAnalyzer(method="template")
            return template_analyzer.generate_code(paper)


def process_pending_tasks():
    """
    Process pending tasks in the queue.
    This function is called by Kimi (heartbeat or manual trigger).
    """
    queue = KimiQueueManager()
    tasks = queue.get_pending_tasks(limit=5)
    
    if not tasks:
        print("No pending tasks found.")
        return
    
    print(f"Found {len(tasks)} pending tasks")
    
    for task in tasks:
        paper = task["paper"]
        task_id = task["task_id"]
        
        print(f"\nProcessing {task_id}: {paper.get('arxiv_id', '')}")
        
        # Here Kimi would actually perform the analysis
        # Since we're inside Kimi, we can generate the analysis
        # But for automation, we'd need to trigger a Kimi session
        
        # Placeholder: mark as needing manual processing
        result = {
            "status": "needs_manual_processing",
            "analysis": f"请手动分析论文 {paper.get('arxiv_id', '')}",
            "task_id": task_id
        }
        
        queue.complete_task(task_id, result)
        print(f"  Task {task_id} marked for manual processing")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Kimi Queue Processor")
    parser.add_argument("--process", action="store_true", help="Process pending tasks")
    parser.add_argument("--status", action="store_true", help="Show queue status")
    args = parser.parse_args()
    
    if args.process:
        process_pending_tasks()
    elif args.status:
        queue = KimiQueueManager()
        pending = len(list(queue.pending_dir.glob("*.json")))
        processing = len(list(queue.processing_dir.glob("*.json")))
        completed = len(list(queue.completed_dir.glob("*.json")))
        print(f"Queue Status: {pending} pending, {processing} processing, {completed} completed")
    else:
        print("Usage: python3 kimi_analyzer.py --process | --status")
