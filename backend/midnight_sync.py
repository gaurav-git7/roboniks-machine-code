import time
import sqlite3
import requests
import json
import os
from pathlib import Path
from datetime import datetime

# CONFIGURATION
# ---------------------------------------------------------
BACKEND_URL = "http://127.0.0.1:8001/api/v1/results/batch-upload"
SYNC_HOUR = 0  # Midnight (00:00)
SYNC_MINUTE_WINDOW = 5 # Run window (00:00 - 00:05)
CHECK_INTERVAL = 60 # Check every 60 seconds

# Path to Client DB (AppData)
CLIENT_DB_PATH = Path.home() / "AppData" / "Local" / "IVD" / "client_data.db"

def get_unsynced_results():
    """Fetch unsynced results from Local Client DB"""
    if not CLIENT_DB_PATH.exists():
        print(f"⚠️ Client DB not found at {CLIENT_DB_PATH}")
        return []

    try:
        conn = sqlite3.connect(CLIENT_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM test_results_local WHERE synced = 0")
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            # Map Row to Pydantic Model (ResultUpload) fields
            item = {
                "local_id": row["id"], # Internal use for ack
                "sample_id": row["sample_id"],
                "test_name": row["test_name"] or "Unknown",
                "result_value": row["result_value"] or "",
                "machine_timestamp": row["created_at"], # ISO format assumed from SQLite default
                "raw_data": row["raw_data_json"] or "{}",
                "hl7": row["hl7_message"],
                "astm": row["astm_message"],
                "stock_usage": [] # Usage syncing can be added later if needed
            }
            results.append(item)
            
        conn.close()
        return results
    except Exception as e:
        print(f"❌ DB Read Error: {e}")
        return []

def mark_as_synced(local_ids):
    """Mark specific IDs as synced in Local Client DB"""
    if not local_ids:
        return

    try:
        conn = sqlite3.connect(CLIENT_DB_PATH)
        cursor = conn.cursor()
        
        # Batch update
        placeholders = ','.join(['?'] * len(local_ids))
        sql = f"UPDATE test_results_local SET synced = 1 WHERE id IN ({placeholders})"
        
        cursor.execute(sql, local_ids)
        conn.commit()
        conn.close()
        print(f"✅ Marked {len(local_ids)} records as synced locally.")
        
    except Exception as e:
        print(f"❌ DB Update Error: {e}")

def perform_sync():
    """The actual sync logic"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Checking for unsynced data...")
    
    unsynced_items = get_unsynced_results()
    
    if not unsynced_items:
        print("   -> No new data.")
        return

    print(f"   -> Found {len(unsynced_items)} items. Uploading...")
    
    # Prepare Payload (Remove local_id before sending if API doesn't want it, 
    # but based on my analysis of results.py, it expects specific fields. 
    # The API model `ResultUpload` does NOT have `local_id`. 
    # We must strip it or the API might error if strict, or ignore it.)
    
    payload = []
    local_ids_map = [] # Keep track of which local ID belongs to which item
    
    for item in unsynced_items:
        local_id = item.pop("local_id")
        local_ids_map.append(local_id)
        payload.append(item)

    try:
        # POST to Server
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("   -> Upload Successful! Server responded 200 OK.")
            mark_as_synced(local_ids_map)
        else:
            print(f"   -> ❌ Server Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(f"   -> ⚠️ Server Unreachable at {BACKEND_URL}")
    except Exception as e:
        print(f"   -> ❌ Sync Error: {e}")

def main():
    print("=========================================")
    print("🌙 Midnight Sync Worker Started")
    print(f"🎯 Target: {BACKEND_URL}")
    print(f"📂 DB: {CLIENT_DB_PATH}")
    print("=========================================")

    # Optional: Run once strictly on startup for testing/debug
    #perform_sync() 

    while True:
        now = datetime.now()
        
        # Check if it is Midnight (00:00 to 00:05)
        if now.hour == SYNC_HOUR and now.minute < SYNC_MINUTE_WINDOW:
            print("🕛 It's Midnight! Starting Sync...")
            perform_sync()
            
            # Sleep until the window is over to avoid repeat syncs
            # Sleep for (6 mins) * 60 = 360 seconds
            print("💤 Sleeping until 01:00 to avoid duplicate runs...")
            time.sleep(3600) 
            
        else:
            # Just wait
            # print(f"⏳ Waiting for midnight... (Current: {now.strftime('%H:%M')})")
            time.sleep(CHECK_INTERVAL)


def start_background_sync():
    """Start the sync worker in a background thread"""
    import threading
    thread = threading.Thread(target=main, daemon=True)
    thread.start()
    print("🌙 Midnight Sync Worker started in background thread.")

if __name__ == "__main__":
    main()
