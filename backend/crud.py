"""
CRUD operations for database
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict
from datetime import datetime
import json

from models import TestResult, LocalStockMovement, MovementType
from schemas import TestResultCreate, TestResultUpdate, StockMovementCreate


# =========================================================
# TEST RESULTS CRUD
# =========================================================

def create_test_result(db: Session, test_data: TestResultCreate, hl7_message: str = None, astm_message: str = None) -> TestResult:
    """
    Create a new test result with pre-generated protocol messages
    """
    # Convert observations to JSON if provided
    observations_json = None
    if test_data.observations:
        observations_json = json.dumps([obs.dict() for obs in test_data.observations])
    
    db_test = TestResult(
        sample_id=test_data.sample_id,
        patient_id=test_data.patient_id,
        patient_name=test_data.patient_name,
        patient_first_name=test_data.patient_first_name,
        patient_last_name=test_data.patient_last_name,
        patient_dob=test_data.patient_dob,
        patient_gender=test_data.patient_gender,
        patient_phone=test_data.patient_phone,
        test_name=test_data.test_name,
        test_code=test_data.test_code,
        loinc_code=test_data.loinc_code,
        result_value=test_data.result_value,
        result_unit=test_data.result_unit,
        reference_range=test_data.reference_range,
        abnormal_flag=test_data.abnormal_flag,
        result_status=test_data.result_status,
        parasite_detected=test_data.parasite_detected,
        parasite_species=test_data.parasite_species,
        parasite_count=test_data.parasite_count,
        microscopy_findings=test_data.microscopy_findings,
        observations_json=observations_json,
        order_number=test_data.order_number,
        ordering_provider=test_data.ordering_provider,
        device_id=test_data.device_id,
        operator_id=test_data.operator_id,
        sample_collected_at=test_data.sample_collected_at,
        test_performed_at=test_data.test_performed_at or datetime.utcnow(),
        hl7_message=hl7_message,
        astm_message=astm_message
    )
    
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test


def get_test_result(db: Session, test_id: int) -> Optional[TestResult]:
    """Get test result by ID"""
    return db.query(TestResult).filter(TestResult.id == test_id).first()


def get_test_result_by_sample_id(db: Session, sample_id: str) -> Optional[TestResult]:
    """Get test result by sample ID"""
    return db.query(TestResult).filter(TestResult.sample_id == sample_id).first()


def get_all_test_results(db: Session, skip: int = 0, limit: int = 100) -> List[TestResult]:
    """Get all test results with pagination"""
    return db.query(TestResult).order_by(desc(TestResult.created_at)).offset(skip).limit(limit).all()


def get_test_results_by_patient(db: Session, patient_id: str) -> List[TestResult]:
    """Get all test results for a patient"""
    return db.query(TestResult).filter(TestResult.patient_id == patient_id).order_by(desc(TestResult.created_at)).all()


def get_untransmitted_test_results(db: Session) -> List[TestResult]:
    """Get all test results that haven't been transmitted"""
    return db.query(TestResult).filter(TestResult.transmitted == False).order_by(TestResult.created_at).all()


def update_test_result(db: Session, test_id: int, update_data: TestResultUpdate) -> Optional[TestResult]:
    """Update test result"""
    db_test = db.query(TestResult).filter(TestResult.id == test_id).first()
    if not db_test:
        return None
    
    update_dict = update_data.dict(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_test, key, value)
    
    db.commit()
    db.refresh(db_test)
    return db_test


def mark_test_transmitted(db: Session, test_id: int, protocol: str, status: str = "success") -> Optional[TestResult]:
    """Mark test result as transmitted"""
    db_test = db.query(TestResult).filter(TestResult.id == test_id).first()
    if not db_test:
        return None
    
    db_test.transmitted = True
    db_test.transmitted_at = datetime.utcnow()
    db_test.transmission_protocol = protocol
    db_test.transmission_status = status
    
    db.commit()
    db.refresh(db_test)
    return db_test


def delete_test_result(db: Session, test_id: int) -> bool:
    """Delete test result"""
    db_test = db.query(TestResult).filter(TestResult.id == test_id).first()
    if not db_test:
        return False
    
    db.delete(db_test)
    db.commit()
    return True


def get_test_results_by_date_range(db: Session, start_date: datetime, end_date: datetime) -> List[TestResult]:
    """Get test results within date range"""
    return db.query(TestResult).filter(
        TestResult.created_at >= start_date,
        TestResult.created_at <= end_date
    ).order_by(TestResult.created_at).all()


def get_test_statistics(db: Session) -> Dict:
    """Get test statistics"""
    total_tests = db.query(func.count(TestResult.id)).scalar()
    transmitted_tests = db.query(func.count(TestResult.id)).filter(TestResult.transmitted == True).scalar()
    positive_results = db.query(func.count(TestResult.id)).filter(TestResult.parasite_detected == True).scalar()
    
    return {
        'total_tests': total_tests or 0,
        'transmitted_tests': transmitted_tests or 0,
        'untransmitted_tests': (total_tests or 0) - (transmitted_tests or 0),
        'positive_results': positive_results or 0,
        'negative_results': (total_tests or 0) - (positive_results or 0)
    }


# =========================================================
# STOCK MOVEMENT CRUD
# =========================================================

def create_stock_movement(db: Session, movement_data: StockMovementCreate) -> LocalStockMovement:
    """Create a new stock movement"""
    db_movement = LocalStockMovement(
        batch_id=movement_data.batch_id,
        batch_pk=movement_data.batch_pk,
        movement_type=MovementType(movement_data.movement_type),
        quantity=movement_data.quantity,
        reference=movement_data.reference
    )
    
    db.add(db_movement)
    db.commit()
    db.refresh(db_movement)
    return db_movement


def get_stock_movements(db: Session, skip: int = 0, limit: int = 100) -> List[LocalStockMovement]:
    """Get all stock movements"""
    return db.query(LocalStockMovement).order_by(desc(LocalStockMovement.created_at)).offset(skip).limit(limit).all()


def get_stock_balance(db: Session, batch_id: str = None) -> int:
    """Get current stock balance"""
    query = db.query(func.sum(LocalStockMovement.quantity))
    
    if batch_id:
        query = query.filter(LocalStockMovement.batch_id == batch_id)
    
    balance = query.scalar()
    return balance or 0


def get_batch_balances(db: Session) -> Dict[str, int]:
    """Get balance for each batch"""
    results = db.query(
        LocalStockMovement.batch_id,
        func.sum(LocalStockMovement.quantity).label('balance')
    ).group_by(LocalStockMovement.batch_id).all()
    
    return {batch_id: balance for batch_id, balance in results}


def record_test_consumption(db: Session, batch_id: str, sample_id: str) -> LocalStockMovement:
    """Record stock consumption for a test (OUT movement)"""
    return create_stock_movement(
        db,
        StockMovementCreate(
            batch_id=batch_id,
            movement_type="OUT",
            quantity=-1,
            reference=f"Test: {sample_id}"
        )
    )
