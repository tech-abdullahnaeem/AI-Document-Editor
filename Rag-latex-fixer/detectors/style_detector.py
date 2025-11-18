"""
Style and layout issue detector for LaTeX documents
"""
import re
from typing import List, Dict, Optional
from loguru import logger

from models import LatexIssue, IssueType, Severity, DocumentAnalysis
from utils.latex_parser import LatexParser


class StyleIssueDetector:
    """
    Detect style and layout issues in LaTeX documents
    Focus on formatting, placement, centering, and structural problems
    """
    
    def __init__(self):
        self.parser = LatexParser()
        
    def analyze_document(self, latex_content: str, 
                        target_format: str = "IEEE_two_column") -> DocumentAnalysis:
        """
        Comprehensive document analysis
        """
        logger.info(f"Analyzing document for {target_format} format compliance")
        
        issues = []
        
        # Extract document structure
        doc_class = self.parser.extract_document_class(latex_content)
        is_two_column = self.parser.is_two_column_document(latex_content)
        
        # 1. Check author block
        author_issues = self._check_author_block(latex_content, target_format)
        issues.extend(author_issues)
        
        # 2. Check title formatting
        title_issues = self._check_title_formatting(latex_content)
        issues.extend(title_issues)
        
        # 3. Check tables
        table_issues = self._check_tables(latex_content, is_two_column)
        issues.extend(table_issues)
        
        # 4. Check figures
        figure_issues = self._check_figures(latex_content, is_two_column)
        issues.extend(figure_issues)
        
        # 5. Check superscript spacing issues
        superscript_issues = self._check_superscript_spacing(latex_content)
        issues.extend(superscript_issues)
        
        # 6. Check indentation and spacing
        spacing_issues = self._check_spacing_and_indentation(latex_content)
        issues.extend(spacing_issues)
        
        # 7. Check column layout consistency
        # DISABLED: Formula overflow checking was disturbing the document
        # if is_two_column:
        #     column_issues = self._check_column_consistency(latex_content)
        #     issues.extend(column_issues)
        
        logger.info(f"Found {len(issues)} issues")
        
        return DocumentAnalysis(
            document_format=target_format,
            detected_issues=issues,
            document_structure={
                "document_class": doc_class,
                "is_two_column": is_two_column,
                "num_tables": len(self.parser.extract_tables(latex_content)),
                "num_figures": len(self.parser.extract_figures(latex_content))
            }
        )
    
    def _check_author_block(self, latex: str, target_format: str) -> List[LatexIssue]:
        """Check author block formatting and centering"""
        issues = []
        
        author_element = self.parser.extract_element(latex, "author")
        if not author_element:
            return issues
        
        # Check if author is centered
        has_centering = self.parser.check_element_centering(author_element['full_match'])
        
        if not has_centering:
            # Check surrounding context for centering
            context = self.parser.extract_context(
                latex, 
                author_element['start_line'], 
                author_element['end_line'],
                context_lines=3
            )
            
            if not self.parser.check_element_centering(context):
                issues.append(LatexIssue(
                    type=IssueType.AUTHOR_BLOCK_INCORRECT,
                    severity=Severity.HIGH,
                    description="Author block is not centered",
                    element="author",
                    location={
                        "start_line": author_element['start_line'],
                        "end_line": author_element['end_line']
                    },
                    current_code=author_element['full_match'],
                    context=context,
                    expected_format=f"Should use \\centering or {target_format}-specific author formatting"
                ))
        
        # Check for format-specific patterns
        if target_format == "IEEE_two_column":
            if "\\IEEEauthorblockN" not in latex and "\\IEEEauthorblockA" not in latex:
                issues.append(LatexIssue(
                    type=IssueType.AUTHOR_BLOCK_INCORRECT,
                    severity=Severity.MEDIUM,
                    description="Not using IEEE-specific author formatting",
                    element="author",
                    location={
                        "start_line": author_element['start_line'],
                        "end_line": author_element['end_line']
                    },
                    current_code=author_element['full_match'],
                    expected_format="Should use \\IEEEauthorblockN and \\IEEEauthorblockA"
                ))
        
        return issues
    
    def _check_title_formatting(self, latex: str) -> List[LatexIssue]:
        """Check title centering and formatting"""
        issues = []
        
        title_element = self.parser.extract_element(latex, "title")
        if not title_element:
            return issues
        
        # Check if title area has proper formatting
        # Most document classes center title by default, but check for issues
        context = self.parser.extract_context(
            latex,
            title_element['start_line'],
            title_element['end_line'],
            context_lines=5
        )
        
        # Check for common issues like manual centering that might interfere
        if re.search(r'\\begin\{flushleft\}', context) or re.search(r'\\raggedright', context):
            issues.append(LatexIssue(
                type=IssueType.TITLE_NOT_CENTERED,
                severity=Severity.MEDIUM,
                description="Title has left-alignment commands that may prevent centering",
                element="title",
                location={
                    "start_line": title_element['start_line'],
                    "end_line": title_element['end_line']
                },
                current_code=title_element['full_match'],
                context=context
            ))
        
        return issues
    
    def _check_tables(self, latex: str, is_two_column: bool) -> List[LatexIssue]:
        """Check table formatting, centering, and placement"""
        issues = []
        
        tables = self.parser.extract_tables(latex)
        
        for i, table in enumerate(tables):
            table_num = i + 1
            
            # Issue 1: Table not centered
            if not table['has_centering']:
                issues.append(LatexIssue(
                    type=IssueType.TABLE_NOT_CENTERED,
                    severity=Severity.HIGH,
                    description=f"Table {table_num} is not centered",
                    element=f"table_{table_num}",
                    location={
                        "start_line": table['start_line'],
                        "end_line": table['end_line']
                    },
                    current_code=table['full_match'],
                    expected_format="Should include \\centering after \\begin{table}"
                ))
            
            # Issue 2: Missing placement parameters
            if not table['placement']:
                issues.append(LatexIssue(
                    type=IssueType.TABLE_PLACEMENT_MISSING,
                    severity=Severity.MEDIUM,
                    description=f"Table {table_num} missing placement parameters",
                    element=f"table_{table_num}",
                    location={
                        "start_line": table['start_line'],
                        "end_line": table['end_line']
                    },
                    current_code=table['full_match'],
                    expected_format="Should include placement like [htbp] or [t]"
                ))
            
            # Issue 3: Column width issues in two-column documents
            if is_two_column:
                # Check if using appropriate width
                if '\\linewidth' in table['full_match'] and not table['is_spanning']:
                    issues.append(LatexIssue(
                        type=IssueType.COLUMN_WIDTH_WRONG,
                        severity=Severity.MEDIUM,
                        description=f"Table {table_num} uses \\linewidth in two-column format",
                        element=f"table_{table_num}",
                        location={
                            "start_line": table['start_line'],
                            "end_line": table['end_line']
                        },
                        current_code=table['full_match'],
                        expected_format="Should use \\columnwidth instead of \\linewidth"
                    ))
                
                # Check if should be spanning
                if self._table_should_span_columns(table['content']):
                    if not table['is_spanning']:
                        issues.append(LatexIssue(
                            type=IssueType.LAYOUT_MISMATCH,
                            severity=Severity.HIGH,
                            description=f"Table {table_num} appears too wide for single column",
                            element=f"table_{table_num}",
                            location={
                                "start_line": table['start_line'],
                                "end_line": table['end_line']
                            },
                            current_code=table['full_match'],
                            expected_format="Consider using table* to span both columns"
                        ))
        
        return issues
    
    def _check_figures(self, latex: str, is_two_column: bool) -> List[LatexIssue]:
        """Check figure formatting, centering, and placement"""
        issues = []
        
        figures = self.parser.extract_figures(latex)
        
        for i, figure in enumerate(figures):
            fig_num = i + 1
            
            # Issue 1: Figure not centered
            if not figure['has_centering']:
                issues.append(LatexIssue(
                    type=IssueType.FIGURE_NOT_CENTERED,
                    severity=Severity.HIGH,
                    description=f"Figure {fig_num} is not centered",
                    element=f"figure_{fig_num}",
                    location={
                        "start_line": figure['start_line'],
                        "end_line": figure['end_line']
                    },
                    current_code=figure['full_match'],
                    expected_format="Should include \\centering after \\begin{figure}"
                ))
            
            # Issue 2: Missing placement parameters
            if not figure['placement']:
                issues.append(LatexIssue(
                    type=IssueType.FLOAT_PLACEMENT_WRONG,
                    severity=Severity.MEDIUM,
                    description=f"Figure {fig_num} missing placement parameters",
                    element=f"figure_{fig_num}",
                    location={
                        "start_line": figure['start_line'],
                        "end_line": figure['end_line']
                    },
                    current_code=figure['full_match'],
                    expected_format="Should include placement like [htbp] or [t]"
                ))
            
            # Issue 3: Width issues in two-column documents
            if is_two_column and not figure['is_spanning']:
                width_match = re.search(r'width=([0-9.]+)\\(linewidth|textwidth)', figure['full_match'])
                if width_match:
                    width_value = float(width_match.group(1))
                    if width_value > 1.0:
                        issues.append(LatexIssue(
                            type=IssueType.COLUMN_WIDTH_WRONG,
                            severity=Severity.HIGH,
                            description=f"Figure {fig_num} width exceeds column width",
                            element=f"figure_{fig_num}",
                            location={
                                "start_line": figure['start_line'],
                                "end_line": figure['end_line']
                            },
                            current_code=figure['full_match'],
                            expected_format="Width should be ≤1.0\\columnwidth or use figure*"
                        ))
        
        return issues
    
    def _check_spacing_and_indentation(self, latex: str) -> List[LatexIssue]:
        """Check for spacing and indentation issues"""
        issues = []
        
        lines = latex.split('\n')
        
        # Check for inconsistent indentation
        indentation_chars = set()
        for line in lines:
            if line and line[0] in [' ', '\t']:
                if line[0] == '\t':
                    indentation_chars.add('tab')
                else:
                    indentation_chars.add('space')
        
        if len(indentation_chars) > 1:
            issues.append(LatexIssue(
                type=IssueType.INDENTATION_INCONSISTENT,
                severity=Severity.LOW,
                description="Inconsistent indentation (mixing tabs and spaces)",
                element="document",
                current_code="Multiple lines with mixed indentation",
                expected_format="Use consistent indentation (prefer spaces)"
            ))
        
        # Check for excessive blank lines
        blank_line_pattern = r'\n\s*\n\s*\n\s*\n'
        if re.search(blank_line_pattern, latex):
            issues.append(LatexIssue(
                type=IssueType.SPACING_INCORRECT,
                severity=Severity.LOW,
                description="Excessive blank lines (3+ consecutive blank lines)",
                element="document",
                current_code="Multiple sections with excessive spacing",
                expected_format="Use single blank lines for paragraph separation"
            ))
        
        return issues
    
    def _check_column_consistency(self, latex: str) -> List[LatexIssue]:
        """Check for column layout consistency in two-column documents"""
        issues = []
        
        # Check for elements that might not work well in two-column
        # Look for wide equations without proper environments
        equation_envs = ['equation', 'align', 'gather']
        for env in equation_envs:
            equations = self.parser.extract_all_environments(latex, env)
            for eq in equations:
                # Check if equation is very long (might need spanning)
                if len(eq['content']) > 50:  # Heuristic
                    # Check if it's in a spanning environment
                    if f'{env}*' not in eq['full_match']:
                        issues.append(LatexIssue(
                            type=IssueType.LAYOUT_MISMATCH,
                            severity=Severity.MEDIUM,
                            description=f"Long equation in {env} may exceed column width",
                            element=f"{env}_environment",
                            location={
                                "start_line": eq['start_line'],
                                "end_line": eq['end_line']
                            },
                            current_code=eq['full_match'],
                            expected_format=f"Consider using {env}* to span columns"
                        ))
        
        return issues
    
    def _check_broken_math_environments(self, latex: str) -> List[LatexIssue]:
        """Check for broken/malformed math environments from PDF conversion"""
        issues = []
        
        # Pattern 1: Inline math ($) mixed with display equation (\begin{equation})
        # e.g., $R\begin{equation}
        pattern1 = r'\$[^$]*\\begin\{(equation|align|multline|gather)'
        for match in re.finditer(pattern1, latex):
            line_num = latex[:match.start()].count('\n') + 1
            issues.append(LatexIssue(
                type=IssueType.MATH_ENVIRONMENT_ERROR,
                severity=Severity.HIGH,
                description="Inline math ($) mixed with display environment (\\begin{equation})",
                element="math_environment",
                location={"start_line": line_num, "end_line": line_num},
                current_code=match.group(0),
                expected_format="Use either inline math ($...$) or display environment (\\begin{equation}...\\end{equation}), not both"
            ))
        
        # Pattern 2: \end{equation} followed immediately by text/math without newline
        # e.g., \end{equation}\mathcal{D}=
        pattern2 = r'\\end\{(equation|align|multline|gather)\}\\?[a-zA-Z\\]'
        for match in re.finditer(pattern2, latex):
            line_num = latex[:match.start()].count('\n') + 1
            issues.append(LatexIssue(
                type=IssueType.MATH_ENVIRONMENT_ERROR,
                severity=Severity.HIGH,
                description="Display math environment ends abruptly in middle of sentence",
                element="math_environment",
                location={"start_line": line_num, "end_line": line_num},
                current_code=match.group(0)[:50],
                expected_format="Math environments should be on their own lines, not inline with text"
            ))
        
        # Pattern 3: Improper use of multline for simple line breaks
        # multline with manual line breaks (\\&)
        pattern3 = r'\\begin\{multline\}[^}]*?\\\\\s*&'
        for match in re.finditer(pattern3, latex, re.DOTALL):
            line_num = latex[:match.start()].count('\n') + 1
            issues.append(LatexIssue(
                type=IssueType.MATH_ENVIRONMENT_ERROR,
                severity=Severity.MEDIUM,
                description="Improper use of multline environment with manual line breaks (\\\\&)",
                element="multline",
                location={"start_line": line_num, "end_line": line_num},
                current_code=match.group(0)[:80],
                expected_format="Use align environment for multi-line equations with alignment, or remove line breaks"
            ))
        
        # Pattern 4: Empty or nearly empty equation environments
        pattern4 = r'\\begin\{(equation|align|multline|gather)\}\s*\n\s*\\end\{\1\}'
        for match in re.finditer(pattern4, latex):
            line_num = latex[:match.start()].count('\n') + 1
            issues.append(LatexIssue(
                type=IssueType.MATH_ENVIRONMENT_ERROR,
                severity=Severity.LOW,
                description=f"Empty {match.group(1)} environment",
                element=match.group(1),
                location={"start_line": line_num, "end_line": line_num},
                current_code=match.group(0),
                expected_format="Remove empty math environments"
            ))
        
        # Pattern 5: Text between \end{multline} and next word (PDF conversion artifact)
        pattern5 = r'\\end\{multline\}[^\\$\n]*?(?=[A-Z]|\$|\\)'
        for match in re.finditer(pattern5, latex):
            if len(match.group(0)) > 15:  # Only flag if there's significant text
                line_num = latex[:match.start()].count('\n') + 1
                issues.append(LatexIssue(
                    type=IssueType.MATH_ENVIRONMENT_ERROR,
                    severity=Severity.MEDIUM,
                    description="Text improperly placed after \\end{multline}",
                    element="multline",
                    location={"start_line": line_num, "end_line": line_num},
                    current_code=match.group(0)[:60],
                    expected_format="Math environments should be separated from surrounding text"
                ))
        
        return issues
    
    def _table_should_span_columns(self, table_content: str) -> bool:
        """Heuristic to determine if table should span columns"""
        # Count columns in tabular
        tabular_match = re.search(r'\\begin\{tabular\}\{([^}]+)\}', table_content)
        if tabular_match:
            col_spec = tabular_match.group(1)
            # Count column specifiers (l, c, r, p)
            num_cols = len(re.findall(r'[lcrp]', col_spec))
            # If more than 4 columns, probably should span
            return num_cols > 4
        return False
    
    def _check_superscript_spacing(self, latex: str) -> List[LatexIssue]:
        """Check for superscript spacing issues like ${ }^{"""
        issues = []
        
        # Pattern for problematic superscript spacing
        superscript_pattern = r'\$\{\s*\}\s*\^\{\s*\d+\s*\}\s*\{\s*\}\s*\^\{\s*.*?\}'
        matches = re.finditer(superscript_pattern, latex, re.MULTILINE)
        
        for match in matches:
            # Find line number
            line_num = latex[:match.start()].count('\n') + 1
            
            issues.append(LatexIssue(
                type=IssueType.FORMATTING_INCONSISTENT,
                severity=Severity.MEDIUM,
                description="Superscript has unnecessary spacing: ${ }^{...}{ }^{...}",
                element="superscript",
                location={"start_line": line_num, "end_line": line_num},
                current_code=match.group(0),
                expected_format="$^{...}$ or proper superscript formatting"
            ))
        
        return issues
