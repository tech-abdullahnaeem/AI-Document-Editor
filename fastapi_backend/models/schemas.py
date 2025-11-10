"""
Pydantic models for API request/response schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

# Enums
class DocumentType(str, Enum):
    RESEARCH = "research"
    NORMAL = "normal"

class ConferenceType(str, Enum):
    IEEE = "IEEE"
    ACM = "ACM"
    SPRINGER = "SPRINGER"
    ELSEVIER = "ELSEVIER"
    GENERIC = "GENERIC"

class ColumnFormat(str, Enum):
    ONE_COLUMN = "1-column"
    TWO_COLUMN = "2-column"

class OriginalFormat(str, Enum):
    PDF = "PDF"
    LATEX = "LATEX"

# Request Models
class PDFToLatexRequest(BaseModel):
    """Request model for PDF to LaTeX conversion"""
    file_id: str = Field(..., description="ID of uploaded PDF file")
    mathpix_app_id: Optional[str] = Field(None, description="MathPix App ID (optional, uses env if not provided)")
    mathpix_app_key: Optional[str] = Field(None, description="MathPix App Key (optional)")

class LaTeXFixerRequest(BaseModel):
    """Request model for LaTeX fixing"""
    file_id: str = Field(..., description="ID of uploaded LaTeX file")
    document_type: DocumentType = Field(DocumentType.RESEARCH, description="Document type (research or normal)")
    conference: ConferenceType = Field(ConferenceType.IEEE, description="Conference type")
    column_format: ColumnFormat = Field(ColumnFormat.TWO_COLUMN, description="Column format")
    converted: bool = Field(False, description="Whether document was converted from PDF")
    original_format: Optional[OriginalFormat] = Field(None, description="Original document format")
    compile_pdf: bool = Field(True, description="Whether to compile to PDF after fixing")
    images_dir_id: Optional[str] = Field(None, description="Optional: ID of uploaded images directory (if document uses images)")

class DocumentEditRequest(BaseModel):
    """Request model for prompt-based document editing"""
    file_id: str = Field(..., description="ID of uploaded LaTeX file")
    prompt: str = Field(..., description="Natural language editing instruction")
    compile_pdf: bool = Field(True, description="Whether to compile to PDF after editing")
    images_dir_id: Optional[str] = Field(None, description="Optional: ID of uploaded images directory (if document uses images)")

class DirectLatexEditRequest(BaseModel):
    """Request model for direct LaTeX code editing"""
    file_id: str = Field(..., description="ID of uploaded LaTeX file")
    latex_content: str = Field(..., description="Modified LaTeX content")
    compile_pdf: bool = Field(True, description="Whether to compile to PDF")

class CompileRequest(BaseModel):
    """Request model for LaTeX compilation"""
    file_id: str = Field(..., description="ID of LaTeX file to compile")
    engine: str = Field("pdflatex", description="LaTeX engine (pdflatex, xelatex, lualatex)")
    images_dir_id: Optional[str] = Field(None, description="Optional: ID of uploaded images directory (if document uses images)")

# Document Editor V1 Models
class DocumentEditV1Request(BaseModel):
    """Request model for document editing V1 (new editor implementation)"""
    file_id: str = Field(..., description="ID of uploaded LaTeX file")
    prompt: str = Field(..., description="Natural language editing instruction")
    compile_pdf: bool = Field(False, description="Whether to compile to PDF after editing")
    images_dir_id: Optional[str] = Field(None, description="Optional: ID of uploaded images directory")

class DocumentEditV1Response(BaseModel):
    """Response model for document editing V1"""
    success: bool = Field(..., description="Editing success status")
    file_id: str = Field(..., description="Edited LaTeX file ID")
    pdf_id: Optional[str] = Field(None, description="Compiled PDF file ID (if requested)")
    operation: str = Field(..., description="Operation performed (replace, format, remove, add, modify)")
    action: str = Field(..., description="Specific action executed")
    changes: int = Field(..., description="Number of changes applied")
    processing_time: float = Field(..., description="Processing time in seconds")
    parsed_query: Dict[str, Any] = Field(..., description="Parsed query details from AI")
    message: str = Field(..., description="Status message")
    error: Optional[str] = Field(None, description="Error message if operation failed")

class DocumentEditV1BatchRequest(BaseModel):
    """Request model for batch document editing V1"""
    file_id: str = Field(..., description="ID of uploaded LaTeX file")
    queries: List[str] = Field(..., description="List of natural language editing instructions")
    compile_pdf: bool = Field(False, description="Whether to compile to PDF after editing")
    delay: float = Field(1.5, description="Delay between operations in seconds for rate limiting")
    images_dir_id: Optional[str] = Field(None, description="Optional: ID of uploaded images directory")

class DocumentEditV1BatchResponse(BaseModel):
    """Response model for batch document editing V1"""
    success: bool = Field(..., description="Batch editing success status")
    file_id: str = Field(..., description="Final edited LaTeX file ID")
    pdf_id: Optional[str] = Field(None, description="Compiled PDF file ID (if requested)")
    total_operations: int = Field(..., description="Total number of operations requested")
    successful_operations: int = Field(..., description="Number of successful operations")
    failed_operations: int = Field(..., description="Number of failed operations")
    results: List[Dict[str, Any]] = Field(..., description="Results for each operation")
    processing_time: float = Field(..., description="Total processing time in seconds")
    message: str = Field(..., description="Status message")

# Response Models
class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    upload_time: str = Field(..., description="Upload timestamp")
    message: str = Field(..., description="Success message")

class PDFToLatexResponse(BaseModel):
    """Response model for PDF to LaTeX conversion"""
    success: bool = Field(..., description="Conversion success status")
    file_id: str = Field(..., description="Generated LaTeX file ID")
    latex_content: Optional[str] = Field(None, description="LaTeX content (if requested)")
    conversion_time: float = Field(..., description="Conversion time in seconds")
    message: str = Field(..., description="Status message")
    warnings: Optional[List[str]] = Field(None, description="Conversion warnings")

class LaTeXFixerResponse(BaseModel):
    """Response model for LaTeX fixing"""
    success: bool = Field(..., description="Fixing success status")
    file_id: str = Field(..., description="Fixed LaTeX file ID")
    pdf_id: Optional[str] = Field(None, description="Compiled PDF file ID (if requested)")
    issues_found: int = Field(..., description="Number of issues detected")
    issues_fixed: int = Field(..., description="Number of issues fixed")
    processing_time: float = Field(..., description="Processing time in seconds")
    images_copied: int = Field(0, description="Number of images copied to output directory")
    output_directory: Optional[str] = Field(None, description="Path to output directory with all files")
    converted_from_pdf: bool = Field(False, description="Whether document was converted from PDF using MathPix")
    mathpix_metadata: Optional[Dict[str, Any]] = Field(None, description="MathPix conversion metadata")
    conversion_warnings: Optional[List[str]] = Field(None, description="MathPix conversion warnings")
    report: Dict[str, Any] = Field(..., description="Detailed processing report")
    message: str = Field(..., description="Status message")

class DocumentEditResponse(BaseModel):
    """Response model for document editing"""
    success: bool = Field(..., description="Editing success status")
    file_id: str = Field(..., description="Edited LaTeX file ID")
    pdf_id: Optional[str] = Field(None, description="Compiled PDF file ID (if requested)")
    edits_applied: int = Field(..., description="Number of edits applied")
    processing_time: float = Field(..., description="Processing time in seconds")
    changes_summary: str = Field(..., description="Summary of changes made")
    message: str = Field(..., description="Status message")

class CompileResponse(BaseModel):
    """Response model for LaTeX compilation"""
    success: bool = Field(..., description="Compilation success status")
    pdf_id: Optional[str] = Field(None, description="Generated PDF file ID")
    compilation_time: float = Field(..., description="Compilation time in seconds")
    log: Optional[str] = Field(None, description="Compilation log")
    warnings: Optional[List[str]] = Field(None, description="Compilation warnings")
    errors: Optional[List[str]] = Field(None, description="Compilation errors")
    message: str = Field(..., description="Status message")

class FileDownloadResponse(BaseModel):
    """Response model for file download info"""
    file_id: str = Field(..., description="File identifier")
    filename: str = Field(..., description="File name")
    file_size: int = Field(..., description="File size in bytes")
    download_url: str = Field(..., description="Download URL")
    content_type: str = Field(..., description="File content type")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="API version")
    gemini_api_configured: bool = Field(..., description="Gemini API configuration status")
    mathpix_api_configured: bool = Field(..., description="MathPix API configuration status")
