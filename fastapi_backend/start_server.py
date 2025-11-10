#!/usr/bin/env python3
"""
FastAPI Backend Starter - Ensures all imports work correctly
"""

import os
import sys
from pathlib import Path

def start_server():
    """
    Start the FastAPI server with proper import handling
    """
    # Get the absolute path to the fastapi_backend directory
    backend_dir = Path(__file__).resolve().parent.absolute()
    
    # Change to the backend directory
    os.chdir(backend_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Clear any cached modules that might cause conflicts
    for module in list(sys.modules.keys()):
        if module.startswith('utils') or module.startswith('routers'):
            sys.modules.pop(module, None)
    
    # Ensure the backend directory is in sys.path
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    
    # Pre-import critical modules to ensure they're in Python's module cache
    print("Pre-importing critical modules...")
    try:
        import utils
        import utils.file_manager
        print("✅ Utils imported successfully")
    except ImportError as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    # Start the server
    print("\n🚀 Starting FastAPI server")
    print("📍 Server URL: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs\n")
    
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Disable reload mode initially to troubleshoot
    )
    
    return True

if __name__ == "__main__":
    start_server()