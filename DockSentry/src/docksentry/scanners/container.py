#!/usr/bin/env python3
import json
import asyncio
import platform
from typing import List, Dict, Any
from docksentry.scanners.base import BaseScanner

class LiveContainerScanner(BaseScanner):
    """
    Evaluates running states of Docker or Podman containers
    by querying engine introspection layers asynchronously.
    """
    async def scan(self, target_names: List[str]) -> List[Dict[str, Any]]:
        findings = []
        use_shell = True if platform.system() == "Windows" else False
        
        # Detect environment daemon runtime state
        runtime = "docker"
        try:
            check_podman = await asyncio.create_subprocess_exec(
                "podman", "--version", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await check_podman.wait()
            if check_podman.returncode == 0:
                runtime = "podman"
        except Exception:
            runtime = "docker"

        for name in target_names:
            if name == "all" or name == "*":
                # Discover active infrastructure workloads dynamically
                cmd = [runtime, "ps", "-a", "--format", "json"]
                try:
                    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                    stdout, _ = await proc.communicate()
                    if proc.returncode == 0 and stdout:
                        raw_lines = stdout.decode().strip()
                        if raw_lines:
                            # Handle different json outputs between engines
                            try:
                                data = json.loads(raw_lines)
                                names_extracted = [c.get("Names", ["unknown"])[0] if isinstance(c.get("Names"), list) else c.get("Names", "unknown") for c in data]
                                findings.extend(await self._evaluate_nodes(runtime, names_extracted))
                            except json.JSONDecodeError:
                                # Fallback logic line matching
                                pass
                except Exception:
                    pass
            else:
                findings.extend(await self._evaluate_nodes(runtime, [name]))
                
        return findings

    async def _evaluate_nodes(self, runtime: str, nodes: List[str]) -> List[Dict[str, Any]]:
        local_findings = []
        for node in nodes:
            if not node or node == "unknown": continue
            cmd = [runtime, "inspect", node]
            try:
                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                stdout, _ = await proc.communicate()
                if proc.returncode != 0 or not stdout: continue
                
                inspect_data = json.loads(stdout.decode())[0]
                config = inspect_data.get("Config", {})
                host_config = inspect_data.get("HostConfig", {})

                # Execution State Evaluation Blocks
                if host_config.get("Privileged", False):
                    local_findings.append(self.build_finding("DS-CIS-4.1", node))

                user_field = config.get("User", "")
                if user_field in ["", "0", "root", "0:0"]:
                    local_findings.append(self.build_finding("DS-CIS-4.3", node))

                if host_config.get("Memory", 0) == 0:
                    local_findings.append(self.build_finding("DS-CIS-4.4", node))

                if host_config.get("NetworkMode", "").lower() == "host":
                    local_findings.append(self.build_finding("DS-CIS-4.7", node))

                if host_config.get("PidMode", "").lower() == "host":
                    local_findings.append(self.build_finding("DS-CIS-4.9", node))

                if not host_config.get("ReadonlyRootfs", False):
                    local_findings.append(self.build_finding("DS-CIS-4.10", node))

                # Deep Scan Host Mount Leakage Points
                mounts = inspect_data.get("Mounts", []) or []
                for m in mounts:
                    src = m.get("Source", "").lower()
                    dest = m.get("Destination", "").lower()
                    if "docker.sock" in dest or "podman.sock" in dest or "docker.sock" in src:
                        local_findings.append(self.build_finding("DS-CIS-4.2", node))
                    if any(p in src for p in ["/etc", "/root", "c:\\windows", "/var/log"]):
                        local_findings.append(self.build_finding("DS-CIS-4.6", node))

            except Exception:
                pass
        return local_findings