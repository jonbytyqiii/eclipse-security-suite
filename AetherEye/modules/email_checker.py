#!/usr/bin/env python3
import asyncio
import httpx
import random
import time
import logging
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

console = Console()

class EmailCheckerEngine:
    def __init__(self, core_framework):
        self.core = core_framework
        self.settings = self.core.config.get("scraping_settings", {})
        
        # Production-grade registration and recovery cross-reference API structures
        self.targets = {
            "GitHub": {
                "url": "https://github.com/signup/check_user",
                "method": "POST",
                "json_payload": {"email": "{}"},
                "headers": {"Component": "Signup"},
                "handler": "json",
                "taken": lambda j: "is already associated" in j.get("errors", {}).get("email", "") or j.get("status") == "taken"
            },
            "Discord": {
                "url": "https://discord.com/api/v9/auth/register",
                "method": "POST",
                "json_payload": {"email": "{}", "consent": True, "gift_code_sku_id": None, "invite": None},
                "handler": "json",
                "taken": lambda j: "EMAIL_ALREADY_REGISTERED" in str(j.get("errors", {}).get("email", {}))
            },
            "TikTok": {
                "url": "https://www.tiktok.com/passport/web/email/check_availability/",
                "method": "POST",
                "data": {"email": "{}"},
                "handler": "json",
                "taken": lambda j: j.get("data", {}).get("is_registered") == 1 or j.get("description") == "Email already registered"
            },
            "Netflix": {
                "url": "https://www.netflix.com/api/shakti/v1e2f7bb7/signup/mre",
                "method": "POST",
                "json_payload": {"email": "{}"},
                "handler": "json",
                "taken": lambda j: j.get("status") == "assigned" or j.get("isCurrentCustomer") is True
            },
            "Spotify": {
                "url": "https://spclient.wg.spotify.com/signup/public/v1/account",
                "method": "POST",
                "data": {"email": "{}", "validate": "1"},
                "handler": "json",
                "taken": lambda j: j.get("status") == 20 or "status" in j and j.get("status") != 1
            },
            "Steam": {
                "url": "https://store.steampowered.com/join/checkemailavailability/",
                "method": "POST",
                "data": {"email": "{}", "count": "1"},
                "handler": "json",
                "taken": lambda j: j.get("bAvailable") is False or j.get("success") == 0
            },
            "Pinterest": {
                "url": "https://www.pinterest.com/resource/UserRegisterResource/get/",
                "method": "GET",
                "url_format": lambda url, em: f"{url}?source_url=%2F&data=%7B%22options%22%3A%7B%22email%22%3A%22{em}%22%7D%7D",
                "handler": "json",
                "taken": lambda j: j.get("resource_response", {}).get("data") is True
            },
            "Adobe": {
                "url": "https://auth.services.adobe.com/auth/v1/users/check",
                "method": "POST",
                "json_payload": {"username": "{}"},
                "handler": "status",
                "taken": lambda r: r.status_code == 200
            },
            "Imgur": {
                "url": "https://api.imgur.com/signin/v1/email/available",
                "method": "POST",
                "data": {"email": "{}"},
                "handler": "json",
                "taken": lambda j: j.get("data", {}).get("available") is False
            },
            "WordPress": {
                "url": "https://wordpress.com/wp-admin/admin-ajax.php",
                "method": "POST",
                "data": {"action": "validate_username_or_email", "email": "{}"},
                "handler": "json",
                "taken": lambda j: j.get("success") is False and "email" in j.get("data", {}).get("errors", {})
            }
        }

    def get_random_user_agent(self):
        ua_list = self.settings.get("user_agents", ["Mozilla/5.0 (Windows NT 10.0; Win64; x64)"])
        return random.choice(ua_list)

    async def probe_node(self, client, site, config, email, state_list, progress, task_id):
        """Asynchronously tests platform vectors using error-insulated verification pipelines"""
        headers = {
            "User-Agent": self.get_random_user_agent(),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://google.com"
        }
        if "headers" in config:
            headers.update(config["headers"])

        try:
            # Human-pacing micro delay adjustments to mitigate WAF blocks
            await asyncio.sleep(random.uniform(0.4, 0.9))
            
            method = config["method"]
            resp = None

            if method == "GET":
                url = config["url_format"](config["url"], email) if "url_format" in config else config["url"].format(email)
                resp = await client.get(url, headers=headers, timeout=7.0)
            elif method == "POST":
                url = config["url"]
                if "data" in config:
                    payload = {k: v.format(email) if isinstance(v, str) else v for k, v in config["data"].items()}
                    resp = await client.post(url, headers=headers, data=payload, timeout=7.0)
                elif "json_payload" in config:
                    payload = {k: v.format(email) if isinstance(v, str) else v for k, v in config["json_payload"].items()}
                    resp = await client.post(url, headers=headers, json=payload, timeout=7.0)

            if resp is None:
                state_list.append((site, "ERROR"))
                return

            # Explicit Rate Limit Threat Evaluation Check
            if resp.status_code in [429, 403]:
                state_list.append((site, "LIMIT"))
                return

            is_taken = False
            if config["handler"] == "json":
                try:
                    json_data = resp.json()
                    is_taken = config["taken"](json_data)
                except ValueError:
                    # Insulation logic catching soft-404 HTML string dumps
                    state_list.append((site, "ERROR"))
                    return
            elif config["handler"] == "status":
                is_taken = config["taken"](resp)

            if is_taken:
                state_list.append((site, "FOUND"))
                self.core.log_intel(
                    vector="EMAIL_CHECKER",
                    email=email,
                    business=f"Account Identified on {site}",
                    url=url[:75],
                    zone="Global Identity Graph"
                )
            else:
                state_list.append((site, "ABSENT"))

        except (httpx.RequestError, httpx.TimeoutException):
            state_list.append((site, "LIMIT"))
        except Exception as e:
            logging.error(f"Insulated cluster anomaly on platform target {site}: {e}")
            state_list.append((site, "ERROR"))
        finally:
            progress.update(task_id, advance=1)

    async def run(self, email):
        console.print(f"[bold magenta][*][/bold magenta] Executing programmatic Holehe handle sweep for target: [bold cyan]'{email}'[/bold cyan]")
        start_time = time.time()
        discovered_states = []
        proxy_str = self.core.rotate_proxy()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, style="magenta", complete_style="bold magenta"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task("[bold white]Cross-checking platform nodes...[/bold white]", total=len(self.targets))
            async with httpx.AsyncClient(proxy=proxy_str, timeout=10.0, follow_redirects=True) as client:
                workers = [
                    self.probe_node(client, site, config, email, discovered_states, progress, task)
                    for site, config in self.targets.items()
                ]
                await asyncio.gather(*workers)

        duration = round(time.time() - start_time, 2)
        
        table = Table(title=f"Platform Fingerprint Audit Ledger: {email}", border_style="magenta", header_style="bold magenta", expand=True)
        table.add_column("Target Platform Registry", style="white", width=25)
        table.add_column("Resolution Matrix Status", justify="center")

        match_count = 0
        for site, state in sorted(discovered_states):
            if state == "FOUND":
                match_count += 1
                table.add_row(site, "[bold green][+] REGISTERED / USED[/bold green]")
            elif state == "LIMIT":
                table.add_row(site, "[bold yellow][x] RATE LIMITED / TIMEOUT[/bold yellow]")
            elif state == "ERROR":
                table.add_row(site, "[bold red][!] TARGET DISRUPTION[/bold red]")
            else:
                table.add_row(f"[dim]{site}[/dim]", "[dim][-] NOT REGISTERED[/dim]")

        console.print("\n")
        console.print(table)
        console.print(f"\n[bold green][+] Pipeline Finished in {duration}s. Recovered [cyan]{match_count}/{len(self.targets)}[/cyan] platform registry footprints.[/bold green]")