"""
FastAPI Backend for LaTeX Document Editing System
Integrates: PDF to LaTeX (MathPix) → RAG LaTeX Fixer → Document Editor
"""

# ==================================================================
# CRITICAL: Import utils first to ensure it's in Python's module cache
# This prevents the "No module named 'utils.file_manager'" error
# ==================================================================
try:
    from . import utils
    from .routers import latex_fixer, file_manager, converter, compiler, debug, doc_editor_v1
except ImportError:
    # Running directly, not as a package
    import utils
    from routers import latex_fixer, file_manager, converter, compiler, debug, doc_editor_v1
# ==================================================================

from fastapi import FastAPI, HTTPException, Depends, Security, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security.api_key import APIKeyHeader
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LaTeX Document Editing API",
    description="Comprehensive API for PDF to LaTeX conversion, fixing, and editing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    """Verify API key for authentication"""
    expected_api_key = os.getenv("FASTAPI_API_KEY", "your-secret-api-key")
    if not api_key_header or api_key_header != expected_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API Key"
        )
    return api_key_header

# Include routers
app.include_router(
    converter.router,
    prefix="/api/v1/convert",
    tags=["PDF to LaTeX Conversion"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    latex_fixer.router,
    prefix="/api/v1/fix",
    tags=["LaTeX Fixer"],
    # dependencies=[Depends(verify_api_key)]
)

# OLD ROUTER REMOVED - Using V1 only now
# app.include_router(
#     doc_editor.router,
#     prefix="/api/v1/edit",
#     tags=["Document Editor"],
# )

app.include_router(
    doc_editor_v1.router,
    prefix="/api/v1/edit",
    tags=["Document Editor V1"],
    # dependencies=[Depends(verify_api_key)]  # Temporarily disabled for testing
)

app.include_router(
    compiler.router,
    prefix="/api/v1/compile",
    tags=["LaTeX Compiler"],
    # dependencies=[Depends(verify_api_key)]  # Temporarily disabled for testing
)

app.include_router(
    file_manager.router,
    prefix="/api/v1/files",
    tags=["File Management"],
    # dependencies=[Depends(verify_api_key)]  # Temporarily disabled for testing
)

app.include_router(
    debug.router,
    prefix="/api/v1/debug",
    tags=["Debug"],
    dependencies=[Depends(verify_api_key)]
)

# Health check endpoint (no authentication required)
@app.get("/health", tags=["Health Check"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LaTeX Document Editing API",
        "version": "1.0.0",
        "gemini_api_configured": bool(os.getenv("GEMINI_API_KEY")),
        "mathpix_api_configured": bool(os.getenv("MATHPIX_APP_ID"))
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LaTeX Document Editing API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
