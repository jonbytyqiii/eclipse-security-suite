Markdown
# Vortex Raptor v2.0.0 - Next-Gen Attack Surface Mapper

## Overview
Vortex Raptor is a multi-threaded, high-concurrency tactical asset mapping engine designed to uncover target infrastructure elements via dual-vector path reconnaissance (Subdomain Discovery and Directory Fuzzing Analysis).

---

## Technical Architecture
* **Dual Reconnaissance Strategies:** Integrates both passive log query matrices (Certificate Transparency scraping via crt.sh) and high-speed dictionary brute-force mechanisms.
* **Smart Filtering Engine:** Automatically baseline-profiles target systems upon initiation to identify and mask false-positive wildcard response traps.
* **Advanced Intercept Layer:** Safe runtime state management handling that traps `CTRL+C` keyboard interrupts, pausing worker threads safely to allow live filtering optimization changes mid-scan.
* **Rich UI Tracking:** Leverages progress track bars and colored validation tabular sheets for maximum readability.

---

## Installation & Deployment

Link the tool into your local system execution path globally so that it can be launched from any terminal environment or script framework simply by running the `raptor` command sequence.

Navigate to the project directory housing `pyproject.toml` and trigger an editable development build:

```bash
pip install -e .
Command Line Metaphors
Interactive Wizard Core Interface
Launch the interactive configuration interface terminal by running:

Bash
raptor
Automation Engine CLI Pipes
To run automated target audits directly from command arguments:

Bash
# Map active subdomains using hybrid passive/active brute-force models
raptor --target example.com --mode sub --strategy 3

# High-concurrency directory path search checking specific validation states
raptor --target [https://example.com](https://example.com) --mode dir --include 200,301,302 --ext php,txt --threads 50
Author
Jon Bytyqi Vortex Matrix Attack Surface Mapping Utility