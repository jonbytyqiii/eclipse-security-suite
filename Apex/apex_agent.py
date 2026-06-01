#!/usr/bin/env python3
import subprocess
import os
import sys
import json
import socket
import time
from colorama import init, Fore, Style

init(autoreset=True)

# CONFIGURATION: Ensure this matches your local Windows operating machine IP channel
ECLIPSE_HOST = "192.168.0.25"  # <-- Put your Windows IP address here!
ECLIPSE_PORT = 9095

class ApexAgent:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_payload(self, p_type, data):
        """Encodes structured JSON payloads cleanly across the wire interface."""
        payload = {"type": p_type, "data": data}
        self.sock.sendall((json.dumps(payload) + "\n").encode('utf-8'))
        time.sleep(0.05) # Prevent socket buffer congestion saturation loops

    def run_command(self, cmd):
        try:
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return res.stdout.strip()
        except Exception:
            return ""

    def local_log(self, action_text):
        """Prints a localized monitoring indicator line on the Linux machine."""
        ts = datetime.datetime.now().strftime("%H:%M:%S") if 'datetime' in sys.modules else "AGENT"
        print(f"{Fore.GREEN}[+] [{ts}] Streaming Matrix Array: {Fore.WHITE}{action_text}")

    def collect_posture(self):
        print(Fore.RED + Style.BRIGHT + "=========================================================")
        print(Fore.YELLOW + "  APEX BEACON AGENT ACTIVE -> STREAMING TO WINDOWS CORE")
        print(Fore.RED + "=========================================================")
        
        # 1. System Info Gathering Phase
        self.local_log("Packaging host identification baselines...")
        self.send_payload("STATUS", "Gathering baseline kernel host data profiles...")
        whoami = self.run_command("whoami")
        uid_id = self.run_command("id")
        kernel = self.run_command("uname -r")
        hostname = self.run_command("hostname")
        os_name = self.run_command("cat /etc/os-release | grep 'PRETTY_NAME' | cut -d'=' -f2 | tr -d '\"'")
        
        self.send_payload("SYS_INFO", {
            "user": whoami, "uid": uid_id, "kernel": kernel, "hostname": hostname, "os_name": os_name
        })
        time.sleep(1)

        # 2. SUID Configuration Vectors跑
        self.local_log("Scanning local filesystem layers for SUID binaries...")
        self.send_payload("STATUS", "Scanning host configuration parameters for active SUID privilege bits...")
        suid_output = self.run_command("find / -perm -4000 -type f 2>/dev/null | head -35")
        for binary in suid_output.splitlines():
            if binary.strip():
                severity = "LOW"
                if any(x in binary for x in ["pkexec", "sudo", "su", "passwd"]):
                    severity = "MEDIUM"
                self.send_payload("FINDING", {"category": "SUID", "severity": severity, "item": binary.strip()})
        time.sleep(1)

        # 3. Linux Kernel File Capabilities Audit
        self.local_log("Querying process file capability mappings...")
        self.send_payload("STATUS", "Evaluating extended system process file capabilities flags (getcap)...")
        cap_output = self.run_command("getcap -r / 2>/dev/null | head -25")
        for line in cap_output.splitlines():
            if line.strip():
                severity = "MEDIUM"
                if "nmap" in line or "python" in line or "perl" in line:
                    severity = "HIGH"
                self.send_payload("FINDING", {"category": "CAPABILITY", "severity": severity, "item": line.strip()})
        time.sleep(1)

        # 4. Sudo Access Permissions Rules Mapping
        self.local_log("Evaluating active sudo configuration parameters...")
        self.send_payload("STATUS", "Analyzing system sudo execution policy tables (sudo -l)...")
        sudo_output = self.run_command("sudo -l 2>/dev/null")
        for line in sudo_output.splitlines():
            if "NOPASSWD" in line:
                self.send_payload("FINDING", {"category": "SUDO", "severity": "HIGH", "item": f"Passwordless Execution Allowed: {line.strip()}"})
            elif "(ALL : ALL) ALL" in line:
                self.send_payload("FINDING", {"category": "SUDO", "severity": "MEDIUM", "item": "User belongs to full sudo wildcard group structure"})
        time.sleep(1)

        # 5. Global Write Mapping Footprints
        self.local_log("Auditing system folders for world-writable exposures...")
        self.send_payload("STATUS", "Wiping sensitive core profile target paths for world-writable exposures...")
        etc_writable = self.run_command("find /etc -writable 2>/dev/null | head -5")
        for line in etc_writable.splitlines():
            if line.strip():
                sev = "HIGH" if ".service" in line or "passwd" in line or "shadow" in line else "MEDIUM"
                self.send_payload("FINDING", {"category": "WRITABLE", "severity": sev, "item": f"Writable System Configuration Path: {line.strip()}"})

        self.local_log("Transmission sequence complete. Closing session socket.")
        self.send_payload("STATUS", "Scan matrix completely finished. Compiling remote logs summary...")

if __name__ == "__main__":
    agent = ApexAgent(ECLIPSE_HOST, ECLIPSE_PORT)
    try:
        agent.connect()
        agent.collect_posture()
    except Exception as e:
        print(f"{Fore.RED}[!] Telemetry execution failure: {e}")