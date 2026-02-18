#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║          CyberMind AI - Personal Cybersecurity Assistant           ║
║          Version 1.0 | Built for Kali Linux + Home Lab            ║
║          AI Backend: Groq (Free) | Model: Llama 3.3 70B           ║
╚═══════════════════════════════════════════════════════════════════╝

HOW IT WORKS:
  - You give commands in plain English (or structured commands)
  - The AI thinks, plans steps, shows you each step for approval
  - Executes approved steps using real Kali tools
  - Learns from every session (stores results in memory_db/)
  - Auto-generates PDF reports for everything
  - Self-heals: if a command fails, it tries an alternative

USAGE:
  python3 agent.py
  python3 agent.py --task "scan 192.168.1.1"
  python3 agent.py --siem-setup
  python3 agent.py --report-only <session_id>
"""

import os
import sys
import json
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# ─── Load environment variables from .env file ───────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ─── Import our custom modules ────────────────────────────────────────────────
from core.ai_brain import AIBrain
from core.memory import MemorySystem
from core.reporter import ReportGenerator
from tools.scanner import SecurityScanner
from tools.siem import SIEMSetup
from tools.exploit import ExploitHelper

# ═══════════════════════════════════════════════════════════════════════════════
#  COLORS — Makes terminal output readable and professional
# ═══════════════════════════════════════════════════════════════════════════════
class C:
    RED    = "\033[91m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    BLUE   = "\033[94m"
    PURPLE = "\033[95m"
    CYAN   = "\033[96m"
    WHITE  = "\033[97m"
    BOLD   = "\033[1m"
    END    = "\033[0m"

def banner():
    print(f"""
{C.CYAN}{C.BOLD}
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███╗   ███╗██╗███╗   ██╗██████╗ 
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║██║  ██║
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██║  ██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝ 
{C.END}
{C.PURPLE}  ┌─ Personal Cybersecurity AI Assistant ─────────────────────────────┐
  │  AI Brain: Groq (Llama 3.3 70B) │ Tools: Kali Suite + Wazuh SIEM │
  │  Mode: Semi-Autonomous   │  Learning: Active   │  Reports: PDF    │
  └─────────────────────────────────────────────────────────────────┘{C.END}
""")

def log(level, msg):
    """Pretty logging with color and timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    icons = {
        "INFO":    f"{C.BLUE}[*]{C.END}",
        "SUCCESS": f"{C.GREEN}[+]{C.END}",
        "WARN":    f"{C.YELLOW}[!]{C.END}",
        "ERROR":   f"{C.RED}[-]{C.END}",
        "AI":      f"{C.PURPLE}[AI]{C.END}",
        "STEP":    f"{C.CYAN}[STEP]{C.END}",
        "LEARN":   f"{C.GREEN}[LEARN]{C.END}",
    }
    icon = icons.get(level, "[?]")
    print(f"  {icon} {C.WHITE}{timestamp}{C.END} {msg}")

def ask_approval(step_num, description, command, risk_level="LOW"):
    """Show the user a planned step and ask for approval before running it."""
    risk_colors = {"LOW": C.GREEN, "MEDIUM": C.YELLOW, "HIGH": C.RED}
    risk_color = risk_colors.get(risk_level, C.WHITE)
    
    print(f"\n  {C.CYAN}{'─'*60}{C.END}")
    print(f"  {C.BOLD}Step {step_num}: {description}{C.END}")
    print(f"  {C.YELLOW}Command:{C.END} {C.WHITE}{command}{C.END}")
    print(f"  {C.YELLOW}Risk:{C.END}    {risk_color}{risk_level}{C.END}")
    print(f"  {C.CYAN}{'─'*60}{C.END}")
    
    while True:
        choice = input(f"\n  {C.BOLD}[y] Run  [s] Skip  [m] Modify  [q] Quit  → {C.END}").strip().lower()
        if choice == 'y':
            return "run", command
        elif choice == 's':
            return "skip", command
        elif choice == 'm':
            new_cmd = input(f"  {C.YELLOW}Enter modified command: {C.END}").strip()
            return "run", new_cmd
        elif choice == 'q':
            return "quit", command
        else:
            print(f"  {C.RED}Invalid choice. Enter y/s/m/q{C.END}")

# ═══════════════════════════════════════════════════════════════════════════════
#  CYBERMIND AGENT CLASS — The main brain that ties everything together
# ═══════════════════════════════════════════════════════════════════════════════
class CyberMindAgent:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log = []
        self.findings = []
        self.errors = []
        
        log("INFO", "Initializing CyberMind AI Agent...")
        
        # Initialize core components
        self.ai = AIBrain()
        self.memory = MemorySystem()
        self.reporter = ReportGenerator()
        self.scanner = SecurityScanner()
        self.siem = SIEMSetup()
        self.exploit_helper = ExploitHelper()
        
        log("SUCCESS", f"Session ID: {C.CYAN}{self.session_id}{C.END}")
        log("SUCCESS", "All modules loaded. Ready for commands.")

    def run_command_with_healing(self, command, description, retry_count=2):
        """
        Run a shell command. If it fails, ask AI to suggest a fix and retry.
        This is the SELF-HEALING feature.
        """
        for attempt in range(retry_count + 1):
            try:
                log("INFO", f"Running: {C.YELLOW}{command}{C.END}")
                result = subprocess.run(
                    command, shell=True, capture_output=True,
                    text=True, timeout=300
                )
                
                output = result.stdout + result.stderr
                self.session_log.append({
                    "command": command,
                    "output": output[:2000],  # Cap at 2000 chars
                    "success": result.returncode == 0,
                    "timestamp": datetime.now().isoformat()
                })
                
                if result.returncode == 0:
                    log("SUCCESS", f"Command completed successfully")
                    return True, output
                else:
                    log("ERROR", f"Command failed (exit code {result.returncode})")
                    
                    if attempt < retry_count:
                        log("AI", "Analyzing error and generating fix...")
                        fix = self.ai.suggest_fix(command, output)
                        if fix:
                            log("LEARN", f"AI suggests: {fix['explanation']}")
                            choice, fixed_cmd = ask_approval(
                                f"Fix-{attempt+1}",
                                f"Auto-fix: {fix['explanation']}",
                                fix["command"],
                                "MEDIUM"
                            )
                            if choice == "run":
                                command = fixed_cmd
                                continue
                    
                    return False, output
                    
            except subprocess.TimeoutExpired:
                log("ERROR", "Command timed out after 5 minutes")
                return False, "TIMEOUT"
            except Exception as e:
                log("ERROR", f"Unexpected error: {str(e)}")
                return False, str(e)
        
        return False, "Max retries reached"

    def pentest_workflow(self, target_ip, target_name="Unknown Target"):
        """
        Full penetration testing workflow.
        Phases: Recon → Scan → Enumerate → Exploit Hints → Report
        """
        log("INFO", f"Starting pentest workflow for target: {C.RED}{target_ip}{C.END}")
        
        # Check memory for previous scans of this target
        previous = self.memory.get_target_history(target_ip)
        if previous:
            log("LEARN", f"Found {len(previous)} previous sessions for this target")
        
        report_data = {
            "target": target_ip,
            "target_name": target_name,
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "phases": {}
        }
        
        # ── PHASE 1: RECONNAISSANCE ──────────────────────────────────────────
        print(f"\n{C.BOLD}{C.CYAN}  ═══ PHASE 1: RECONNAISSANCE ═══{C.END}")
        
        # AI generates a personalized recon plan
        recon_plan = self.ai.generate_pentest_plan("recon", target_ip, previous)
        
        for i, step in enumerate(recon_plan["steps"], 1):
            choice, cmd = ask_approval(i, step["description"], step["command"], step.get("risk", "LOW"))
            
            if choice == "quit":
                log("WARN", "User stopped the scan. Generating partial report...")
                break
            elif choice == "skip":
                log("INFO", f"Skipped: {step['description']}")
                continue
            
            success, output = self.run_command_with_healing(cmd, step["description"])
            
            if success:
                # AI analyzes output and extracts findings
                findings = self.ai.analyze_output(output, step["description"], target_ip)
                self.findings.extend(findings.get("findings", []))
                report_data["phases"].setdefault("recon", []).append({
                    "step": step["description"],
                    "command": cmd,
                    "output_summary": findings.get("summary", output[:500]),
                    "findings": findings.get("findings", [])
                })
        
        # ── PHASE 2: SCANNING ────────────────────────────────────────────────
        print(f"\n{C.BOLD}{C.CYAN}  ═══ PHASE 2: PORT & SERVICE SCANNING ═══{C.END}")
        
        scan_plan = self.ai.generate_pentest_plan("scan", target_ip, self.findings)
        
        for i, step in enumerate(scan_plan["steps"], 1):
            choice, cmd = ask_approval(i, step["description"], step["command"], step.get("risk", "LOW"))
            
            if choice == "quit":
                break
            elif choice == "skip":
                continue
            
            success, output = self.run_command_with_healing(cmd, step["description"])
            if success:
                findings = self.ai.analyze_output(output, step["description"], target_ip)
                self.findings.extend(findings.get("findings", []))
                report_data["phases"].setdefault("scanning", []).append({
                    "step": step["description"],
                    "command": cmd,
                    "output_summary": findings.get("summary", output[:500]),
                    "findings": findings.get("findings", [])
                })
        
        # ── PHASE 3: VULNERABILITY ANALYSIS ─────────────────────────────────
        print(f"\n{C.BOLD}{C.CYAN}  ═══ PHASE 3: VULNERABILITY ANALYSIS ═══{C.END}")
        
        vuln_plan = self.ai.generate_pentest_plan("vuln", target_ip, self.findings)
        
        for i, step in enumerate(vuln_plan["steps"], 1):
            choice, cmd = ask_approval(i, step["description"], step["command"], step.get("risk", step.get("risk", "MEDIUM")))
            
            if choice == "quit":
                break
            elif choice == "skip":
                continue
            
            success, output = self.run_command_with_healing(cmd, step["description"])
            if success:
                findings = self.ai.analyze_output(output, step["description"], target_ip)
                self.findings.extend(findings.get("findings", []))
                report_data["phases"].setdefault("vulnerability", []).append({
                    "step": step["description"],
                    "command": cmd,
                    "output_summary": findings.get("summary", output[:500]),
                    "findings": findings.get("findings", [])
                })
        
        # ── PHASE 4: AI EXPLOITATION SUGGESTIONS ─────────────────────────────
        print(f"\n{C.BOLD}{C.RED}  ═══ PHASE 4: EXPLOITATION HINTS (AI Guidance) ═══{C.END}")
        log("WARN", "Exploitation hints are for AUTHORIZED testing only!")
        
        if self.findings:
            exploit_hints = self.ai.suggest_exploits(self.findings, target_ip)
            report_data["phases"]["exploit_hints"] = exploit_hints
            
            for hint in exploit_hints.get("suggestions", []):
                print(f"\n  {C.RED}[VULN]{C.END} {hint['vulnerability']}")
                print(f"  {C.YELLOW}Severity:{C.END} {hint['severity']}")
                print(f"  {C.YELLOW}Tool:{C.END}     {hint['tool']}")
                print(f"  {C.YELLOW}Command:{C.END}  {hint['command']}")
                print(f"  {C.YELLOW}Notes:{C.END}    {hint['notes']}")
        
        # ── FINALIZE ─────────────────────────────────────────────────────────
        report_data["end_time"] = datetime.now().isoformat()
        report_data["total_findings"] = len(self.findings)
        report_data["session_log"] = self.session_log
        
        # Save to memory for future learning
        self.memory.save_session(self.session_id, target_ip, report_data, self.findings)
        log("LEARN", "Session saved to memory database")
        
        # Generate PDF report
        print(f"\n{C.BOLD}{C.CYAN}  ═══ GENERATING PDF REPORT ═══{C.END}")
        pdf_path = self.reporter.generate_pentest_report(report_data, self.findings)
        log("SUCCESS", f"PDF Report saved: {C.GREEN}{pdf_path}{C.END}")
        
        return report_data

    def siem_setup_workflow(self):
        """Automated Wazuh SIEM setup for home lab."""
        log("INFO", "Starting Wazuh SIEM setup for home lab...")
        
        siem_plan = self.siem.get_setup_plan()
        
        print(f"\n{C.BOLD}{C.CYAN}  ═══ WAZUH SIEM HOME LAB SETUP ═══{C.END}")
        print(f"  This will install Wazuh Manager + Dashboard on this machine.")
        print(f"  Requirements: 4GB RAM minimum, Ubuntu/Kali Linux\n")
        
        for i, step in enumerate(siem_plan, 1):
            choice, cmd = ask_approval(i, step["description"], step["command"], step.get("risk", "LOW"))
            
            if choice == "quit":
                log("WARN", "SIEM setup cancelled by user")
                break
            elif choice == "skip":
                log("INFO", f"Skipped: {step['description']}")
                continue
            
            success, output = self.run_command_with_healing(cmd, step["description"])
            
            if not success and step.get("required", False):
                log("ERROR", f"Critical step failed: {step['description']}")
                log("WARN", "SIEM setup cannot continue without this step")
                break
        
        # Generate SIEM setup documentation
        pdf_path = self.reporter.generate_siem_report(siem_plan, self.session_log)
        log("SUCCESS", f"SIEM Setup Guide PDF saved: {C.GREEN}{pdf_path}{C.END}")

    def interactive_mode(self):
        """Main interactive chat loop - talk to the AI in plain English."""
        print(f"\n{C.BOLD}{C.CYAN}  ═══ INTERACTIVE MODE ═══{C.END}")
        print(f"  Type commands in plain English. Examples:")
        print(f"  {C.YELLOW}→ 'scan 192.168.1.1 for vulnerabilities'{C.END}")
        print(f"  {C.YELLOW}→ 'set up wazuh siem on this machine'{C.END}")
        print(f"  {C.YELLOW}→ 'generate report for my last session'{C.END}")
        print(f"  {C.YELLOW}→ 'what did i find last time i scanned 192.168.1.10'{C.END}")
        print(f"  {C.YELLOW}→ 'explain what nmap -sV means'{C.END}")
        print(f"  {C.YELLOW}→ 'help'{C.END}  or  {C.YELLOW}'quit'{C.END}\n")
        
        while True:
            try:
                user_input = input(f"  {C.BOLD}{C.CYAN}CyberMind{C.END}{C.BOLD}>{C.END} ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    log("INFO", "Saving session and exiting...")
                    if self.session_log:
                        self.memory.save_session(self.session_id, "interactive", 
                                                  {"log": self.session_log}, [])
                    print(f"\n  {C.GREEN}Stay ethical. Stay legal. Happy hacking!{C.END}\n")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                # Let the AI interpret the command
                interpretation = self.ai.interpret_command(user_input, self.memory.get_context())
                
                if interpretation["type"] == "pentest":
                    target = interpretation.get("target")
                    if target:
                        self.pentest_workflow(target)
                    else:
                        print(f"  {C.YELLOW}What's the target IP or hostname?{C.END} ")
                        target = input("  → ").strip()
                        if target:
                            self.pentest_workflow(target)
                
                elif interpretation["type"] == "siem_setup":
                    self.siem_setup_workflow()
                
                elif interpretation["type"] == "question":
                    # Pure educational question — just ask AI and display
                    answer = self.ai.answer_question(user_input)
                    print(f"\n  {C.PURPLE}[AI Answer]{C.END}\n")
                    # Word-wrap the answer
                    words = answer.split()
                    line = "  "
                    for word in words:
                        if len(line) + len(word) > 80:
                            print(line)
                            line = "  " + word + " "
                        else:
                            line += word + " "
                    if line.strip():
                        print(line)
                    print()
                
                elif interpretation["type"] == "memory_query":
                    results = self.memory.search(interpretation.get("query", user_input))
                    if results:
                        print(f"\n  {C.GREEN}Found {len(results)} relevant memories:{C.END}")
                        for r in results[:3]:
                            print(f"  {C.YELLOW}[{r['date']}]{C.END} {r['summary']}")
                    else:
                        print(f"  {C.YELLOW}No memories found for that query.{C.END}")
                
                elif interpretation["type"] == "report":
                    session_id = interpretation.get("session_id", self.session_id)
                    data = self.memory.load_session(session_id)
                    if data:
                        pdf_path = self.reporter.generate_pentest_report(data, data.get("findings", []))
                        log("SUCCESS", f"Report generated: {pdf_path}")
                    else:
                        log("WARN", "Session not found. Showing available sessions:")
                        sessions = self.memory.list_sessions()
                        for s in sessions[-5:]:
                            print(f"  {C.CYAN}{s['id']}{C.END} | {s['target']} | {s['date']}")
                
                else:
                    # Unknown command - ask AI to explain or handle
                    response = self.ai.handle_unknown(user_input)
                    print(f"\n  {C.PURPLE}[AI]{C.END} {response}\n")
                    
            except KeyboardInterrupt:
                print(f"\n  {C.YELLOW}[!] Interrupted. Type 'quit' to exit cleanly.{C.END}")
            except Exception as e:
                log("ERROR", f"Agent error: {str(e)}")
                self.errors.append({"error": str(e), "timestamp": datetime.now().isoformat()})

    def _show_help(self):
        help_text = f"""
  {C.BOLD}{C.CYAN}CyberMind AI - Command Reference{C.END}
  {'─'*50}
  {C.YELLOW}PENTEST COMMANDS:{C.END}
    scan <IP>                  → Run full pentest workflow
    scan <IP> quick            → Quick port scan only
    scan <IP> web              → Web app focused scan
    
  {C.YELLOW}SIEM COMMANDS:{C.END}
    setup siem                 → Install Wazuh SIEM
    siem status                → Check Wazuh status
    
  {C.YELLOW}MEMORY & REPORTS:{C.END}
    show history <IP>          → Past scans for this target
    generate report            → PDF for current session
    list sessions              → Show all past sessions
    
  {C.YELLOW}LEARNING:{C.END}
    what is <term>             → Explain any security concept
    explain <command>          → Explain what a command does
    why did <tool> fail        → AI debug assistance
    
  {C.YELLOW}SYSTEM:{C.END}
    help                       → Show this menu
    quit / exit                → Exit CyberMind
  {'─'*50}
"""
        print(help_text)


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description="CyberMind AI - Personal Cybersecurity Assistant"
    )
    parser.add_argument("--task", type=str, help="Single task to execute (non-interactive)")
    parser.add_argument("--target", type=str, help="Target IP for pentest")
    parser.add_argument("--siem-setup", action="store_true", help="Start SIEM setup workflow")
    parser.add_argument("--report-only", type=str, help="Generate report for session ID")
    parser.add_argument("--no-banner", action="store_true", help="Skip the banner")
    
    args = parser.parse_args()
    
    if not args.no_banner:
        banner()
    
    # Check for API key
    if not os.getenv("GROQ_API_KEY"):
        print(f"\n  {C.RED}[ERROR] GROQ_API_KEY not set!{C.END}")
        print(f"  {C.YELLOW}1. Get free key at: https://console.groq.com{C.END}")
        print(f"  {C.YELLOW}2. Copy .env.example to .env{C.END}")
        print(f"  {C.YELLOW}3. Add your key: GROQ_API_KEY=gsk_xxxxxxxxx{C.END}\n")
        sys.exit(1)
    
    agent = CyberMindAgent()
    
    if args.siem_setup:
        agent.siem_setup_workflow()
    elif args.target:
        agent.pentest_workflow(args.target)
    elif args.report_only:
        data = agent.memory.load_session(args.report_only)
        if data:
            agent.reporter.generate_pentest_report(data, data.get("findings", []))
    else:
        agent.interactive_mode()

if __name__ == "__main__":
    main()
