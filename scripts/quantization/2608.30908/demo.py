#!/usr/bin/env python3
"""Real-weight Qwen3-0.6B reproduction for arXiv:2608.30908."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from qwen_utils import run

if __name__ == "__main__":
    run("2608.30908")
