#!/usr/bin/env python3
"""
Quick Comprehensive Test - All Operations
Tests FORMAT, REPLACE, MODIFY, REMOVE, ADD with 10-second delays
"""

import requests
import time

BASE_URL = "http://localhost:8000"
DELAY = 10

def test(name, payload, expected_min_changes=0):
    """Run a single test"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Prompt: {payload['prompt'][:70]}...")
    
    start = time.time()
    resp = requests.post(f"{BASE_URL}/api/v1/edit/edit-doc-v1", json=payload, timeout=120)
    elapsed = time.time() - start
    
    if resp.status_code == 200:
        result = resp.json()
        changes = result.get('changes', 0)
        success = "✅" if changes >= expected_min_changes else "⚠️"
        print(f"{success} Status: {resp.status_code} | Changes: {changes} | Time: {elapsed:.1f}s")
        print(f"   Operation: {result.get('operation')}/{result.get('action')}")
        return result.get('file_id'), changes > 0
    else:
        print(f"❌ FAILED: {resp.status_code}")
        print(f"   Error: {resp.text[:100]}")
        return payload['file_id'], False

# Start
print("\n" + "="*60)
print("COMPREHENSIVE API TEST - ALL OPERATIONS")
print("="*60)

file_id = "3345c6b2-4590-4c3f-9aba-65cb6dcfefd4"
results = {"passed": 0, "failed": 0}

# TEST 1: REPLACE
file_id, success = test(
    "REPLACE - Words",
    {"file_id": file_id, "prompt": "replace 'glucose' with 'blood glucose'", "compile_pdf": False},
    expected_min_changes=1
)
results["passed" if success else "failed"] += 1
time.sleep(DELAY)

# TEST 2: FORMAT
file_id, success = test(
    "FORMAT - Bold",
    {"file_id": file_id, "prompt": "make 'blood glucose' bold", "compile_pdf": False},
    expected_min_changes=1
)
results["passed" if success else "failed"] += 1
time.sleep(DELAY)

# TEST 3: FORMAT - Highlight
file_id, success = test(
    "FORMAT - Highlight",
    {"file_id": file_id, "prompt": "highlight 'diabetes' in yellow", "compile_pdf": False},
    expected_min_changes=1
)
results["passed" if success else "failed"] += 1
time.sleep(DELAY)

# TEST 4: REMOVE
file_id, success = test(
    "REMOVE - Section",
    {"file_id": file_id, "prompt": "remove the Acknowledgments section", "compile_pdf": False},
    expected_min_changes=1
)
results["passed" if success else "failed"] += 1
time.sleep(DELAY)

# TEST 5: ADD - Section with AI
file_id, success = test(
    "ADD - Section (AI Generated)",
    {"file_id": file_id, "prompt": "create a new section titled 'Future Works' discussing emerging CGM technologies", "compile_pdf": False},
    expected_min_changes=1
)
results["passed" if success else "failed"] += 1
time.sleep(DELAY)

# TEST 6: ADD - Content to section
file_id, success = test(
    "ADD - Content to Section",
    {"file_id": file_id, "prompt": "add content to the Limitations section about cost barriers", "compile_pdf": False},
    expected_min_changes=0  # May be 0 if section not found
)
results["passed" if success else "failed"] += 1
time.sleep(DELAY)

# TEST 7: MODIFY - AI Enhancement
file_id, success = test(
    "MODIFY - Expand Section (AI)",
    {"file_id": file_id, "prompt": "modify the Limitations section to include more technical details", "compile_pdf": False},
    expected_min_changes=0  # May be 0
)
results["passed" if success else "failed"] += 1
time.sleep(DELAY)

# TEST 8: BATCH
print(f"\n{'='*60}")
print(f"TEST: BATCH - Multiple Operations")
print(f"{'='*60}")

batch_payload = {
    "file_id": file_id,
    "queries": [
        "make 'monitoring' italic",
        "add a section 'Conclusion' summarizing key points"
    ],
    "compile_pdf": False
}

start = time.time()
resp = requests.post(f"{BASE_URL}/api/v1/edit/batch-edit-v1", json=batch_payload, timeout=120)
elapsed = time.time() - start

if resp.status_code == 200:
    result = resp.json()
    total_changes = result.get('total_changes', 0)
    print(f"✅ Status: {resp.status_code} | Total Changes: {total_changes} | Time: {elapsed:.1f}s")
    print(f"   Operations: {len(result.get('results', []))}")
    file_id = result.get('final_file_id')
    results["passed"] += 1
else:
    print(f"❌ FAILED: {resp.status_code}")
    results["failed"] += 1

time.sleep(DELAY)

# TEST 9: PDF Compilation
file_id, success = test(
    "PDF COMPILATION",
    {"file_id": file_id, "prompt": "add a section 'References' for citations", "compile_pdf": True},
    expected_min_changes=0
)
if success:
    results["passed"] += 1
else:
    results["failed"] += 1

# SUMMARY
print(f"\n{'='*60}")
print("FINAL RESULTS")
print(f"{'='*60}")
total = results["passed"] + results["failed"]
print(f"Total Tests: {total}")
print(f"✅ Passed: {results['passed']} ({results['passed']/total*100:.0f}%)")
print(f"❌ Failed: {results['failed']}")
print(f"\n📄 Final Document: downloads/{file_id}.tex")
print(f"{'='*60}\n")
