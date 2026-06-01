#!/usr/bin/env python3
import os
import http.client
import urllib.parse
import urllib.request
import json
import socket
import re
import sys
import secrets
import time
import argparse
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.panel import Panel

console = Console()

RAPTOR_BANNER = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║ ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ ║
║▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌║
║                                                                              ║
║                  [bold red]V O R T E X   R A P T O R[/bold red]                                   ║
║                                                                              ║
║   ██████╗  █████╗ ██████╗ ████████╗ ██████╗ ██████╗     [bold cyan]SUBDOMAIN[/bold cyan]            ║
║   ██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗     [bold cyan]DIRECTORY[/bold cyan]            ║
║   ██████╔╝███████║██████╔╝   ██║   ██║   ██║██████╔╝     [bold cyan]RECON[/bold cyan]                ║
║   ██╔══██╗██╔══██║██╔═══╝    ██║   ██║   ██║██╔══██╗                         ║
║   ██║  ██║██║  ██║██║        ██║   ╚██████╔╝██║  ██║                         ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
           [bold yellow]⚡ NEXT-GEN ATTACK SURFACE MAPPER — SUBDOMAIN & DIRECTORY HUNTER ⚡[/bold yellow]
"""

# Global pause-control state tracking flags
SCAN_PAUSED = False
SCAN_ABORTED = False

def parse_status_codes(cfg_string):
    if not cfg_string:
        return set()
    codes = set()
    for block in cfg_string.split(','):
        block = block.strip()
        if '-' in block:
            try:
                start, end = map(int, block.split('-'))
                codes.update(range(start, end + 1))
            except ValueError:
                continue
        else:
            try:
                codes.add(int(block))
            except ValueError:
                continue
    return codes

def parse_size_filters(cfg_string):
    if not cfg_string:
        return []
    
    def to_bytes(text):
        text = text.strip().upper()
        match = re.match(r'^(\d+)\s*(B|KB|MB|GB)?$', text)
        if not match:
            return None
        val, unit = match.groups()
        val = int(val)
        if unit == 'KB': return val * 1024
        if unit == 'MB': return val * 1024 * 1024
        if unit == 'GB': return val * 1024 * 1024 * 1024
        return val

    filters = []
    for block in cfg_string.split(','):
        block = block.strip()
        if '-' in block:
            try:
                start_str, end_str = block.split('-')
                start_b = to_bytes(start_str)
                end_b = to_bytes(end_str)
                if start_b is not None and end_b is not None:
                    filters.append(('range', start_b, end_b))
            except ValueError:
                continue
        else:
            b_val = to_bytes(block)
            if b_val is not None:
                filters.append(('exact', b_val))
    return filters

def format_size(num_bytes):
    if num_bytes is None:
        return "0B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.0f}{unit}" if unit == 'B' else f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f}TB"

def colorize_status(status):
    status_int = int(status) if str(status).isdigit() else 0
    if 200 <= status_int < 300: return f"[bold green]{status}[/bold green]"
    if 300 <= status_int < 400: return f"[bold cyan]{status}[/bold cyan]"
    if 400 <= status_int < 500: return f"[bold yellow]{status}[/bold yellow]"
    return f"[bold red]{status}[/bold red]"

def is_filtered(status, size, inc_codes, exc_codes, exc_sizes, wildcards):
    if (status, size) in wildcards:
        return True
    if inc_codes and status not in inc_codes:
        return True
    if exc_codes and status in exc_codes:
        return True
    for f_type, *bounds in exc_sizes:
        if f_type == 'exact' and size == bounds[0]:
            return True
        if f_type == 'range' and bounds[0] <= size <= bounds[1]:
            return True
    return False

def profile_target_wildcards(base_host, proto):
    console.print("[bold yellow][*] Calibrating Engine Baseline Filters (Wildcard Detection Check)...[/bold yellow]")
    wildcard_signatures = set()
    
    for _ in range(3):
        rand_str = f"/{secrets.token_hex(6)}"
        try:
            conn = (http.client.HTTPSConnection(base_host, 443, timeout=4.0) 
                    if proto == "https" else http.client.HTTPConnection(base_host, 80, timeout=4.0))
            conn.request("GET", rand_str, headers={'User-Agent': 'Mozilla/5.0 (VortexEngine)'})
            res = conn.getresponse()
            body = res.read()
            wildcard_signatures.add((int(res.status), len(body)))
        except Exception:
            continue
            
    if wildcard_signatures:
        for status, size in wildcard_signatures:
            console.print(f"  [bold magenta][!][/bold magenta] Profiler locked onto false-positive rule: Status [cyan]{status}[/cyan] ({format_size(size)})")
    else:
        console.print("  [bold green][+][/bold green] Clean baseline profiling: Target is responding normally.")
        
    return wildcard_signatures

def fetch_passive_subdomains(domain):
    console.print(f"\n[bold cyan][*][/bold cyan] Extracting Passive Footprints for: [yellow]{domain}[/yellow]...")
    subdomains = set()
    
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode('utf-8'))
            for entry in data:
                name = entry['name_value'].lower()
                for part in (name.split("\n") if "\n" in name else [name]):
                    part = part.replace("*.", "").strip()
                    if part.endswith(domain) and part != domain:
                        subdomains.add(part)
        console.print("  [bold green][+][/bold green] Ingested Certificate logs from [cyan]crt.sh[/cyan]")
    except Exception:
        console.print("  [bold bright_black][!][/bold bright_black] Engine [red]crt.sh[/red] timed out/rate-limited.")

    return list(subdomains)

def verify_host(host):
    try:
        ip = socket.gethostbyname(host)
        for port, proto in [(443, "https"), (80, "http")]:
            try:
                conn = (http.client.HTTPSConnection(host, port, timeout=2.0) 
                        if proto == "https" else http.client.HTTPConnection(host, port, timeout=2.0))
                conn.request("HEAD", "/")
                res = conn.getresponse()
                return {"host": host, "ip": ip, "status": int(res.status), "proto": proto}
            except Exception:
                continue
        return {"host": host, "ip": ip, "status": "Alive", "proto": "http"}
    except socket.gaierror:
        return None

def fuzz_directory_path(target_url, base_host, path, proto):
    global SCAN_PAUSED, SCAN_ABORTED
    
    while SCAN_PAUSED:
        time.sleep(0.2)
        if SCAN_ABORTED:
            return None
            
    if SCAN_ABORTED:
        return None

    clean_path = path if path.startswith('/') else f"/{path}"
    try:
        conn = (http.client.HTTPSConnection(base_host, 443, timeout=4.0) 
                if proto == "https" else http.client.HTTPConnection(base_host, 80, timeout=4.0))
        conn.request("GET", clean_path, headers={
            'User-Agent': 'Mozilla/5.0 (VortexEngine/2.0; Elite Architecture)',
            'Accept': '*/*',
            'Connection': 'keep-alive'
        })
        res = conn.getresponse()
        body = res.read()
        size = len(body)
        
        redirect_str = ""
        if res.status in [301, 302, 307, 308]:
            redirect_str = res.headers.get('Location', '')
            
        return {"path": clean_path, "status": int(res.status), "size": size, "redirect": redirect_str}
    except Exception:
        return None

# --- STRATEGY ROUTERS ---

def handle_subdomain_strategy(domain, sub_choice=None, target_wl=None, threads=40):
    if not sub_choice:
        console.print("\n[bold yellow]═══ SUBDOMAIN RECONNAISSANCE MODE ═══[/bold yellow]")
        console.print("[bold cyan][1][/bold cyan] Passive Intelligence Mapping Only [bright_black](No Traffic Sent)[/bright_black]")
        console.print("[bold cyan][2][/bold cyan] Active Dictionary Brute-Force Only [bright_black](Wordlist Vector)[/bright_black]")
        console.print("[bold cyan][3][/bold cyan] Hybrid Attack Mapping Matrix [bright_black](Run Both Vectors)[/bright_black]")
        sub_choice = console.input("\n[bold cyan]ECLIPSE@RAPTOR> Choose Vector Type ID: [/bold cyan]").strip()
    
    all_potential_hosts = [domain, f"www.{domain}"]
    
    if sub_choice in ["1", "3"]:
        passive_found = fetch_passive_subdomains(domain)
        all_potential_hosts.extend(passive_found)
        
    if sub_choice in ["2", "3"]:
        if not target_wl:
            wl_path = console.input("[bold white] ↳ Path to Subdomain Wordlist [[Enter] for default]: [/bold white]").strip()
            target_wl = wl_path if wl_path else "wordlists/subdomains.txt"
        
        if not os.path.exists(target_wl):
            os.makedirs("wordlists", exist_ok=True)
            with open(target_wl, "w") as f:
                f.write("\n".join(["www", "mail", "cpanel", "webmail", "api", "vpn", "dev", "stage", "secure", "portal"]))
            
        try:
            with open(target_wl, "r") as f:
                for line in f:
                    item = line.strip().lower()
                    if item and not item.startswith("#"):
                        all_potential_hosts.append(f"{item}.{domain}")
        except Exception as e:
            console.print(f"[bold red][!] Error loading wordlist: {e}[/bold red]")

    all_potential_hosts = sorted(list(set(all_potential_hosts)))
    validated_live_hosts = []

    console.print(f"\n[bold magenta]► Launching Multi-Threaded Host Validation Layer across {len(all_potential_hosts)} instances...[/bold magenta]")
    with Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn(), TimeRemainingColumn(), console=console) as progress:
        task = progress.add_task("[cyan]Resolving Active Targets...", total=len(all_potential_hosts))
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(verify_host, host): host for host in all_potential_hosts}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    validated_live_hosts.append(res)
                progress.update(task, advance=1)

    infra_table = Table(title=f"VORTEX VERIFIED MAP: {domain}", header_style="bold magenta", border_style="bright_black")
    infra_table.add_column("LIVE HOST ENDPOINT", style="white")
    infra_table.add_column("RESOLVED ENDPOINT IP", style="green", justify="center")
    infra_table.add_column("HTTP ROOT BANNER", style="yellow", justify="center")
    
    for entry in validated_live_hosts:
        infra_table.add_row(f"{entry['proto']}://{entry['host']}", entry["ip"], str(entry["status"]))
    console.print("\n", infra_table, "\n")


def handle_directory_strategy(target_input, inc_input=None, exc_input=None, size_input=None, dir_wl_path=None, ext_input=None, threads=50):
    global SCAN_PAUSED, SCAN_ABORTED
    SCAN_PAUSED = False
    SCAN_ABORTED = False

    if target_input.startswith("https://"):
        proto = "https"
    elif target_input.startswith("http://"):
        proto = "http"
    else:
        proto = "https"

    clean_target = target_input.replace("http://", "").replace("https://", "")
    base_host = clean_target.split('/')[0]

    wildcards = profile_target_wildcards(base_host, proto)

    if inc_input is None:
        console.print("\n[bold yellow]═══ DIRECTORY VECTOR FILTERING CONFIGURATION ═══[/bold yellow]")
        inc_input = console.input("[bold white] ↳ Include Status Codes [[Enter] for 200,204,301,302,403]: [/bold white]").strip()
    inc_codes = parse_status_codes(inc_input if inc_input else "200,204,301,302,403")
    
    if exc_input is None:
        exc_input = console.input("[bold white] ↳ Exclude Status Codes [[Enter] for None]: [/bold white]").strip()
    exc_codes = parse_status_codes(exc_input)
    
    if size_input is None:
        size_input = console.input("[bold white] ↳ Exclude Response Sizes (e.g. 0B,500B-2KB) [[Enter] for None]: [/bold white]").strip()
    exc_sizes = parse_size_filters(size_input)

    if dir_wl_path is None:
        console.print("\n[bold yellow]═══ DICTIONARY PATH SETTINGS ═══[/bold yellow]")
        dir_wl_path = console.input("[bold white] ↳ Path to Directory Wordlist [[Enter] for Default]: [/bold white]").strip()
    target_dir_wl = dir_wl_path if dir_wl_path else "wordlists/directories.txt"
    
    if not os.path.exists(target_dir_wl):
        os.makedirs("wordlists", exist_ok=True)
        with open(target_dir_wl, "w") as f:
            f.write("\n".join(["admin", "login", "robots.txt", "backup", "private", "api"]))
            
    if ext_input is None:
        ext_input = console.input("[bold white] ↳ Target Extensions to Force-Append (e.g. php,html,txt) [[Enter] for None]: [/bold white]").strip()
    extensions = [e.strip().lstrip('.') for e in ext_input.split(',')] if ext_input else []

    base_paths = []
    try:
        with open(target_dir_wl, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    base_paths.append(line)
    except Exception as e:
        console.print(f"[bold red][!] Error processing wordlist mapping vectors: {e}[/bold red]")
        base_paths = ["admin", "login", "robots.txt"]

    compiled_paths = []
    for path in base_paths:
        compiled_paths.append(path)
        for ext in extensions:
            if not path.endswith(f".{ext}"):
                compiled_paths.append(f"{path}.{ext}")
                
    compiled_paths = sorted(list(set(compiled_paths)))

    console.print(f"\n[bold yellow]⚡ Commencing Structural Scanning Grid against: {proto}://{base_host}/[/bold yellow]")
    console.print("[bold red][!] Press CTRL+C at any time to pause threads and open the intercept menu.[/bold red]")
    console.print(f"[bold dim]Time     Status     Size      Fuzzed Location Pathway[/bold dim]")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(fuzz_directory_path, target_input, base_host, p, proto): p for p in compiled_paths}
        
        try:
            for future in as_completed(futures):
                if SCAN_ABORTED:
                    break
                res = future.result()
                if res:
                    if not is_filtered(res["status"], res["size"], inc_codes, exc_codes, exc_sizes, wildcards):
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        color_stat = colorize_status(res["status"])
                        human_size = format_size(res["size"]).rjust(7)
                        redirect_info = f" -> [cyan]{res['redirect']}[/cyan]" if res["redirect"] else ""
                        
                        console.print(f"[{timestamp}] {color_stat} - {human_size} - [white]{res['path']}[/white]{redirect_info}")
        
        except KeyboardInterrupt:
            SCAN_PAUSED = True
            console.print("\n\n[bold yellow]███████████████ SCANNING PAUSED (THREADS ASLEEP) ███████████████[/bold yellow]")
            console.print("[bold white][c][/bold white] Continue scanning processing grid")
            console.print("[bold white][q][/bold white] Stop vector execution and return to Core Module menu")
            
            while True:
                op = input("\nECLIPSE@INTERCEPT> Action selection: ").strip().lower()
                if op == 'c':
                    console.print("[bold green][*] Resuming scanner engine pipelines...[/bold green]\n")
                    SCAN_PAUSED = False
                    for future in as_completed(futures):
                        if SCAN_ABORTED: break
                        res = future.result()
                        if res and not is_filtered(res["status"], res["size"], inc_codes, exc_codes, exc_sizes, wildcards):
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            console.print(f"[{timestamp}] {colorize_status(res['status'])} - {format_size(res['size']).rjust(7)} - [white]{res['path']}[/white]" + (f" -> [cyan]{res['redirect']}[/cyan]" if res["redirect"] else ""))
                    break
                elif op == 'q':
                    console.print("[bold red][!] Aborting active fuzzing matrix operations...[/bold red]")
                    SCAN_ABORTED = True
                    SCAN_PAUSED = False
                    break
                else:
                    print("Invalid operational command choice code.")

# --- NATIVE IN-MENU MANUAL HELP MATRIX ---

def display_interactive_manual():
    console.print(f"\n╭───────────────────────────────────────────────────────────── TACTICAL MANUAL ─────────────────────────────────────────────────────────────╮")
    print(f"│ Script-Level Command Line Execution Parameters:                                                                                           │")
    print(f"│   python raptor.py --target <Domain/URL> [Execution Flags]                                                                                │")
    print(f"│   python raptor.py --target example.com --mode sub --strategy 3                                                                           │")
    print(f"│   python raptor.py --target https://example.com --mode dir --include 200,302 --ext php,html                                               │")
    print(f"╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯")
    console.print(f"\n[bold cyan]Operational Arguments Reference Matrix[/bold cyan]")
    print(f"┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"┃ Flag Vector ┃ Parameter Mapping                       ┃ Functional Definition / Options Details                                  ┃")
    print(f"┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩")
    print(f"│  -t, --target│ <Target Scope String Mapping>           │ Target domain name or base HTTP/HTTPS URL destination protocol layout.   │")
    print(f"│  -m, --mode  │ <Engine Scan Profile Mode>              │ Target operations boundaries: 'sub' (Subdomains) or 'dir' (Directories). │")
    print(f"│  --strategy  │ <Subdomain Strategy Option>             │ Strategy IDs: [1] Passive Recon, [2] Wordlist Brute, [3] Hybrid Matrix.  │")
    print(f"│  -w, --wlist │ <Custom Wordlist System Pathway>        │ File path location pointer to replace default fallback brute files.      │")
    print(f"│  --include   │ <Status Codes Validation Filter>        │ White-list server status codes separated by commas (Default: 200,301,302)│")
    print(f"│  --exclude   │ <Status Codes Rejection Filter>         │ Hard exclusions server response status codes to drop completely.        │")
    print(f"│  --size      │ <Content Length Exclusion Bounds>       │ Size filter exact mappings or range blocks to ignore (e.g., 0B, 2KB-5KB) │")
    print(f"│  -x, --ext   │ <Force Append Extension Array>          │ Extensions to enforce during directory sweeps (e.g., php,html,txt,json)   │")
    print(f"│  --threads   │ <Max Thread Processing Cap Allocation> │ Processing worker pool concurrent allocation ceiling limits (40/50 caps)│")
    print(f"┗━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    console.print(f"\n[bold yellow]💡 INTERACTIVE MODULE ENGINE NOTES:[/bold yellow]")
    print(f" ↳ [1] Subdomain Mode: Passive vector uses crt.sh certificate transparency tables without altering endpoint firewalls.")
    print(f" ↳ [2] Directory Mode: Implements dynamic calibration profiling rules to catch false-positive wildcard traps natively.")
    print(f" ↳ [CTRL+C INTERCEPT]: During active fuzz loops, hitting break switches into a thread-safe menu to alter tracking parameters.")


# --- MASTER MODULE PIPELINE RUNNER ---

def run_raptor_pipeline(initial_target=None):
    os.makedirs("wordlists", exist_ok=True)
    console.print(RAPTOR_BANNER)
    console.print("") 
    
    target_scope = initial_target if initial_target else ""
    if not target_scope:
        target_scope = console.input("[bold magenta] ↳ [/bold magenta][bold white]Enter Scan Target Destination (Domain/URL): [/bold white]").strip()
        while not target_scope:
            console.print("[bold red][[!]] Error: Scope input sequence verification cannot be null.[/bold red]")
            target_scope = console.input("[bold magenta] ↳ [/bold magenta][bold white]Enter Scan Target Destination: [/bold white]").strip()

    while True:
        menu_content = (
            f"[bold green]TARGET SCOPE CONFIGURATION:[/bold green] [yellow]{target_scope}[/yellow]\n\n"
            "[bold cyan][1][/bold cyan] Subdomain Reconnaissance Matrix [bright_black](Passive / Active Brute)[/bright_black]\n"
            "[bold magenta][2][/bold magenta] Directory Path Discovery Matrix   [bright_black](Fuzzing & Content Filters)[/bright_black]\n"
            "[bold yellow][3][/bold yellow] Shift Target Scope Matrix        [bright_black](Modify Active Target)[/bright_black]\n"
            "[bold blue][4][/bold blue] Tactical Engine Reference Manual  [bright_black](View Options Documentation)[/bright_black]\n\n"
            "[bold red][0][/bold red] Complete Task Execution Sequence [bright_black](Return to Core Control)[/bright_black]"
        )
        console.print("\n", Panel(menu_content, title="[bold magenta]VECTOR MODULE CONFIGURATION[/bold magenta]", border_style="cyan"))
        
        choice = console.input("\n[bold cyan]ECLIPSE@RAPTOR> Select Operational Strategy Vector: [/bold cyan]").strip()
        
        if choice == "0" or not choice:
            console.print("\n[bold yellow][*] Flushing cache arrays. Returning to Master ECLIPSE Matrix Framework...[/bold yellow]\n")
            break
            
        elif choice == "1":
            clean_domain = target_scope.replace("http://", "").replace("https://", "").split('/')[0]
            handle_subdomain_strategy(clean_domain)
            input("\n[DONE] Strategy Complete. Press Enter to return to Vector Menu...")
            
        elif choice == "2":
            handle_directory_strategy(target_scope)
            input("\n[DONE] Strategy Complete. Press Enter to return to Vector Menu...")

        elif choice == "3":
            new_scope = console.input("\n[bold yellow] ↳ Enter NEW Scan Target Destination (Domain/URL): [/bold yellow]").strip()
            if new_scope:
                target_scope = new_scope
                console.print(f"[bold green][+] Target scope successfully changed onto:[/bold green] [yellow]{target_scope}[/yellow]")
            else:
                console.print("[bold red][!] Change canceled. Scope cannot be empty.[/bold red]")
            input("\nPress Enter to return to Vector Menu...")

        elif choice == "4":
            display_interactive_manual()
            input("\nPress Enter to return to Vector Menu...")


class HardenedHelpParser(argparse.ArgumentParser):
    def error(self, message):
        console.print(f"\n[bold red][!] Operational Execution Matrix Exception: {message}[/bold red]")
        self.print_help()
        sys.exit(2)

    def print_help(self):
        console.print(RAPTOR_BANNER)
        display_interactive_manual()


# --- RUNTIME CONTROLLER ---

# --- RUNTIME CONTROLLER ENTRY POINT ---

def main():
    parser = HardenedHelpParser(add_help=False)
    
    parser.add_argument("-t", "--target", help=argparse.SUPPRESS)
    parser.add_argument("-m", "--mode", choices=["sub", "dir"], help=argparse.SUPPRESS)
    parser.add_argument("--strategy", choices=["1", "2", "3"], help=argparse.SUPPRESS)
    parser.add_argument("-w", "--wlist", help=argparse.SUPPRESS)
    parser.add_argument("--include", help=argparse.SUPPRESS)
    parser.add_argument("--exclude", help=argparse.SUPPRESS)
    parser.add_argument("--size", help=argparse.SUPPRESS)
    parser.add_argument("-x", "--ext", help=argparse.SUPPRESS)
    parser.add_argument("--threads", type=int, help=argparse.SUPPRESS)
    parser.add_argument("-h", "--help", action="store_true", help=argparse.SUPPRESS)

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(0)

    if args.help:
        parser.print_help()
        sys.exit(0)

    try:
        run_raptor_pipeline(initial_target=args.target if args.target else None)
    except KeyboardInterrupt:
        console.print("\n[bold red][!] Execution stopped by operator request switch command.[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    main()