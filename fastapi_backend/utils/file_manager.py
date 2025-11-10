"""
File Manager Utility - Handle file uploads, downloads, and storage
"""

import os
import uuid
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import json

class FileManager:
    """Manages file operations for uploads, downloads, and temporary storage"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.uploads_dir = self.base_dir / "uploads"
        self.downloads_dir = self.base_dir / "downloads"
        self.temp_dir = self.base_dir / "temp"
        
        # Create directories if they don't exist
        for directory in [self.uploads_dir, self.downloads_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # File metadata storage
        self.metadata_file = self.base_dir / "file_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> dict:
        """Load file metadata from JSON"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save file metadata to JSON"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def save_uploaded_file(self, content: bytes, filename: str, content_type: str) -> str:
        """Save uploaded file and return file ID"""
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        file_path = self.uploads_dir / f"{file_id}{file_extension}"
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Store metadata
        self.metadata[file_id] = {
            "original_filename": filename,
            "file_path": str(file_path),
            "content_type": content_type,
            "upload_time": datetime.now().isoformat(),
            "file_size": len(content)
        }
        self._save_metadata()
        
        return file_id
    
    def save_file(self, content, filename: str, file_type: str) -> str:
        """Save generated file content (string or bytes) and return file ID"""
        file_id = str(uuid.uuid4())
        
        if file_type == "latex":
            file_path = self.downloads_dir / f"{file_id}.tex"
        elif file_type == "pdf":
            file_path = self.downloads_dir / f"{file_id}.pdf"
        else:
            file_path = self.downloads_dir / f"{file_id}_{filename}"
        
        # Write file - handle both text and binary content
        if isinstance(content, bytes):
            # Binary content (e.g., PDF)
            with open(file_path, 'wb') as f:
                f.write(content)
            file_size = len(content)
        else:
            # Text content (e.g., LaTeX)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            file_size = len(content.encode('utf-8'))
        
        # Store metadata
        self.metadata[file_id] = {
            "original_filename": filename,
            "file_path": str(file_path),
            "file_type": file_type,
            "created_time": datetime.now().isoformat(),
            "file_size": file_size
        }
        self._save_metadata()
        
        return file_id
    
    def save_images_directory(self, zip_content: bytes, dir_name: str = "images") -> str:
        """
        Extract and save images from ZIP file, return directory ID
        
        Args:
            zip_content: ZIP file bytes containing images
            dir_name: Name for the images directory
            
        Returns:
            Directory ID that can be used to reference the images
        """
        import zipfile
        import io
        
        dir_id = str(uuid.uuid4())
        images_path = self.uploads_dir / f"{dir_id}_images"
        images_path.mkdir(exist_ok=True)
        
        try:
            # Extract ZIP
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
                # Filter for image files only
                image_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.eps', '.svg', '.gif', '.bmp'}
                image_files = [f for f in zip_ref.namelist() 
                             if os.path.splitext(f)[1].lower() in image_extensions]
                
                # Extract image files
                for img_file in image_files:
                    zip_ref.extract(img_file, images_path)
            
            # Count extracted images
            image_count = len(list(images_path.rglob('*.*')))
            
            # Store metadata
            self.metadata[dir_id] = {
                "original_filename": dir_name,
                "file_path": str(images_path),
                "file_type": "images_directory",
                "created_time": datetime.now().isoformat(),
                "file_size": sum(f.stat().st_size for f in images_path.rglob('*') if f.is_file()),
                "image_count": image_count
            }
            self._save_metadata()
            
            return dir_id
            
        except Exception as e:
            # Cleanup on error
            if images_path.exists():
                shutil.rmtree(images_path)
            raise Exception(f"Failed to extract images: {str(e)}")
    
    def save_existing_file(self, source_path: str, filename: str, file_type: str) -> str:
        """Copy existing file to downloads and return file ID"""
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(source_path)[1]
        file_path = self.downloads_dir / f"{file_id}{file_extension}"
        
        # Copy file
        shutil.copy2(source_path, file_path)
        
        # Store metadata
        self.metadata[file_id] = {
            "original_filename": filename,
            "file_path": str(file_path),
            "file_type": file_type,
            "created_time": datetime.now().isoformat(),
            "file_size": os.path.getsize(file_path)
        }
        self._save_metadata()
        
        return file_id
    
    def get_file_path(self, file_id: str) -> Optional[str]:
        """Get file path by file ID"""
        # Reload metadata to ensure we have the latest data
        self.metadata = self._load_metadata()
        
        if file_id in self.metadata:
            return self.metadata[file_id].get("file_path")
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file and its metadata"""
        if file_id not in self.metadata:
            return False
        
        file_path = self.metadata[file_id].get("file_path")
        if file_path and os.path.exists(file_path):
            try:
                # Check if it's a directory
                if os.path.isdir(file_path):
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except (PermissionError, OSError) as e:
                print(f"⚠️  Could not delete {file_path}: {e}")
                # Continue anyway - just log the error
        
        del self.metadata[file_id]
        self._save_metadata()
        
        return True
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        files_to_delete = []
        for file_id, metadata in self.metadata.items():
            created_time = datetime.fromisoformat(metadata.get("created_time", metadata.get("upload_time", "")))
            if created_time < cutoff_time:
                files_to_delete.append(file_id)
        
        for file_id in files_to_delete:
            self.delete_file(file_id)
        
        # Also clean temp directory
        for file_path in self.temp_dir.glob("*"):
            if file_path.is_file():
                file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age > timedelta(hours=max_age_hours):
                    os.remove(file_path)
