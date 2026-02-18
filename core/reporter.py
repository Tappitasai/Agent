"""
Report Generator — Creates professional PDF reports for every session.
Covers: Pentest reports, SIEM setup docs, vulnerability summaries.
Uses ReportLab for PDF creation.
"""

import os
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, black, white, red, orange
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                     TableStyle, PageBreak, HRFlowable)
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("  [WARN] reportlab not installed. PDF reports disabled.")
    print("  Run: pip install reportlab")

REPORTS_DIR = Path(__file__).parent.parent / "reports"

# ─── Colors ───────────────────────────────────────────────────────────────────
DARK_BG   = HexColor("#1a1a2e") if REPORTLAB_AVAILABLE else None
ACCENT    = HexColor("#e94560") if REPORTLAB_AVAILABLE else None
MID       = HexColor("#16213e") if REPORTLAB_AVAILABLE else None
LIGHT     = HexColor("#0f3460") if REPORTLAB_AVAILABLE else None
TEXT      = HexColor("#e8e8e8") if REPORTLAB_AVAILABLE else None
GREEN_OK  = HexColor("#00d4aa") if REPORTLAB_AVAILABLE else None
ORANGE_W  = HexColor("#f5a623") if REPORTLAB_AVAILABLE else None
RED_CRIT  = HexColor("#ff4757") if REPORTLAB_AVAILABLE else None

SEVERITY_COLORS = {
    "CRITICAL": "#ff4757",
    "HIGH":     "#ff6b35",
    "MEDIUM":   "#f5a623",
    "LOW":      "#00d4aa",
    "INFO":     "#4a9eda",
}


class ReportGenerator:
    def __init__(self):
        REPORTS_DIR.mkdir(exist_ok=True)
        if REPORTLAB_AVAILABLE:
            self.styles = self._build_styles()
    
    def _build_styles(self):
        """Create custom styles for the dark-themed report."""
        base = getSampleStyleSheet()
        styles = {}
        
        styles["title"] = ParagraphStyle(
            "ReportTitle",
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=TEXT,
            spaceAfter=6,
            alignment=TA_CENTER
        )
        styles["subtitle"] = ParagraphStyle(
            "Subtitle",
            fontName="Helvetica",
            fontSize=12,
            textColor=ACCENT,
            spaceAfter=20,
            alignment=TA_CENTER
        )
        styles["heading1"] = ParagraphStyle(
            "H1",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=ACCENT,
            spaceBefore=16,
            spaceAfter=6
        )
        styles["heading2"] = ParagraphStyle(
            "H2",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=GREEN_OK,
            spaceBefore=12,
            spaceAfter=4
        )
        styles["body"] = ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=10,
            textColor=TEXT,
            spaceAfter=6,
            leading=14
        )
        styles["code"] = ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=8,
            textColor=GREEN_OK,
            spaceAfter=4,
            backColor=MID,
            leftIndent=10,
            rightIndent=10
        )
        styles["warning"] = ParagraphStyle(
            "Warning",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=ORANGE_W,
            spaceAfter=4
        )
        return styles
    
    def generate_pentest_report(self, report_data, findings):
        """Generate a comprehensive pentest PDF report."""
        if not REPORTLAB_AVAILABLE:
            return self._save_text_report(report_data, findings)
        
        target = report_data.get("target", "Unknown")
        session_id = report_data.get("session_id", "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"pentest_{target.replace('.', '_')}_{timestamp}.pdf"
        filepath = REPORTS_DIR / filename
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        s = self.styles
        
        # ── COVER PAGE ────────────────────────────────────────────────────────
        story.append(Spacer(1, 2*cm))
        
        # Header bar
        header_data = [[Paragraph("CYBERMIND AI", ParagraphStyle(
            "hdr", fontName="Helvetica-Bold", fontSize=10, textColor=TEXT))]]
        header_table = Table(header_data, colWidths=[17*cm])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 1*cm))
        
        story.append(Paragraph("PENETRATION TEST REPORT", s["title"]))
        story.append(Paragraph(f"Target: {target}", s["subtitle"]))
        story.append(Spacer(1, 0.5*cm))
        
        # Meta table
        meta_rows = [
            ["Session ID:", session_id],
            ["Target IP:", target],
            ["Date:", datetime.now().strftime("%B %d, %Y %H:%M:%S")],
            ["Start Time:", report_data.get("start_time", "N/A")],
            ["End Time:", report_data.get("end_time", "N/A")],
            ["Total Findings:", str(len(findings))],
        ]
        
        meta_table = Table(meta_rows, colWidths=[4*cm, 13*cm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,-1), MID),
            ("BACKGROUND", (1,0), (1,-1), DARK_BG),
            ("TEXTCOLOR", (0,0), (-1,-1), TEXT),
            ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, LIGHT),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 1*cm))
        
        # Legal disclaimer
        disclaimer_data = [[Paragraph(
            "LEGAL DISCLAIMER: This report was generated for AUTHORIZED testing only. "
            "All testing was performed on systems owned or explicitly authorized by the tester. "
            "Unauthorized use of this information is illegal.", 
            s["warning"]
        )]]
        disc_table = Table(disclaimer_data, colWidths=[17*cm])
        disc_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), HexColor("#2d1f00")),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
            ("BOX", (0,0), (-1,-1), 1, ORANGE_W),
        ]))
        story.append(disc_table)
        story.append(PageBreak())
        
        # ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────
        story.append(Paragraph("1. EXECUTIVE SUMMARY", s["heading1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        story.append(Spacer(1, 0.3*cm))
        
        # Severity counts
        sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in findings:
            sev = f.get("severity", "INFO")
            sev_counts[sev] = sev_counts.get(sev, 0) + 1
        
        sev_data = [["Severity", "Count", "Action Required"]]
        sev_actions = {
            "CRITICAL": "Immediate action required",
            "HIGH":     "Remediate within 7 days",
            "MEDIUM":   "Remediate within 30 days",
            "LOW":      "Remediate next cycle",
            "INFO":     "Review and document"
        }
        for sev, count in sev_counts.items():
            sev_data.append([sev, str(count), sev_actions[sev]])
        
        sev_table = Table(sev_data, colWidths=[4*cm, 3*cm, 10*cm])
        sev_styles = [
            ("BACKGROUND", (0,0), (-1,0), LIGHT),
            ("TEXTCOLOR", (0,0), (-1,0), TEXT),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("GRID", (0,0), (-1,-1), 0.5, LIGHT),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]
        for i, sev in enumerate(["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"], 1):
            color = HexColor(SEVERITY_COLORS[sev])
            sev_styles.append(("TEXTCOLOR", (0,i), (0,i), color))
            sev_styles.append(("FONTNAME", (0,i), (0,i), "Helvetica-Bold"))
            sev_styles.append(("BACKGROUND", (0,i), (-1,i), DARK_BG))
            sev_styles.append(("TEXTCOLOR", (1,i), (-1,i), TEXT))
        
        sev_table.setStyle(TableStyle(sev_styles))
        story.append(sev_table)
        story.append(Spacer(1, 0.5*cm))
        
        # ── FINDINGS ──────────────────────────────────────────────────────────
        story.append(PageBreak())
        story.append(Paragraph("2. DETAILED FINDINGS", s["heading1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        story.append(Spacer(1, 0.3*cm))
        
        if findings:
            # Sort by severity
            sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}
            sorted_findings = sorted(findings, key=lambda x: sev_order.get(x.get("severity", "INFO"), 5))
            
            for i, finding in enumerate(sorted_findings, 1):
                sev = finding.get("severity", "INFO")
                sev_color = HexColor(SEVERITY_COLORS.get(sev, "#4a9eda"))
                
                story.append(Paragraph(
                    f"Finding #{i}: {finding.get('title', 'Untitled')}",
                    s["heading2"]
                ))
                
                # Finding details table
                details_rows = [
                    ["Severity:", sev],
                    ["Type:", finding.get("type", "Unknown")],
                ]
                if finding.get("cve"):
                    details_rows.append(["CVE:", finding["cve"]])
                
                det_table = Table(details_rows, colWidths=[3*cm, 14*cm])
                det_style = [
                    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
                    ("FONTSIZE", (0,0), (-1,-1), 9),
                    ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
                    ("TOPPADDING", (0,0), (-1,-1), 4),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                    ("LEFTPADDING", (0,0), (-1,-1), 8),
                    ("TEXTCOLOR", (0,0), (0,-1), HexColor("#aaaaaa")),
                    ("TEXTCOLOR", (1,0), (1,0), sev_color),
                    ("TEXTCOLOR", (1,1), (-1,-1), TEXT),
                ]
                det_table.setStyle(TableStyle(det_style))
                story.append(det_table)
                
                story.append(Paragraph(
                    finding.get("detail", "No details available."),
                    s["body"]
                ))
                
                if finding.get("recommendation"):
                    story.append(Paragraph(
                        f"Recommendation: {finding['recommendation']}",
                        ParagraphStyle("rec", fontName="Helvetica-BoldOblique",
                                       fontSize=9, textColor=GREEN_OK, spaceAfter=8)
                    ))
                
                story.append(Spacer(1, 0.3*cm))
        else:
            story.append(Paragraph("No findings were recorded in this session.", s["body"]))
        
        # ── SCAN LOGS ─────────────────────────────────────────────────────────
        story.append(PageBreak())
        story.append(Paragraph("3. COMMANDS EXECUTED", s["heading1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        story.append(Spacer(1, 0.3*cm))
        
        phases = report_data.get("phases", {})
        for phase_name, phase_steps in phases.items():
            if phase_name == "exploit_hints":
                continue
            story.append(Paragraph(phase_name.upper().replace("_", " "), s["heading2"]))
            
            if isinstance(phase_steps, list):
                for step in phase_steps:
                    if isinstance(step, dict):
                        story.append(Paragraph(
                            f"Step: {step.get('step', '')}",
                            ParagraphStyle("stepname", fontName="Helvetica-Bold",
                                           fontSize=9, textColor=ORANGE_W, spaceAfter=2)
                        ))
                        cmd = step.get('command', '')
                        if cmd:
                            story.append(Paragraph(f"$ {cmd}", s["code"]))
                        summary = step.get('output_summary', '')
                        if summary:
                            story.append(Paragraph(summary, s["body"]))
                        story.append(Spacer(1, 0.2*cm))
        
        # ── RECOMMENDATIONS ───────────────────────────────────────────────────
        story.append(PageBreak())
        story.append(Paragraph("4. REMEDIATION RECOMMENDATIONS", s["heading1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        story.append(Spacer(1, 0.3*cm))
        
        if findings:
            story.append(Paragraph(
                "The following remediation steps are recommended based on findings:",
                s["body"]
            ))
            
            for i, finding in enumerate(sorted_findings[:10], 1):
                if finding.get("recommendation"):
                    story.append(Paragraph(
                        f"{i}. [{finding.get('severity')}] {finding.get('title', '')}: "
                        f"{finding.get('recommendation', '')}",
                        s["body"]
                    ))
        
        # Footer note
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(
            f"Report generated by CyberMind AI | Session {session_id} | "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ParagraphStyle("footer", fontName="Helvetica", fontSize=8,
                           textColor=HexColor("#666666"), alignment=TA_CENTER)
        ))
        
        # Build PDF
        doc.build(story)
        print(f"  [SUCCESS] Report saved: {filepath}")
        return str(filepath)
    
    def generate_siem_report(self, setup_plan, session_log):
        """Generate a SIEM setup documentation PDF."""
        if not REPORTLAB_AVAILABLE:
            return self._save_text_siem_report(setup_plan)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"siem_setup_guide_{timestamp}.pdf"
        filepath = REPORTS_DIR / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                                 rightMargin=2*cm, leftMargin=2*cm,
                                 topMargin=2*cm, bottomMargin=2*cm)
        story = []
        s = self.styles
        
        story.append(Paragraph("WAZUH SIEM SETUP GUIDE", s["title"]))
        story.append(Paragraph("Home Lab Security Monitoring Setup", s["subtitle"]))
        story.append(Spacer(1, 0.5*cm))
        
        story.append(Paragraph("OVERVIEW", s["heading1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        story.append(Paragraph(
            "This document covers the complete Wazuh SIEM installation and configuration "
            "for a home lab environment. Wazuh provides: real-time security monitoring, "
            "log analysis, vulnerability detection, file integrity monitoring, and compliance reporting.",
            s["body"]
        ))
        story.append(Spacer(1, 0.3*cm))
        
        story.append(Paragraph("SETUP STEPS", s["heading1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT))
        
        for i, step in enumerate(setup_plan, 1):
            story.append(Paragraph(f"Step {i}: {step.get('description', '')}", s["heading2"]))
            story.append(Paragraph(f"$ {step.get('command', '')}", s["code"]))
            if step.get("notes"):
                story.append(Paragraph(f"Note: {step['notes']}", s["body"]))
            if step.get("troubleshooting"):
                story.append(Paragraph(
                    f"Troubleshooting: {step['troubleshooting']}",
                    ParagraphStyle("ts", fontName="Helvetica-Oblique", fontSize=9,
                                   textColor=ORANGE_W, spaceAfter=6)
                ))
            story.append(Spacer(1, 0.2*cm))
        
        doc.build(story)
        return str(filepath)
    
    def _save_text_report(self, report_data, findings):
        """Fallback text report when reportlab is not available."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}.txt"
        filepath = REPORTS_DIR / filename
        
        with open(filepath, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("CYBERMIND AI - PENTEST REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Target: {report_data.get('target', 'Unknown')}\n")
            f.write(f"Date: {datetime.now()}\n")
            f.write(f"Findings: {len(findings)}\n\n")
            
            for i, f_item in enumerate(findings, 1):
                f.write(f"\n[{f_item.get('severity', 'INFO')}] Finding #{i}: {f_item.get('title', '')}\n")
                f.write(f"  {f_item.get('detail', '')}\n")
                f.write(f"  Fix: {f_item.get('recommendation', '')}\n")
        
        return str(filepath)
    
    def _save_text_siem_report(self, setup_plan):
        """Fallback text SIEM guide."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"siem_guide_{timestamp}.txt"
        filepath = REPORTS_DIR / filename
        
        with open(filepath, 'w') as f:
            f.write("WAZUH SIEM SETUP GUIDE\n\n")
            for i, step in enumerate(setup_plan, 1):
                f.write(f"Step {i}: {step.get('description', '')}\n")
                f.write(f"  Command: {step.get('command', '')}\n\n")
        
        return str(filepath)
