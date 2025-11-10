#!/usr/bin/env python3
"""
Minimal test to isolate segfault
"""

import os
import sys

# Set up paths
sys.path.append('.')
sys.path.append('./src')

def test_file_loading():
    """Test file loading"""
    try:
        with open("../final research paper/glucobench .tex", 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ File loaded: {len(content)} characters")
        return content
    except Exception as e:
        print(f"❌ File loading failed: {e}")
        return None

def test_basic_processing():
    """Test basic processing without RAG"""
    content = test_file_loading()
    if not content:
        return
    
    print("Testing basic string operations...")
    
    # Test regex operations that might cause segfault
    import re
    
    # Test math pattern matching
    try:
        math_patterns = [
            (r'\$\$([^$]+)\$\$', 'display math'),
            (r'\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}', 'equation'),
        ]
        
        for pattern, name in math_patterns:
            matches = list(re.finditer(pattern, content, re.DOTALL))
            print(f"✅ {name}: found {len(matches)} matches")
            
    except Exception as e:
        print(f"❌ Regex matching failed: {e}")
        
    print("Basic processing completed")

if __name__ == "__main__":
    test_basic_processing()