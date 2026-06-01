# ShatterEngine (RedDevil) v3.0 - High-Performance Cryptographic Framework

## Overview

ShatterEngine (RedDevil) is a modular, high-performance Python-based cryptographic framework engineered for granular forensic structural verification, data transformation validation, and compliance-driven password policy auditing. Leveraging advanced multiprocessing workers, RedDevil evaluates cryptographic matrices efficiently across modern heavy standards and classic hashes.

---

## Technical Architecture

* **Multi-Threaded Workloads:** Built around an asynchronous execution engine utilizing `ProcessPoolExecutor` to handle computationally heavy analysis chains across multiple isolated logical processes.
* **Granular Target Fingerprinting:** Features a signature matching engine capable of running instant regex validation metrics to infer hash categories and structural classifications.
* **Checkpoint Persistence Engine:** Integrated with a resilient SQLite transactional storage tracking system (`sessions.db`) allowing runtime session state logging, mutation tracking, and pause/resume execution capabilities.
* **Rule and Mutation Engine:** Features a rules dictionary layout that applies industry-standard structural string transformations, character prepending/appending, and leetspeak translation routines.
* **Polished Telemetry Dashboard:** Utilizes the `Rich` framework console components to deliver clear telemetry reporting, terminal interface layouts, and tracking distributions.

---

## Standalone Installation & Deployment

To deploy ShatterEngine as a decoupled module outside the core Eclipse parent suite environment, instantiate a local Python virtual environment inside your tool folder:

```powershell
# Create and engage isolated runtime terminal container
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install package locally in editable development mode
pip install -e .
Core Operations Guide
1. Interactive Analysis Wizard
Launch the automated prompt matrix with zero configuration flags:

PowerShell
reddevil
2. Structured Command Suite Execution
Provide discrete evaluation targets directly via the orchestration command suite flags:

PowerShell
reddevil run --target "81dc9bdb52d04dc20036dbd8313ed055" --mask "?d?d?d?d"
3. Core Engine Diagnostic Evaluation
Run benchmarking suites to test system throughput and calculate maximum process pool execution analytics:

PowerShell
reddevil run --benchmark
Compliance and Policy Verification Disclaimer
This framework is built strictly for:

Academic lab data parsing and structural mapping assignments.

Administrative compliance validation and system account audit loops.

Authorized local forensic verification protocols.

Defensive vulnerability testing boundaries.

Always secure clear explicit operational clearance from systems stakeholders before conducting auditing procedures on active verification pipelines.

Project Engineering Status
[x] Restructured to isolated src/ modular layout packaging standards.

[x] Implemented absolute target configuration path safety loops.

[x] Standardized pyproject.toml dependency mapping and metadata records.

[x] Verified reddevil namespace path mappings across sub-modules.

Author: Jon Bytyqi

Cryptographic Forensic Framework Engineering Initiative