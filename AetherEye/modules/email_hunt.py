#!/usr/bin/env python3
import asyncio
import httpx
import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class EmailHuntEngine:
    def __init__(self, core_framework):
        self.core = core_framework
        self.api_key = self.core.config.get("api_keys", {}).get("hunter_io", "")

    async def run(self, domain):
        """Queries Hunter.io for corporate addresses and records distinct findings"""
        # Explicit validation check for missing or unconfigured API keys
        if not self.api_key or "YOUR_" in self.api_key or self.api_key.strip() == "":
            console.print("[bold red][!] ERROR: Hunter.io API key is not provided.[/bold red]")
            return

        console.print(f"[bold magenta][*][/bold magenta] Querying global intelligence registers for domain: [bold cyan]{domain}[/bold cyan]")
        
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={self.api_key}"
        proxy_str = self.core.rotate_proxy()

        try:
            # Using proxy= instead of deprecated proxies= dictionary parameter
            async with httpx.AsyncClient(proxy=proxy_str, timeout=10.0) as client:
                resp = await client.get(url)
                
                if resp.status_code == 200:
                    data = resp.json().get('data', {})
                    emails = data.get('emails', [])
                    
                    if not emails:
                        console.print("[bold yellow][*] No indexed corporate communication profiles recovered for this domain.[/bold yellow]")
                        return

                    table = Table(title=f"Target Corporate Identity Map: {domain.upper()}", border_style="magenta", header_style="bold magenta", expand=True)
                    table.add_column("Discovered Contact Node", style="white")
                    table.add_column("Organizational Role", style="yellow")
                    table.add_column("Confidence Score", justify="center", style="green")

                    new_records = 0
                    for item in emails:
                        email_str = item.get('value', '')
                        role = item.get('position', 'Unspecified Profile Domain') or 'Unspecified Profile Domain'
                        confidence = f"{item.get('confidence', 0)}%"
                        
                        is_new = self.core.log_intel(
                            vector="DOMAIN_HUNT",
                            email=email_str,
                            business=domain,
                            url=f"https://hunter.io/domains/{domain}",
                            zone="Global Corporate WAN"
                        )
                        
                        if is_new:
                            new_records += 1
                            table.add_row(email_str, role, confidence)
                        else:
                            table.add_row(f"[dim]{email_str} (Duplicate)[/dim]", role, "[dim]Skipped[/dim]")

                    console.print("\n")
                    console.print(table)
                    console.print(f"\n[bold green][+][/bold green] Analysis complete. Loaded [cyan]{new_records}[/cyan] unique records into local database storage.")
                
                elif resp.status_code == 401:
                    console.print("[bold red][!] API Error: Unauthorized access. Hunter.io API key is invalid or expired.[/bold red]")
                else:
                    console.print(f"[bold red][!] Threat Register Response Failure: Status code {resp.status_code}[/bold red]")
                    
        except Exception as e:
            console.print(f"[bold red][!] Network interface failure during api communication: {e}[/bold red]")
            logging.error(f"Hunter.io vector drop: {e}")