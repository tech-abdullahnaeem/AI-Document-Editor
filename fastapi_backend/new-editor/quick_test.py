"""
QUICK TEST - All operations with bold modifications
"""

import os
from workflow import LatexEditorWorkflow


def quick_test():
    """Quick test of all operations"""
    
    tex_file = '/Users/abdullah/Desktop/Techinoid/final with fast api copy/input /glucobench/glucobench .tex'
    
    if not os.path.exists(tex_file):
        print(f"❌ File not found: {tex_file}")
        return
    
    workflow = LatexEditorWorkflow(output_dir='./quick_test_output')
    
    # Test all operation types in one batch
    queries = [
        # REPLACE + BOLD
        "replace 'accuracy' with 'precision'",
        "make 'precision' bold",
        
        # REMOVE
        "remove the word 'however'",
        
        # FORMAT - Highlight
        "highlight 'glucose' in yellow",
        
        # FORMAT - Bold
        "make 'prediction' bold",
        
        # FORMAT - Italic  
        "make 'et al.' italic",
    ]
    
    print("\n" + "="*70)
    print(f"QUICK TEST: {len(queries)} operations")
    print("="*70)
    
    result = workflow.batch_process(
        tex_file,
        queries,
        output_name="quick_test_all_ops",
        compile_pdf=True
    )
    
    print("\n" + "="*70)
    print("RESULTS:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Operations: {result['successful_operations']}/{result['operations']}")
    print(f"Changes: {result['changes']}")
    print(f"TEX: {result['tex_path']}")
    print(f"PDF: {result['pdf_path']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    quick_test()
