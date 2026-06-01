#!/usr/bin/env python3
import os
import time
import socket
import queue
import logging
from typing import Optional

logger = logging.getLogger("EclipseAuditor")

# Safe validation wrapper for underlying platform drivers
try:
    from scapy.all import sniff, UDP, Raw, DNS, DNSQR, IP, conf
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

class LivePacketAuditor:
    def __init__(self, interface: Optional[str] = None, callback_queue: Optional[queue.Queue] = None, loopback_port: int = 4445):
        self.interface = interface
        self.queue = callback_queue if callback_queue is not None else queue.Queue()
        self.loopback_port = loopback_port
        self.running = False

    def verify_capture_environment(self) -> tuple[bool, str]:
        """Validates that the underlying operating system environment has the necessary capture elements."""
        if not SCAPY_AVAILABLE:
            return False, "The Scapy library is missing or misconfigured in this Python environment."
        
        if os.name == 'nt':
            try:
                # Scapy dynamically links to packet capture backends on initialization. 
                # If the interfaces dictionary is flatly empty, Npcap or WinPcap is missing.
                if not conf.ifaces or len(conf.ifaces) == 0:
                    return False, "No underlying packet capture interfaces found. Ensure Npcap is installed."
            except Exception as e:
                return False, f"Failed to probe Windows network interface structures: {e}"
                
        return True, "Environment validated successfully."

    def process_frame(self, packet) -> None:
        """Processes live captures out of raw frame buffers securely."""
        try:
            source_ip = packet[IP].src if packet.haslayer(IP) else "127.0.0.1"
            
            # 1. LLMNR Broadcast Inbound Capture (UDP 5355)
            if packet.haslayer(UDP) and packet[UDP].dport == 5355:
                if packet.haslayer(DNS) and packet[DNS].qr == 0:
                    if packet.haslayer(DNSQR):
                        q_name = packet[DNSQR].qname.decode('utf-8', errors='ignore').strip('.')
                        self.queue.put({"type": "LLMNR", "ip": source_ip, "payload": q_name})
                        return

            # 2. NetBIOS Name Service Inbound Capture (UDP 137)
            if packet.haslayer(UDP) and packet[UDP].dport == 137:
                if packet.haslayer(Raw):
                    raw_payload = packet[Raw].load
                    if len(raw_payload) > 12:
                        from modules.parser import ProtocolDissector
                        dissector = ProtocolDissector()
                        nbt_name = dissector.parse_nbid_name(raw_payload[12:])
                        self.queue.put({"type": "NBTNS", "ip": source_ip, "payload": nbt_name})
                        return
        except Exception as e:
            logger.debug(f"Error handling live packet frame: {e}")

    def start_loop(self) -> None:
        """Starts real-world network parsing after verifying capture driver state."""
        env_ok, env_msg = self.verify_capture_environment()
        if not env_ok:
            logger.error(f"Auditor initialization rejected: {env_msg}")
            # Notify the main thread via the safe event loop queue
            self.queue.put({"type": "ENV_ERROR", "payload": env_msg})
            self.running = False
            return

        self.running = True
        while self.running:
            try:
                sniff(iface=self.interface, prn=self.process_frame, store=0, timeout=1)
            except Exception as e:
                logger.error(f"Recoverable exception during socket read loop: {e}")
                time.sleep(2)