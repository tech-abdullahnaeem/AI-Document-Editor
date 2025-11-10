"""
File Manager Router - File upload/download operations
"""

from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from ..models.schemas import FileUploadResponse, FileDownloadResponse
from ..utils.file_manager import FileManager
from datetime import datetime
import os

router = APIRouter()
try:
    file_manager = FileManager()
except Exception as e:
    print(f"⚠️  FileManager initialization warning: {e}")
    file_manager = None

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file (LaTeX or PDF)
    
    Supported formats:
    - .tex (LaTeX)
    - .pdf (PDF documents)
    """
    try:
        # Validate file type
        allowed_extensions = ['.tex', '.pdf']
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Save file
        file_id = file_manager.save_uploaded_file(
            content=content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        return FileUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=file_size,
            upload_time=datetime.now().isoformat(),
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {str(e)}"
        )

@router.post("/upload-images", response_model=FileUploadResponse)
async def upload_images(file: UploadFile = File(...)):
    """
    Upload images as a ZIP file
    
    Supported format:
    - .zip containing image files (.jpg, .jpeg, .png, .pdf, .eps, .svg, .gif, .bmp)
    
    Returns directory ID that can be used as images_dir_id in LaTeX fixing requests
    """
    try:
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension != '.zip':
            raise HTTPException(
                status_code=400,
                detail="Images must be uploaded as a ZIP file"
            )
        
        # Read ZIP content
        content = await file.read()
        file_size = len(content)
        
        # Extract and save images
        dir_id = file_manager.save_images_directory(
            zip_content=content,
            dir_name=os.path.splitext(file.filename)[0]
        )
        
        return FileUploadResponse(
            file_id=dir_id,
            filename=file.filename,
            file_size=file_size,
            upload_time=datetime.now().isoformat(),
            message=f"Images extracted successfully. Use this ID as images_dir_id"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading images: {str(e)}"
        )

@router.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Download a file by its ID
    """
    try:
        file_path = file_manager.get_file_path(file_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine content type
        extension = os.path.splitext(file_path)[1].lower()
        content_type_map = {
            '.tex': 'text/x-tex',
            '.pdf': 'application/pdf',
            '.log': 'text/plain'
        }
        content_type = content_type_map.get(extension, 'application/octet-stream')
        
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=os.path.basename(file_path)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading file: {str(e)}"
        )

@router.get("/info/{file_id}", response_model=FileDownloadResponse)
async def get_file_info(file_id: str):
    """
    Get information about a file
    """
    try:
        file_path = file_manager.get_file_path(file_id)
        
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        extension = os.path.splitext(file_path)[1].lower()
        
        content_type_map = {
            '.tex': 'text/x-tex',
            '.pdf': 'application/pdf',
            '.log': 'text/plain'
        }
        content_type = content_type_map.get(extension, 'application/octet-stream')
        
        return FileDownloadResponse(
            file_id=file_id,
            filename=filename,
            file_size=file_size,
            download_url=f"/api/v1/files/download/{file_id}",
            content_type=content_type
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting file info: {str(e)}"
        )

@router.delete("/delete/{file_id}")
async def delete_file(file_id: str):
    """
    Delete a file
    """
    try:
        success = file_manager.delete_file(file_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        return {
            "success": True,
            "message": f"File {file_id} deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {str(e)}"
        )
