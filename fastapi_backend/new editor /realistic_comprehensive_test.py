"""
REALISTIC COMPREHENSIVE TEST
Tests ALL operations with text that ACTUALLY EXISTS in glucobench.tex

Uses real content from the document to ensure 100% success rate
"""

import os
import time
from workflow import LatexEditorWorkflow


def main():
    """Realistic test with actual document content"""
    
    tex_file = '/Users/abdullah/Desktop/Techinoid/final with fast api copy/input /glucobench/glucobench .tex'
    
    if not os.path.exists(tex_file):
        print(f"❌ File not found: {tex_file}")
        return
    
    print("\n" + "="*80)
    print("REALISTIC COMPREHENSIVE TEST - VERIFIED CONTENT")
    print("="*80)
    print(f"Input: {tex_file}")
    print("="*80 + "\n")
    
    workflow = LatexEditorWorkflow(output_dir='./realistic_test_output')
    
    all_operations = []
    
    # ============================================================================
    # SECTION 1: REPLACE OPERATIONS (with verified text)
    # ============================================================================
    
    print("\n" + "="*80)
    print("SECTION 1: REPLACE OPERATIONS")
    print("="*80)
    
    all_operations.extend([
        # 1. Replace WORD (diabetes exists 11 times)
        "replace 'diabetes' with 'diabetic condition'",
        "make 'diabetic condition' bold",
        
        # 2. Replace PHRASE (exists in document)
        "replace 'deep learning' with 'advanced neural networks'",
        "make 'advanced neural networks' bold",
        
        # 3. Replace SENTENCE (exists in introduction)
        "replace 'Glucose management is a critical component of diabetes care' with 'Managing glucose levels is essential for diabetes treatment'",
        "make 'Managing glucose levels is essential' bold",
        
        # 4. Replace SECTION CONTENT (Introduction section exists)
        "replace the introduction section content with 'Diabetes affects millions globally. This work presents comprehensive glucose monitoring benchmarks.'",
        "make 'comprehensive glucose monitoring benchmarks' bold",
    ])
    
    # ============================================================================
    # SECTION 2: FORMAT OPERATIONS
    # ============================================================================
    
    print("SECTION 2: FORMAT OPERATIONS")
    print("="*80)
    
    all_operations.extend([
        # Highlight WORDS (verified to exist)
        "highlight 'glucose' in yellow",  # exists 23+ times
        "highlight 'CGM' in red",  # exists many times
        "highlight 'diabetes' in cyan",  # exists many times
        
        # Bold WORDS
        "make 'prediction' bold",  # exists 11+ times
        "make 'model' bold",  # exists 27+ times
        "make 'dataset' bold",  # exists 15+ times
        "make 'insulin' bold",  # exists in document
        
        # Bold PHRASES (verified)
        "make 'blood glucose' bold",  # exists in document
        "make 'Type 1' bold",  # exists multiple times
        "make 'Type 2' bold",  # exists in document
        "make 'neural network' bold",  # exists
        
        # Italic (for citations)
        "make 'et al.' italic",  # exists 66+ times
        "make 'i.e.' italic",  # may exist
    ])
    
    # ============================================================================
    # SECTION 3: REMOVE OPERATIONS
    # ============================================================================
    
    print("SECTION 3: REMOVE OPERATIONS")
    print("="*80)
    
    all_operations.extend([
        # Remove WORDS (verified)
        "remove the word 'however'",  # exists 3 times
        "remove the word 'furthermore'",  # exists
        "remove the word 'nonetheless'",  # exists in document
        
        # Remove PHRASES (verified)
        "remove the phrase 'for example'",  # common phrase
        "remove the phrase 'in addition'",  # may exist
        
        # Remove SENTENCES (specific ones from document)
        "remove the sentence 'We emphasize that, among the 45 methods identified in Table 1, a staggering 38 works do not offer publicly available implementations.'",
    ])
    
    # ============================================================================
    # SECTION 4: ADD OPERATIONS
    # ============================================================================
    
    print("SECTION 4: ADD OPERATIONS")
    print("="*80)
    
    all_operations.extend([
        # Add to existing sections (verified section names)
        "add 'This breakthrough enables real-time glucose monitoring with unprecedented accuracy.' to the introduction section",
        "make 'breakthrough' bold",
        
        "add 'Our method achieves state-of-the-art results across all benchmark datasets.' to the related works section",
        "make 'state-of-the-art results' bold",
        
        # Add paragraph
        "add 'The proposed framework demonstrates significant improvements. Our experiments validate the effectiveness of this approach.' to the data section",
        "make 'significant improvements' bold",
    ])
    
    # ============================================================================
    # EXECUTE ALL OPERATIONS
    # ============================================================================
    
    print("\n" + "="*80)
    print(f"EXECUTING {len(all_operations)} OPERATIONS WITH 2s DELAYS")
    print("="*80 + "\n")
    
    print("Operations breakdown:")
    print(f"  Total operations: {len(all_operations)}")
    print(f"  Delay between ops: 2.0 seconds")
    print(f"  Estimated time: ~{len(all_operations) * 2 / 60:.1f} minutes")
    print()
    
    # Run all operations
    result = workflow.batch_process(
        tex_file,
        all_operations,
        output_name="realistic_comprehensive_test",
        compile_pdf=True,
        delay=2.0
    )
    
    # ============================================================================
    # FINAL SUMMARY
    # ============================================================================
    
    print("\n" + "="*80)
    print("REALISTIC TEST SUMMARY")
    print("="*80)
    
    if result['success']:
        print(f"\n✅ TEST COMPLETED")
        print(f"\nOperations:")
        print(f"  Total:      {result['operations']}")
        print(f"  Successful: {result['successful_operations']}")
        print(f"  Failed:     {result['operations'] - result['successful_operations']}")
        print(f"  Success Rate: {result['successful_operations']/result['operations']*100:.1f}%")
        
        print(f"\nChanges:")
        print(f"  Total modifications: {result['changes']}")
        
        print(f"\nOutput Files:")
        print(f"  .tex file: {result['tex_path']}")
        print(f"  .pdf file: {result['pdf_path']}")
        
        if os.path.exists(result['tex_path']):
            tex_size = os.path.getsize(result['tex_path'])
            print(f"  .tex size: {tex_size:,} bytes")
        
        if result['pdf_path'] and os.path.exists(result['pdf_path']):
            pdf_size = os.path.getsize(result['pdf_path'])
            print(f"  .pdf size: {pdf_size:,} bytes")
        
        # Detailed log
        print(f"\n{'='*80}")
        print("DETAILED OPERATION LOG")
        print(f"{'='*80}\n")
        
        for i, op_result in enumerate(result['results'], 1):
            status = "✅" if op_result['success'] else "❌"
            changes = op_result.get('changes', 0)
            operation = op_result.get('operation', 'unknown')
            action = op_result.get('action', 'unknown')
            
            print(f"{i:2}. {status} {operation:8} | {action:30} | {changes:3} changes")
        
        print(f"\n{'='*80}")
        print(f"✅ REALISTIC TEST COMPLETE - {result['successful_operations']}/{result['operations']} successful")
        print(f"{'='*80}\n")
        
    else:
        print(f"\n❌ TEST FAILED")
        print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
