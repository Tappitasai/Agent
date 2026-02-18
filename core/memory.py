"""
Memory System — CyberMind's brain storage
Stores and retrieves:
  - Past pentest sessions
  - Findings per target
  - Successful commands (reinforcement learning)
  - Failed commands and their fixes
  - User preferences

This is how CyberMind LEARNS over time:
  - "I scanned this IP before, here's what I found"
  - "This command failed last time, I'll try the fix first"
  - "This target has port 80 open, let me start with web checks"
"""

import os
import json
from datetime import datetime
from pathlib import Path

# Memory database is stored as JSON files in memory_db/
MEMORY_DIR = Path(__file__).parent.parent / "memory_db"


class MemorySystem:
    def __init__(self):
        MEMORY_DIR.mkdir(exist_ok=True)
        (MEMORY_DIR / "sessions").mkdir(exist_ok=True)
        (MEMORY_DIR / "targets").mkdir(exist_ok=True)
        
        self.index_file = MEMORY_DIR / "index.json"
        self.fixes_file = MEMORY_DIR / "known_fixes.json"
        self.prefs_file = MEMORY_DIR / "preferences.json"
        
        # Load or create index
        self.index = self._load_json(self.index_file, default={"sessions": [], "targets": {}})
        self.known_fixes = self._load_json(self.fixes_file, default={"fixes": []})
        self.preferences = self._load_json(self.prefs_file, default={
            "default_scan_type": "standard",
            "auto_approve_recon": False,
            "report_format": "detailed"
        })
        
    def _load_json(self, path, default=None):
        """Safely load a JSON file, return default if not found."""
        try:
            if Path(path).exists():
                with open(path, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return default or {}
    
    def _save_json(self, path, data):
        """Save data to a JSON file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def save_session(self, session_id, target, report_data, findings):
        """Save a complete pentest session to disk."""
        session_file = MEMORY_DIR / "sessions" / f"{session_id}.json"
        
        session = {
            "id": session_id,
            "target": target,
            "date": datetime.now().isoformat(),
            "findings": findings,
            "report": report_data,
            "finding_count": len(findings),
            "severity_counts": self._count_severities(findings)
        }
        
        self._save_json(session_file, session)
        
        # Update index
        self.index["sessions"].append({
            "id": session_id,
            "target": target,
            "date": datetime.now().isoformat(),
            "finding_count": len(findings),
            "summary": f"{len(findings)} findings"
        })
        
        # Update target history
        if target not in self.index["targets"]:
            self.index["targets"][target] = []
        self.index["targets"][target].append(session_id)
        
        self._save_json(self.index_file, self.index)
        
        # Also save target-specific file
        target_safe = target.replace(".", "_").replace("/", "_")
        target_file = MEMORY_DIR / "targets" / f"{target_safe}.json"
        
        target_data = self._load_json(target_file, default={"target": target, "sessions": []})
        target_data["sessions"].append({
            "session_id": session_id,
            "date": datetime.now().isoformat(),
            "findings": findings[:20],  # Store up to 20 findings per target
            "finding_count": len(findings)
        })
        self._save_json(target_file, target_data)
        
        print(f"  [MEMORY] Session {session_id} saved ({len(findings)} findings)")
    
    def load_session(self, session_id):
        """Load a specific session by ID."""
        session_file = MEMORY_DIR / "sessions" / f"{session_id}.json"
        return self._load_json(session_file)
    
    def get_target_history(self, target_ip):
        """Get all past findings for a specific target IP."""
        target_safe = target_ip.replace(".", "_").replace("/", "_")
        target_file = MEMORY_DIR / "targets" / f"{target_safe}.json"
        
        data = self._load_json(target_file)
        if data:
            sessions = data.get("sessions", [])
            # Return last 3 sessions' findings
            all_findings = []
            for session in sessions[-3:]:
                all_findings.extend(session.get("findings", []))
            return all_findings
        return []
    
    def search(self, query):
        """
        Search memory for relevant past sessions.
        Simple keyword search — looks through findings and session data.
        """
        results = []
        query_lower = query.lower()
        
        for session_meta in self.index.get("sessions", [])[-20:]:  # Search last 20
            session_id = session_meta.get("id")
            if not session_id:
                continue
                
            session = self.load_session(session_id)
            if not session:
                continue
            
            # Check if query matches target, findings, or report
            target = session.get("target", "")
            findings_str = json.dumps(session.get("findings", [])).lower()
            
            if query_lower in target or query_lower in findings_str:
                results.append({
                    "session_id": session_id,
                    "target": target,
                    "date": session_meta.get("date", ""),
                    "summary": f"{session_meta.get('finding_count', 0)} findings on {target}",
                    "findings": session.get("findings", [])[:5]
                })
        
        return results
    
    def list_sessions(self):
        """List all past sessions (most recent first)."""
        sessions = self.index.get("sessions", [])
        return sorted(sessions, key=lambda x: x.get("date", ""), reverse=True)
    
    def save_fix(self, failed_command, error, fix_command, success):
        """
        Save a command fix to the knowledge base.
        This is how CyberMind improves over time — it remembers what fixes work.
        """
        fix_entry = {
            "failed_command_pattern": failed_command[:100],
            "error_pattern": error[:200],
            "fix": fix_command,
            "worked": success,
            "date": datetime.now().isoformat()
        }
        
        self.known_fixes["fixes"].append(fix_entry)
        
        # Keep only last 100 fixes
        if len(self.known_fixes["fixes"]) > 100:
            self.known_fixes["fixes"] = self.known_fixes["fixes"][-100:]
        
        self._save_json(self.fixes_file, self.known_fixes)
    
    def get_known_fix(self, failed_command, error):
        """
        Check if we've seen this error before and have a fix.
        This makes CyberMind smarter over time.
        """
        for fix in reversed(self.known_fixes.get("fixes", [])):
            if (fix.get("failed_command_pattern", "") in failed_command or
                fix.get("error_pattern", "") in error):
                if fix.get("worked", False):
                    return fix["fix"]
        return None
    
    def get_context(self):
        """Get recent context for AI to use in interpreting commands."""
        recent_sessions = self.list_sessions()[:3]
        return {
            "recent_targets": [s.get("target") for s in recent_sessions],
            "total_sessions": len(self.index.get("sessions", [])),
            "known_targets": list(self.index.get("targets", {}).keys())
        }
    
    def _count_severities(self, findings):
        """Count findings by severity level."""
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in findings:
            sev = f.get("severity", "INFO")
            counts[sev] = counts.get(sev, 0) + 1
        return counts
    
    def update_preference(self, key, value):
        """Update a user preference."""
        self.preferences[key] = value
        self._save_json(self.prefs_file, self.preferences)
    
    def get_stats(self):
        """Get overall stats about CyberMind's learning progress."""
        sessions = self.index.get("sessions", [])
        targets = self.index.get("targets", {})
        fixes = self.known_fixes.get("fixes", [])
        
        return {
            "total_sessions": len(sessions),
            "unique_targets": len(targets),
            "known_fixes": len([f for f in fixes if f.get("worked")]),
            "total_findings": sum(s.get("finding_count", 0) for s in sessions)
        }
