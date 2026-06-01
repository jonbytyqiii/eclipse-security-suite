#!/usr/bin/env python3
import platform
import subprocess
import json
import sys
from rich.console import Console
from rich.table import Table

console = Console()

class DecoupledForensicAuditor:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"

    def harvest_security_metrics(self, count=10):
        table = Table(title="🛡️ HOST SYSTEM AUTHENTICATION METRICS AUDIT", border_style="red", expand=True)
        if self.is_windows:
            table.add_column("Time Created", style="dim")
            table.add_column("Event ID", justify="center", style="cyan")
            table.add_column("Summary context description", style="white")
            
            script = f'Get-WinEvent -LogName Security -MaxEvents {count} -ErrorAction SilentlyContinue | Select-Object TimeCreated, Id, Message | ConvertTo-Json'
            try:
                proc = subprocess.run(["powershell", "-Command", script], capture_output=True, text=True, timeout=5)
                if proc.stdout.strip() and proc.stdout.strip() != "[]":
                    events = json.loads(proc.stdout.strip())
                    if isinstance(events, dict): 
                        events = [events]
                    for ev in events:
                        table.add_row(
                            str(ev.get("TimeCreated", "")), 
                            str(ev.get("Id", "")), 
                            str(ev.get("Message", "")).split("\n")[0][:80]
                        )
                    console.print(table)
                    return
            except subprocess.TimeoutExpired:
                print("[!] PowerShell events query timed out.", file=sys.stderr)
            except json.JSONDecodeError:
                print("[!] Failed to decode incoming Event Log JSON telemetry.", file=sys.stderr)
            except subprocess.SubprocessError as e:
                print(f"[!] Subprocess execution fault: {e}", file=sys.stderr)
        console.print("[yellow][!] System trail metrics empty or administrative privileges are restricted.[/yellow]")

    def map_active_tasks(self):
        table = Table(title="📊 SYSTEM TASK INSTANCE MAPPING", border_style="cyan", expand=True)
        table.add_column("System Process Mapping Output", style="white")
        
        cmd = ["tasklist", "/FI", "STATUS eq RUNNING"] if self.is_windows else ["ps", "aux"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            for line in proc.stdout.split("\n")[:20]:
                table.add_row(line)
            console.print(table)
        except subprocess.SubprocessError as e:
            print(f"[!] Target process map extraction failed: {e}", file=sys.stderr)

    def print_local_users(self):
        """Option 04: Audits local OS user baseline registry profiles"""
        table = Table(title="👥 LOCAL OPERATING SYSTEM USER AUDIT", border_style="green", expand=True)
        table.add_column("Identified Local Host Accounts", style="white")
        
        cmd = ["net", "user"] if self.is_windows else ["cut", "-d:", "-f1", "/etc/passwd"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            lines = proc.stdout.split("\n")
            display_lines = lines if not self.is_windows else [l for l in lines if l and not l.startswith("User accounts") and not l.startswith("----")]
            for line in display_lines[:15]:
                if line.strip():
                    table.add_row(line.strip())
            console.print(table)
        except subprocess.SubprocessError as e:
            print(f"[!] User accounts baseline query dropped: {e}", file=sys.stderr)

    def map_scheduled_tasks(self):
        """Option 05: Runs recon on cron/persistence mechanisms"""
        table = Table(title="⏰ HOST SCHEDULED TASK & PERSISTENCE RECON MAP", border_style="magenta", expand=True)
        table.add_column("Persistence / Scheduled Trigger Profile", style="white")
        
        cmd = ["schtasks", "/query", "/fo", "TABLE"] if self.is_windows else ["crontab", "-l"]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if proc.stdout.strip():
                for line in proc.stdout.split("\n")[:15]:
                    table.add_row(line)
            else:
                table.add_row("No explicit scheduled persistence configurations returned.")
            console.print(table)
        except subprocess.SubprocessError as e:
            print(f"[!] Scheduled baseline investigation failed: {e}", file=sys.stderr)