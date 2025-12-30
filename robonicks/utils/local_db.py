import sqlite3
import os
from pathlib import Path

class LocalDB:
    def __init__(self):
        self.base_path = Path.home() / "AppData" / "Local" / "IVD"
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Use same DB as MinimalDB for consistency
        self.db_path = self.base_path / "client_data.db"
        self.conn = sqlite3.connect(self.db_path)
        # Memory Optimization Pragma
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA cache_size=0;") # Disable cache for low RAM
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            distributor_name TEXT,
            distributor_code TEXT,
            activated INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)

        self.conn.commit()

    # Check activation
    def is_activated(self):
        """Check activation status from local backend API"""
        try:
            import requests
            response = requests.get("http://127.0.0.1:8001/activation/check", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get("activated", False)
        except:
            pass
        cursor = self.conn.cursor()
        cursor.execute("SELECT activated FROM activation WHERE activated = 1 LIMIT 1;")
        row = cursor.fetchone()
        return row is not None

    # Save Activation
    def save_activation(self, name, code):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM activation;")  # keep only one row
        cursor.execute(
            "INSERT INTO activation (distributor_name, distributor_code, activated) VALUES (?, ?, 1)",
            (name, code)
        )
        self.conn.commit()

