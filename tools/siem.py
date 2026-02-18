"""
SIEM Setup — Automates Wazuh installation and configuration for home lab.
Wazuh is the best free open-source SIEM — enterprise-grade, free forever.

Architecture for home lab:
  Kali VM (Wazuh Manager + Dashboard) 
      ↑ agents report to
  Other VMs (Windows, Ubuntu, Metasploitable targets)
"""


class SIEMSetup:
    def get_setup_plan(self):
        """
        Returns the complete Wazuh SIEM setup plan as a list of steps.
        Each step has: description, command, risk, notes, troubleshooting.
        """
        return [
            # ── PRE-FLIGHT CHECKS ───────────────────────────────────────────
            {
                "description": "Check system RAM (Wazuh needs 4GB minimum)",
                "command": "free -h",
                "risk": "LOW",
                "required": True,
                "notes": "Need at least 4GB free. Wazuh Manager uses ~2-3GB RAM.",
                "troubleshooting": "If RAM is low, close other VMs before proceeding"
            },
            {
                "description": "Check available disk space (need 20GB+)",
                "command": "df -h /",
                "risk": "LOW",
                "required": True,
                "notes": "Wazuh logs grow fast. 50GB recommended for home lab.",
                "troubleshooting": "Free up space with: apt autoremove && apt autoclean"
            },
            {
                "description": "Update package lists",
                "command": "sudo apt-get update -y",
                "risk": "LOW",
                "required": True,
                "notes": "Required before installing any packages.",
                "troubleshooting": "If fails: check internet connection in VM"
            },
            {
                "description": "Install required dependencies",
                "command": "sudo apt-get install -y curl wget gnupg apt-transport-https",
                "risk": "LOW",
                "required": True,
                "notes": "These are needed to add the Wazuh repository.",
                "troubleshooting": ""
            },
            
            # ── WAZUH REPO SETUP ─────────────────────────────────────────────
            {
                "description": "Import Wazuh GPG signing key",
                "command": "curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && sudo chmod 644 /usr/share/keyrings/wazuh.gpg",
                "risk": "LOW",
                "required": True,
                "notes": "This verifies the Wazuh packages are authentic (not tampered with).",
                "troubleshooting": "If curl fails: check your internet connection inside Kali VM"
            },
            {
                "description": "Add Wazuh 4.x repository",
                "command": 'echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee -a /etc/apt/sources.list.d/wazuh.list',
                "risk": "LOW",
                "required": True,
                "notes": "Adds Wazuh's official package repository to your system.",
                "troubleshooting": ""
            },
            {
                "description": "Update package list with new Wazuh repo",
                "command": "sudo apt-get update",
                "risk": "LOW",
                "required": True,
                "notes": "",
                "troubleshooting": "If GPG error appears: re-run the GPG key import step"
            },
            
            # ── WAZUH MANAGER INSTALL ────────────────────────────────────────
            {
                "description": "Install Wazuh Manager (the central brain of your SIEM)",
                "command": "sudo apt-get install -y wazuh-manager",
                "risk": "LOW",
                "required": True,
                "notes": "This is the main server that collects and analyzes security events. Takes ~5-10 minutes.",
                "troubleshooting": "If fails: sudo apt-get -f install then retry"
            },
            {
                "description": "Enable and start Wazuh Manager service",
                "command": "sudo systemctl daemon-reload && sudo systemctl enable wazuh-manager && sudo systemctl start wazuh-manager",
                "risk": "LOW",
                "required": True,
                "notes": "Makes Wazuh start automatically on boot.",
                "troubleshooting": "Check logs with: sudo journalctl -u wazuh-manager -f"
            },
            {
                "description": "Check Wazuh Manager status",
                "command": "sudo systemctl status wazuh-manager",
                "risk": "LOW",
                "required": False,
                "notes": "Should show 'active (running)'. If not, check the troubleshooting below.",
                "troubleshooting": "sudo /var/ossec/bin/wazuh-control status"
            },
            
            # ── FILEBEAT + ELASTICSEARCH ─────────────────────────────────────
            {
                "description": "Install Filebeat (ships Wazuh logs to the dashboard)",
                "command": "sudo apt-get install -y filebeat=8.11.3",
                "risk": "LOW",
                "required": True,
                "notes": "Filebeat forwards Wazuh alerts to the OpenSearch/Elasticsearch backend.",
                "troubleshooting": "Try: sudo apt-get install -y filebeat"
            },
            {
                "description": "Download Wazuh Filebeat configuration",
                "command": "sudo curl -so /etc/filebeat/filebeat.yml https://packages.wazuh.com/4.7/tpl/wazuh/filebeat/filebeat.yml",
                "risk": "LOW",
                "required": True,
                "notes": "Pre-configured to work with Wazuh out of the box.",
                "troubleshooting": ""
            },
            
            # ── WAZUH DASHBOARD (Web UI) ─────────────────────────────────────
            {
                "description": "Install Wazuh Dashboard (beautiful web UI - access at https://localhost)",
                "command": "sudo apt-get install -y wazuh-dashboard",
                "risk": "LOW",
                "required": True,
                "notes": "The web interface for your SIEM. Open browser → https://localhost after this. Takes 5+ min.",
                "troubleshooting": "If fails, skip and use API directly"
            },
            {
                "description": "Enable and start Wazuh Dashboard",
                "command": "sudo systemctl enable wazuh-dashboard && sudo systemctl start wazuh-dashboard",
                "risk": "LOW",
                "required": False,
                "notes": "",
                "troubleshooting": "sudo journalctl -u wazuh-dashboard -f"
            },
            
            # ── POST-INSTALL HARDENING ───────────────────────────────────────
            {
                "description": "Set Wazuh admin password (IMPORTANT: change default password!)",
                "command": 'sudo /usr/share/wazuh-indexer/plugins/opensearch-security/tools/wazuh-passwords-tool.sh --change-all | sudo tee /root/wazuh_passwords.txt',
                "risk": "MEDIUM",
                "required": False,
                "notes": "Passwords saved to /root/wazuh_passwords.txt — store these safely!",
                "troubleshooting": ""
            },
            {
                "description": "Add a Wazuh agent registration token (for connecting other VMs)",
                "command": "sudo /var/ossec/bin/manage_agents",
                "risk": "LOW",
                "required": False,
                "notes": "Use option (A) to add agent, then (E) to get the token for other VMs.",
                "troubleshooting": ""
            },
            
            # ── VERIFICATION ─────────────────────────────────────────────────
            {
                "description": "View real-time Wazuh alerts (test it's working)",
                "command": "sudo tail -f /var/ossec/logs/alerts/alerts.json | python3 -m json.tool",
                "risk": "LOW",
                "required": False,
                "notes": "Press Ctrl+C to stop. You should see security events streaming in.",
                "troubleshooting": "No events? Try triggering one: sudo cat /etc/shadow"
            },
            {
                "description": "Check all Wazuh services are running",
                "command": "sudo /var/ossec/bin/wazuh-control status",
                "risk": "LOW",
                "required": False,
                "notes": "All services should show 'is running'",
                "troubleshooting": "Restart with: sudo /var/ossec/bin/wazuh-control restart"
            },
        ]
    
    def get_agent_install_commands(self, manager_ip, agent_os="ubuntu"):
        """Get commands to install Wazuh agent on a target VM."""
        if agent_os == "ubuntu" or agent_os == "kali":
            return [
                f"curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | sudo gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import",
                f'echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | sudo tee /etc/apt/sources.list.d/wazuh.list',
                "sudo apt-get update",
                "sudo apt-get install -y wazuh-agent",
                f'sudo WAZUH_MANAGER="{manager_ip}" WAZUH_AGENT_NAME="$(hostname)" /var/ossec/bin/agent-auth -m {manager_ip}',
                "sudo systemctl enable wazuh-agent && sudo systemctl start wazuh-agent"
            ]
        elif agent_os == "windows":
            return [
                f"# Download from: https://packages.wazuh.com/4.x/windows/wazuh-agent-4.7.0-1.msi",
                f'# Install with: msiexec.exe /i wazuh-agent-4.7.0-1.msi /q WAZUH_MANAGER="{manager_ip}" WAZUH_REGISTRATION_SERVER="{manager_ip}"',
                "# Then: NET START WazuhSvc"
            ]
        return []
