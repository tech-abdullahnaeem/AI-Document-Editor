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
    Intelligently find images directory by:
    1. Extracting image references from LaTeX file
    2. Searching Mathpix conversion directories for matching images
    3. Falling back to standard locations
    
    This enables finding images for both new and edited documents.
    """
    import re
    
    latex_dir = Path(latex_file_path).parent
    
    # Step 1: Extract image names from LaTeX file
    try:
        with open(latex_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            latex_content = f.read()
        
        # Find all \includegraphics{filename} references
        image_refs = re.findall(r'\\includegraphics(?:\[.*?\])?\{([^}]+)\}', latex_content)
        if image_refs:
            print(f"   📝 Found image references in LaTeX: {image_refs[:3]}{'...' if len(image_refs) > 3 else ''}")
    except Exception as e:
        print(f"   ⚠️  Could not read LaTeX file: {e}")
        image_refs = []
    
    # Step 2: Search Mathpix conversion directories
    base_dir = Path(__file__).parent.parent.parent
    rag_output = base_dir / "latex fixed output:input" / "images"
    
    if rag_output.exists() and rag_output.is_dir():
        # Look for conversion directories (e.g., 2025_11_11_d9f2e0b53544faad84bbg)
        for conv_dir in rag_output.iterdir():
            if conv_dir.is_dir():
                images_subdir = conv_dir / "images"
                if images_subdir.exists() and images_subdir.is_dir():
                    # Check if this directory contains any of our referenced images
                    images_in_dir = list(images_subdir.glob('*.jpg'))
                    if images_in_dir:
                        # If we have image refs, check if they match
                        if image_refs:
                            dir_image_names = {img.stem for img in images_in_dir}
                            matching = [ref for ref in image_refs if ref in dir_image_names]
                            if matching:
                                print(f"   ✅ Found matching images in: {conv_dir.name}/images")
                                return str(images_subdir)
                        else:
                            # No image refs found in LaTeX, return first conversion with images
                            print(f"   ✅ Found images directory: {conv_dir.name}/images")
                            return str(images_subdir)
    
    # Step 3: Check standard locations
    print(f"   🔍 Standard locations not found, checking fallbacks...")
    
    # Check for images in same directory as LaTeX file
    same_dir_images = latex_dir / "images"
    if same_dir_images.exists() and same_dir_images.is_dir():
        images_found = list(same_dir_images.glob('*.jpg'))
        if images_found:
            print(f"   ✅ Found {len(images_found)} images in: {same_dir_images}")
            return str(same_dir_images)
    
    # Check parent directory
    parent_images = latex_dir.parent / "images"
    if parent_images.exists() and parent_images.is_dir():
        images_found = list(parent_images.glob('*.jpg'))
        if images_found:
            print(f"   ✅ Found {len(images_found)} images in: {parent_images}")
            return str(parent_images)
    
    print(f"   ❌ No images directory found")
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
                
                # Skip if source and target are the same file
                try:
                    if image_file.samefile(target_file):
                        print(f"   ℹ️  Already in place: {image_file.name}")
                        images_copied += 1
                        continue
                except (OSError, ValueError):
                    # File doesn't exist yet or paths are not comparable
                    pass
                
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
