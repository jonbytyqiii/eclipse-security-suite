# AetherEye OSINT Suite v9.5

## Overview
**AetherEye** is a modular open-source intelligence (OSINT) gathering and infrastructure reconnaissance platform designed for automated information security audits, passive network mapping, and identity verification tracking. 

Built using Python's concurrent asynchronous runtime (`asyncio`), AetherEye processes data feeds across multiple target intelligence pipelines concurrently, providing high-performance telemetry via a comprehensive Terminal User Interface (TUI).

---

## Core Architecture & Engine Layout
The platform is organized flatly with distinct logical sub-engines handling target evaluation criteria:

```text
AetherEye/
│
├── pyproject.toml         # System installation and entry-point definition
├── config.yaml            # Active configuration matrices and API infrastructure tokens
├── config.example.yaml    # Reference settings skeleton configuration
├── aethereye.db           # SQLite tracking ledger database
├── core.py                # Central infrastructure orchestrator engine
├── launcher.py            # Universal working directory boundary alignment layer
├── requirements.txt       # Core package requirements tracking manifest
│
├───logs/                  # Automated platform execution session output files
│   └── aethereye_*.log
│
└───modules/               # High-fidelity target investigation sub-engines
    ├── __init__.py
    ├── geo_harvest.py     # Target Location Business Scraper
    ├── email_hunt.py      # Identity Pattern Verification
    ├── shodan_infra.py    # Active Port Topology Audit
    ├── image_forensics.py # EXIF Metadata Extraction Engine
    ├── social_stalker.py  # Cross-Platform Identity Hunter
    └── email_checker.py   # Advanced Holehe-Style Account Profiler
Technical Feature Matrix
1. OSINT Data Aggregation Vectors
Geo-Harvesting: Passive business, scraping, and spatial localization telemetry for target geography footprints.

Identity Profiling & Pattern Hunting: Automated email checking using Holehe-style registrations across social/web databases and cross-platform moniker tracing.

Infrastructure Mapping: Shodan API integrations profiling target perimeter setups, active services, and open network topologies.

Forensics Layer: Local image analysis tools parsing target files for hidden EXIF metadata or GPS geolocation markers.

2. Operational Highlights
Proxy/Proxychains Integration: Native support routing traffic safely across proxy infrastructure nodes to avoid rate-limiting or discovery.

Persistence Layer: Integrated SQLite ledger archiving session audits, targets, and discovery indicators.

Structured Logging: Auto-generating chronological .log operational files inside the logs/ repository for audit reviews.

Installation & Deployment
AetherEye handles global terminal shortcut alignments natively using Python's modern package specifications.

Prerequisites
Python >= 3.10

System packages (such as proxychains for secure session routing if applicable)

Global Setup
Clone or copy the tool repository workspace directory.

Open your terminal window inside the root AetherEye/ directory folder.

Install the package locally in editable/development mode to compile system hooks:

Bash
python -m pip install -e .
Usage Guide
Once installed, the toolkit maps a unified global terminal alias configuration shortcut (aethereye) across your system environment path.

Vector 1: Interactive Control Panel Hub (TUI)
Launch the unified platform dashboard directly from any current working terminal directory to process interactive queries manually:

Bash
aethereye
Vector 2: Fast-Track Pipeline Mode (Headless Command Line)
Execute high-priority automated recon processing on specific target regions or locations directly bypassing the primary terminal menu screens:

Bash
aethereye --geo pristina
Security Notice & Compliance
This suite is designed exclusively for authorized penetration testing environments, corporate asset defensive reviews, research simulations, and certified cybersecurity academies.

Ensure proper authorization bounds are fully satisfied before running active Shodan infrastructure queries or cross-referencing public information arrays.

Author: Jon Bytyqi

AetherEye Intelligence Operations Framework — Architecture v9.5