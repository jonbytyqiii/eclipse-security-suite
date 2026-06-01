#!/usr/bin/env python3
import asyncio
import httpx
import logging
import random
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()

class SocialStalkerEngine:
    def __init__(self, core_framework):
        self.core = core_framework
        self.settings = self.core.config.get("scraping_settings", {})
        
        self.platforms = {
            "GitHub": {"url": "https://github.com/{}", "error_type": "status", "validation": "text"},
            "Instagram": {"url": "https://www.instagram.com/{}/", "error_type": "text", "validation": "Login • Instagram"},
            "TikTok": {"url": "https://www.tiktok.com/@{}", "error_type": "text", "validation": "Watch historical videos"},
            "Pinterest": {"url": "https://www.pinterest.com/{}/", "error_type": "status", "validation": "text"},
            "Reddit": {"url": "https://www.reddit.com/user/{}", "error_type": "status", "validation": "text"}
        }

    def get_random_user_agent(self):
        ua_list = self.settings.get("user_agents", ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"])
        return random.choice(ua_list)

    async def check_platform(self, client, site, config, username, results_list, progress, task_id):
        target_url = config["url"].format(username)
        headers = {"User-Agent": self.get_random_user_agent(), "Accept-Language": "en-US,en;q=0.9"}
        
        try:
            await asyncio.sleep(random.uniform(0.2, 0.6))
            resp = await client.get(target_url, headers=headers, follow_redirects=True, timeout=6.0)
            is_found = False

            if config["error_type"] == "status" and resp.status_code == 200:
                is_found = True
            elif config["error_type"] == "text" and resp.status_code == 200 and config["validation"] not in resp.text:
                is_found = True

            if is_found:
                results_list.append((site, "FOUND", target_url))
                self.core.log_intel("SOCIAL_STALKER", f"{username}@{site.lower()}.com", "Identity Profile Match", target_url, "Global Social Graph")
            else:
                results_list.append((site, "NULL", target_url))
        except:
            results_list.append((site, "TIMEOUT", target_url))
        finally:
            progress.update(task_id, advance=1)

    async def run(self, username):
        console.print(f"[bold magenta][*][/bold magenta] Querying global platform nodes for user identity: [bold cyan]'{username}'[/bold cyan]")
        discovered_matches = []
        proxy_str = self.core.rotate_proxy()
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(bar_width=40, style="magenta"), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), console=console) as progress:
            task = progress.add_task("[bold white]Stalking nodes...[/bold white]", total=len(self.platforms))
            async with httpx.AsyncClient(proxy=proxy_str, timeout=8.0) as client:
                worker_pool = [self.check_platform(client, site, config, username, discovered_matches, progress, task) for site, config in self.platforms.items()]
                await asyncio.gather(*worker_pool)

        table = Table(title=f"Identity Extraction Footprint: {username}", border_style="magenta", header_style="bold magenta", expand=True)
        table.add_column("Target Site Node", style="white", width=20)
        table.add_column("Status", justify="center")
        table.add_column("Intelligence URL", style="cyan")

        found_count = 0
        for site, status, url in sorted(discovered_matches):
            if status == "FOUND":
                found_count += 1
                table.add_row(site, "[bold green]FOUND[/bold green]", url)
            else:
                table.add_row(f"[dim]{site}[/dim]", "[dim]NULL[/dim]", f"[dim]{url}[/dim]")

        console.print("\n")
        console.print(table)
        console.print(f"\n[bold green][+][/bold green] Analysis complete. Recovered [cyan]{found_count}[/cyan] active footprints.")