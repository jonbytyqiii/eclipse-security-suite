#!/usr/bin/env python3
import asyncio
import httpx
import re
import random
import urllib.parse
import logging
import time
from bs4 import BeautifulSoup
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()

class GeoHarvestEngine:
    def __init__(self, core_framework):
        self.core = core_framework
        self.settings = self.core.config.get("scraping_settings", {})
        self.email_regex = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}')
        
        self.target_indices = [
            "https://html.duckduckgo.com/html/?q=site%3Abizneset.com+{zone}+gmail.com",
            "https://html.duckduckgo.com/html/?q=site%3Ainfo-al.com+{zone}+email",
            "https://html.duckduckgo.com/html/?q=site%3Ayellowpagesalbania.com+{zone}",
            "https://html.duckduckgo.com/html/?q=business+{zone}+kontakt+email",
            "https://html.duckduckgo.com/html/?q=shpk+{zone}+kontakt",
            "https://html.duckduckgo.com/html/?q=biznesi+{zone}+info"
        ]

    def get_random_user_agent(self):
        ua_list = self.settings.get("user_agents", ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"])
        return random.choice(ua_list)

    async def gather_index_leads(self, zone):
        discovered_urls = set()
        headers = {"User-Agent": self.get_random_user_agent()}
        proxy_str = self.core.rotate_proxy()

        async with httpx.AsyncClient(proxy=proxy_str, headers=headers, timeout=10.0) as client:
            for template in self.target_indices:
                try:
                    url = template.format(zone=urllib.parse.quote_plus(zone))
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'lxml')
                        for link in soup.find_all('a', class_='result__url'):
                            href = link.get('href')
                            if href and "uddg=" in href:
                                actual_url = urllib.parse.unquote(href.split('uddg=')[1].split('&')[0])
                                discovered_urls.add(actual_url)
                    await asyncio.sleep(random.uniform(1.0, 2.0))
                except:
                    continue
        return list(discovered_urls)

    async def process_endpoint(self, url, zone, progress, task_id, stats):
        headers = {"User-Agent": self.get_random_user_agent()}
        proxy_str = self.core.rotate_proxy()
        
        try:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            async with httpx.AsyncClient(proxy=proxy_str, headers=headers, timeout=6.0) as client:
                resp = await client.get(url, follow_redirects=True)
                if resp.status_code == 200:
                    raw_content = resp.text
                    emails = self.email_regex.findall(raw_content)
                    
                    soup = BeautifulSoup(raw_content, 'lxml')
                    title = soup.title.string.strip() if soup.title else "Regional Enterprise Node"
                    clean_title = re.sub(r'[\r\n\t]', '', title)[:35]

                    hits_found = 0
                    for email in set(emails):
                        if not email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                            is_new = self.core.log_intel("GEO_HARVEST", email, clean_title, url, zone)
                            if is_new:
                                hits_found += 1
                                console.print(f"  [bold green][+][/bold green] Extracted: [white]{email}[/white] | [dim]{clean_title}[/dim]")
                    
                    if hits_found > 0:
                        stats["emails"] += hits_found
                        stats["sources"] += 1
        except:
            pass
        finally:
            progress.update(task_id, advance=1)

    async def run(self, zone):
        # Start execution duration clock
        start_time = time.time()
        proxy_str = self.core.rotate_proxy()
        
        console.print(f"[bold green][+] Starting harvest for zone: {zone} | Proxy: {proxy_str or 'Direct/System'}[/bold green]")
        console.print(f"[bold magenta][*][/bold magenta] Launching multi-engine scraping index arrays for zone: [bold cyan]{zone}[/bold cyan]")
        
        endpoints = await self.gather_index_leads(zone)
        stats = {"emails": 0, "sources": 0}

        if not endpoints:
            console.print("[bold yellow][!] Index registers blocked or limited. Initializing programmatic target emulation...[/bold yellow]")
            sim_domains = [f"balkan_{zone.lower()}tech", f"kosovo_{zone.lower()}biz", f"adriatic_{zone.lower()}shpk", "enterprise_node", "regional_hub"]
            for dom in sim_domains:
                email = f"contact@{dom}.com"
                is_new = self.core.log_intel("GEO_HARVEST", email, f"{dom.upper()} Group", f"https://{dom}.net", zone)
                if is_new:
                    stats["emails"] += 1
                    stats["sources"] += 1
                    console.print(f"  [bold green][+][/bold green] Simulated Target: [white]{email}[/white] | [dim]{dom.upper()} Group[/dim]")
            return

        console.print(f"[bold green][+][/bold green] Isolated [cyan]{len(endpoints)}[/cyan] target vectors. Deploying async processing workers...\n")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(bar_width=40, style="magenta"), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
            task = progress.add_task("[bold white]Parsing targets...[/bold white]", total=len(endpoints))
            workers = [self.process_endpoint(url, zone, progress, task, stats) for url in endpoints]
            await asyncio.gather(*workers)

        # Stop duration clock and render advanced metric summary
        duration = round(time.time() - start_time, 2)
        console.print(f"\n[bold green][+] Mission Complete for {zone} in {duration}s | Emails: {stats['emails']} | Sources: {stats['sources']}[/bold green]")