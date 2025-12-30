import sqlite3
import json
from pathlib import Path
from datetime import datetime

class MinimalDB:
    def __init__(self):
        # Use a distinct Client DB file
        self.base_path = Path.home() / "AppData" / "Local" / "IVD"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.base_path / "client_data.db"
        
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row # Access columns by name
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create a simple flat table for results
        # We store complex structures as JSON text
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results_local (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sample_id TEXT NOT NULL,
            patient_id TEXT,
            test_name TEXT,
            result_value TEXT,
            hl7_message TEXT,
            astm_message TEXT,
            
            -- Store the full result dictionary as JSON for potential reconstruction
            raw_data_json TEXT,
            
            synced INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create stock usage table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS local_stock_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            batch_id TEXT,
            quantity_used INTEGER,
            synced INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create machine settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS machine_settings (
            id INTEGER PRIMARY KEY,
            setting_key TEXT UNIQUE NOT NULL,
            setting_value TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        conn.close()

    def insert_result(self, sample_id, patient_id, test_name, result_value, hl7_msg, astm_msg, raw_data_dict):
        """Insert a new test result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
            INSERT INTO test_results_local 
            (sample_id, patient_id, test_name, result_value, hl7_message, astm_message, raw_data_json, synced)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                sample_id,
                patient_id,
                test_name,
                result_value,
                hl7_msg,
                astm_msg,
                json.dumps(raw_data_dict, default=str) # Handle dates in json
            ))
            
            new_id = cursor.lastrowid
            conn.commit()
            print(f"MinimalDB: Saved result ID {new_id} for Sample {sample_id}")
            return new_id
        except Exception as e:
            print(f"MinimalDB Error: {e}")
            return None
        finally:
            conn.close()

    def get_unsynced_results(self):
        """Get all results that haven't been sent to server"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_results_local WHERE synced = 0")
        rows = cursor.fetchall()
        
        results = [dict(row) for row in rows]
        conn.close()
        return results

    def mark_synced(self, local_id):
        """Mark a record as synced"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE test_results_local SET synced = 1 WHERE id = ?", (local_id,))
        conn.commit()
        conn.close()

    # --- Stock Usage Methods ---

    def record_usage(self, batch_id, quantity):
        """Record usage of stock (e.g., 1 test used)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO local_stock_usage (batch_id, quantity_used, synced)
            VALUES (?, ?, 0)
            """, (batch_id, quantity))
            conn.commit()
            print(f"MinimalDB: Recorded usage of {quantity} for Batch {batch_id}")
        except Exception as e:
            print(f"MinimalDB Stock Error: {e}")
        finally:
            conn.close()

    def get_unsynced_usage(self):
        """Get unsynced stock usage"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM local_stock_usage WHERE synced = 0")
        rows = cursor.fetchall()
        
        results = [dict(row) for row in rows]
        conn.close()
        return results

    def mark_usage_synced(self, usage_id):
        """Mark usage as synced"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE local_stock_usage SET synced = 1 WHERE id = ?", (usage_id,))
        conn.commit()
        conn.close()

    # --- Settings Methods ---

    def get_setting(self, key, default=None):
        """Get a setting value by key"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT setting_value FROM machine_settings WHERE setting_key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        
        return row['setting_value'] if row else default

    def set_setting(self, key, value):
        """Set or update a setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
        INSERT INTO machine_settings (setting_key, setting_value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(setting_key) DO UPDATE SET 
            setting_value = excluded.setting_value,
            updated_at = excluded.updated_at
        """, (key, value, datetime.now()))
        
        conn.commit()
        conn.close()
        print(f"MinimalDB: Setting '{key}' = '{value}'")
