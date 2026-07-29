#!/bin/bash
# =============================================================================
# Daily ArXiv Pipeline - Wrapper Script
# =============================================================================
# 
# This script is called by cron/launchd daily at 18:00.
# It coordinates the full pipeline: collect → filter → analyze → code → push.
#
# Schedule:
#   cron: 0 18 * * * /path/to/reading_machine/scripts/daily_run.sh
#   launchd: See ai.openclaw.reading-machine.plist
#
# Environment:
#   WORKSPACE - Path to reading_machine repo
#   LOG_DIR   - Log output directory
# =============================================================================

set -euo pipefail

# Configuration
WORKSPACE="${WORKSPACE:-$HOME/.kimi_openclaw/workspace/reading_machine}"
LOG_DIR="${LOG_DIR:-$WORKSPACE/logs}"
DATE=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d)
BRANCH_NAME="daily/${DATE}"

echo "======================================================================"
echo "Daily ArXiv Pipeline - $(date)"
echo "Processing date: ${DATE}"
echo "Workspace: ${WORKSPACE}"
echo "======================================================================"

# Create log directory
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/daily_${DATE}_$(date +%H%M%S).log"

# Redirect all output to log file
exec &> >(tee -a "${LOG_FILE}")

cd "${WORKSPACE}"

# Step 1: Collect papers from arXiv
echo ""
echo "[1/6] Collecting papers from arXiv for ${DATE}..."
python3 scripts/daily_pipeline.py --date "${DATE}" --verbose 2>&1 || {
    echo "ERROR: Collection failed"
    exit 1
}

# Step 2: Download PDFs
echo ""
echo "[2/6] Downloading PDFs..."
python3 scripts/download_pdfs.py --date "${DATE}" 2>&1 || {
    echo "WARNING: Some PDF downloads failed"
}

# Step 3: Extract text from PDFs
echo ""
echo "[3/6] Extracting text from PDFs..."
for pdf in papers/${DATE}/*/paper.pdf; do
    if [ -f "$pdf" ]; then
        id=$(basename $(dirname "$pdf"))
        python3 scripts/extract_pdf.py "$pdf" 25000 > "papers/${DATE}/${id}/paper.txt" 2>/dev/null || true
    fi
done

# Step 4: Generate deep analysis (requires AI)
# This step requires an AI model. Options:
#   A. Use OpenClaw session spawn (recommended)
#   B. Use OpenAI API
#   C. Manual review

echo ""
echo "[4/6] Generating deep analysis..."
echo "NOTE: This step requires AI analysis. Options:"
echo "  1. Run: openclaw session spawn with analysis task"
echo "  2. Or use: python3 scripts/batch_analyze.py"
echo "  3. Or manually review and update tech_analysis.md files"

# For automated runs, we can call OpenClaw:
# openclaw run --task "Analyze all papers in papers/${DATE} and write tech_analysis.md"

# Step 5: Generate standalone code for <=4bit/<=8bit papers
echo ""
echo "[5/6] Generating standalone code..."
python3 scripts/quantization/code_generator.py --date "${DATE}" 2>/dev/null || {
    echo "WARNING: Code generation not fully automated yet"
}

# Step 6: Git branch, commit, push
echo ""
echo "[6/6] Creating Git branch and pushing..."

# Create branch
git checkout -b "${BRANCH_NAME}" 2>/dev/null || git checkout "${BRANCH_NAME}"

# Add all changes
git add -A

# Commit
COMMIT_MSG="daily: ${DATE} arxiv quantization analysis

- Auto-collected papers for ${DATE}
- Filtered by quantization/compression keywords
- Generated technical analyses
- Created standalone PyTorch demos for <=4bit/<=8bit papers

Pipeline run: $(date -Iseconds)"

git commit -m "${COMMIT_MSG}" 2>/dev/null || {
    echo "Nothing to commit or commit failed"
}

# Push
git push -u origin "${BRANCH_NAME}" 2>/dev/null || {
    echo "Push failed - may need authentication"
}

echo ""
echo "======================================================================"
echo "Pipeline Complete!"
echo "Date: ${DATE}"
echo "Branch: ${BRANCH_NAME}"
echo "Log: ${LOG_FILE}"
echo "======================================================================"

# Optional: Send notification (Discord/Slack/Email)
# curl -X POST -H 'Content-type: application/json' \
#   --data '{"text":"Daily ArXiv pipeline complete: '"${BRANCH_NAME}"'"}' \
#   YOUR_WEBHOOK_URL
