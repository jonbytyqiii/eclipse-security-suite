#!/usr/bin/env python3
import sqlite3
import os
from rich.console import Console
from rich.table import Table

console = Console()
DB_PATH = "storage/siem_alerts.db"

def triage_stored_alerts():
    if not os.path.exists(DB_PATH):
        console.print(f"[bold red][!] Target forensic database missing at {DB_PATH}[/bold red]")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, timestamp, rule_id, title, severity, source_ip FROM security_alerts ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        
        if not rows:
            console.print("[bold yellow][*] Alert journal matrix is empty. Monitor live telemetry to populate rows.[/bold yellow]")
            return

        table = Table(title="📡 LOGPULSE CACHED INCIDENT TRIAGE LOGS", border_style="cyan", expand=True)
        table.add_column("ID", justify="center", style="dim")
        table.add_column("Timestamp", style="white")
        table.add_column("Rule ID", style="magenta")
        table.add_column("Alert Title", style="yellow")
        table.add_column("Severity", justify="center")
        table.add_column("Source Address", style="green")

        for row in rows:
            sev = row[4].upper()
            sev_color = "[bold red]" if sev in ["CRITICAL", "HIGH"] else "[bold yellow]"
            table.add_row(
                str(row[0]),
                str(row[1]),
                str(row[2]),
                str(row[3]),
                f"{sev_color}{sev}[/]",
                str(row[5])
            )
        console.print(table)
    except sqlite3.OperationalError:
        console.print("[bold red][!] Database table schema initialization missing or corrupted.[/bold red]")
    finally:
        conn.close()

if __name__ == "__main__":
    triage_stored_alerts()