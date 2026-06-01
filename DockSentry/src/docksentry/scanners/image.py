#!/usr/bin/env python3
import asyncio
import json
import shutil
from typing import List, Dict, Any
from docksentry.scanners.base import BaseScanner

class TrivyImageScanner(BaseScanner):
    """
    Acts as an abstraction wrapper around system installations 
    of Trivy to catch structural CVE data arrays dynamically.
    """
    async def scan(self, image_name: str) -> List[Dict[str, Any]]:
        findings = []
        if not shutil.which("trivy"):
            # Graceful Degradation Strategy if external system binary calls are absent
            return [self.build_finding("DS-EXT-WARN", image_name, "Local system binary path dependencies for Trivy are missing. Skipping CVE analysis checks.")]

        cmd = ["trivy", "image", "--format", "json", "--severity", "HIGH,CRITICAL", image_name]
        try:
            proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, _ = await proc.communicate()
            
            if proc.returncode == 0 and stdout:
                raw_data = json.loads(stdout.decode())
                results = raw_data.get("Results", []) or []
                for res in results:
                    vulns = res.get("Vulnerabilities", []) or []
                    for v in vulns[:5]: # Cap output display logs seamlessly
                        findings.append({
                            "id": v.get("VulnerabilityID", "CVE-UNKNOWN"),
                            "name": f"Image Flaw: {v.get('PkgName', 'System Package')}",
                            "severity": v.get("Severity", "HIGH"),
                            "category": "CVE-Vulnerability",
                            "mapping": "NVD NIST",
                            "target": image_name,
                            "desc": v.get("Title", "Unresolved software package vulnerability discovered within layers."),
                            "remediation": f"Upgrade package reference {v.get('PkgName')} past operational version boundaries: {v.get('FixedVersion', 'Latest Available')}"
                        })
        except Exception as e:
            pass
        return findings