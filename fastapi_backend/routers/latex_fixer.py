"""
LaTeX Fixer Router - RAG-based LaTeX fixing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models.schemas import LaTeXFixerRequest, LaTeXFixerResponse
from ..services.rag_fixer_service_full import RAGFixerService
from ..utils.file_manager import FileManager
import time
import os

router = APIRouter()

# Initialize file_manager safely
try:
    file_manager = FileManager()
except Exception as e:
    print(f"⚠️  FileManager initialization warning: {e}")
    file_manager = None

@router.post("/latex-rag", response_model=LaTeXFixerResponse)
async def fix_latex_rag(
    request: LaTeXFixerRequest,
    background_tasks: BackgroundTasks
):
    """
    Fix LaTeX document using RAG-based approach
    
    - Detects and fixes LaTeX issues using contextual examples
    - Applies conference-specific formatting
    - Handles conversion issues from PDF to LaTeX
    - Optionally compiles to PDF
    """
    start_time = time.time()
    
    try:
        # Get uploaded file
        file_path = file_manager.get_file_path(request.file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if it's a PDF file (will be auto-converted by service)
        is_pdf = file_path.lower().endswith('.pdf')
        
        # Read file content (will be LaTeX or PDF)
        if is_pdf:
            print(f"📄 PDF file detected, will be converted to LaTeX by MathPix")
            latex_content = ""  # Will be populated by MathPix in service
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                latex_content = f.read()
        
        # Get images directory if provided
        images_dir = None
        if request.images_dir_id:
            images_dir = file_manager.get_file_path(request.images_dir_id)
            if not images_dir or not os.path.exists(images_dir):
                print(f"⚠️  Images directory not found: {request.images_dir_id}")
                images_dir = None
        
        # Initialize RAG fixer service
        rag_service = RAGFixerService()
        
        # Process document (will auto-detect and convert PDF if needed)
        result = await rag_service.fix_latex_document(
            latex_content=latex_content,
            document_type=request.document_type.value,
            conference=request.conference.value,
            column_format=request.column_format.value,
            converted=request.converted,
            original_format=request.original_format.value if request.original_format else None,
            compile_pdf=request.compile_pdf,
            images_dir=images_dir,
            file_path=file_path  # Pass file path for PDF detection
        )
        
        # Save fixed LaTeX
        fixed_file_id = file_manager.save_file(
            content=result["fixed_content"],
            filename=f"{request.file_id}_fixed.tex",
            file_type="latex"
        )
        
        # Save PDF if it was compiled
        pdf_id = None
        if request.compile_pdf and result.get("pdf_content"):
            # Save PDF from bytes content
            pdf_id = file_manager.save_file(
                content=result["pdf_content"],
                filename=f"{request.file_id}_fixed.pdf",
                file_type="pdf"
            )
        
        processing_time = time.time() - start_time
        
        # Schedule cleanup of temporary files
        background_tasks.add_task(file_manager.cleanup_temp_files)
        
        # Build success message
        message_parts = []
        if result.get("converted_from_pdf"):
            message_parts.append("✅ MathPix conversion SUCCESS")
        if result.get("issues_fixed", 0) > 0:
            message_parts.append(f"✅ RAG processing SUCCESS - {result.get('issues_fixed', 0)} issues fixed")
        else:
            message_parts.append("LaTeX document processed successfully")
        if result.get("output_directory"):
            message_parts.append(f"Files saved to: {result.get('output_directory')}")
        
        return LaTeXFixerResponse(
            success=True,
            file_id=fixed_file_id,
            pdf_id=pdf_id,
            issues_found=result.get("issues_found", 0),
            issues_fixed=result.get("issues_fixed", 0),
            processing_time=processing_time,
            images_copied=result.get("images_copied", 0),
            output_directory=result.get("output_directory"),
            converted_from_pdf=result.get("converted_from_pdf", False),
            mathpix_metadata=result.get("mathpix_metadata"),
            conversion_warnings=result.get("conversion_warnings"),
            report=result.get("report", {}),
            message=" | ".join(message_parts)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fixing LaTeX document: {str(e)}"
        )

@router.post("/latex-simple", response_model=LaTeXFixerResponse)
async def fix_latex_simple(
    request: LaTeXFixerRequest,
    background_tasks: BackgroundTasks
):
    """
    Fix LaTeX document using simple rule-based approach (no RAG)
    
    - Faster processing
    - Basic fixes without contextual examples
    - Good for simple documents
    """
    start_time = time.time()
    
    try:
        file_path = file_manager.get_file_path(request.file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            latex_content = f.read()
        
        rag_service = RAGFixerService()
        
        # Use simple fixing method
        result = await rag_service.fix_latex_simple(
            latex_content=latex_content,
            document_type=request.document_type.value,
            compile_pdf=request.compile_pdf
        )
        
        fixed_file_id = file_manager.save_file(
            content=result["fixed_content"],
            filename=f"{request.file_id}_simple_fixed.tex",
            file_type="latex"
        )
        
        pdf_id = None
        if request.compile_pdf and result.get("pdf_path"):
            pdf_id = file_manager.save_existing_file(
                source_path=result["pdf_path"],
                filename=f"{request.file_id}_simple_fixed.pdf",
                file_type="pdf"
            )
        
        processing_time = time.time() - start_time
        background_tasks.add_task(file_manager.cleanup_temp_files)
        
        return LaTeXFixerResponse(
            success=True,
            file_id=fixed_file_id,
            pdf_id=pdf_id,
            issues_found=result.get("issues_found", 0),
            issues_fixed=result.get("issues_fixed", 0),
            processing_time=processing_time,
            report=result.get("report", {}),
            message="LaTeX document fixed successfully (simple mode)"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fixing LaTeX document: {str(e)}"
        )
