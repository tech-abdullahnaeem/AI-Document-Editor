#!/usr/bin/env python3
"""Direct test of the edit-doc-v1 endpoint without HTTP"""

import sys
from pathlib import Path

# Setup paths
backend_dir = Path(__file__).parent.resolve()
sys.path.insert(0, str(backend_dir))

print("\n" + "="*70)
print("DIRECT ENDPOINT TEST")
print("="*70)

# Import the router
print("\n[1] Importing doc_editor_v1 router...")
try:
    from routers import doc_editor_v1
    print("   ✅ Router imported successfully")
    print(f"   NEW_EDITOR_AVAILABLE: {doc_editor_v1.NEW_EDITOR_AVAILABLE}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Import Pydantic models
print("\n[2] Importing request/response models...")
try:
    from models.schemas import DocumentEditV1Request, DocumentEditV1Response
    print("   ✅ Schemas imported successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Import file manager
print("\n[3] Importing file manager...")
try:
    from utils.file_manager import FileManager
    fm = FileManager()
    print("   ✅ FileManager initialized")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Create a test file
print("\n[4] Creating test LaTeX file...")
sample_latex = r"""\documentclass{article}
\begin{document}
\section{Introduction}
Machine learning is powerful. Deep learning is amazing.
\section{Methods}
We use neural networks for classification.
\end{document}
"""

try:
    file_id = fm.save_file(sample_latex, file_extension=".tex")
    print(f"   ✅ File created: {file_id}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test the endpoint handler directly
print("\n[5] Testing endpoint handler directly...")

test_cases = [
    {
        "name": "Replace word",
        "prompt": "replace 'powerful' with 'revolutionary'",
        "compile_pdf": False
    },
    {
        "name": "Format text (bold)",
        "prompt": "make 'Deep learning' bold",
        "compile_pdf": False
    },
    {
        "name": "Remove phrase",
        "prompt": "remove 'neural networks'",
        "compile_pdf": False
    }
]

for i, test in enumerate(test_cases, 1):
    print(f"\n   Test {i}: {test['name']}")
    print(f"   Prompt: {test['prompt']}")
    print(f"   Compile PDF: {test['compile_pdf']}")
    
    try:
        # Create request
        request = DocumentEditV1Request(
            file_id=file_id,
            prompt=test['prompt'],
            compile_pdf=test['compile_pdf']
        )
        
        # Call the endpoint handler
        response = doc_editor_v1.edit_document_v1(request)
        
        print(f"   ✅ Response received")
        print(f"      Success: {response['success']}")
        print(f"      Operation: {response['operation']}")
        print(f"      Action: {response['action']}")
        print(f"      Changes: {response['changes']}")
        print(f"      Processing time: {response['processing_time']:.2f}s")
        print(f"      New file ID: {response['file_id']}")
        if response.get('pdf_id'):
            print(f"      PDF ID: {response['pdf_id']}")
        
        # Update file_id for next test
        file_id = response['file_id']
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
print("✅ DIRECT ENDPOINT TEST COMPLETE")
print("="*70)
print()
