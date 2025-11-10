"""
FastAPI web API for RAG LaTeX Fixer
"""
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import tempfile
from pathlib import Path
from loguru import logger

from pipeline import LatexFixerPipeline
from models import LatexIssue, FixSuggestion, ValidationResult
from config import settings

# Initialize FastAPI app
app = FastAPI(
    title="RAG LaTeX Fixer API",
    description="AI-powered LaTeX style and layout fixer using RAG",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline
pipeline = LatexFixerPipeline()


# Request/Response models
class FixRequest(BaseModel):
    latex_content: str
    document_format: str = "IEEE_two_column"
    validate_compilation: bool = False


class IssueResponse(BaseModel):
    type: str
    severity: str
    description: str
    element: str
    current_code: str
    expected_format: Optional[str] = None


class FixResponse(BaseModel):
    original_code: str
    fixed_code: str
    explanation: str
    confidence_score: float
    changes_made: List[str]


class FixReportResponse(BaseModel):
    success: bool
    original_latex: str
    fixed_latex: str
    issues_count: int
    fixes_count: int
    processing_time: float
    issues: List[IssueResponse]
    fixes: List[FixResponse]
    validation: Optional[dict] = None


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "service": "RAG LaTeX Fixer API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/fix", response_model=FixReportResponse)
async def fix_latex(request: FixRequest):
    """
    Fix LaTeX document style and layout issues
    
    Args:
        request: FixRequest with latex_content and options
    
    Returns:
        FixReportResponse with original, fixed content, and details
    """
    try:
        logger.info(f"Received fix request for {request.document_format} format")
        
        # Process document
        report = pipeline.process_document(
            latex_content=request.latex_content,
            document_format=request.document_format,
            validate_compilation=request.validate_compilation
        )
        
        # Convert to response format
        response = FixReportResponse(
            success=report.success,
            original_latex=report.original_latex,
            fixed_latex=report.fixed_latex,
            issues_count=len(report.issues_fixed),
            fixes_count=len(report.fixes_applied),
            processing_time=report.processing_time,
            issues=[
                IssueResponse(
                    type=issue.type.value,
                    severity=issue.severity.value,
                    description=issue.description,
                    element=issue.element,
                    current_code=issue.current_code,
                    expected_format=issue.expected_format
                )
                for issue in report.issues_fixed
            ],
            fixes=[
                FixResponse(
                    original_code=fix.original_code,
                    fixed_code=fix.fixed_code,
                    explanation=fix.explanation,
                    confidence_score=fix.confidence_score,
                    changes_made=fix.changes_made
                )
                for fix in report.fixes_applied
            ],
            validation={
                "compilation_success": report.validation_result.compilation_success,
                "style_compliance_score": report.validation_result.style_compliance_score,
                "improvements": report.validation_result.improvements,
                "warnings": report.validation_result.warnings
            } if report.validation_result else None
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fix/file")
async def fix_latex_file(
    file: UploadFile = File(...),
    document_format: str = Form("IEEE_two_column"),
    validate_compilation: bool = Form(False)
):
    """
    Fix LaTeX file upload
    
    Args:
        file: LaTeX file upload
        document_format: Target format
        validate_compilation: Whether to validate by compilation
    
    Returns:
        Fixed LaTeX content
    """
    try:
        # Read file content
        content = await file.read()
        latex_content = content.decode('utf-8')
        
        # Process
        report = pipeline.process_document(
            latex_content=latex_content,
            document_format=document_format,
            validate_compilation=validate_compilation
        )
        
        return {
            "success": report.success,
            "fixed_latex": report.fixed_latex,
            "issues_count": len(report.issues_fixed),
            "processing_time": report.processing_time
        }
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/formats")
def get_supported_formats():
    """Get list of supported document formats"""
    return {
        "formats": settings.SUPPORTED_FORMATS,
        "default": "IEEE_two_column"
    }


@app.post("/analyze")
async def analyze_latex(request: FixRequest):
    """
    Analyze LaTeX document without fixing
    Only detect and report issues
    """
    try:
        from detectors.style_detector import StyleIssueDetector
        
        detector = StyleIssueDetector()
        analysis = detector.analyze_document(
            request.latex_content,
            request.document_format
        )
        
        return {
            "issues_count": len(analysis.detected_issues),
            "document_format": analysis.document_format,
            "document_structure": analysis.document_structure,
            "issues": [
                IssueResponse(
                    type=issue.type.value,
                    severity=issue.severity.value,
                    description=issue.description,
                    element=issue.element,
                    current_code=issue.current_code,
                    expected_format=issue.expected_format
                )
                for issue in analysis.detected_issues
            ]
        }
        
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
