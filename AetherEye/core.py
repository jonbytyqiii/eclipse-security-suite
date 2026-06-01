#!/usr/bin/env python3
import os
import sys
import time
import yaml
import sqlite3
import logging
import asyncio
import csv
import argparse
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Framework Sub-Module Imports
from modules.geo_harvest import GeoHarvestEngine
from modules.email_hunt import EmailHuntEngine
from modules.shodan_infra import ShodanInfraEngine
from modules.image_forensics import ImageForensicsEngine
from modules.social_stalker import SocialStalkerEngine
from modules.email_checker import EmailCheckerEngine

console = Console()

class AetherEyeCore:
    def __init__(self, config_path="config.yaml"):
        self.config_path = config_path
        self.session_id = os.urandom(3).hex().upper()
        self.boot_time = datetime.now().strftime("%H:%M:%S")
        
        os.makedirs("logs", exist_ok=True)
        self.setup_logging()
        
        self.config = self.load_config()
        self.db_conn = self.setup_database()
        
        self.current_proxy = None
        self.last_proxy_rotation = time.time()

    def setup_logging(self):
        log_file = f"logs/aethereye_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    def load_config(self):
        if not os.path.exists(self.config_path):
            if os.path.exists("config.example.yaml"):
                with open("config.example.yaml", "r") as f:
                    return yaml.safe_load(f)
            console.print("[bold red][!] CRITICAL CONFIGURATION FAULT: Specification layouts missing.[/bold red]")
            sys.exit(1)
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def setup_database(self):
        db_path = self.config.get("database", {}).get("path", "aethereye.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intelligence_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, vector TEXT,
                email TEXT UNIQUE, business_name TEXT, source_url TEXT, zone TEXT, proxy_used TEXT
            )
        """)
        conn.commit()
        return conn

    def get_total_collected_count(self):
        try:
            cursor = self.db_conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM intelligence_ledger")
            return cursor.fetchone()[0]
        except:
            return 0

    def rotate_proxy(self):
        proxy_cfg = self.config.get("proxies", {})
        if not proxy_cfg.get("enabled", False):
            return None
        now = time.time()
        interval = self.config.get("scraping_settings", {}).get("rotation_interval", 15)
        if now - self.last_proxy_rotation >= interval or self.current_proxy is None:
            proxy_list = proxy_cfg.get("list", [])
            if proxy_list:
                idx = int(now // interval) % len(proxy_list)
                self.current_proxy = proxy_list[idx]
                self.last_proxy_rotation = now
        return self.current_proxy

    def log_intel(self, vector, email, business, url, zone):
        proxy = self.current_proxy if self.current_proxy else "ENVIRONMENTAL/DIRECT"
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO intelligence_ledger (timestamp, vector, email, business_name, source_url, zone, proxy_used)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ts, vector, email.strip().lower(), business, url, zone, proxy))
            self.db_conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def render_summary_report(self):
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT timestamp, vector, email, business_name, zone, source_url, proxy_used FROM intelligence_ledger ORDER BY id DESC")
        rows = cursor.fetchall()

        if not rows:
            console.print("\n[bold yellow][!] Operational Registry Empty: No data records exist inside storage yet.[/bold yellow]")
            return

        table = Table(title="🔥 AETHEREYE MASTER INTELLIGENCE LEDGER REGISTRY", border_style="green", header_style="bold green", expand=True)
        table.add_column("Timestamp", style="dim")
        table.add_column("Vector Type", style="magenta")
        table.add_column("Extracted Target Address", style="white")
        table.add_column("Attribution Context", style="cyan")
        table.add_column("Geographic Zone", style="yellow")

        for r in rows:
            table.add_row(r[0], r[1], r[2], r[3], r[4])
        console.print("\n")
        console.print(table)

        export_choice = input(f"\n[?] Export global session parameters to master CSV log format? (y/N): ").strip().lower()
        if export_choice in ["y", "yes"]:
            export_file = "AETHEREYE_INTEL_MASTER.csv"
            with open(export_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["TIMESTAMP", "VECTOR", "TARGET_ADDRESS", "ATTRIBUTION_CONTEXT", "ZONE", "SOURCE_URL", "PROXY_USED"])
                writer.writerows(rows)
            console.print(Panel(f"[bold green][+] Forensic Export Completed Successful: Saved to {export_file}[/bold green]", border_style="green"))

    def display_dashboard_headers(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")
        proxy_status = self.current_proxy if self.current_proxy else "SYSTEM/PROXYCHAINS"
        total_intel = self.get_total_collected_count()
        grid.add_row(
            f"[bold cyan]AETHEREYE MASTER ORCHESTRATOR v9.5[/bold cyan] | [yellow]ROUTE: {proxy_status}[/yellow]",
            f"[bold magenta]LEDGER RECORDS: {total_intel} | SESSION: {self.session_id}[/bold magenta]"
        )
        console.print(Panel(grid, style="bright_black"))

    def show_menu(self):
        table = Table(show_header=False, box=None, expand=True)
        table.add_column(style="bold cyan", width=6)
        table.add_column(style="white")
        table.add_row("[01]", "GEO-HARVEST (Target Location Business Scraper) [Priority]")
        table.add_row("[02]", "DOMAIN & EMAIL HUNT (Identity Pattern Verification)")
        table.add_row("[03]", "SHODAN INFRA MAP (Active Port Topology Audit)")
        table.add_row("[04]", "REPORT LEAK LEDGER (Query Global Session Records)")
        table.add_row("[05]", "IMAGE FORENSICS (EXIF Extraction Engine)")
        table.add_row("[06]", "SOCIAL STALKER (Cross-Platform Identity Hunter)")
        table.add_row("[07]", "EMAIL CHECKER (Holehe-Style Account Detection)")
        table.add_row("[Q]", "TERMINATE FRAMEWORK RUNTIME")
        return Panel(table, title="[bold white]MISSION ORCHESTRATION CONTROL HUB[/bold white]", border_style="magenta")

def run_tui(framework):
    while True:
        framework.rotate_proxy()
        console.print("""[bold magenta]
   █████╗ ███████╗████████╗██╗  ██╗███████╗██████╗ ███████╗██╗   ██╗███████╗
  ██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝
  ███████║█████╗     ██║   ███████║█████╗  ██████╔╝█████╗   ╚████╔╝ █████╗  
  ██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗██╔══╝    ╚██╔╝  ██╔══╝  
  ██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║███████╗   ██║   ███████╗
  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝[/bold magenta]
       [bold red]>> MASTER INTELLIGENCE DISPATCH INFRASTRUCTURE NODE ONLINE <<[/bold red]""")
        framework.display_dashboard_headers()
        console.print(framework.show_menu())
        
        choice = input("\n[AETHER@INPUT]> ").strip().lower()
        if choice in ["01", "1"]:
            zone = input("\nEnter target geographic zone (e.g., Pristina): ").strip()
            if zone: asyncio.run(GeoHarvestEngine(framework).run(zone))
            input("\nPress Enter to return...")
        elif choice in ["02", "2"]:
            dom = input("\nEnter corporate domain (e.g., target.com): ").strip()
            if dom: asyncio.run(EmailHuntEngine(framework).run(dom))
            input("\nPress Enter to return...")
        elif choice in ["03", "3"]:
            ip = input("\nEnter target IP address (e.g., 8.8.8.8): ").strip()
            if ip: asyncio.run(ShodanInfraEngine(framework).run(ip))
            input("\nPress Enter to return...")
        elif choice in ["04", "4"]:
            framework.render_summary_report()
            input("\nPress Enter to return...")
        elif choice in ["05", "5"]:
            file_target = input("\nEnter path to target image file: ").strip()
            if file_target: ImageForensicsEngine(framework).run(file_target)
            input("\nPress Enter to return...")
        elif choice in ["06", "6"]:
            user_target = input("\nEnter profile username handle to trace: ").strip()
            if user_target: asyncio.run(SocialStalkerEngine(framework).run(user_target))
            input("\nPress Enter to return...")
        elif choice in ["07", "7"]:
            email_target = input("\nEnter target email address to check registers: ").strip()
            if email_target: asyncio.run(EmailCheckerEngine(framework).run(email_target))
            input("\nPress Enter to return...")
        elif choice == "q":
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AetherEye v9.5 Platform Core")
    parser.add_argument("--geo", type=str, help="Execute direct geo-harvest operations on location")
    args = parser.parse_args()
    
    core = AetherEyeCore()
    if args.geo:
        console.print(f"[bold yellow][*] Initializing Automated Pipeline Vector: {args.geo}[/bold yellow]")
        asyncio.run(GeoHarvestEngine(core).run(args.geo))
        core.render_summary_report()
    else:
        run_tui(core)