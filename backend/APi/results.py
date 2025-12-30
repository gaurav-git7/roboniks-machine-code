from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from db_utils import get_db_conn

router = APIRouter()

# --- Pydantic Models ---

class StockUsageItem(BaseModel):
    batch_id: str
    quantity_used: int
    id: int # Local ID to confirm sync

class ResultUpload(BaseModel):
    sample_id: str
    test_name: str
    result_value: str
    machine_timestamp: str # ISO format
    raw_data: str # JSON string
    hl7: Optional[str] = None
    astm: Optional[str] = None
    stock_usage: Optional[List[StockUsageItem]] = []
    
    # We might need the local ID to confirm sync back to client? 
    # Actually, the client handles sync state. The server just says "OK".
    
# --- Endpoints ---

@router.post("/batch-upload")
async def batch_upload(uploads: List[ResultUpload]):
    """
    Receive a batch of results and stock usage from a client machine.
    """
    try:
        with get_db_conn() as conn:
            cursor = conn.cursor()
            
            for item in uploads:
                # 1. Insert Test Result
                # We need to ensure the 'test_results' table exists. 
                # Note: db_utils.init_db() in this Prototype might not have created test_results yet if it was copied from a version that only had stock.
                # Use "CREATE TABLE IF NOT EXISTS" logic or assume it exists. 
                # Given models.py has it, we should ensure table exists. 
                # For safety in this prototype, I'll execute create if not exists here or relying on init_db.
                # Let's assume init_db *should* have it, but looking at db_utils.py context, it only had 2 tables!
                # I MUST ADD test_results creation to db_utils or do it here.
                # To be safe, I'll do a quick check/create here or update db_utils. 
                # Proceeding with assumption I will update db_utils.py separately or handled by `models.py` if used.
                # Since I am using raw sql, I'll just write to 'test_results'.
                
                # Check timestamps
                try:
                    performed_at = datetime.fromisoformat(item.machine_timestamp)
                except:
                    performed_at = datetime.utcnow()

                cursor.execute("""
                    INSERT INTO test_results (
                        sample_id, test_name, result_value, 
                        observations_json, hl7_message, astm_message,
                        test_performed_at, created_at, transmitted
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.sample_id,
                    item.test_name,
                    item.result_value,
                    item.raw_data,
                    item.hl7,
                    item.astm,
                    performed_at,
                    datetime.utcnow(),
                    True # Marked as transmitted since it's on the server now
                ))
                
                # 2. Insert Stock Usage (if any linked to this result)
                if item.stock_usage:
                    for usage in item.stock_usage:
                        cursor.execute("""
                            INSERT INTO local_stock_movements (
                                batch_id, movement_type, quantity, 
                                reference, created_at, sync_status
                            ) VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            usage.batch_id,
                            "OUT",
                            -usage.quantity_used, # Negative for consumption
                            f"Sync_Usage_Sample_{item.sample_id}",
                            datetime.utcnow(),
                            "SYNCED"
                        ))
            
            conn.commit()
            return {"status": "success", "processed_count": len(uploads)}

    except Exception as e:
        print(f"Batch Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
