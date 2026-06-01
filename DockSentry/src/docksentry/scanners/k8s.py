#!/usr/bin/env python3
import os
import yaml
from typing import List, Dict, Any
from docksentry.scanners.base import BaseScanner

class KubernetesManifestScanner(BaseScanner):
    """
    Performs deterministic syntax tree evaluation against structural 
    Kubernetes manifest charts to isolate orchestration deployment issues.
    """
    async def scan(self, file_path: str) -> List[Dict[str, Any]]:
        findings = []
        if not os.path.exists(file_path):
            return findings

        target_label = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                docs = yaml.safe_load_all(f)
                for doc in docs:
                    if not doc or not isinstance(doc, dict): continue
                    await self._parse_k8s_doc(doc, target_label, findings)
        except Exception:
            pass
        return findings

    async def _parse_k8s_doc(self, doc: Dict[str, Any], label: str, findings: List[Dict[str, Any]]):
        kind = doc.get("kind", "")
        # Standardize nested tree entry point extraction parsing arrays
        pod_spec = None
        if kind == "Pod":
            pod_spec = doc.get("spec", {})
        elif kind in ["Deployment", "ReplicaSet", "DaemonSet", "StatefulSet", "Job"]:
            pod_spec = doc.get("spec", {}).get("template", {}).get("spec", {})

        if not pod_spec: return

        # Validate Automount Service Account Token configuration rules
        if pod_spec.get("automountServiceAccountToken") is not False:
            findings.append(self.build_finding("DS-CIS-6.1", f"{label} [{kind}]"))

        containers = pod_spec.get("containers", []) or []
        for c in containers:
            c_name = c.get("name", "unnamed-container")
            sec_ctx = c.get("securityContext", {})
            
            if sec_ctx.get("privileged", False):
                findings.append(self.build_finding("DS-CIS-4.1", f"{label}://{c_name}"))
            
            if sec_ctx.get("runAsRoot") is not False and not sec_ctx.get("runAsNonRoot"):
                findings.append(self.build_finding("DS-CIS-4.4", f"{label}://{c_name}", "Container defaults to root authorization boundaries."))

            resources = c.get("resources", {})
            if not resources.get("limits", {}).get("memory") or not resources.get("limits", {}).get("cpu"):
                findings.append(self.build_finding("DS-CIS-4.4", f"{label}://{c_name}", "Workload definitions lack enforce-capped boundary blocks."))