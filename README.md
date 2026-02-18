# CyberMind AI - Autonomous Penetration Testing Agent

**Version 2.0** | Built for CTF/HackTheBox environments | AI-powered autonomous exploitation

```
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███╗   ███╗██╗███╗   ██╗██████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║██║  ██║
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██║  ██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
```

## What is CyberMind AI?

**An intelligent, autonomous pentesting agent for CTF and HackTheBox challenges** that:

- 🤖 **Fully Autonomous**: Auto-exploits vulnerabilities without user prompts
- 🔗 **Automatic Shell Retrieval**: Gets meterpreter sessions, reverse shells, bind shells automatically
- 📈 **Smart Reconnaissance**: Uses AI to plan optimal attack paths
- 💻 **Post-Exploitation**: Automatic privilege escalation and data extraction
- 🧠 **Learns Over Time**: Remembers past targets and successful techniques
- 📊 **Auto-Reports**: Generates professional PDF pentest reports
- 🛡️ **Integrated Tools**: Nmap, Metasploit, SQLmap, Hydra, and more

## Features

### ✨ Core Capabilities

1. **Autonomous Exploitation Pipeline**
   - Reconnaissance → Scanning → Vulnerability Analysis → **Automatic Exploitation** → Post-Exploitation
   - No user prompts needed - agent decides and executes
   - Intelligent fallback strategies when exploits fail

2. **Automatic Shell Retrieval**
   - Meterpreter sessions (Windows/Linux)
   - Reverse TCP shells
   - Bind shells
   - Web shells
   - Full callback handling and session management

3. **Post-Exploitation Automation**
   - Automatic privilege escalation attempts
   - Credential harvesting and dumping
   - Sensitive data extraction
   - Lateral movement suggestions
   - Persistence mechanism installation

4. **AI-Powered Decision Making**
   - Uses Groq's Llama 3.3 70B for intelligent planning
   - Analyzes scan output to identify exploitable vulnerabilities
   - Prioritizes exploits by success likelihood
   - Suggests next steps automatically

5. **Memory & Learning**
   - Stores all sessions and findings
   - Learns from successful and failed exploits
   - Recognizes patterns in target behavior
   - Reuses proven techniques on similar targets

## Installation

### Requirements
- Kali Linux or similar penetration testing distro
- Python 3.8+
- Metasploit Framework installed
- Common tools: nmap, nikto, gobuster, sqlmap, hydra

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd cybermind-ai

# Install dependencies
pip install -r requirements.txt --break-system-packages

# Get your free Groq API key
# 1. Go to https://console.groq.com
# 2. Sign up and create an API key
# 3. Copy .env.example to .env
# 4. Add your key

cp .env.example .env
nano .env  # Add GROQ_API_KEY=gsk_your_key_here
```

## Usage

### Autonomous Mode (No Prompts)

```bash
# Full autonomous pentest with automatic exploitation
python3 agent.py --target 192.168.1.100 --autonomous

# In this mode:
# - Reconnaissance runs automatically
# - Vulnerabilities are identified
# - Exploits are executed without waiting for approval
# - Shells are captured automatically
# - Post-exploitation runs automatically
```

### Manual Mode (With Prompts)

```bash
# Standard mode - shows each step and asks for approval
python3 agent.py --target 192.168.1.100

# Useful for:
# - Learning what commands are being run
# - Testing in non-CTF environments
# - Step-by-step verification
```

### Interactive Mode

```bash
# Open interactive shell for natural language commands
python3 agent.py

# Examples inside:
# > scan 192.168.1.1 for vulnerabilities
# > setup siem
# > what is privilege escalation
# > show history 192.168.1.50
```

### Other Options

```bash
# SIEM (Wazuh) setup
python3 agent.py --siem-setup

# Generate report from past session
python3 agent.py --report-only session_id_here

# Single command execution
python3 agent.py --target 10.0.0.5 --task "scan quickly"
```

## How It Works

### Reconnaissance Phase
- Ping sweeps and host discovery
- ARP scanning on local network
- OS detection and traceroute

### Scanning Phase
- Fast TCP port scan (top 1000 ports)
- Full port scan on open ports
- Service version detection
- UDP port scanning
- Vulnerability script scanning

### Vulnerability Analysis
- CVE matching for identified services
- Web application scanning (Nikto)
- SMB enumeration (enum4linux)
- Database scanning (SQLmap for web apps)
- Exploit availability checking (searchsploit)

### Autonomous Exploitation (NEW!)
- AI analyzes vulnerabilities and selects best exploits
- Automatically generates Metasploit resource scripts
- Sets up listeners for incoming shells
- Executes exploits without waiting for user approval
- Captures all shell sessions

### Post-Exploitation
- System enumeration (whoami, id, uname, etc.)
- Privilege escalation attempts
- Credential extraction
- Sensitive file discovery
- Lateral movement preparation

### Reporting
- Professional PDF reports with:
  - Executive summary with severity counts
  - Detailed findings with remediation
  - All commands executed
  - Shell sessions obtained
  - Recommendations for remediation

## Configuration

Edit `.env` to customize behavior:

```env
# Required: Groq API Key
GROQ_API_KEY=gsk_your_key_here

# AI Model (best free model for cybersecurity)
AI_MODEL=llama-3.3-70b-versatile

# Settings
AUTO_APPROVE_RECON=false  # Skip approval for recon (LOW risk)
SCAN_TIMEOUT=300          # Max seconds per command
DEBUG=false               # Enable debug logging
```

## Architecture

```
cybermind-ai/
├── agent.py                 # Main entry point
├── core/
│   ├── ai_brain.py         # AI reasoning engine (Groq)
│   ├── memory.py           # Session storage & learning
│   └── reporter.py         # PDF report generation
├── tools/
│   ├── scanner.py          # Reconnaissance tools
│   ├── exploit.py          # Exploitation engine (new!)
│   └── siem.py             # Wazuh SIEM setup
├── memory_db/              # Past sessions storage
├── reports/                # Generated PDF reports
└── requirements.txt        # Python dependencies
```

## What Makes It Autonomous?

**Traditional Pentesting:**
```
Reconnaissance → [Wait for user]
Scanning → [Wait for user]
Vulnerability Analysis → [Wait for user]
Exploitation → [Wait for user to run exploit]
Shell Access → [Manual shell handling]
```

**CyberMind AI Autonomous Mode:**
```
Reconnaissance ↓ (auto)
Scanning ↓ (auto)
Vulnerability Analysis ↓ (auto)
Exploitation ↓ (auto - AI picks best exploit)
Shell Access ↓ (auto - capture session)
Post-Exploitation ↓ (auto - enumerate and escalate)
```

No user interaction required. Agent handles everything.

## Command Examples

### Autonomous CTF Challenges
```bash
# HackTheBox machine
python3 agent.py --target 10.10.10.40 --autonomous

# Output:
# [*] Starting autonomous exploitation on 10.10.10.40
# [+] Found Apache 2.4.1 - CVE-2012-0053
# [+] Running exploit: exploit/unix/www/apache_optionsbleed
# [+] Exploit successful! Meterpreter session opened
# [+] Running post-exploitation enumeration...
# [+] Found credentials in config files
# [+] Report saved: reports/pentest_10_10_10_40_20240101_120000.pdf
```

### Learning from Past Scans
```bash
# Interactive mode
python3 agent.py

CyberMind> show history 10.10.10.40
Found 3 previous sessions for this target

CyberMind> what credentials did I find last time
[AI shows previous findings and credentials found]

CyberMind> scan 10.10.10.40 again
[Runs new scan, AI uses previous knowledge for faster exploitation]
```

### Custom Scan Profiles
```bash
# Web application focused
python3 agent.py --target 192.168.1.50 --task "scan for web vulnerabilities"

# Database focused
python3 agent.py --target 192.168.1.60 --task "scan for database vulnerabilities"

# Quick recon only
python3 agent.py --target 192.168.1.70 --task "quick recon"
```

## For CTF/HackTheBox Players

**CyberMind is perfect for:**
- Quick reconnaissance and exploitation
- Automated vulnerability identification
- Learning attack paths through AI guidance
- Speeding up challenge solving
- Understanding what commands to run

**Usage in CTF workflow:**
1. Get target IP from HTB/CTF
2. Run: `python3 agent.py --target <IP> --autonomous`
3. Let it exploit and get shell
4. Review findings in PDF report
5. Manually verify shell access

## Disclaimer

**IMPORTANT:** This tool is designed ONLY for:
- CTF/Capture-The-Flag competitions
- HackTheBox machines
- Authorized penetration testing engagements
- Personal learning and home lab environments

**NOT for:**
- Unauthorized access to systems
- Testing systems you don't own
- Malicious purposes
- Any illegal activity

Always ensure you have proper authorization before testing any target.

## API Keys & Setup

### Getting a Free Groq API Key
1. Visit https://console.groq.com
2. Click "Sign Up" (free tier available)
3. Go to "API Keys" section
4. Click "Create New Secret Key"
5. Copy the key (starts with `gsk_`)
6. Paste into `.env` file as `GROQ_API_KEY=gsk_your_key`

The free tier includes:
- 30 requests per minute
- Full access to Llama 3.3 70B model
- Perfect for pentesting workflows

## Troubleshooting

### "GROQ_API_KEY not set"
```bash
cp .env.example .env
# Edit .env and add your API key
```

### "Metasploit not found"
```bash
# Make sure Metasploit is installed
which msfconsole
# If not installed: apt install metasploit-framework
```

### "Python dependencies missing"
```bash
pip install -r requirements.txt --break-system-packages
```

### "Scan timeouts"
Increase `SCAN_TIMEOUT` in `.env`:
```env
SCAN_TIMEOUT=600  # 10 minutes instead of 5
```

## Recent Updates (v2.0)

- ✨ **Autonomous Exploitation**: Full exploitation without prompts
- 🔗 **Automatic Shell Retrieval**: Meterpreter and reverse shell capture
- 📈 **Post-Exploitation Automation**: Auto privilege escalation and data extraction
- 🧠 **Smarter Vulnerability-to-Exploit Mapping**: AI prioritizes exploits
- 📊 **Enhanced Reporting**: Shell session tracking and post-exploit results
- ⚡ **Faster Execution**: Parallel scanning and concurrent exploitation

## Development & Contribution

This project demonstrates:
- AI-powered cybersecurity decision making
- Integration of multiple security tools
- Autonomous agent design patterns
- Professional pentest workflows
- Learning systems for security operations

## License

MIT License - Educational and authorized security testing only

---

**Built with:**
- Groq API (Llama 3.3 70B)
- Metasploit Framework
- Nmap, Nikto, SQLmap, Hydra
- Python 3.8+
- ReportLab for PDF generation

**For authorized CTF/HackTheBox challenges only.**
