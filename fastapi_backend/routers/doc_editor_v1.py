"""
Document Editor V1 Router - New Implementation with Advanced Editing
Uses the new editor implementation from 'new editor' folder with AI-powered query parsing
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models.schemas import DocumentEditV1Request, DocumentEditV1Response, DocumentEditV1BatchRequest, DocumentEditV1BatchResponse
from ..utils.file_manager import FileManager
import time
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directories to path to import from 'new editor' folder
backend_dir = Path(__file__).parent.parent
new_editor_dir = backend_dir / "new editor "  # Fixed: folder is inside fastapi_backend, not parent
sys.path.insert(0, str(new_editor_dir))

# Import the new editor components
try:
    from document_editor import DocumentEditor
    NEW_EDITOR_AVAILABLE = True
    print("✅ New Editor (V1) imported successfully")
except ImportError as e:
    NEW_EDITOR_AVAILABLE = False
    print(f"⚠️  New Editor (V1) not available: {e}")

router = APIRouter()

try:
    file_manager = FileManager()
except Exception as e:
    print(f"⚠️  FileManager initialization warning: {e}")
    file_manager = None


@router.post("/edit-doc-v1", response_model=DocumentEditV1Response)
async def edit_document_v1(
    request: DocumentEditV1Request,
    background_tasks: BackgroundTasks
):
    """
    Edit LaTeX document using advanced V1 editor with AI-powered natural language processing.
    
    Supports operations:
    - Replace: Change words, phrases, sentences, or section content
    - Format: Highlight, bold, or italicize text
    - Remove: Delete words, phrases, sentences, or sections
    - Add: Add sentences or sections at specific positions
    - Modify: AI-powered section improvement with specific instructions
    
    Examples:
    - "replace 'accuracy' with 'precision' in the abstract"
    - "highlight 'machine learning' in yellow"
    - "make 'neural network' bold"
    - "remove all tables from the document"
    - "modify the introduction to be more engaging"
    
    Query Format:
    Natural language instructions are automatically parsed by Gemini AI to understand intent.
    No special format needed - just describe what you want to do!
    """
    start_time = time.time()
    
    if not NEW_EDITOR_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="New Editor (V1) is not available. Check server configuration."
        )
    
    try:
        # Get uploaded file
        file_path = file_manager.get_file_path(request.file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read LaTeX content
        with open(file_path, 'r', encoding='utf-8') as f:
            latex_content = f.read()
        
        print(f"🤖 Processing V1 edit request: {request.prompt[:80]}...")
        
        # Initialize document editor
        editor = DocumentEditor()
        
        # Execute the edit
        modified_content, result_info = editor.edit(latex_content, request.prompt)
        
        # Check if operation was successful
        # Note: success=False with changes=0 is NOT an error - just means no matches found
        # Only raise error if there's an actual error message
        if not result_info.get('success', False) and result_info.get('error'):
            error_msg = result_info.get('error')
            raise HTTPException(status_code=500, detail=f"Editing failed: {error_msg}")
        
        # If success=False but no error, treat as successful operation with 0 changes
        # This happens when trying to replace/remove content that doesn't exist
        
        # Save edited LaTeX to file manager
        edited_file_id = file_manager.save_file(
            content=modified_content,
            filename=f"{request.file_id}_v1_edited.tex",
            file_type="latex"
        )
        
        # Handle PDF compilation if requested
        pdf_id = None
        if request.compile_pdf:
            try:
                # Import compiler service for PDF generation
                from ..services.compiler_service import CompilerService
                
                # Get the path to the edited LaTeX file
                edited_latex_path = file_manager.get_file_path(edited_file_id)
                
                if edited_latex_path and os.path.exists(edited_latex_path):
                    # Compile to PDF
                    compiler_service = CompilerService(engine="pdflatex")
                    compile_result = compiler_service.compile_latex(edited_latex_path)
                    
                    if compile_result.get("success") and compile_result.get("pdf_path"):
                        pdf_path = compile_result["pdf_path"]
                        if os.path.exists(pdf_path):
                            pdf_id = file_manager.save_existing_file(
                                source_path=pdf_path,
                                filename=f"{request.file_id}_v1_edited.pdf",
                                file_type="pdf"
                            )
                            print(f"✅ PDF compiled and saved: {pdf_id}")
                        else:
                            print(f"⚠️  PDF file not created at {pdf_path}")
                    else:
                        print(f"⚠️  PDF compilation failed: {compile_result}")
                else:
                    print(f"⚠️  Could not get path to edited LaTeX file")
                        
            except Exception as e:
                print(f"⚠️  PDF compilation error: {e}")
                import traceback
                traceback.print_exc()
                # Don't fail the entire request if PDF compilation fails
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Extract parsed query info
        parsed_query = result_info.get('parsed_query', {})
        operation = result_info.get('operation', 'unknown')
        action = result_info.get('action', 'unknown')
        changes = result_info.get('changes', 0)
        
        # Schedule cleanup
        background_tasks.add_task(file_manager.cleanup_temp_files)
        
        print(f"✅ V1 Editing complete: {operation}/{action} with {changes} changes ({processing_time:.2f}s)")
        
        return DocumentEditV1Response(
            success=True,
            file_id=edited_file_id,
            pdf_id=pdf_id,
            operation=operation,
            action=action,
            changes=changes,
            processing_time=processing_time,
            parsed_query=parsed_query,
            message=f"Document edited successfully. Operation: {operation}/{action}, Changes: {changes}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        processing_time = time.time() - start_time
        
        raise HTTPException(
            status_code=500,
            detail=f"Error during document editing: {str(e)}"
        )


@router.post("/batch-edit-v1", response_model=DocumentEditV1BatchResponse)
async def batch_edit_documents_v1(
    request: DocumentEditV1BatchRequest,
    background_tasks: BackgroundTasks
):
    """
    Execute multiple editing operations on a document in sequence.
    
    Parameters:
    - file_id: ID of the LaTeX file to edit
    - queries: List of natural language editing instructions
    - compile_pdf: Whether to compile final result to PDF
    - delay: Delay in seconds between operations (default: 1.5s for API rate limiting)
    
    Returns:
    - Final edited file ID
    - List of results for each operation
    - Final PDF ID if compilation requested
    """
    
    if not NEW_EDITOR_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail="New Editor (V1) is not available. Check server configuration."
        )
    
    if not request.queries or not isinstance(request.queries, list):
        raise HTTPException(status_code=400, detail="queries must be a non-empty list")
    
    try:
        start_time = time.time()
        
        # Get file
        file_path = file_manager.get_file_path(request.file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Read initial content
        with open(file_path, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Initialize editor
        editor = DocumentEditor()
        
        # Execute batch edits
        final_content, results = editor.batch_edit(current_content, request.queries, delay=request.delay)
        
        # Save final edited file
        edited_file_id = file_manager.save_file(
            content=final_content,
            filename=f"{request.file_id}_v1_batch_edited.tex",
            file_type="latex"
        )
        
        # Handle PDF compilation if requested
        pdf_id = None
        if request.compile_pdf:
            try:
                from ..services.compiler_service import CompilerService
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = Path(temp_dir)
                    temp_latex = temp_path / "document.tex"
                    temp_latex.write_text(final_content, encoding='utf-8')
                    
                    compiler_service = CompilerService(engine="pdflatex")
                    compile_result = compiler_service.compile_latex(str(temp_latex))
                    
                    if compile_result.get("success") and compile_result.get("pdf_path"):
                        pdf_path = compile_result["pdf_path"]
                        if os.path.exists(pdf_path):
                            pdf_id = file_manager.save_existing_file(
                                source_path=pdf_path,
                                filename=f"{request.file_id}_v1_batch_edited.pdf",
                                file_type="pdf"
                            )
                            
            except Exception as e:
                print(f"⚠️  PDF compilation error in batch edit: {e}")
        
        processing_time = time.time() - start_time
        
        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(file_manager.cleanup_temp_files)
        
        successful = sum(1 for r in results if r.get('success', False))
        
        return {
            "success": True,
            "file_id": edited_file_id,
            "pdf_id": pdf_id,
            "total_operations": len(request.queries),
            "successful_operations": successful,
            "failed_operations": len(request.queries) - successful,
            "results": results,
            "processing_time": processing_time,
            "message": f"Batch editing complete: {successful}/{len(request.queries)} operations successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Error during batch editing: {str(e)}"
        )
