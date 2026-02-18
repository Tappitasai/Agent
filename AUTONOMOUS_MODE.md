# CyberMind AI - Autonomous Mode Guide

## Complete Autonomous Exploitation Workflow

This guide covers the fully autonomous penetration testing agent for CTF/HackTheBox environments.

## Quick Start - Autonomous Mode

```bash
# Run fully autonomous pentest with automatic exploitation
python3 agent.py --target 192.168.1.100 --autonomous
```

**What happens:**
1. Reconnaissance runs automatically
2. Port scanning executes without waiting for approval
3. Vulnerability analysis runs automatically
4. Exploits are executed without user prompts
5. Shells are captured automatically
6. Post-exploitation runs (privilege escalation, data extraction)
7. PDF report is generated with all findings

## Detailed Autonomous Workflow

### Phase 1: Reconnaissance (Automatic)
```
✓ Ping sweep to verify host is online
✓ ARP scanning on local network
✓ OS detection via TTL analysis
✓ Traceroute to understand network path
```

**Execution time:** ~30 seconds
**No user approval needed**

### Phase 2: Port & Service Scanning (Automatic)
```
✓ Fast scan of top 1000 ports
✓ Full TCP port scan (1-65535) on open ports
✓ Service version detection
✓ UDP scan on top ports
✓ Nmap vulnerability scripts
```

**Execution time:** 2-10 minutes depending on target
**No user approval needed**

### Phase 3: Vulnerability Analysis (Automatic)
```
✓ CVE matching for identified services
✓ Exploit availability checking (searchsploit)
✓ Web app scanning if HTTP found (Nikto)
✓ SMB enumeration if port 445 open (enum4linux)
✓ Database vulnerability scanning (SQLmap)
```

**Execution time:** 3-15 minutes
**No user approval needed**

### Phase 4: Autonomous Exploitation (NEW!)
```
✓ AI analyzes all findings
✓ AI selects most likely exploits to succeed
✓ Metasploit resource scripts generated automatically
✓ Listener setup for shell callbacks
✓ Exploit execution without waiting for confirmation
✓ Shell session captured automatically
```

**If exploit succeeds:**
- Meterpreter session established
- Shell access confirmed
- Proceeds to Phase 5

**If exploit fails:**
- Tries next most likely exploit
- Up to 3 exploit attempts before moving on

### Phase 5: Post-Exploitation (Automatic)
```
✓ System information gathering (sysinfo, id, whoami)
✓ Current user privileges enumeration
✓ Available privilege escalation methods
✓ Process enumeration
✓ Network configuration capture
✓ Attempt local privilege escalation
✓ Credential extraction (if possible)
✓ Sensitive file discovery
```

## Example Autonomous Execution

```bash
$ python3 agent.py --target 10.10.10.40 --autonomous
```

**Output:**
```
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███╗   ███╗██╗███╗   ██╗██████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗
...
[*] Session ID: 20240118_143022
[+] AUTONOMOUS MODE ENABLED
[+] All modules loaded. Ready for commands.

[*] Starting pentest workflow for target: 10.10.10.40

  ═══ PHASE 1: RECONNAISSANCE ═══
  [STEP] Step 1: Ping host to check if alive
  [AUTO] Executing: Ping host to check if alive
  [*] Running: ping -c 4 10.10.10.40
  [+] Command completed successfully
  [*] Host is online

  [STEP] Step 2: Quick Nmap host scan
  [AUTO] Executing: Quick Nmap host scan
  [*] Running: nmap -sn 10.10.10.40
  [+] Command completed successfully

  ═══ PHASE 2: PORT & SERVICE SCANNING ═══
  [STEP] Step 1: Fast top 1000 ports
  [AUTO] Executing: Fast top 1000 ports
  [*] Running: nmap -F 10.10.10.40
  [+] Command completed successfully
  [+] Found open ports: 22, 80, 443

  [STEP] Step 2: Service version detection
  [AUTO] Executing: Service version detection
  [*] Running: nmap -sV 10.10.10.40
  [+] Command completed successfully
  [+] Apache 2.4.1 on port 80
  [+] OpenSSH 6.6 on port 22

  ═══ PHASE 3: VULNERABILITY ANALYSIS ═══
  [STEP] Step 1: CVE matching
  [AUTO] Executing: CVE matching
  [+] Apache 2.4.1 - CVE-2012-0053 (HTTP OPTIONS overflow)
  [+] OpenSSH 6.6 - CVE-2018-15473 (Username enumeration)

  ═══ PHASE 4: AUTONOMOUS EXPLOITATION ═══
  [AI] Analyzing findings and preparing exploits...
  [WARN] Attempting exploit: Apache Optionsbleed RCE
  [*] Running: msfconsole -r /tmp/msf_exploit_auto.rc
  [+] Exploit successful! Shell obtained on 10.10.10.40
  [SUCCESS] Meterpreter session 1 opened

  ═══ PHASE 5: POST-EXPLOITATION ═══
  [AI] Beginning post-exploitation enumeration...
  [*] System Info: Linux 3.2.0-4-amd64 x86_64
  [*] Current User: www-data (uid=33)
  [WARN] Not root - attempting privilege escalation
  [*] Found sudo permissions without password
  [+] Privilege escalation successful! Now running as root
  [+] Extracted credentials from /root/.ssh/

  ═══ GENERATING PDF REPORT ═══
  [+] Report saved: reports/pentest_10_10_10_40_20240118_143022.pdf
```

## Key Differences: Autonomous vs Manual Mode

### Manual Mode (Default)
```bash
python3 agent.py --target 10.10.10.40
```
- Shows each command before running
- Asks: `[y] Run [s] Skip [m] Modify [q] Quit`
- User must press `y` for each step
- Good for learning what commands do
- Good for verifying target authorization
- Slower execution

### Autonomous Mode
```bash
python3 agent.py --target 10.10.10.40 --autonomous
```
- Runs all phases automatically
- No user prompts
- AI makes exploitation decisions
- Faster execution
- Better for CTF speed runs
- Good for home lab automation

## Autonomous Mode Decision Logic

**When selecting exploits, CyberMind AI considers:**

1. **Vulnerability Severity**
   - CRITICAL (100% priority)
   - HIGH (90% priority)
   - MEDIUM (70% priority)

2. **Exploit Reliability**
   - Past success rate on similar targets
   - Known CVE with public exploit (80% weight)
   - Unconfirmed vulnerability (40% weight)

3. **Execution Complexity**
   - Simple exploits first (Metasploit modules)
   - Complex exploits second (custom scripts)
   - Brute force attacks last

4. **Resource Requirements**
   - Low resource exploits first
   - High resource exploits only if needed

## Post-Exploitation Automation

After obtaining shell access, CyberMind automatically:

### For Meterpreter Sessions
```
sysinfo          → Gather system information
getuid           → Check current user/privileges
getprivs         → List available privileges
ps               → Process enumeration
ipconfig         → Network configuration
arp              → ARP table
route            → Routing table
```

### For Linux Shells
```
whoami           → Current user
id               → User/group info
uname -a         → System details
sudo -l          → Sudo permissions
cat /etc/passwd  → User enumeration
find / -perm -4000 → SUID binaries
```

### For Windows Shells
```
systeminfo       → System info
net localgroup administrators → Admin check
wmic product list brief → Installed software
netstat -an      → Active connections
tasklist         → Running processes
```

## Configuring Autonomous Behavior

Edit `.env` to customize:

```env
# Enable autonomous mode by default
AUTONOMOUS_MODE=true

# Auto-approval for recon (LOW risk only)
AUTO_APPROVE_RECON=true

# Exploit settings
EXPLOIT_TIMEOUT=300           # Seconds to wait for exploit
MAX_EXPLOIT_ATTEMPTS=3        # Number of exploits to try
AUTO_ESCALATE_PRIVS=true      # Auto privilege escalation

# Post-exploitation
AUTO_EXTRACT_CREDS=true       # Dump credentials automatically
AUTO_FIND_SENSITIVE_FILES=true # Search for interesting files
```

## Handling Exploit Failures

If an exploit fails, CyberMind:
1. Logs the failure
2. Analyzes why it failed
3. Suggests alternative exploit
4. Tries next most likely exploit (up to 3 attempts)
5. Continues to post-exploitation if any shell obtained
6. Switches to manual mode if all exploits fail

## Security Considerations

**Autonomous mode is safe when:**
- Testing authorized targets (CTF/HackTheBox)
- Running in isolated lab environment
- Target IP is verified correct
- Only targeting machines you own

**Never use autonomous mode for:**
- Unauthorized testing
- Production systems
- Systems you don't own
- Networks without explicit permission

## Performance Tips for Autonomous Mode

### For Fast Execution
```bash
# Reduce scan scope
python3 agent.py --target 10.10.10.40 --autonomous --quick

# Skip slow phases
# Edit agent.py to disable UDP/script scans
```

### For Thorough Exploitation
```bash
# Increase exploit attempts and timeouts
# Edit .env:
# MAX_EXPLOIT_ATTEMPTS=5
# EXPLOIT_TIMEOUT=600
```

### For Parallel Exploitation
```bash
# Run multiple agents on different targets
python3 agent.py --target 10.10.10.40 --autonomous &
python3 agent.py --target 10.10.10.41 --autonomous &
python3 agent.py --target 10.10.10.42 --autonomous &
wait
```

## Troubleshooting Autonomous Mode

### Exploits not running
```bash
# Check Metasploit is installed
which msfconsole

# Check API connection
echo $GROQ_API_KEY  # Should not be empty
```

### Shell not captured
```bash
# Check if listener is running
netstat -tln | grep 4444

# Check firewall isn't blocking callback
sudo ufw allow 4444/tcp
```

### Target unreachable
```bash
# Verify target IP and ping
ping -c 4 10.10.10.40

# Check if target is online
nmap -sn 10.10.10.40
```

## Example: HTB Machine Automation

```bash
#!/bin/bash
# batch_htb.sh - Automated HTB machine scanning

TARGETS=(10.10.10.40 10.10.10.50 10.10.10.60)

for target in "${TARGETS[@]}"; do
    echo "[*] Pwning $target..."
    python3 agent.py --target $target --autonomous --no-banner

    # Extract shell info from PDF
    echo "[+] Check reports/ for full details"
done
```

Run with:
```bash
chmod +x batch_htb.sh
./batch_htb.sh
```

## Viewing Results

After autonomous exploitation completes:

```bash
# View generated reports
ls -lh reports/

# Open PDF report
open reports/pentest_10_10_10_40_*.pdf

# View session memory
cat memory_db/sessions/*.json | jq '.[] | {target, total_findings}'

# Check shells obtained
cat memory_db/index.json | jq '.sessions[] | {target, shells_obtained}'
```

---

**Autonomous Mode is designed for CTF/HackTheBox environments where:**
- You own the target system
- Speed is a priority
- Full automation is beneficial

**For authorized security testing use Manual Mode to verify each step.**
