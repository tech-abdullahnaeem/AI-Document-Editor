#!/usr/bin/env python3
"""
Test with modified ContextAwareRAGFixer that skips FAISS
"""

import os
import sys
sys.path.append('.')
sys.path.append('./src')

# Import original classes
from enhanced_user_guided_rag import DocumentContext, LaTeXExample
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

class SafeContextAwareRAGFixer:
    """Modified version that skips FAISS to avoid segfault"""
    
    def __init__(self, api_key: str):
        """Initialize without FAISS"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.examples = []
        self.index = None
        self.load_minimal_examples()
        print("✅ SafeContextAwareRAGFixer initialized without FAISS")
    
    def load_minimal_examples(self):
        """Load minimal examples without causing segfault"""
        self.examples = [
            LaTeXExample(
                problem="Long formula in 2-column format may overflow",
                solution="Break long formulas using align environment: \\begin{align} formula_part1 &= \\\\ &\\quad formula_part2 \\end{align}",
                context="2-column format requires shorter line lengths for formulas",
                conference_tags=["ACM", "IEEE", "GENERIC"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="ACM document class missing",
                solution="Use \\documentclass[sigconf,twocolumn]{acmart} for ACM 2-column format",
                context="ACM papers require acmart document class",
                conference_tags=["ACM"],
                format_tags=["2-column"],
                issue_type="conversion"
            )
        ]
        print(f"✅ Loaded {len(self.examples)} minimal examples")

def test_safe_rag():
    """Test the safe RAG version"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No API key")
        return
    
    try:
        # Test safe RAG fixer
        rag_fixer = SafeContextAwareRAGFixer(api_key)
        print("✅ Safe RAG fixer created successfully")
        
        # Test with document context
        context = DocumentContext(
            column_format='2-column',
            conference_type='ACM',
            original_format=None,
            conversion_applied=False
        )
        print("✅ Document context created")
        
        # Load test file
        with open("../final research paper/glucobench .tex", 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ File loaded: {len(content)} characters")
        
    except Exception as e:
        print(f"❌ Safe RAG test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_safe_rag()