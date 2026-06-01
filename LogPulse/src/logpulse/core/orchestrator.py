#!/usr/bin/env python3
import asyncio
import os
import time
import platform
from datetime import datetime

# Centralized absolute package imports
from logpulse.core.normalizer import LogEvent
from logpulse.core.detector import DynamicCorrelationEngine
from logpulse.core.database import AlertDatabase

class SIEMPipelineOrchestrator:
    def __init__(self, config, ui_callback):
        self.cfg = config
        self.ui_callback = ui_callback
        
        # Resolve absolute pathing relative to this file's folder location
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 1. Map SQLite Database Space Securely
        configured_db_path = self.cfg.get("global_settings", {}).get("alert_db", "storage/siem_alerts.db")
        self.db_path = os.path.normpath(os.path.join(base_dir, "../../../", configured_db_path))
        self.db = AlertDatabase(self.db_path)
        
        # 2. Map Rules Folder Matrix Securely
        configured_rules_dir = self.cfg.get("detection_parameters", {}).get("rules_directory", "rules")
        self.rules_path = os.path.normpath(os.path.join(base_dir, "../../../", configured_rules_dir))
        self.detector = DynamicCorrelationEngine(self.rules_path)
        
        self.is_running = False

    async def tail_log_stream(self, file_path, stream_type):
        """Asynchronously watches an active file on the file system for live modifications"""
        # Enforce absolute path resolution matching your core project directory
        if not os.path.isabs(file_path):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.normpath(os.path.join(base_dir, "../../../", file_path))

        # Dynamically build the directory architecture if it doesn't exist yet
        log_dir = os.path.dirname(os.path.abspath(file_path))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Generate a placeholder log stream file if missing to prevent loop hangs
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f: 
                f.write("# LogPulse Ingestion Pipe Initialized\n")

        # Open using low-level descriptor flags to enforce shared reading access states on Windows
        def shared_open(path, flags):
            return os.open(path, flags | os.O_RDONLY)

        with open(file_path, "r", opener=shared_open, errors="ignore") as f:
            f.seek(0, os.SEEK_END)  # Jump straight to the tail end of the file
            while self.is_running:
                line = f.readline()
                if not line:
                    await asyncio.sleep(0.1)  # Give CPU core slices breathing space
                    continue
                
                if line.strip() and not line.startswith("#"):
                    event = LogEvent(line, stream_type)
                    triggered_alerts = self.detector.evaluate(event)
                    
                    for rule in triggered_alerts:
                        self.db.save_alert(
                            rule_id=rule["rule_id"],
                            title=rule["title"],
                            severity=rule["severity"],
                            mitre=f"{rule['mitre_attack']['tactic']} ({rule['mitre_attack']['technique']})",
                            ip=event.source_ip,
                            raw=event.raw_message
                        )
                        
                        ui_alert_packet = {
                            "timestamp": event.timestamp,
                            "rule_id": rule["rule_id"],
                            "title": rule["title"],
                            "severity": rule["severity"],
                            "source_ip": event.source_ip,
                            "raw_payload": event.raw_message
                        }
                        self.ui_callback(ui_alert_packet)

    async def run_cache_purger(self):
        """Periodically reads configurations from config.yaml to flush old memory matrices"""
        purge_interval = self.cfg.get("detection_parameters", {}).get("purge_interval_seconds", 30)
        while self.is_running:
            await asyncio.sleep(purge_interval)
            now = time.time()
            for key in list(self.detector.state_matrices.keys()):
                while self.detector.state_matrices[key] and now - self.detector.state_matrices[key][0] > 10:
                    self.detector.state_matrices[key].popleft()

    async def boot_monitor_cluster(self):
        self.is_running = True
        tasks = []
        
        # Spin up the automatic cache purger as a background task
        tasks.append(asyncio.create_task(self.run_cache_purger()))
        
        for source in self.cfg.get("monitored_sources", []):
            path = os.path.normpath(source.get("path", ""))
            stream_type = source.get("format", "generic")
            
            if platform.system() != "Windows" and ("inetpub" in path or "System32" in path):
                continue
                
            tasks.append(asyncio.create_task(self.tail_log_stream(path, stream_type)))
            
        await asyncio.gather(*tasks)

    def shutdown_orchestrator(self):
        """Safely stops the background file tailing loops and cleans up resources"""
        self.is_running = False