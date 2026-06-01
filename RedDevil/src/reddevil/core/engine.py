import os
import time
import hashlib
import base64
import sqlite3
import itertools
import urllib.parse
from typing import Optional, List, Dict, Generator, Tuple
from concurrent.futures import ProcessPoolExecutor, as_completed

# Modern Heavy Cryptographic Bindings
import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

# --- MULTIPROCESSING CORE WORKER ROUTINES ---
def _init_worker():
    """Silence keyboard interrupts in child worker processes"""
    import signal
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def _check_chunk_slice(args: Tuple[List[str], str, str, str]) -> Optional[str]:
    """Worker function executed in separate processes"""
    try:
        candidates, target, algorithm, salt = args
        target_lower = target.lower()

        for candidate in candidates:
            if algorithm == "bcrypt":
                if bcrypt.checkpw(candidate.encode('utf-8'), target.encode('utf-8')):
                    return candidate
            elif algorithm == "argon2":
                try:
                    if PasswordHasher().verify(target, candidate):
                        return candidate
                except Exception:
                    pass
            elif algorithm == "pbkdf2_sha256":
                try:
                    parts = target.split('$')
                    if len(parts) == 4:
                        key = hashlib.pbkdf2_hmac('sha256', candidate.encode('utf-8'),
                                                parts[2].encode('utf-8'), int(parts[1]))
                        if key.hex() == parts[3]:
                            return candidate
                except Exception:
                    pass
            elif algorithm == "ntlm":
                if hashlib.new('md4', candidate.encode('utf-16le')).hexdigest() == target_lower:
                    return candidate
            else:
                payload = f"{candidate}{salt}".encode('utf-8') if salt else candidate.encode('utf-8')
                if hashlib.new(algorithm, payload).hexdigest() == target_lower:
                    return candidate
    except Exception:
        pass
    return None


class RedDevilEngine:
    def __init__(self, db_path: str = "core/sessions.db", max_workers: int = 0, enable_gpu: bool = False):
        self.db_path = db_path
        self.workers = max_workers or os.cpu_count() or 4
        self.found = False
        self.result = None
        self._init_db()
        self.telemetry = {"hashes_checked": 0, "start_time": 0.0}

    def _init_db(self):
        """Initializes the SQLite database for session state tracking and checkpoints"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    session_key TEXT PRIMARY KEY,
                    processed_count INTEGER,
                    timestamp TEXT
                )
            """)
            conn.commit()

    def save_checkpoint(self, session_key: str, processed_count: int):
        """Saves current calculation status inside local storage database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO checkpoints (session_key, processed_count, timestamp)
                VALUES (?, ?, datetime('now'))
                ON CONFLICT(session_key) DO UPDATE SET
                processed_count = excluded.processed_count, timestamp = datetime('now')
            """, (session_key, processed_count))
            conn.commit()

    def load_checkpoint(self, session_key: str) -> int:
        """Retrieves checkpoint markers to resume execution states"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT processed_count FROM checkpoints WHERE session_key = ?", (session_key,))
            row = cursor.fetchone()
            return row[0] if row else 0

    def execute_decode_pipeline(self, target: str, method: str) -> Optional[str]:
        """Handles on-the-fly transformations for data strings with padding verification"""
        try:
            if method == "base64":
                padded_target = target + "=" * ((4 - len(target) % 4) % 4)
                return base64.b64decode(padded_target.encode('utf-8')).decode('utf-8', errors='ignore')
            elif method == "hex":
                return bytes.fromhex(target).decode('utf-8', errors='ignore')
            elif method == "url":
                return urllib.parse.unquote(target)
            return None
        except Exception:
            return None

    def generate_mutations(self, word: str, rules: Dict[str, str]) -> List[str]:
        """Applies dynamic character substitutions and advanced casing array rule variations"""
        mutations = {word, word.lower(), word.upper(), word.capitalize()}
        
        if len(word) > 1:
            mutations.add(word[0].lower() + word[1:].upper())
            mutations.add(word[0].upper() + word[1:].lower())
            
        mutated_word = word.lower()
        for key, value in rules.items():
            mutated_word = mutated_word.replace(key, value)
        mutations.add(mutated_word)
        mutations.add(mutated_word.capitalize())
        
        return list(mutations)

    def _stream_mask_chunks(self, tokens: List[str], chunk_size: int) -> Generator[List[str], None, None]:
        """Memory-safe lazy chunk generator for mask attacks that resolves tuples into strings"""
        iterator = itertools.product(*tokens)
        while True:
            chunk = list(itertools.islice(iterator, chunk_size))
            if not chunk:
                break
            yield ["".join(item) for item in chunk]

    def execute_mask_crack(self, target: str, algorithm: str, mask: str, telemetry_callback=None) -> Optional[str]:
        """Safe multi-core mask attack utilizing generator isolation pipelines"""
        charset_map = {
            "?d": "0123456789",
            "?l": "abcdefghijklmnopqrstuvwxyz",
            "?u": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "?s": "!@#$%^&*()-_+=[]{}|;:',.<>?/"
        }
        
        tokens = []
        i = 0
        while i < len(mask):
            if mask[i] == '?' and i + 1 < len(mask):
                spec = mask[i:i+2]
                if spec in charset_map:
                    tokens.append(charset_map[spec])
                    i += 2
                    continue
            tokens.append(mask[i])
            i += 1

        self.telemetry["start_time"] = time.time()
        self.telemetry["hashes_checked"] = 0
        chunk_limit = 20000

        with ProcessPoolExecutor(max_workers=self.workers, initializer=_init_worker) as executor:
            futures = set()
            
            for chunk_buffer in self._stream_mask_chunks(tokens, chunk_limit):
                self.telemetry["hashes_checked"] += len(chunk_buffer)
                futures.add(executor.submit(_check_chunk_slice, (chunk_buffer, target, algorithm, "")))
                
                if len(futures) >= self.workers * 2:
                    for completed in as_completed(futures):
                        futures.remove(completed)
                        res = completed.result()
                        if res:
                            return res
                        break
                
                if telemetry_callback:
                    telemetry_callback(self.telemetry["hashes_checked"], time.time() - self.telemetry["start_time"])
            
            for completed in as_completed(futures):
                res = completed.result()
                if res:
                    return res
                    
        return None

    def execute_dictionary_attack(self, target: str, algorithm: str, wordlist: str, 
                                  rules: Dict[str, str], salt: str = "", 
                                  progress_callback=None) -> Optional[str]:
        """High-performance parallelized Dictionary processing system with early exit optimizations"""
        if not os.path.exists(wordlist):
            return None

        session_key = f"{target.lower()[:10]}:{algorithm}:{os.path.basename(wordlist)}"
        resume_index = self.load_checkpoint(session_key)
        
        processed_lines = 0
        chunk_buffer = []
        chunk_limit = 10000
        
        with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
            with ProcessPoolExecutor(max_workers=self.workers, initializer=_init_worker) as executor:
                futures = set()
                
                for line in f:
                    processed_lines += 1
                    if processed_lines < resume_index:
                        continue
                        
                    raw_word = line.strip()
                    if not raw_word:
                        continue
                        
                    candidates = self.generate_mutations(raw_word, rules)
                    chunk_buffer.extend(candidates)
                    
                    if len(chunk_buffer) >= chunk_limit:
                        futures.add(executor.submit(_check_chunk_slice, (chunk_buffer, target, algorithm, salt)))
                        chunk_buffer = []
                        
                        if len(futures) >= self.workers * 2:
                            for completed in as_completed(futures):
                                futures.remove(completed)
                                res = completed.result()
                                if res:
                                    self.save_checkpoint(session_key, processed_lines)
                                    return res
                                break
                        
                        if progress_callback:
                            progress_callback(processed_lines, raw_word)
                            
                if chunk_buffer:
                    futures.add(executor.submit(_check_chunk_slice, (chunk_buffer, target, algorithm, salt)))
                    
                for completed in as_completed(futures):
                    res = completed.result()
                    if res:
                        self.save_checkpoint(session_key, processed_lines)
                        return res
                        
        return None