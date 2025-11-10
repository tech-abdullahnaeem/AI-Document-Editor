"""
LaTeX Compiler Router - Compile LaTeX to PDF
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from ..models.schemas import CompileRequest, CompileResponse
from ..services.compiler_service import CompilerService
from ..utils.file_manager import FileManager
import time
import os
import shutil
from pathlib import Path
from typing import Optional

router = APIRouter()
try:
    file_manager = FileManager()
except Exception as e:
    print(f"⚠️  FileManager initialization warning: {e}")
    file_manager = None

def find_images_directory(latex_file_path: str) -> Optional[str]:
    """
    Find images directory near the LaTeX file or in common locations
    Looks for: ./images/, ../images/, or in the RAG output directory
    """
    latex_dir = Path(latex_file_path).parent
    
    # Check for images in same directory as LaTeX file
    same_dir_images = latex_dir / "images"
    if same_dir_images.exists() and same_dir_images.is_dir():
        return str(same_dir_images)
    
    # Check parent directory
    parent_images = latex_dir.parent / "images"
    if parent_images.exists() and parent_images.is_dir():
        return str(parent_images)
    
    # Check in RAG output directory (common location) - dynamically find base path
    base_dir = Path(__file__).parent.parent.parent
    rag_output = base_dir / "latex fixed output:input" / "images"
    if rag_output.exists() and rag_output.is_dir():
        return str(rag_output)
    
    return None

def copy_images_to_latex_dir(latex_path: str) -> int:
    """
    Copy images to the LaTeX file's directory so they can be found during compilation
    Returns number of images copied
    """
    latex_file = Path(latex_path)
    latex_dir = latex_file.parent
    
    # Find source images directory
    source_images = find_images_directory(latex_path)
    if not source_images or not Path(source_images).exists():
        print(f"⚠️  No images directory found")
        return 0
    
    source_images_path = Path(source_images)
    target_images_dir = latex_dir / "images"
    
    try:
        # Create images directory in LaTeX folder
        target_images_dir.mkdir(exist_ok=True)
        
        # Copy all images directly to target (flatten subdirectories)
        images_copied = 0
        for image_file in source_images_path.rglob('*.jpg'):
            if image_file.is_file():
                # Copy directly without subdirectories
                target_file = target_images_dir / image_file.name
                shutil.copy2(image_file, target_file)
                images_copied += 1
                print(f"   ✅ Copied: {image_file.name}")
        
        if images_copied > 0:
            print(f"📸 Successfully copied {images_copied} image files to {target_images_dir}")
        
        return images_copied
        
    except Exception as e:
        print(f"❌ Error copying images: {e}")
        return 0

@router.post("/pdf", response_model=CompileResponse)
async def compile_to_pdf(
    request: CompileRequest,
    background_tasks: BackgroundTasks
):
    """
    Compile LaTeX document to PDF
    
    Supported engines:
    - pdflatex (default)
    - xelatex
    - lualatex
    """
    start_time = time.time()
    
    try:
        # Get LaTeX file
        latex_path = file_manager.get_file_path(request.file_id)
        if not latex_path or not os.path.exists(latex_path):
            raise HTTPException(status_code=404, detail="LaTeX file not found")
        
        # Validate file is LaTeX
        if not latex_path.lower().endswith('.tex'):
            raise HTTPException(status_code=400, detail="File must be a LaTeX (.tex) file")
        
        # Copy images to LaTeX directory so they can be found during compilation
        print(f"\n📸 COPYING IMAGES FOR COMPILATION")
        print(f"{'='*60}")
        images_copied = copy_images_to_latex_dir(latex_path)
        
        # Initialize compiler service
        compiler_service = CompilerService(engine=request.engine)
        
        # Compile LaTeX to PDF (not async)
        result = compiler_service.compile_latex(latex_path)
        
        # Save PDF
        pdf_id = None
        if result.get("pdf_path") and os.path.exists(result["pdf_path"]):
            pdf_id = file_manager.save_existing_file(
                source_path=result["pdf_path"],
                filename=f"{request.file_id}_compiled.pdf",
                file_type="pdf"
            )
        
        compilation_time = time.time() - start_time
        
        # Schedule cleanup
        background_tasks.add_task(file_manager.cleanup_temp_files)
        
        return CompileResponse(
            success=result["success"],
            pdf_id=pdf_id if result["success"] else None,
            compilation_time=compilation_time,
            log=result.get("log"),
            warnings=result.get("warnings", []),
            errors=result.get("errors", []),
            message=f"LaTeX compiled successfully (copied {images_copied} images)" if result["success"] else "Compilation failed"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error compiling LaTeX: {str(e)}"
        )
