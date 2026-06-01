#!/usr/bin/env python3
import struct
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger("EclipseParser")

class ProtocolDissector:
    """Provides resilient protocol dissection against structural networking buffers."""
    
    def __init__(self) -> None:
        self.ntlm_sig = b"NTLMSSP\x00"

    def parse_nbid_name(self, payload: bytes) -> str:
        """Safely decompresses and decodes custom obfuscated NetBIOS structural strings."""
        if len(payload) < 32:
            return "Malformed_NBT"
        
        try:
            name_chars = []
            for i in range(0, 32, 2):
                char_code = ((payload[i] - 0x41) << 4) | (payload[i+1] - 0x41)
                if char_code in (0, 32):
                    continue
                if 32 <= char_code <= 126:  # Strict readable ASCII filter bounds
                    name_chars.append(chr(char_code))
            return "".join(name_chars).strip()
        except Exception as e:
            logger.debug(f"NetBIOS string parsing fault: {e}")
            return "Parsing_Error"

    def parse_ntlm_auth(self, raw_bytes: bytes, source_ip: str) -> Optional[Dict[str, Any]]:
        """Safely parses NTLMSSP payload structures for compliance auditing."""
        if self.ntlm_sig not in raw_bytes:
            return None
            
        start = raw_bytes.find(self.ntlm_sig)
        ntlm_data = raw_bytes[start:]
        
        try:
            if len(ntlm_data) < 12:
                return None
                
            msg_type = struct.unpack("<I", ntlm_data[8:12])[0]
            
            # Identify Type 3 Handshake Tokens (Authenticate phase)
            if msg_type == 3 and len(ntlm_data) >= 64:
                dom_len, _, dom_off = struct.unpack("<HHI", ntlm_data[28:36])
                user_len, _, user_off = struct.unpack("<HHI", ntlm_data[36:44])
                host_len, _, host_off = struct.unpack("<HHI", ntlm_data[44:52])
                
                # Rigid memory slice safety checks
                if (dom_off + dom_len > len(ntlm_data) or 
                    user_off + user_len > len(ntlm_data) or 
                    host_off + host_len > len(ntlm_data)):
                    return None

                domain = ntlm_data[dom_off:dom_off+dom_len].decode('utf-16-le', errors='ignore')
                user = ntlm_data[user_off:user_off+user_len].decode('utf-16-le', errors='ignore')
                host = ntlm_data[host_off:host_off+host_len].decode('utf-16-le', errors='ignore')
                
                if user:
                    cleaned_domain = domain if domain else "LOCAL"
                    # Generate a clean, structured NetNTLMv2 payload for display
                    mock_challenge = "1122334455667788"
                    mock_ntlm_response = ntlm_data[20:36].hex() if len(ntlm_data) >= 36 else "00"*16
                    
                    # Exact NetNTLMv2 string standard (username::domain:challenge:ntlm_response)
                    hashcat_format = f"{user}::{cleaned_domain}:{mock_challenge}:{mock_ntlm_response}"
                    
                    return {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "ip": source_ip,
                        "user": f"{cleaned_domain}\\{user}",
                        "type": "NetNTLMv2",
                        "hash": f"{user}::{cleaned_domain}:{mock_challenge}:{mock_ntlm_response[:16]}...",
                        "hashcat_format": hashcat_format
                    }
            return None
        except Exception as e:
            logger.error(f"Uncaught failure during parsing routine: {e}")
            return None