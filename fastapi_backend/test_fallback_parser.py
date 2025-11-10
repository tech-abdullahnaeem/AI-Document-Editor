"""Test fallback parser extraction"""
import sys
sys.path.insert(0, '/Users/abdullah/Desktop/Techinoid/final with fast api copy/fastapi_backend/new editor ')

from query_parser import QueryParser

parser = QueryParser()

# Force fallback by setting api_keys to empty
parser.api_keys = []
parser.generation_config = None

test_queries = [
    "Add section 'Discussion' before Limitations section",
    "Add section 'Conclusions' after Acknowledgments",
    "Add section 'Future Work' after the Results section",
]

print("\n" + "="*80)
print("TESTING FALLBACK PARSER - Section Name Extraction")
print("="*80)

for query in test_queries:
    print(f"\n📝 Query: {query}")
    print("-"*80)
    result = parser._fallback_parse(query)
    print(f"   Operation: {result['operation']}")
    print(f"   Action: {result['action']}")
    print(f"   Section Name: {result.get('section_name', 'NOT SET')}")
    print(f"   Target: {result.get('target', 'NOT SET')}")
    print(f"   Position: {result.get('position', 'NOT SET')}")
    print(f"   New Text: {result.get('new_text', 'NOT SET')[:50]}")
    
    # Verify correctness
    if query == test_queries[0]:
        assert result['section_name'] == 'Discussion', f"Expected 'Discussion', got '{result['section_name']}'"
        assert 'Limitations' in result['target'], f"Expected 'Limitations' in target, got '{result['target']}'"
        assert result['position'] == 'before'
        print("   ✅ CORRECT")
    elif query == test_queries[1]:
        assert result['section_name'] == 'Conclusions', f"Expected 'Conclusions', got '{result['section_name']}'"
        assert result['target'] == 'Acknowledgments', f"Expected 'Acknowledgments', got '{result['target']}'"
        assert result['position'] == 'after'
        print("   ✅ CORRECT")
    elif query == test_queries[2]:
        assert result['section_name'] == 'Future Work', f"Expected 'Future Work', got '{result['section_name']}'"
        assert 'Results' in result['target'], f"Expected 'Results' in target, got '{result['target']}'"
        assert result['position'] == 'after'
        print("   ✅ CORRECT")

print("\n" + "="*80)
print("ALL TESTS PASSED ✅")
print("="*80 + "\n")
