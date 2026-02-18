# Quick Usage Guide

## Installation (5 minutes)

```bash
# Clone repo
git clone <repo>
cd cybermind-ai

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Setup .env
cp .env.example .env
# Edit .env and add GROQ_API_KEY from https://console.groq.com
```

## Basic Commands

### 1. Autonomous Mode (No User Prompts)
```bash
python3 agent.py --target 10.10.10.40 --autonomous
```
✓ Full automated exploitation
✓ Automatic shell retrieval
✓ Post-exploitation automation
✓ PDF report generation

### 2. Manual Mode (With Prompts)
```bash
python3 agent.py --target 10.10.10.40
```
✓ Shows each step
✓ Asks for approval before running
✓ Good for learning

### 3. Interactive Mode
```bash
python3 agent.py
```
Natural language commands:
- `scan 192.168.1.1 for vulnerabilities`
- `setup siem`
- `what is privilege escalation`
- `show history 192.168.1.50`

### 4. Other Options
```bash
# SIEM setup (Wazuh)
python3 agent.py --siem-setup

# Generate report from past session
python3 agent.py --report-only session_id

# Single command
python3 agent.py --target 10.0.0.5 --task "scan"
```

## Autonomous Mode Workflow

```
1. Reconnaissance       → Automatic
2. Port Scanning       → Automatic
3. Vulnerability Scan  → Automatic
4. Exploitation        → Automatic (AI selects best exploit)
5. Shell Access        → Automatic (captured session)
6. Post-Exploitation   → Automatic (privilege escalation, etc)
7. PDF Report          → Generated automatically
```

**Total time:** 5-30 minutes depending on target complexity

## What Gets Generated

After running a scan:

```bash
# Reports (PDF format)
ls reports/pentest_*.pdf

# Memory database
ls memory_db/sessions/*.json

# Raw tool output
ls reports/raw_output/
```

## Finding Results

### View Latest Report
```bash
ls -lt reports/ | head -1
# Open the PDF
```

### Check Memory for Past Scans
```bash
# List all sessions
python3 -c "
from core.memory import MemorySystem
m = MemorySystem()
for s in m.list_sessions()[:5]:
    print(f\"{s['id']} | {s['target']} | {s['finding_count']} findings\")
"
```

### Extract Findings
```bash
# JSON format
python3 -c "
import json
from pathlib import Path
for f in Path('memory_db/sessions').glob('*.json'):
    data = json.load(open(f))
    print(f\"{data['target']}: {len(data['findings'])} findings\")
"
```

## Common Use Cases

### CTF Challenge (Speed Run)
```bash
# Get shell as fast as possible
python3 agent.py --target 10.10.10.40 --autonomous

# Results in: Exploited, shell obtained, report ready
```

### HackTheBox Machine
```bash
# Autonomous exploitation
python3 agent.py --target 10.10.10.50 --autonomous

# Review PDF report for findings
# Use obtained shell to continue
```

### Learning What Commands Do
```bash
# Manual mode shows each command
python3 agent.py --target 192.168.1.100

# Approve each step to see what it does
```

### Multiple Targets
```bash
#!/bin/bash
for ip in 10.10.10.{40..50}; do
    python3 agent.py --target $ip --autonomous &
done
wait
```

## Tips & Tricks

### Skip Recon for Faster Exploitation
Edit `agent.py` in the pentest_workflow method, comment out Phase 1.

### Increase Exploit Attempts
```env
# In .env
MAX_EXPLOIT_ATTEMPTS=5
EXPLOIT_TIMEOUT=600
```

### View AI Reasoning
```env
# In .env
DEBUG=true
```
Shows internal AI decisions and reasoning.

### Custom Wordlists
```bash
# For directory busting, set wordlist path
# Edit tools/scanner.py, change dirbuster path
```

### Target Multiple Ports
```bash
# Edit core/ai_brain.py generate_pentest_plan
# Modify scan commands to add specific ports
```

## Troubleshooting

### "API key not found"
```bash
cp .env.example .env
# Add: GROQ_API_KEY=gsk_your_key_here
```

### "Metasploit not found"
```bash
# Install Metasploit
apt install metasploit-framework

# Or set PATH
export PATH=$PATH:/usr/share/metasploit-framework/bin
```

### "Connection timeout"
```bash
# Increase timeout in .env
SCAN_TIMEOUT=600

# Or check if target is online
ping -c 4 10.10.10.40
```

### "No findings discovered"
```bash
# Target might be filtered
nmap -Pn 10.10.10.40  # Skip ping
nmap -sU 10.10.10.40  # Try UDP
```

## Configuration

Key settings in `.env`:

```env
# API
GROQ_API_KEY=gsk_...                # Required
AI_MODEL=llama-3.3-70b-versatile    # Free model

# Autonomous behavior
AUTO_APPROVE_RECON=false            # Skip approval for recon
SCAN_TIMEOUT=300                    # Max seconds per command
DEBUG=false                         # Debug logging

# Output
REPORT_DIR=./reports
MEMORY_DIR=./memory_db
AUTO_GENERATE_REPORT=true
```

## Performance

### Fast Mode (~5 minutes)
```bash
# Quick reconnaissance only
python3 agent.py --target 10.10.10.40 --task "quick recon"
```

### Standard Mode (~15 minutes)
```bash
# Normal scan
python3 agent.py --target 10.10.10.40
```

### Thorough Mode (~30 minutes)
```bash
# Deep scanning with all checks
# Edit agent.py to enable all phases
```

### Parallel Scanning (~10 minutes for 3 targets)
```bash
python3 agent.py --target 10.10.10.40 --autonomous &
python3 agent.py --target 10.10.10.41 --autonomous &
python3 agent.py --target 10.10.10.42 --autonomous &
wait
```

## File Structure

```
cybermind-ai/
├── agent.py              # Main program
├── core/
│   ├── ai_brain.py      # AI reasoning (Groq)
│   ├── memory.py        # Session storage
│   └── reporter.py      # PDF generation
├── tools/
│   ├── scanner.py       # Reconnaissance
│   ├── exploit.py       # Exploitation
│   └── siem.py          # SIEM setup
├── memory_db/           # Past sessions
├── reports/             # Generated PDFs
└── requirements.txt     # Dependencies
```

## Next Steps

1. **Run first scan**: `python3 agent.py --target 10.10.10.40 --autonomous`
2. **Check results**: Open PDF in `reports/`
3. **Review findings**: Check JSON in `memory_db/sessions/`
4. **Iterate**: Modify `.env` and try again

---

**Questions?** Check README.md for detailed documentation.
**For CTF challenges:** Use `--autonomous` flag for fastest results.
**For learning:** Use manual mode to see each command.
