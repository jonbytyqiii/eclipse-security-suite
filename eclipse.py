#!/usr/bin/env python3
import os
import sys
import time
import platform
from datetime import datetime
from rich import box
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.markup import escape  # Added to prevent parsing error crashes

# Initialize the High-End Console
console = Console()

class EclipseOS:
    def __init__(self):
        # Generates a unique session ID for the "Impossible" feel
        self.session_id = os.urandom(4).hex().upper()
        self.boot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def generate_header(self):
        banner = """
[bold magenta]
              ::::::::::  ::::::::  :::        ::::::::::: :::::::::  ::::::::  ::::::::::
             +:+        +:+    +:+ +:+            +:+     +:+    +:+ +:+    +:+ +:+        
            +:+        +:+        +:+            +:+     +:+    +:+ +:+        +:+        
           +#++:++#   +#+        +#+            +#+     +#++:++#+  +#++:++#++ +#++:++#   
          +#+        +#+        +#+            +#+     +#+              +#+ +#+        
         #+#        #+#    #+# #+#            #+#     #+#        #+#    #+# #+#        
        ##########  ########  ########## ########### ###         ########  ##########
[/bold magenta]
[bold white]      >> NEURAL-LINK ESTABLISHED // SESSION: {0} // PURPLE-TEAM ORCHESTRATOR <<[/bold white]
        """.format(self.session_id)
        return Panel(banner, style="magenta", border_style="bright_black")

    def generate_menu(self):
        table = Table(box=box.SQUARE, show_header=True, header_style="bold cyan", border_style="magenta", expand=True)
        table.add_column("VECTOR", justify="center", style="dim")
        table.add_column("ID", justify="center")
        table.add_column("MODULE NAME", style="bold white")
        table.add_column("ENVIRONMENT STATUS", justify="center")

        table.add_row("[red]OFFENSIVE[/red]", "01", "Eagle-Eye Network Infiltration", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[red]OFFENSIVE[/red]", "02", "Vortex Surface Raptor Engine (Subfinder x Dirbuster)", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[red]OFFENSIVE[/red]", "03", "ShatterEngine (RedDevil)", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[blue]DEFENSIVE[/blue]", "04", "LogPulse Forensic SIEM Engine", "[bold cyan]WIN/LINUX[/bold cyan]")
        table.add_row("[blue]DEFENSIVE[/blue]", "05", "Raven Stealth Shell", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[yellow]OSINT[/yellow]", "06", "AetherEye Total Intelligence Engine", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[white]SYSTEM[/white]", "07", "APEX Linux Audit Toolkit Listener", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[red]OFFENSIVE[/red]", "08", "BreachDeck Authentication Relay Suite", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[blue]DEFENSIVE[/blue]", "09", "DockSentry Container Risk Auditor", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[blue]DEFENSIVE[/blue]", "10", "Dexter Enterprise Static Forensics Core", "[bold cyan]WIN/PE STATIC[/bold cyan]")
        table.add_row("[red]OFFENSIVE[/red]", "11", "TitanBrute Comprehensive Authentication Suite", "[bold green]CROSS-OS[/bold green]")
        table.add_row("[white]SYSTEM[/white]", "00", "Terminate Session", "[dim]EXIT[/dim]")
        
        return Panel(table, title="[bold white]MISSION CONTROL[/bold white]", border_style="magenta")

    def get_sys_info(self):
        info = Table.grid(expand=True)
        info.add_row(f"[magenta]SYSTEM:[/magenta] ECLIPSE v2.0-STABLE")
        info.add_row(f"[magenta]BOOT:[/magenta] {self.boot_time}")
        info.add_row(f"[magenta]MODE:[/magenta] PURPLE TEAM (Hybrid)")
        info.add_row(f"[magenta]ENGINE:[/magenta] JIT/Numba Optimized")
        return Panel(info, title="[bold white]SYSTEM DATA[/bold white]", border_style="bright_black")

    def display_module_info(self, target_id):
        manifest = {
            "01": {
                "title": "EAGLE-EYE NETWORK INFILTRATION",
                "color": "cyan",
                "desc": "An automated asynchronous Layer 2/3 asset discovery mapping engine. "
                        "Utilizes custom socket crafting to identify live nodes, map open logical ports, "
                        "and fingerprint active operating systems within targeted internal networks."
            },
            "02": {
                "title": "VORTEX SURFACE RAPTOR ENGINE",
                "color": "red",
                "desc": "An automated, dual-phase attack surface pipeline mapping module. "
                        "Concurrently interrogates target domain networks to isolate hidden subdomains "
                        "and instantly cascades discovered hosts through an asynchronous multi-threaded "
                        "resource fuzzing layer to look for exposed directories and entry points."
            },
            "03": {
                "title": "SHATTERENGINE (REDDEVIL)",
                "color": "red",
                "desc": "A heavy-duty cryptographic processing and decoding matrix array. "
                        "Leverages multiprocessing and concurrent optimization models to crack "
                        "target credential hashes while handling dictionary mutations, custom mangling, "
                        "and mask layout parameter sequences natively."
            },
            "04": {
                "title": "LOGPULSE FORENSIC SIEM ENGINE",
                "color": "cyan",
                "desc": "An asynchronous threat hunting and event parsing mini-SIEM engine. Normalizes "
                        "incoming raw streams down to uniform event models and processes sliding time-window "
                        "correlation rules to map attacker techniques directly to the MITRE ATT&CK framework."
            },
            "05": {
                "title": "RAVEN STEALTH SHELL",
                "color": "yellow",
                "desc": "A low-observable reverse tactical access node and listener module. Establishes encrypted "
                        "socket bridges from remote assets back to Mission Control, bypassing typical application-layer "
                        "firewalls through tailored evasion headers and minimized memory footings."
            },
            "06": {
                "title": "AETHEREYE TOTAL INTELLIGENCE ENGINE",
                "color": "magenta",
                "desc": "A multi-vector public reconnaissance orchestrator. Automatically alternates proxy nodes "
                        "internally to gather deep-web corporate footprints. Integrates native Shodan infrastructure maps, "
                        "Hunter.io enterprise profiles, image EXIF forensics, Maigret username stalking, and "
                        "Holehe-style asynchronous email account checker verification algorithms."
            },
            "07": {
                "title": "APEX LINUX SECURITY AUDIT TOOLKIT",
                "color": "green",
                "desc": "A multi-threaded backend access verification listener matrix. Spins up a socket bridge "
                        "to ingest local system auditing metrics transmitted directly from deployed host beacon agents. "
                        "Tracks SUID vector anomalies, system file capabilities, and open global write paths securely."
            },
            "08": {
                "title": "BREACHDECK AUTHENTICATION RELAY SUITE",
                "color": "yellow",
                "desc": "An advanced subnet-wide cryptographic validation and traffic analysis deck. "
                        "Simulates active broadcast protocol auditing (LLMNR/NBT-NS) and evaluates "
                        "Active Directory authentication exposure risks including NTLM handshakes and "
                        "Kerberos service ticket (TGS-REP) structures."
            },
            "09": {
                "title": "DOCKSENTRY CONTAINER RISK AUDITOR",
                "color": "cyan",
                "desc": "A production-grade Container Security Posture Management (CSPM) tool. "
                        "Queries container runtime environments (Docker SDK/Podman CLI) directly to analyze namespace isolation, "
                        "privileged modes, mounted host sockets, user context capabilities, and resource scheduling limits."
            },
            "10": {
                "title": "DEXTER ENTERPRISE STATIC FORENSICS CORE",
                "color": "cyan",
                "desc": "An automated deep static file analysis and triage processing core. "
                        "Calculates multi-algorithmic cryptographic signatures, evaluates Shannon entropy limits, "
                        "decodes PE section structural anomalies, extracts embedded URI/IPv4 markers, "
                        "and compiles comprehensive JSON/HTML compliance forensics maps."
            },
            "11": {
                "title": "TITANBRUTE COMPREHENSIVE AUTHENTICATION SUITE",
                "color": "red",
                "desc": "An enterprise-grade dictionary authentication validation engine. "
                        "Supports concurrent credential testing verification routines against "
                        "Secure Shell (SSH), File Transfer Protocol (FTP), and standard HTTP Web Forms "
                        "to locate and document access policy vulnerabilities in lab targets."
            }
        }
        
        clean_id = target_id.zfill(2)
        
        if clean_id in manifest:
            m = manifest[clean_id]
            content = f"\n[bold white]VECTOR ARCHITECTURE:[/bold white]\n{m['desc']}\n\n"
            content += f"[dim]Operational Profile: Execute option '{clean_id}' directly to initialize execution array.[/dim]"
            
            console.print("\n")
            console.print(Panel(content, title=f"[bold white]INTEL BRIEF: {m['title']}[/bold white]", border_style=m['color']))
            input("\n[INFO VIEW] Press Enter to return to Mission Control...")
        else:
            console.print(f"\n[bold red][!] TARGET ENVELOPE '{target_id}' NOT FOUND IN CORE MANIFEST.[/bold red]")
            time.sleep(1.5)

    def display_module_help(self, target_id):
        help_manifest = {
            "01": {
                "title": "EAGLE-EYE NETWORK INFILTRATION",
                "color": "cyan",
                "usage": "Select Option [01] from main menu.\nInput targeted local network range or singular IP vector when prompted.",
                "example": "Target IP/Range: 192.168.1.1 or 192.168.1.0/24",
                "commands": "• --speed <1-5> : Adjust asynchronous execution delay loops.\n"
                            "• --udp          : Swap primary scan channels from TCP handshake synthesis to raw UDP packets.\n"
                            "• --ports <all>  : Toggle common top-100 matrix scanning vs comprehensive 65535 logical port checks.",
                "configs": "Modifies 'network_scanner.py' sockets locally."
            },
            "02": {
                "title": "VORTEX SURFACE RAPTOR ENGINE",
                "color": "red",
                "usage": "Select Option [02] from main menu.\nProvide base domain, subdomain lookup ledger, and destination path wordlists.",
                "example": "Base Target Domain: target.local\nSubdomain Wordlist: subs.txt\nDirectory Wordlist: common.txt",
                "commands": "• Multi-Phase Execution Cascade Pipeline (Automated Subfinder to Dirbuster flow).",
                "configs": "Core Class Module Path: raptor.py"
            },
            "03": {
                "title": "SHATTERENGINE (REDDEVIL)",
                "color": "red",
                "usage": "Select Option [03] from main menu to spin up the cryptographic matrix bridge.\nSupply raw password hash signatures along with targeted wordlists.",
                "example": "Hash: b09315ea09c6d3b5680094257f1f70e4\nWordlist Path: wordlist.txt",
                "commands": "• attack_mode 0   : Straightforward dictionary pass sequence.\n"
                            "• attack_mode 3   : Dynamic structural brute-force permutation scan.\n"
                            "• --rules <path> : Load custom rule mutations (leetspeak, capitalizing sequences, suffix appends).",
                "configs": "Pipeline Settings: RedDevil/config.yaml\nRule Sets: RedDevil/core/rules.py"
            },
            "04": {
                "title": "LOGPULSE FORENSIC SIEM ENGINE",
                "color": "cyan",
                "usage": "Select Option [04] to boot the log monitoring interface environment.\nSelect active log file streams to monitor incoming events dynamically.",
                "example": "Logs simulation file target path: LogPulse/logs/auth_sim.log",
                "commands": "• monitor_live   : Continuously tail targets using multi-threaded file monitors.\n"
                            "• analyze_mitre  : Filter parsed events directly against common adversary execution IDs.\n"
                            "• export_report  : Compile anomalies into an organized forensic analysis summary.",
                "configs": "Pipeline Settings: LogPulse/config.yaml\nSigma Rules: LogPulse/rules/"
            },
            "05": {
                "title": "RAVEN STEALTH SHELL (C2 COMMAND PLAYBOOK)",
                "color": "yellow",
                "usage": "Select Option [05] to bind low-observable listening nodes.\nConfigures local listening sockets to catch tactical inbound remote reverse connection callbacks.",
                "example": "Default listener bind parameter: Port 4444\nRAVEN-NODE-01> interact",
                "commands": "• interact       : Enter the active prompt array for the targeted remote endpoint.\n"
                            "  ├── \\[survey]   : Run automated system reconnaissance (OS patch level, user context, network maps).\n"
                            "  ├── \\[shell]    : Spawn a native terminal system command execution channel.\n"
                            "  ├── \\[chat]     : Open an encrypted plaintext communication bridge with the asset user.\n"
                            "  ├── \\[elevate]  : Trigger local privilege check scripts to verify admin/root vector tracking.\n"
                            "  └── \\[download] : Exfiltrate target file paths directly down to local workspace buffers.\n"
                            "• sys_info       : Query remote CPU cores, system architectures, and interface boundaries.\n"
                            "• terminate      : Close active background sockets cleanly to wipe memory footprints.",
                "configs": "Listener Core: raven_server.py"
            },
            "06": {
                "title": "AETHEREYE TOTAL INTELLIGENCE ENGINE",
                "color": "magenta",
                "usage": "Interactive Mode: Type '06' to open the sub-framework TUI layout dashboard.\nPipeline Mode: Type '06 <location_name>' directly from core console to trigger automated background harvesting profiles.",
                "example": "ECLIPSE@SYSTEM> 06 Pristina\nECLIPSE@SYSTEM> 06 Prizren",
                "commands": "• --shodan       : Query open network exposure profiles across corporate public routing spaces.\n"
                            "• --hunter       : Scrape linked enterprise contact email chains and account patterns.\n"
                            "• --verify       : Test accounts across common web databases asynchronously using email checks.",
                "configs": "Global Core Configurations: AetherEye/config.yaml\nDatabase Ledger: AetherEye/aethereye.db"
            },
            "07": {
                "title": "APEX REMOTE NETWORK LISTENER PACKAGE INTEGRATION",
                "color": "green",
                "usage": "Select Option [07] to launch the listening matrix on Windows. Once waiting, launch the agent binary payload from the remote target machine.",
                "example": "ECLIPSE@SYSTEM> 07\nTarget node launch string: python3 apex_agent.py",
                "commands": "• listener_port  : Network capture bind initialization (defaults to socket port 9095).\n"
                            "• ingest_stream  : Processes streaming real-time ANSI/Colorama log fragments directly from memory bounds.",
                "configs": "Listener Module Path: Apex/listener.py\nTarget Agent Script: Apex/apex_agent.py"
            },
            "08": {
                "title": "BREACHDECK AUTHENTICATION RELAY SUITE",
                "color": "yellow",
                "usage": "Select Option [08] from the main menu to initialize the traffic deck interface.\nSelect your network monitoring interface to begin live broadcast packet capture.",
                "example": "Captured Hashes Output Directory: BreachDeck/captured_hashes.txt",
                "commands": "• listen_loop    : Start up background Scapy packet-crafting socket listeners.\n"
                            "• filter_ntlm    : Focus visualization fields strictly on incoming NTLMSSP authentication frames.\n"
                            "• export_hashcat : Strip formatting headers and compile pure token lists optimized for hashcat rules.",
                "configs": "Interception Parameters: BreachDeck/config.yaml\nCore Module: BreachDeck/interceptor.py"
            },
            "09": {
                "title": "DOCKSENTRY CONTAINER RISK AUDITOR",
                "color": "cyan",
                "usage": "Select Option [09] from the primary terminal console view.\nAccept defaults to automatically analyze localized namespace constraints.",
                "example": "ECLIPSE@SYSTEM> 09\nECLIPSE@SYSTEM> docksentry",
                "commands": "• --target <type>: Manually force audit context mapping targets (auto, docker, podman).\n"
                            "• --export       : Force compile machine-readable JSON assets and HTML report dashboards.\n"
                            "• --quiet        : Mute post-audit code hardening compose snippet compilation engines.",
                "configs": "Audit Configuration Rules Matrix: DockSentry/rules.yaml"
            },
            "10": {
                "title": "DEXTER ENTERPRISE STATIC FORENSICS CORE",
                "color": "cyan",
                "usage": "Select Option [10] from the main orchestration terminal deck. Enter the targeted file path context or directory array when prompted.",
                "example": "Enter Target File or Directory path: C:\\Windows\\System32\\cmd.exe",
                "commands": "• Verbosity [0] : Minimum output telemetry tracking.\n"
                            "• Verbosity [1] : Standard automated security profiling view.\n"
                            "• Verbosity [2] : Deep Forensics layout matrix deployment.",
                "configs": "Module Target Script: dexter.py\nReport Asset Footprints: dexter_reports/"
            },
            "11": {
                "title": "TITANBRUTE COMPREHENSIVE AUTHENTICATION SUITE",
                "color": "red",
                "usage": "Select Option [11] from the main menu. Follow the prompt switches to input targeted host addresses, active protocols, user lists, and wordlists.",
                "example": "Select Vector Mode: [1] SSH, [2] FTP, [3] WEBFORM",
                "commands": "• Multi-Protocol Selector (SSH / FTP / HTTP Form Ingestion Engine).\n"
                            "• Live terminal connection validation logging arrays.",
                "configs": "Module Target Script: titanbrute/main.py"
            }
        }

        clean_id = target_id.zfill(2)
        if clean_id in help_manifest:
            h = help_manifest[clean_id]
            content = f"\n[bold white]📖 HOW TO OPERATE & EXECUTE:[/bold white]\n{h['usage']}\n\n"
            content += f"[bold white]🛠️  AVAILABLE PLAYBOOK COMMANDS:[/bold white]\n{h['commands']}\n\n"
            content += f"[bold white]🎯 RUNTIME EXAMPLES:[/bold white]\n{h['example']}\n\n"
            content += f"[bold white]⚙️ CONFIGURATION ASSETS:[/bold white]\n{h['configs']}\n"
            
            console.print("\n")
            console.print(Panel(content, title=f"[bold white]OPERATIONAL SCRIPT GUIDE: {h['title']}[/bold white]", border_style=h['color']))
            input("\n[HELP VIEW] Press Enter to return to Mission Control...")
        else:
            console.print(f"\n[bold red][!] HELP MANIFEST FOR ENTRY '{target_id}' NOT AVAILABLE.[/bold red]")
            time.sleep(1.5)

    def run(self):
        while True:
            console.clear()
            console.print(self.generate_header())
            console.print(self.get_sys_info())
            console.print(self.generate_menu())
            
            try:
                console.print("[dim]💡 Pro-Tip: Query blueprints using '[cyan]info <id>[/cyan]' or syntax guides via '[cyan]help <id>[/cyan]' (e.g., help 11)[/dim]")
                choice = console.input("\n[bold magenta]ECLIPSE@SYSTEM[/bold magenta]> ").strip()
                
                if choice == "00" or choice == "0":
                    console.print("[bold magenta][*] Terminating Neural Link... Goodbye.[/bold magenta]")
                    break
                
                if choice.lower().startswith("info "):
                    target_id = choice.split(" ", 1)[1].strip()
                    self.session_id = os.urandom(4).hex().upper()  # Re-randomize session for visual fidelity
                    self.display_module_info(target_id)
                elif choice.lower().startswith("help "):
                    target_id = choice.split(" ", 1)[1].strip()
                    self.display_module_help(target_id)
                else:
                    self.execute(choice)
                    
            except KeyboardInterrupt:
                console.print("\n[bold yellow][*] Sub-module context interrupted. Re-centering Control Matrix...[/bold yellow]")
                time.sleep(1.5)
                continue
            except Exception as e:
                console.print("[bold red][!] SYSTEM ERROR:[/bold red] ", end="")
                console.print(escape(str(e)))
                time.sleep(2)

    def execute(self, choice):
        try:
            # 1. NETWORK SCANNER (EAGLE EYE)
            if choice == "01" or choice == "1":
                console.print("[cyan][*] Initializing Eagle-Eye Scan via Global System Command...[/cyan]")
                os.system("eagleeye")
                input("\n[DONE] Press Enter to return to ECLIPSE...")
                
            # 2. VORTEX SURFACE RAPTOR ENGINE
            elif choice == "02" or choice == "2":
                console.print("[bold cyan][*][/bold cyan] Spinning up Vortex Surface Raptor Engine via Global System Command...")
                os.system("raptor")
                input("\n[DONE] Press Enter to return to ECLIPSE...")

            # 3. SHATTERENGINE (REDDEVIL)
            elif choice == "03" or choice == "3":
                console.print("[red][*] Initializing ShatterEngine Cryptographic Stations via Global System Command...[/red]")
                os.system("reddevil")
                input("\n[DONE] Session Terminated. Press Enter to return to ECLIPSE...")
                
            # 4. LOGPULSE FORENSIC SIEM ENGINE
            elif choice == "04" or choice == "4":
                console.print("[magenta][*] Initializing LogPulse SOC Threat Hunting Engine Cluster via Global System Command...[/magenta]")
                os.system("logpulse")
                input("\n[DONE] Pipeline Run Complete. Press Enter to return to ECLIPSE...")
                
            # 5. RAVEN STEALTH SHELL
            elif choice == "05" or choice == "5":
                console.print("[yellow][*] Opening Raven Stealth Server via Global System Command...[/yellow]")
                os.system('raven-nest')
                input("\n[DONE] Press Enter to return to ECLIPSE...")

            # 6. INTEGRATED AETHER_EYE OSINT SUITE
            elif choice.startswith("06") or choice.startswith("6"):
                parts = choice.split(" ", 1)
                if len(parts) > 1:
                    target_zone = parts[1].strip()
                    console.print(f"[magenta][*] Deploying Headless AetherEye Pipeline Mode for: {target_zone}...[/magenta]")
                    os.system(f'aethereye --geo "{target_zone}"')
                    input("\n[DONE] Pipeline Run Complete. Press Enter to return to ECLIPSE...")
                else:
                    console.print("[magenta][*] Deploying AetherEye OSINT Platform Hub Interactive TUI...[/magenta]")
                    os.system("aethereye")
                
            # 7. APEX REMOTE NETWORK LISTENER PACKAGE INTEGRATION
            elif choice == "07" or choice == "7":
                console.print("[bold green][*] Booting APEX Privilege Escalation Ingestion Deck...[/bold green]")
                os.system("apex-listener")
                    
            # 8. STANDALONE BREACHDECK AUTHENTICATION RELAY SUITE
            elif choice == "08" or choice == "8":
                console.print("[cyan][*] Deploying Standalone BreachDeck Subnet Interception Engine...[/cyan]")
                os.system("breachdeck")
                
            # 9. DOCKSENTRY CONTAINER RISK AUDITOR
            elif choice == "09" or choice == "9":
                console.print("[cyan][*] Deploying DockSentry Container Risk Auditing Cluster...[/cyan]")
                os.system("docksentry")
                
            # 10. DEXTER ENTERPRISE STATIC FORENSICS CORE INTEGRATION
            elif choice == "10":
                console.print("[bold cyan][*] Initializing Dexter Static Forensics Core Assembly Engine...[/bold cyan]\n")
                os.system("dexter")
                input("\n[DONE] Forensics Sequence Terminated. Press Enter to return to ECLIPSE...")

            # 11. TITANBRUTE SUITE DIRECTORY ROUTER
            elif choice == "11":
                console.print("[bold red][*] Ingesting TitanBrute Multi-Protocol Authentication Core...[/bold red]\n")
                os.system("titanbrute")
                input("\n[DONE] Infiltration Lab Complete. Press Enter to return to ECLIPSE...")

            # DEFAULT HANDLER
            else:
                console.print("[red][!] INVALID VECTOR OR COMMAND. Access Denied.[/red]")
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass

def main():
    ui = EclipseOS()
    ui.run()

if __name__ == "__main__":
    main()