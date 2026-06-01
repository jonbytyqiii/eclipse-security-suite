#!/usr/bin/env python3
import os
import sys
import yaml
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# Core framework package namespaces
from reddevil.core.identifier import HashIdentifier
from reddevil.core.engine import RedDevilEngine
from reddevil.utils.ui import print_banner, TelemetryTracker

app = typer.Typer(help="RedDevil v3.0: God-Tier Cryptographic Forensic Framework")
console = Console()

def load_configurations():
    """Loads operational directives safely from local yaml configurations"""
    # Look for config in the current working directory to allow local runtime overrides
    local_config = os.path.join(os.getcwd(), "config.yaml")
    if os.path.exists(local_config):
        with open(local_config, "r") as f:
            return yaml.safe_load(f)
    return {
        "performance": {"chunk_size": 200000, "max_workers": 4, "enable_gpu": False},
        "rulesets": {"leetspeak": {'a':'4','e':'3','i':'1','o':'0','s':'5'}}
    }

def display_help_manual():
    """Renders a comprehensive terminal help manual breaking down options and usage examples"""
    console.print("\n" + "─" * 40 + " REDDEVIL DOCUMENTATION MANUAL " + "─" * 40 + "\n")
    
    table = Table(title="Operational Vector Reference Matrix", show_header=True, header_style="bold red", border_style="red")
    table.add_column("Vector Flag", style="cyan")
    table.add_column("Description", style="white")
    table.add_row("--target", "Specify target cryptographic target sequence under evaluation")
    table.add_row("--mask", "Apply custom positional masks or mutation rule paths")
    table.add_row("--godmode", "Force max throughput operational state configurations")
    table.add_row("--benchmark", "Execute standalone core performance telemetry scans")
    
    console.print(table)

def run_interactive_menu():
    """Fallback terminal wizard interface loop"""
    print_banner()
    console.print("[bold cyan][*] Initializing Interactive Cryptographic Evaluation Wizard...[/bold cyan]\n")
    
    target_hash = Prompt.ask("[bold white][?] Enter Target Hash or Encoded Node to Analyze[/bold white]")
    if not target_hash.strip():
        console.print("[bold red][!] Target sequence empty. Aborting workflow.[/bold red]")
        return

    identifier = HashIdentifier()
    category, subtype = identifier.identify(target_hash)
    
    console.print(f"\n[bold green][+] Structural Target Analysis Successful:[/bold green]")
    console.print(f"    - Match Target Type: [yellow]{subtype if subtype else 'Unknown Pattern'}[/yellow]")
    console.print(f"    - Structural Classification: [yellow]{category}[/yellow]\n")
    
    # Rest of your excellent interactive logic goes here...

@app.command()
def run(
    target: str = typer.Option(None, "--target", "-t", help="Target cryptographic string sequence"),
    mask: str = typer.Option(None, "--mask", "-m", help="Positional string transformation pattern"),
    godmode: bool = typer.Option(False, "--godmode", help="Force max throughput operational state configurations"),
    benchmark: bool = typer.Option(False, "--benchmark", help="Execute standalone core performance telemetry scans")
):
    """
    RedDevil v3.0 Command Orchestrator Interface
    """
    if target is None and mask is None and not godmode and not benchmark:
        run_interactive_menu()
    else:
        config = load_configurations()
        workers = config["performance"]["max_workers"] if config["performance"]["max_workers"] > 0 else 4
        engine = RedDevilEngine(max_workers=workers)
        
        if benchmark or godmode:
            TelemetryTracker.execute_benchmark_suit(engine)
            if benchmark:
                return
        
        identifier = HashIdentifier()
        category, subtype = identifier.identify(target)
        
        if mask and target and subtype:
            def cli_hook(count, elapsed):
                TelemetryTracker.render_live_stats(count, elapsed)
            res = engine.execute_mask_crack(target, subtype, mask, telemetry_callback=cli_hook)
            if res:
                print(f"[+] FOUND: {res}")
            else:
                print("[-] EXHAUSTED")

def main():
    """Global execution wrapper framework entrypoint"""
    try:
        if len(sys.argv) == 1:
            run_interactive_menu()
        else:
            app()
    except KeyboardInterrupt:
        console.print("\n\n[bold red][!] Session aborted by operator controller override.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()