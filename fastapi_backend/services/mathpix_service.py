"""
MathPix Service - PDF to LaTeX conversion using MathPix Official SDK (mpxpy)
"""

import os
import time
import asyncio
import zipfile
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv()

# Thread pool for running sync SDK operations
executor = ThreadPoolExecutor(max_workers=4)

class MathPixService:
    """Service for MathPix API integration using official SDK (mpxpy)"""
    
    def __init__(self, app_id: Optional[str] = None, app_key: Optional[str] = None):
        """
        Initialize MathPix service with official SDK
        
        Args:
            app_id: MathPix App ID (optional, uses env variable if not provided)
            app_key: MathPix App Key (optional, uses env variable if not provided)
        """
        self.app_id = app_id or os.getenv("MATHPIX_APP_ID")
        self.app_key = app_key or os.getenv("MATHPIX_APP_KEY")
        
        print(f"🔑 Initializing MathPix Official SDK with credentials")
        print(f"   APP_ID: {self.app_id[:15]}..." if self.app_id else "   APP_ID: None")
        print(f"   APP_KEY: {self.app_key[:15]}..." if self.app_key else "   APP_KEY: None")
        
        if not self.app_id or not self.app_key:
            raise ValueError("MathPix credentials required (MATHPIX_APP_ID and MATHPIX_APP_KEY)")
        
        print("✅ MathPix Official SDK service initialized")

    def _convert_pdf_sync(self, pdf_path: str) -> Dict[str, Any]:
        """
        Synchronous PDF to LaTeX conversion using MathPix Official SDK
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with conversion results including extracted images
        """
        try:
            from mpxpy.mathpix_client import MathpixClient
            
            print(f"🔄 Converting PDF using MathPix Official SDK: {pdf_path}")
            
            # Initialize the MathPix client
            client = MathpixClient(
                app_id=self.app_id,
                app_key=self.app_key
            )
            
            # Convert PDF to LaTeX
            print("📤 Uploading PDF to MathPix...")
            result = client.pdf_new(
                pdf_path,
                convert_to_tex_zip=True
            )
            
            print("⏳ Waiting for conversion to complete...")
            result.wait_until_complete()
            
            print("📥 Downloading LaTeX ZIP...")
            # Get LaTeX content as bytes (ZIP file)
            latex_zip_bytes = result.to_tex_zip_bytes()
            
            print(f"📦 Received ZIP file of size: {len(latex_zip_bytes)} bytes")
            
            # Create a temporary directory to extract all files
            with tempfile.TemporaryDirectory() as temp_extract_dir:
                # Save ZIP file temporarily
                with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
                    temp_zip.write(latex_zip_bytes)
                    temp_zip_path = temp_zip.name
                
                try:
                    # Extract ALL files from the ZIP
                    with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_extract_dir)
                        extracted_files = zip_ref.namelist()
                        
                        print(f"📦 Extracted {len(extracted_files)} files:")
                        for file in extracted_files:
                            print(f"   📄 {file}")
                        
                        # Categorize files
                        tex_files = [f for f in extracted_files if f.endswith('.tex')]
                        image_files = [f for f in extracted_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.eps'))]
                        other_files = [f for f in extracted_files if not f.endswith('.tex') and not f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.pdf', '.eps'))]
                        
                        print(f"📊 File breakdown: {len(tex_files)} .tex, {len(image_files)} images, {len(other_files)} other")
                        
                        if not tex_files:
                            return {
                                "success": False,
                                "error": "No LaTeX file found in conversion result"
                            }
                        
                        # Read the main LaTeX file
                        main_tex_file = tex_files[0]
                        main_tex_path = os.path.join(temp_extract_dir, main_tex_file)
                        
                        print(f"📄 Reading main LaTeX from: {main_tex_file}")
                        with open(main_tex_path, 'r', encoding='utf-8') as f:
                            latex_content = f.read()
                        
                        # Read all extracted files into memory
                        extracted_file_data = {}
                        for file_name in extracted_files:
                            file_path = os.path.join(temp_extract_dir, file_name)
                            if os.path.isfile(file_path):
                                if file_name.endswith('.tex') or file_name.endswith('.txt'):
                                    # Read text files as text
                                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                        extracted_file_data[file_name] = {
                                            'type': 'text',
                                            'content': f.read(),
                                            'size': os.path.getsize(file_path)
                                        }
                                else:
                                    # Read binary files (images) as bytes
                                    with open(file_path, 'rb') as f:
                                        extracted_file_data[file_name] = {
                                            'type': 'binary',
                                            'content': f.read(),
                                            'size': os.path.getsize(file_path)
                                        }
                    
                    print(f"✅ Successfully extracted LaTeX content ({len(latex_content)} characters) and {len(image_files)} images")
                    
                    return {
                        "success": True,
                        "latex_content": latex_content,
                        "extracted_files": extracted_file_data,
                        "file_structure": {
                            "tex_files": tex_files,
                            "image_files": image_files,
                            "other_files": other_files,
                            "total_files": len(extracted_files)
                        },
                        "mathpix_metadata": {
                            "conversion_method": "official_sdk_mpxpy",
                            "main_file": main_tex_file,
                            "total_tex_files": len(tex_files),
                            "total_images": len(image_files),
                            "zip_size": len(latex_zip_bytes)
                        },
                        "warnings": []
                    }
                    
                finally:
                    # Clean up temporary ZIP file
                    os.unlink(temp_zip_path)
                
        except ImportError as e:
            print(f"❌ MathPix SDK import error: {e}")
            return {
                "success": False,
                "error": "MathPix SDK (mpxpy) not installed. Run: pip install mpxpy"
            }
        except Exception as e:
            print(f"❌ Error during PDF conversion: {str(e)}")
            return {
                "success": False,
                "error": f"Conversion error: {str(e)}"
            }
    
    async def convert_pdf_to_latex(self, pdf_path: str) -> Dict[str, Any]:
        """
        Convert PDF to LaTeX using MathPix Official SDK (async wrapper)
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with conversion results
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        print(f"📄 Starting async PDF to LaTeX conversion: {Path(pdf_path).name}")
        
        # Run the synchronous SDK operation in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, self._convert_pdf_sync, pdf_path)
        
        print(f"🎯 Conversion completed. Success: {result.get('success')}")
        return result
