#!/bin/bash

# =========================================================
# Robonicks Memory Optimization Launcher
# =========================================================

# 1. Use system malloc instead of Python's small object allocator
#    This allows malloc_trim to actually release memory to OS
export PYTHONMALLOC=malloc

# 2. Trim memory immediately after free (default is usually 128KB)
export MALLOC_TRIM_THRESHOLD_=0

# 3. Use mmap for larger allocations (reduces heap fragmentation)
export MALLOC_MMAP_THRESHOLD_=131072

# 4. Limit memory arenas to prevent fragmentation across threads
export MALLOC_ARENA_MAX=2

echo "Starting Robonicks with Memory Optimizations..."
echo "PYTHONMALLOC=$PYTHONMALLOC"

# 2. Start Backend Server (Background)
echo "Starting Backend Server..."
# Adjust path relative to this script: ../backend/main.py
# We assume script is run from project root or handled via specific paths
# Let's try to locate it relative to script location
SCRIPT_DIR=$(dirname "$0")

# Start backend in background and log to /dev/null or a log file
python3 -OO "$SCRIPT_DIR/../backend/main.py" > /dev/null 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID"

# Function to kill backend on exit
cleanup() {
    echo "Stopping Backend (PID $BACKEND_PID)..."
    kill $BACKEND_PID
}
trap cleanup EXIT

# Wait a moment for backend to initialize
sleep 2

# 3. Run the application
python3 -OO main.py
