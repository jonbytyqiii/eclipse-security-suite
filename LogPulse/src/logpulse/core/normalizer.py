#!/usr/bin/env python3
import re
from datetime import datetime

class LogEvent:
    def __init__(self, raw_message, stream_type):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stream_type = stream_type
        self.raw_message = raw_message.strip()
        self.source_ip = "127.0.0.1"
        self.username = "system"
        self.event_type = "generic"
        self.normalize()

    def normalize(self):
        """Transforms variable format entries into standard normalized data signatures"""
        msg_lower = self.raw_message.lower()
        
        # Extract standard IPv4 signatures dynamically
        ips = re.findall(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', self.raw_message)
        if ips:
            self.source_ip = ips[0]

        # Ingestion stream normalizations
        if self.stream_type == "linux_auth":
            if "failed" in msg_lower or "auth_failure" in msg_lower or "authentication failure" in msg_lower:
                self.event_type = "auth_failure"
                user_match = re.search(r'for (?:invalid )?user (\w+)|user=(\w+)', msg_lower)
                if user_match:
                    self.username = next((u for u in user_match.groups() if u), "unknown")
            elif "accepted" in msg_lower or "success" in msg_lower:
                self.event_type = "auth_success"

        elif self.stream_type in ["nginx", "iis"]:
            self.event_type = "web_server_traffic"
            # Flag anomalous application tracks explicitly inside the normalizer
            if any(ind in msg_lower for ind in ["..%2f", "../", "..\\", "%2e%2e%2f"]):
                self.event_type = "web_attack_traversal"
            elif any(cmd in msg_lower for cmd in ["whoami", "cmd.exe", "/bin/sh", "shell_exec", "passthru", "eval"]):
                self.event_type = "web_attack_webshell"