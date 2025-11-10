"""
RAG LaTeX Fixer Service - SIMPLIFIED for testing
"""

import os
from typing import Dict, Any, Optional

class RAGFixerService:
    """Service for RAG-based LaTeX fixing - SIMPLIFIED"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.gemini_api_key:
            print("Warning: GEMINI_API_KEY not found, using simplified mode")
    
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
        Fix LaTeX document using RAG approach - SIMPLIFIED
        """
        # SIMPLIFIED IMPLEMENTATION FOR TESTING
        fixed_content = latex_content
        fixes_applied = []
        
        # Apply some basic LaTeX fixes
        
        # Fix common package issues
        if "\\usepackage{graphicx}" not in fixed_content and "\\includegraphics" in fixed_content:
            fixed_content = fixed_content.replace("\\usepackage{amsfonts}", "\\usepackage{amsfonts}\n\\usepackage{graphicx}")
            fixes_applied.append("Added missing graphicx package")
        
        # Fix spacing issues
        if "\\\\\\\\" in fixed_content:
            fixed_content = fixed_content.replace("\\\\\\\\", "\\\\")
            fixes_applied.append("Fixed double line breaks")
        
        # Add basic conference formatting if IEEE
        if conference == "IEEE" and "\\documentclass[conference]{IEEEtran}" not in fixed_content:
            if "\\documentclass{article}" in fixed_content:
                fixed_content = fixed_content.replace("\\documentclass{article}", "\\documentclass[conference]{IEEEtran}")
                fixes_applied.append("Applied IEEE conference formatting")
        
        # Fix common LaTeX issues
        if "\\cite{}" in fixed_content:
            fixed_content = fixed_content.replace("\\cite{}", "\\cite{reference}")
            fixes_applied.append("Fixed empty citations")
        
        # Ensure proper package ordering
        if "\\usepackage{hyperref}" in fixed_content and "\\usepackage{url}" in fixed_content:
            # Move hyperref to end (simplified)
            hyperref_line = "\\usepackage{hyperref}"
            if fixed_content.find(hyperref_line) < fixed_content.find("\\usepackage{url}"):
                fixed_content = fixed_content.replace(hyperref_line, "")
                fixed_content = fixed_content.replace("\\usepackage{url}", "\\usepackage{url}\n" + hyperref_line)
                fixes_applied.append("Reordered package loading")
        
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
        # Use the same logic as the main fix method for now
        return await self.fix_latex_document(
            latex_content=latex_content,
            document_type=document_type,
            compile_pdf=compile_pdf
        )