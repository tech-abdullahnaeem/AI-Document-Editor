"""
END-TO-END LATEX EDITOR WORKFLOW

Complete workflow:
1. User provides .tex file path and natural language prompt
2. Read the .tex file
3. Parse prompt with AI to extract editing intent
4. Apply modifications at exact positions
5. Save modified .tex file
6. Compile to PDF
7. Return paths to modified .tex and .pdf files
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Tuple, Dict, Optional
from document_editor import DocumentEditor


class LatexEditorWorkflow:
    """
    Complete workflow for editing LaTeX files via natural language.
    
    Features:
    - Reads .tex file from disk
    - Parses natural language editing instructions
    - Applies modifications at exact positions in document
    - Saves modified .tex file
    - Compiles to PDF
    - Returns both .tex and .pdf outputs
    """
    
    def __init__(self, output_dir: str = None):
        """
        Initialize the workflow.
        
        Args:
            output_dir: Directory for output files (default: './editing_output')
        """
        self.editor = DocumentEditor()
        self.output_dir = output_dir or './editing_output'
        
        # Create output directory if it doesn't exist
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Output directory: {self.output_dir}")
    
    def process(self, 
                tex_file_path: str, 
                prompt: str,
                output_name: str = None,
                compile_pdf: bool = True) -> Dict:
        """
        Complete editing workflow.
        
        Args:
            tex_file_path: Path to input .tex file
            prompt: Natural language editing instruction(s)
            output_name: Name for output files (default: based on input filename)
            compile_pdf: Whether to compile to PDF (default: True)
            
        Returns:
            Dictionary with:
            - success: bool
            - tex_path: path to modified .tex file
            - pdf_path: path to compiled .pdf (if compile_pdf=True)
            - changes: number of modifications made
            - operation: type of operation performed
            - error: error message (if any)
            
        Example:
            >>> workflow = LatexEditorWorkflow()
            >>> result = workflow.process(
            ...     'paper.tex',
            ...     "highlight 'machine learning' in yellow"
            ... )
            >>> print(result['pdf_path'])
        """
        print("\n" + "="*70)
        print("LATEX EDITING WORKFLOW")
        print("="*70)
        print(f"Input file: {tex_file_path}")
        print(f"Prompt: {prompt}")
        print("="*70 + "\n")
        
        try:
            # Step 1: Read the .tex file
            print("📖 Step 1: Reading LaTeX file...")
            if not os.path.exists(tex_file_path):
                raise FileNotFoundError(f"File not found: {tex_file_path}")
            
            with open(tex_file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            print(f"   ✅ Read {len(original_content)} characters\n")
            
            # Step 2: Parse prompt and apply modifications
            print("🤖 Step 2: Parsing prompt and applying modifications...")
            modified_content, result = self.editor.edit(original_content, prompt)
            
            if not result['success']:
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'tex_path': None,
                    'pdf_path': None,
                    'changes': 0
                }
            
            print(f"   ✅ Applied {result['changes']} modification(s)\n")
            
            # Step 3: Determine output filename
            if output_name is None:
                input_name = Path(tex_file_path).stem
                operation = result.get('operation', 'edited')
                output_name = f"{input_name}_{operation}"
            
            # Step 4: Save modified .tex file
            print("💾 Step 3: Saving modified LaTeX file...")
            tex_output_path = os.path.join(self.output_dir, f"{output_name}.tex")
            
            with open(tex_output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"   ✅ Saved to: {tex_output_path}\n")
            
            # Step 5: Compile to PDF (if requested)
            pdf_output_path = None
            if compile_pdf:
                print("🔨 Step 4: Compiling to PDF...")
                pdf_output_path = self._compile_pdf(tex_output_path)
                
                if pdf_output_path:
                    print(f"   ✅ PDF created: {pdf_output_path}\n")
                else:
                    print("   ⚠️  PDF compilation failed (but .tex file is saved)\n")
            
            # Success!
            print("="*70)
            print("✅ WORKFLOW COMPLETE")
            print("="*70)
            print(f"Modified .tex: {tex_output_path}")
            if pdf_output_path:
                print(f"Compiled .pdf: {pdf_output_path}")
            print("="*70 + "\n")
            
            return {
                'success': True,
                'tex_path': tex_output_path,
                'pdf_path': pdf_output_path,
                'changes': result['changes'],
                'operation': result.get('operation'),
                'action': result.get('action'),
                'error': None
            }
            
        except Exception as e:
            print(f"\n❌ Error in workflow: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'tex_path': None,
                'pdf_path': None,
                'changes': 0
            }
    
    def batch_process(self,
                     tex_file_path: str,
                     prompts: list,
                     output_name: str = None,
                     compile_pdf: bool = True,
                     delay: float = 1.5) -> Dict:
        """
        Process multiple editing operations in sequence.
        
        Args:
            tex_file_path: Path to input .tex file
            prompts: List of natural language editing instructions
            output_name: Name for output files
            compile_pdf: Whether to compile to PDF
            delay: Delay in seconds between operations (default: 1.5s)
            
        Returns:
            Dictionary with results
        """
        print("\n" + "="*70)
        print("BATCH LATEX EDITING WORKFLOW")
        print("="*70)
        print(f"Input file: {tex_file_path}")
        print(f"Operations: {len(prompts)}")
        print(f"Delay: {delay}s between operations")
        print("="*70 + "\n")
        
        try:
            # Step 1: Read the .tex file
            print("📖 Step 1: Reading LaTeX file...")
            if not os.path.exists(tex_file_path):
                raise FileNotFoundError(f"File not found: {tex_file_path}")
            
            with open(tex_file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            print(f"   ✅ Read {len(original_content)} characters\n")
            
            # Step 2: Apply all modifications with delays
            print(f"🤖 Step 2: Applying {len(prompts)} modifications with {delay}s delays...")
            modified_content, results = self.editor.batch_edit(original_content, prompts, delay=delay)
            
            successful = sum(1 for r in results if r['success'])
            total_changes = sum(r.get('changes', 0) for r in results if r['success'])
            
            print(f"   ✅ {successful}/{len(prompts)} operations successful")
            print(f"   ✅ Total changes: {total_changes}\n")
            
            # Step 3: Determine output filename
            if output_name is None:
                input_name = Path(tex_file_path).stem
                output_name = f"{input_name}_batch_edited"
            
            # Step 4: Save modified .tex file
            print("💾 Step 3: Saving modified LaTeX file...")
            tex_output_path = os.path.join(self.output_dir, f"{output_name}.tex")
            
            with open(tex_output_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print(f"   ✅ Saved to: {tex_output_path}\n")
            
            # Step 5: Compile to PDF
            pdf_output_path = None
            if compile_pdf:
                print("🔨 Step 4: Compiling to PDF...")
                pdf_output_path = self._compile_pdf(tex_output_path)
                
                if pdf_output_path:
                    print(f"   ✅ PDF created: {pdf_output_path}\n")
                else:
                    print("   ⚠️  PDF compilation failed (but .tex file is saved)\n")
            
            # Success!
            print("="*70)
            print("✅ BATCH WORKFLOW COMPLETE")
            print("="*70)
            print(f"Modified .tex: {tex_output_path}")
            if pdf_output_path:
                print(f"Compiled .pdf: {pdf_output_path}")
            print(f"Operations: {successful}/{len(prompts)} successful")
            print(f"Total changes: {total_changes}")
            print("="*70 + "\n")
            
            return {
                'success': True,
                'tex_path': tex_output_path,
                'pdf_path': pdf_output_path,
                'changes': total_changes,
                'operations': len(prompts),
                'successful_operations': successful,
                'results': results,
                'error': None
            }
            
        except Exception as e:
            print(f"\n❌ Error in batch workflow: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'success': False,
                'error': str(e),
                'tex_path': None,
                'pdf_path': None,
                'changes': 0
            }
    
    def _compile_pdf(self, tex_path: str) -> Optional[str]:
        """
        Compile .tex file to PDF using pdflatex.
        
        Args:
            tex_path: Path to .tex file
            
        Returns:
            Path to generated .pdf file, or None if compilation failed
        """
        try:
            # Get absolute path
            tex_path = os.path.abspath(tex_path)
            tex_dir = os.path.dirname(tex_path)
            tex_filename = os.path.basename(tex_path)
            
            # Run pdflatex
            # We run it twice to resolve references
            for run in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_filename],
                    cwd=tex_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if run == 0 and result.returncode != 0:
                    print(f"   ⚠️  pdflatex first pass had errors (continuing...)")
            
            # Check if PDF was created
            pdf_path = tex_path.replace('.tex', '.pdf')
            if os.path.exists(pdf_path):
                # Clean up auxiliary files
                self._cleanup_aux_files(tex_path)
                return pdf_path
            else:
                print(f"   ❌ PDF not created")
                # Print last few lines of log for debugging
                log_path = tex_path.replace('.tex', '.log')
                if os.path.exists(log_path):
                    with open(log_path, 'r') as f:
                        lines = f.readlines()
                        print("   Last log lines:")
                        for line in lines[-10:]:
                            print(f"      {line.rstrip()}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ PDF compilation timed out")
            return None
        except FileNotFoundError:
            print(f"   ❌ pdflatex not found - please install LaTeX")
            return None
        except Exception as e:
            print(f"   ❌ PDF compilation error: {e}")
            return None
    
    def _cleanup_aux_files(self, tex_path: str):
        """Clean up auxiliary files created by pdflatex"""
        base_path = tex_path.replace('.tex', '')
        extensions = ['.aux', '.log', '.out', '.toc', '.lof', '.lot', '.fls', '.fdb_latexmk']
        
        for ext in extensions:
            aux_file = base_path + ext
            if os.path.exists(aux_file):
                try:
                    os.remove(aux_file)
                except:
                    pass


def main():
    """Demo usage"""
    
    # Use the specified .tex file
    tex_file = '/Users/abdullah/Desktop/Techinoid/final with fast api copy/input /glucobench/glucobench .tex'
    
    if not os.path.exists(tex_file):
        print(f"❌ File not found: {tex_file}")
        print("   Please check the file path")
        return
    
    print(f"✅ Using file: {tex_file}")
    
    # Create workflow
    workflow = LatexEditorWorkflow(output_dir='./demo_output')
    
    # Demo 1: Single operation
    print("\n" + "="*70)
    print("DEMO 1: Single Operation")
    print("="*70)
    
    result = workflow.process(
        tex_file,
        "highlight 'machine learning' in yellow",
        output_name="demo_highlighted"
    )
    
    if result['success']:
        print(f"\n✅ Success!")
        print(f"   Changes: {result['changes']}")
        print(f"   TEX: {result['tex_path']}")
        print(f"   PDF: {result['pdf_path']}")
    else:
        print(f"\n❌ Failed: {result['error']}")
    
    # Demo 2: Batch operations
    print("\n" + "="*70)
    print("DEMO 2: Batch Operations")
    print("="*70)
    
    batch_result = workflow.batch_process(
        tex_file,
        [
            "replace 'accuracy' with 'precision'",
            "make 'neural network' bold",
            "remove the word 'significant'"
        ],
        output_name="demo_batch"
    )
    
    if batch_result['success']:
        print(f"\n✅ Batch Success!")
        print(f"   Operations: {batch_result['successful_operations']}/{batch_result['operations']}")
        print(f"   Total changes: {batch_result['changes']}")
        print(f"   TEX: {batch_result['tex_path']}")
        print(f"   PDF: {batch_result['pdf_path']}")
    else:
        print(f"\n❌ Batch Failed: {batch_result['error']}")


if __name__ == "__main__":
    main()
