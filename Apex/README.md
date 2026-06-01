# ⚡ Apex - Remote Linux Post-Exploitation & Forensic Auditor

> **Asynchronous Socket-Driven Post-Exploitation Enumeration & Threat Hunting Framework**

---

# 🏗️ Project Overview

Apex is a high-performance, decoupled client-server security auditing framework designed for targeted Linux host surveillance and vulnerability reconnaissance.

The architecture separates operational boundaries cleanly to streamline multi-target audits:

- **Listener (C2 Console)** → Administrative orchestration console deployed globally on the analyst workstation.
- **Agent (Target Utility)** → Automated standalone host execution utility designed to compile volatile target metrics.

The framework optimizes target inspection through rapid privilege auditing, memory-space reconnaissance, scheduled task inspection, and structured telemetry streaming over raw TCP sockets using JSON transport matrices.

---

# ⚡ Key Features

## Decoupled Stream Processing
Uses non-blocking socket buffer managers to safely transport structured JSON payloads without interface congestion or fragmented buffer corruption.

## Automated Privilege Reconnaissance
Programmatically identifies:
- SUID/SGID binaries
- Passwordless sudo configurations
- Root execution contexts
- Privileged escalation vectors

## Volatile Host Analytics
Performs active system reconnaissance including:
- Process inventory tracking
- Memory-space visibility
- Execution path inspection
- Suspicious process correlation

## Rich Live Analytics UI
Renders live telemetry, active findings, and severity classifications using thread-safe Rich terminal tables.

## Zero-Dependency Agent Design
The remote agent is engineered using native Python libraries (`socket`, `subprocess`, `os`, `json`). This ensures full cross-compatibility with restrictive, legacy, or minimally provisioned target Linux environments without installing external packages.

---

# 📁 Project Architecture & Layout

Apex is packaged using modern packaging specifications to allow context-independent execution of the listening suite while keeping the agent highly portable:

```text
Apex/
│
├── pyproject.toml         # System installation and entry-point definition
├── listener.py            # Pristine core orchestration ingestion logic
├── apex_launcher.py       # Context-aware environment boundary anchor module
├── apex_agent.py          # Standalone, loose deployable forensic target agent
├── requirements.txt       # Local workstation interface dependencies
└── __init__.py
⚡ Installation & Global DeploymentApex uses modern Python packaging conventions to establish a universal system-wide shortcut alias for the monitoring console while leaving the target agent unbundled and portable.1. Workstation InstallationOpen your terminal shell window inside your root Apex/ directory workspace and link the application hooks locally using developer editable mode:

PowerShell
python -m pip install -e .

2. Launch the Control Tower (Listener)Once installed, you can trigger the interactive telemetry console from any active directory path on your machine using the global execution alias:

PowerShell
apex-listener

Note: The listener defaults to port 9095. Ensure your network firewalls allow inbound traffic on this interface.3. Deploy the Inspection Agent (Target Host)Because the agent utility (apex_agent.py) remains standalone, lightweight, and loose, transfer it directly to your target Linux audit node and fire it up manually via native python:

Bashpython3 
apex_agent.py

📡 Pipeline Socket ProtocolTelemetry is serialized into structured JSON lines delimited by trailing newline characters (\n) to prevent socket fragmentation during high-throughput operations.Example PacketJSON{
  "type": "FINDING",
  "data": {
    "category": "SUID",
    "severity": "HIGH",
    "item": "Setuid binary discovered: /usr/bin/chfn"
  }
}
🎯 Audit Engine VectorsVector ModuleAnalysis StrategyRisk FocusSystem ProfilingKernel tracking, hostname mapping, user context checksEnvironment validationVolatile AuditingActive process and execution path inspectionThreat trackingSUID/SGID MappingElevated binary discovery scansPrivilege escalation vectorsSudo Configuration/etc/sudoers inspectionAdministrative weaknessesWrite Permission AnalysisWorld-writable path discoverySystem manipulation risks

⚙️ Internal Core ModulesAdministration Listener FrameworkThe administrative console component handles:TCP socket ingestion via apex_launcher.py directory containment tracking.Structured JSON parsing loop blocks.Real-time telemetry dashboard rendering.Severity classification mappings and thread-safe console interface updates.Forensic Agent FrameworkThe remote agent processes non-interactively on the target node to extract:Linux privilege reconnaissance matrix tracks.File-system world-writable auditing vectors.Native process space analysis and /etc/sudoers policy evaluations.High-efficiency result serialization strings.

📊 Telemetry DesignApex streams findings in real time using:JSON line serialization vectorsBuffered socket pipelinesIncremental live UI updatesSeverity-based classification handlingThis allows the framework to maintain stable performance under heavy audit workloads.

🛡️ Security Audit NoticeThis software toolkit is developed strictly for:Authorized infrastructure security auditingAcademic laboratory environmentsDefensive blue-team engineeringThreat hunting and malware researchUnauthorized deployment or usage against infrastructure without explicit authorization may violate regional or international computer security laws.

🚀 Verification Checklist[x] Global package installation architecture verified[x] Unique context-aware execution launcher apex_launcher.py integrated[x] Structured JSON socket transport documented[x] Rich terminal telemetry interface documented[x] Loose target deployment model verified for raw apex_agent.py operations[x] Modern pyproject.toml environment blueprint finalized

👨‍💻 Author
Jon Bytyqi Apex Remote Forensic Operations Framework — Core Architecture v1.0.0