#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  CyberMind AI - Complete Setup Script for Kali Linux
#  Run this ONCE after cloning the repo
#  Usage: chmod +x setup.sh && ./setup.sh
# ═══════════════════════════════════════════════════════════════════

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

print_step() { echo -e "\n${CYAN}[STEP]${NC} $1"; }
print_ok()   { echo -e "  ${GREEN}[✓]${NC} $1"; }
print_warn() { echo -e "  ${YELLOW}[!]${NC} $1"; }
print_err()  { echo -e "  ${RED}[✗]${NC} $1"; }

echo -e "${CYAN}${BOLD}"
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║     CyberMind AI - Installation Script        ║"
echo "  ║     Kali Linux + VMware Home Lab Setup        ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# ── STEP 1: Check if we're on Kali ────────────────────────────────
print_step "Checking system..."
if grep -qi kali /etc/os-release 2>/dev/null; then
    print_ok "Kali Linux detected"
else
    print_warn "Not Kali Linux — some tools may need manual install"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_ok "Python version: $PYTHON_VERSION"

# ── STEP 2: Update system ─────────────────────────────────────────
print_step "Updating package lists..."
sudo apt-get update -q 2>/dev/null
print_ok "Package lists updated"

# ── STEP 3: Install Kali security tools (if not already there) ────
print_step "Checking/installing security tools..."

TOOLS="nmap nikto gobuster enum4linux searchsploit whatweb arp-scan hydra sqlmap netcat"
MISSING_TOOLS=""

for tool in $TOOLS; do
    if command -v $tool &> /dev/null; then
        print_ok "$tool already installed"
    else
        MISSING_TOOLS="$MISSING_TOOLS $tool"
    fi
done

if [ ! -z "$MISSING_TOOLS" ]; then
    print_warn "Installing missing tools:$MISSING_TOOLS"
    
    # Map tool names to package names
    sudo apt-get install -y nmap nikto gobuster enum4linux exploitdb whatweb arp-scan hydra sqlmap netcat-traditional 2>/dev/null
    
    # Check metasploit separately
    if ! command -v msfconsole &> /dev/null; then
        print_warn "Metasploit not found. Installing..."
        sudo apt-get install -y metasploit-framework 2>/dev/null
    fi
fi

print_ok "Security tools check complete"

# ── STEP 4: Install wordlists ──────────────────────────────────────
print_step "Checking wordlists..."
if [ -f /usr/share/wordlists/rockyou.txt ]; then
    print_ok "rockyou.txt found"
elif [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
    print_warn "Extracting rockyou.txt..."
    sudo gunzip /usr/share/wordlists/rockyou.txt.gz
    print_ok "rockyou.txt extracted"
else
    print_warn "rockyou.txt not found. Installing wordlists..."
    sudo apt-get install -y wordlists 2>/dev/null
    if [ -f /usr/share/wordlists/rockyou.txt.gz ]; then
        sudo gunzip /usr/share/wordlists/rockyou.txt.gz
    fi
fi

# ── STEP 5: Install Python dependencies ──────────────────────────
print_step "Installing Python dependencies..."
pip3 install -r requirements.txt --break-system-packages -q

if [ $? -eq 0 ]; then
    print_ok "Python packages installed"
else
    print_err "Some packages failed. Trying with --user flag..."
    pip3 install -r requirements.txt --user -q
fi

# ── STEP 6: Set up configuration ─────────────────────────────────
print_step "Setting up configuration..."

if [ ! -f .env ]; then
    cp .env.example .env
    print_ok "Created .env file from template"
    print_warn "IMPORTANT: Edit .env and add your GROQ_API_KEY!"
    echo ""
    echo -e "  ${YELLOW}Steps to get FREE Groq API key:${NC}"
    echo "  1. Go to: https://console.groq.com"
    echo "  2. Sign up (free, no credit card)"
    echo "  3. Click 'API Keys' → 'Create API Key'"
    echo "  4. Copy the key (starts with gsk_...)"
    echo "  5. Edit .env: GROQ_API_KEY=gsk_your_key_here"
    echo ""
else
    print_ok ".env file already exists"
fi

# ── STEP 7: Create directories ────────────────────────────────────
print_step "Creating required directories..."
mkdir -p reports/raw_output memory_db/sessions memory_db/targets
print_ok "Directories created"

# ── STEP 8: Make agent executable ────────────────────────────────
chmod +x agent.py
print_ok "agent.py is executable"

# ── STEP 9: Create a quick-launch script ─────────────────────────
print_step "Creating launcher..."
cat > cybermind << 'LAUNCHER'
#!/bin/bash
# Quick launcher for CyberMind AI
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
python3 agent.py "$@"
LAUNCHER
chmod +x cybermind
print_ok "Created 'cybermind' launcher"

# ── STEP 10: Optional - add to PATH ──────────────────────────────
print_step "Adding to PATH (optional)..."
CURRENT_DIR=$(pwd)
if ! grep -q "cybermind" ~/.bashrc 2>/dev/null; then
    echo "export PATH=\"$CURRENT_DIR:\$PATH\"" >> ~/.bashrc
    echo "alias cybermind='python3 $CURRENT_DIR/agent.py'" >> ~/.bashrc
    print_ok "Added to ~/.bashrc (restart terminal or run: source ~/.bashrc)"
else
    print_ok "Already in PATH"
fi

# ── FINAL SUMMARY ─────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  CyberMind AI Setup Complete!${NC}"
echo -e "${GREEN}${BOLD}═══════════════════════════════════════════${NC}"
echo ""
echo -e "  ${CYAN}NEXT STEPS:${NC}"
echo ""
echo -e "  ${YELLOW}1.${NC} Get your FREE Groq API key:"
echo "     → https://console.groq.com (no credit card)"
echo ""
echo -e "  ${YELLOW}2.${NC} Add it to your config:"
echo "     → nano .env"
echo "     → Set GROQ_API_KEY=gsk_your_key_here"
echo ""
echo -e "  ${YELLOW}3.${NC} Launch CyberMind:"
echo "     → python3 agent.py"
echo "     → python3 agent.py --target 192.168.1.1"
echo "     → python3 agent.py --siem-setup"
echo ""
echo -e "  ${YELLOW}4.${NC} Inside interactive mode, try:"
echo "     → 'scan 192.168.1.1'"
echo "     → 'setup wazuh siem'"
echo "     → 'what is privilege escalation'"
echo ""
echo -e "  ${RED}⚠  LEGAL REMINDER:${NC} Only scan systems you own"
echo "     or have explicit written permission to test."
echo ""
