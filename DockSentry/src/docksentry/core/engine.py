#!/usr/bin/env python3
import os
import logging
import asyncio
from typing import List, Dict, Any
import yaml

from docksentry.scanners.container import LiveContainerScanner
from docksentry.scanners.dockerfile import DockerfileScanner
from docksentry.scanners.k8s import KubernetesManifestScanner
from docksentry.scanners.image import TrivyImageScanner

logger = logging.getLogger("DockSentryEngine")

class ContainerAuditEngine:
    """
    Asynchronous Core Engine coordinating specialized scanners 
    across local container platforms, static manifests, and image registries.
    """
    def __init__(self, rules_path: str = None):
        self.rules_path = rules_path or os.path.join(os.path.dirname(__file__), "rules.yaml")
        self.rules = self._load_rules()
        self.findings: List[Dict[str, Any]] = []

    def _load_rules(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(self.rules_path):
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("rules", [])
            return []
        except Exception as e:
            logger.error(f"Failed to ingest compliance ruleset matrix: {str(e)}")
            return []

    def calculate_metrics(self, targeted_findings: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        eval_list = targeted_findings if targeted_findings is not None else self.findings
        total = len(eval_list)
        critical = sum(1 for f in eval_list if f["severity"] == "CRITICAL")
        high = sum(1 for f in eval_list if f["severity"] == "HIGH")
        medium = sum(1 for f in eval_list if f["severity"] == "MEDIUM")
        low = sum(1 for f in eval_list if f["severity"] == "LOW")

        # Dynamic Risk Scoring Algorithm
        deductions = (critical * 25) + (high * 15) + (medium * 7) + (low * 2)
        score = max(0, min(100, 100 - deductions))

        return {
            "total_flaws": total,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
            "compliance_score": score
        }

    async def execute_comprehensive_audit(self, targets: Dict[str, List[str]], status_cb=None) -> List[Dict[str, Any]]:
        """
        Orchestrates concurrent execution tasks across multi-vector environments.
        """
        self.findings.clear()
        tasks = []

        # 1. Active Containers Engine Initialization
        if "containers" in targets and targets["containers"]:
            if status_cb: status_cb("Launching Live Runtime Assessment Engine...")
            c_scanner = LiveContainerScanner(self.rules)
            tasks.append(c_scanner.scan(targets["containers"]))

        # 2. Static Dockerfile Component Execution
        if "dockerfiles" in targets and targets["dockerfiles"]:
            if status_cb: status_cb("Initializing Static Dockerfile Parsing...")
            df_scanner = DockerfileScanner(self.rules)
            for df_path in targets["dockerfiles"]:
                tasks.append(df_scanner.scan(df_path))

        # 3. Kubernetes Orchestration Manifest Analysis
        if "k8s" in targets and targets["k8s"]:
            if status_cb: status_cb("Analyzing Kubernetes Declarative Manifest Layers...")
            k8s_scanner = KubernetesManifestScanner(self.rules)
            for k8s_path in targets["k8s"]:
                tasks.append(k8s_scanner.scan(k8s_path))

        # 4. External CVE Image Analyzer Trigger Integration
        if "images" in targets and targets["images"]:
            if status_cb: status_cb("Querying Vulnerability Registries...")
            img_scanner = TrivyImageScanner(self.rules)
            for img_name in targets["images"]:
                tasks.append(img_scanner.scan(img_name))

        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for res in results:
                if isinstance(res, list):
                    self.findings.extend(res)
                elif isinstance(res, dict):
                    self.findings.append(res)
                elif isinstance(res, Exception):
                    logger.error(f"Scanner sub-component execution error: {str(res)}")

        if status_cb: status_cb("Audit complete. Writing results to storage pipelines.")
        return self.findings