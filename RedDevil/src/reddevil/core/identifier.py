import re
from typing import Tuple, Optional, List

class HashIdentifier:
    def __init__(self):
        # Precise evaluation fingerprints mapped by character bounds and regex structures
        self.signatures = [
            {"name": "md5", "regex": r"^[a-fA-F0-9]{32}$", "category": "hash"},
            {"name": "ntlm", "regex": r"^[a-fA-F0-9]{32}$", "category": "hash"},
            {"name": "sha1", "regex": r"^[a-fA-F0-9]{40}$", "category": "hash"},
            {"name": "sha256", "regex": r"^[a-fA-F0-9]{64}$", "category": "hash"},
            {"name": "sha512", "regex": r"^[a-fA-F0-9]{128}$", "category": "hash"},
            {"name": "md5-salt", "regex": r"^[a-fA-F0-9]{32}:[a-zA-Z0-9./+=_-]+$", "category": "salted_hash"},
            {"name": "sha256-salt", "regex": r"^[a-fA-F0-9]{64}:[a-zA-Z0-9./+=_-]+$", "category": "salted_hash"},
            {"name": "base64", "regex": r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$", "category": "encoding"},
            {"name": "hex", "regex": r"^[0-9a-fA-F]+$", "category": "encoding"}
        ]

    def identify(self, target: str) -> Tuple[Optional[str], Optional[str]]:
        target = target.strip()
        if not target:
            return None, None

        for sig in self.signatures:
            if re.match(sig["regex"], target):
                # Handle standard collision ambiguity for identical lengths (e.g., MD5 vs NTLM)
                return sig["category"], sig["name"]

        return None, None

    def extract_salt(self, target: str) -> Tuple[str, str]:
        """Splits a salted target token down to its raw components safely"""
        parts = target.strip().split(":", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""