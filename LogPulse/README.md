# LogPulse v1.0 - Forensic SIEM Engine

## Overview

LogPulse is a professional-grade, asynchronous log auditing and security information event management (SIEM) pipeline engine. Built with an event-driven architecture, LogPulse monitors active infrastructure audit points, normalizes unstructured security event text feeds, and processes telemetry streams against customizable multi-vector YAML threshold conditions.

---

## Technical Features

* **Asynchronous Ingestion Streams:** Utilizes an `asyncio` event loop architecture using dynamic file-system tail hooks to continuously look for modifications across active platform application pipelines without impacting UI telemetry.
* **Granular Normalization Processing:** Automatically maps divergent input streams (e.g., Linux authentication logs, Nginx/IIS web records) down into unified structured payloads (`LogEvent`).
* **Dynamic Sliding-Window Detection Engine:** Leverages customized YAML rules to execute state tracking, matching regex sequences and calculating windowed threshold criteria (e.g., tracking repeated authentication errors across sliding 10-second intervals).
* **Robust Relational Auditing Core:** Persists validated security incidents securely inside an SQLite persistence schema database tracking historical event counts, severities, and MITRE ATT&CK framework tactics.
* **TUI Metric Display Panels:** Employs an interactive terminal layout using the `Rich` live display engine to showcase security incident counters, telemetry logs, and local forensic modules side-by-side.

---

## Standalone Installation & Deployment

To execute LogPulse as a completely standalone component separate from the core Eclipse parent orchestration desk:

```powershell
# Instantiate clean workspace runtime boundaries
python -m venv venv
.\venv\Scripts\Activate.ps1

# Bind project package tracking in editable mode
pip install -e .
Interface Command Guide
Launch the primary forensic tracking center panel:

PowerShell
logpulse
Registered Local Diagnostic Controls
[H]: Toggles your interactive engineering documentation overlay manual panels.

[1]: Directs the forensic module to harvest administrative system authentication metrics.

[2]: Queries local raw network adapter interfaces to inventory active network connections.

[3]: Audits background processes to identify masqueraded system binaries.

[4]: Reviews structural configuration profile records and user account registries.

[5]: Maps scheduler systems to discover unauthorized cron persistence setups.

[Q]: Safely unmounts pipeline listeners and closes interface session bounds.

Security Audit Disclaimer
This tracking framework is explicitly built for:

Local forensic infrastructure monitoring.

Academic SIEM rule development and event normalization labs.

Authorized defense posturing and network compliance validation cycles.

Project Engineering Status
[x] Restructured into an isolated src/ layout ecosystem.

[x] Preserved all multi-threaded ingestion logic and event loops.

[x] Standardized pyproject.toml entry point hooks and mappings.

[x] Verified decoupled rules/ matching paths.

Author: Jon Bytyqi

SIEM & Forensic Logging Infrastructure Project