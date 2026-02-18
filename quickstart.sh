#!/bin/bash

# CyberMind AI - Quick Start Script
# Automates initial setup for CTF/HackTheBox penetration testing

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║    CyberMind AI v2.0 - Autonomous Pentesting Agent Setup       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Linux
if [[ ! "$OSTYPE" == "linux-gnu"* ]]; then
    echo "[!] Warning: This tool is optimized for Kali Linux/ParrotOS"
    echo "[!] Some tools may not be available on this system"
fi

echo "[1] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Install with: sudo apt install python3 python3-pip"
    exit 1
fi
echo "[✓] Python $(python3 --version | cut -d' ' -f2) found"

echo ""
echo "[2] Checking required tools..."
TOOLS=("nmap" "git" "curl")
MISSING=()
for tool in "${TOOLS[@]}"; do
    if command -v $tool &> /dev/null; then
        echo "[✓] $tool found"
    else
        echo "[!] $tool not found"
        MISSING+=("$tool")
    fi
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    echo "[!] Missing tools: ${MISSING[*]}"
    echo "[!] Install with: sudo apt install ${MISSING[*]}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "[3] Installing Python dependencies..."
pip install -r requirements.txt --break-system-packages -q 2>/dev/null && echo "[✓] Dependencies installed" || echo "[!] Some dependencies may have failed"

echo ""
echo "[4] Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[✓] Created .env file"
    echo ""
    echo "[!] IMPORTANT: Add your Groq API key to .env"
    echo "    1. Get free key at: https://console.groq.com"
    echo "    2. Edit .env and add: GROQ_API_KEY=gsk_your_key_here"
    echo ""
    read -p "Have you added your API key? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "[!] Setup incomplete. Add API key to .env and run again."
        exit 1
    fi
else
    echo "[✓] .env file already exists"
fi

echo ""
echo "[5] Testing CyberMind..."
python3 agent.py --help > /dev/null 2>&1 && echo "[✓] CyberMind ready!" || {
    echo "[ERROR] CyberMind test failed"
    exit 1
}

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   SETUP COMPLETE!                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Quick Commands:"
echo "  Autonomous mode:  python3 agent.py --target 10.10.10.40 --autonomous"
echo "  Manual mode:      python3 agent.py --target 10.10.10.40"
echo "  Interactive:      python3 agent.py"
echo ""
echo "Documentation:"
echo "  Quick start:      cat USAGE.md"
echo "  Full docs:        cat README.md"
echo "  Autonomous mode:  cat AUTONOMOUS_MODE.md"
echo ""
echo "Ready to pwn! Let's go... 🚀"
echo ""
