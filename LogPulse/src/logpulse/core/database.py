#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

class AlertDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self.initialize_schema()

    def initialize_schema(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS security_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    rule_id TEXT,
                    title TEXT,
                    severity TEXT,
                    mitre_mapping TEXT,
                    source_ip TEXT,
                    raw_payload TEXT
                )
            """)
            conn.commit()

    def save_alert(self, rule_id, title, severity, mitre, ip, raw):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO security_alerts (timestamp, rule_id, title, severity, mitre_mapping, source_ip, raw_payload)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), rule_id, title, severity, mitre, ip, raw))
            conn.commit()