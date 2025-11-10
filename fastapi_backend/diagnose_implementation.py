#!/usr/bin/env python3
"""
Comprehensive diagnostic scan for edit-doc-v1 endpoint implementation
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).parent.resolve()

print("\n" + "="*90)
print(" " * 25 + "COMPREHENSIVE IMPLEMENTATION SCAN")
print("="*90)

issues_found = []
warnings_found = []

# 1. Check file structure
print("\n[1] FILE STRUCTURE CHECK")
print("-" * 90)

required_files = {
    "routers/doc_editor_v1.py": "Router file",
    "models/schemas.py": "Schemas file",
    "main.py": "Main application file",
}

for file_path, description in required_files.items():
    full_path = backend_dir / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"  ✅ {description}: {file_path} ({size} bytes)")
    else:
        issues_found.append(f"{description} missing: {file_path}")
        print(f"  ❌ {description} missing: {file_path}")

# 2. Check 'new editor' folder
print("\n[2] NEW EDITOR FOLDER CHECK")
print("-" * 90)

new_editor_dir = backend_dir / "new editor "
print(f"  Path: {new_editor_dir}")

if new_editor_dir.exists():
    print(f"  ✅ Folder exists")
    
    # Check required files
    required_modules = [
        'document_editor.py',
        'query_parser.py',
        'replace.py',
        'format.py',
        'remove.py',
        'add.py',
        'modify.py'
    ]
    
    for module in required_modules:
        module_path = new_editor_dir / module
        if module_path.exists():
            print(f"  ✅ {module}")
        else:
            issues_found.append(f"Module missing in 'new editor': {module}")
            print(f"  ❌ {module} missing")
else:
    issues_found.append("'new editor' folder not found")
    print(f"  ❌ Folder does not exist")

# 3. Check router implementation
print("\n[3] ROUTER IMPLEMENTATION CHECK")
print("-" * 90)

router_file = backend_dir / "routers" / "doc_editor_v1.py"
if router_file.exists():
    with open(router_file) as f:
        router_content = f.read()
    
    checks = [
        ("Path setup", 'backend_dir.parent / "new editor "'),
        ("DocumentEditor import", "from document_editor import DocumentEditor"),
        ("Route decorator", '@router.post("/edit-doc-v1"'),
        ("Response model", "DocumentEditV1Response"),
        ("Request model", "DocumentEditV1Request"),
        ("File manager", "file_manager.get_file_path"),
        ("Editor initialization", "editor = DocumentEditor()"),
        ("Edit execution", "editor.edit("),
        ("PDF compilation", "compile_pdf"),
        ("Error handling", "HTTPException"),
    ]
    
    for check_name, check_string in checks:
        if check_string in router_content:
            print(f"  ✅ {check_name}")
        else:
            warnings_found.append(f"Router: {check_name} not found")
            print(f"  ⚠️  {check_name} not found")
else:
    issues_found.append("Router file does not exist")

# 4. Check schemas
print("\n[4] SCHEMAS CHECK")
print("-" * 90)

schemas_file = backend_dir / "models" / "schemas.py"
if schemas_file.exists():
    with open(schemas_file) as f:
        schemas_content = f.read()
    
    schema_checks = [
        ("DocumentEditV1Request class", "class DocumentEditV1Request"),
        ("DocumentEditV1Response class", "class DocumentEditV1Response"),
        ("file_id field", "file_id: str"),
        ("prompt field", "prompt: str"),
        ("compile_pdf field", "compile_pdf: bool"),
        ("operation field", "operation: str"),
        ("changes field", "changes: int"),
        ("parsed_query field", "parsed_query: Dict"),
    ]
    
    for check_name, check_string in schema_checks:
        if check_string in schemas_content:
            print(f"  ✅ {check_name}")
        else:
            warnings_found.append(f"Schema: {check_name} not found")
            print(f"  ⚠️  {check_name} not found")
else:
    issues_found.append("Schemas file does not exist")

# 5. Check main.py registration
print("\n[5] MAIN.PY REGISTRATION CHECK")
print("-" * 90)

main_file = backend_dir / "main.py"
if main_file.exists():
    with open(main_file) as f:
        main_content = f.read()
    
    main_checks = [
        ("Import statement", "doc_editor_v1"),
        ("Router inclusion", "include_router(doc_editor_v1.router"),
        ("Correct prefix", 'prefix="/api/v1/edit"'),
        ("Tag definition", 'tags=["Document Editor V1"]'),
    ]
    
    for check_name, check_string in main_checks:
        if check_string in main_content:
            print(f"  ✅ {check_name}")
        else:
            issues_found.append(f"main.py: {check_name} not found")
            print(f"  ❌ {check_name} not found")
else:
    issues_found.append("main.py does not exist")

# 6. Check path construction
print("\n[6] PATH CONSTRUCTION CHECK")
print("-" * 90)

if router_file.exists():
    # Verify the path logic
    test_backend = Path(__file__).parent.resolve()
    test_new_editor = test_backend / "new editor "
    
    print(f"  Backend dir: {test_backend}")
    print(f"  New editor dir: {test_new_editor}")
    print(f"  New editor exists: {test_new_editor.exists()}")
    
    if test_new_editor.exists():
        print(f"  ✅ Path construction is correct")
    else:
        issues_found.append("Path construction leads to non-existent directory")
        print(f"  ❌ Path leads to non-existent directory")

# 7. Check imports compatibility
print("\n[7] IMPORT COMPATIBILITY CHECK")
print("-" * 90)

sys.path.insert(0, str(new_editor_dir))
import_issues = []

modules_to_test = [
    ('document_editor', 'DocumentEditor'),
    ('query_parser', 'QueryParser'),
    ('replace', 'SimpleReplacer'),
    ('format', 'SimpleFormatter'),
    ('remove', 'SimpleRemover'),
    ('add', 'SimpleAdder'),
    ('modify', 'SimpleModifier'),
]

for module_name, class_name in modules_to_test:
    try:
        module = __import__(module_name)
        if hasattr(module, class_name):
            print(f"  ✅ {module_name}.{class_name} importable")
        else:
            import_issues.append(f"{class_name} not found in {module_name}")
            print(f"  ⚠️  {class_name} not found in {module_name}")
    except Exception as e:
        import_issues.append(f"Cannot import {module_name}: {e}")
        print(f"  ❌ Cannot import {module_name}: {str(e)[:50]}")

# SUMMARY
print("\n" + "="*90)
print(" " * 35 + "DIAGNOSTIC SUMMARY")
print("="*90)

if not issues_found and not warnings_found and not import_issues:
    print("\n✅ ALL CHECKS PASSED - Implementation is correct!")
    print("\nThe endpoint implementation:")
    print("  ✓ Has all required files")
    print("  ✓ Uses DocumentEditor from 'new editor' folder")
    print("  ✓ Has proper schemas defined")
    print("  ✓ Is registered in main.py")
    print("  ✓ All imports are working")
else:
    if issues_found:
        print(f"\n❌ CRITICAL ISSUES FOUND: {len(issues_found)}")
        for i, issue in enumerate(issues_found, 1):
            print(f"  {i}. {issue}")
    
    if warnings_found:
        print(f"\n⚠️  WARNINGS: {len(warnings_found)}")
        for i, warning in enumerate(warnings_found, 1):
            print(f"  {i}. {warning}")
    
    if import_issues:
        print(f"\n⚠️  IMPORT ISSUES: {len(import_issues)}")
        for i, issue in enumerate(import_issues, 1):
            print(f"  {i}. {issue}")

print("\n" + "="*90)
print("\nAPI Endpoint Details:")
print("  URL: POST /api/v1/edit/edit-doc-v1")
print("  Request: DocumentEditV1Request (file_id, prompt, compile_pdf, images_dir_id)")
print("  Response: DocumentEditV1Response (success, file_id, pdf_id, operation, etc.)")
print("\nTo test:")
print("  python start_server.py")
print("  http://localhost:8000/docs")
print("="*90 + "\n")
