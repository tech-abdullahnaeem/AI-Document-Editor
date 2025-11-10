"""
RAG LaTeX Fixer Service - Wrapper for existing RAG fixer
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import shutil

# Add parent directories to path
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir / "Rag latex fixer"))
sys.path.insert(0, str(parent_dir))

# Temporarily disable RAG imports to test basic server functionality
# try:
#     from enhanced_user_guided_rag import ContextAwareRAGFixer, DocumentContext
#     from user_guided_comprehensive_rag import UserGuidedLaTeXProcessor, AdvancedRAGLatexFixer
# except ImportError as e:
#     print(f"Warning: Could not import RAG components: {e}")
#     # We'll handle this gracefully in the service methods

# Placeholder for testing
ContextAwareRAGFixer = None
DocumentContext = None
UserGuidedLaTeXProcessor = None
AdvancedRAGLatexFixer = None

class RAGFixerService:
    """Service for RAG-based LaTeX fixing"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")
    
    async def fix_latex_document(
        self,
        latex_content: str,
        document_type: str = "research",
        conference: str = "IEEE",
        column_format: str = "2-column",
        converted: bool = False,
        original_format: Optional[str] = None,
        compile_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Fix LaTeX document using RAG approach (SIMPLIFIED FOR TESTING)
        
        Args:
            latex_content: LaTeX source code
            document_type: "research" or "normal"
            conference: Conference type
            column_format: "1-column" or "2-column"
            converted: Whether document was converted from PDF
            original_format: Original document format
            compile_pdf: Whether to compile to PDF
            
        Returns:
            Dictionary with fixed content and metadata
        """
        # SIMPLIFIED IMPLEMENTATION FOR TESTING
        # Apply basic fixes to demonstrate functionality
        
        fixed_content = latex_content
        
        # Apply some basic LaTeX fixes
        fixes_applied = []
        
        # Fix common issues
        if "\\usepackage{graphicx}" not in fixed_content and "\\includegraphics" in fixed_content:
            fixed_content = fixed_content.replace("\\usepackage{amsfonts}", "\\usepackage{amsfonts}\n\\usepackage{graphicx}")
            fixes_applied.append("Added missing graphicx package")
        
        # Fix spacing issues
        fixed_content = fixed_content.replace("\\\\\\\\", "\\\\")
        if "\\\\\\\\" in latex_content:
            fixes_applied.append("Fixed double line breaks")
        
        # Add basic conference formatting if IEEE
        if conference == "IEEE" and "\\documentclass[conference]{IEEEtran}" not in fixed_content:
            if "\\documentclass" in fixed_content:
                fixed_content = fixed_content.replace("\\documentclass{", "\\documentclass[conference]{IEEEtran}")
                fixes_applied.append("Applied IEEE conference formatting")
        
        return {
            "fixed_content": fixed_content,
            "pdf_path": None,  # PDF compilation disabled for testing
            "issues_found": len(fixes_applied),
            "issues_fixed": len(fixes_applied),
            "report": {
                "total_issues": len(fixes_applied),
                "contextual_fixes": len(fixes_applied),
                "generic_fixes": 0,
                "confidence_scores": [],
                "document_type": document_type,
                "conference": conference,
                "column_format": column_format,
                "fixes_applied": fixes_applied
            }
        }
    
    async def fix_latex_simple(
        self,
        latex_content: str,
        document_type: str = "normal",
        compile_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Simple LaTeX fixing without RAG (faster, basic fixes)
        """
        # For normal documents, use generic fixes only
        context = DocumentContext(
            column_format="1-column",
            conference_type="GENERIC",
            original_format=None,
            conversion_applied=False
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            
            input_file = temp_dir_path / "input.tex"
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            # Initialize with simplified context
            fixer = AdvancedRAGLatexFixer(context)
            
            try:
                # Apply basic fixes
                fixed_content = fixer.apply_fixes_to_document(latex_content)
                
                # Save fixed content
                output_file = temp_dir_path / "output.tex"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Compile if requested
                pdf_path = None
                if compile_pdf:
                    try:
                        from latex_compiler import LaTeXCompiler
                        compiler = LaTeXCompiler(latex_engine="pdflatex")
                        pdf_path = compiler.compile(str(output_file), str(temp_dir_path))
                    except Exception as e:
                        print(f"PDF compilation warning: {e}")
                
                return {
                    "fixed_content": fixed_content,
                    "pdf_path": pdf_path,
                    "issues_found": 0,  # Simple mode doesn't count issues
                    "issues_fixed": 0,
                    "report": {
                        "mode": "simple",
                        "document_type": document_type
                    }
                }
                
            except Exception as e:
                raise Exception(f"Error in simple fixing process: {str(e)}")
