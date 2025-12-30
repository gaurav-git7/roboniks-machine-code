# APi/operations.py - Reagent scanning and test consumption

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db
import models
import json
from datetime import datetime

router = APIRouter(prefix="/ops", tags=["Operations"])

# ---------------------------------------------------------
# 1. SCAN QR API - Called when scanning reagent QR code
# ---------------------------------------------------------
@router.post("/scan-qr")
def scan_reagent_qr(qr_string: str, db: Session = Depends(get_db)):
    """
    Input: "D0001-BATCH2025-PACK1"
    Logic: Adds +50 tests to the local stock JSON.
    """
    try:
        # Parse the QR String (format: Distributor-Batch-Pack)
        parts = qr_string.split('-')
        if len(parts) < 3:
            raise HTTPException(status_code=400, detail="Invalid QR Format. Expected: D0001-BATCH2025-PACK1")
             
        dist_code = parts[0]
        batch_id = parts[1]
        
        # Get the latest Stock Snapshot
        last_snapshot = db.query(models.LocalStockSnapshot).order_by(models.LocalStockSnapshot.id.desc()).first()
        
        current_stock = []
        if last_snapshot and last_snapshot.stock_json:
            try:
                current_stock = json.loads(last_snapshot.stock_json)
            except:
                current_stock = []

        # Add the New Item
        new_item = {
            "sr_no": len(current_stock) + 1,
            "batch_id": batch_id,
            "distributor": dist_code,
            "unopened_packs": 1,
            "opened_tests": 0,
            "total": 50,  # 1 pack = 50 tests
            "added_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        current_stock.append(new_item)

        # Save New Snapshot
        new_snapshot = models.LocalStockSnapshot(
            stock_json=json.dumps(current_stock),
            average_consumption=last_snapshot.average_consumption if last_snapshot else 0,
            synced=False
        )
        
        db.add(new_snapshot)
        db.commit()
        
        total_tests = sum(int(item.get("total", 0)) for item in current_stock)
        
        return {
            "status": "success", 
            "added_tests": 50, 
            "batch": batch_id,
            "total_remaining": total_tests
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------
# 2. RUN TEST API - Called when test is performed
# ---------------------------------------------------------
@router.post("/run-test")
def run_test_consumption(sample_id: str, db: Session = Depends(get_db)):
    """
    Logic: Deducts 1 test from stock AND logs it in the Consumption table.
    """
    # Get Stock
    snapshot = db.query(models.LocalStockSnapshot).order_by(models.LocalStockSnapshot.id.desc()).first()
    if not snapshot or not snapshot.stock_json:
        raise HTTPException(status_code=400, detail="No Stock Available")
    
    stock_list = json.loads(snapshot.stock_json)
    
    # Find a pack with stock and deduct
    stock_deducted = False
    for item in stock_list:
        total = int(item.get("total", 0))
        if total > 0:
            item["total"] = total - 1
            stock_deducted = True
            break
    
    if not stock_deducted:
        raise HTTPException(status_code=400, detail="Out of Stock!")

    # Save Updated Stock Snapshot
    new_snapshot = models.LocalStockSnapshot(
        stock_json=json.dumps(stock_list),
        average_consumption=snapshot.average_consumption,
        synced=False
    )
    db.add(new_snapshot)
    
    # Log Consumption
    current_month = datetime.now().strftime("%B %Y")
    log_entry = db.query(models.Consumption).filter(models.Consumption.month == current_month).first()
    
    if not log_entry:
        log_entry = models.Consumption(
            month=current_month,
            positive=1,
            negative=0
        )
        db.add(log_entry)
    else:
        log_entry.positive += 1
        
    db.commit()
    
    total_remaining = sum(int(i.get("total", 0)) for i in stock_list)

    return {
        "status": "success", 
        "remaining_stock": total_remaining,
        "sample_id": sample_id,
        "message": f"Test logged for {sample_id}"
    }


# ---------------------------------------------------------
# 3. GET CURRENT STOCK
# ---------------------------------------------------------
@router.get("/current-stock")
def get_current_stock(db: Session = Depends(get_db)):
    """
    Returns current stock level
    """
    snapshot = db.query(models.LocalStockSnapshot).order_by(models.LocalStockSnapshot.id.desc()).first()
    
    if not snapshot or not snapshot.stock_json:
        return {"total_remaining": 0, "items": []}
        
    stock_list = json.loads(snapshot.stock_json)
    total_tests = sum(int(item.get("total", 0)) for item in stock_list)
    
    return {
        "total_remaining": total_tests,
        "items": stock_list
    }


# ---------------------------------------------------------
# 4. GET CONSUMPTION HISTORY
# ---------------------------------------------------------
@router.get("/consumption")
def get_consumption_history(db: Session = Depends(get_db)):
    """
    Returns monthly consumption data for History page
    """
    # Get all consumption records
    records = db.query(models.Consumption).order_by(models.Consumption.id.desc()).all()
    
    if not records:
        # Return sample data if no records exist
        return [
            {"month": "December 2024", "positive": 0, "negative": 0, "high_time": "", "low_time": ""},
        ]
    
    result = []
    for rec in records:
        result.append({
            "month": rec.month,
            "positive": rec.positive or 0,
            "negative": rec.negative or 0,
            "high_time": "",
            "low_time": ""
        })
    
    return result
