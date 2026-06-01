#!/usr/bin/env python3
import socket
import sys
import json
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class ApexListener:
    def __init__(self, port=9095):
        self.port = port
        self.sys_info = {}
        self.findings = []
        self.status = "Initializing Ingestion Port..."

    def generate_dashboard(self) -> Table:
        grid = Table.grid(padding=1, expand=True)

        # 1. Top Headers Matrix Split
        sys_summary = (
            f"[bold cyan]Remote Host Node :[/bold cyan] [white]{self.sys_info.get('user', 'ENUMERATING...')}@{self.sys_info.get('hostname', 'UNKNOWN')}[/white]\n"
            f"[bold cyan]Kernel Build Layer:[/bold cyan] [yellow]{self.sys_info.get('kernel', 'WAITING FOR DATA...')}[/yellow]\n"
            f"[bold cyan]OS Platform Context:[/bold cyan] [magenta]{self.sys_info.get('os_name', 'WAITING...')}[/magenta]"
        )
        
        status_text = f"[bold green]● INGESTION CHANNEL PORT {self.port} ACTIVE[/bold green]\n\n[magenta]Current Action Path:\n→ {self.status}[/magenta]"
        
        top_split = Table.grid(expand=True, padding=1)
        top_split.add_column(ratio=2)
        top_split.add_column(ratio=1)
        top_split.add_row(
            Panel(sys_summary, title="🖥️ TARGET HOST IDENTIFICATION VECTOR", border_style="cyan"),
            Panel(status_text, title="⚙️ ENGINE CONTROL DECK", border_style="magenta")
        )
        grid.add_row(top_split)

        # 2. Central Structural Exposures Ledger Grid
        ledger = Table(box=box.SQUARE, show_header=True, header_style="bold cyan", border_style="bright_black", expand=True)
        ledger.add_column("Vector Category", width=18, justify="center")
        ledger.add_column("Risk Flag Severity", width=14, justify="center")
        ledger.add_column("Identified Exposure Configuration Point", style="bold white")

        if not self.findings:
            ledger.add_row("[dim]SCANNING[/dim]", "[dim]WAITING[/dim]", "[dim]Awaiting remote transmission matrix stream arrays...[/dim]")
        else:
            for f in self.findings:
                sev = f["severity"]
                if sev == "CRITICAL":
                    sev_disp = "[bold red]CRITICAL[/bold red]"
                elif sev == "HIGH":
                    sev_disp = "[bold orange3]HIGH[/bold orange3]"
                elif sev == "MEDIUM":
                    sev_disp = "[bold yellow]MEDIUM[/bold yellow]"
                else:
                    sev_disp = "[bold blue]LOW[/bold blue]"
                
                cat = f["category"]
                if cat == "SUID":
                    cat_disp = "[bold magenta]SUID BINARY[/bold magenta]"
                elif cat == "CAPABILITY":
                    cat_disp = "[bold cyan]CAPABILITY[/bold cyan]"
                elif cat == "SUDO":
                    cat_disp = "[bold red]SUDO RULE[/bold red]"
                else:
                    cat_disp = "[bold yellow]WRITABLE[/bold yellow]"

                ledger.add_row(cat_disp, sev_disp, f["item"])

        grid.add_row(Panel(ledger, title="⚡ REAL-TIME SYSTEM PRIVILEGE POSTURE AUDITING LEDGER", border_style="green"))
        return grid

    def start(self):
        # Print a high-end initialization splash screen before binding socket layers
        console.clear()
        console.print(r"""[bold red]
    ___     ____    ______   _  __
   /   |   / __ \  / ____/  | |/ /
  / /| |  / /_/ / / __/     |   / 
 / ___ | / ____/ / /___    /   |  
/_/  |_|/_/     /_____/   /_/|_|  
  >> KERNEL & PERMISSION MATRIX DECK <<[/bold red]
        """)
        console.print(f"[bold green][+] APEX Multi-Threaded Ingestion Socket Open on Port {self.port}[/bold green]")
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server_socket.bind(("0.0.0.0", self.port))
            server_socket.listen(1)
            
            with Progress(SpinnerColumn("dots12"), TextColumn("[bold yellow]{task.description}"), transient=True) as progress:
                progress.add_task(description="Awaiting incoming target deployment beacon network handshakes...")
                conn, addr = server_socket.accept()
            
            self.status = f"Connection mapped from client node: {addr[0]}. Initializing stream unpacking loops..."
            
            with Live(self.generate_dashboard(), refresh_per_second=4) as live:
                buffer = ""
                while True:
                    data = conn.recv(4096)
                    if not data:
                        break
                    
                    buffer += data.decode('utf-8', errors='ignore')
                    
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        if not line.strip():
                            continue
                        
                        try:
                            payload = json.loads(line)
                            p_type = payload.get("type")
                            
                            if p_type == "SYS_INFO":
                                self.sys_info = payload["data"]
                            elif p_type == "STATUS":
                                self.status = payload["data"]
                            elif p_type == "FINDING":
                                self.findings.append(payload["data"])
                                live.update(self.generate_dashboard())
                        except Exception:
                            pass
                
                self.status = "Data capture complete. Connection terminated cleanly."
                live.update(self.generate_dashboard())

        except Exception as e:
            console.print(f"\n[bold red][!] Interception stack crashed: {e}[/bold red]")
        finally:
            server_socket.close()
            input(f"\n[MENU RETURN] Press Enter to drop back into ECLIPSE Control Tower...")