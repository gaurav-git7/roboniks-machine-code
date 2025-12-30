from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    DateTime,
    Boolean,
    Text,
    func,
    text
)
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum
from sqlalchemy import event
Base = declarative_base()

# =========================================================
# 1️⃣ MACHINE ACTIVATION
# =========================================================

class MachineActivation(Base):
    """
    Stores whether the machine is activated or not.
    One row per machine.
    """

    __tablename__ = "machine_activation"

    id = Column(Integer, primary_key=True, autoincrement=True)

    machine_id = Column(String(50), unique=True, nullable=True)

    
    distributor_id = Column(Integer, nullable=True)
    dist_code = Column(String(15), nullable=False)
    dist_name = Column(String(100))
    activated = Column(Boolean, default=False)
    activated_at = Column(DateTime, nullable=True)



# =========================================================
# 2️⃣ STOCK MOVEMENT TYPE ENUM
# =========================================================
class MovementType(str, enum.Enum):
    IN = "IN"     # Stock received
    OUT = "OUT"   # Stock consumed (1 test at a time)


# =========================================================
# 3️⃣ LOCAL STOCK MOVEMENTS (CORE TABLE)
# =========================================================
class LocalStockMovement(Base):
    """
    Append-only table.
    Every stock addition or consumption creates ONE row.
    This is the HEART of the machine DB.
    """

    __tablename__ = "local_stock_movements"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 🔹 Business batch ID (from server)
    batch_id = Column(String(30), index=True, nullable=False)

    # 🔹 Server-side stock_labels.id (reference only, NO FK)
    batch_pk = Column(Integer, nullable=True)

    movement_type = Column(
        Enum(MovementType, name="movement_type"),
        nullable=False
    )

    # IN  → positive quantity
    # OUT → -1 per test
    quantity = Column(Integer, nullable=False)

    # Test ID / Run ID / Machine reference
    reference = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # 🔄 Sync control
    synced = Column(Boolean, default=False)
    sync_attempts = Column(Integer, default=0)


# =========================================================
# 4️⃣ LOCAL STOCK SNAPSHOT (OPTIONAL UI CACHE)
# =========================================================
class LocalStockSnapshot(Base):
    """
    Optional table.
    Stores UI snapshot for quick loading.
    NEVER used for calculations.
    """

    __tablename__ = "local_stock_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # JSON string of UI table data
    stock_json = Column(Text, nullable=False)

    average_consumption = Column(Integer, nullable=True)

    synced = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    last_sync_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.current_timestamp())


# =========================================================
# 5️⃣ MONTHLY CONSUMPTION SUMMARY (OPTIONAL ANALYTICS)
# =========================================================
class Consumption(Base):
    """
    Optional analytics table.
    Used only for reports / charts.
    """

    __tablename__ = "consumption"

    id = Column(Integer, primary_key=True, autoincrement=True)

    month = Column(String(20), nullable=False)

    positive = Column(Integer, nullable=False)
    negative = Column(Integer, nullable=True)

    peak_time = Column(DateTime, nullable=True)
    off_peak_time = Column(DateTime, nullable=True)


# =========================================================
# 6️⃣ TEST RESULTS
# =========================================================
class TestResult(Base):
    """
    Stores test results from Read Sample operations
    Includes pre-generated HL7 and ASTM message formats
    """

    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Sample identification
    sample_id = Column(String(50), nullable=False, index=True)
    patient_id = Column(String(50), nullable=True)
    patient_name = Column(String(200), nullable=True)
    
    # Patient demographics
    patient_first_name = Column(String(100), nullable=True)
    patient_last_name = Column(String(100), nullable=True)
    patient_dob = Column(String(20), nullable=True)
    patient_gender = Column(String(10), nullable=True)
    patient_phone = Column(String(20), nullable=True)
    
    # Test information
    test_name = Column(String(100), nullable=False)
    test_code = Column(String(50), nullable=True)
    loinc_code = Column(String(50), nullable=True)
    
    # Test results - Parasite detection
    result_value = Column(String(100), nullable=True)
    result_unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    abnormal_flag = Column(String(10), nullable=True)
    result_status = Column(String(10), default='F')  # F=Final, P=Preliminary, C=Corrected
    
    # Parasite-specific results
    parasite_detected = Column(Boolean, default=False)
    parasite_species = Column(String(200), nullable=True)
    parasite_count = Column(Integer, nullable=True)
    microscopy_findings = Column(Text, nullable=True)
    
    # Multiple observations (JSON format)
    observations_json = Column(Text, nullable=True)
    
    # Order information
    order_number = Column(String(50), nullable=True)
    ordering_provider = Column(String(200), nullable=True)
    
    # Device information
    device_id = Column(String(50), nullable=True)
    operator_id = Column(String(50), nullable=True)
    
    # Timestamps
    sample_collected_at = Column(DateTime, nullable=True)
    test_performed_at = Column(DateTime, default=datetime.utcnow)
    result_reported_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Protocol messages (pre-generated)
    hl7_message = Column(Text, nullable=True)
    astm_message = Column(Text, nullable=True)
    
    # Transmission status
    transmitted = Column(Boolean, default=False)
    transmitted_at = Column(DateTime, nullable=True)
    transmission_protocol = Column(String(10), nullable=True)  # HL7 or ASTM
    transmission_status = Column(String(50), nullable=True)
    
    # Sync control
    synced = Column(Boolean, default=False)
    sync_attempts = Column(Integer, default=0)
    last_sync_at = Column(DateTime, nullable=True)
