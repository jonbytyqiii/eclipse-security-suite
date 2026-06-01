#!/usr/bin/env python3
import time
from datetime import datetime
from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

console = Console()

class TerminalUserInterface:
    def __init__(self, score=100, total_scanned=0, critical=0, warnings=0, findings=None):
        self.score = score
        self.total_scanned = total_scanned
        self.critical_count = critical
        self.warnings_count = warnings
        self.findings = findings if findings is not None else []

    def update_telemetry(self, score, total_scanned, critical, warnings, findings):
        """Dynamically updates the internal dataset during active asynchronous scanner passes."""
        self.score = score
        self.total_scanned = total_scanned
        self.critical_count = critical
        self.warnings_count = warnings
        self.findings = findings

    def create_header_panel(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        grid.add_row(
            "[bold cyan]DOCKSENTRY // ADVANCED REAL-TIME COMPLIANCE MONITOR v2.5[/bold cyan]",
            f"[bold magenta]MATRIX TIME: {timestamp}[/bold magenta]"
        )
        return Panel(grid, style="bright_black")

    def create_score_panel(self) -> Panel:
        if self.score >= 80:
            score_color = "green"
            status_text = "POSTURE SECURE"
        elif self.score >= 50:
            score_color = "yellow"
            status_text = "WARNING: EXPOSURES IDENTIFIED"
        else:
            score_color = "red"
            status_text = "CRITICAL POSTURE BREACH"

        grid = Table.grid(expand=True)
        grid.add_row("[bold white]SECURITY POSTURE METRIC:[/bold white]")
        grid.add_row(f"[bold {score_color}]   {self.score} / 100[/bold {score_color}]")
        grid.add_row(f"[dim]Status: {status_text}[/dim]")
        return Panel(grid, title="[bold white]POSTURE SCORE[/bold white]", border_style=score_color)

    def create_statistics_panel(self) -> Panel:
        table = Table.grid(padding=(0, 1))
        table.add_row("[cyan]• ACTIVE CONTAINERS EVALUATED :[/cyan]", f"[bold white]{self.total_scanned}[/bold white]")
        table.add_row("[red]• CRITICAL POLICY EXPOSURES :[/red]", f"[bold red]{self.critical_count}[/bold red]")
        table.add_row("[yellow]• COMPLIANCE RISK WARNINGS   :[/yellow]", f"[bold yellow]{self.warnings_count}[/bold yellow]")
        table.add_row("[green]• THREAT INTEL HARMONIZATION :[/green]", "[bold green]LIVE CONNECTED[/bold green]")
        return Panel(table, title="[bold white]TELEMETRY ENGINE STATS[/bold white]", border_style="bright_black")

    def create_findings_panel(self) -> Panel:
        table = Table(box=box.MINIMAL_DOUBLE_HEAD, show_header=True, header_style="bold cyan", expand=True)
        table.add_column("TARGET VECTOR", style="bold white", ratio=2)
        table.add_column("SEVERITY", justify="center", ratio=1)
        table.add_column("VULNERABILITY DESCRIPTION / COMPLIANCE VIOLATION", ratio=5)
        table.add_column("REMEDIATION RULE", style="dim", ratio=3)

        if not self.findings:
            table.add_row("PENDING", "[bold yellow]SCANNING...[/bold yellow]", "Awaiting tactical engine analytical passes...", "Calculating layout...")
        else:
            for item in self.findings:
                sev = str(item.get("severity", "LOW")).upper()
                if "CRIT" in sev or "HIGH" in sev:
                    sev_display = f"[bold red]{sev}[/bold red]"
                elif "WARN" in sev or "MED" in sev:
                    sev_display = f"[bold yellow]{sev}[/bold yellow]"
                else:
                    sev_display = f"[bold blue]{sev}[/bold blue]"
                
                table.add_row(
                    item.get("container", "Global Core"),
                    sev_display,
                    item.get("description", "Analyzing configuration signature..."),
                    item.get("remediation", "Pending verification rule.")
                )
        return Panel(table, title="[bold white]ISOLATED RISK VECTORS & SECURITY ANOMALIES[/bold white]", border_style="cyan")

    def create_footer_panel(self) -> Panel:
        return Panel(
            "[bold white][ENTER][/bold white] Exit live dashboard mode and drop down to remediation menu strategies.",
            border_style="bright_black"
        )

    def generate_current_layout(self) -> Layout:
        """Assembles and returns a unified nested grid template layout block."""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=3)
        )
        layout["body"].split_row(
            Layout(name="metrics_pane", ratio=1),
            Layout(name="data_pane", ratio=3)
        )
        layout["metrics_pane"].split(
            Layout(name="score_box", ratio=1),
            Layout(name="stats_box", ratio=1)
        )
        
        layout["header"].update(self.create_header_panel())
        layout["score_box"].update(self.create_score_panel())
        layout["stats_box"].update(self.create_statistics_panel())
        layout["data_pane"].update(self.create_findings_panel())
        layout["footer"].update(self.create_footer_panel())
        return layout