"""
Debug Router - Test endpoints for debugging
"""

from fastapi import APIRouter, HTTPException
from ..utils.file_manager import FileManager
import os
import json

router = APIRouter()

@router.get("/debug/file/{file_id}")
async def debug_file_access(file_id: str):
    """Debug endpoint to check file access"""
    try:
        # Create FileManager instance
        file_manager = FileManager()
        
        debug_info = {
            "file_id": file_id,
            "base_dir": str(file_manager.base_dir),
            "uploads_dir": str(file_manager.uploads_dir),
            "metadata_file": str(file_manager.metadata_file),
            "metadata_file_exists": os.path.exists(file_manager.metadata_file),
            "metadata_keys": list(file_manager.metadata.keys()),
            "file_id_in_metadata": file_id in file_manager.metadata,
        }
        
        # Test get_file_path
        file_path = file_manager.get_file_path(file_id)
        debug_info["file_path"] = file_path
        debug_info["file_path_exists"] = os.path.exists(file_path) if file_path else False
        
        if file_path and os.path.exists(file_path):
            debug_info["file_size"] = os.path.getsize(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(100)
                debug_info["content_preview"] = content
        
        return debug_info
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")

@router.get("/debug/metadata")
async def debug_metadata():
    """Debug endpoint to check metadata"""
    try:
        file_manager = FileManager()
        return {
            "metadata_file": str(file_manager.metadata_file),
            "metadata_exists": os.path.exists(file_manager.metadata_file),
            "metadata": file_manager.metadata,
            "uploads_dir": str(file_manager.uploads_dir),
            "uploads_files": [f.name for f in file_manager.uploads_dir.glob("*")]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Debug error: {str(e)}")