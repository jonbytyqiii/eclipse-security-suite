DockSentry (v2.0.0)

An Enterprise-Grade Cloud Native & Container Security Posture Management (CSPM) Platform.

🛠️ System Architecture & Layout

DockSentry uses a modern, standardized Python src/ directory layout to ensure clean dependency isolation, seamless package discovery, and native cross-platform execution compatibility.

DockSentry/
├── pyproject.toml              # Build-system definition & package metadata
├── README.md                   # Platform documentation
├── requirements.txt            # Static dependency manifest
└── src/
    └── docksentry/
        ├── __init__.py         # Package initialization
        ├── main.py             # Core application entry point & dashboard loop
        └── rules.yaml          # Security posture evaluation matrix & baseline rules
⚡ Installation & Global Registration

DockSentry is packaged using modern PEP 517 build standards. You can install it locally in editable mode, which registers the docksentry executable across your entire system environment path natively.

1. Developer Setup (Editable Mode)

Navigate to the root directory containing your pyproject.toml and execute:

pip install -e .

2. Verify Global Execution Path

Once registered, verify that your environment correctly routes the standalone binary wrapper by checking its location or launching it from any arbitrary folder directory:

# Fire the naked command from anywhere on the system
docksentry
🚀 Operation & Playbook Commands

When launched, DockSentry initializes its high-fidelity Core Systems Deployment Dashboard. The toolkit handles real-time container runtime ingestion and securely guides the operator through five distinct assessment vectors.

Core Modules Matrix
1. Run Full Environmental Security Audit

Evaluates container context configurations against secure baselines, searching for namespace isolation violations, root privileges, and storage safety anomalies.

2. Scan Explicit Targets / Specific Containers

Targets a localized subset of active containers by identifier or name tags to isolate transient infrastructure shifts.

3. Compile Hardened Infrastructure Composition Matrix

Generates actionable code-hardening snippets and secure Docker Compose translation properties based on discovered misconfigurations.

4. View Previous Tactical Assessment Report

Parses and renders previous tactical evaluations directly in the terminal window without data loss or terminal screen corruption.

5. Terminate Application Context Interface

Gracefully tears down runtime engine loops and hands system control back to the orchestrator environment.

🧩 Command Line Switches
Usage: docksentry [OPTIONS]

Options:
  --target [auto|docker|podman]   Manually force audit context mapping targets.
  --export                        Compile machine-readable JSON assets and HTML report dashboards.
  --quiet                         Mute post-audit code hardening compose snippet engines.
  --help                          Show this help manual sequence and exit.
🛡️ Telemetry & Security Baseline Engine

DockSentry evaluates your container environment using the configurations defined in src/docksentry/rules.yaml.

The engine performs dynamic telemetry tracking across the following critical risk fields:

Namespace Isolation Constraints

Verifies that containers maintain independent execution boundaries from the host kernel.

Privileged Mode Allocation

Flags risky container configurations running with extended administrative host privileges.

Mounted Host Sockets

Audits dangerous exposures such as mounting the host's /var/run/docker.sock internally.

User Context Capabilities

Evaluates if processes inside containers are explicitly dropped down to non-root accounts.

Resource Scheduling Limits

Validates that maximum CPU and memory boundaries are set to prevent localized Denial of Service (DoS) constraints.

📦 Example Usage
Standard Runtime Scan
docksentry
Force Docker Runtime Mapping
docksentry --target docker
Export Reports
docksentry --export
Quiet Operational Mode
docksentry --quiet
📊 Generated Output Artifacts

When export functionality is enabled, DockSentry can generate:

Machine-readable JSON assessment reports
Human-readable HTML security dashboards
Hardened Docker Compose remediation snippets
Tactical audit summaries for compliance review
🔒 Security Philosophy

DockSentry follows a defensive-first infrastructure validation model focused on:

Least privilege enforcement
Runtime exposure minimization
Hardened container isolation
Misconfiguration discovery
Secure-by-default operational posture

The platform is designed for security engineers, DevSecOps operators, cloud administrators, and container platform auditors seeking rapid visibility into runtime security drift.

📄 License

This project is licensed under the terms of the MIT License.