"""
Initialize Database
Run this script to create all database tables including test_results
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

# Change to backend directory so database is created there
os.chdir(backend_path)

# Import models to register them
from models import Base
from database import engine

if __name__ == "__main__":
    print("Initializing database...")
    print(f"Database location: {os.path.abspath('test.db')}")
    print(f"Database URL: {engine.url}")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialization complete!")
    print("\nTables created:")
    print("  - machine_activation")
    print("  - local_stock_movements")
    print("  - local_stock_snapshots")
    print("  - consumption")
    print("  - test_results (NEW)")
