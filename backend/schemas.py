"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


# =========================================================
# TEST RESULT SCHEMAS
# =========================================================

class ObservationBase(BaseModel):
    """Single observation/test result"""
    test_code: Optional[str] = None
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None


class TestResultCreate(BaseModel):
    """Schema for creating a new test result"""
    # Sample identification
    sample_id: str
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    
    # Patient demographics
    patient_first_name: Optional[str] = None
    patient_last_name: Optional[str] = None
    patient_dob: Optional[str] = None
    patient_gender: Optional[str] = None
    patient_phone: Optional[str] = None
    
    # Test information
    test_name: str
    test_code: Optional[str] = None
    loinc_code: Optional[str] = None
    
    # Test results
    result_value: Optional[str] = None
    result_unit: Optional[str] = None
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None
    result_status: str = 'F'
    
    # Parasite-specific results
    parasite_detected: bool = False
    parasite_species: Optional[str] = None
    parasite_count: Optional[int] = None
    microscopy_findings: Optional[str] = None
    
    # Multiple observations
    observations: Optional[List[ObservationBase]] = None
    
    # Order information
    order_number: Optional[str] = None
    ordering_provider: Optional[str] = None
    
    # Device information
    device_id: Optional[str] = None
    operator_id: Optional[str] = None
    
    # Timestamps
    sample_collected_at: Optional[datetime] = None
    test_performed_at: Optional[datetime] = None


class TestResultResponse(BaseModel):
    """Schema for test result response"""
    id: int
    sample_id: str
    patient_id: Optional[str]
    patient_name: Optional[str]
    test_name: str
    result_value: Optional[str]
    parasite_detected: bool
    parasite_species: Optional[str]
    hl7_message: Optional[str]
    astm_message: Optional[str]
    transmitted: bool
    transmission_protocol: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TestResultUpdate(BaseModel):
    """Schema for updating test result"""
    transmitted: Optional[bool] = None
    transmitted_at: Optional[datetime] = None
    transmission_protocol: Optional[str] = None
    transmission_status: Optional[str] = None
    synced: Optional[bool] = None


# =========================================================
# STOCK MOVEMENT SCHEMAS
# =========================================================

class StockMovementCreate(BaseModel):
    """Schema for creating stock movement"""
    batch_id: str
    batch_pk: Optional[int] = None
    movement_type: str  # IN or OUT
    quantity: int
    reference: Optional[str] = None


class StockMovementResponse(BaseModel):
    """Schema for stock movement response"""
    id: int
    batch_id: str
    movement_type: str
    quantity: int
    reference: Optional[str]
    created_at: datetime
    synced: bool
    
    class Config:
        from_attributes = True
