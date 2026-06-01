#!/usr/bin/env python3
import os
import sys

def main():
    # Dynamically locate the home directory of this suite
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    sys.path.insert(0, base_dir)
    
    # Import the untouched core system modules
    import core
    import asyncio
    
    # Check if a pipeline argument (--geo) was supplied via the CLI
    # This captures both: "aethereye --geo pristina" and your main menu "aethereye --geo target"
    if "--geo" in sys.argv:
        try:
            geo_idx = sys.argv.index("--geo")
            target_location = sys.argv[geo_idx + 1]
            
            # Replicate core.py's exact automated background engine loop execution
            engine = core.AetherEyeCore()
            core.console.print(f"[bold yellow][*] Initializing Automated Pipeline Vector: {target_location}[/bold yellow]")
            asyncio.run(core.GeoHarvestEngine(engine).run(target_location))
            return # Exit successfully after completing the pipeline run
        except (IndexError, ValueError):
            core.console.print("[bold red][!] Error: Missing location target string after --geo argument.[/bold red]")
            return

    # Default fallback: Fire the standard TUI interactive control panel
    engine = core.AetherEyeCore()
    core.run_tui(engine)

if __name__ == '__main__':
    main()