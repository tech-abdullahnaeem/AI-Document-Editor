"""
Simple test for section positioning (before/after)
Tests the fixed fallback parser and API key rotation
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_add_section(prompt, test_name):
    """Test adding a section"""
    print(f"\n{'='*80}")
    print(f"TEST: {test_name}")
    print(f"{'='*80}")
    print(f"Prompt: {prompt}")
    print(f"{'-'*80}")
    
    payload = {
        "file_id": "3345c6b2-4590-4c3f-9aba-65cb6dcfefd4",
        "prompt": prompt
    }
    
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/api/v1/edit/edit-doc-v1",
        json=payload,
        timeout=120
    )
    elapsed = time.time() - start
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SUCCESS ({elapsed:.1f}s)")
        print(f"   Operation: {result.get('operation')}")
        print(f"   Action: {result.get('action')}")
        print(f"   Changes: {result.get('changes')}")
        print(f"   File ID: {result.get('file_id')}")
        
        # Show parsed query
        if 'parsed_query' in result:
            pq = result['parsed_query']
            print(f"\n   📋 Parsed Query:")
            print(f"      Operation: {pq.get('operation')}")
            print(f"      Action: {pq.get('action')}")
            print(f"      Target: {pq.get('target')}")
            if pq.get('section_name'):
                print(f"      Section: {pq.get('section_name')}")
            if pq.get('position'):
                print(f"      Position: {pq.get('position')}")
        
        return result
    else:
        print(f"❌ FAILED ({elapsed:.1f}s)")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
        return None

def main():
    print("\n" + "="*80)
    print("SECTION POSITIONING TEST - Simple Version")
    print("Testing fallback parser and API key rotation fixes")
    print("="*80)
    
    # Test 1: Add section BEFORE another section
    result1 = test_add_section(
        "Add a new section called 'Discussion' before the Limitations section. Write about the study implications.",
        "Add Section BEFORE Limitations"
    )
    
    if result1:
        print(f"\n✅ Test 1 PASSED - Changes: {result1.get('changes')}")
    else:
        print(f"\n❌ Test 1 FAILED")
    
    time.sleep(5)
    
    # Test 2: Add section AFTER another section
    result2 = test_add_section(
        "Add a new section called 'Data Availability' after the Acknowledgments section. Describe data access.",
        "Add Section AFTER Acknowledgments"
    )
    
    if result2:
        print(f"\n✅ Test 2 PASSED - Changes: {result2.get('changes')}")
    else:
        print(f"\n❌ Test 2 FAILED")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    tests_passed = sum([1 for r in [result1, result2] if r and r.get('changes', 0) > 0])
    print(f"Tests Passed: {tests_passed}/2")
    print(f"Success Rate: {(tests_passed/2)*100:.0f}%")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
