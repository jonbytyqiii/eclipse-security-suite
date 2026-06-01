#!/usr/bin/env python3
import os
import sys
import yaml
import asyncio
from datetime import datetime

# Enforce absolute package space dot-notation
from logpulse.core.normalizer import LogEvent
from logpulse.core.detector import DynamicCorrelationEngine
from logpulse.core.orchestrator import SIEMPipelineOrchestrator
from logpulse.forensic.auditor import DecoupledForensicAuditor

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live

console = Console()

# ====================================================================
# LOGPULSE CENTRAL OPERATIONAL INTERFACE BRIDGE
# ====================================================================
class LogPulseApp:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Traverse straight up to your main root project directory
        # base_dir is src/logpulse, so ../../ config.yaml points to LogPulse/config.yaml
        config_path = os.path.normpath(os.path.join(base_dir, "../../config.yaml"))
        
        if not os.path.exists(config_path):
            console.print(f"[bold red][!] Configuration tracker missing at target path: {config_path}[/bold red]")
            sys.exit(1)
            
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
            
        self.auditor = DecoupledForensicAuditor()
        self.reset_counters()

    def reset_counters(self):
        self.active_alerts = []
        self.dedup_cache = {}  
        self.stats = {"processed": 0, "alerts": 0, "critical": 0}

    def append_alert_ui_callback(self, rule, event, mitre_str):
        self.stats["alerts"] += 1
        if rule.get("severity") == "CRITICAL":
            self.stats["critical"] += 1

        dedup_key = f"{rule['rule_id']}_{event.source_ip}"
        curr_time_str = event.timestamp.split(" ")[1] if " " in event.timestamp else event.timestamp

        if dedup_key in self.dedup_cache:
            idx = self.dedup_cache[dedup_key]
            self.active_alerts[idx]["hits"] += 1
            self.active_alerts[idx]["time"] = curr_time_str
        else:
            self.active_alerts.append({
                "time": curr_time_str,
                "title": rule["title"],
                "severity": rule["severity"],
                "mitre": mitre_str,
                "ip": event.source_ip,
                "hits": 1
            })
            self.dedup_cache[dedup_key] = len(self.active_alerts) - 1

    def generate_dashboard_view(self) -> Layout:
        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="body", ratio=1))
        layout["body"].split_row(Layout(name="left", ratio=1), Layout(name="right", ratio=2))
        
        layout["header"].update(Panel(
            f"[bold cyan]LOGPULSE THREAT HUNTING CENTRAL MONITOR v10.0[/bold cyan] | Ingestion Cluster: [green]ONLINE[/green] | Mode: Production-Grade Academy Lab",
            border_style="bright_black"
        ))
        
        stats_table = Table.grid(padding=1)
        stats_table.add_row("[white]Total Logs LogPulse Captured:[/white]", f"[bold white]{self.stats['processed']}[/bold white]")
        stats_table.add_row("[red]Active Threat Rules Triggered:[/red]", f"[bold red]{self.stats['alerts']}[/bold red]")
        stats_table.add_row("[magenta]Escalated Critical Anomalies:[/magenta]", f"[bold magenta]{self.stats['critical']}[/bold magenta]")
        layout["left"].update(Panel(stats_table, title="📊 TELEMETRY RECON STATS", border_style="cyan"))

        alerts_table = Table(box=None, expand=True)
        alerts_table.add_column("Timestamp", style="dim", width=10)
        alerts_table.add_column("Rule Context Vector", style="white")
        alerts_table.add_column("Severity", justify="center", width=12)
        alerts_table.add_column("MITRE ATT&CK Mapping", style="yellow")
        alerts_table.add_column("Attribution IP", style="cyan")
        alerts_table.add_column("Hits", style="green", justify="center")

        for a in self.active_alerts[-8:]:
            sev = a["severity"].upper()
            if sev == "CRITICAL":
                color_tag = "[bold blink red]"
                end_tag = "[/bold blink red]"
            elif sev == "HIGH":
                color_tag = "[bold red]"
                end_tag = "[/bold red]"
            elif sev == "MEDIUM":
                color_tag = "[bold orange3]"
                end_tag = "[/bold orange3]"
            else:
                color_tag = "[bold yellow]"
                end_tag = "[/bold yellow]"

            alerts_table.add_row(
                a["time"], 
                a["title"], 
                f"{color_tag}{sev}{end_tag}", 
                a["mitre"], 
                a["ip"], 
                str(a["hits"])
            )

        layout["right"].update(Panel(alerts_table, title="🔔 LIVE ADVANCED TELEMETRY TRIAGE STREAM", border_style="magenta"))
        return layout

    def render_menu(self):
        table = Table(show_header=False, box=None, expand=True)
        table.add_column(style="bold cyan", width=6)
        table.add_column(style="white")
        table.add_row("[01]", "DEPLOY ASYNC MULTI-STREAM SIEM MONITOR (Real File Tailing System)")
        table.add_row("[02]", "RUN HOST SECURITY HISTORY AUDIT (Logon / Logoff Events)")
        table.add_row("[03]", "RUN ACTIVE HOST PROCESS SYSTEM RECON MAP (Task Explorer)")
        table.add_row("[04]", "AUDIT LOCAL OS PROFILES REGISTRY (User Base Audit)")
        table.add_row("[05]", "RUN ACTIVE HOST SCHEDULED TASK RECON MAP (Cron/Persistence)")
        table.add_row("[H]", "VIEW LOGPULSE SUB-SYSTEM HELP & CLI DOCUMENTATION")
        table.add_row("[Q]", "RETURN TO CENTRAL CONTROL HUB TERMINAL BOUNDS")
        return Panel(table, title="[bold white]LOGPULSE THREAT INTERFACE OPERATION BRIDGE[/bold white]", border_style="cyan")

    def run(self):
        while True:
            console.print(f"\n[bold blue] >> LOGPULSE ASSIGNMENT MANAGEMENT INTERFACE BRIDGE << [/bold blue]")
            console.print(self.render_menu())
            choice = input("\n[LOGPULSE@INPUT]> ").strip().lower()
            
            if choice in ["01", "1"]:
                console.print("\n[magenta][*] Mounting async file watching hooks... Processing active pipeline logs...[/magenta]\n")
                orchestrator = SIEMPipelineOrchestrator(self.config, self.append_alert_ui_callback)
                self.reset_counters()
                
                try:
                    async def sim_attacker_activity():
                        await asyncio.sleep(0.5)
                        log_dir = os.path.normpath("logs")
                        log_file = os.path.join(log_dir, "auth_sim.log")
                        os.makedirs(log_dir, exist_ok=True)
                        
                        with open(log_file, "a", encoding="utf-8") as f:
                            for _ in range(5):
                                self.stats["processed"] += 1
                                f.write("sshd[1042]: auth_failure password for invalid user admin from 192.168.1.50 port 22 ssh2\n")
                                f.flush()
                                await asyncio.sleep(0.1)
                                
                        await asyncio.sleep(0.5)
                        with open(log_file, "a", encoding="utf-8") as f:
                            self.stats["processed"] += 1
                            f.write("nginx_access: 192.168.1.75 - - [GET] /index.php?file=../../../../etc/passwd HTTP/1.1 403\n")
                            f.flush()

                    async def run_dashboard_and_pipeline():
                        with Live(self.generate_dashboard_view(), refresh_per_second=4, screen=False) as live:
                            task = asyncio.create_task(orchestrator.boot_monitor_cluster())
                            await sim_attacker_activity()
                            
                            for _ in range(25):
                                await asyncio.sleep(0.1)
                                live.update(self.generate_dashboard_view())
                            
                            # Updated to align with orchestrator's real shutdown function
                            orchestrator.shutdown_orchestrator()

                    async def main_pipeline_execution():
                        await run_dashboard_and_pipeline()

                    asyncio.run(main_pipeline_execution())
                    
                except KeyboardInterrupt:
                    # Updated to align with orchestrator's real shutdown function
                    orchestrator.shutdown_orchestrator()
                    console.print("\n[bold yellow][*] Core SIEM event tracking pipeline safely unmounted.[/bold yellow]")
                except Exception as e:
                    console.print(f"[bold red][!] Ingestion failure: {e}[/bold red]")
                input("\nPress Enter to return to menu...")
                
            elif choice in ["02", "2"]:
                console.print(f"\n[bold red][!] Interrogating host security event databases...[/bold red]\n")
                self.auditor.harvest_security_metrics(10)
                input("\nPress Enter to return...")
                
            elif choice in ["03", "3"]:
                console.print(f"\n[bold yellow][*] Running Active Host Process System Recon Map...[/bold yellow]\n")
                self.auditor.map_active_tasks()
                input("\nPress Enter to return...")
                
            elif choice in ["04", "4"]:
                console.print(f"\n[bold green][*] Auditing local OS profiles registry...[/bold green]\n")
                self.auditor.print_local_users()
                input("\nPress Enter to return...")
                
            elif choice in ["05", "5"]:
                console.print(f"\n[bold cyan][*] Mapping active logical scheduler tasks...[/bold cyan]\n")
                self.auditor.map_scheduled_tasks()
                input("\nPress Enter to return...")
                
            elif choice == "h":
                console.print("\n[bold cyan]📖 LOGPULSE OPERATIONS MANUAL & COMPONENT DOCUMENTATION[/bold cyan]")
                
                help_table = Table(box=None, expand=True)
                help_table.add_column("Command", style="bold yellow", width=14)
                help_table.add_column("Functional Sub-system Description", style="white")
                
                help_table.add_row("[01] SIEM", "Launches asynchronous log ingestion handlers using non-blocking streams. Monitored paths are evaluated against dynamic regex matrices to capture operational threat signatures.")
                help_table.add_row("[02] Audit", "Interrogates underlying infrastructure authentication databases. Collects historical security session signatures (Logon/Logoff patterns).")
                help_table.add_row("[03] Tasks", "Maps current processing trees to find hidden processes, background binaries, or potential masqueraded threads on the host framework.")
                help_table.add_row("[04] Profiles", "Audits local security system components and structural user profiles registries to inventory unauthorized modifications to accounts.")
                help_table.add_row("[05] Cron", "Scans logical workspace scheduling engines (schtasks/crontab environment) to reveal persistence anomalies set up by adversarial threat actors.")
                
                console.print(Panel(help_table, title="[bold white]ENGINE MODULE MATRIX OVERVIEW[/bold white]", border_style="bright_black"))
                input("[dim]Press Enter to unmount reference manual frames and return to context bounds...[/dim]")

            elif choice == "q":
                console.print("[bold green][*] Terminating interface session bounds. Goodbye.[/bold green]")
                break
                
            else:
                console.print(f"\n[bold red][!] Operator Signature Error: '{choice}' is not a registered pipeline sub-command.[/bold red]")
                console.print("[yellow][*] Hint: Input [H] to view module descriptions or [Q] to close interface bounds safely.[/yellow]\n")
                asyncio.run(asyncio.sleep(1.5))

# ====================================================================
# GLOBAL CONSOLE ENTRY POINT
# ====================================================================
def main():
    """Global system entry point called by the logpulse console wrapper"""
    app = LogPulseApp()
    app.run()

if __name__ == "__main__":
    main()