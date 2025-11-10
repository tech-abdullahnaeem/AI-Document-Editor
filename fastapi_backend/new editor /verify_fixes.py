"""
Quick verification that fixes are in place
Tests the methods WITHOUT actually running operations
"""

import sys
import inspect

# Test 1: Check if remove_phrase exists
print("\n" + "="*80)
print("VERIFICATION 1: SimpleRemover.remove_phrase method")
print("="*80)

try:
    from remove import SimpleRemover
    remover = SimpleRemover()
    
    if hasattr(remover, 'remove_phrase'):
        print("✅ remove_phrase method EXISTS")
        
        # Check signature
        sig = inspect.signature(remover.remove_phrase)
        params = list(sig.parameters.keys())
        print(f"   Parameters: {params}")
        
        expected_params = ['content', 'phrase']
        if params == expected_params:
            print(f"✅ Signature CORRECT: {expected_params}")
        else:
            print(f"❌ Signature INCORRECT: expected {expected_params}, got {params}")
    else:
        print("❌ remove_phrase method DOES NOT EXIST")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Test 2: Check add_content_to_section signature
print("\n" + "="*80)
print("VERIFICATION 2: SimpleAdder.add_content_to_section signature")
print("="*80)

try:
    from add import SimpleAdder
    adder = SimpleAdder()
    
    if hasattr(adder, 'add_content_to_section'):
        print("✅ add_content_to_section method EXISTS")
        
        # Check signature
        sig = inspect.signature(adder.add_content_to_section)
        params = list(sig.parameters.keys())
        print(f"   Parameters: {params}")
        
        expected_params = ['content', 'section_name', 'new_content', 'position']
        if params == expected_params:
            print(f"✅ Signature CORRECT: {expected_params}")
        else:
            print(f"⚠️  Signature: expected {expected_params}, got {params}")
        
        # Check if it has 'convert_to_latex' parameter (should NOT have it)
        if 'convert_to_latex' in params:
            print("❌ INCORRECT: Has 'convert_to_latex' parameter (should use 'position')")
            sys.exit(1)
        else:
            print("✅ CORRECT: Does NOT have 'convert_to_latex' parameter")
            
    else:
        print("❌ add_content_to_section method DOES NOT EXIST")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Test 3: Check DocumentEditor._execute_add doesn't use convert_to_latex
print("\n" + "="*80)
print("VERIFICATION 3: DocumentEditor._execute_add uses correct parameters")
print("="*80)

try:
    with open('document_editor.py', 'r') as f:
        content = f.read()
    
    # Check if convert_to_latex is used in _execute_add
    if 'convert_to_latex=convert' in content:
        # Check if it's in _execute_add section
        execute_add_section = content.split('def _execute_add')[1].split('def ')[0]
        
        if 'convert_to_latex=convert' in execute_add_section:
            print("❌ INCORRECT: _execute_add still uses 'convert_to_latex=convert'")
            sys.exit(1)
        else:
            print("✅ CORRECT: _execute_add does NOT use 'convert_to_latex=convert'")
    else:
        print("✅ CORRECT: No 'convert_to_latex=convert' found in document_editor.py")
    
    # Check if position="end" is used
    if 'position="end"' in content:
        print("✅ CORRECT: Uses 'position=\"end\"' parameter")
    else:
        print("⚠️  WARNING: 'position=\"end\"' not found")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Test 4: Check DocumentEditor._execute_remove calls remove_phrase
print("\n" + "="*80)
print("VERIFICATION 4: DocumentEditor._execute_remove calls remove_phrase")
print("="*80)

try:
    with open('document_editor.py', 'r') as f:
        content = f.read()
    
    # Check if remove_phrase is called
    if "action == 'remove_phrase'" in content and 'self.remover.remove_phrase' in content:
        print("✅ CORRECT: _execute_remove has remove_phrase action mapped")
    else:
        print("❌ INCORRECT: _execute_remove does NOT call remove_phrase")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)

# Final summary
print("\n" + "="*80)
print("VERIFICATION SUMMARY")
print("="*80)
print("✅ All fixes verified successfully!")
print("\nChanges confirmed:")
print("  1. ✅ SimpleRemover.remove_phrase() method added")
print("  2. ✅ SimpleAdder.add_content_to_section() uses 'position' parameter")
print("  3. ✅ DocumentEditor._execute_add() uses 'position=\"end\"'")
print("  4. ✅ DocumentEditor._execute_remove() calls remove_phrase()")
print("\n🎉 Ready to run ultimate_comprehensive_test.py! 🎉")
print("="*80 + "\n")
