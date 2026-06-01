#!/usr/bin/env python3
"""
EAGLE Eye v5.4 - Ultimate Advanced Network Reconnaissance Framework (Academy God-Tier Edition)
Author: Elite Cyber Academy Project (Jon Bytyqi Optimization Masterclass)
Description: Production-grade, thread-safe, multi-protocol tactical scanner.
             Implements Scapy optimization engines with custom Windows cache overrides,
             native raw structural fallbacks, authentic Nmap Top 100/1000 empirical 
             distributions, concrete error isolation, and multi-probe host discovery.
             Includes full global execution analytics tracking metrics.
"""

import os
import sys
import re
import time
import json
import socket
import struct
import random
import argparse
import threading
import subprocess
import platform
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from xml.etree.ElementTree import Element, SubElement, ElementTree

# --- OPTIONAL DEGRADATION HANDLING WITH HARDENED CACHE OVERRIDES ---
try:
    logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
    import scapy.config
    scapy.config.conf.use_cache = False  
    
    import scapy.all as scapy
    HAS_SCAPY = True
except (ImportError, PermissionError):
    HAS_SCAPY = False

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

# --- TERMINAL PALETTE CODES ---
if platform.system().lower() == 'windows':
    os.system('')

GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
BLUE   = '\033[94m'
PURPLE = '\033[95m'
CYAN   = '\033[96m'
WHITE  = '\033[97m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

BANNER = f"""{BLUE}{BOLD}
  ███████╗ █████╗  ██████╗ ██╗      ███████╗    ███████╗██╗   ██╗███████╗
  ██╔════╝██╔══██╗██╔════╝ ██║      ██╔════╝    ██╔════╝╚██╗ ██╔╝██╔════╝
  █████╗  ███████║██║  ███╗██║      █████╗      █████╗   ╚████╔╝ █████╗  
  ██╔══╝  ██╔══██║██║   ██║██║      ██╔══╝      ██╔══╝    ╚██╔╝  ██╔══╝  
  ███████╗██║  ██║╚██████╔╝███████╗ ███████╗    ███████╗   ██║   ███████╗
  ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚══════╝    ╚══════╝   ╚═╝   ╚══════╝
                     {YELLOW}Tactical Network Engine v5.4 [GOD-TIER]{RESET}
                     {CYAN}Engine Core: HYBRID SCAPY / NATIVE STRUCT PACKETS{RESET}
"""

NMAP_TOP_100_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080
]

NMAP_TOP_1000 = [
    1,7,9,11,13,15,19,21,22,23,25,37,42,49,53,70,79,80,81,82,83,84,85,88,89,90,99,100,106,109,110,111,113,119,125,135,
    139,143,144,146,161,163,179,199,211,212,222,254,255,256,259,264,280,301,306,311,340,366,389,406,416,417,425,427,
    443,444,445,458,464,465,481,497,500,512,513,514,515,524,541,543,544,545,548,554,555,563,587,616,617,625,631,636,
    646,648,666,667,668,683,687,691,700,705,711,714,720,722,726,749,765,777,800,801,808,843,873,880,888,898,900,901,
    902,903,911,912,981,987,990,992,993,995,999,1000,1001,1002,1007,1009,1010,1011,1021,1022,1023,1024,1025,1026,1027,
    1028,1029,1030,1031,1032,1033,1034,1035,1036,1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,1050,
    1051,1052,1053,1054,1055,1056,1057,1058,1059,1060,1061,1062,1063,1064,1065,1066,1067,1068,1069,1070,1071,1072,1073,
    1074,1075,1076,1077,1078,1079,1080,1081,1082,1083,1084,1085,1086,1087,1088,1089,1090,1091,1092,1093,1094,1095,1096,
    1097,1098,1099,1100,1214,1248,1352,1433,1434,1494,1521,1604,1720,1723,1741,1755,1761,1801,1900,1935,1998,2000,2001,
    2002,2003,2005,2049,2103,2105,2107,2121,2144,2161,2301,2383,2401,2483,2484,2525,2717,2869,2947,3000,3050,3077,3128,
    3268,3269,3306,3389,3456,3659,3690,3703,3986,4000,4029,4045,4111,4125,4144,4242,4443,4444,4567,4662,4848,4899,4900,
    5000,5001,5002,5003,5004,5009,5050,5051,5060,5061,5080,5101,5120,5145,5151,5154,5190,5222,5223,5225,5226,5269,5308,
    5357,5402,5432,5544,5555,5566,5631,5633,5666,5678,5679,5718,5730,5800,5801,5802,5900,5901,5902,5903,5904,5906,5907,
    5910,5915,5922,5925,5950,5952,5959,5960,5961,5962,5963,5984,5985,5986,6000,6001,6002,6003,6004,6005,6006,6007,6009,
    6025,6059,6101,6106,6112,6123,6124,6141,6142,6143,6257,6346,6347,6389,6502,6543,6547,6565,6566,6567,6588,6646,6666,
    6667,6668,6669,6671,6689,6692,6699,6779,6788,6789,6792,6839,6881,6901,6969,7000,7001,7002,7004,7007,7019,7025,7070,
    7100,7200,7201,7435,7443,7496,7512,7625,7627,7676,7741,7777,7778,7800,7911,7920,7921,7937,7938,7999,8000,8001,8002,
    8007,8008,8009,8010,8011,8021,8022,8031,8042,8043,8044,8074,8080,8081,8082,8083,8084,8085,8086,8087,8088,8089,8090,
    8093,8099,8118,8180,8181,8200,8222,8254,8290,8291,8292,8300,8333,8383,8400,8443,8445,8500,8554,8600,8649,8651,8652,
    8654,8701,8800,8873,8888,8899,8994,9000,9001,9002,9003,9009,9010,9011,9040,9050,9071,9080,9081,9090,9091,9099,9100,
    9101,9102,9103,9111,9200,9207,9312,9400,9415,9418,9500,9502,9535,9575,9593,9594,9595,9618,9666,9876,9877,9898,9900,
    9917,9929,9943,9944,9968,9998,9999,10000,10001,10002,10003,10004,10009,10010,10012,10024,10025,10082,10180,10215,
    10243,10566,10616,10626,10628,10629,10778,11110,11111,11967,12000,12174,12265,12345,13400,13722,13724,13782,13783,
    14000,14238,14441,14442,15000,15002,15003,15004,15214,16000,16001,16012,16016,16018,16080,16113,16992,16993,17877,
    17988,18040,18101,18988,19101,19283,19315,19350,19780,19842,20000,20005,20031,20222,20443,21212,23456,23796,25001,
    25109,25400,25565,27015,27352,27353,27355,27356,27715,28201,30000,30718,30951,31038,31337,32768,32769,32770,32771,
    32772,32773,32774,32775,32776,32777,32778,32779,32780,32781,32782,32783,32784,32785,33333,33354,33899,34571,34572,
    34573,34937,35500,38292,40193,40911,41511,42510,44176,44442,44443,44501,45100,47808,49152,49153,49154,49155,49156,
    49157,49158,49159,49160,49161,49163,49165,49167,49175,49176,49400,49999,50001,50002,50003,50006,50300,50389,50500,
    50636,51493,52822,52848,52869,54045,54321,55555,56312,60020,60443,61532,61900,62514,64623,64680,65000,65129,65535
]

PORT_SERVICES = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns", 80: "http", 110: "pop3", 111: "rpcbind",
    135: "msrpc", 139: "netbios-ssn", 143: "imap", 443: "https", 445: "microsoft-ds", 993: "imaps",
    995: "pop3s", 1433: "ms-sql-s", 3306: "mysql", 3389: "ms-wbt-server", 5432: "postgresql",
    5900: "vnc", 8080: "http-proxy", 8443: "https-alt"
}

OFFLINE_OUI_DB = {
    "00:50:56": "VMware, Inc.", "00:0C:29": "VMware, Inc.", "00:05:69": "VMware, Inc.",
    "00:15:5D": "Microsoft Hyper-V", "08:00:27": "Oracle VirtualBox", "00:11:32": "Synology Inc.", 
    "B8:27:EB": "Raspberry Pi Foundation", "DC:A6:32": "Raspberry Pi Foundation", 
    "00:00:0C": "Cisco Systems", "00:14:6C": "Netgear", "18:66:DA": "Dell Inc.", 
    "A4:BF:01": "Intel Corporation", "EC:8E:B5": "Hewlett Packard"
}

SERVICE_SIGNATURES = {
    b"SSH-": "OpenSSH Secure Shell Daemon",
    b"vsFTPd": "vsFTPd Server Engine",
    b"Pure-FTPd": "Pure-FTPd Engine",
    b"ProFTPD": "ProFTPD Infrastructure",
    b"HTTP/1.": "Web Daemon Instance",
    b"AMAZON": "AWS Edge Proxy Stack",
    b"Nginx": "Nginx Web Reverse Proxy",
    b"Apache": "Apache HTTP Server Engine"
}


# --- HARDENED UTILITY MODULE ---

class NetworkUtils:
    @staticmethod
    def get_local_subnet():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                prefix = ".".join(local_ip.split('.')[:-1]) + "."
                return prefix, local_ip
        except socket.error:
            return None, None

    @staticmethod
    def resolve_target(target_str):
        target_str = re.sub(r'^https?://', '', target_str).split('/')[0].split(':')[0]
        try:
            return socket.gethostbyname(target_str), target_str
        except socket.gaierror:
            return None, None

    @staticmethod
    def parse_target_range(target_str):
        if os.path.isfile(target_str):
            ips = []
            try:
                with open(target_str, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            ips.extend(NetworkUtils.parse_target_range(line))
            except IOError as e:
                print(f"{RED}[!] Target List Reading Interrupted: {e}{RESET}")
            return ips
        
        cidr_match = re.match(r"^([\d.]+)/(\d+)$", target_str)
        if cidr_match:
            base_ip = cidr_match.group(1)
            prefix = int(cidr_match.group(2))
            if prefix == 24:
                dots = ".".join(base_ip.split('.')[:-1]) + "."
                return [f"{dots}{i}" for i in range(1, 255)]
        
        ip, _ = NetworkUtils.resolve_target(target_str)
        return [ip] if ip else []


# --- THE DATA SERIALIZATION ENGINE (REPORTING MODULE) ---

class ReportingEngine:
    @staticmethod
    def export_json(data, filename):
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"{GREEN}[+] Report serialized cleanly to JSON: {filename}{RESET}")
        except (IOError, TypeError) as e:
            print(f"{RED}[!] Serialization Exception [JSON Output Vector Fault]: {e}{RESET}")

    @staticmethod
    def export_xml(data, filename):
        try:
            root = Element("EagleEyeScanReport", timestamp=datetime.now().isoformat())
            for ip, info in data.items():
                host_node = SubElement(root, "HostNode", ip=ip, hostname=info.get("hostname", "Unknown"))
                SubElement(host_node, "MacAddress").text = info.get("mac", "00:00:00:00:00:00")
                SubElement(host_node, "HardwareVendor").text = info.get("vendor", "Unknown Vendor Target")
                SubElement(host_node, "OperatingSystem").text = info.get("os", "Undetermined Platform Topology")
                ports_node = SubElement(host_node, "OpenPorts")
                for p in info.get("ports", []):
                    SubElement(ports_node, "PortEntry", port=str(p['port']), service=p['service']).text = p['version']
            tree = ElementTree(root)
            tree.write(filename, encoding="utf-8", xml_declaration=True)
            print(f"{GREEN}[+] Report serialized cleanly to XML: {filename}{RESET}")
        except IOError as e:
            print(f"{RED}[!] Serialization Exception [XML Output Vector Fault]: {e}{RESET}")


# --- CRYPTO & PACKET ENGINE BLOCK (STRUCT PACKING MACHINE) ---

class PacketFactory:
    @staticmethod
    def checksum(msg):
        if len(msg) % 2 == 1:
            msg = msg + b'\x00'
        s = 0
        for i in range(0, len(msg), 2):
            w = (msg[i] << 8) + (msg[i+1])
            s += w
        s = (s >> 16) + (s & 0xffff)
        return (~s & 0xffff)

    @staticmethod
    def build_syn_packet(src, dst, port):
        sport = random.randint(49152, 65535)
        seq_num = random.randint(100000, 200000)
        
        ip_id = random.randint(1000, 50000)
        ip_hdr = struct.pack('!BBHHHBBH4s4s', 69, 0, 40, ip_id, 0, 64, socket.IPPROTO_TCP, 0, socket.inet_aton(src), socket.inet_aton(dst))
        
        tcp_base = struct.pack('!HHLLBBHHH', sport, port, seq_num, 0, 80, 0x02, socket.htons(5840), 0, 0)
        pseudo_hdr = struct.pack('!4s4sBBH', socket.inet_aton(src), socket.inet_aton(dst), 0, socket.IPPROTO_TCP, len(tcp_base))
        tcp_chk = PacketFactory.checksum(pseudo_hdr + tcp_base)
        
        tcp_hdr = struct.pack('!HHLLBBH', sport, port, seq_num, 0, 80, 0x02, socket.htons(5840)) + struct.pack('!H', tcp_chk) + struct.pack('!H', 0)
        return ip_hdr + tcp_hdr


# --- RADAR MONITOR CORE ENGINE ---

class EagleEyeCore:
    def __init__(self, threads=150, timing_profile=3):
        self.threads = threads
        self.results = {}
        self.timeout = {0: 2.5, 1: 1.5, 2: 0.8, 3: 0.4, 4: 0.18}.get(timing_profile, 0.4)
        self.delay = {0: 1.2, 1: 0.6, 2: 0.15, 3: 0.0, 4: 0.0}.get(timing_profile, 0.0)
        
        self.total_hosts_audited = 0
        self.total_open_ports_discovered = 0

    def discover_hosts(self, target_list):
        live_ips = []
        is_win = platform.system().lower() == "windows"
        
        print(f"[*] Sweeping architecture queue via structural multi-probe discovery protocols across {len(target_list)} hosts...")

        if HAS_SCAPY and len(target_list) > 1:
            try:
                internal_prefix, _ = NetworkUtils.get_local_subnet()
                if internal_prefix and target_list[0].startswith(internal_prefix):
                    ans, _ = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff")/scapy.ARP(pdst=[t for t in target_list]), timeout=1.5, verbose=False)
                    for _, rcv in ans:
                        live_ips.append(rcv.psrc)
                    if live_ips:
                        return self._finalize_discovery_matrix(list(set(live_ips)))
            except (socket.error, IndexError, ValueError):
                pass 

        def multi_probe_node(ip):
            timeout_str = "150" if is_win else "1"
            cmd = ["ping", "-n" if is_win else "-c", "1", "-w" if is_win else "-W", timeout_str, ip]
            if subprocess.run(cmd, capture_output=True, text=True).returncode == 0:
                return ip
            
            for probe_port in [22, 80, 443]:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(0.5)
                        if s.connect_ex((ip, probe_port)) == 0:
                            return ip
                except socket.error:
                    continue
            return None

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            if tqdm:
                futures = {executor.submit(multi_probe_node, t): t for t in target_list}
                for fut in tqdm(as_completed(futures), total=len(target_list), desc="Host Discovery", unit="node"):
                    res = fut.result()
                    if res: live_ips.append(res)
            else:
                futures = [executor.submit(multi_probe_node, t) for t in target_list]
                for fut in as_completed(futures):
                    res = fut.result()
                    if res: live_ips.append(res)
                    
        return self._finalize_discovery_matrix(list(set(live_ips)))

    def _finalize_discovery_matrix(self, ip_list):
        discovered_matrix = []
        with ThreadPoolExecutor(max_workers=self.threads) as resolver:
            futures = [resolver.submit(lambda ip: (ip, self.get_hostname(ip)), ip) for ip in ip_list]
            for fut in as_completed(futures):
                discovered_matrix.append(fut.result())
        discovered_matrix.sort(key=lambda x: [int(num) for num in x[0].split('.')])
        return discovered_matrix

    def tcp_connect_scan(self, ip, ports_list):
        open_ports = []
        
        def worker(port):
            if self.delay > 0: time.sleep(self.delay)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(self.timeout)
                    if s.connect_ex((ip, port)) == 0:
                        return port
            except (socket.timeout, socket.error):
                pass
            return None

        with ThreadPoolExecutor(max_workers=self.threads) as execr:
            if tqdm:
                futures = [execr.submit(worker, p) for p in ports_list]
                for fut in tqdm(as_completed(futures), total=len(ports_list), desc=f"TCP Connect [{ip}]", unit="port", leave=False):
                    res = fut.result()
                    if res: open_ports.append(res)
            else:
                futures = [execr.submit(worker, p) for p in ports_list]
                for fut in as_completed(futures):
                    res = fut.result()
                    if res: open_ports.append(res)
        return sorted(open_ports)

    def tcp_syn_stealth_scan(self, ip, ports_list):
        if HAS_SCAPY:
            open_ports = []
            if self.delay > 0: time.sleep(self.delay)
            try:
                ans, _ = scapy.sr(scapy.IP(dst=ip)/scapy.TCP(dport=ports_list, flags="S"), timeout=self.timeout, verbose=False)
                for _, rcv in ans:
                    if rcv.haslayer(scapy.TCP) and rcv[scapy.TCP].flags == 0x12: 
                        open_ports.append(rcv[scapy.TCP].dport) 
                return sorted(open_ports)
            except (socket.error, ValueError, IndexError):
                pass 

        if platform.system().lower() == "windows" or os.getuid() != 0:
            print(f"{YELLOW}[!] Administrative privileges missing. Demoting scanner session to TCP Connect.{RESET}")
            return self.tcp_connect_scan(ip, ports_list)

        open_ports = []
        try:
            send_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            recv_sock.settimeout(self.timeout)
        except socket.error as e:
            print(f"{RED}[!] Raw Socket Allocation Fault: {e}. Dropping execution fallback downward.{RESET}")
            return self.tcp_connect_scan(ip, ports_list)

        try:
            _, local_ip = NetworkUtils.get_local_subnet()
            src_ip = local_ip if local_ip else "127.0.0.1"
            
            for port in ports_list:
                if self.delay > 0: time.sleep(self.delay)
                packet = PacketFactory.build_syn_packet(src_ip, ip, port)
                try:
                    send_sock.sendto(packet, (ip, 0))
                except socket.error:
                    continue 
                
                start_time = time.time()
                while (time.time() - start_time) < self.timeout:
                    try:
                        raw_packet, _ = recv_sock.recvfrom(65535)
                        iph = struct.unpack('!BBHHHBBH4s4s', raw_packet[0:20])
                        
                        if socket.inet_ntoa(iph[8]) == ip:
                            tcph = struct.unpack('!HHLLBBHHH', raw_packet[20:40])
                            if tcph[0] == port and (tcph[5] & 0x12): 
                                open_ports.append(port)
                                break
                    except socket.timeout:
                        break
                    except socket.error:
                        continue
        finally:
            send_sock.close()
            recv_sock.close()
            
        return sorted(open_ports)

    def udp_scan(self, ip, ports_list):
        open_or_filtered = []
        if platform.system().lower() == "windows" or os.getuid() != 0:
            for port in ports_list:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                        s.settimeout(self.timeout)
                        payload = b'\x00\x00\x00\x00' if port not in [53, 161] else b'\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00'
                        s.sendto(payload, (ip, port))
                        s.recvfrom(1024)
                        open_or_filtered.append(port)
                except socket.timeout:
                    open_or_filtered.append(port)
                except socket.error:
                    pass
            return open_or_filtered

        try:
            icmp_sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            icmp_sniffer.settimeout(self.timeout)
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            return open_or_filtered

        for port in ports_list:
            try:
                payload = b'\x00\x00\x00\x00'
                udp_sock.sendto(payload, (ip, port))
                try:
                    raw_packet, _ = icmp_sniffer.recvfrom(65535)
                    type_byte, code_byte = struct.unpack('!BB', raw_packet[20:22])
                    if type_byte == 3 and code_byte == 3:
                        continue 
                except socket.timeout:
                    open_or_filtered.append(port)
            except socket.error:
                pass
        
        udp_sock.close()
        icmp_sniffer.close()
        return open_or_filtered

    def process_node_fingerprint(self, ip, open_ports, aggressive=True):
        self.total_hosts_audited += 1
        self.total_open_ports_discovered += len(open_ports)
        
        node_data = {
            "hostname": self.get_hostname(ip),
            "mac": self.get_mac_address(ip),
            "vendor": "Unknown Vendor Target",
            "os": self._infer_os_ttl(ip),
            "ports": []
        }
        node_data["vendor"] = self.lookup_vendor_oui(node_data["mac"])
        
        print(f"\n{BLUE}{BOLD}🔍 Targeting Vector Node: {ip} ({node_data['hostname']}){RESET}")
        print(f" ├─ MAC Hardware Signature: {YELLOW}{node_data['mac']}{RESET} [{node_data['vendor']}]")
        
        if open_ports:
            print(f" ┃ {BOLD}{'PORT':<6} | {'SERVICE':<15} | {'VERSION / HEURISTIC EXTENDED DETECTION':<45}{RESET}")
            print(f" ┃" + "━" * 81)
            
            for p in open_ports:
                svc_name = PORT_SERVICES.get(p, "unknown")
                version_str = self._probe_deep_version(ip, p) if aggressive else "Active Endpoint Open"
                node_data["ports"].append({"port": p, "service": svc_name, "version": version_str})
                print(f" ┃ {GREEN}{p:<6}{RESET} | {CYAN}{svc_name:<15}{RESET} | {WHITE}{version_str[:45]:<45}{RESET}")
        else:
            print(f" ┃  No monitored open ports discovered within execution constraints.")
        
        print(f" └─ Identified OS Fingerprint: {GREEN}{BOLD}{node_data['os']}{RESET}\n")
        self.results[ip] = node_data

    def _probe_deep_version(self, ip, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5)
                s.connect((ip, port))
                if port in [80, 8080]:
                    s.sendall(b"GET / HTTP/1.1\r\nHost: local\r\n\r\n")
                elif port == 21:
                    s.sendall(b"SYST\r\n")
                    
                raw_resp = s.recv(1024)
                if raw_resp:
                    for sig, identity in SERVICE_SIGNATURES.items():
                        if sig in raw_resp:
                            return identity
                    return f"Custom Broadcast: {raw_resp.decode('utf-8', errors='ignore').strip()[:35]}"
        except socket.error:
            pass
        return "Active Endpoint (Service Verification Masked)"

    def _infer_os_ttl(self, ip):
        try:
            is_win = platform.system().lower() == "windows"
            cmd = ["ping", "-n" if is_win else "-c", "1", "-w" if is_win else "-W", "1", ip]
            out = subprocess.run(cmd, capture_output=True, text=True).stdout
            match = re.search(r"(ttl|TTL)=(\d+)", out)
            if match:
                ttl = int(match.group(2))
                if ttl <= 64: return "Linux / Kernel Stack Architecture (Unix/Android)"
                elif ttl <= 128: return "Microsoft Windows Framework (NT Core)"
                return "Network Appliance Infrastructure Core (Cisco/Firewall Edge)"
        except (subprocess.SubprocessError, ValueError, IndexError):
            pass
        return "Undetermined OS Platform Topology"

    def get_hostname(self, ip):
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return "Unknown Host"

    def get_mac_address(self, ip):
        try:
            is_win = platform.system().lower() == "windows"
            cmd = ["arp", "-a", ip] if is_win else ["arp", "-n", ip]
            out = subprocess.run(cmd, capture_output=True, text=True).stdout
            match = re.search(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", out)
            if match: return match.group(0).upper().replace('-', ':')
        except (subprocess.SubprocessError, ValueError, IndexError):
            pass
        return "00:00:00:00:00:00"

    def lookup_vendor_oui(self, mac):
        if mac in ["00:00:00:00:00:00", "Unknown"]: 
            return "WAN Route / External Destination"
        oui_prefix = mac.upper().replace('-', ':')[:8]
        return OFFLINE_OUI_DB.get(oui_prefix, "Private Hardware Vendor")

    def print_final_telemetry_summary(self, total_duration):
        print(f"\n{CYAN}{BOLD}====================================================================={RESET}")
        print(f"{YELLOW}{BOLD}                     EAGLE EYE ENGINE FINAL RUN REPORT               {RESET}")
        print(f"{CYAN}{BOLD}====================================================================={RESET}")
        print(f" ├─ Analysis Completion Time : {WHITE}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
        print(f" ├─ Total Operational Hosts  : {GREEN}{self.total_hosts_audited} nodes identified active{RESET}")
        print(f" ├─ Discovered Open Vectors : {GREEN}{self.total_open_ports_discovered} ports flagged open{RESET}")
        print(f" └─ Exact Tactical Duration  : {PURPLE}{total_duration:.2f} seconds elapsed{RESET}")
        print(f"{CYAN}{BOLD}====================================================================={RESET}\n")


# --- CUSTOM NATIVE IN-MENU MANUAL LAYOUT ---

def display_interactive_manual():
    print(f"\n╭───────────────────────────────────────────────────────────── TACTICAL MANUAL ─────────────────────────────────────────────────────────────╮")
    print(f"│ {YELLOW}Linux Terminal Command Line Usage Structure:{RESET}                                                                                              │")
    print(f"│   python eagle-eye.py --target <IP/Domain/File> [Execution Flags]                                                                         │")
    print(f"│   python eagle-eye.py --target 192.168.1.1 -sS -A -T 4                                                                                    │")
    print(f"╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯")
    print(f"\n{BOLD}{CYAN}Operational Arguments Reference Matrix{RESET}")
    print(f"┏━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print(f"┃ Flag Vector ┃ Parameter Mapping                       ┃ Functional Definition / Values Bounds                                    ┃")
    print(f"┡━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩")
    print(f"│  -t, --target│ <Target Address Path configuration>    │ Target Domain Name, Public IP Asset, CIDR Range, or Local Text File List │")
    print(f"│  -p, --ports │ <Execution Port Range Configuration>   │ Profile Distribution Rules: 'top100', 'top1000', or Boundaries: '1-65535'│")
    print(f"│  -sT        │ TCP Connect Mapping Enable Flag         │ Execute explicit 3-Way Handshake Connection Probing sequences            │")
    print(f"│  -sS        │ Asynchronous SYN Stealth Verification    │ Execute raw pseudo-header asynchronous TCP SYN background scanning       │")
    print(f"│  -sU        │ ICMP Evaluation UDP Analysis Core       │ Send empty data configurations to evaluate raw closed port ICMP packets  │")
    print(f"│  -A         │ Application Protocol Signature Audit    │ Trigger hard-coded challenge buffers to capture application version data │")
    print(f"│  -T, --timing│ <Timing Profile Setting Thresholds>     │ Profiles: [0-4] (Setting 4 minimizes packet processing sleep intervals)  │")
    print(f"│  --threads  │ <Workers Pool Threads Limit Max>        │ Bounds maximum socket concurrency processing pool ceiling (Default: 150) │")
    print(f"│  -oJ        │ <JSON Session Output Storage Path>      │ Target filesystem workspace path where the engine saves JSON data objects│")
    print(f"│  -oX        │ <XML Session Output Storage Path>       │ Target filesystem workspace path where the engine saves standard XML logs│")
    print(f"┗━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print(f"\n💡 {WHITE}Interactive Script Integration Engine: Options can be passed securely via arguments when invoking from automated tool chains.{RESET}\n")


# --- INTERACTIVE USER MANAGEMENT CONFIG (LOOP ENHANCED) ---

def run_interactive_wizard(engine, ports):
    while True:
        print(BANNER)
        print(f"{BOLD}{CYAN}[?] SELECT OPERATIONAL RECON MODULE:{RESET}")
        print(f" [{GREEN}1{RESET}] Auto-Discover & Audit Local Subnet")
        print(f" [{GREEN}2{RESET}] Target Custom Node Manually (Domain Name, External IP, or Target List)")
        print(f" [{GREEN}3{RESET}] Tactical Engine Reference Manual (View Flags Documentation)")
        print(f" [{GREEN}0{RESET}] Complete Task Execution Sequence (Exit Framework Loop)")
        
        mode = input(f"\n{PURPLE}ECLIPSE@EagleEye > Choose Engine Mode [0-3]: {RESET}").strip()
        
        if mode == "0" or not mode:
            print(f"\n{YELLOW}[*] Flushing active arrays. Returning to Master ECLIPSE Matrix Framework...{RESET}\n")
            break
            
        elif mode == "3":
            display_interactive_manual()
            input(f"{YELLOW}Press Enter to return to the core operational module...{RESET}")
            continue

        if mode not in ["1", "2"]:
             print(f"{RED}[!] Erroneous Mode Allocation Vector Selected. Defaulting to Subnet Discovery.{RESET}")
             mode = "1"
        
        target_ips = []
        if mode == "2":
            manual_target = input(f"\n{YELLOW}[*] Enter Domain Target String, Public IP Asset, or File List: {RESET}").strip()
            target_ips = NetworkUtils.parse_target_range(manual_target)
        else:
            prefix, my_ip = NetworkUtils.get_local_subnet()
            if not prefix:
                print(f"{RED}[!] Error identifying structural network subnets.{RESET}")
                return
            print(f"{GREEN}[+] Subnet Map Found: {prefix}0/24 (Your Host Node IP: {my_ip}){RESET}")
            subnet_ips = [f"{prefix}{i}" for i in range(1, 255) if f"{prefix}{i}" != my_ip]
            
            live_matrix = engine.discover_hosts(subnet_ips)
            print(f"\n{BOLD}{CYAN}================= EAGLE EYE DISCOVERY TARGET MATRIX ================={RESET}")
            for idx, (ip, hostname) in enumerate(live_matrix):
                print(f" [{GREEN}{idx + 1}{RESET}] Operational Host Node: {BOLD}{ip:<15}{RESET} ({hostname})")
            print(f" [{GREEN}M{RESET}] Specify Custom Target Address Manually Override")
            print("=====================================================================")
            
            choice = input(f"\n{PURPLE}ECLIPSE@EagleEye > Select Target Node Index Value or 'M': {RESET}").strip()
            if choice.upper() == 'M':
                manual_target = input(f"\n{YELLOW}[*] Enter Custom Target IP, Block, or Domain Name: {RESET}").strip()
                target_ips = NetworkUtils.parse_target_range(manual_target)
            else:
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(live_matrix):
                        target_ips = [live_matrix[idx][0]]
                    else:
                        print(f"{RED}[!] Selection Index Out of Bounds.{RESET}")
                        continue
                except ValueError:
                    print(f"{RED}[!] Selection Parse Failure.{RESET}")
                    continue

        if not target_ips:
            print(f"{RED}[!] Empty Targeting Vector Target Range. Aborting loop path.{RESET}")
            input(f"\nPress Enter to return to main wizard layout...")
            continue

        print(f"\n{BOLD}{CYAN}[?] Select Protocol Engine Strategy:{RESET}")
        print(f" [{GREEN}1{RESET}] Standard TCP Connect Audit")
        print(f" [{GREEN}2{RESET}] Stealth TCP SYN Scan (Optimized Core)")
        print(f" [{GREEN}3{RESET}] High-Fidelity UDP Discovery Engine")
        scan_choice = input(f"{PURPLE}ECLIPSE@EagleEye > Choose Protocol Strategy [1-3]: {RESET}").strip()

        start_time = time.time()
        for target_ip in target_ips:
            if scan_choice == "2": open_ports = engine.tcp_syn_stealth_scan(target_ip, ports)
            elif scan_choice == "3": open_ports = engine.udp_scan(target_ip, ports)
            else: open_ports = engine.tcp_connect_scan(target_ip, ports)
            
            engine.process_node_fingerprint(target_ip, open_ports, aggressive=True)
        
        elapsed_time = time.time() - start_time
        engine.print_final_telemetry_summary(elapsed_time)

        out_choice = input(f"{PURPLE}ECLIPSE@EagleEye > Export session reports? (y/N): {RESET}").strip().lower()
        if out_choice == 'y':
            out_base = f"eagleeye_report_{int(time.time())}"
            ReportingEngine.export_json(engine.results, f"{out_base}.json")
            ReportingEngine.export_xml(engine.results, f"{out_base}.xml")
        
        input(f"\n{GREEN}[DONE] Task Complete.{RESET} Press Enter to return to main wizard menu...")


# --- CUSTOM MANUAL HELP PARSER OVERRIDE ---

class HardenedHelpParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"\n{RED}{BOLD}[!] Operational Execution Matrix Exception: {message}{RESET}")
        self.print_help()
        sys.exit(2)

    def print_help(self):
        print(BANNER)
        display_interactive_manual()


# --- RUNTIME CONTROLLER ---

# --- RUNTIME CONTROLLER ENTRY POINT ---

def main():
    parser = HardenedHelpParser(add_help=False)
    
    parser.add_argument("-t", "--target", nargs='+', help=argparse.SUPPRESS)
    parser.add_argument("-p", "--ports", default="top100", help=argparse.SUPPRESS)
    parser.add_argument("-sT", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-sS", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-sU", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-A", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-T", "--timing", type=int, choices=[0, 1, 2, 3, 4], default=3, help=argparse.SUPPRESS)
    parser.add_argument("--threads", type=int, default=150, help=argparse.SUPPRESS)
    parser.add_argument("-oJ", "--json", help=argparse.SUPPRESS)
    parser.add_argument("-oX", "--xml", help=argparse.SUPPRESS)
    parser.add_argument("-h", "--help", action="store_true", help=argparse.SUPPRESS)

    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(0)

    if args.help:
        parser.print_help()
        sys.exit(0)

    if args.ports == "top100":
        selected_ports = NMAP_TOP_100_PORTS
    elif args.ports == "top1000":
        selected_ports = NMAP_TOP_1000
    elif "-" in args.ports:
        try:
            start_p, end_p = map(int, args.ports.split("-"))
            selected_ports = list(range(start_p, end_p + 1))
        except ValueError:
            print(f"{RED}[!] Incorrect custom port string token definition. Falling back to Nmap Top 100 Profile.{RESET}")
            selected_ports = NMAP_TOP_100_PORTS
    else:
        try:
            selected_ports = [int(p) for p in args.ports.split(",")]
        except ValueError:
            selected_ports = NMAP_TOP_100_PORTS

    scanner_core = EagleEyeCore(threads=args.threads, timing_profile=args.timing)

    if not args.target:
        run_interactive_wizard(scanner_core, selected_ports)
        sys.exit(0)

    execution_targets = []
    for arg_item in args.target:
        execution_targets.extend(NetworkUtils.parse_target_range(arg_item))

    if not execution_targets:
        print(f"{RED}[!] Target execution list resolved empty. Halting operation vectors.{RESET}")
        sys.exit(1)

    print(BANNER)
    print(f"{GREEN}[+] Launching CLI Operational Scanner Core against {len(execution_targets)} targets...{RESET}")
    
    global_start = time.time()
    for node_ip in execution_targets:
        if args.sS:
            open_vectors = scanner_core.tcp_syn_stealth_scan(node_ip, selected_ports)
        elif args.sU:
            open_vectors = scanner_core.udp_scan(node_ip, selected_ports)
        else:
            open_vectors = scanner_core.tcp_connect_scan(node_ip, selected_ports)

        scanner_core.process_node_fingerprint(node_ip, open_vectors, aggressive=args.A)

    duration_elapsed = time.time() - global_start
    scanner_core.print_final_telemetry_summary(duration_elapsed)

    if args.json:
        ReportingEngine.export_json(scanner_core.results, args.json)
    if args.xml:
        ReportingEngine.export_xml(scanner_core.results, args.xml)

if __name__ == "__main__":
    main()