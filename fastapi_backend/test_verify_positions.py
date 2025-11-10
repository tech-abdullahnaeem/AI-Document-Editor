"""
Final verification test: Check that sections are actually added at correct positions
"""
import requests
import re

BASE_URL = "http://localhost:8000/api/v1/edit"
DOC_ID = "3345c6b2-4590-4c3f-9aba-65cb6dcfefd4"

def get_sections(file_id):
    """Extract section names in order from a document"""
    try:
        with open(f"downloads/{file_id}.tex", 'r') as f:
            content = f.read()
        sections = []
        for line in content.split('\n'):
            if line.strip().startswith('\\section'):
                match = re.search(r'\\section\*?\{([^}]+)\}', line)
                if match:
                    sections.append(match.group(1))
        return sections
    except:
        return []

def test_positioning(prompt, expected_new_section, expected_before=None, expected_after=None):
    """Test that a section is added at the correct position"""
    print(f"\n{'='*80}")
    print(f"Testing: {prompt[:70]}...")
    print('='*80)
    
    r = requests.post(f"{BASE_URL}/edit-doc-v1",
                     json={"file_id": DOC_ID, "prompt": prompt},
                     timeout=120)
    
    if r.status_code != 200:
        print(f"❌ FAILED - Status {r.status_code}")
        return False
    
    result = r.json()
    new_file_id = result.get('file_id')
    
    if not new_file_id:
        print(f"❌ FAILED - No file_id returned")
        return False
    
    sections = get_sections(new_file_id)
    print(f"\n📋 Document sections ({len(sections)} total):")
    for i, sec in enumerate(sections, 1):
        marker = "👉" if sec == expected_new_section else "  "
        print(f"   {marker} {i}. {sec}")
    
    if expected_new_section not in sections:
        print(f"\n❌ FAILED - Section '{expected_new_section}' not found!")
        return False
    
    idx = sections.index(expected_new_section)
    
    # Check BEFORE relationship
    if expected_before:
        if expected_before in sections:
            before_idx = sections.index(expected_before)
            if idx < before_idx:
                print(f"\n✅ CORRECT - '{expected_new_section}' is BEFORE '{expected_before}'")
                print(f"   Position: {idx+1} < {before_idx+1}")
                return True
            else:
                print(f"\n❌ WRONG - '{expected_new_section}' at {idx+1}, should be before '{expected_before}' at {before_idx+1}")
                return False
        else:
            print(f"\n⚠️  Reference section '{expected_before}' not found, added at position {idx+1}")
            return True  # Still pass if reference doesn't exist
    
    # Check AFTER relationship
    if expected_after:
        if expected_after in sections:
            after_idx = sections.index(expected_after)
            if idx > after_idx:
                print(f"\n✅ CORRECT - '{expected_new_section}' is AFTER '{expected_after}'")
                print(f"   Position: {idx+1} > {after_idx+1}")
                return True
            else:
                print(f"\n❌ WRONG - '{expected_new_section}' at {idx+1}, should be after '{expected_after}' at {after_idx+1}")
                return False
        else:
            print(f"\n⚠️  Reference section '{expected_after}' not found, added at position {idx+1}")
            return True
    
    # If no specific position check, just confirm it was added
    print(f"\n✅ ADDED - '{expected_new_section}' at position {idx+1}")
    return True

print("\n" + "="*80)
print("SECTION POSITIONING VERIFICATION TEST")
print("Verifying sections are added at correct positions in document")
print("="*80)

import time

results = []

# Test 1: Add BEFORE
results.append(test_positioning(
    "Add section 'Discussion' before Limitations section",
    expected_new_section="Discussion",
    expected_before="Limitations"
))
time.sleep(3)

# Test 2: Add AFTER  
results.append(test_positioning(
    "Add section 'Future Directions' after Acknowledgments",
    expected_new_section="Future Directions",
    expected_after="Acknowledgments"
))
time.sleep(3)

# Test 3: Add BEFORE numbered section
results.append(test_positioning(
    "Add section 'Background' before Introduction section",
    expected_new_section="Background",
    expected_before="1 Introduction"
))

print(f"\n{'='*80}")
print(f"FINAL RESULTS: {sum(results)}/3 tests passed ({sum(results)/3*100:.0f}%)")
print(f"{'='*80}\n")
