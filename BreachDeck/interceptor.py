#!/usr/bin/env python3
import os
import sys
import yaml
import time
import queue
import threading
import logging
from datetime import datetime
from typing import Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

from modules.sniffer import LivePacketAuditor

# Global Logging Configuration - Silences background chatter to preserve the TUI
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EclipseMain")

console = Console()

class AuthenticationInterceptor:
    def __init__(self) -> None:
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = self._load_configuration()
        
        self.is_running = False
        self.evt_queue: queue.Queue = queue.Queue()
        self.captured_tokens = []
        self.detected_flaws: Dict[str, Dict[str, str]] = {}
        self.lock = threading.Lock()
        
        self.stats = {"llmnr_spoofed": 0, "ntlm_intercepted": 0, "relay_targets": 0}
        self.critical_error = None
        
        log_cfg = self.config.get("logging_options", {})
        self.output_dir = os.path.join(self.base_dir, log_cfg.get("output_directory", "BreachDeck"))
        self.output_file = os.path.join(self.output_dir, log_cfg.get("log_filename", "captured_hashes.txt"))

    def _load_configuration(self) -> Dict[str, Any]:
        """Loads configuration from yaml or falls back to robust defaults."""
        config_path = os.path.join(self.base_dir, "config.yaml")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error(f"Failed to parse configuration file: {e}")
        return {"network_binding": {"promiscuous_mode": True, "default_loopback_port": 4445}}

    def check_privileges(self) -> bool:
        """Determines if the application has raw socket creation capabilities."""
        try:
            if os.name == 'nt':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            return os.getuid() == 0
        except Exception:
            return False

    def write_hash_to_disk(self, data: Dict[str, Any]) -> None:
        """Appends verified cryptographic data securely onto system storage paths."""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            with open(self.output_file, "a", encoding="utf-8") as f:
                f.write(f"[{data['time']}] Host: {data['ip']} | Account: {data['user']} | Type: {data['type']}\n")
                if "hashcat_format" in data:
                    f.write(f" Hashcat Format: {data['hashcat_format']}\n")
                f.write("-" * 80 + "\n")
        except IOError as e:
            logger.error(f"Failed writing token string to disk: {e}")

    def run_simulation_engine(self) -> None:
        """Feeds periodic background demo events to the queue if configuration specifies."""
        sim_config = self.config.get("simulation_modes", {})
        if not sim_config.get("enable_demo_simulation", False):
            return
            
        time.sleep(3)
        if self.is_running and not self.critical_error:
            self.evt_queue.put({
                "type": "LLMNR", 
                "ip": "192.168.1.144", 
                "payload": "WORKSPACE-PC-02"
            })
            
        time.sleep(3)
        if self.is_running and not self.critical_error:
            mock_hash = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "ip": "192.168.1.144",
                "user": "ECLIPSE-DOM\\jbytyqi",
                "type": "NetNTLMv2",
                "hash": "jbytyqi::ECLIPSE-DOM:1122334455667788:e3b0c44298fc...",
                "hashcat_format": "jbytyqi::ECLIPSE-DOM:1122334455667788:e3b0c44298fc1c149afbf4c8996fb924"
            }
            self.evt_queue.put({"type": "NTLM", "data": mock_hash})

    def process_incoming_queue(self) -> None:
        """Dispatches data objects read from packet capture and simulation pipelines."""
        while self.is_running:
            try:
                item = self.evt_queue.get(timeout=0.5)
                with self.lock:
                    if item["type"] == "ENV_ERROR":
                        self.critical_error = item["payload"]
                    elif item["type"] in ["LLMNR", "NBTNS"]:
                        self.stats["llmnr_spoofed"] += 1
                        self.detected_flaws[f"{item['type']} Broadcast Traced"] = {
                            "sev": "MEDIUM", 
                            "desc": f"Passive monitor spotted broadcast name lookup: '{item['payload']}'"
                        }
                    elif item["type"] == "NTLM":
                        self.stats["ntlm_intercepted"] += 1
                        self.stats["relay_targets"] += 1
                        self.detected_flaws["Insecure NTLMSSP Exchange"] = {
                            "sev": "HIGH", 
                            "desc": "Authentication signature framework observed over monitoring context."
                        }
                        self.captured_tokens.append(item["data"])
                        self.write_hash_to_disk(item["data"])
                self.evt_queue.task_done()
            except queue.Empty:
                continue

    def generate_live_dashboard(self) -> Table:
        """Constructs and draws the interactive rich user terminal matrix layout."""
        main_grid = Table.grid(padding=1, expand=True)
        split_table = Table.grid(expand=True)
        split_table.add_column(ratio=1)
        split_table.add_column(ratio=1)

        with self.lock:
            if self.critical_error:
                status_line = f"[bold red]CRITICAL ENVIRONMENT FAULT: {self.critical_error}[/bold red]"
            else:
                status_line = "[green]PASSIVE SNIFFER ACTIVE[/green]"
                if self.config.get("simulation_modes", {}).get("enable_demo_simulation", False):
                    status_line += " [cyan](DEMO SIMULATION MODULE EMBEDDED)[/cyan]"

            telemetry_text = (
                f"[bold yellow]Operational Engine State :[/bold yellow] {status_line}\n"
                f"[bold white]Broadcast Packets Audited :[/bold white] [cyan]{self.stats['llmnr_spoofed']}[/cyan]\n"
                f"[bold red]Intercepted NTLM Hashes   :[/bold red] [bold red]{self.stats['ntlm_intercepted']}[/bold red]\n"
                f"[bold magenta]Available Relay Inbounds  :[/bold magenta] [magenta]{self.stats['relay_targets']}[/magenta]"
            )
            telemetry_panel = Panel(telemetry_text, title="⚡ MONITOR TELEMETRY FEED", border_style="yellow")

            flaws_text = ""
            if self.critical_error:
                flaws_text = f"[bold red][!] Application terminated. Verify Npcap/libpcap system driver states manually.[/bold red]"
            elif not self.detected_flaws:
                flaws_text = "[green][+] Listening on network lines... Awaiting misconfiguration broadcast tags.[/green]"
            else:
                for title, data in list(self.detected_flaws.items())[-3:]:
                    color = "red" if data["sev"] == "HIGH" else "yellow"
                    flaws_text += f"[{color}][!] {data['sev']}[/{color}] [bold white]{title}[/bold white]\n└─ [dim]{data['desc']}[/dim]\n"

            flaws_panel = Panel(flaws_text.strip(), title="⚠️  SUBNET DISCOVERY HEURISTICS", border_style="red")
            
            split_table.add_row(telemetry_panel, flaws_panel)
            main_grid.add_row(split_table)

            token_table = Table(title="🔥 AUDITED LOCAL NETWORK LEDGER", expand=True)
            token_table.add_column("Timestamp", style="dim", width=12)
            token_table.add_column("Origin Address", style="cyan", width=16)
            token_table.add_column("Target Principal Identity", style="bold white", width=26)
            token_table.add_column("Format Type", style="magenta", width=14)
            token_table.add_column("Cryptographic Content Extraction (Hashcat Standard Output)", style="red")

            for t in self.captured_tokens[-8:]:
                token_table.add_row(t["time"], t["ip"], t["user"], t["type"], t["hash"])

        main_grid.add_row(token_table)
        return main_grid

    def start(self) -> None:
        """Powers on interface tracking streams and handles user engagement."""
        console.clear()
        console.print(Panel("""[bold yellow]
  ██████▄   ████████▄   ████████  ████████  ████████  ██    ██
  ██    ██  ██     ██  ██    ██  ██        ██    ██  ██▄  ▄██
  ██    ██  ████████▀  ████████  ██        ██    ██  ███▄████
  ██    ██  ██   ██    ██    ██  ██        ██    ██  ██ ▀█ ██
  ██████▀   ██    ██   ██    ██  ████████  ████████  ██    ██[/bold yellow]
\n[bold white]        >> PROJECT ECLIPSE: DRAGON PASSIVE INTERCEPTOR v3.1 <<[/bold white]
[dim]     Production Diagnostic Profile: Secure Protocol Auditing Infrastructure[/dim]""", border_style="yellow", expand=False))
        
        if not self.check_privileges():
            console.print(f"\n[bold red][!] SYSTEM WARNING: Administrative/Root privileges are required to attach packet hooks to raw sockets.[/bold red]\n")

        selected_interface = input(f"Target Interface ID (Press Enter for Auto-Selection Core Matrix): ").strip() or None
        
        if not selected_interface and os.name == 'nt' and 'scapy' in sys.modules:
            try:
                from scapy.all import conf
                for iface in conf.ifaces.values():
                    if "loopback" in iface.name.lower() or "npcap" in iface.description.lower():
                        selected_interface = iface.name
                        console.print(f"[cyan][*] Auto-selected core interface mapping adapter: {iface.description}[/cyan]")
                        break
            except Exception:
                pass

        bind_port = self.config.get("network_binding", {}).get("default_loopback_port", 4445)
        auditor = LivePacketAuditor(interface=selected_interface, callback_queue=self.evt_queue, loopback_port=bind_port)
        self.is_running = True

        # Assign asynchronous worker loops securely
        threading.Thread(target=auditor.start_loop, daemon=True).start()
        threading.Thread(target=self.process_incoming_queue, daemon=True).start()
        threading.Thread(target=self.run_simulation_engine, daemon=True).start()

        console.print(f"[green][+] Building live dashboard display structures cleanly...[/green]\n")
        time.sleep(1)

        try:
            with Live(self.generate_live_dashboard(), refresh_per_second=2) as live:
                while self.is_running and not self.critical_error:
                    time.sleep(0.5)
                    live.update(self.generate_live_dashboard())
                if self.critical_error:
                    live.update(self.generate_live_dashboard())
        except KeyboardInterrupt:
            console.print(f"\n[yellow][*] Execution runtime halted safely via terminal interrupt signals.[/yellow]")
        finally:
            self.is_running = False
            auditor.running = False
            
        console.print(f"\n[bold green][+] Audit complete. Persistent output saved to: '{self.output_file}'.[/bold green]\n")

if __name__ == "__main__":
    engine = AuthenticationInterceptor()
    engine.start()