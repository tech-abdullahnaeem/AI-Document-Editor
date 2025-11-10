#!/usr/bin/env python3
"""
Test individual components causing segfault
"""

import os
import sys

def test_sentence_transformer():
    """Test SentenceTransformer loading"""
    try:
        print("Loading SentenceTransformer...")
        from sentence_transformers import SentenceTransformer
        encoder = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ SentenceTransformer loaded successfully")
        
        # Test encoding
        test_text = "This is a test sentence"
        embedding = encoder.encode(test_text)
        print(f"✅ Encoding test successful: {embedding.shape}")
        
    except Exception as e:
        print(f"❌ SentenceTransformer failed: {e}")
        import traceback
        traceback.print_exc()

def test_faiss():
    """Test FAISS loading"""
    try:
        print("Loading FAISS...")
        import faiss
        print("✅ FAISS loaded successfully")
        
        # Test basic FAISS operations
        import numpy as np
        dimension = 384
        index = faiss.IndexFlatL2(dimension)
        print(f"✅ FAISS index created: {index}")
        
    except Exception as e:
        print(f"❌ FAISS failed: {e}")
        import traceback
        traceback.print_exc()

def test_google_ai():
    """Test Google AI"""
    try:
        print("Loading Google Generative AI...")
        import google.generativeai as genai
        print("✅ Google AI loaded successfully")
        
        # Test configuration (don't actually initialize model)
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            print("✅ Google AI configured")
        else:
            print("⚠️ No API key for Google AI test")
            
    except Exception as e:
        print(f"❌ Google AI failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing individual components...")
    test_sentence_transformer()
    test_faiss()  
    test_google_ai()
    print("Individual component testing completed")