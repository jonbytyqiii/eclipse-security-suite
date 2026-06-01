# 🐉 Dragon Interceptor (Project Eclipse)

> **Asynchronous Multi-Threaded Local Area Network Auditing & Protocol Visibility Framework**

---

# 🏗️ Project Overview

Dragon Interceptor is a high-performance, local area network auditing and protocol visibility framework engineered in Python. It provides network administrators and defensive security practitioners with high-visibility, real-time diagnostic insight into ambient link-local broadcast resolution traffic (`LLMNR` and `NetBIOS NBT-NS`) traversing local subnet infrastructure.

The framework captures local broadcast name requests, analyzes passive hostname discovery telemetry, and processes ambient identity mapping requests using non-blocking asynchronous hooks.

---

# ⚡ Core Technical Features

### 1. Real-Time Terminal Interface (TUI)

Built on the `rich` console rendering framework to present immediate network telemetry, parsed traffic tables, and live protocol visibility without terminal clutter or rendering instability.

### 2. Resilient Low-Level Packet Processing

Designed using predictive length-offset parsing strategies inside custom extraction sub-engines (`modules/parser.py`) to harden packet dissectors against malformed traffic, truncated frames, and corrupted packet structures.

### 3. Environmental Self-Healing Checks

Performs proactive host interrogation during launch to safely detect missing runtime system components (such as Npcap or libpcap), outputting operator-friendly diagnostics instead of raw traceback execution failures.

### 4. Dual Sniffer / Simulation Architecture

Supports both production-grade packet interception via raw interface sockets and isolated simulation workflows (`modules/sniffer.py`) for safe classroom demonstrations, local lab validation, and controlled educational environments.

---

# 📁 Project Architecture & Layout

Dragon Interceptor is structured cleanly as an isolated, globally deployable package within the `eclipse` framework. It utilizes a dedicated launcher to safely anchor paths so configuration attributes load flawlessly from any folder space:

```text
BreachDeck/
│
├── pyproject.toml         # Central packaging layout and global command mapping
├── config.yaml            # Operational parameter matrices & simulation states
├── interceptor.py         # Pristine core packet ingestion layer logic
├── breachdeck_launcher.py # Unique context-aware environment path directory anchor
├── requirements.txt       # Global third-party dependency installation manifest
├── README.md              # Project documentation matrix
│
└───modules/               # High-Fidelity Network Protocol Sub-Engines
    ├── parser.py          # Data stream parser and structural payload identifier
    └── sniffer.py         # Network socket listener and simulation handler
```

---

# 🛠️ Driver Prerequisites & Settings

Before deploying Dragon Interceptor, ensure the host system satisfies the following low-level operating kernel driver requirements.

---

## Windows Platforms

Requires `Npcap` installed on the host operating system kernel.

### Official Download

https://npcap.com/

### Critical Setup Option

Ensure the following option is explicitly enabled during the installation wizard:

```text
Install Npcap in WinPcap API-compatible mode
```

---

## Linux Platforms

Requires the following runtime dependencies:

* `libpcap-dev`
* Root privileges (`sudo`)
* Raw socket capabilities (`CAP_NET_RAW`)

Install required libraries:

```bash
sudo apt update && sudo apt install libpcap-dev
```

---

# 🚀 Installation & Global Deployment

The framework utilizes a modern standard package environment layout enabling universal terminal execution mapping while keeping source files clean and modular.

---

## 1. Global Setup

Open an elevated terminal or PowerShell prompt, navigate into the root project directory, and compile the application locally using editable package mode:

```powershell
cd BreachDeck
python -m pip install -e .
```

---

## 2. Running Globally

Once compiled, the package maps a unified global terminal shortcut command (`breachdeck`) into the system path environment.

Launch the framework directly from any active directory path.

### Windows PowerShell (Administrator)

```powershell
breachdeck
```

### Linux Terminal (Root Context)

```bash
sudo breachdeck
```

---

# ⚙️ Runtime Tuning & Simulation Profiles

Operational behavior, packet capture thresholds, and offline educational states can be managed directly through the local `config.yaml` configuration matrix.

```yaml
simulation_modes:
  enable_demo_simulation: true
```

---

## Parameter Configuration

| Parameter                | Type    | Objective Description                                                                                                                 |
| ------------------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `enable_demo_simulation` | Boolean | Enables isolated educational loop blocks simulating LLMNR and NetBIOS traffic arrays without binding to active production interfaces. |

---

# 📡 Protocol Visibility Coverage

Dragon Interceptor continuously tracks, extracts, and reports:

* `LLMNR` (Link-Local Multicast Name Resolution) queries over UDP port `5355`
* `NBT-NS` (NetBIOS Name Service) requests over UDP port `137`
* Ambient local subnet broadcast identification signatures
* Passive hostname mapping telemetry
* Identity request correlation streams
* Source endpoint mapping visibility

---

# 📊 Administrative Disclosures

> 📝 **Operational Design Note**
>
> Passive auditing utilities do not inherently capture authenticated NetNTLMv2 challenge-response exchanges under standard network conditions.
>
> Real credential negotiation occurs during authenticated service transactions such as SMB, LDAP, or HTTP authentication workflows.
>
> Dragon Interceptor focuses strictly on passive protocol visibility, hostname resolution diagnostics, and local broadcast telemetry analysis.
>
> Advanced laboratory research simulations may combine this passive visibility engine alongside isolated relay architecture demonstrations.

---

# 🔒 Security & Stability Design Goals

* Defensive-first network visibility tracking paradigms
* Stable packet parsing layout bounds under malformed traffic anomalies
* Safe dependency validation layers to minimize runtime crashes
* Cross-platform packet inspection compatibility across Windows and Linux systems
* Clean asynchronous event processing architecture
* Operator-readable telemetry rendering workflows

---

# 📄 Licensing Terms

Distributed under the terms and conditions of the MIT License.

---

# 👤 Author

**Jon Bytyqi**
Dragon Interceptor Network Visibility Framework — Framework Architecture v1.0.0
