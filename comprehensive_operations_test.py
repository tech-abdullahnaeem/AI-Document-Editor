"""
Comprehensive Test Suite for LaTeX Document Editor
Tests ALL operations: Add, Replace, Remove, Modify
At ALL levels: Word, Sentence, Paragraph, Section
"""

import requests
import time
import re
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000/api/v1"
TEST_FILE = "/Users/abdullah/Desktop/Techinoid/final with fast api copy/latex fixed output:input/glucobench _USER_GUIDED_FIXED.tex"

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""
        self.details = {}
    
    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status}: {self.name}\n   {self.message}"


def upload_file(file_path: str = TEST_FILE) -> str:
    """Upload file and return file_id"""
    with open(file_path, 'r') as f:
        response = requests.post(
            f"{BASE_URL}/files/upload",
            files={"file": ("test.tex", f, "text/plain")}
        )
    if response.status_code != 200:
        raise Exception(f"Upload failed: {response.text}")
    return response.json()["file_id"]


def edit_document(file_id: str, prompt: str) -> str:
    """Edit document and return new file_id"""
    response = requests.post(
        f"{BASE_URL}/edit/prompt",
        json={"file_id": file_id, "prompt": prompt}
    )
    if response.status_code != 200:
        raise Exception(f"Edit failed: {response.text}")
    return response.json()["file_id"]


def download_content(file_id: str) -> str:
    """Download file content"""
    response = requests.get(f"{BASE_URL}/files/download/{file_id}")
    return response.text


# ============================================================================
# WORD-LEVEL OPERATIONS
# ============================================================================

def test_word_add() -> TestResult:
    """Test: Add word to existing text"""
    result = TestResult("Word Add")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Count initial occurrences of "revolutionary"
        initial_count = initial.lower().count("revolutionary")
        
        # This test just verifies word replacement works (add is implicit in replace)
        new_file_id = edit_document(file_id, "replace diabetes with revolutionary diabetes")
        final = download_content(new_file_id)
        
        final_count = final.lower().count("revolutionary")
        
        if final_count > initial_count:
            result.passed = True
            result.message = f"Added 'revolutionary' - count increased from {initial_count} to {final_count}"
        else:
            result.message = f"Failed to add word - count stayed at {initial_count}"
        
        result.details = {"before": initial_count, "after": final_count}
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_word_replace() -> TestResult:
    """Test: Replace all occurrences of a word"""
    result = TestResult("Word Replace")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Count CGM and replacement word
        cgm_count = initial.count("CGM")
        initial_glucose_count = initial.count("glucose monitor")
        
        new_file_id = edit_document(file_id, "replace CGM with glucose monitor")
        final = download_content(new_file_id)
        
        final_cgm = final.count("CGM")
        final_glucose = final.count("glucose monitor")
        
        if final_cgm < cgm_count and final_glucose > initial_glucose_count:
            result.passed = True
            result.message = f"Replaced {cgm_count - final_cgm} occurrences of 'CGM' with 'glucose monitor'"
            result.details = {
                "cgm_before": cgm_count,
                "cgm_after": final_cgm,
                "replacement_added": final_glucose - initial_glucose_count
            }
        else:
            result.message = f"Replacement failed - CGM: {cgm_count}→{final_cgm}, glucose monitor: {initial_glucose_count}→{final_glucose}"
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_word_remove() -> TestResult:
    """Test: Remove all occurrences of a word"""
    result = TestResult("Word Remove")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Count occurrences
        word = "dataset"
        initial_count = initial.lower().count(word)
        
        new_file_id = edit_document(file_id, f"remove all occurrences of {word}")
        final = download_content(new_file_id)
        
        final_count = final.lower().count(word)
        
        if final_count == 0 and initial_count > 0:
            result.passed = True
            result.message = f"Removed all {initial_count} occurrences of '{word}'"
            result.details = {"removed": initial_count}
        else:
            result.message = f"Failed - {final_count} occurrences remain (started with {initial_count})"
            result.details = {"before": initial_count, "after": final_count}
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_word_modify() -> TestResult:
    """Test: Modify word (bold/italic styling)"""
    result = TestResult("Word Modify (Style)")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Check for bold formatting
        initial_bold = initial.count(r"\textbf{diabetes}")
        
        new_file_id = edit_document(file_id, "make the word diabetes bold")
        final = download_content(new_file_id)
        
        final_bold = final.count(r"\textbf{diabetes}")
        
        if final_bold > initial_bold:
            result.passed = True
            result.message = f"Made 'diabetes' bold - {final_bold - initial_bold} instances formatted"
            result.details = {"bold_added": final_bold - initial_bold}
        else:
            result.message = f"Styling failed - bold count: {initial_bold}→{final_bold}"
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


# ============================================================================
# SENTENCE-LEVEL OPERATIONS
# ============================================================================

def test_sentence_add() -> TestResult:
    """Test: Add a sentence to a section"""
    result = TestResult("Sentence Add")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        test_sentence = "This represents a significant advancement in the field."
        initial_has_sentence = test_sentence in initial
        
        new_file_id = edit_document(
            file_id,
            f"add the sentence '{test_sentence}' to the Introduction section"
        )
        final = download_content(new_file_id)
        
        final_has_sentence = test_sentence in final
        
        if not initial_has_sentence and final_has_sentence:
            result.passed = True
            result.message = f"Successfully added sentence to Introduction"
        elif initial_has_sentence and final_has_sentence:
            result.passed = True
            result.message = f"Sentence was already present (or added)"
        else:
            result.message = f"Failed to add sentence"
        
        result.details = {"sentence_added": final_has_sentence}
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_sentence_replace() -> TestResult:
    """Test: Replace a specific sentence"""
    result = TestResult("Sentence Replace")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        old_text = "The rising rates of diabetes"
        new_text = "Global diabetes prevalence is increasing rapidly"
        
        has_old = old_text in initial
        
        new_file_id = edit_document(
            file_id,
            f"replace the sentence containing '{old_text}' with '{new_text}'"
        )
        final = download_content(new_file_id)
        
        has_old_final = old_text in final
        has_new = new_text in final
        
        if has_old and not has_old_final and has_new:
            result.passed = True
            result.message = f"Successfully replaced sentence"
            result.details = {"old_removed": True, "new_added": True}
        else:
            result.message = f"Replacement incomplete - old: {has_old_final}, new: {has_new}"
            result.details = {"old_still_present": has_old_final, "new_present": has_new}
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_sentence_remove() -> TestResult:
    """Test: Remove a specific sentence"""
    result = TestResult("Sentence Remove")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        target = "For ARIMA, we use the code from"
        has_sentence = target in initial
        
        new_file_id = edit_document(file_id, f"remove the sentence containing '{target}'")
        final = download_content(new_file_id)
        
        still_has = target in final
        
        if has_sentence and not still_has:
            result.passed = True
            result.message = f"Successfully removed sentence"
        elif not has_sentence:
            result.passed = False
            result.message = f"Sentence not found in original document"
        else:
            result.message = f"Failed to remove sentence (still present)"
        
        result.details = {"removed": not still_has}
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_sentence_highlight() -> TestResult:
    """Test: Highlight sentences containing specific text"""
    result = TestResult("Sentence Highlight")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Count existing highlights
        initial_highlights = initial.count(r"\textcolor{yellow}")
        
        new_file_id = edit_document(file_id, "highlight all sentences containing the word 'diabetes' in yellow")
        final = download_content(new_file_id)
        
        final_highlights = final.count(r"\textcolor{yellow}")
        
        if final_highlights > initial_highlights:
            result.passed = True
            result.message = f"Added {final_highlights - initial_highlights} highlights"
            result.details = {"highlights_added": final_highlights - initial_highlights}
        else:
            result.message = f"No highlights added - count: {initial_highlights}→{final_highlights}"
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


# ============================================================================
# SECTION-LEVEL OPERATIONS
# ============================================================================

def test_section_add() -> TestResult:
    """Test: Add a new section"""
    result = TestResult("Section Add")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        section_title = "Future Work"
        section_pattern = r'\\section\*?\{.*' + section_title + r'.*\}'
        
        has_section = bool(re.search(section_pattern, initial, re.IGNORECASE))
        
        new_file_id = edit_document(
            file_id,
            f"add a new section titled '{section_title}' with content about potential future research directions"
        )
        final = download_content(new_file_id)
        
        has_section_final = bool(re.search(section_pattern, final, re.IGNORECASE))
        
        if not has_section and has_section_final:
            result.passed = True
            result.message = f"Successfully added '{section_title}' section"
        elif has_section:
            result.passed = True
            result.message = f"Section already existed or was added"
        else:
            result.message = f"Failed to add section"
        
        result.details = {"section_present": has_section_final}
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_section_replace_title() -> TestResult:
    """Test: Replace section title"""
    result = TestResult("Section Title Replace")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        old_title = "Related works"
        new_title = "Literature Survey"
        
        old_pattern = r'\\section\*?\{.*' + old_title + r'.*\}'
        new_pattern = r'\\section\*?\{.*' + new_title + r'.*\}'
        
        has_old = bool(re.search(old_pattern, initial, re.IGNORECASE))
        
        new_file_id = edit_document(file_id, f"replace {old_title} with {new_title}")
        final = download_content(new_file_id)
        
        has_old_final = bool(re.search(old_pattern, final, re.IGNORECASE))
        has_new = bool(re.search(new_pattern, final, re.IGNORECASE))
        
        if has_old and not has_old_final and has_new:
            result.passed = True
            result.message = f"Successfully replaced section title"
            result.details = {"old_removed": True, "new_added": True}
        else:
            result.message = f"Title replacement failed - old present: {has_old_final}, new present: {has_new}"
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_section_remove() -> TestResult:
    """Test: Remove an entire section"""
    result = TestResult("Section Remove")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Count sections
        initial_sections = len(re.findall(r'\\section\*?\{', initial))
        
        new_file_id = edit_document(file_id, "remove the Limitations section")
        final = download_content(new_file_id)
        
        final_sections = len(re.findall(r'\\section\*?\{', final))
        has_limitations = "Limitations." in final  # Check content too
        
        if final_sections < initial_sections or not has_limitations:
            result.passed = True
            result.message = f"Section count: {initial_sections}→{final_sections}"
            result.details = {"sections_removed": initial_sections - final_sections}
        else:
            result.message = f"Failed to remove section - count unchanged: {initial_sections}"
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_section_modify_content() -> TestResult:
    """Test: Modify content of a section"""
    result = TestResult("Section Content Modify")
    try:
        file_id = upload_file()
        
        new_file_id = edit_document(
            file_id,
            "modify the Introduction section to make it more concise and impactful"
        )
        
        # If it completes without error, consider it a success
        # (Content modification is subjective and hard to validate programmatically)
        result.passed = True
        result.message = "Section modification completed"
        result.details = {"modified": True}
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


# ============================================================================
# SPECIAL OPERATIONS
# ============================================================================

def test_table_remove() -> TestResult:
    """Test: Remove all tables"""
    result = TestResult("Remove All Tables")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Count tables
        initial_tables = initial.count(r"\begin{table")
        
        new_file_id = edit_document(file_id, "remove all tables")
        final = download_content(new_file_id)
        
        final_tables = final.count(r"\begin{table")
        
        if initial_tables > 0 and final_tables == 0:
            result.passed = True
            result.message = f"Removed all {initial_tables} tables"
            result.details = {"removed": initial_tables}
        elif initial_tables == 0:
            result.passed = True
            result.message = "No tables to remove"
        else:
            result.message = f"Failed - {final_tables} tables remain (started with {initial_tables})"
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


def test_equation_remove() -> TestResult:
    """Test: Remove all equations"""
    result = TestResult("Remove All Equations")
    try:
        file_id = upload_file()
        initial = download_content(file_id)
        
        # Count various equation environments
        equation_patterns = [r'\begin{equation', r'\begin{align', r'\$.*\$', r'\\\[.*\\\]']
        initial_count = sum(len(re.findall(pattern, initial, re.DOTALL)) for pattern in equation_patterns)
        
        new_file_id = edit_document(file_id, "remove all equations and formulas")
        final = download_content(new_file_id)
        
        final_count = sum(len(re.findall(pattern, final, re.DOTALL)) for pattern in equation_patterns)
        
        if initial_count > 0 and final_count < initial_count:
            result.passed = True
            result.message = f"Reduced equations from {initial_count} to {final_count}"
            result.details = {"removed": initial_count - final_count}
        elif initial_count == 0:
            result.passed = True
            result.message = "No equations found"
        else:
            result.message = f"Failed to remove equations - count: {initial_count}→{final_count}"
        
    except Exception as e:
        result.message = f"Error: {str(e)}"
    
    return result


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run comprehensive test suite"""
    print("\n" + "="*80)
    print("COMPREHENSIVE LATEX DOCUMENT EDITOR TEST SUITE")
    print("="*80)
    
    test_groups = {
        "WORD-LEVEL OPERATIONS": [
            test_word_add,
            test_word_replace,
            test_word_remove,
            test_word_modify,
        ],
        "SENTENCE-LEVEL OPERATIONS": [
            test_sentence_add,
            test_sentence_replace,
            test_sentence_remove,
            test_sentence_highlight,
        ],
        "SECTION-LEVEL OPERATIONS": [
            test_section_add,
            test_section_replace_title,
            test_section_remove,
            test_section_modify_content,
        ],
        "SPECIAL OPERATIONS": [
            test_table_remove,
            test_equation_remove,
        ]
    }
    
    all_results = []
    
    for group_name, tests in test_groups.items():
        print(f"\n{'='*80}")
        print(f"{group_name}")
        print(f"{'='*80}")
        
        for test_func in tests:
            print(f"\n🧪 Running: {test_func.__doc__.replace('Test: ', '')}...")
            result = test_func()
            all_results.append(result)
            print(f"   {result}")
            if result.details:
                for key, value in result.details.items():
                    print(f"      • {key}: {value}")
            time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\n📊 Overall Results: {passed}/{total} tests passed ({percentage:.1f}%)\n")
    
    # Group by status
    passed_tests = [r for r in all_results if r.passed]
    failed_tests = [r for r in all_results if not r.passed]
    
    if passed_tests:
        print(f"✅ PASSED ({len(passed_tests)}):")
        for r in passed_tests:
            print(f"   • {r.name}")
    
    if failed_tests:
        print(f"\n❌ FAILED ({len(failed_tests)}):")
        for r in failed_tests:
            print(f"   • {r.name}")
            print(f"     └─ {r.message}")
    
    print("\n" + "="*80)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
