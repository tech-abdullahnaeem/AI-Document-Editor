import requests
import time
import json

BASE_URL = "http://localhost:8000"
DELAY = 10  # seconds between tests

def print_section_line(char="="):
    print(char * 80)

def test_add_section(test_num, description, payload, expected_position=None):
    """Test adding a section with specific positioning"""
    print_section_line()
    print(f"\nTEST {test_num}: {description}")
    print_section_line("-")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/edit/edit-doc-v1",
            json=payload,
            timeout=120
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ SUCCESS")
            print(f"   Status: {result.get('success', 'N/A')}")
            print(f"   Operation: {result.get('operation', 'N/A')}")
            print(f"   Action: {result.get('action', 'N/A')}")
            print(f"   Changes: {result.get('changes', 0)}")
            print(f"   Processing Time: {elapsed:.2f}s")
            print(f"   New File ID: {result.get('file_id', 'N/A')}")
            
            # Get the document content to verify section positioning
            if result.get('file_id'):
                doc_id = result['file_id']
                
                # Read the document to check section order
                try:
                    with open(f"downloads/{doc_id}.tex", 'r') as f:
                        content = f.read()
                        
                    # Extract section names in order
                    sections = []
                    for line in content.split('\n'):
                        if line.strip().startswith('\\section'):
                            # Extract section name
                            section_name = line.split('{')[1].split('}')[0] if '{' in line else ''
                            sections.append(section_name)
                    
                    print(f"\n   📋 DOCUMENT SECTIONS (in order):")
                    for idx, section in enumerate(sections, 1):
                        # Extract section name from prompt for comparison
                        prompt_lower = payload.get('prompt', '').lower()
                        section_lower = section.lower()
                        marker = "  👉" if any(word in section_lower for word in ['discussion', 'data availability', 'abstract extension', 'quality assessment', 'appendix', 'error handling']) else "    "
                        print(f"   {marker} {idx}. {section}")
                    
                    # Verify expected position
                    if expected_position:
                        print(f"\n   🎯 EXPECTED POSITION: {expected_position}")
                    
                except Exception as e:
                    print(f"   ⚠️  Could not read document: {str(e)}")
            
            return result
        else:
            print(f"❌ FAILED")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ ERROR after {elapsed:.2f}s")
        print(f"   {str(e)}")
        return None

def main():
    print("\n" + "=" * 80)
    print("SECTION POSITIONING TEST SUITE")
    print("Testing 'before' and 'after' section placement")
    print("=" * 80)
    
    # Start with a fresh document
    initial_doc = "3345c6b2-4590-4c3f-9aba-65cb6dcfefd4"
    current_doc = initial_doc
    
    print(f"\nStarting Document: {initial_doc}")
    print(f"Delay between tests: {DELAY} seconds\n")
    
    # TEST 1: Add section BEFORE "Limitations"
    time.sleep(DELAY)
    test1_payload = {
        "file_id": current_doc,
        "prompt": "Add a new section called 'Discussion' before the Limitations section. Write a discussion about the implications of the glucose monitoring benchmarks presented in this paper, including comparisons with previous work and future research directions."
    }
    
    result1 = test_add_section(
        1, 
        "ADD SECTION 'Discussion' BEFORE 'Limitations'",
        test1_payload,
        expected_position="before Limitations"
    )
    
    if result1 and result1.get('file_id'):
        current_doc = result1['file_id']
    
    # TEST 2: Add section AFTER "Acknowledgments"
    time.sleep(DELAY)
    test2_payload = {
        "file_id": current_doc,
        "prompt": "Add a new section called 'Data Availability' after the Acknowledgments section. Write a data availability statement describing where readers can access the datasets and code mentioned in this paper."
    }
    
    result2 = test_add_section(
        2,
        "ADD SECTION 'Data Availability' AFTER 'Acknowledgments'",
        test2_payload,
        expected_position="after Acknowledgments"
    )
    
    if result2 and result2.get('file_id'):
        current_doc = result2['file_id']
    
    # TEST 3: Add section BEFORE first section (numbered section "1 Introduction")
    time.sleep(DELAY)
    test3_payload = {
        "file_id": current_doc,
        "prompt": "Add a new section called 'Abstract Extension' before the Introduction section. This extended abstract provides additional context about the comprehensive nature of this glucose monitoring benchmark study."
    }
    
    result3 = test_add_section(
        3,
        "ADD SECTION 'Abstract Extension' BEFORE '1 Introduction'",
        test3_payload,
        expected_position="before 1 Introduction"
    )
    
    if result3 and result3.get('file_id'):
        current_doc = result3['file_id']
    
    # TEST 4: Add section AFTER a middle section ("3 Data")
    time.sleep(DELAY)
    test4_payload = {
        "file_id": current_doc,
        "prompt": "Add a new section called 'Data Quality Assessment' after the Data section. Write about the quality assessment metrics used to validate the CGM datasets, including criteria for data inclusion and exclusion."
    }
    
    result4 = test_add_section(
        4,
        "ADD SECTION 'Data Quality Assessment' AFTER '3 Data'",
        test4_payload,
        expected_position="after 3 Data"
    )
    
    if result4 and result4.get('file_id'):
        current_doc = result4['file_id']
    
    # TEST 5: Add section at the END (default behavior when no position specified)
    time.sleep(DELAY)
    test5_payload = {
        "file_id": current_doc,
        "prompt": "Add a new section called 'Appendix' at the end of the document. Content: Supplementary Materials - Additional tables and figures are available in the supplementary materials."
    }
    
    result5 = test_add_section(
        5,
        "ADD SECTION 'Appendix' at END (no position specified)",
        test5_payload,
        expected_position="at end"
    )
    
    if result5 and result5.get('file_id'):
        current_doc = result5['file_id']
    
    # TEST 6: Add section BEFORE non-existent section (should fall back to end)
    time.sleep(DELAY)
    test6_payload = {
        "file_id": current_doc,
        "prompt": "Add a new section called 'Error Handling Test' before the 'Non-Existent Section'. Content: This tests what happens when the reference section doesn't exist. Should add at end."
    }
    
    result6 = test_add_section(
        6,
        "ADD SECTION with BEFORE non-existent section (fallback test)",
        test6_payload,
        expected_position="at end (fallback)"
    )
    
    if result6 and result6.get('file_id'):
        current_doc = result6['file_id']
    
    # Summary
    print_section_line("=")
    print("\n📊 TEST SUITE SUMMARY")
    print_section_line("=")
    
    results = [result1, result2, result3, result4, result5, result6]
    successful = sum(1 for r in results if r and r.get('success') == True)
    
    print(f"\nTests Run: 6")
    print(f"Successful: {successful}")
    print(f"Failed: {6 - successful}")
    print(f"Success Rate: {(successful/6)*100:.1f}%")
    print(f"\nInitial Document: {initial_doc}")
    print(f"Final Document: {current_doc}")
    
    print_section_line("=")

if __name__ == "__main__":
    main()
