#!/usr/bin/env python3
"""
================================================================================
PROJECT DEXTER: GOD-TIER STATIC FORENSICS & MALWARE TRIAGE FRAMEWORK
================================================================================
Author: Senior Python Security Engineer / Malware Analyst
Description: Professional-grade static triage tool designed for Blue Teams, 
             Incident Responders, and SOC Analysts. Parses multi-format binaries,
             documents, and imagery to deliver localized indicator extractions, 
             cryptographic cross-matching, and deterministic risk modeling.

Dependencies Installation:
    pip install rich pefile yara-python ppdeep python-magic pypdf python-docx olefile piexif requests

System Requirements:
    - libmagic binaries (Windows users: pip install python-magic-bin)
    - Python 3.8+
================================================================================
"""

import os
import sys
import json
import math
import re
import argparse
import hashlib
import mimetypes
import logging
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Set

# Programmatically suppress third-party library warning clutter globally
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*ARC4.*")

# --- RICH TERMINAL MANAGEMENT ---
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, MofNCompleteColumn
from rich.logging import RichHandler
from rich.traceback import install as install_rich_traceback
from rich.markdown import Markdown

install_rich_traceback()
console = Console()

# --- OPTIONAL DEFENSIVE SECURITY IMPORTS (WITH CROSS-PLATFORM WRAPPERS) ---
MISSING_LIBS = []

try:
    import magic
except ImportError:
    try:
        import magic_bin as magic
    except ImportError:
        magic = None
        MISSING_LIBS.append("python-magic (File type verification degraded)")

try:
    import pefile
except ImportError:
    pefile = None
    MISSING_LIBS.append("pefile (Windows Portable Executable parsing disabled)")

try:
    import yara
except ImportError:
    yara = None
    MISSING_LIBS.append("yara-python (YARA heuristics subsystem disabled)")

try:
    import ppdeep
except ImportError:
    ppdeep = None
    MISSING_LIBS.append("ppdeep (Fuzzy hashing signatures disabled)")

try:
    import pypdf
except ImportError:
    pypdf = None
    MISSING_LIBS.append("pypdf (PDF object structural parsing disabled)")

try:
    import docx
except ImportError:
    docx = None
    MISSING_LIBS.append("python-docx (Office Open XML forensics disabled)")

try:
    import olefile
except ImportError:
    olefile = None
    MISSING_LIBS.append("olefile (Structured OLE2 / Legacy Office parsing disabled)")

try:
    import piexif
except ImportError:
    piexif = None
    MISSING_LIBS.append("piexif (Image EXIF data mining disabled)")

try:
    import requests
except ImportError:
    requests = None
    MISSING_LIBS.append("requests (VirusTotal lookup system disabled)")


# --- BUILT-IN DETONATION & TRIAGE SIGNATURES (YARA FALLBACK) ---
BUILTIN_YARA_RULES = """
rule Embedded_EXE_Header {
    meta:
        description = "Detects an embedded Windows executable header sequence"
        severity = "Medium"
    strings:
        $mz = { 4D 5A }
    condition:
        $mz at 0 or ($mz and not filename matches /\\.exe$/ and not filename matches /\\.dll$/ and not filename matches /\\.sys$/)
}

rule Evasion_Indicators {
    meta:
        description = "Detects common anti-analysis and discovery patterns"
        severity = "High"
    strings:
        $s1 = "IsDebuggerPresent" ascii nocase
        $s2 = "CheckRemoteDebuggerPresent" ascii nocase
        $s3 = "NtQueryInformationProcess" ascii nocase
        $s4 = "GetTickCount" ascii nocase
        $s5 = "Sleep" ascii nocase
        $s6 = "VBOX" ascii nocase
        $s7 = "VMware" ascii nocase
    condition:
        3 of them
}

rule Execution_Anomalies {
    meta:
        description = "Detects persistence mechanics, injection targets, and download cradles"
        severity = "High"
    strings:
        $cmd = "cmd.exe /c" ascii nocase
        $ps = "powershell.exe" ascii nocase
        $bypass = "-ExecutionPolicy Bypass" ascii nocase
        $hidden = "-WindowStyle Hidden" ascii nocase
        $wscript = "WScript.Shell" ascii nocase
        $reg1 = "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run" ascii wide
        $reg2 = "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\RunOnce" ascii wide
        $vbs = ".vbs" ascii nocase
        $bits = "bitsadmin" ascii nocase
    condition:
        2 of them
}

rule Offensive_Tooling_Matches {
    meta:
        description = "Detects known offensive framework indicators and payload elements"
        severity = "Critical"
    strings:
        $m1 = "ReflectiveLoader" ascii
        $m2 = "mimikatz" ascii nocase
        $m3 = "wce.exe" ascii nocase
        $m4 = "CobaltStrike" ascii nocase
        $m5 = "Metasploit" ascii nocase
    condition:
        any of them
}
"""

# --- REGEX COMPILER FOR NETWORK/HOST INDICATORS OF COMPROMISE ---
IOC_REGEX = {
    "IPv4 Address": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
    "URL String": re.compile(r'https?://[^\s"\'>]+'),
    "Email Pattern": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    "Registry Location": re.compile(r'\b(HKLM|HKCU|Registry\\Machine|Registry\\UserAll)\\Software\\[A-Za-z0-9_\\\-]+', re.IGNORECASE),
    "Windows Directory Path": re.compile(r'\b[A-Za-z]:\\(?:Windows|Program Files|Users)\\[A-Za-z0-9_.\s\\\-]+', re.IGNORECASE)
}


class DexterFramework:
    """The central analysis orchestrator for all static telemetry processing."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = {
            "vt_api_key": "virus_total_api_key_here",
            "yara_rules_path": None,
            "max_string_len": 128,
            "min_string_len": 5,
            "chunk_size": 65536,
            "reports_dir": "dexter_reports"
        }
        if config_path:
            self.load_config(config_path)
            
        self.yara_ctx = None
        self._compile_yara_rules()
        os.makedirs(self.config["reports_dir"], exist_ok=True)

    def load_config(self, path: str) -> None:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    user_data = json.load(f)
                    self.config.update(user_data)
                logging.info(f"Loaded config from {path}")
        except Exception as e:
            logging.error(f"Failed to load config matrix from {path}: {str(e)}")

    def _compile_yara_rules(self) -> None:
        if not yara:
            return
        try:
            if self.config["yara_rules_path"] and os.path.exists(self.config["yara_rules_path"]):
                self.yara_ctx = yara.compile(filepath=self.config["yara_rules_path"])
                logging.info(f"YARA operational utilizing ruleset context: {self.config['yara_rules_path']}")
            else:
                self.yara_ctx = yara.compile(source=BUILTIN_YARA_RULES)
                logging.info("YARA operational utilizing integrated core signatures.")
        except Exception as e:
            logging.error(f"Failed compile loop inside YARA framework engine: {str(e)}")

    def determine_mime_type(self, path: str) -> str:
        if magic:
            try:
                return magic.from_file(path, mime=True)
            except Exception:
                pass
        guess, _ = mimetypes.guess_type(path)
        return guess or "application/octet-stream"

    def compute_cryptographic_hashes(self, path: str) -> Dict[str, str]:
        h_md5 = hashlib.md5()
        h_sha1 = hashlib.sha1()
        h_sha256 = hashlib.sha256()
        
        ssdeep_ctx = None
        if ppdeep:
            try:
                if hasattr(ppdeep, 'preprocess'):
                    ssdeep_ctx = ppdeep.preprocess()
                elif hasattr(ppdeep, 'HashContext'):
                    ssdeep_ctx = ppdeep.HashContext()
            except Exception:
                ssdeep_ctx = None

        try:
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(self.config["chunk_size"])
                    if not chunk:
                        break
                    h_md5.update(chunk)
                    h_sha1.update(chunk)
                    h_sha256.update(chunk)
                    
                    if ppdeep and ssdeep_ctx and hasattr(ppdeep, 'update'):
                        try:
                            ppdeep.update(ssdeep_ctx, chunk)
                        except Exception:
                            pass
                        
            ssdeep_final = "N/A"
            if ppdeep and ssdeep_ctx and hasattr(ppdeep, 'finish'):
                try:
                    ssdeep_final = ppdeep.finish(ssdeep_ctx)
                except Exception:
                    pass
                    
            return {
                "md5": h_md5.hexdigest(),
                "sha1": h_sha1.hexdigest(),
                "sha256": h_sha256.hexdigest(),
                "ssdeep": ssdeep_final
            }
        except Exception as e:
            logging.error(f"Hash calculation error for target tracking array: {str(e)}")
            return {"md5": "ERROR", "sha1": "ERROR", "sha256": "ERROR", "ssdeep": "N/A"}
        
    @staticmethod
    def calculate_entropy(path: str) -> float:
        frequencies = [0] * 256
        total_size = 0
        
        try:
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    for byte in chunk:
                        frequencies[byte] += 1
                        
            if total_size == 0:
                return 0.0
                
            entropy = 0.0
            for count in frequencies:
                if count > 0:
                    p = count / total_size
                    entropy -= p * math.log2(p)
            return round(entropy, 4)
        except Exception:
            return 0.0

    def parse_strings_and_iocs(self, path: str) -> Tuple[List[str], Dict[str, List[str]]]:
        """Scans binary maps extracting high-density ASCII/Unicode data maps for IoC verification."""
        extracted_strings = []
        iocs = {k: set() for k in IOC_REGEX.keys()}
        
        min_len = self.config["min_string_len"]
        max_len = self.config["max_string_len"]
        
        ascii_pattern = re.compile(r'[\x20-\x7E]{' + str(min_len) + ',' + str(max_len) + '}')

        try:
            with open(path, 'rb') as f:
                while True:
                    chunk = f.read(262144) 
                    if not chunk:
                        break
                    
                    # Decoded chunks are passed safely as strings to the compiled text-regex loops
                    decoded_chunk = chunk.decode('ascii', errors='ignore')
                    for match in ascii_pattern.finditer(decoded_chunk):
                        s_val = match.group().strip()
                        if s_val:
                            extracted_strings.append(s_val)
                            for ioc_name, regex in IOC_REGEX.items():
                                for hit in regex.findall(s_val):
                                    if isinstance(hit, tuple):
                                        hit = hit[0]
                                    iocs[ioc_name].add(str(hit))

                    # Unicode search conversion
                    unicode_decoded = chunk.decode('utf-16le', errors='ignore')
                    for match in ascii_pattern.finditer(unicode_decoded):
                        s_val = match.group().strip()
                        if s_val and len(s_val) >= min_len:
                            extracted_strings.append(s_val)
                            for ioc_name, regex in IOC_REGEX.items():
                                for hit in regex.findall(s_val):
                                    if isinstance(hit, tuple):
                                        hit = hit[0]
                                    iocs[ioc_name].add(str(hit))
                            
            sanitized_iocs = {k: list(v)[:50] for k, v in iocs.items()} 
            return extracted_strings[:200], sanitized_iocs
        except Exception as e:
            logging.error(f"Error executing raw structural string miner loops: {str(e)}")
            return [], {k: [] for k in IOC_REGEX.keys()}

    def execute_yara_scans(self, path: str) -> List[Dict[str, str]]:
        matches_found = []
        if not self.yara_ctx:
            return matches_found
        try:
            matches = self.yara_ctx.match(filepath=path)
            for m in matches:
                matches_found.append({
                    "rule": m.rule,
                    "namespace": m.namespace,
                    "severity": m.meta.get("severity", "Medium"),
                    "description": m.meta.get("description", "No descriptions logged.")
                })
        except Exception as e:
            logging.error(f"YARA logic error mapping metadata fields: {str(e)}")
        return matches_found

    def triage_portable_executable(self, path: str) -> Dict[str, Any]:
        pe_metrics = {"status": "unsupported", "anomalies": [], "sections": [], "imports": [], "tls_callbacks": False}
        if not pefile:
            return pe_metrics

        try:
            pe = pefile.PE(path, fast_load=False)
            pe_metrics["status"] = "parsed"
            pe_metrics["machine"] = hex(pe.FILE_HEADER.Machine)
            
            try:
                pe_metrics["compile_time"] = datetime.fromtimestamp(pe.FILE_HEADER.TimeDateStamp, timezone.utc).isoformat()
            except Exception:
                pe_metrics["compile_time"] = "Invalid Timestamp/Anomaly Detected"

            if hasattr(pe, 'DIRECTORY_ENTRY_TLS') and pe.DIRECTORY_ENTRY_TLS and pe.DIRECTORY_ENTRY_TLS.struct:
                pe_metrics["tls_callbacks"] = True
                pe_metrics["anomalies"].append("TLS Callbacks detected (Potential execution diversion vector)")

            for sec in pe.sections:
                sec_name = sec.Name.decode('utf-8', errors='ignore').strip('\x00')
                sec_entropy = self.calculate_entropy_of_data(sec.get_data())
                
                is_packed = sec_entropy > 7.4
                if is_packed:
                    pe_metrics["anomalies"].append(f"High entropy packed code layer within target section: {sec_name}")

                known_sections = ['.text', '.rdata', '.data', '.pdata', '.rcid', '.rsrc', '.reloc']
                if sec_name not in known_sections and not sec_name.startswith('/'):
                    pe_metrics["anomalies"].append(f"Non-standard PE binary workspace header recognized: {sec_name}")

                pe_metrics["sections"].append({
                    "name": sec_name,
                    "virtual_size": hex(sec.Misc_VirtualSize),
                    "raw_size": hex(sec.SizeOfRawData),
                    "entropy": sec_entropy,
                    "packed": is_packed
                })

            if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
                for entry in pe.DIRECTORY_ENTRY_IMPORT:
                    dll_name = entry.dll.decode('utf-8', errors='ignore')
                    for imp in entry.imports:
                        if imp.name:
                            pe_metrics["imports"].append(f"{dll_name}!{imp.name.decode('utf-8', errors='ignore')}")
                            
            pe.close()
        except Exception as e:
            pe_metrics["status"] = "error"
            pe_metrics["anomalies"].append(f"PE structure structural parser errors: {str(e)}")
        return pe_metrics

    @staticmethod
    def calculate_entropy_of_data(data: bytes) -> float:
        if not data: return 0.0
        entropy = 0.0
        frequencies = [0] * 256
        for b in data: frequencies[b] += 1
        for count in frequencies:
            if count > 0:
                p = count / len(data)
                entropy -= p * math.log2(p)
        return round(entropy, 4)

    def process_pdf_metadata(self, path: str) -> Dict[str, Any]:
        meta = {"status": "unsupported", "pages": 0, "author": "N/A", "creator": "N/A", "anomalies": []}
        if not pypdf: return meta
        try:
            with open(path, 'rb') as f:
                reader = pypdf.PdfReader(f)
                meta["status"] = "parsed"
                meta["pages"] = len(reader.pages)
                info = reader.metadata
                if info:
                    meta["author"] = info.author if info.author else "N/A"
                    meta["creator"] = info.creator if info.creator else "N/A"
                
                raw_text = ""
                for idx in range(min(5, len(reader.pages))):
                    raw_text += reader.pages[idx].extract_text()
                    
                if "/JavaScript" in raw_text or "/JS" in raw_text:
                    meta["anomalies"].append("Embedded Active JavaScript structures discovered inside object catalog layers.")
        except Exception as e:
            meta["status"] = "error"
            meta["anomalies"].append(f"PDF structure verification trace drop: {str(e)}")
        return meta

    def process_office_metadata(self, path: str) -> Dict[str, Any]:
        meta = {"status": "unsupported", "macros": False, "properties": {}, "anomalies": []}
        if olefile and olefile.isOleFile(path):
            meta["status"] = "parsed (OLE Legacy)"
            try:
                ole = olefile.OleFileIO(path)
                if ole.exists('macros/vba') or ole.exists('Macros') or ole.exists('_VBA_PROJECT_CUR'):
                    meta["macros"] = True
                    meta["anomalies"].append("VBA Script macro framework assets actively bound into document binary files.")
                ole.close()
            except Exception:
                pass
                
        elif docx and path.lower().endswith('.docx'):
            meta["status"] = "parsed (OOXML)"
            try:
                doc = docx.Document(path)
                prop = doc.core_properties
                meta["properties"] = {"author": prop.author, "created": str(prop.created)}
            except Exception:
                pass
        return meta

    def process_image_metadata(self, path: str) -> Dict[str, Any]:
        meta = {"status": "unsupported", "exif": {}}
        if not piexif: return meta
        try:
            exif_dict = piexif.load(path)
            if exif_dict and "0th" in exif_dict:
                meta["status"] = "parsed"
                for tag in exif_dict["0th"]:
                    meta["exif"][str(tag)] = str(exif_dict["0th"][tag][:40])
        except Exception:
            pass
        return meta

    def scan_virustotal_reputation(self, sha256_hash: str) -> Dict[str, Any]:
        if not self.config["vt_api_key"] or not requests:
            return {"status": "offline", "msg": "VirusTotal intelligence query pipeline is offline."}
            
        url = f"https://www.virustotal.com/api/v3/files/{sha256_hash}"
        headers = {"x-apikey": self.config["vt_api_key"], "accept": "application/json"}
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                attributes = res.json().get("data", {}).get("attributes", {})
                stats = attributes.get("last_analysis_stats", {})
                classification = attributes.get("popular_threat_classification", {})
                return {
                    "status": "matched",
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "total": sum(stats.values()),
                    "label": classification.get("suggested_threat_label", "N/A")
                }
            elif res.status_code == 404:
                return {"status": "unknown", "msg": "No prior records mapped into reputation datasets."}
            return {"status": "error", "msg": f"API responded with tracking status code: {res.status_code}"}
        except Exception as e:
            return {"status": "error", "msg": f"Target route map trace exception dropped: {str(e)}"}

    def run_deterministic_risk_matrix(self, report: Dict[str, Any]) -> Tuple[str, int, List[str]]:
        score = 0
        reasons = []

        if report["entropy"] > 7.5:
            score += 35
            reasons.append(f"High cryptographic byte layer density distribution found ({report['entropy']}) indicating encryption/packing patterns.")
        elif report["entropy"] < 1.5 and report["target_meta"]["size_bytes"] > 10240:
            score += 15
            reasons.append("Highly flat binary density matrix matching malicious hollow zero pattern profiles.")

        yara_count = len(report["yara_matches"])
        if yara_count > 0:
            score += (yara_count * 30)
            for m in report["yara_matches"]:
                reasons.append(f"YARA Heuristic Signature Engine Matched: [{m['rule']}] (Severity Map: {m['severity']})")

        if "pe_forensics" in report and report["pe_forensics"].get("status") == "parsed":
            pe = report["pe_forensics"]
            anom_count = len(pe.get("anomalies", []))
            if anom_count > 0:
                score += (anom_count * 15)
                for anom in pe["anomalies"]:
                    reasons.append(f"PE Header Structural Anomaly: {anom}")
            
            susp_apis = ["LoadLibrary", "GetProcAddress", "VirtualAlloc", "VirtualProtect", "WriteProcessMemory", "CreateRemoteThread"]
            api_hits = [api for api in susp_apis if any(api in imp for imp in pe.get("imports", []))]
            if len(api_hits) >= 3:
                score += 25
                reasons.append(f"High-density injection/evasion Windows API imports resolved: {', '.join(api_hits)}")

        if "office_forensics" in report and report["office_forensics"].get("macros"):
            score += 50
            reasons.append("Active VBA Core Execution Macro components detected inside document package streams.")

        vt = report["virus_total"]
        if vt.get("status") == "matched" and vt.get("malicious", 0) > 0:
            score += (vt["malicious"] * 12)
            reasons.append(f"VirusTotal Cloud Intelligence Cross-Check returned {vt['malicious']} defensive multi-engine alerts.")

        final_score = min(score, 100)
        
        if final_score >= 70 or vt.get("malicious", 0) > 4:
            verdict = "[bold red]MALICIOUS[/bold red]"
        elif final_score >= 30:
            verdict = "[bold yellow]SUSPICIOUS[/bold yellow]"
        else:
            verdict = "[bold green]CLEAN[/bold green]"
            
        return verdict, final_score, reasons

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        path = os.path.abspath(file_path)
        hashes = self.compute_cryptographic_hashes(path)
        entropy = self.calculate_entropy(path)
        mime = self.determine_mime_type(path)
        strings, iocs = self.parse_strings_and_iocs(path)
        yara_hits = self.execute_yara_scans(path)
        vt_data = self.scan_virustotal_reputation(hashes["sha256"])

        report = {
            "target_meta": {
                "name": os.path.basename(path),
                "path": path,
                "size_bytes": os.path.getsize(path),
                "mime_type": mime,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "hashes": hashes,
            "entropy": entropy,
            "yara_matches": yara_hits,
            "virus_total": vt_data,
            "extracted_iocs": iocs,
            "strings_preview": strings[:12]
        }

        if file_path.lower().endswith(('.exe', '.dll', '.sys', '.mui')):
            report["pe_forensics"] = self.triage_portable_executable(path)
        if file_path.lower().endswith('.pdf'):
            report["pdf_forensics"] = self.process_pdf_metadata(path)
        if file_path.lower().endswith(('.docx', '.doc', '.docm', '.xlsx', '.xls')):
            report["office_forensics"] = self.process_office_metadata(path)
        if file_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            report["image_forensics"] = self.process_image_metadata(path)

        verdict, score, reasons = self.run_deterministic_risk_matrix(report)
        report["summary"] = {
            "verdict": verdict,
            "risk_score": score,
            "reasons": reasons
        }

        self.export_report_data(report)
        return report

    def export_report_data(self, report: Dict[str, Any]) -> None:
        base_name = f"DEXTER_{report['hashes']['sha256'][:16]}"
        reports_dir = Path(self.config["reports_dir"])
        
        json_path = reports_dir / f"{base_name}.json"
        with open(json_path, 'w') as f:
            json.dump(report, f, indent=4)

        html_path = reports_dir / f"{base_name}.html"
        with open(html_path, 'w') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>Project Dexter Forensic Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f111a; color: #a6accd; padding: 25px; }}
        .panel {{ background-color: #1a1c25; border: 1px solid #2e3244; padding: 20px; border-radius: 6px; margin-bottom: 20px; }}
        h1, h2, h3 {{ color: #ff5370; margin-top: 0; }}
        .clean {{ color: #c3e88d; font-weight: bold; }}
        .suspicious {{ color: #ffcb6b; font-weight: bold; }}
        .malicious {{ color: #f07178; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #232635; }}
        th {{ color: #89ddff; }}
        .string-seq {{ font-family: 'Courier New', Courier, monospace; color: #f07178; font-size: 13px; }}
    </style>
</head>
<body>
    <h1>PROJECT DEXTER // FORENSICS INSIGHT LOG</h1>
    <div class="panel">
        <h2>Target Core System Identity Map</h2>
        <table>
            <tr><th>File Name</th><td>{report['target_meta']['name']}</td></tr>
            <tr><th>MIME Type</th><td>{report['target_meta']['mime_type']}</td></tr>
            <tr><th>Size</th><td>{report['target_meta']['size_bytes']} bytes</td></tr>
            <tr><th>MD5</th><td>{report['hashes']['md5']}</td></tr>
            <tr><th>SHA-256</th><td>{report['hashes']['sha256']}</td></tr>
            <tr><th>Entropy Rating</th><td>{report['entropy']} / 8.0</td></tr>
        </table>
    </div>
    <div class="panel">
        <h2>Threat Evaluation Matrix</h2>
        <h3>Risk Score Status Indicator: {report['summary']['risk_score']} / 100</h3>
        <p>Anomalies/Triggers Verified:</p>
        <ul>
            {"".join(f"<li>{r}</li>" for r in report['summary']['reasons'])}
        </ul>
    </div>
</body>
</html>
""")


def render_terminal_dashboard(report: Dict[str, Any], verbosity: int) -> None:
    banner = """
    [bold magenta]██████╗ ███████╗██╗  ██╗████████╗███████╗██████╗ [/bold magenta]
    [bold magenta]██╔══██╗██╔════╝╚██╗██╔╝╚══██╔══╝██╔════╝██╔══██╗[/bold magenta]
    [bold cyan]██║  ██║█████╗   ╚███╔╝    ██║   █████╗  ██████╔╝[/bold cyan]
    [bold cyan]██║  ██║██╔══╝   ██╔██╗    ██║   ██╔══╝  ██╔══██╗[/bold cyan]
    [bold blue]██████╔╝███████╗██╔╝ ██╗   ██║   ███████╗██║  ██║[/bold blue]
    [bold blue]╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝[/bold blue]
         -- [bold white]ENTERPRISE STATIC FILE FORENSICS CORE[/bold white] --
    """
    console.print(banner)

    meta = report["target_meta"]
    hashes = report["hashes"]
    summary = report["summary"]

    telemetry_table = Table(title="File System Identity Telemetry", title_style="bold cyan", box=None, expand=True)
    telemetry_table.add_column("Property Header Key", style="bold yellow", width=25)
    telemetry_table.add_column("Extracted Verification Registry Value", style="white")

    telemetry_table.add_row("Target Location File Name", meta["name"])
    telemetry_table.add_row("Magic Byte MIME Type", meta["mime_type"])
    telemetry_table.add_row("File Allocation Boundary Size", f"{meta['size_bytes']} bytes")
    telemetry_table.add_row("Shannon Entropy Index", f"{report['entropy']} / 8.0")
    telemetry_table.add_row("MD5 Digest Signature", hashes["md5"])
    telemetry_table.add_row("SHA-256 Signature Header", hashes["sha256"])
    telemetry_table.add_row("Fuzzy Signature Hash (SSDeep)", hashes["ssdeep"])

    vt = report["virus_total"]
    if vt.get("status") == "matched":
        vt_display = f"[bold red]MALICIOUS IDENTIFIED: {vt['malicious']}/{vt['total']}[/bold red] (Classification Vector Label: {vt['label']})"
    elif vt.get("status") == "offline":
        vt_display = f"[dim white]Skipped Core Lookups ({vt['msg']})[/dim white]"
    else:
        vt_display = "[bold yellow]VirusTotal api key not provided[/bold yellow]"
    telemetry_table.add_row("VirusTotal Engine Array", vt_display)

    console.print(Panel(telemetry_table, border_style="blue", title="[bold blue]Triage Metadata Core[/bold blue]"))

    verdict_panel_content = f"Analytical Threat Determination Matrix Status Verdict: {summary['verdict']}\n" \
                            f"Calculated Absolute Scoring Evaluation Array: [bold cyan]{summary['risk_score']}/100[/bold cyan]\n\n"
    if summary["reasons"]:
        verdict_panel_content += "[bold red]Risk Evaluation Indicators Flagged:[/bold red]\n" + "\n".join(f" [bold red]•[/bold red] {r}" for r in summary["reasons"])
    else:
        verdict_panel_content += "[bold green]• No anomalies recognized via localized verification models.[/bold green]"

    console.print(Panel(verdict_panel_content, border_style="magenta", title="[bold magenta]Threat Engine Decision Metrics[/bold magenta]"))

    if verbosity >= 1:
        ioc_table = Table(title="Network Indicators & Host Signatures Matrix Extraction Profile", title_style="bold cyan", expand=True)
        ioc_table.add_column("Indicator Signature Target Category Types", style="bold yellow")
        ioc_table.add_column("Extracted Telemetry Mapping Values Captured", style="green")

        for key, value in report["extracted_iocs"].items():
            display_val = ", ".join(value[:6]) if value else "[dim white]None Discovered[/dim white]"
            ioc_table.add_row(key, display_val)

        console.print(ioc_table)

    if verbosity >= 2:
        if "pe_forensics" in report and report["pe_forensics"].get("status") == "parsed":
            pe = report["pe_forensics"]
            pe_table = Table(title="PE Structural Binary Internals Deep Analytics", title_style="bold magenta", expand=True)
            pe_table.add_column("Target Section Layer Label", style="bold yellow")
            pe_table.add_column("Virtual Bounds", style="white")
            pe_table.add_column("Raw Allocation Bounds", style="white")
            pe_table.add_column("Entropy Allocation Matrix", style="white")
            
            for sec in pe["sections"]:
                ent_color = "red" if sec["packed"] else "green"
                pe_table.add_row(sec["name"], sec["virtual_size"], sec["raw_size"], f"[{ent_color}]{sec['entropy']}[/{ent_color}]")
            console.print(pe_table)


def main():
    # Interactive mode logic fallback context detection for Eclipse IDE workflows
    if len(sys.argv) == 1:
        console.print(Panel("[bold yellow][*] Interactive Mode Launch Context Recognized (No CLI arguments given)[/bold yellow]\nPerfect for Eclipse execution profiles.", border_style="cyan"))
        target_input = input("Enter Target File or Directory path: ").strip()
        target_input = target_input.strip("'\"")
        
        verbosity_input = input("Select Triage Verbosity Level [0=Min, 1=Standard, 2=Deep Forensics] (Default=1): ").strip()
        verbosity = int(verbosity_input) if verbosity_input in ['0', '1', '2'] else 1
        config_path = None
    else:
        parser = argparse.ArgumentParser(description="Project Dexter: Professional Static Threat Intelligence Platform Engine")
        parser.add_argument("-t", "--target", required=True, help="Path targeting file or directory structures for analysis operations.")
        parser.add_argument("-c", "--config", required=False, help="Explicit path location parameter mapping configurations.")
        parser.add_argument("-v", "--verbosity", type=int, default=1, choices=[0, 1, 2], help="UI Verbosity levels.")
        args = parser.parse_args()
        target_input = args.target
        verbosity = args.verbosity
        config_path = args.config

    if MISSING_LIBS:
        missing_markdown = "\n".join(f" * [bold yellow]WARNING Option Context Missing:[/bold yellow] {lib}" for lib in MISSING_LIBS)
        console.print(Panel(Markdown(f"### Functional Engine Degradation Status Warning Matrix\n{missing_markdown}"), border_style="yellow"))

    framework = DexterFramework(config_path=config_path)

    if os.path.isfile(target_input):
        with Progress(
            SpinnerColumn(spinner_name="dots"),
            TextColumn("[bold cyan]{task.description}[/bold cyan]"),
            console=console
        ) as progress:
            task = progress.add_task(f"Deconstructing execution metadata boundaries: {os.path.basename(target_input)}", total=None)
            report = framework.analyze_file(target_input)
            progress.update(task, completed=True)
            
        render_terminal_dashboard(report, verbosity)
        console.print(f"\n[bold green][+][/bold green] Forensic data matrix exports written successfully inside layout files: [bold white]{framework.config['reports_dir']}/[/bold white]")

    elif os.path.isdir(target_input):
        target_dir = Path(target_input)
        file_list = [str(p) for p in target_dir.rglob('*') if p.is_file()]
        
        console.print(Panel(f"[bold yellow][*][/bold yellow] Commencing batch validation sweeps across directory processing arrays.\nDiscovered Asset File Targets Count: [bold white]{len(file_list)}[/bold white]", border_style="blue"))
        
        malicious_count = 0
        suspicious_count = 0
        
        with Progress(
            SpinnerColumn(spinner_name="bouncingBar"),
            BarColumn(),
            MofNCompleteColumn(),
            TextColumn("[bold magenta]{task.description}[/bold magenta]"),
            console=console
        ) as progress:
            batch_task = progress.add_task("Executing structural recursive triages...", total=len(file_list))
            
            for file_path in file_list:
                try:
                    res = framework.analyze_file(file_path)
                    score = res["summary"]["risk_score"]
                    if score >= 70: malicious_count += 1
                    elif score >= 30: suspicious_count += 1
                except Exception:
                    pass
                progress.advance(batch_task)

        summary_table = Table(title="Recursive Directory Threat Summary Matrix Matrix", title_style="bold magenta", expand=True)
        summary_table.add_column("Triage Metric Category Category", style="bold yellow")
        summary_table.add_column("Calculated Evaluated Asset Array Elements Value Metrics", style="bold white")
        summary_table.add_row("Total Data Scanned Boundary Footprints", str(len(file_list)))
        summary_table.add_row("Malicious System Signatures Discovered", f"[bold red]{malicious_count}[/bold red]")
        summary_table.add_row("Suspicious Telemetry Targets Flagged", f"[bold yellow]{suspicious_count}[/bold yellow]")
        console.print(Panel(summary_table, border_style="magenta"))
    else:
        console.print("[bold red][!] Operational Failure Target Error: Specified reference location context could not be read or does not exist.[/bold red]")


if __name__ == "__main__":
    main()