#!/usr/bin/env python3
import asyncio
import httpx
import logging
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

class ShodanInfraEngine:
    def __init__(self, core_framework):
        self.core = core_framework
        self.api_key = self.core.config.get("api_keys", {}).get("shodan", "")

    async def run(self, ip_target):
        """Queries Shodan API database for network infrastructure and active vulnerabilities"""
        # Explicit validation check for missing or unconfigured API keys
        if not self.api_key or "YOUR_" in self.api_key or self.api_key.strip() == "":
            console.print("[bold red][!] ERROR: Shodan API key is not provided.[/bold red]")
            return

        console.print(f"[bold magenta][*][/bold magenta] Contacting Shodan Intelligence maps for IP: [bold cyan]{ip_target}[/bold cyan]")
        
        url = f"https://api.shodan.io/shodan/host/{ip_target}?key={self.api_key}"
        proxy_str = self.core.rotate_proxy()

        try:
            async with httpx.AsyncClient(proxy=proxy_str, timeout=10.0) as client:
                resp = await client.get(url)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    org = data.get("org", "Unknown Infrastructure Group")
                    isp = data.get("isp", "Unknown Provider ASN")
                    os_version = data.get("os", "Undetermined Fingerprint OS")
                    ports = data.get("ports", [])
                    vulns = data.get("vulns", [])

                    intel_summary = (
                        f"[bold white]Target Autonomous Group (Org):[/bold white] {org}\n"
                        f"[bold white]Transit Infrastructure Provider (ISP):[/bold white] {isp}\n"
                        f"[bold white]Remote Fingerprint Platform OS:[/bold white] {os_version}"
                    )
                    console.print(Panel(intel_summary, title=f"TOPOLOGY OVERVIEW: {ip_target}", border_style="cyan"))

                    if ports:
                        port_str = ", ".join(f"[bold green]{p}[/bold green]" for p in ports)
                        console.print(Panel(port_str, title="EXPOSED PORTS SCAN MATRIX", border_style="green"))

                    if vulns:
                        vuln_str = ", ".join(f"[bold red]{v}[/bold red]" for v in vulns[:12])
                        console.print(Panel(vuln_str, title="🔥 EXPOSED KNOWN SYSTEM VULNERABILITIES", border_style="red"))
                    else:
                        console.print("[bold green][+] Clean Bill of Health: No public vulnerabilities indexed on Shodan.[/bold green]")
                        
                elif resp.status_code == 404:
                    console.print("[bold yellow][!] Shodan Registry Notice: No intelligence records exist for this specific host.[/bold yellow]")
                elif resp.status_code == 401:
                    console.print("[bold red][!] API Authentication Denied: Shodan API key is invalid or expired.[/bold red]")
                else:
                    console.print(f"[bold red][!] Connection Drop: API returned status code {resp.status_code}[/bold red]")
                    
        except Exception as e:
            console.print(f"[bold red][!] Interface error linking to Shodan: {e}[/bold red]")
            logging.error(f"Shodan mapping fail: {e}")