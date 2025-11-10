#!/usr/bin/env python3
"""
FastAPI Backend Launcher  
Ensures proper working directory before starting server
"""

import sys
import os
from pathlib import Path

if __name__ == "__main__":
    # Change to fastapi_backend directory  
    backend_dir = Path(__file__).parent / "fastapi_backend"
    os.chdir(str(backend_dir))
    
    print("🚀 Starting FastAPI LaTeX Document Editor")
    print(f"📂 Working directory: {os.getcwd()}")
    print("📍 Server URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print()
    
    # Import uvicorn and run
    import uvicorn
    
    # Run with reload for development
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )