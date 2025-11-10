"""
Document Editor Router - Prompt-based LaTeX editing (CLI Logic Implementation)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models.schemas import DocumentEditRequest, DirectLatexEditRequest, DocumentEditResponse
from ..utils.file_manager import FileManager
import time
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directories to path to access doc_edit modules
parent_dir = Path(__file__).parent.parent.parent
src_dir = parent_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(parent_dir))

from doc_edit.document_editor import DocumentEditor

router = APIRouter()
try:
    file_manager = FileManager()
except Exception as e:
    print(f"⚠️  FileManager initialization warning: {e}")
    file_manager = None

@router.post("/prompt", response_model=DocumentEditResponse)
async def edit_with_prompt(
    request: DocumentEditRequest,
    background_tasks: BackgroundTasks
):
    """
    Edit LaTeX document using natural language prompts - EXACT CLI LOGIC
    
    This endpoint now uses the EXACT SAME logic as the CLI version:
    - Surgical editing with LaTeX Annotator
    - AI-powered Query Analyzer for object identification
    - Surgical Editor for precise modifications
    - Same 200-char preview logic
    - Same fallback mechanisms
    
    Examples:
    - "change the word 'data' with 'abdullah' in the document"
    - "remove all tables from the document"
    - "modify the table caption with 'abdullah is great'"
    - "highlight all equations in yellow"
    """
    start_time = time.time()
    
    try:
        # Get uploaded file
        file_path = file_manager.get_file_path(request.file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check for images directory if provided
        source_images_dir = None
        if request.images_dir_id:
            images_path = file_manager.get_file_path(request.images_dir_id)
            if images_path and os.path.exists(images_path) and os.path.isdir(images_path):
                source_images_dir = images_path
                print(f"📸 Using images directory: {images_path}")
        
        # Get API key from environment
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        # Create temporary working directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            # Copy the source file to temp directory
            temp_latex_file = temp_dir_path / "input.tex"
            shutil.copy2(file_path, temp_latex_file)
            
            # Copy images if source images directory is provided
            if source_images_dir:
                dest_images_dir = temp_dir_path / "images"
                try:
                    shutil.copytree(source_images_dir, dest_images_dir)
                    image_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.eps', '.svg', '.gif', '.bmp', '.tiff'}
                    images_copied = sum(1 for f in dest_images_dir.rglob('*') 
                                      if f.is_file() and f.suffix.lower() in image_extensions)
                    print(f"📸 Copied {images_copied} image files to working directory")
                except Exception as e:
                    print(f"⚠️  Warning: Could not copy images: {e}")
            
            # Create output directory within temp
            output_dir = temp_dir_path / "output"
            output_dir.mkdir(exist_ok=True)
            
            # Initialize DocumentEditor with EXACT same parameters as CLI
            editor = DocumentEditor(
                api_key=gemini_api_key,
                gemini_model="gemini-2.0-flash-exp",  # Same model as CLI
                output_dir=str(output_dir),
                latex_engine="pdflatex",
                require_latex=not request.compile_pdf,  # Only require LaTeX if we need to compile
                debug_mode=True  # Always enable debug mode for reports
            )
            
            print(f"🤖 Processing edit request: {request.prompt[:80]}...")
            
            # Call the EXACT SAME method used by CLI: edit_latex_file
            result = editor.edit_latex_file(
                latex_path=str(temp_latex_file),
                edit_prompt=request.prompt,
                output_filename="output",
                context=None,
                modify_original=False
            )
            
            if not result.get("success", False):
                error_msg = result.get("error", "Unknown error")
                raise HTTPException(status_code=500, detail=f"Editing failed: {error_msg}")
            
            # Get edited content
            edited_latex = result.get("edited_latex")
            if not edited_latex:
                raise HTTPException(status_code=500, detail="No edited content returned")
            
            # Save edited LaTeX to file manager
            edited_file_id = file_manager.save_file(
                content=edited_latex,
                filename=f"{request.file_id}_edited.tex",
                file_type="latex"
            )
            
            # Handle PDF compilation if requested
            pdf_id = None
            if request.compile_pdf:
                pdf_path = result.get("pdf_file")
                if pdf_path and os.path.exists(pdf_path):
                    pdf_id = file_manager.save_existing_file(
                        source_path=pdf_path,
                        filename=f"{request.file_id}_edited.pdf",
                        file_type="pdf"
                    )
                    print(f"✅ PDF compiled and saved: {pdf_id}")
                else:
                    print(f"⚠️  PDF compilation was requested but file not available")
            
            # Calculate changes summary
            original_latex = result.get("original_latex", "")
            if edited_latex != original_latex:
                changes = len(edited_latex) - len(original_latex)
                changes_summary = f"Document edited successfully. Size changed by {changes:+d} characters."
                edits_applied = 1
                
                # Try to get detailed info from JSON report
                json_report_path = result.get("json_report")
                if json_report_path and os.path.exists(json_report_path):
                    import json
                    try:
                        with open(json_report_path, 'r') as f:
                            json_data = json.load(f)
                            matched_objects = json_data.get("matched_objects", [])
                            edits_applied = len(matched_objects) if matched_objects else 1
                            changes_summary = f"Applied {edits_applied} surgical edits to document"
                    except Exception as e:
                        print(f"⚠️  Could not parse JSON report: {e}")
            else:
                changes_summary = "No changes were made to the document"
                edits_applied = 0
            
            processing_time = time.time() - start_time
            background_tasks.add_task(file_manager.cleanup_temp_files)
            
            print(f"✅ Editing complete: {changes_summary} ({processing_time:.2f}s)")
            
            return DocumentEditResponse(
                success=True,
                file_id=edited_file_id,
                pdf_id=pdf_id,
                edits_applied=edits_applied,
                processing_time=processing_time,
                changes_summary=changes_summary,
                message="Document edited successfully using CLI logic"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error editing document: {str(e)}"
        )

@router.post("/latex-direct", response_model=DocumentEditResponse)
async def edit_latex_directly(
    request: DirectLatexEditRequest,
    background_tasks: BackgroundTasks
):
    """
    Update LaTeX document with directly edited content
    
    ⚠️ NOT IMPLEMENTED YET - This endpoint is placeholder for future implementation
    
    Allows users to edit LaTeX code manually in a code editor
    """
    raise HTTPException(
        status_code=501,
        detail="Direct LaTeX editing not implemented yet. Please use prompt-based editing."
    )

@router.get("/preview/{file_id}")
async def preview_latex(file_id: str):
    """
    Get LaTeX content for preview/editing
    """
    try:
        file_path = file_manager.get_file_path(file_id)
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "file_id": file_id,
            "content": content,
            "line_count": len(content.split('\n')),
            "character_count": len(content)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving LaTeX content: {str(e)}"
        )
