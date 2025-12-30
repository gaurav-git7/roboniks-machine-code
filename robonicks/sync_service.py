import schedule
import time
import requests
import sys
import os
from utils.minimal_db import MinimalDB

# Configuration
SERVER_URL = "http://your-server-ip:8000/api/v1/results/batch-upload"
SYNC_TIME = "00:00" # Midnight

def batch_upload():
    print(f"Starting batch upload at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    db = MinimalDB()
    
    # 1. Get pending records
    results = db.get_unsynced_results()
    stock_usage_list = db.get_unsynced_usage()
    
    if not results and not stock_usage_list:
        print("No new results or stock usage to sync.")
        return

    print(f"Found {len(results)} results and {len(stock_usage_list)} stock usage items.")
    
    # 2. Upload Logic
    # We attach all pending stock usage to the FIRST result in the batch 
    # to ensure it gets sent to the server.
    
    # If we have stock but no results, we can't send stock with this API structure 
    # (since root is List[ResultUpload]).
    # Ideally we'd have a separate /stock-sync endpoint. 
    # For now, we only sync stock when we sync a result.
    
    if results:
        for index, record in enumerate(results):
            try:
                # Attach stock usage ONLY to the first record to avoid duplication
                current_stock_payload = []
                if index == 0 and stock_usage_list:
                    current_stock_payload = [
                        {
                            "batch_id": s['batch_id'], 
                            "quantity_used": s['quantity_used'],
                            "id": s['id']
                        } 
                        for s in stock_usage_list
                    ]

                # Prepare payload
                payload = {
                    "sample_id": record['sample_id'],
                    "test_name": record['test_name'],
                    "result_value": record['result_value'],
                    
                    # FULL PAYLOAD (User Request)
                    "hl7": record['hl7_message'],
                    "astm": record['astm_message'],
                    "raw_data": record['raw_data_json'],
                    
                    "machine_timestamp": record['created_at'],
                    "stock_usage": current_stock_payload
                }
                
                # 3. Send to Server (Simulated)
                print(f"Uploading Sample {record['sample_id']} (with {len(current_stock_payload)} stock items)... ", end="")
                
                # In real implementation:
                # requests.post(SERVER_URL, json=[payload]) 
                
                success = True # SIMULATED
                
                if success:
                    # 4. Mark Result Synced
                    db.mark_synced(record['id'])
                    
                    # 5. Mark Stock Synced (only if we sent it)
                    if current_stock_payload:
                        for s_item in current_stock_payload:
                            db.mark_usage_synced(s_item['id'])
                            
                    print("SUCCESS")
                    success_count += 1
                else:
                    print("FAILED")
                    fail_count += 1
                    
            except Exception as e:
                print(f"FAILED ({str(e)})")
                fail_count += 1
            
    print(f"Sync Complete. Success: {success_count}, Failed: {fail_count}")

def run_scheduler():
    print(f"Sync Service Started. Scheduled for {SYNC_TIME} daily.")
    # Schedule the job
    schedule.every().day.at(SYNC_TIME).do(batch_upload)
    
    # Also run once at startup for testing/debug if needed
    # batch_upload()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # If run with argument --now, run immediately
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        batch_upload()
    else:
        run_scheduler()
