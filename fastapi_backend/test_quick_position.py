"""
Quick test for before/after section positioning
Tests 3 scenarios with minimal delay
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1/edit"

def test(prompt, name):
    print(f"\n{'='*70}\n{name}\n{'='*70}")
    start = time.time()
    r = requests.post(f"{BASE_URL}/edit-doc-v1", 
                     json={"file_id": "3345c6b2-4590-4c3f-9aba-65cb6dcfefd4", "prompt": prompt}, 
                     timeout=90)
    elapsed = time.time() - start
    
    if r.status_code == 200:
        result = r.json()
        print(f"✅ {name} - {result.get('changes')} changes ({elapsed:.1f}s)")
        print(f"   {result.get('operation')}/{result.get('action')}")
        if 'parsed_query' in result and result['parsed_query'].get('position'):
            print(f"   Position: {result['parsed_query'].get('position')}")
        return True
    else:
        print(f"❌ {name} - FAILED ({elapsed:.1f}s)")
        return False

print("\n🧪 QUICK SECTION POSITIONING TEST")
print("="*70)

results = []
results.append(test("Add section 'Methods' before Introduction", "Test 1: BEFORE"))
time.sleep(3)
results.append(test("Add section 'Conclusions' after Acknowledgments", "Test 2: AFTER"))
time.sleep(3)
results.append(test("Add section 'Appendix' at the end", "Test 3: END"))

print(f"\n{'='*70}")
print(f"RESULTS: {sum(results)}/3 passed ({sum(results)/3*100:.0f}%)")
print(f"{'='*70}\n")
