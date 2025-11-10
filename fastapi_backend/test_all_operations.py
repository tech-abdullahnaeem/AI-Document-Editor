#!/usr/bin/env python3
"""
Comprehensive Test Suite for Document Editor API
Tests all operations: FORMAT, REPLACE, MODIFY, REMOVE, ADD
with 10-second delays between operations
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
DELAY_SECONDS = 10

# Test results tracker
test_results = {
    "passed": [],
    "failed": [],
    "total_time": 0
}

def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"{title:^70}")
    print("=" * 70)

def print_separator():
    """Print a separator line"""
    print("-" * 70)

def countdown_delay(seconds: int):
    """Show countdown timer"""
    print(f"\n⏳ Waiting {seconds} seconds before next test...", end="", flush=True)
    for i in range(seconds, 0, -1):
        print(f"\r⏳ Waiting {i} seconds before next test...{' ' * 10}", end="", flush=True)
        time.sleep(1)
    print(f"\r✅ Ready for next test!{' ' * 30}")

def send_request(payload: Dict[str, Any], test_name: str, timeout: int = 90) -> Dict[str, Any]:
    """Send request to the API and track results"""
    try:
        print(f"\n📤 Sending request for: {test_name}")
        print(f"   Prompt: {payload['prompt'][:80]}...")
        
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/edit/edit-doc-v1",
            json=payload,
            timeout=timeout
        )
        elapsed = time.time() - start_time
        
        print(f"📥 Response: {response.status_code} (took {elapsed:.1f}s)")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"   Changes: {result.get('changes', 0)}")
            print(f"   Operation: {result.get('operation')}/{result.get('action')}")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
            print(f"   New File ID: {result.get('file_id')}")
            
            test_results["passed"].append({
                "test": test_name,
                "time": elapsed,
                "changes": result.get('changes', 0)
            })
            
            return result
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            test_results["failed"].append({
                "test": test_name,
                "error": response.text[:200]
            })
            return None
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        test_results["failed"].append({
            "test": test_name,
            "error": str(e)
        })
        return None

def verify_content(file_id: str, section_name: str = None, search_text: str = None) -> bool:
    """Verify content in the generated file"""
    try:
        file_path = f"downloads/{file_id}.tex"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if section_name:
            if section_name in content:
                print(f"   ✓ Section '{section_name}' found in document")
                return True
            else:
                print(f"   ✗ Section '{section_name}' NOT found")
                return False
                
        if search_text:
            if search_text in content:
                print(f"   ✓ Text '{search_text[:50]}...' found")
                return True
            else:
                print(f"   ✗ Text not found")
                return False
                
        return True
    except Exception as e:
        print(f"   ⚠️  Could not verify: {e}")
        return False

def run_all_tests():
    """Run comprehensive tests for all operations"""
    
    print_header("COMPREHENSIVE API TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    print(f"Delay between tests: {DELAY_SECONDS} seconds")
    
    # Initial file ID
    file_id = "3345c6b2-4590-4c3f-9aba-65cb6dcfefd4"
    
    # ==========================================================================
    # TEST 1: REPLACE Operations
    # ==========================================================================
    print_header("TEST 1: REPLACE OPERATIONS")
    
    # Test 1a: Replace words
    payload = {
        "file_id": file_id,
        "prompt": "replace all occurrences of 'glucose' with 'blood glucose'",
        "compile_pdf": False
    }
    result = send_request(payload, "REPLACE - Words")
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 1b: Replace phrases
    payload = {
        "file_id": file_id,
        "prompt": "replace 'continuous monitoring' with 'real-time continuous monitoring'",
        "compile_pdf": False
    }
    result = send_request(payload, "REPLACE - Phrases")
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # ==========================================================================
    # TEST 2: FORMAT Operations
    # ==========================================================================
    print_header("TEST 2: FORMAT OPERATIONS")
    
    # Test 2a: Bold formatting
    payload = {
        "file_id": file_id,
        "prompt": "make 'blood glucose' bold throughout the document",
        "compile_pdf": False
    }
    result = send_request(payload, "FORMAT - Bold")
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 2b: Highlight formatting
    payload = {
        "file_id": file_id,
        "prompt": "highlight 'diabetes' in yellow throughout the document",
        "compile_pdf": False
    }
    result = send_request(payload, "FORMAT - Highlight")
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 2c: Italic formatting
    payload = {
        "file_id": file_id,
        "prompt": "make 'monitoring' italic",
        "compile_pdf": False
    }
    result = send_request(payload, "FORMAT - Italic")
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # ==========================================================================
    # TEST 3: REMOVE Operations
    # ==========================================================================
    print_header("TEST 3: REMOVE OPERATIONS")
    
    # Test 3a: Remove section
    payload = {
        "file_id": file_id,
        "prompt": "remove the acknowledgments section",
        "compile_pdf": False
    }
    result = send_request(payload, "REMOVE - Section")
    if result:
        file_id = result.get('file_id')
        verify_content(file_id, section_name="Acknowledgments")
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 3b: Remove specific text
    payload = {
        "file_id": file_id,
        "prompt": "remove all mentions of 'real-time' from the document",
        "compile_pdf": False
    }
    result = send_request(payload, "REMOVE - Text")
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # ==========================================================================
    # TEST 4: MODIFY Operations (AI-Powered)
    # ==========================================================================
    print_header("TEST 4: MODIFY OPERATIONS (AI-Powered)")
    
    # Test 4a: Modify section to add details
    payload = {
        "file_id": file_id,
        "prompt": "modify the 'Limitations' section to expand on technical challenges",
        "compile_pdf": False
    }
    result = send_request(payload, "MODIFY - Expand Limitations", timeout=120)
    if result:
        file_id = result.get('file_id')
        print(f"   ℹ️  This operation uses AI to enhance content")
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 4b: Modify existing section
    payload = {
        "file_id": file_id,
        "prompt": "modify the abstract to be more concise",
        "compile_pdf": False
    }
    result = send_request(payload, "MODIFY - Simplify Abstract", timeout=120)
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # ==========================================================================
    # TEST 5: ADD Operations (AI-Powered Smart Positioning)
    # ==========================================================================
    print_header("TEST 5: ADD OPERATIONS (AI-Powered)")
    
    # Test 5a: Add section with AI content generation
    payload = {
        "file_id": file_id,
        "prompt": "add a new section titled 'Future Directions' that discusses emerging technologies in glucose monitoring",
        "compile_pdf": False
    }
    result = send_request(payload, "ADD - Section with AI Content", timeout=120)
    if result:
        file_id = result.get('file_id')
        verify_content(file_id, section_name="Future Directions")
        print(f"   ℹ️  AI generated content using Gemini 2.5 Flash")
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 5b: Add another section
    payload = {
        "file_id": file_id,
        "prompt": "create a new section called 'Clinical Implications' about the impact of CGM on patient outcomes",
        "compile_pdf": False
    }
    result = send_request(payload, "ADD - Clinical Implications", timeout=120)
    if result:
        file_id = result.get('file_id')
        verify_content(file_id, section_name="Clinical Implications")
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 5c: Add content to existing section  
    payload = {
        "file_id": file_id,
        "prompt": "add content to the Limitations section about sensor calibration requirements",
        "compile_pdf": False
    }
    result = send_request(payload, "ADD - Content to Limitations", timeout=120)
    if result:
        file_id = result.get('file_id')
    
    countdown_delay(DELAY_SECONDS)
    
    # Test 5d: Add section with ethical considerations
    payload = {
        "file_id": file_id,
        "prompt": "add a section 'Ethical Considerations' discussing privacy concerns, data security, and algorithmic bias in AI-powered medical devices",
        "compile_pdf": False
    }
    result = send_request(payload, "ADD - Ethical Considerations")
    if result:
        file_id = result.get('file_id')
        verify_content(file_id, section_name="Ethical Considerations")
    
    countdown_delay(DELAY_SECONDS)
    
    # ==========================================================================
    # TEST 6: BATCH OPERATIONS
    # ==========================================================================
    print_header("TEST 6: BATCH OPERATIONS")
    
    batch_payload = {
        "file_id": file_id,
        "queries": [  # Fixed: should be 'queries' not 'prompts'
            "replace 'CGM' with 'Continuous Glucose Monitoring (CGM)' in the first occurrence",
            "make 'artificial intelligence' bold throughout the document",
            "add a section 'Clinical Applications' discussing hospital use of CGM systems"
        ],
        "compile_pdf": False
    }
    
    print(f"\n📤 Sending BATCH request with {len(batch_payload['queries'])} operations")
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/edit/batch-edit-v1",
            json=batch_payload,
            timeout=120
        )
        elapsed = time.time() - start_time
        
        print(f"📥 Response: {response.status_code} (took {elapsed:.1f}s)")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Batch Success!")
            print(f"   Total Changes: {result.get('total_changes', 0)}")
            print(f"   Operations: {len(result.get('results', []))}")
            print(f"   Processing Time: {result.get('total_processing_time', 0):.2f}s")
            print(f"   Final File ID: {result.get('final_file_id')}")
            
            # Show individual results
            for i, op_result in enumerate(result.get('results', []), 1):
                print(f"\n   Operation {i}:")
                print(f"     Changes: {op_result.get('changes', 0)}")
                print(f"     Type: {op_result.get('operation')}/{op_result.get('action')}")
            
            test_results["passed"].append({
                "test": "BATCH - Multiple Operations",
                "time": elapsed,
                "changes": result.get('total_changes', 0)
            })
            
            file_id = result.get('final_file_id')
        else:
            print(f"❌ Batch Failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            test_results["failed"].append({
                "test": "BATCH - Multiple Operations",
                "error": response.text[:200]
            })
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        test_results["failed"].append({
            "test": "BATCH - Multiple Operations",
            "error": str(e)
        })
    
    countdown_delay(DELAY_SECONDS)
    
    # ==========================================================================
    # TEST 7: PDF COMPILATION
    # ==========================================================================
    print_header("TEST 7: PDF COMPILATION")
    
    payload = {
        "file_id": file_id,
        "prompt": "add a section 'Conclusion' summarizing the key findings about continuous glucose monitoring",
        "compile_pdf": True  # Enable PDF compilation
    }
    result = send_request(payload, "ADD with PDF Compilation", timeout=120)
    if result:
        file_id = result.get('file_id')
        pdf_id = result.get('pdf_id')
        if pdf_id:
            print(f"   📄 PDF Generated: {pdf_id}")
            print(f"   ✅ PDF compilation successful!")
        else:
            print(f"   ⚠️  No PDF generated (might have failed)")
    
    # ==========================================================================
    # FINAL SUMMARY
    # ==========================================================================
    print_header("TEST SUMMARY")
    
    total_tests = len(test_results["passed"]) + len(test_results["failed"])
    pass_rate = (len(test_results["passed"]) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {len(test_results['passed'])} ({pass_rate:.1f}%)")
    print(f"   ❌ Failed: {len(test_results['failed'])}")
    
    if test_results["passed"]:
        print(f"\n✅ Passed Tests:")
        for test in test_results["passed"]:
            print(f"   • {test['test']}: {test['changes']} changes in {test['time']:.1f}s")
    
    if test_results["failed"]:
        print(f"\n❌ Failed Tests:")
        for test in test_results["failed"]:
            print(f"   • {test['test']}: {test['error'][:100]}...")
    
    print(f"\n📝 Final Document ID: {file_id}")
    print(f"   Location: downloads/{file_id}.tex")
    
    # Show all sections in final document
    try:
        with open(f"downloads/{file_id}.tex", 'r') as f:
            content = f.read()
        sections = re.findall(r'\\section\{([^}]+)\}', content)
        if sections:
            print(f"\n📚 Sections in Final Document ({len(sections)}):")
            for i, section in enumerate(sections, 1):
                print(f"   {i}. {section}")
    except Exception as e:
        print(f"   ⚠️  Could not list sections: {e}")
    
    print(f"\n🏁 Test suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test suite interrupted by user")
        print(f"Completed {len(test_results['passed'])} tests before interruption")
    except Exception as e:
        print(f"\n\n❌ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
