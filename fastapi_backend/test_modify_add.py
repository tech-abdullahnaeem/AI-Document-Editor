#!/usr/bin/env python3
"""
Focused Test: MODIFY, ADD Sentence, ADD Section
"""

import requests
import time

BASE_URL = "http://localhost:8000"
DELAY = 10

print("=" * 70)
print("FOCUSED TEST: MODIFY, ADD SENTENCE, ADD SECTION")
print("=" * 70)

file_id = "3345c6b2-4590-4c3f-9aba-65cb6dcfefd4"

# ==========================================================================
# TEST 1: ADD SECTION with AI Content
# ==========================================================================
print(f"\n{'='*70}")
print("TEST 1: ADD SECTION - 'Future Directions' (AI Generated)")
print(f"{'='*70}")

payload = {
    "file_id": file_id,
    "prompt": "create a new section titled 'Future Directions' discussing emerging technologies in continuous glucose monitoring",
    "compile_pdf": False
}

print(f"📤 Prompt: {payload['prompt']}")
print(f"⏳ Sending request...")

start = time.time()
response = requests.post(f"{BASE_URL}/api/v1/edit/edit-doc-v1", json=payload, timeout=120)
elapsed = time.time() - start

print(f"\n📥 Response Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ SUCCESS")
    print(f"   Changes: {result.get('changes')}")
    print(f"   Operation: {result.get('operation')}/{result.get('action')}")
    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
    print(f"   Request Time: {elapsed:.2f}s")
    print(f"   New File ID: {result.get('file_id')}")
    
    file_id = result.get('file_id')
    
    # Verify content
    try:
        with open(f"downloads/{file_id}.tex", 'r') as f:
            content = f.read()
        if "Future Directions" in content:
            print(f"   ✓ Section 'Future Directions' found in document")
            # Find section content
            import re
            match = re.search(r'\\section\{Future Directions\}(.*?)(?=\\section|\\end{document})', 
                             content, re.DOTALL)
            if match:
                section_content = match.group(1).strip()
                print(f"   ✓ Section has {len(section_content)} characters")
                if len(section_content) > 500:
                    print(f"   🤖 AI-generated content confirmed!")
                    print(f"\n   Preview:")
                    print(f"   {section_content[:200]}...")
        else:
            print(f"   ✗ Section NOT found")
    except Exception as e:
        print(f"   ⚠️ Could not verify: {e}")
else:
    print(f"❌ FAILED: {response.text[:200]}")

print(f"\n⏳ Waiting {DELAY} seconds...")
time.sleep(DELAY)

# ==========================================================================
# TEST 2: ADD SENTENCE to Section
# ==========================================================================
print(f"\n{'='*70}")
print("TEST 2: ADD SENTENCE to Limitations Section")
print(f"{'='*70}")

payload = {
    "file_id": file_id,
    "prompt": "add a sentence to the Limitations section about sensor accuracy challenges",
    "compile_pdf": False
}

print(f"📤 Prompt: {payload['prompt']}")
print(f"⏳ Sending request...")

start = time.time()
response = requests.post(f"{BASE_URL}/api/v1/edit/edit-doc-v1", json=payload, timeout=120)
elapsed = time.time() - start

print(f"\n📥 Response Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ SUCCESS")
    print(f"   Changes: {result.get('changes')}")
    print(f"   Operation: {result.get('operation')}/{result.get('action')}")
    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
    print(f"   Request Time: {elapsed:.2f}s")
    print(f"   New File ID: {result.get('file_id')}")
    
    file_id = result.get('file_id')
else:
    print(f"❌ FAILED: {response.text[:200]}")

print(f"\n⏳ Waiting {DELAY} seconds...")
time.sleep(DELAY)

# ==========================================================================
# TEST 3: ADD CONTENT (Paragraph) to Section
# ==========================================================================
print(f"\n{'='*70}")
print("TEST 3: ADD PARAGRAPH to Limitations Section")
print(f"{'='*70}")

payload = {
    "file_id": file_id,
    "prompt": "add a paragraph to the Limitations section discussing cost barriers and accessibility issues",
    "compile_pdf": False
}

print(f"📤 Prompt: {payload['prompt']}")
print(f"⏳ Sending request...")

start = time.time()
response = requests.post(f"{BASE_URL}/api/v1/edit/edit-doc-v1", json=payload, timeout=120)
elapsed = time.time() - start

print(f"\n📥 Response Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ SUCCESS")
    print(f"   Changes: {result.get('changes')}")
    print(f"   Operation: {result.get('operation')}/{result.get('action')}")
    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
    print(f"   Request Time: {elapsed:.2f}s")
    print(f"   New File ID: {result.get('file_id')}")
    
    file_id = result.get('file_id')
else:
    print(f"❌ FAILED: {response.text[:200]}")

print(f"\n⏳ Waiting {DELAY} seconds...")
time.sleep(DELAY)

# ==========================================================================
# TEST 4: MODIFY SECTION (AI Enhancement)
# ==========================================================================
print(f"\n{'='*70}")
print("TEST 4: MODIFY SECTION - Expand Limitations (AI)")
print(f"{'='*70}")

payload = {
    "file_id": file_id,
    "prompt": "modify the Limitations section to include more technical details about sensor drift and calibration requirements",
    "compile_pdf": False
}

print(f"📤 Prompt: {payload['prompt']}")
print(f"⏳ Sending request (AI processing may take 20-40 seconds)...")

start = time.time()
response = requests.post(f"{BASE_URL}/api/v1/edit/edit-doc-v1", json=payload, timeout=120)
elapsed = time.time() - start

print(f"\n📥 Response Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ SUCCESS")
    print(f"   Changes: {result.get('changes')}")
    print(f"   Operation: {result.get('operation')}/{result.get('action')}")
    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
    print(f"   Request Time: {elapsed:.2f}s")
    print(f"   New File ID: {result.get('file_id')}")
    print(f"   🤖 AI-powered modification using Gemini 2.5 Flash")
    
    file_id = result.get('file_id')
else:
    print(f"❌ FAILED: {response.text[:200]}")

print(f"\n⏳ Waiting {DELAY} seconds...")
time.sleep(DELAY)

# ==========================================================================
# TEST 5: ADD ANOTHER SECTION
# ==========================================================================
print(f"\n{'='*70}")
print("TEST 5: ADD SECTION - 'Clinical Applications'")
print(f"{'='*70}")

payload = {
    "file_id": file_id,
    "prompt": "create a new section called 'Clinical Applications' about using CGM in hospital settings",
    "compile_pdf": False
}

print(f"📤 Prompt: {payload['prompt']}")
print(f"⏳ Sending request...")

start = time.time()
response = requests.post(f"{BASE_URL}/api/v1/edit/edit-doc-v1", json=payload, timeout=120)
elapsed = time.time() - start

print(f"\n📥 Response Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"✅ SUCCESS")
    print(f"   Changes: {result.get('changes')}")
    print(f"   Operation: {result.get('operation')}/{result.get('action')}")
    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
    print(f"   Request Time: {elapsed:.2f}s")
    print(f"   New File ID: {result.get('file_id')}")
    
    file_id = result.get('file_id')
    
    # Verify content
    try:
        with open(f"downloads/{file_id}.tex", 'r') as f:
            content = f.read()
        if "Clinical Applications" in content:
            print(f"   ✓ Section 'Clinical Applications' found")
    except:
        pass
else:
    print(f"❌ FAILED: {response.text[:200]}")

# ==========================================================================
# FINAL SUMMARY
# ==========================================================================
print(f"\n{'='*70}")
print("TEST SUMMARY")
print(f"{'='*70}")
print(f"\n✅ All tests completed!")
print(f"📄 Final Document: downloads/{file_id}.tex")

# Show sections in final document
try:
    import re
    with open(f"downloads/{file_id}.tex", 'r') as f:
        content = f.read()
    sections = re.findall(r'\\section\{([^}]+)\}', content)
    print(f"\n📚 Sections in Final Document ({len(sections)}):")
    for i, section in enumerate(sections, 1):
        print(f"   {i}. {section}")
except Exception as e:
    print(f"   ⚠️ Could not list sections: {e}")

print(f"\n{'='*70}\n")
