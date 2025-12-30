import sqlite3
from datetime import datetime
import contextlib

DB_PATH = "./test.db"

def init_db():
    """Initialize database schema using raw SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Memory Optimizations
        c.execute("PRAGMA journal_mode=WAL;")
        c.execute("PRAGMA cache_size=0;") # Minimal cache
        c.execute("PRAGMA synchronous=NORMAL;")
        
        # 1. Machine Activation Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS machine_activation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                machine_id TEXT UNIQUE,
                distributor_id INTEGER,
                dist_code TEXT NOT NULL,
                dist_name TEXT,
                activated BOOLEAN DEFAULT 0,
                activated_at TIMESTAMP
            )
        """)
        
        # 2. Local Stock Movements Table
        c.execute("""
            CREATE TABLE IF NOT EXISTS local_stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id TEXT,
                batch_pk INTEGER,
                test_name TEXT,
                movement_type TEXT,
                quantity INTEGER,
                expiry_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sync_status TEXT DEFAULT 'PENDING'
            )
        """)
        
        # 3. Test Results Table (For Server Side Storage)
        c.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sample_id TEXT,
                test_name TEXT,
                result_value TEXT,
                observations_json TEXT,  -- Raw JSON dump
                hl7_message TEXT,
                astm_message TEXT,
                test_performed_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                transmitted BOOLEAN DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
        print("Database initialized (SQLite3 Mode)")
    except Exception as e:
        print(f"DB Init Error: {e}")

@contextlib.contextmanager
def get_db_conn():
    """Yields a raw sqlite3 connection with dict factory"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Allow accessing columns by name
    
    # Apply PRAGMAs on every connection
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA cache_size=0;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    try:
        yield conn
    finally:
        conn.close()
