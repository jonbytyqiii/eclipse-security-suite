#!/usr/bin/env python3
import yaml
from typing import Dict, Any, List

class RemediatingCodePatcher:
    """
    Generates tailored, immediately deployable Docker Compose structures 
    and infrastructure automation scripts directly from discovered vulnerabilities.
    """
    @staticmethod
    def generate_remediation_manifest(finding: Dict[str, Any]) -> str:
        target = finding.get("target", "app_service")
        # Sanitize label parsing formats seamlessly
        clean_target = target.split("://")[-1].split(":")[0].replace(".", "_")

        base_patch = {
            "version": "3.8",
            "services": {
                clean_target: {
                    "image": f"hardened_{clean_target}:latest",
                    "user": "10001:10001",
                    "read_only": True,
                    "security_opt": ["no-new-privileges:true", "seccomp=default"],
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": "0.50",
                                "memory": "512M"
                            }
                        }
                    },
                    "networks": ["isolated_secure_bridge"]
                }
            },
            "networks": {
                "isolated_secure_bridge": {
                    "driver": "bridge",
                    "internal": True
                }
            }
        }
        return yaml.dump(base_patch, default_flow_style=False)

    @staticmethod
    def construct_one_click_fix(findings: List[Dict[str, Any]]) -> str:
        """
        Synthesizes individual remediation strategies into a comprehensive docker-compose.yml setup.
        """
        master_services = {}
        for f in findings:
            target = f.get("target", "workload_node")
            clean_name = target.split("://")[-1].split(":")[0].replace(".", "_")
            if clean_name not in master_services:
                master_services[clean_name] = {
                    "image": f"hardened_{clean_name}:stable",
                    "user": "10001",
                    "read_only": True,
                    "deploy": {
                        "resources": {
                            "limits": {"cpus": "0.50", "memory": "512M"}
                        }
                    }
                }
        
        compose_output = {"version": "3.8", "services": master_services}
        return yaml.dump(compose_output, default_flow_style=False)