"""
LaTeX parsing and structure extraction utilities
"""
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path


class LatexParser:
    """Parse and analyze LaTeX document structure"""
    
    def __init__(self):
        self.document_class_pattern = re.compile(r'\\documentclass(\[.*?\])?\{(.*?)\}')
        self.package_pattern = re.compile(r'\\usepackage(\[.*?\])?\{(.*?)\}')
        self.begin_pattern = re.compile(r'\\begin\{(.*?)\}')
        self.end_pattern = re.compile(r'\\end\{(.*?)\}')
        
    def extract_document_class(self, latex: str) -> Dict[str, str]:
        """Extract document class and options"""
        match = self.document_class_pattern.search(latex)
        if match:
            options = match.group(1).strip('[]') if match.group(1) else ""
            doc_class = match.group(2)
            return {
                "class": doc_class,
                "options": options,
                "is_two_column": "twocolumn" in options.lower()
            }
        return {"class": "unknown", "options": "", "is_two_column": False}
    
    def extract_packages(self, latex: str) -> List[Dict[str, str]]:
        """Extract all packages used"""
        packages = []
        for match in self.package_pattern.finditer(latex):
            packages.append({
                "name": match.group(2),
                "options": match.group(1).strip('[]') if match.group(1) else ""
            })
        return packages
    
    def is_two_column_document(self, latex: str) -> bool:
        """Determine if document is two-column format"""
        doc_class = self.extract_document_class(latex)
        if doc_class["is_two_column"]:
            return True
        
        # Check for multicol package
        packages = self.extract_packages(latex)
        if any(pkg["name"] == "multicol" for pkg in packages):
            return True
        
        return False
    
    def extract_element(self, latex: str, element_type: str) -> Optional[Dict[str, any]]:
        """
        Extract specific elements like \\author, \\title, etc.
        """
        # Pattern to match \element{...} with nested braces support
        pattern = rf'\\{element_type}\s*{{([^{{}}]*(?:{{[^{{}}]*}}[^{{}}]*)*)}}'
        match = re.search(pattern, latex, re.DOTALL)
        
        if match:
            start_pos = match.start()
            end_pos = match.end()
            
            # Find line numbers
            lines_before = latex[:start_pos].count('\n')
            lines_in_element = match.group(0).count('\n')
            
            return {
                "content": match.group(1),
                "full_match": match.group(0),
                "start_line": lines_before + 1,
                "end_line": lines_before + lines_in_element + 1,
                "start_pos": start_pos,
                "end_pos": end_pos
            }
        return None
    
    def extract_all_environments(self, latex: str, env_name: str) -> List[Dict[str, any]]:
        """
        Extract all instances of a specific environment
        """
        environments = []
        pattern = rf'\\begin\{{{env_name}\}}(.*?)\\end\{{{env_name}\}}'
        
        for match in re.finditer(pattern, latex, re.DOTALL):
            start_pos = match.start()
            end_pos = match.end()
            lines_before = latex[:start_pos].count('\n')
            lines_in_env = match.group(0).count('\n')
            
            environments.append({
                "content": match.group(1),
                "full_match": match.group(0),
                "start_line": lines_before + 1,
                "end_line": lines_before + lines_in_env + 1,
                "start_pos": start_pos,
                "end_pos": end_pos
            })
        
        return environments
    
    def extract_tables(self, latex: str) -> List[Dict[str, any]]:
        """Extract all table environments"""
        tables = []
        
        # Find table environments
        table_envs = self.extract_all_environments(latex, "table")
        table_star_envs = self.extract_all_environments(latex, "table\\*")
        
        all_tables = table_envs + table_star_envs
        
        for table in all_tables:
            # Check if centering is present
            has_centering = r'\centering' in table['full_match'] or \
                          r'\begin{center}' in table['full_match']
            
            # Check for placement parameters
            placement_match = re.search(r'\\begin\{table\*?\}\[(.*?)\]', table['full_match'])
            placement = placement_match.group(1) if placement_match else None
            
            # Check if it's spanning columns
            is_spanning = 'table*' in table['full_match']
            
            tables.append({
                **table,
                "has_centering": has_centering,
                "placement": placement,
                "is_spanning": is_spanning
            })
        
        return tables
    
    def extract_figures(self, latex: str) -> List[Dict[str, any]]:
        """Extract all figure environments"""
        figures = []
        
        # Find figure environments
        figure_envs = self.extract_all_environments(latex, "figure")
        figure_star_envs = self.extract_all_environments(latex, "figure\\*")
        
        all_figures = figure_envs + figure_star_envs
        
        for figure in all_figures:
            # Check if centering is present
            has_centering = r'\centering' in figure['full_match'] or \
                          r'\begin{center}' in figure['full_match']
            
            # Check for placement parameters
            placement_match = re.search(r'\\begin\{figure\*?\}\[(.*?)\]', figure['full_match'])
            placement = placement_match.group(1) if placement_match else None
            
            # Check if it's spanning columns
            is_spanning = 'figure*' in figure['full_match']
            
            figures.append({
                **figure,
                "has_centering": has_centering,
                "placement": placement,
                "is_spanning": is_spanning
            })
        
        return figures
    
    def check_element_centering(self, element_code: str) -> bool:
        """Check if element has centering commands"""
        centering_patterns = [
            r'\\centering',
            r'\\begin\{center\}',
            r'\\centerline\{',
        ]
        return any(re.search(pattern, element_code) for pattern in centering_patterns)
    
    def extract_context(self, latex: str, start_line: int, end_line: int, 
                       context_lines: int = 5) -> str:
        """Extract code with surrounding context"""
        lines = latex.split('\n')
        start_idx = max(0, start_line - context_lines - 1)
        end_idx = min(len(lines), end_line + context_lines)
        return '\n'.join(lines[start_idx:end_idx])
    
    def get_preamble(self, latex: str) -> str:
        """Extract document preamble"""
        match = re.search(r'(.*?)\\begin\{document\}', latex, re.DOTALL)
        return match.group(1) if match else ""
    
    def get_document_body(self, latex: str) -> str:
        """Extract document body"""
        match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', latex, re.DOTALL)
        return match.group(1) if match else ""
