#!/usr/bin/env python3
import os
import json
from datetime import datetime
from typing import List, Dict, Any

from docksentry.reports.pdf_gen import DocumentReportGenerator

class AuditReportingManager:
    """
    Manages structural data exports across JSON, HTML, Markdown, and custom PDF formats.
    """
    @staticmethod
    def write_reports(findings: List[Dict[str, Any]], metrics: Dict[str, Any], output_dir: str = ".") -> Dict[str, str]:
        try:
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            paths = {
                "json": os.path.join(output_dir, f"audit_report_{timestamp}.json"),
                "html": os.path.join(output_dir, f"audit_report_{timestamp}.html"),
                "md": os.path.join(output_dir, f"audit_report_{timestamp}.md"),
                "pdf": os.path.join(output_dir, f"audit_report_{timestamp}.pdf")
            }

            payload = {"timestamp": datetime.now().isoformat(), "metrics": metrics, "findings": findings}
            with open(paths["json"], "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=4)

            html_content = AuditReportingManager._build_html(findings, metrics)
            with open(paths["html"], "w", encoding="utf-8") as f:
                f.write(html_content)

            md_content = AuditReportingManager._build_markdown(findings, metrics)
            with open(paths["md"], "w", encoding="utf-8") as f:
                f.write(md_content)

            # Flag to track if PDF successfully compiled
            pdf_success = True
            try:
                DocumentReportGenerator.compile_pdf_file(findings, metrics, paths["pdf"])
            except Exception as pdf_err:
                pdf_success = False
                print(f"[!] PDF Generation skipped: {pdf_err}")

            print(f"\n[+] Successfully wrote compliance reports to: {os.path.abspath(output_dir)}")
            print(f"    ├── JSON Ledger: {os.path.basename(paths['json'])}")
            print(f"    ├── HTML Dashboard: {os.path.basename(paths['html'])}")
            if pdf_success:
                print(f"    └── PDF Executive: {os.path.basename(paths['pdf'])}")
            return paths

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Failed to write audit reports to disk: {e}")
            import traceback
            traceback.print_exc()
            return {}

    @staticmethod
    def _build_html(findings: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>DockSentry Compliance Matrix Executive Report</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; color: #f3f4f6; padding: 40px; margin: 0; }}
                header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 30px; }}
                h1 {{ color: #10b981; margin: 0; font-size: 2.5rem; letter-spacing: -0.05em; }}
                .score-radial {{ background: #1e293b; border-radius: 12px; padding: 24px; display: inline-block; margin-bottom: 30px; border: 1px solid #334155; }}
                .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 40px; }}
                .stat-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; text-align: center; }}
                .finding {{ background: #111827; border: 1px solid #374151; border-left: 6px solid #ef4444; border-radius: 4px; padding: 24px; margin-bottom: 20px; }}
                .remediation {{ background: #1f2937; border-left: 4px solid #eab308; padding: 15px; margin-top: 15px; font-family: monospace; color: #fde047; }}
            </style>
        </head>
        <body>
            <header>
                <h1>ECLIPSE SECURITY POSTURE AUDIT LEDGER</h1>
                <p>System Engine Metrics Validation Pipeline Logs</p>
            </header>
            <div class="score-radial">
                <div>Compliance Rating Score</div>
                <div class="score-val">{metrics.get('compliance_score', 0)}%</div>
            </div>
            <div class="grid">
                <div class="stat-card"><h3>Total Exposures</h3><h2>{metrics.get('total_flaws', 0)}</h2></div>
                <div class="stat-card" style="color:#ec4899;"><h3>Critical</h3><h2>{metrics.get('critical', 0)}</h2></div>
                <div class="stat-card" style="color:#ef4444;"><h3>High Risk</h3><h2>{metrics.get('high', 0)}</h2></div>
                <div class="stat-card" style="color:#f59e0b;"><h3>Medium</h3><h2>{metrics.get('medium', 0)}</h2></div>
            </div>
            <h2>Discovered Vulnerability Logs</h2>
        """
        for f in findings:
            html += f"""
            <div class="finding {f.get('severity', 'LOW')}">
                <span style="float:right; background:#374151; padding:4px 12px; border-radius:12px; font-size:0.85rem;">{f.get('mapping','N/A')}</span>
                <h3>[{f.get('severity', 'LOW')}] {f.get('name', 'Unknown Rule')}</h3>
                <p><strong>Target Context Node:</strong> {f.get('target', 'unknown')}</p>
                <p>{f.get('desc', 'No description available.')}</p>
                <div class="remediation"><strong>Hardening Execution Patch:</strong><br>{f.get('remediation', 'N/A')}</div>
            </div>
            """
        html += "</body></html>"
        return html

    @staticmethod
    def _build_markdown(findings: List[Dict[str, Any]], metrics: Dict[str, Any]) -> str:
        md = "# DockSentry Governance Compliance Matrix Audit Report\n\n"
        for f in findings:
            md += f"### [{f.get('severity', 'LOW')}] {f.get('name', 'Unknown Rule')}\n"
            md += f"* **Target Node:** {f.get('target', 'unknown')}\n"
            md += f"* **Remediation:** {f.get('remediation', 'N/A')}\n\n"
        return md
