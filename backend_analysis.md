# Backend Comparison: `Prototype\robo1-main` vs `Prototype\Robo\backend`

## Overview
This document outlines the differences between the backend implementations in `robo1-main` and `Robo` directories, and identifies missing components in `Robo\backend` that should be implemented.

## Key Differences

| Feature | `robo1-main\backend` | `Robo\backend` |
| :--- | :--- | :--- |
| **Sync Worker** | **Has `machine_sync.py`** | ❌ **Missing** |
| **Database Utils** | Basic `database.py` | Advanced `db_utils.py` + `database.py` |
| **API Endpoints** | Activation, Stock, Ops | Activation, Stock, Ops, **Results** |
| **Models** | Basic Schema | Extended Schema (Added `TestResult`, `LocalStockMovement`) |
| **File Sizes** | Smaller (Older version) | Larger (Newer/Refactored version) |

## Missing Component in `Robo\backend`
The primary component missing from `(Latter) Prototype\Robo\backend` logic is the **`machine_sync.py`** script.

In `robo1-main`, this script runs as a separate process to:
1.  Check the `local_stock_snapshots` table for unsynced records (`synced=0`).
2.  Upload them to the cloud server.
3.  Mark them as synced in the local database.

The **good news** is that `Robo\backend` **already has the necessary database support** for this feature:
-   `models.py` contains the `LocalStockSnapshot` table definition with `synced` and `stock_json` columns.
-   `APi/operations.py` correctly populates this table when stock is added or consumed, setting `synced=False`.

## Implementation Plan
To fully restore functionality in `Robo\backend`, you should implement the `machine_sync.py` file.

### Recommended `machine_sync.py` for `Robo\backend`

Create a new file `c:\College_projects\Medical Devices\Project\Robo\Prototype\Robo\backend\machine_sync.py` with the following content. This version is adapted to work with the `Robo` environment (ensuring `test.db` path is correct).

```python
import time
import requests
import sqlite3
import json
from datetime import datetime
import os

# CONFIGURATION
# Ensure we point to the correct DB file relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_DB_PATH = os.path.join(BASE_DIR, "test.db") 

CLOUD_API_URL = "http://127.0.0.1:8000/stock/sync" # Update with your actual Cloud URL
MACHINE_ID = "MAH001" # This should ideally come from machine_activation table or config

def get_unsynced_data():
    """Fetch the latest UNSYNCED snapshot from local DB"""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        
        # Get the latest row where synced=0 (False)
        cursor.execute("SELECT id, stock_json, average_consumption FROM local_stock_snapshots WHERE synced=0 ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        return row
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def mark_as_synced(row_id):
    """Update the local DB to say 'We sent this!'"""
    try:
        conn = sqlite3.connect(LOCAL_DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE local_stock_snapshots SET synced=1 WHERE id=?", (row_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Update Error: {e}")

def sync_loop():
    print(f"🚀 Sync Worker Started... Monitoring {LOCAL_DB_PATH}")
    while True:
        data = get_unsynced_data()
        
        if data:
            row_id, stock_json, avg_consumption = data
            print(f"📦 Found unsynced data (ID: {row_id}). Sending to Cloud...")
            
            payload = {
                "machine_id": MACHINE_ID,
                "stock_json": stock_json,
                "consumption_count": avg_consumption or 0
            }
            
            try:
                response = requests.post(CLOUD_API_URL, json=payload)
                
                if response.status_code == 200:
                    print("✅ Upload Success!")
                    mark_as_synced(row_id)
                else:
                    print(f"❌ Cloud Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"⚠️ Connection Failed: {e}")
        
        else:
            # Optional: Print less frequently to avoid spam
            # print("💤 No new data. Sleeping...")
            pass
            
        time.sleep(60) # Wait 60 seconds before checking again

if __name__ == "__main__":
    sync_loop()
```

## How to Run
1.  Navigate to `Prototype\Robo\backend`.
2.  Run the sync worker in a separate terminal:
    ```powershell
    python machine_sync.py
    ```
