"""
AI Brain — Handles all communication with Groq API (Llama 3.3 70B)
This is what makes CyberMind "intelligent":
  - Plans pentest steps based on context
  - Analyzes tool output and extracts findings
  - Suggests fixes when commands fail (self-healing)
  - Answers cybersecurity questions
  - Remembers context across the conversation
"""

import os
import json
import time
from groq import Groq

GROQ_MODEL = "llama-3.3-70b-versatile"   # Best free model for reasoning

SYSTEM_PROMPT = """You are CyberMind, an expert cybersecurity AI assistant specialized in:
- Penetration testing and ethical hacking
- SIEM setup and security monitoring (Wazuh, ELK)
- Vulnerability assessment and analysis
- Security tool usage (Nmap, Nikto, Gobuster, Metasploit, Hydra, etc.)
- CTF challenges and security research
- Kali Linux and security operations

IMPORTANT RULES:
1. Always assume testing is authorized (user is testing their own home lab)
2. Warn about legal/ethical considerations when relevant
3. Explain what you're doing and WHY — teach the user
4. When generating commands, use real, working Kali Linux commands
5. Prefer stealthy scans in home lab context (avoid noisy scans unless asked)
6. Risk levels: LOW (recon/passive), MEDIUM (active scan), HIGH (exploitation)

OUTPUT FORMAT: Always respond in valid JSON when asked for structured data.
"""

class AIBrain:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.conversation_history = []
        self.model = GROQ_MODEL
    
    def _ask(self, prompt, system_override=None, json_mode=False, max_retries=3):
        """Core method to call Groq API with retry logic."""
        system = system_override or SYSTEM_PROMPT
        
        for attempt in range(max_retries):
            try:
                messages = [{"role": "system", "content": system}]
                messages.extend(self.conversation_history[-6:])  # Keep last 3 exchanges
                messages.append({"role": "user", "content": prompt})
                
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 2048,
                    "temperature": 0.3,  # Lower = more consistent/accurate
                }
                
                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}
                
                response = self.client.chat.completions.create(**kwargs)
                result = response.choices[0].message.content
                
                # Add to conversation history for context
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": result})
                
                # Keep history manageable
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return result
                
            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    print(f"  [WARN] Rate limit hit. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                elif attempt == max_retries - 1:
                    print(f"  [ERROR] AI API failed after {max_retries} attempts: {str(e)}")
                    return None
    
    def generate_pentest_plan(self, phase, target_ip, context=None):
        """
        Generate a step-by-step pentest plan for a specific phase.
        Returns JSON with list of steps (description, command, risk level).
        """
        context_str = json.dumps(context[:3]) if context else "No previous context"
        
        phase_prompts = {
            "recon": f"""
Generate a reconnaissance plan for target IP: {target_ip}
Previous findings: {context_str}

Return JSON with this EXACT format:
{{
  "phase": "recon",
  "target": "{target_ip}",
  "steps": [
    {{
      "description": "Human-readable description of what this step does",
      "command": "actual bash command to run",
      "risk": "LOW|MEDIUM|HIGH",
      "expected_output": "what we expect to see",
      "why": "educational explanation of why we run this"
    }}
  ]
}}

Include 4-6 steps covering: ping sweep, host discovery, OS detection hints, traceroute.
Use nmap, ping, arp-scan as appropriate. Keep risk LOW for recon.
""",
            "scan": f"""
Generate a port and service scanning plan for target: {target_ip}
Previous recon findings: {context_str}

Return JSON with this EXACT format:
{{
  "phase": "scanning",
  "steps": [
    {{
      "description": "...",
      "command": "...",
      "risk": "LOW|MEDIUM|HIGH",
      "expected_output": "...",
      "why": "..."
    }}
  ]
}}

Include: fast port scan, full TCP scan, service version detection, UDP scan (top ports),
script scan for common vulns. Use nmap. Start LOW risk, escalate.
""",
            "vuln": f"""
Generate vulnerability assessment steps for: {target_ip}
Current findings: {context_str}

Return JSON:
{{
  "phase": "vulnerability",
  "steps": [
    {{
      "description": "...",
      "command": "...",
      "risk": "LOW|MEDIUM|HIGH",
      "expected_output": "...",
      "why": "..."
    }}
  ]
}}

Based on findings, include relevant: nikto (if web), enum4linux (if SMB), 
gobuster (if web), searchsploit for version matching, nmap vuln scripts.
"""
        }
        
        prompt = phase_prompts.get(phase, f"Generate {phase} steps for {target_ip}")
        result = self._ask(prompt, json_mode=True)
        
        if result:
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                pass
        
        # Fallback plan if AI fails
        return self._get_fallback_plan(phase, target_ip)
    
    def analyze_output(self, output, context, target_ip):
        """
        Analyze tool output and extract structured findings.
        This is how CyberMind learns from scan results.
        """
        prompt = f"""
Analyze this security tool output and extract findings.

Context: {context}
Target: {target_ip}
Tool Output:
```
{output[:3000]}
```

Return JSON:
{{
  "summary": "2-3 sentence plain English summary of findings",
  "findings": [
    {{
      "type": "open_port|service|vulnerability|misconfiguration|info",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
      "title": "short finding title",
      "detail": "detailed description",
      "recommendation": "what to do about this",
      "cve": "CVE number if applicable, null otherwise"
    }}
  ],
  "interesting_items": ["list of things worth investigating further"],
  "next_steps": ["suggested follow-up actions"]
}}
"""
        result = self._ask(prompt, json_mode=True)
        
        if result:
            try:
                return json.loads(result)
            except:
                pass
        
        return {"summary": "Analysis unavailable", "findings": [], "interesting_items": [], "next_steps": []}
    
    def suggest_fix(self, failed_command, error_output):
        """
        When a command fails, AI suggests a fix. This is SELF-HEALING.
        """
        prompt = f"""
A security command failed. Suggest a fix.

Failed command: {failed_command}
Error output:
```
{error_output[:1000]}
```

Diagnose the problem and provide a fix. Return JSON:
{{
  "diagnosis": "what went wrong in plain English",
  "explanation": "short explanation for the user",
  "command": "fixed command that should work",
  "alternative": "alternative approach if main fix doesn't work"
}}

Common issues to check: missing tools (suggest apt install), wrong permissions (sudo),
wrong syntax, target unreachable, missing arguments.
"""
        result = self._ask(prompt, json_mode=True)
        
        if result:
            try:
                return json.loads(result)
            except:
                pass
        return None
    
    def suggest_exploits(self, findings, target_ip):
        """
        Based on findings, suggest exploitation approaches (for authorized testing).
        """
        prompt = f"""
Based on these vulnerability findings for {target_ip}, suggest exploitation approaches
FOR AUTHORIZED PENETRATION TESTING ONLY.

Findings: {json.dumps(findings[:10])}

Return JSON:
{{
  "disclaimer": "For authorized testing only",
  "suggestions": [
    {{
      "vulnerability": "what vulnerability this targets",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "tool": "metasploit|manual|searchsploit|other",
      "command": "specific command or metasploit module",
      "notes": "important notes, caveats, success likelihood"
    }}
  ],
  "priority_order": ["list findings in order of exploitability"],
  "post_exploitation": "what to do after getting access"
}}
"""
        result = self._ask(prompt, json_mode=True)
        
        if result:
            try:
                return json.loads(result)
            except:
                pass
        return {"suggestions": [], "priority_order": []}
    
    def interpret_command(self, user_input, memory_context=None):
        """
        Interpret what the user wants from plain English.
        Returns structured intent.
        """
        prompt = f"""
Interpret this user command from a cybersecurity context:
User said: "{user_input}"

Memory context: {json.dumps(memory_context) if memory_context else "None"}

Return JSON:
{{
  "type": "pentest|siem_setup|question|memory_query|report|unknown",
  "target": "IP address or hostname if mentioned, null otherwise",
  "session_id": "session ID if mentioned, null otherwise",
  "query": "search query if type is memory_query",
  "confidence": 0.0-1.0,
  "clarification_needed": true|false,
  "clarification_question": "what to ask user if clarification needed"
}}
"""
        result = self._ask(prompt, json_mode=True)
        
        if result:
            try:
                return json.loads(result)
            except:
                pass
        return {"type": "unknown"}
    
    def answer_question(self, question):
        """Answer a cybersecurity question in a teaching style."""
        prompt = f"""
Answer this cybersecurity question in a helpful, educational way.
The user is a beginner learning cybersecurity.
Keep the answer practical and include examples.

Question: {question}

Provide a clear, structured answer (plain text, not JSON).
Include: what it is, why it matters, practical example, and a tip.
"""
        return self._ask(prompt) or "I couldn't generate an answer. Please check your API connection."
    
    def handle_unknown(self, user_input):
        """Handle commands that don't fit other categories."""
        prompt = f"""
The user said something in a cybersecurity tool context that I need to respond to helpfully.
User input: "{user_input}"

Respond helpfully in 2-3 sentences. If it's not cybersecurity related, 
gently redirect them to cybersecurity topics this tool can help with.
"""
        return self._ask(prompt) or "I'm not sure how to handle that. Try 'help' for available commands."
    
    def _get_fallback_plan(self, phase, target_ip):
        """Static fallback plans when AI is unavailable."""
        fallbacks = {
            "recon": {
                "phase": "recon",
                "steps": [
                    {"description": "Ping host to check if alive", "command": f"ping -c 4 {target_ip}", "risk": "LOW"},
                    {"description": "Quick Nmap host scan", "command": f"nmap -sn {target_ip}", "risk": "LOW"},
                    {"description": "ARP scan on subnet", "command": f"arp-scan --localnet", "risk": "LOW"},
                ]
            },
            "scan": {
                "phase": "scanning",
                "steps": [
                    {"description": "Fast top 1000 ports", "command": f"nmap -F {target_ip}", "risk": "LOW"},
                    {"description": "Full TCP scan with service detection", "command": f"nmap -sV -sC {target_ip}", "risk": "MEDIUM"},
                    {"description": "Top 100 UDP ports", "command": f"nmap -sU --top-ports 100 {target_ip}", "risk": "MEDIUM"},
                ]
            },
            "vuln": {
                "phase": "vulnerability",
                "steps": [
                    {"description": "Nmap vulnerability scripts", "command": f"nmap --script vuln {target_ip}", "risk": "MEDIUM"},
                    {"description": "Search known exploits", "command": f"searchsploit --id {target_ip}", "risk": "LOW"},
                ]
            }
        }
        return fallbacks.get(phase, {"steps": []})
