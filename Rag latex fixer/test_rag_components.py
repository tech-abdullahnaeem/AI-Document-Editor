#!/usr/bin/env python3
"""
Test RAG components step by step
"""

import os
import sys

# Set up paths
sys.path.append('.')
sys.path.append('./src')

def test_rag_components():
    """Test RAG components individually"""
    
    # Set API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ No API key set")
        return
        
    print("✅ API key found")
    
    # Test document context
    try:
        from enhanced_user_guided_rag import DocumentContext
        context = DocumentContext(
            column_format='2-column',
            conference_type='ACM',
            original_format=None,
            conversion_applied=False
        )
        print("✅ DocumentContext created")
    except Exception as e:
        print(f"❌ DocumentContext failed: {e}")
        return
        
    # Test RAG fixer initialization
    try:
        from enhanced_user_guided_rag import ContextAwareRAGFixer
        rag_fixer = ContextAwareRAGFixer(api_key)
        print("✅ ContextAwareRAGFixer created")
    except Exception as e:
        print(f"❌ ContextAwareRAGFixer failed: {e}")
        return
        
    # Test detector initialization
    try:
        from detectors.style_detector import StyleIssueDetector
        style_detector = StyleIssueDetector()
        print("✅ StyleIssueDetector created")
    except Exception as e:
        print(f"❌ StyleIssueDetector failed: {e}")
        return
        
    # Test format detector
    try:
        from detect_conversion_issues import DocumentFormatDetector
        format_detector = DocumentFormatDetector()
        print("✅ DocumentFormatDetector created")
    except Exception as e:
        print(f"❌ DocumentFormatDetector failed: {e}")
        return
        
    print("✅ All components initialized successfully")
    
    # Test with actual content
    try:
        with open("../final research paper/glucobench .tex", 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ File loaded: {len(content)} characters")
        
        # Test style detection
        style_issues = style_detector.detect_issues(content)
        print(f"✅ Style detection: {len(style_issues)} issues found")
        
        # Test format detection
        format_issues = format_detector.detect_issues(content)
        print(f"✅ Format detection: {len(format_issues)} issues found")
        
    except Exception as e:
        print(f"❌ Content processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_components()