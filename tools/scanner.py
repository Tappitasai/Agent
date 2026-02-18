"""
Security Scanner — Wraps Kali Linux tools with smart execution
Tools: Nmap, Nikto, Gobuster, Enum4Linux, Searchsploit, WhatWeb
"""

import subprocess
import shutil
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent / "reports" / "raw_output"


class SecurityScanner:
    def __init__(self):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        self.available_tools = self._check_tools()
    
    def _check_tools(self):
        """Check which security tools are installed."""
        tools = ["nmap", "nikto", "gobuster", "enum4linux", "searchsploit", 
                 "whatweb", "arp-scan", "netcat", "hydra", "sqlmap"]
        available = {}
        for tool in tools:
            available[tool] = shutil.which(tool) is not None
        return available
    
    def get_status(self):
        """Return which tools are available."""
        return self.available_tools
    
    def quick_scan(self, target):
        """Quick Nmap scan — just top ports."""
        return f"nmap -F --open {target}"
    
    def full_scan(self, target):
        """Full TCP scan with version detection."""
        return f"nmap -sV -sC -p- --open -T4 {target}"
    
    def stealth_scan(self, target):
        """SYN scan (requires root)."""
        return f"sudo nmap -sS -sV -O --top-ports 1000 {target}"
    
    def web_scan(self, target, port=80):
        """Nikto web application scan."""
        return f"nikto -h {target} -p {port}"
    
    def dir_busting(self, target, port=80):
        """Gobuster directory enumeration."""
        return f"gobuster dir -u http://{target}:{port}/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 50"
    
    def smb_enum(self, target):
        """SMB enumeration with enum4linux."""
        return f"enum4linux -a {target}"
    
    def vuln_scan(self, target):
        """Nmap vulnerability scripts."""
        return f"nmap --script vuln {target}"
    
    def exploit_search(self, service, version):
        """Search for exploits with searchsploit."""
        return f"searchsploit {service} {version}"
