#!/usr/bin/env python3
"""Extract text from PDF for analysis."""

import sys
import subprocess
from pathlib import Path

def extract_text(pdf_path, max_chars=15000):
    """Extract text from PDF using pdftotext or pdfplumber."""
    pdf_path = Path(pdf_path)
    
    # Try pdftotext first (fastest)
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout[:max_chars]
    except FileNotFoundError:
        pass
    
    # Fallback: try pdfplumber
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages[:10]:  # First 10 pages
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n\n"
                if len(text) >= max_chars:
                    break
        return text[:max_chars]
    except ImportError:
        pass
    
    return "[Could not extract text from PDF]"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_path> [max_chars]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    max_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 15000
    print(extract_text(pdf_path, max_chars))
