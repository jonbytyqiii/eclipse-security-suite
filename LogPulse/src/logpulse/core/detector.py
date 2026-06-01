#!/usr/bin/env python3
import os
import re
import yaml
import time
from collections import defaultdict, deque

class DynamicCorrelationEngine:
    def __init__(self, rules_directory):
        self.rules = self.load_rules_signature_registry(rules_directory)
        self.state_matrices = defaultdict(lambda: deque())

    def load_rules_signature_registry(self, path):
        rules_pool = []
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.endswith((".yaml", ".yml")):
                    with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                        try:
                            rule_data = yaml.safe_load(f)
                            if rule_data:
                                rules_pool.append(rule_data)
                        except Exception:
                            continue
        return rules_pool

    def evaluate(self, event) -> list:
        """Evaluates live events against volatile state tracking structures"""
        alerts = []
        now = time.time()

        for rule in self.rules:
            cond = rule.get("condition", {})
            cond_type = cond.get("type")
            target_field = cond.get("field", "raw_message")
            match_pattern = cond.get("match", "")

            # 1. Sliding-Window Threshold / Correlation Rules (e.g. Brute Force)
            if cond_type == "threshold":
                val_to_check = getattr(event, target_field, "")
                if val_to_check == match_pattern:
                    key = f"{rule['rule_id']}_{event.source_ip}"
                    self.state_matrices[key].append(now)
                    
                    # Dynamically adjust window from rule if defined, else defaults to 10s
                    window_seconds = rule.get("condition", {}).get("window", 10)
                    threshold = rule.get("condition", {}).get("threshold", 5)
                    
                    while self.state_matrices[key] and now - self.state_matrices[key][0] > window_seconds:
                        self.state_matrices[key].popleft()
                        
                    if len(self.state_matrices[key]) >= threshold:
                        self.state_matrices[key].clear()
                        alerts.append(rule)

            # 2. Signature Regex Rules (e.g. Directory Traversal, Web Shells)
            elif cond_type == "regex":
                val_to_check = getattr(event, target_field, "")
                if re.search(match_pattern, val_to_check, re.IGNORECASE):
                    alerts.append(rule)

        return alerts