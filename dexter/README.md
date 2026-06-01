# Project Dexter: Static Forensics & Malware Triage Framework

## Overview
**Project Dexter** is a professional-grade static file triage and defensive forensic analysis framework built for Blue Teams, Incident Responders, SOC Analysts, and security researchers. 

The platform delivers high-speed automated binary, document, and image dissection, extracting embedded localization indicators, computing cryptographic fingerprints, tracking binary structural layout anomalies, and rendering deterministic risk scores using high-fidelity `rich` terminal interfaces.

---

## Project Structure & Architecture
The tool uses an isolated packaging layout enabling universal terminal shortcut execution while preserving localized report exports:

```text
dexter/
│
├── pyproject.toml         # Central packaging and script entry shortcut blueprint
├── dexter.py              # Core static forensics orchestrator engine (Cleaned)
├── dexter_launcher.py     # Unique environment directory boundary anchor
├── README.md              # Project documentation matrix
├── requirements.txt       # Dependency installation manifest file
│
└───dexter_reports/        # Automated session summary matrix storage
Technical Feature Matrix
1. Static Forensic Analysis Arrays
Multi-Format Parsing: Structural extraction capabilities targeting compiled binaries, documents, and imagery data.

Cryptographic Signatures: Computes file hashes across multiple mathematical standards along with fuzzy matching logic to discover mutated malware variants.

Deterministic Risk Modeling: Analyzes structural markers, section anomalies, hidden payload blocks, and compressed layouts to output an automated threat risk score.

🔑 API Keys & Infrastructure Configuration
⚠️ Critical Security Update: Hardcoded credentials have been stripped from the core source code files.

Project Dexter runs all core extraction, decompilation parsing, and algorithmic matching 100% locally on your host station. However, for extended global threat reputation correlation via VirusTotal, you must supply an authorized API key.

How to set your API Key securely:
Do not hardcode your keys inside dexter.py. Instead, load them directly into your current terminal environment session before starting the platform:

inside dexter.py line 189:

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

dexter
Key Validation Handling
If the application launches and detects that no API key has been provided, it will cleanly post an automated diagnostic warning notification inside your terminal screen loop:

Local static file dissections, entropy graphs, and layout parsing arrays will continue to execute normally.

External cloud reputation indexing and remote hash validation lookups will be safely bypassed to ensure runtime execution does not crash.

Installation & Deployment
Dexter is packaged using standard modern Python ecosystem blueprints for clean global terminal mapping.

System Prerequisites
Python >= 3.10

Mime Type Discovery Core: Local system libmagic binaries must be present.

Windows Systems: Automated via pip install python-magic-bin.

Linux Systems: Ensure native tools are present (sudo apt install libmagic1).

Environment Compilation
Open your terminal shell and steer into the root dexter/ directory workspace.

Compile and link the tool system paths locally using developer editable mode:

Bash
python -m pip install -e .

Usage Guide
Once compiled, the application exposes a global, context-independent shell command (dexter).

Launch Interactive File Triage
Execute the framework from any folder path on your operating system by specifying the target directory or explicit file asset you wish to examine:

Bash
dexter
Security Notice & Compliance
This suite is designed explicitly for authorized target host evaluations, malware triage, incident response verification playbooks, and security academy research laboratories. Ensure suspicious live samples are processed inside strictly isolated sandbox virtualization environments.

Author: Jon Bytyqi

Project Dexter Malware Forensics Engineering — Core Version 1.0.0