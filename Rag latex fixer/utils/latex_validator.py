"""
LaTeX compilation and validation utilities
"""
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, List, Optional
import re


class LatexValidator:
    """Validate LaTeX documents by compilation"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.latex_compilers = ['pdflatex', 'xelatex', 'lualatex']
        
    def compile_latex(self, latex_content: str, 
                     compiler: str = 'pdflatex') -> Tuple[bool, str, List[str]]:
        """
        Compile LaTeX content and return results
        
        Returns:
            Tuple of (success, log_content, errors)
        """
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            tex_file = temp_path / "document.tex"
            
            # Write LaTeX content
            tex_file.write_text(latex_content, encoding='utf-8')
            
            try:
                # Run pdflatex
                result = subprocess.run(
                    [compiler, '-interaction=nonstopmode', 'document.tex'],
                    cwd=temp_path,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                # Read log file
                log_file = temp_path / "document.log"
                log_content = log_file.read_text(encoding='utf-8', errors='ignore') if log_file.exists() else ""
                
                # Parse errors
                errors = self._parse_latex_errors(log_content)
                
                # Check if PDF was generated
                pdf_file = temp_path / "document.pdf"
                success = pdf_file.exists() and len(errors) == 0
                
                return success, log_content, errors
                
            except subprocess.TimeoutExpired:
                return False, "", ["Compilation timeout"]
            except Exception as e:
                return False, "", [f"Compilation error: {str(e)}"]
    
    def _parse_latex_errors(self, log_content: str) -> List[str]:
        """Parse LaTeX log file for errors"""
        errors = []
        
        # Pattern for LaTeX errors
        error_patterns = [
            r'! (.+)',  # Error lines start with !
            r'.*Error:.*',
            r'.*Fatal.*',
        ]
        
        for line in log_content.split('\n'):
            for pattern in error_patterns:
                if re.match(pattern, line):
                    errors.append(line.strip())
        
        return errors
    
    def check_syntax(self, latex_content: str) -> Tuple[bool, List[str]]:
        """
        Quick syntax check without full compilation
        """
        issues = []
        
        # Check for basic syntax issues
        # 1. Unmatched braces
        open_braces = latex_content.count('{')
        close_braces = latex_content.count('}')
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
        
        # 2. Unmatched environments
        begin_envs = re.findall(r'\\begin\{(\w+)\}', latex_content)
        end_envs = re.findall(r'\\end\{(\w+)\}', latex_content)
        
        for env in begin_envs:
            if begin_envs.count(env) != end_envs.count(env):
                issues.append(f"Unmatched environment: {env}")
        
        # 3. Check for document structure
        if '\\documentclass' not in latex_content:
            issues.append("Missing \\documentclass")
        
        if '\\begin{document}' not in latex_content:
            issues.append("Missing \\begin{document}")
        
        if '\\end{document}' not in latex_content:
            issues.append("Missing \\end{document}")
        
        return len(issues) == 0, issues
    
    def validate_with_compilation(self, latex_content: str) -> dict:
        """
        Full validation with compilation
        """
        # First do quick syntax check
        syntax_ok, syntax_issues = self.check_syntax(latex_content)
        
        if not syntax_ok:
            return {
                "success": False,
                "syntax_valid": False,
                "compilation_success": False,
                "errors": syntax_issues
            }
        
        # Try compilation
        success, log, errors = self.compile_latex(latex_content)
        
        return {
            "success": success,
            "syntax_valid": True,
            "compilation_success": success,
            "errors": errors,
            "log": log
        }
