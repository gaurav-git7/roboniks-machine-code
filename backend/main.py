from fastapi import FastAPI
from APi.machine_Activation import router as activation_router
from APi.stock import router as stock_router
# from models import Base  <-- REMOVED
# from database import engine <-- REMOVED
import uvicorn
from db_utils import init_db
from midnight_sync import start_background_sync

# Initialize Schema (Raw SQLite)
init_db()

app=FastAPI()

# Memory Optimization: Explicit malloc_trim on startup/shutdown for Linux
import ctypes
import os
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Force memory trim
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except:
        pass
    
    # Start Background Sync
    start_background_sync()
    
    yield
    # Shutdown
    try:
        ctypes.CDLL("libc.so.6").malloc_trim(0)
    except:
        pass

app = FastAPI(lifespan=lifespan)

app.include_router(activation_router)
app.include_router(stock_router)

from APi.operations import router as operations_router
app.include_router(operations_router)

from APi.results import router as results_router
app.include_router(results_router, prefix="/api/v1/results", tags=["Results"])

if __name__=="__main__":
    # reload=False for production (saves RAM/CPU and prevents subprocess spawning)
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=False, workers=1)