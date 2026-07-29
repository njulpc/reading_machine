# Heartbeat Tasks

## Daily Checks

### 1. Kimi Analysis Queue
Check for pending paper analysis tasks submitted by the daily pipeline.

```
Run: python3 scripts/kimi_analyzer.py --status
```

If pending tasks exist:
1. Read paper PDF and metadata
2. Generate deep analysis following the 6-section template
3. Generate standalone PyTorch code (if <=4bit/<=8bit paper)
4. Mark task as completed

### 2. Daily Pipeline Status
Verify yesterday's pipeline completed successfully:
- Check branch `daily/YYYY-MM-DD` exists on GitHub
- Verify PDFs were downloaded
- Check analysis files were generated

### 3. arxiv_monitor Sync
Check if arxiv_monitor (separate cron job) has new papers to integrate.

---

## Processing Pending Kimi Tasks

When pending tasks are detected:

```bash
cd ~/.kimi_openclaw/workspace/reading_machine
python3 scripts/kimi_analyzer.py --process
```

This will:
1. Read each pending task from `.kimi_queue/pending/`
2. Move to `.kimi_queue/processing/`
3. Generate analysis and code
4. Write results to paper directory
5. Mark as completed in `.kimi_queue/completed/`

---

## Manual Trigger

To manually process all pending tasks:

```bash
cd reading_machine
# Check status
python3 scripts/kimi_analyzer.py --status

# Process all pending
python3 scripts/kimi_analyzer.py --process

# Or process with priority filter
python3 scripts/kimi_analyzer.py --process --min-priority 0.7
```

---

*Last updated: 2026-07-29*
