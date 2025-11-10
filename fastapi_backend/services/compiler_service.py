"""
Compiler Service - LaTeX to PDF compilation using CLI logic
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import tempfile
import shutil

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent.parent
src_dir = parent_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(parent_dir))

# Import the same LaTeX compiler used by CLI
try:
    from doc_edit.latex_compiler import LaTeXCompiler
except ImportError as e:
    print(f"⚠️  Warning: Could not import LaTeXCompiler: {e}")
    print(f"   src_dir: {src_dir}")
    print(f"   parent_dir: {parent_dir}")
    LaTeXCompiler = None

class CompilerService:
    """Service for compiling LaTeX documents to PDF - Uses CLI Logic"""
    
    def __init__(self, engine: str = "pdflatex"):
        """
        Initialize compiler service with CLI's LaTeX compiler
        
        Args:
            engine: LaTeX engine (pdflatex, xelatex, lualatex)
        """
        self.engine = engine
        # Use the exact same compiler as CLI
        if LaTeXCompiler:
            self.compiler = LaTeXCompiler(latex_engine=engine)
        else:
            self.compiler = None
    
    def compile_latex(self, latex_path: str) -> Dict[str, Any]:
        """
        Compile LaTeX file to PDF using CLI's LaTeX compiler
        
        Args:
            latex_path: Path to LaTeX file
            
        Returns:
            Dictionary with compilation results
        """
        if not os.path.exists(latex_path):
            raise FileNotFoundError(f"LaTeX file not found: {latex_path}")
        
        if not self.compiler:
            return {
                "success": False,
                "pdf_path": None,
                "log": "LaTeX compiler not available",
                "warnings": [],
                "errors": ["LaTeXCompiler could not be imported"]
            }
        
        latex_file = Path(latex_path)
        work_dir = latex_file.parent
        output_pdf = str(work_dir / f"{latex_file.stem}.pdf")
        
        try:
            # Read LaTeX content
            with open(latex_path, 'r', encoding='utf-8') as f:
                latex_code = f.read()
            
            # Use CLI's compiler - EXACT SAME METHOD AS CLI
            print(f"🔧 Compiling with {self.engine} using CLI logic...")
            pdf_path, compilation_log = self.compiler.compile_latex_to_pdf(
                latex_code=latex_code,
                output_path=output_pdf,
                working_dir=str(work_dir)
            )
            
            # Check if compilation succeeded
            if pdf_path and os.path.exists(pdf_path):
                print(f"✅ PDF compiled successfully: {pdf_path}")
                return {
                    "success": True,
                    "pdf_path": pdf_path,
                    "log": compilation_log or "Compilation successful",
                    "warnings": [],
                    "errors": []
                }
            else:
                print(f"❌ Compilation failed")
                return {
                    "success": False,
                    "pdf_path": None,
                    "log": compilation_log or "Compilation failed",
                    "warnings": [],
                    "errors": [compilation_log] if compilation_log else ["Unknown compilation error"]
                }
                
        except Exception as e:
            print(f"❌ Compilation error: {str(e)}")
            return {
                "success": False,
                "pdf_path": None,
                "log": str(e),
                "warnings": [],
                "errors": [str(e)]
            }
