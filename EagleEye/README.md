# EagleEye v5.4 - Tactical Reconnaissance Engine

## Overview

EagleEye is a professional, thread-safe, multi-protocol network asset discovery and reconnaissance utility. Built with a hybrid execution engine, it attempts high-speed asynchronous packet inspection using raw socket wrappers while maintaining reliable native fallback logic for restrictive execution boundaries.

---

# Technical Features

* **Hybrid Execution Pipeline:** Fully leverages Scapy for advanced stealth scanning, while incorporating native Python `struct` packing algorithms to ensure continuity when Scapy bindings or elevated permissions are unavailable.

* **Multi-Protocol Capabilities:** Implements deep auditing layers across TCP Connect, Stealth SYN, and ICMP-backed UDP scan vectors.

* **Empirical Analysis Profiles:** Incorporates native structural arrays corresponding to industry-standard Nmap Top 100 and Top 1000 statistical port frequencies.

* **OS Fingerprinting & OUI Mapping:** Infers remote operational environments via historical TTL metrics and resolves local hardware vendor profiles using an embedded offline IEEE database snapshot.

* **Dual Interface Modes:** Features an elegant command-line interface (CLI) for automated workflow pipelines alongside an interactive console wizard for standalone lab use.

---

# Installation & Deployment

### 1. Isolated Subsystem Environment
To execute EagleEye as an isolated subsystem detached from the parent orchestration workspace, spin up a localized Python virtual environment:

```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
2. Global Command Line Integration (Recommended)
You can link the framework globally into your system path so that it can be executed from any terminal directory simply by typing eagleeye.

Navigate to the root directory where pyproject.toml is located and install it in development/editable mode:

Bash
pip install -e .
Note: The -e flag establishes a symlink to your source folder. Any modifications you make to the code will immediately reflect globally without requiring a reinstall.

Execution Metaphors
Once installed via pip install -e ., you can launch the system from any directory pathway using the global workspace command.

Interactive Console Wizard Mode
To spin up the modular wizard tracker and automatically parse your local subnets:

Bash
eagleeye
CLI Automation Engine Mode
To bypass the wizard and feed direct operational vectors into an automated testing pipeline, leverage the core CLI switches:

Bash
# Execute a thread-safe stealth SYN scan against a target network across the top 1000 ports
eagleeye -t 192.168.1.0/24 -p top1000 -sS -A

# Audit explicit port vectors on an exact system and export structured data sets
eagleeye -t 10.10.10.105 -p 22,80,443,3389 -oJ network_audit.json -oX network_audit.xml
The underlying reporting system serializes scan telemetry into clean JSON and XML structures.

Example JSON Output
JSON
{
    "192.168.1.105": {
        "hostname": "ubuntu-server.local",
        "mac": "00:0C:29:XX:XX:XX",
        "vendor": "VMware, Inc.",
        "os": "Linux / Kernel Stack Architecture (Unix/Android)",
        "ports": [
            {
                "port": 22,
                "service": "ssh",
                "version": "OpenSSH Secure Shell Daemon"
            },
            {
                "port": 80,
                "service": "http",
                "version": "Nginx Web Reverse Proxy"
            }
        ]
    }
}
Security Audit Disclaimer
This software engine is developed exclusively for:

Authorized infrastructure scanning

Professional vulnerability auditing

Educational target-validation environments

Defensive cybersecurity research

Always ensure explicit authorization has been granted before evaluating live infrastructure or external network assets.

Current Status Checklist
[x] EagleEye module structure verified and packed into src/eagleeye/

[x] Global entry point mapped to pyproject.toml blueprint definitions

[x] .gitignore logging exclusions configured

[x] Standalone requirements.txt finalized

[x] Professional standalone README.md updated with pip install -e . integration

[x] CLI and interactive execution modes documented

Project Status
EagleEye v5.4 is officially complete and ready for deployment, portfolio presentation, or GitHub publication.

Author
Jon Bytyqi

Cybersecurity / Network Reconnaissance Engineering Project
