# machine_backend/main.py
from fastapi import APIRouter, HTTPException, status
# from sqlalchemy.orm import Session  <-- REMOVED
# from database import SessionLocal   <-- REMOVED
# import models                       <-- REMOVED
# from dependencies import get_db     <-- REMOVED
from db_utils import get_db_conn
from datetime import datetime

router = APIRouter(prefix="/activation",tags=["Activation"])

@router.get("/check")
def check_activation():
    """Check if machine is activated"""
    try:
        with get_db_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, machine_id, dist_code, dist_name FROM machine_activation WHERE activated=1 LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                return {
                    "activated": True,
                    "machine_id": row[1],
                    "dist_code": row[2],
                    "dist_name": row[3]
                }
            else:
                return {"activated": False}
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/activate")
def activate_machine(data: dict):
    # Raw SQLite Implementation
    try:
        with get_db_conn() as conn:
            cursor = conn.cursor()
            
            # Insert new activation record
            sql = """
                INSERT INTO machine_activation 
                (machine_id, dist_code, dist_name, activated, activated_at)
                VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(sql, (
                data["machine_id"],
                data["dist_code"],
                data.get("dist_name"),
                1, # True
                datetime.utcnow()
            ))
            conn.commit()
            return {
                "status": "activated",
                "machine_id": data["machine_id"] 
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
