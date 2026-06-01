#!/usr/bin/env python3
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseScanner(ABC):
    """
    Abstract Base Class enforcing consistent contracts 
    across all custom plugin security assessment components.
    """
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules

    @abstractmethod
    async def scan(self, target: Any) -> List[Dict[str, Any]]:
        pass

    def build_finding(self, rule_id: str, target_node: str, specific_context: str = "") -> Dict[str, Any]:
        for r in self.rules:
            if r["id"] == rule_id:
                return {
                    "id": r["id"],
                    "name": r["name"],
                    "severity": r["severity"],
                    "category": r.get("category", "General"),
                    "mapping": r.get("mapping", "N/A"),
                    "target": target_node,
                    "desc": specific_context or r["description"],
                    "remediation": r["remediation"]
                }
        return {
            "id": rule_id,
            "name": "Unknown Policy Infraction",
            "severity": "MEDIUM",
            "category": "General",
            "mapping": "N/A",
            "target": target_node,
            "desc": f"Policy breach identified without localized metadata tracking block. Context: {specific_context}",
            "remediation": "Review system requirements and lock down authorization privileges."
        }