#!/usr/bin/env python3
"""
Download processed files from the API
"""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8001"
API_KEY = "your-secret-api-key-change-this"
HEADERS = {"X-API-Key": API_KEY}

def download_file(file_id, output_name):
    """Download a file from the API"""
    print(f"📥 Downloading {file_id}...")
    response = requests.get(f"{BASE_URL}/api/v1/files/download/{file_id}", headers=HEADERS)
    
    if response.status_code == 200:
        output_path = Path(output_name)
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Saved to: {output_path.absolute()}")
        print(f"   Size: {len(response.content)} bytes\n")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.text}\n")
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("  FILE DOWNLOAD UTILITY")
    print("="*70 + "\n")
    
    # From the last test run:
    # Original: 8835dc91-cfd0-4393-9020-9fa46cb668ef
    # Fixed: 0b566b52-7ac1-43a2-9d5f-43af15a57e17
    # Edited: e79fccab-b48e-4cc4-8df0-8270416203d6
    # PDF: b7e4573f-1ea5-4cc8-b739-481402334374
    
    files_to_download = [
        ("8835dc91-cfd0-4393-9020-9fa46cb668ef", "original.tex"),
        ("0b566b52-7ac1-43a2-9d5f-43af15a57e17", "fixed_by_rag.tex"),
        ("e79fccab-b48e-4cc4-8df0-8270416203d6", "edited_by_ai.tex"),
        ("b7e4573f-1ea5-4cc8-b739-481402334374", "compiled.pdf"),
    ]
    
    success_count = 0
    for file_id, output_name in files_to_download:
        if download_file(file_id, output_name):
            success_count += 1
    
    print("="*70)
    print(f"✅ Downloaded {success_count}/{len(files_to_download)} files")
    print("="*70 + "\n")
