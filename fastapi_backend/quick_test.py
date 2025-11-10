#!/usr/bin/env python3
"""Quick test of the edit-doc-v1 endpoint"""

import sys
from pathlib import Path

# Setup paths
backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))
new_editor_dir = backend_dir / "new editor "
sys.path.insert(0, str(new_editor_dir))

print("\n" + "="*70)
print("QUICK ENDPOINT TEST")
print("="*70)

# Test DocumentEditor directly
print("\n[1] Testing DocumentEditor directly...")
try:
    from document_editor import DocumentEditor
    
    editor = DocumentEditor()
    
    sample_latex = r"""
\documentclass{article}
\begin{document}
\section{Introduction}
Machine learning is powerful.
\end{document}
"""
    
    prompt = "replace 'powerful' with 'amazing'"
    
    print(f"   Prompt: {prompt}")
    modified, result = editor.edit(sample_latex, prompt)
    
    print(f"   ✅ Success: {result.get('success')}")
    print(f"   Operation: {result.get('operation')}")
    print(f"   Changes: {result.get('changes')}")
    
    if "amazing" in modified:
        print("   ✅ Text replacement verified!")
    else:
        print("   ❌ Text replacement failed")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test FastAPI app import
print("\n[2] Testing FastAPI app import...")
try:
    from main import app
    print("   ✅ FastAPI app imported")
    
    # Check routes
    routes = [r.path for r in app.routes]
    if "/api/v1/edit/edit-doc-v1" in routes:
        print("   ✅ Route /api/v1/edit/edit-doc-v1 registered")
    else:
        print("   ❌ Route not found in app.routes")
        print(f"   Available routes with 'edit': {[r for r in routes if 'edit' in r]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nTo test with HTTP requests:")
print("  1. Start: python start_server.py")
print("  2. Docs: http://localhost:8000/docs")
print("  3. Test endpoint: POST /api/v1/edit/edit-doc-v1")
print()
