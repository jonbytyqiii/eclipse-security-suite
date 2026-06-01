#!/usr/bin/env python3
import os
import re
from typing import List, Dict, Any
from docksentry.scanners.base import BaseScanner

class DockerfileScanner(BaseScanner):
    """
    Parses static Dockerfile configuration declarations
    to discover compile-time vulnerabilities before build phases.
    """
    async def scan(self, file_path: str) -> List[Dict[str, Any]]:
        findings = []
        if not os.path.exists(file_path):
            return findings

        target_label = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.splitlines()
            user_defined = False
            secret_keywords = ["passwd", "password", "api_key", "secret", "token", "private_key"]

            for idx, line in enumerate(lines, 1):
                cleaned = line.strip()
                if cleaned.startswith("#") or not cleaned:
                    continue

                # Rule Matching Matrix logic rules
                if cleaned.startswith("FROM"):
                    if any(bad in cleaned.lower() for bad in ["ubuntu:latest", "debian:latest", "centos:7"]):
                        findings.append(self.build_finding(
                            "DS-CIS-5.2", f"{target_label}:{idx}", 
                            f"Over-privileged OS base layer platform inherited: '{cleaned}'."
                        ))

                if cleaned.startswith("USER"):
                    if "root" not in cleaned.lower() and "0" not in cleaned.split():
                        user_defined = True

                if cleaned.startswith("ENV") or cleaned.startswith("ARG"):
                    if any(key in cleaned.lower() for key in secret_keywords) and not re.search(r'\$\{[A-Za-z0-9_]+\}', cleaned):
                        findings.append(self.build_finding(
                            "DS-CIS-5.1", f"{target_label}:{idx}",
                            f"Potential hardcoded administrative credentials exposed: '{cleaned}'."
                        ))

            if not user_defined:
                findings.append(self.build_finding(
                    "DS-CIS-4.3", target_label,
                    "No valid alternate non-privileged execution USER policy declared within the target build script."
                ))

        except Exception as e:
            pass

        return findings