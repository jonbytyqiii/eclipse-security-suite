#!/usr/bin/env python3
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
import asyncio

from docksentry.core.engine import ContainerAuditEngine
from docksentry.reports.manager import AuditReportingManager

app = FastAPI(title="DockSentry Enterprise Web Gateway UI Portal Engine")
engine = ContainerAuditEngine()
global_state = {"status": "Awaiting commands...", "findings": [], "metrics": {"compliance_score": 100, "total_flaws": 0}}

async def background_audit_runner():
    global_state["status"] = "Active asynchronous matrix verification running..."
    targets = {"containers": ["all"], "dockerfiles": [], "k8s": [], "images": []}
    findings = await engine.execute_comprehensive_audit(targets)
    global_state["findings"] = findings
    global_state["metrics"] = engine.calculate_metrics(findings)
    global_state["status"] = "Assessment verification loops completed successfully."
    AuditReportingManager.write_reports(findings, global_state["metrics"])

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard_root_portal():
    # Built-in lightweight operational template UI layout context delivery
    color = "emerald" if global_state["metrics"]["compliance_score"] >= 80 else "amber" if global_state["metrics"]["compliance_score"] >= 50 else "rose"
    
    html = f"""
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <title>DockSentry Security Operations Dashboard</title>
    </head>
    <body class="bg-slate-950 text-slate-100 p-12 font-sans">
        <div class="max-w-6xl mx-auto">
            <div class="flex justify-between items-center border-b border-slate-800 pb-6 mb-8">
                <div>
                    <h1 class="text-4xl font-extrabold text-indigo-400 tracking-tight">DockSentry CSPM</h1>
                    <p class="text-slate-400 mt-1">Continuous Cloud-Native Posture Management Infrastructure Console</p>
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-lg p-4 text-center">
                    <span class="text-xs text-slate-500 uppercase block font-semibold tracking-wider">Compliance Status Score</span>
                    <span class="text-4xl font-black text-{color}-400">{global_state["metrics"]["compliance_score"]}%</span>
                </div>
            </div>
            
            <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-8">
                <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">Engine Activity Monitor Pipeline</h3>
                <div class="text-indigo-300 font-mono text-lg animate-pulse">⚡ {global_state["status"]}</div>
            </div>

            <h2 class="text-2xl font-bold mb-4 tracking-tight">Discovered Threat Intelligence Logs Matrix</h2>
            <div class="space-y-4">
    """
    if not global_state["findings"]:
        html += '<p class="text-emerald-400 font-mono bg-emerald-950/30 border border-emerald-900/50 p-4 rounded-lg">✔ System state configuration clear. No validation errors flagged.</p>'
    for f in global_state["findings"]:
        html += f"""
        <div class="bg-slate-900 border-l-4 border-rose-500 p-5 rounded-r-lg shadow-xl">
            <div class="flex justify-between items-start">
                <h4 class="text-lg font-bold text-slate-200">{f['name']}</h4>
                <span class="bg-slate-800 px-3 py-1 rounded text-xs font-mono text-indigo-400">{f.get('id','')}</span>
            </div>
            <p class="text-sm text-slate-400 mt-2">Target Interface Path: <code class="text-cyan-400 font-mono text-xs">{f['target']}</code></p>
            <p class="text-slate-300 mt-2 text-sm">{f['desc']}</p>
        </div>
        """
    html += "</div></div></body></html>"
    return html

@app.post("/api/v2/trigger-scan")
async def trigger_dashboard_scan_task(background_tasks: BackgroundTasks):
    background_tasks.add_task(background_audit_runner)
    return {"status": "Asynchronous validation engine processing queued successfully."}