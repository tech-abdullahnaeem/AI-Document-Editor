#!/usr/bin/env python3
"""
Complete User-Guided RAG LaTeX System
Integrates user context with comprehensive detection and fixing
"""

import os
import sys
import json
import argparse
import numpy as np
import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Import our existing components
sys.path.append('.')
sys.path.append('./src')
from enhanced_user_guided_rag import ContextAwareRAGFixer, DocumentContext
from detect_conversion_issues import DocumentFormatDetector
from detectors.style_detector import StyleIssueDetector

@dataclass
class ProcessingStats:
    """Statistics for user-guided processing"""
    total_issues: int = 0
    contextual_fixes: int = 0
    generic_fixes: int = 0
    confidence_scores: List[float] = None
    context_relevance_scores: List[str] = None
    
    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = []
        if self.context_relevance_scores is None:
            self.context_relevance_scores = []

class UserGuidedLaTeXProcessor:
    """Comprehensive processor with user context guidance"""
    
    def __init__(self, api_key: str, context: DocumentContext):
        """Initialize with user context"""
        self.context = context
        self.rag_fixer = ContextAwareRAGFixer(api_key)
        self.style_detector = StyleIssueDetector()
        self.format_detector = DocumentFormatDetector()
        self.stats = ProcessingStats()
        
    def detect_context_specific_issues(self, content: str) -> List[Dict]:
        """Detect issues with context awareness"""
        all_issues = []
        
        print(f"🔍 Phase 1: Standard LaTeX Issues ({self.context.conference_type} focus)")
        # Map conference type to format
        format_map = {
            "IEEE": "IEEE_two_column" if self.context.column_format == "2-column" else "IEEE_one_column",
            "ACM": "ACM_two_column" if self.context.column_format == "2-column" else "ACM_one_column", 
            "SPRINGER": "generic",
            "ELSEVIER": "generic",
            "GENERIC": "generic"
        }
        format_name = format_map.get(self.context.conference_type, "generic")
        
        analysis = self.style_detector.analyze_document(content, format_name)
        style_issues_raw = analysis.detected_issues
        
        # Convert to dict format
        style_issues = []
        for issue in style_issues_raw:
            style_issues.append({
                'type': issue.type.value if hasattr(issue.type, 'value') else str(issue.type),
                'severity': issue.severity.value if hasattr(issue.severity, 'value') else str(issue.severity),
                'description': issue.description,
                'line_number': getattr(issue.location, 'line', 1) if issue.location else 1
            })
        
        # Filter style issues by conference type
        filtered_style_issues = []
        for issue in style_issues:
            # Add context-specific severity based on conference
            if self.context.conference_type == "IEEE":
                if "author" in issue['description'].lower():
                    issue['context_priority'] = "HIGH"
                elif "formatting" in issue['description'].lower():
                    issue['context_priority'] = "MEDIUM"
                else:
                    issue['context_priority'] = "LOW"
            elif self.context.conference_type == "ACM":
                if "title" in issue['description'].lower() or "author" in issue['description'].lower():
                    issue['context_priority'] = "HIGH"
                else:
                    issue['context_priority'] = "MEDIUM"
            else:
                issue['context_priority'] = "MEDIUM"
                
            filtered_style_issues.append(issue)
        
        all_issues.extend(filtered_style_issues)
        print(f"   Found {len(filtered_style_issues)} context-prioritized style issues")
        
        print(f"🔍 Phase 2: Conversion Issues ({self.context.column_format} format)")
        if self.context.conversion_applied:
            conversion_issues = self._detect_conversion_issues(content)
            
            # Add context-specific information
            for issue in conversion_issues:
                issue['context_priority'] = "HIGH"  # Conversion issues are always high priority
                if self.context.column_format == "2-column" and "margin" in issue['description'].lower():
                    issue['context_priority'] = "CRITICAL"
                    
            all_issues.extend(conversion_issues)
            print(f"   Found {len(conversion_issues)} conversion-specific issues")
        else:
            print("   Skipping conversion detection (document not converted)")
            
        print(f"🔍 Phase 3: Conference-Specific Requirements")
        conference_issues = self._detect_conference_specific_issues(content)
        all_issues.extend(conference_issues)
        print(f"   Found {len(conference_issues)} conference-specific issues")
        
        self.stats.total_issues = len(all_issues)
        return all_issues
    
    def _detect_conference_specific_issues(self, content: str) -> List[Dict]:
        """Detect conference-specific formatting issues"""
        issues = []
        
        # For normal documents: only check for basic document class and margin issues
        if hasattr(self.context, 'document_type') and self.context.document_type == 'normal':
            # Check for proper article document class
            if "\\documentclass" in content and "article" not in content:
                issues.append({
                    'type': 'document_class_fix',
                    'severity': 'medium',
                    'description': 'Normal document should use article document class',
                    'line_number': self._find_line_number(content, "\\documentclass"),
                    'context_priority': 'HIGH'
                })
            
            # Check for geometry package (margin control)
            if "\\usepackage{geometry}" not in content:
                issues.append({
                    'type': 'margin_control',
                    'severity': 'high',
                    'description': 'Add geometry package with 0.5in margins for better space utilization',
                    'line_number': self._find_line_number(content, "\\usepackage") or 1,
                    'context_priority': 'HIGH'
                })
            
            # Still check for table formatting (same as research papers)
            table_issues = self._detect_table_formatting_issues(content)
            issues.extend(table_issues)
            
            return issues
        
        # For research papers: full conference-specific processing
        if self.context.conference_type == "IEEE":
            # Check for IEEEtran document class
            if "\\documentclass" in content and "IEEEtran" not in content:
                issues.append({
                    'type': 'conference_format',
                    'severity': 'high',
                    'description': 'IEEE papers should use IEEEtran document class',
                    'line_number': self._find_line_number(content, "\\documentclass"),
                    'context_priority': 'CRITICAL'
                })
                
            # Check for IEEE author formatting
            if "\\author" in content and "\\IEEEauthorblockN" not in content:
                issues.append({
                    'type': 'conference_format',
                    'severity': 'medium',
                    'description': 'IEEE papers should use \\IEEEauthorblockN for authors',
                    'line_number': self._find_line_number(content, "\\author"),
                    'context_priority': 'HIGH'
                })
            
            # Check for table formatting issues (both 1-column and 2-column)
            table_issues = self._detect_table_formatting_issues(content)
            issues.extend(table_issues)
                
        elif self.context.conference_type == "ACM":
            # Check for ACM document class
            if "\\documentclass" in content and "acmart" not in content:
                issues.append({
                    'type': 'conference_format',
                    'severity': 'high',
                    'description': 'ACM papers should use acmart document class',
                    'line_number': self._find_line_number(content, "\\documentclass"),
                    'context_priority': 'CRITICAL'
                })
            
            # Check for ACM author format
            if "\\author" in content and "\\affiliation" not in content:
                issues.append({
                    'type': 'author_block_incorrect',
                    'severity': 'high',
                    'description': 'ACM papers should use proper \\author{} and \\affiliation{} format',
                    'line_number': self._find_line_number(content, "\\author"),
                    'context_priority': 'HIGH'
                })
            
            # Check for legacy ACM formatting issues
            if "\\footnotetext" in content and "Address correspondence" in content:
                issues.append({
                    'type': 'legacy_correspondence_footnote',
                    'severity': 'medium',
                    'description': 'Legacy correspondence footnote conflicts with ACM authornote format',
                    'line_number': self._find_line_number(content, "\\footnotetext"),
                    'context_priority': 'MEDIUM'
                })
            
            if "\\date{}" in content:
                issues.append({
                    'type': 'redundant_date_command',
                    'severity': 'low',
                    'description': 'Redundant \\date{} command - ACM uses \\received{} instead',
                    'line_number': self._find_line_number(content, "\\date{}"),
                    'context_priority': 'LOW'
                })
            
            if "\\setcounter{enumi}{2019}" in content:
                issues.append({
                    'type': 'enumerate_counter_hack',
                    'severity': 'medium',
                    'description': 'Strange enumerate counter manipulation should be replaced with proper text',
                    'line_number': self._find_line_number(content, "\\setcounter{enumi}{2019}"),
                    'context_priority': 'MEDIUM'
                })
            
            # Check for table formatting in ACM (both 1-column and 2-column)
            table_issues = self._detect_table_formatting_issues(content)
            issues.extend(table_issues)
                
        elif self.context.conference_type == "GENERIC":
            # For generic format, ensure article document class
            if "\\documentclass" in content and "article" not in content:
                issues.append({
                    'type': 'conference_format',
                    'severity': 'medium',
                    'description': 'Generic format should use article document class',
                    'line_number': self._find_line_number(content, "\\documentclass"),
                    'context_priority': 'HIGH'
                })
            
            # GENERIC format should have reduced margins for better space utilization
            if "\\usepackage{geometry}" not in content and "\\usepackage[" not in content or "geometry" not in content:
                issues.append({
                    'type': 'margin_control',
                    'severity': 'high',
                    'description': 'Generic format should use geometry package with 0.5in margins for better space utilization',
                    'line_number': self._find_line_number(content, "\\usepackage"),
                    'context_priority': 'HIGH'
                })
            
            # Ensure proper table placement without cutting text
            table_issues = self._detect_table_formatting_issues(content)
            issues.extend(table_issues)
                
        # Check column format consistency for non-GENERIC conferences
        if self.context.conference_type != "GENERIC":
            if self.context.column_format == "2-column":
                if ("twocolumn" not in content and 
                    "\\begin{multicols}" not in content and
                    "IEEEtran" not in content):
                    issues.append({
                        'type': 'format_consistency',
                        'severity': 'high',
                        'description': f'Document should be formatted as {self.context.column_format}',
                        'line_number': 1,
                        'context_priority': 'HIGH'
                    })
                
        return issues
    
    def _detect_table_formatting_issues(self, content: str) -> List[Dict]:
        """Detect table formatting issues specific to conference requirements"""
        import re
        issues = []
        
        # Find all table environments
        table_pattern = r'\\begin\{table\*?\}.*?\\end\{table\*?\}'
        tables = re.findall(table_pattern, content, re.DOTALL)
        
        for i, table in enumerate(tables):
            table_line = self._find_line_number(content, table[:50])  # Find approximate line
            
            # IEEE specific table rules
            if self.context.conference_type == "IEEE":
                if self.context.column_format == "2-column":
                    # ALL tables in IEEE 2-column should use table* to span both columns
                    if '\\begin{table}' in table and '\\begin{table*}' not in table:
                        issues.append({
                            'type': 'table_formatting',
                            'severity': 'high',
                            'description': 'IEEE 2-column format requires table* environment for all tables to span both columns and appear at page top',
                            'line_number': table_line,
                            'context_priority': 'HIGH'
                        })
                    
                    # Check table positioning - should use [!tb] with stfloats package for better placement
                    if '\\begin{table' in table and '[!tb]' not in table:
                        issues.append({
                            'type': 'table_formatting',
                            'severity': 'medium',
                            'description': 'IEEE 2-column tables should use [!tb] positioning with stfloats package to place at top',
                            'line_number': table_line,
                            'context_priority': 'MEDIUM'
                        })
                
                elif self.context.column_format == "1-column":
                    # IEEE 1-column tables can appear between text with [htbp] positioning
                    if '\\begin{table' in table and '[htbp]' not in table:
                        issues.append({
                            'type': 'table_formatting',
                            'severity': 'medium',
                            'description': 'IEEE 1-column tables should use [htbp] positioning to appear naturally without covering text',
                            'line_number': table_line,
                            'context_priority': 'MEDIUM'
                        })
                        
            # ACM specific table rules
            elif self.context.conference_type == "ACM":
                if self.context.column_format == "2-column":
                    # ALL tables in ACM 2-column should use table* to span both columns
                    if '\\begin{table}' in table and '\\begin{table*}' not in table:
                        issues.append({
                            'type': 'table_formatting',
                            'severity': 'high',
                            'description': 'ACM 2-column format requires table* environment for all tables to span both columns and appear at page top',
                            'line_number': table_line,
                            'context_priority': 'HIGH'
                        })
                    
                    # Check table positioning for top placement
                    if '\\begin{table' in table and '[!t]' not in table and '[t]' not in table:
                        issues.append({
                            'type': 'table_formatting',
                            'severity': 'medium',
                            'description': 'ACM 2-column tables should use [!t] positioning to place at page top',
                            'line_number': table_line,
                            'context_priority': 'MEDIUM'
                        })
                
                elif self.context.column_format == "1-column":
                    # ACM 1-column tables can appear between text with [htbp] positioning
                    if '\\begin{table' in table and '[htbp]' not in table:
                        issues.append({
                            'type': 'table_formatting',
                            'severity': 'medium',
                            'description': 'ACM 1-column tables should use [htbp] positioning to appear naturally without covering text',
                            'line_number': table_line,
                            'context_priority': 'MEDIUM'
                        })
                        
            # GENERIC format rules - PRESERVE ORIGINAL POSITIONING
            elif self.context.conference_type == "GENERIC":
                # For GENERIC format, don't detect positioning issues
                # Preserve whatever positioning the user has chosen
                pass
            
            # Common issues for all formats
            # Check for proper centering method
            if '\\begin{center}' in table:
                issues.append({
                    'type': 'table_formatting',
                    'severity': 'medium',
                    'description': 'Use \\centering instead of \\begin{center} in tables for better formatting',
                    'line_number': table_line,
                    'context_priority': 'MEDIUM'
                })
            
            # Check for missing caption labels (good practice for all formats)
            if '\\caption{' in table and '\\label{' not in table:
                issues.append({
                    'type': 'table_formatting',
                    'severity': 'low',
                    'description': 'Table should have \\label for proper referencing',
                    'line_number': table_line,
                    'context_priority': 'LOW'
                })
            
            # Check for wide tables with left-aligned columns that may overflow margins
            tabular_match = re.search(r'\\begin\{tabular\}\{([^}]+)\}', table)
            if tabular_match:
                column_spec = tabular_match.group(1)
                # Count consecutive l (left-aligned) columns
                left_aligned_cols = len(re.findall(r'\|?l\|?', column_spec))
                
                # If table has 4+ left-aligned columns, it likely needs width control
                if left_aligned_cols >= 4 and 'p{' not in column_spec:
                    issues.append({
                        'type': 'table_formatting',
                        'severity': 'high',
                        'description': f'Table with {left_aligned_cols} left-aligned columns may overflow page margins. Convert to fixed-width columns with text wrapping',
                        'line_number': table_line,
                        'context_priority': 'HIGH'
                    })
        
        # Check figures for missing labels
        figures = re.findall(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', content, re.DOTALL)
        for i, figure in enumerate(figures):
            figure_line = content[:content.find(figure)].count('\n') + 1
            
            # Check for missing caption labels (good practice for all formats)
            if '\\caption{' in figure and '\\label{' not in figure:
                issues.append({
                    'type': 'figure_formatting',
                    'severity': 'low',
                    'description': 'Figure should have \\label for proper referencing',
                    'line_number': figure_line,
                    'context_priority': 'LOW'
                })
            
            # Check for image sizing issues in 2-column format
            if self.context.column_format == '2-column':
                # Check if figure uses single column environment in 2-column format
                if '\\begin{figure}' in figure and '\\begin{figure*}' not in figure:
                    # Check if image might be too wide
                    if '\\includegraphics[width=\\textwidth]' in figure or '\\includegraphics[width=1' in figure:
                        issues.append({
                            'type': 'figure_sizing',
                            'severity': 'high',
                            'description': 'Figure in 2-column format should use figure* environment and proper width to avoid text overlap',
                            'line_number': figure_line,
                            'context_priority': 'HIGH'
                        })
                
                # Check for improper width specifications
                if '\\includegraphics' in figure and 'width=' in figure:
                    # For figure* (spanning both columns), should use \textwidth
                    # For figure (single column), should use \columnwidth
                    if '\\begin{figure*}' in figure and 'width=\\columnwidth' in figure:
                        issues.append({
                            'type': 'figure_sizing',
                            'severity': 'medium',
                            'description': 'Figure* environment should use \\textwidth for proper sizing across both columns',
                            'line_number': figure_line,
                            'context_priority': 'MEDIUM'
                        })
                    elif '\\begin{figure}' in figure and '\\begin{figure*}' not in figure and 'width=\\textwidth' in figure:
                        issues.append({
                            'type': 'figure_sizing',
                            'severity': 'medium',
                            'description': 'Single column figure should use \\columnwidth instead of \\textwidth',
                            'line_number': figure_line,
                            'context_priority': 'MEDIUM'
                        })
            
            # Check for positioning that allows images to float too far
            positioning_issues = []
            if '\\begin{figure}[h]' in figure or '\\begin{figure*}[h]' in figure:
                positioning_issues.append('[h] positioning can cause text overlap')
            elif '[!htbp]' not in figure and '[!ht]' not in figure and '[H]' not in figure:
                positioning_issues.append('Missing restrictive positioning to keep image close to text')
            
            if positioning_issues:
                issues.append({
                    'type': 'figure_positioning',
                    'severity': 'high',
                    'description': f'Image positioning should use [!ht] or [!htbp] to prevent floating to document end. {positioning_issues[0]}',
                    'line_number': figure_line,
                    'context_priority': 'HIGH'
                })
            
            # Check for oversized images that might get pushed to document end
            if '\\includegraphics' in figure:
                # Look for large width specifications that might cause float displacement
                if ('width=1\\textwidth' in figure or 'width=\\textwidth' in figure or 
                    'width=1.0\\textwidth' in figure or 'width=0.9\\textwidth' in figure):
                    issues.append({
                        'type': 'figure_sizing',
                        'severity': 'high',
                        'description': 'Large image width may cause figure to float to document end. Consider using smaller width (0.8\\textwidth or 0.7\\textwidth) for better placement',
                        'line_number': figure_line,
                        'context_priority': 'HIGH'
                    })
                
                # Check for missing width specification which can cause size issues
                elif 'width=' not in figure and 'scale=' not in figure:
                    issues.append({
                        'type': 'figure_sizing',
                        'severity': 'medium',
                        'description': 'Figure missing size specification. Add width parameter to control placement and prevent floating to document end',
                        'line_number': figure_line,
                        'context_priority': 'MEDIUM'
                    })
        
        return issues
    
    def _detect_conversion_issues(self, content: str) -> List[Dict]:
        """Detect PDF-to-LaTeX conversion issues"""
        issues = []
        
        # Check for generic article class when IEEE/ACM expected
        if "\\documentclass" in content:
            if ("\\documentclass[10pt]{article}" in content or 
                "\\documentclass{article}" in content):
                if self.context.conference_type in ["IEEE", "ACM"]:
                    issues.append({
                        'type': 'conversion_artifact',
                        'severity': 'high',
                        'description': f'Document uses generic article class instead of {self.context.conference_type} format',
                        'line_number': self._find_line_number(content, "\\documentclass"),
                        'context_priority': 'CRITICAL'
                    })
        
        # Check for missing margin control in converted documents
        if "\\usepackage{geometry}" not in content:
            issues.append({
                'type': 'conversion_artifact',
                'severity': 'medium',
                'description': 'Missing margin control package (common in PDF-to-LaTeX conversion)',
                'line_number': 1,
                'context_priority': 'HIGH'
            })
        
        # Check for missing column format specification
        if self.context.column_format == "2-column":
            if ("twocolumn" not in content and 
                "\\begin{multicols}" not in content and
                "IEEEtran" not in content):
                issues.append({
                    'type': 'format_loss',
                    'severity': 'high',
                    'description': 'Original 2-column format lost in conversion',
                    'line_number': 1,
                    'context_priority': 'CRITICAL'
                })
        
        return issues
    
    def _apply_smart_word_breaks(self, table_content: str, column_widths: list = None) -> str:
        """Dynamically add line breaks to long words in table cells based on column width"""
        import re
        
        # Calculate approximate character limit per column based on width
        def get_char_limit_for_width(width_cm):
            """Estimate character limit based on column width in cm"""
            # Rough estimate: 1cm ≈ 2.5-3 characters in small font
            chars_per_cm = 2.5
            return int(width_cm * chars_per_cm)
        
        # Default character limits if no width info
        default_char_limit = 8  # Conservative limit for narrow columns
        
        def break_long_word(word, char_limit=default_char_limit):
            """Break a long word intelligently at good hyphenation points"""
            if len(word) <= char_limit or '\\' in word:  # Don't break LaTeX commands
                return word
            
            # Common patterns for breaking compound words
            compound_patterns = [
                (r'([A-Z][a-z]+)([A-Z][a-z]+)', r'\1\\linebreak \2'),  # CamelCase
                (r'([a-z]+)([A-Z][a-z]+)', r'\1\\linebreak \2'),       # wordWord
                (r'(\w+)(\+\w+)', r'\1\\linebreak \2'),                # word+word
                (r'(\w+)(\(\w+\))', r'\1\\linebreak \2'),              # word(word)
            ]
            
            # Try compound patterns first
            for pattern, replacement in compound_patterns:
                if re.search(pattern, word):
                    return re.sub(pattern, replacement, word)
            
            # For simple long words, break at reasonable points
            if len(word) > char_limit * 1.5:  # Only break very long words
                # Try to break at natural syllable boundaries
                break_points = []
                
                # Look for common syllable patterns
                vowels = 'aeiouAEIOU'
                for i in range(2, len(word) - 2):
                    # Break after consonant-vowel or vowel-consonant transitions
                    if (word[i-1] not in vowels and word[i] in vowels) or \
                       (word[i-1] in vowels and word[i] not in vowels):
                        break_points.append(i)
                
                # Choose break point closest to middle
                if break_points:
                    mid = len(word) // 2
                    best_break = min(break_points, key=lambda x: abs(x - mid))
                    # Ensure minimum 3 characters on each side
                    if best_break >= 3 and len(word) - best_break >= 3:
                        return word[:best_break] + '-\\linebreak ' + word[best_break:]
            
            return word
        
        def process_table_cell(cell_content, char_limit=default_char_limit):
            """Process words in a table cell"""
            # Split by spaces and process each word
            words = cell_content.split()
            processed_words = []
            
            for word in words:
                # Skip LaTeX commands and numbers
                if word.startswith('\\') or word.replace('.', '').replace('-', '').isdigit():
                    processed_words.append(word)
                else:
                    # Remove punctuation for length check but keep it
                    clean_word = re.sub(r'[^\w+()]', '', word)
                    if len(clean_word) > char_limit:
                        broken_word = break_long_word(clean_word, char_limit)
                        # Replace the clean word part with broken version
                        processed_word = word.replace(clean_word, broken_word)
                        processed_words.append(processed_word)
                    else:
                        processed_words.append(word)
            
            return ' '.join(processed_words)
        
        # Process table rows
        def process_table_row(match):
            row_content = match.group(0)
            
            # Skip header rows and lines with only formatting
            if '\\hline' in row_content or '\\multicolumn' in row_content:
                return row_content
            
            # Split by & to get cells
            cells = re.split(r'(\s*&\s*)', row_content)
            
            # Determine character limit based on column count
            num_cells = len([c for c in cells if '&' not in c])
            if num_cells > 0:
                # Adjust character limit based on number of columns
                if num_cells >= 10:
                    char_limit = 6   # Very narrow columns
                elif num_cells >= 6:
                    char_limit = 8   # Narrow columns  
                elif num_cells >= 4:
                    char_limit = 10  # Medium columns
                else:
                    char_limit = 12  # Wide columns
                
                # Process actual cell content (not separators)
                for i in range(0, len(cells), 2):
                    if i < len(cells) and '&' not in cells[i]:
                        cells[i] = process_table_cell(cells[i].strip(), char_limit)
            
            return ''.join(cells)
        
        # Apply to all table rows ending with \\
        table_content = re.sub(r'^[^\\]*\\\\.*$', process_table_row, table_content, flags=re.MULTILINE)
        
        return table_content
    
    def _apply_table_fixes(self, content: str, issue: Dict) -> str:
        """Apply table formatting fixes"""
        import re
        
        # IEEE specific table fixes
        if self.context.conference_type == "IEEE":
            if self.context.column_format == "2-column":
                # IEEE 2-column: Convert ALL tables to table* with [!tb] positioning
                if ('table*' in issue['description'] or 'span both columns' in issue['description']):
                    content = re.sub(r'\\begin\{table\}(\[[^\]]*\])?', r'\\begin{table*}[!tb]', content)
                    content = re.sub(r'\\end\{table\}', r'\\end{table*}', content)
                    
                    # Add stfloats package for better placement
                    if '\\usepackage{stfloats}' not in content:
                        content = re.sub(r'(\\usepackage\{caption\})', r'\1\n\\usepackage{stfloats}', content)
                
                elif 'positioning' in issue['description'].lower():
                    # Fix positioning to [!tb] for IEEE 2-column
                    content = re.sub(r'\\begin\{table\*?\}(\[[^\]]*\])?', r'\\begin{table*}[!tb]', content)
                    
                    if '\\usepackage{stfloats}' not in content:
                        content = re.sub(r'(\\usepackage\{caption\})', r'\1\n\\usepackage{stfloats}', content)
            
            elif self.context.column_format == "1-column":
                # IEEE 1-column: Use [htbp] positioning to appear naturally
                if 'positioning' in issue['description'].lower():
                    content = re.sub(r'\\begin\{table\}(\[[^\]]*\])?', r'\\begin{table}[htbp]', content)
        
        # ACM specific table fixes
        elif self.context.conference_type == "ACM":
            if self.context.column_format == "2-column":
                # ACM 2-column: ALL tables use table* with [!t] to span both columns
                if 'table*' in issue['description'] or 'span both columns' in issue['description']:
                    content = re.sub(r'\\begin\{table\}(\[[^\]]*\])?', r'\\begin{table*}[!t]', content)
                    content = re.sub(r'\\end\{table\}', r'\\end{table*}', content)
                elif 'positioning' in issue['description'].lower():
                    # For existing table* keep it, for regular tables use [!t]
                    if 'table*' in content:
                        content = re.sub(r'\\begin\{table\*\}(\[[^\]]*\])?', r'\\begin{table*}[!t]', content)
                    else:
                        content = re.sub(r'\\begin\{table\}(\[[^\]]*\])?', r'\\begin{table}[!t]', content)
            
            elif self.context.column_format == "1-column":
                # ACM 1-column: Use [htbp] positioning to appear naturally
                if 'positioning' in issue['description'].lower():
                    content = re.sub(r'\\begin\{table\}(\[[^\]]*\])?', r'\\begin{table}[htbp]', content)
        
        # GENERIC format table fixes - PRESERVE ORIGINAL POSITIONING
        elif self.context.conference_type == "GENERIC":
            # For GENERIC format, don't change positioning - preserve original
            # Only apply positioning changes for IEEE/ACM which have specific requirements
            pass
        
        # Common fixes for all formats
        if 'centering' in issue['description'].lower():
            # Fix centering method for all formats
            content = re.sub(r'\\begin\{center\}', r'\\centering', content)
            content = re.sub(r'\\end\{center\}', '', content)
            
            # Also apply smart word breaks to all tables to prevent overflow
            def apply_word_breaks_to_table(match):
                table_content = match.group(0)
                return self._apply_smart_word_breaks(table_content)
            
            content = re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', 
                           apply_word_breaks_to_table, content, flags=re.DOTALL)
            
        elif 'label' in issue['description'].lower():
            # Add missing table labels ONLY to captions that don't already have labels
            import re
            
            # Find all table environments first
            table_pattern = r'\\begin\{table\*?\}.*?\\end\{table\*?\}'
            tables = re.findall(table_pattern, content, re.DOTALL)
            
            for table in tables:
                # Check if this table has a caption but no label
                if '\\caption{' in table and '\\label{' not in table:
                    # Find the caption in this specific table
                    caption_match = re.search(r'(\\caption\{[^}]+\})', table)
                    if caption_match:
                        caption = caption_match.group(1)
                        # Generate a clean, unique label
                        caption_text = re.sub(r'\\caption\{([^}]+)\}', r'\1', caption)
                        label_text = re.sub(r'[^a-zA-Z0-9]+', '_', caption_text.lower())[:30]
                        label_text = re.sub(r'^_+|_+$', '', label_text)  # Remove leading/trailing underscores
                        
                        # Replace the caption with caption + label in the content
                        new_table = table.replace(caption, f"{caption}\n\\label{{tab:{label_text}}}")
                        content = content.replace(table, new_table)
        
        # Fix wide tables with left-aligned columns - NEW APPROACH
        if 'overflow page margins' in issue['description'] or 'left-aligned columns' in issue['description']:
            # Find tables with |l|l|l|l| format and convert to fixed-width columns
            def fix_table_columns_smart(match):
                table_content = match.group(0)
                
                # Find the tabular column specification
                tabular_match = re.search(r'\\begin\{tabular\}\{([^}]+)\}', table_content)
                if tabular_match:
                    column_spec = tabular_match.group(1)
                    
                    # Count all columns (l, c, r, p{...})
                    total_cols = len(re.findall(r'[lcr]|p\{[^}]+\}', column_spec))
                    
                    # STEP 1: Determine full page width including margin space
                    if (self.context.conference_type in ["ACM", "IEEE"] and 
                        self.context.column_format == "2-column"):
                        base_width = 14.0  # cm - text width for table*
                        margin_space = 4.0  # cm - can extend into margins
                    elif self.context.conference_type == "GENERIC":
                        # GENERIC format with 0.5in margins = 1.27cm per side
                        # Letter paper: 21.59cm - 2.54cm = 19.05cm text width
                        # Use 18cm to leave some breathing room and account for borders
                        base_width = 18.0  # cm - text width for 1-column with 0.5in margins
                        margin_space = 0.0  # cm - already using minimal margins
                    else:
                        base_width = 10.8  # cm - text width for 1-column  
                        margin_space = 6.0  # cm - can extend into margins
                    
                    # STEP 2: FIRST EXPAND - Use maximum available space (base + margins)
                    border_space = 0.15 * (total_cols + 1)  # Space for borders
                    total_available_space = base_width + margin_space - border_space
                    expanded_col_width = total_available_space / total_cols
                    
                    # Create expanded column widths
                    expanded_widths = [expanded_col_width] * total_cols
                    expanded_table_width = sum(expanded_widths) + border_space
                    
                    # STEP 3: THEN SCALE DOWN - Check if we need to fit within constraints
                    # For GENERIC format with [ht] positioning, keep table conservative to avoid deferral
                    # Use only 25% of margin space to ensure table fits on page
                    max_reasonable_width = base_width + (margin_space * 0.25)  # Use 25% of margin space for safer fit
                    
                    if expanded_table_width > max_reasonable_width:
                        # Scale down to fit reasonably
                        usable_width = max_reasonable_width - border_space
                        scale_factor = usable_width / sum(expanded_widths)
                        final_widths = [w * scale_factor for w in expanded_widths]
                        total_table_width = sum(final_widths) + border_space
                        margin_shift = (total_table_width - base_width) / 2
                    else:
                        # Use expanded widths with appropriate margin shift
                        final_widths = expanded_widths.copy()
                        total_table_width = expanded_table_width
                        margin_shift = (total_table_width - base_width) / 2
                    
                    # STEP 6: Generate new column specification
                    new_spec = '|' + '|'.join([f'p{{{w:.1f}cm}}' for w in final_widths]) + '|'
                    
                    # Replace the column specification
                    table_content = table_content.replace(
                        f'\\begin{{tabular}}{{{column_spec}}}',
                        f'\\begin{{tabular}}{{{new_spec}}}'
                    )
                    
                    # STEP 7: Apply margin positioning if needed
                    if margin_shift > 0.5:  # Only apply if significant shift needed
                        if '\\centering' in table_content:
                            table_content = table_content.replace(
                                '\\centering',
                                f'\\\\hspace*{{-{margin_shift:.1f}cm}}\\n\\\\centering'
                            )
                        else:
                            # If no centering, add positioning before tabular
                            table_content = re.sub(
                                r'(\\begin\{tabular\})',
                                f'\\\\hspace*{{-{margin_shift:.1f}cm}}\\n\\1',
                                table_content
                            )
                    
                    # STEP 8: Add \small for better fit if not present
                    if '\\small' not in table_content.split('\\begin{tabular}')[0]:
                        # Add \small before tabular
                        table_content = re.sub(
                            r'(\n)(\\begin\{tabular\})',
                            r'\1\\small\n\2',
                            table_content
                        )
                    
                    # STEP 9: Apply smart word breaks based on column widths
                    table_content = self._apply_smart_word_breaks(table_content, final_widths)
                
                return table_content
            
            # Apply to all table environments - SAFER APPROACH
            # Find all table matches first, then process each individually
            table_matches = list(re.finditer(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', content, flags=re.DOTALL))
            
            # Process tables in reverse order to avoid position shifts
            for match in reversed(table_matches):
                try:
                    original_table = match.group(0)
                    fixed_table = fix_table_columns_smart(match)
                    if fixed_table and fixed_table != original_table:
                        start, end = match.span()
                        content = content[:start] + fixed_table + content[end:]
                except Exception as e:
                    # If table processing fails, skip this table to avoid corruption
                    print(f"Warning: Table processing failed, skipping: {e}")
                    continue
        
        # Add float parameters based on conference and format
        if 'setcounter' not in content or 'topfraction' not in content:
            float_params = ""
            if self.context.conference_type == "IEEE" and self.context.column_format == "2-column":
                # IEEE 2-column: prevent tables floating to end
                float_params = ("\n% Adjust float parameters for better table placement\n" +
                              "\\setcounter{dbltopnumber}{2}\n" +
                              "\\renewcommand{\\dbltopfraction}{0.9}\n" +
                              "\\renewcommand{\\dblfloatpagefraction}{0.7}\n")
            elif self.context.conference_type == "IEEE" and self.context.column_format == "1-column":
                # IEEE 1-column: ensure tables don't break text
                float_params = ("\n% Float parameters to ensure tables don't break text\n" +
                              "\\setcounter{topnumber}{2}\n" +
                              "\\renewcommand{\\topfraction}{0.9}\n" +
                              "\\renewcommand{\\textfraction}{0.1}\n" +
                              "\\renewcommand{\\floatpagefraction}{0.8}\n")
            elif self.context.conference_type == "ACM":
                # ACM format: ensure tables don't break text
                float_params = ("\n% Float parameters to ensure tables don't break text\n" +
                              "\\setcounter{topnumber}{2}\n" +
                              "\\renewcommand{\\topfraction}{0.9}\n" +
                              "\\renewcommand{\\textfraction}{0.1}\n" +
                              "\\renewcommand{\\floatpagefraction}{0.8}\n")
            elif self.context.conference_type == "GENERIC":
                # GENERIC format: ensure tables don't cut text
                float_params = ("\n% Float parameters to ensure tables don't break text\n" +
                              "\\setcounter{topnumber}{2}\n" +
                              "\\renewcommand{\\topfraction}{0.9}\n" +
                              "\\renewcommand{\\textfraction}{0.1}\n" +
                              "\\renewcommand{\\floatpagefraction}{0.8}\n")
            
            if float_params:
                # Use string concatenation instead of r'\1' + float_params to avoid regex escape issues
                content = re.sub(r'(\\begin\{document\})', lambda m: m.group(1) + float_params, content)
        
        # FINAL STEP: For GENERIC format, change [h] to [ht] to prevent table deferral
        # [h] = "here only" - if table doesn't fit, LaTeX defers it to end
        # [ht] = "here or top" - if table doesn't fit here, place at top of page
        if self.context.conference_type == "GENERIC":
            content = re.sub(r'\\begin\{table\}\[h\]', r'\\begin{table}[ht]', content)
            content = re.sub(r'\\begin\{table\*\}\[h\]', r'\\begin{table*}[ht]', content)
            
        return content
    
    def _find_line_number(self, content: str, search_text: str) -> int:
        """Find line number of text in content"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_text in line:
                return i
        return 1
    
    def process_issues_with_context(self, issues: List[Dict]) -> List[Dict]:
        """Process issues using context-aware RAG"""
        processed_fixes = []
        
        # Sort issues by context priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_issues = sorted(issues, key=lambda x: priority_order.get(x.get('context_priority', 'LOW'), 3))
        
        for i, issue in enumerate(sorted_issues, 1):
            print(f"🛠️  Processing Issue {i}/{len(issues)}: {issue['description']}")
            print(f"   Priority: {issue.get('context_priority', 'MEDIUM')}")
            
            # Create issue query for RAG
            issue_query = f"{issue['description']} {issue.get('type', '')} {self.context.conference_type}"
            
            # Retrieve contextual examples
            examples = self.rag_fixer.retrieve_contextual_examples(
                issue_query, self.context, top_k=3
            )
            
            print(f"   📚 Retrieved {len(examples)} contextual examples")
            
            # Generate context-aware fix
            fix_result = self.rag_fixer.generate_contextual_fix(
                issue['description'], self.context, examples
            )
            
            # Combine issue info with fix
            processed_fix = {
                'issue': issue,
                'fix': fix_result,
                'examples_used': len(examples),
                'is_contextual': len([ex for ex in examples if 
                                    self.context.conference_type in ex[0].conference_tags]) > 0
            }
            
            processed_fixes.append(processed_fix)
            
            # Update stats
            if processed_fix['is_contextual']:
                self.stats.contextual_fixes += 1
            else:
                self.stats.generic_fixes += 1
                
            self.stats.confidence_scores.append(fix_result.get('confidence', 0.0))
            self.stats.context_relevance_scores.append(fix_result.get('context_relevance', 'Unknown'))
            
            print(f"   ✅ Fix generated (Confidence: {fix_result.get('confidence', 0.0):.2f})")
            
        return processed_fixes
    
    def apply_fixes_to_document(self, original_content: str, fixes: List[Dict]) -> str:
        """Apply all fixes to the original document content"""
        modified_content = original_content
        applied_fixes = []
        
        print(f"\n🔧 APPLYING FIXES TO DOCUMENT")
        print("-" * 40)
        
        # Sort fixes by priority for better application order
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        sorted_fixes = sorted(fixes, key=lambda x: priority_order.get(x['issue'].get('context_priority', 'LOW'), 3))
        
        for i, fix_info in enumerate(sorted_fixes, 1):
            issue = fix_info['issue']
            fix = fix_info['fix']
            
            print(f"Applying Fix {i}/{len(fixes)}: {issue['description']}")
            
            # Apply specific fixes based on issue type
            if issue['type'] == 'document_class_fix':
                # For normal documents: use simple article class
                modified_content = self._apply_document_class_fix(modified_content, 'article')
                applied_fixes.append("Document class updated to article format")
                
            elif issue['type'] == 'conference_format' and 'document class' in issue['description'].lower():
                # Fix document class based on conference type
                if self.context.conference_type == 'IEEE':
                    modified_content = self._apply_document_class_fix(modified_content, 'IEEEtran')
                elif self.context.conference_type == 'ACM':
                    modified_content = self._apply_document_class_fix(modified_content, 'acmart')
                elif self.context.conference_type == 'GENERIC':
                    modified_content = self._apply_document_class_fix(modified_content, 'generic')
                applied_fixes.append(f"Document class updated to {self.context.conference_type} format")
                
            elif issue['type'] == 'conversion_artifact' and 'margin' in issue['description'].lower():
                # Add geometry package
                modified_content = self._apply_geometry_fix(modified_content)
                applied_fixes.append("Added geometry package for margin control")
            
            elif issue['type'] == 'margin_control':
                # Add geometry package with appropriate margins for GENERIC format
                modified_content = self._apply_geometry_fix(modified_content)
                applied_fixes.append("Added geometry package with 0.5in margins for GENERIC format")
                
            elif issue['type'] == 'author_block_incorrect':
                # Fix author formatting
                modified_content = self._apply_author_fix(modified_content)
                applied_fixes.append("Applied conference-specific author formatting")
                
            elif issue['type'] == 'format_loss' and '2-column' in issue['description']:
                # Restore 2-column format
                modified_content = self._apply_column_fix(modified_content)
                applied_fixes.append("Restored 2-column format")
            
            elif issue['type'] == 'table_formatting':
                # Fix table formatting issues
                modified_content = self._apply_table_fixes(modified_content, issue)
                applied_fixes.append(f"Fixed table formatting: {issue['description']}")
                
            elif issue['type'] == 'figure_formatting' or issue['type'] == 'figure_sizing' or issue['type'] == 'figure_positioning':
                # Fix figure formatting, sizing, and positioning issues
                modified_content = self._apply_figure_fixes(modified_content, issue)
                applied_fixes.append(f"Fixed figure: {issue['description']}")
                
            elif issue['type'] in ['legacy_correspondence_footnote', 'redundant_date_command', 'enumerate_counter_hack']:
                # These are handled automatically within the ACM author conversion
                # No separate action needed as _clean_legacy_acm_formatting handles them
                applied_fixes.append(f"Cleaned legacy ACM formatting: {issue['description']}")
                
            
            print(f"   ✅ Applied successfully")
        
        print(f"\n📝 Applied {len(applied_fixes)} fixes to document")
        
        # POST-PROCESSING: Force all images to use [!htbp] positioning
        modified_content = self._force_image_positioning_here(modified_content)
        
        # POST-PROCESSING: Limit all image sizes to maximum 50% width
        modified_content = self._limit_image_sizes(modified_content)
        
        return modified_content
    
    def _force_image_positioning_here(self, content: str) -> str:
        """
        Force all figure environments to use [h] positioning to keep images
        at their exact location and prevent floating to document end
        """
        import re
        
        print(f"\n🔒 LOCKING IMAGE POSITIONS")
        print("-" * 40)
        
        # Replace all figure* positioning with [!htbp] for better placement
        # Pattern: \begin{figure*}[any positioning]
        count_figure_star = len(re.findall(r'\\begin\{figure\*\}\[[^\]]*\]', content))
        content = re.sub(
            r'\\begin\{figure\*\}\[[^\]]*\]',
            r'\\begin{figure*}[!htbp]',
            content
        )
        
        # Replace all figure positioning with [!htbp] for better placement
        # Pattern: \begin{figure}[any positioning]
        count_figure = len(re.findall(r'\\begin\{figure\}\[[^\]]*\]', content))
        content = re.sub(
            r'\\begin\{figure\}\[[^\]]*\]',
            r'\\begin{figure}[!htbp]',
            content
        )
        
        # Add [!htbp] to figures without positioning
        # Pattern: \begin{figure*} (no positioning)
        count_no_pos_star = len(re.findall(r'\\begin\{figure\*\}(?!\[)', content))
        content = re.sub(
            r'\\begin\{figure\*\}(?!\[)',
            r'\\begin{figure*}[!htbp]',
            content
        )
        
        # Pattern: \begin{figure} (no positioning)
        count_no_pos = len(re.findall(r'\\begin\{figure\}(?!\[)', content))
        content = re.sub(
            r'\\begin\{figure\}(?!\[)',
            r'\\begin{figure}[!htbp]',
            content
        )
        
        total_locked = count_figure_star + count_figure + count_no_pos_star + count_no_pos
        if total_locked > 0:
            print(f"   ✅ Applied [!htbp] positioning to {total_locked} images")
            print(f"   📌 Images will stay closer: here, top, bottom, or page")
        else:
            print(f"   ℹ️  No images found to reposition")
        
        return content
    
    def _limit_image_sizes(self, content: str) -> str:
        """
        Limit all image widths to maximum 50% to prevent oversized images
        that cause floating to document end
        """
        import re
        
        print(f"\n📏 LIMITING IMAGE SIZES")
        print("-" * 40)
        
        max_width = "0.5"  # 50% width
        count_resized = 0
        
        # Find all includegraphics commands with width specifications
        # Pattern: \includegraphics[width=...]{filename}
        
        # 1. Replace width=\textwidth or width=1\textwidth or width=1.0\textwidth
        patterns_to_replace = [
            (r'\\includegraphics\[width=\\textwidth\]', r'\\includegraphics[width=' + max_width + r'\\textwidth]'),
            (r'\\includegraphics\[width=1\\textwidth\]', r'\\includegraphics[width=' + max_width + r'\\textwidth]'),
            (r'\\includegraphics\[width=1\.0\\textwidth\]', r'\\includegraphics[width=' + max_width + r'\\textwidth]'),
            (r'\\includegraphics\[width=0\.[6-9]\\textwidth\]', r'\\includegraphics[width=' + max_width + r'\\textwidth]'),
            (r'\\includegraphics\[width=\\columnwidth\]', r'\\includegraphics[width=' + max_width + r'\\columnwidth]'),
            (r'\\includegraphics\[width=1\\columnwidth\]', r'\\includegraphics[width=' + max_width + r'\\columnwidth]'),
            (r'\\includegraphics\[width=1\.0\\columnwidth\]', r'\\includegraphics[width=' + max_width + r'\\columnwidth]'),
            (r'\\includegraphics\[width=0\.[6-9]\\columnwidth\]', r'\\includegraphics[width=' + max_width + r'\\columnwidth]'),
        ]
        
        for pattern, replacement in patterns_to_replace:
            matches = re.findall(pattern, content)
            if matches:
                count_resized += len(matches)
                content = re.sub(pattern, replacement, content)
        
        # 2. Add width to images without size specification
        # Pattern: \includegraphics{filename} (no width)
        images_no_width = re.findall(r'\\includegraphics\{[^}]+\}', content)
        if images_no_width:
            for img in images_no_width:
                # Only process if no [ ] after \includegraphics
                if '[' not in img:
                    new_img = img.replace(r'\includegraphics{', r'\includegraphics[width=' + max_width + r'\textwidth]{')
                    content = content.replace(img, new_img)
                    count_resized += 1
        
        if count_resized > 0:
            print(f"   ✅ Limited {count_resized} images to maximum {max_width} (50%) width")
            print(f"   📐 Smaller images help prevent floating to document end")
        else:
            print(f"   ℹ️  All images already have appropriate sizing")
        
        return content
    
    def _calculate_optimal_column_widths(self, total_cols: int, original_spec: str, table_content: str = "", apply_positioning: bool = False) -> str:
        """
        Content-aware algorithm to calculate optimal column widths dynamically
        Analyzes actual text content in each column to determine optimal widths
        """
        import re
        
        if total_cols <= 0:
            return original_spec
            
        # Determine available page width based on format
        if (self.context.conference_type in ["ACM", "IEEE"] and 
            self.context.column_format == "2-column"):
            available_width = 14.0  # cm - wider for table*
            min_col_width = 0.8
            max_col_width = 6.0
        else:
            available_width = 10.8  # cm - narrower for single column
            min_col_width = 0.6
            max_col_width = 4.0
        
        border_space = 0.2 * (total_cols + 1)
        usable_width = available_width - border_space
        
        # CONTENT-AWARE: Analyze actual column content including sub-columns
        column_content_lengths = []
        if table_content:
            try:
                # Extract table rows (between \hline or \\)
                rows = re.split(r'\\\\|\\hline', table_content)
                
                max_lengths_per_col = [0] * total_cols
                multicolumn_groups = {}  # Track which columns are grouped under multicolumn headers
                
                for row_idx, row in enumerate(rows):
                    # Skip empty rows or rows with only whitespace
                    if not row.strip() or '\\begin{tabular}' in row or '\\end{tabular}' in row:
                        continue
                    
                    # Detect multicolumn headers (like \multicolumn{2}{|c|}{Age})
                    multicolumn_matches = list(re.finditer(r'\\multicolumn\{(\d+)\}\{[^}]*\}\{([^}]*)\}', row))
                    
                    if multicolumn_matches:
                        # This row has multicolumn headers - track the groupings
                        col_position = 0
                        for match in multicolumn_matches:
                            span = int(match.group(1))  # Number of columns spanned
                            header_text = match.group(2)  # Header text
                            
                            # Find the column position by counting & before this match
                            cells_before = row[:match.start()].count('&')
                            col_position = cells_before
                            
                            # Mark these columns as a group
                            if col_position not in multicolumn_groups:
                                multicolumn_groups[col_position] = {
                                    'span': span,
                                    'header': header_text,
                                    'sub_cols': list(range(col_position, min(col_position + span, total_cols)))
                                }
                    
                    # Split by & to get individual cells
                    cells = row.split('&')
                    
                    # Skip rows with multicolumn (we'll analyze sub-columns in other rows)
                    if multicolumn_matches:
                        continue
                    
                    for idx, cell in enumerate(cells[:total_cols]):
                        # ENHANCED CELL CLEANING: More thorough text extraction
                        clean_cell = cell
                        
                        # Remove multirow commands but keep the text
                        clean_cell = re.sub(r'\\multirow\{[^}]*\}\{[^}]*\}\{([^}]*)\}', r'\1', clean_cell)
                        
                        # Remove other LaTeX commands but keep text content
                        clean_cell = re.sub(r'\\textbf\{([^}]*)\}', r'\1', clean_cell)
                        clean_cell = re.sub(r'\\emph\{([^}]*)\}', r'\1', clean_cell)
                        clean_cell = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', clean_cell)
                        clean_cell = re.sub(r'\\[a-zA-Z]+', '', clean_cell)
                        
                        # Clean special characters and spacing
                        clean_cell = re.sub(r'[\{\}\$\|#\\]', '', clean_cell)
                        clean_cell = re.sub(r'\s+', ' ', clean_cell)  # normalize whitespace
                        clean_cell = clean_cell.strip()
                        
                        # Calculate content length (characters) - account for word spacing
                        if clean_cell:
                            # For multi-word cells, add extra space for word breaks
                            word_count = len(clean_cell.split())
                            content_length = len(clean_cell)
                            if word_count > 1:
                                content_length += (word_count - 1) * 0.5  # extra space between words
                            
                            if content_length > max_lengths_per_col[idx]:
                                max_lengths_per_col[idx] = int(content_length)
                
                # CRITICAL: Also analyze header row content (not just data)
                # Find ALL header rows (before first \\hline\\hline or first data row)
                header_row_count = 0
                for row_idx, row in enumerate(rows):
                    if not row.strip() or '\\begin{tabular}' in row or '\\end{tabular}' in row:
                        continue
                    
                    # Stop at double hline (end of headers) or if we see numeric data (start of data rows)
                    if '\\hline' in row and row_idx > 0 and '\\hline' in rows[row_idx - 1]:
                        break
                    
                    # Skip multicolumn/multirow rows from analysis but don't stop
                    if '\\multicolumn' in row or '\\multirow' in row:
                        continue
                    
                    # This is a regular header row - analyze it with enhanced cleaning
                    cells = row.split('&')
                    for idx, cell in enumerate(cells[:total_cols]):
                        # ENHANCED HEADER CLEANING: Same thorough approach as data rows
                        clean_cell = cell
                        
                        # Remove LaTeX commands but preserve text
                        clean_cell = re.sub(r'\\textbf\{([^}]*)\}', r'\1', clean_cell)
                        clean_cell = re.sub(r'\\emph\{([^}]*)\}', r'\1', clean_cell)
                        clean_cell = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', clean_cell)
                        clean_cell = re.sub(r'\\[a-zA-Z]+', '', clean_cell)
                        
                        # Clean special characters
                        clean_cell = re.sub(r'[\{\}\$\|#\\]', '', clean_cell)
                        clean_cell = re.sub(r'\s+', ' ', clean_cell)
                        clean_cell = clean_cell.strip()
                        
                        if clean_cell:
                            # For headers, account for word spacing and give extra weight
                            word_count = len(clean_cell.split())
                            header_length = len(clean_cell)
                            if word_count > 1:
                                header_length += (word_count - 1) * 0.5
                            
                            # Give headers 2.5x weight since they're critical for readability
                            weighted_length = int(header_length * 2.5)
                            if weighted_length > max_lengths_per_col[idx]:
                                max_lengths_per_col[idx] = weighted_length
                    
                    header_row_count += 1
                    # Analyze at most 2 header rows (main headers + sub-headers)
                    if header_row_count >= 2:
                        break
                
                # Adjust widths for multicolumn groups DYNAMICALLY
                # Sub-columns must accommodate BOTH the multicolumn header AND their own headers
                for group_start, group_info in multicolumn_groups.items():
                    sub_cols = group_info['sub_cols']
                    # Clean multicolumn header text
                    header_text = group_info['header']
                    header_text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', header_text)
                    header_text = re.sub(r'\\[a-zA-Z]+', '', header_text)
                    header_text = re.sub(r'\{|\}|\$|\||#', '', header_text)
                    header_length = len(header_text.strip())
                    
                    # Calculate total width of sub-columns
                    total_sub_width = sum(max_lengths_per_col[col] for col in sub_cols)
                    
                    # DYNAMIC: Calculate required width based on multicolumn header length
                    # Add 40% padding for spacing + centering of multicolumn header
                    required_width = header_length * 1.4
                    
                    if required_width > total_sub_width:
                        # Distribute the required width equally among sub-columns
                        width_per_subcol = required_width / len(sub_cols)
                        for col in sub_cols:
                            # Use the maximum of current width or proportional width
                            max_lengths_per_col[col] = max(
                                max_lengths_per_col[col],
                                int(width_per_subcol)
                            )
                    
                    # ENHANCED SUB-COLUMN BALANCING: Ensure fairness within multicolumn groups
                    # Sub-columns under same multicolumn header should be more balanced
                    if len(sub_cols) > 1:
                        # Calculate the maximum width among sub-columns in this group
                        max_subcol_width = max(max_lengths_per_col[col] for col in sub_cols)
                        min_balanced_width = max_subcol_width * 0.7  # At least 70% of the largest
                        
                        # Ensure no sub-column is too narrow compared to its siblings
                        for col in sub_cols:
                            if max_lengths_per_col[col] < min_balanced_width:
                                max_lengths_per_col[col] = int(min_balanced_width)
                    
                    # DYNAMIC MINIMUM: Ensure each sub-column can fit its own header text
                    for col in sub_cols:
                        # Calculate minimum based on actual content + padding
                        min_for_content = max_lengths_per_col[col] * 1.25  # 25% padding
                        if max_lengths_per_col[col] < min_for_content:
                            max_lengths_per_col[col] = int(min_for_content)
                
                # Store multicolumn_groups for later use in width enforcement
                self._last_multicolumn_groups = multicolumn_groups
                self._last_max_lengths_per_col = max_lengths_per_col.copy()
                
                # Convert character lengths to relative weights
                total_chars = sum(max_lengths_per_col) if sum(max_lengths_per_col) > 0 else total_cols
                
                if total_chars > 0:
                    for max_len in max_lengths_per_col:
                        # Weight based on content: more characters = more width
                        # Normalize to get proportion of total width
                        weight = max_len / total_chars if total_chars > 0 else 1.0 / total_cols
                        column_content_lengths.append(weight)
                        
            except Exception as e:
                # If content analysis fails, fall back to pattern-based
                print(f"Content analysis failed: {e}, using pattern-based distribution")
                column_content_lengths = []
                self._last_multicolumn_groups = {}
                self._last_max_lengths_per_col = []
        
        # Calculate column widths based on content or pattern
        column_widths = []
        
        if column_content_lengths and len(column_content_lengths) == total_cols:
            # CONTENT-BASED DISTRIBUTION
            for weight in column_content_lengths:
                # Allocate width proportional to content length
                width = usable_width * weight
                
                # Apply min/max constraints
                width = max(min_col_width, min(width, max_col_width))
                column_widths.append(width)

            # --- TWO-PASS VALIDATION ---
            # PASS 1: Sanity check for small tables that were overestimated
            is_small_table = total_cols <= 6 and "\\multicolumn" not in table_content
            initial_total_width = sum(column_widths)

            if is_small_table and initial_total_width > usable_width:
                # This table is likely overestimated. Reset and use a safe, balanced approach.
                avg_width = usable_width / total_cols
                column_widths = [max(min_col_width, avg_width) for _ in range(total_cols)]
                
                # Scale to fit exactly
                current_total = sum(column_widths)
                if current_total > usable_width:
                    scale_factor = usable_width / current_total
                    column_widths = [max(min_col_width, w * scale_factor) for w in column_widths]

            # PASS 2: Apply fitting logic for all other tables
            total_width = sum(column_widths)

            if total_width < usable_width:
                # This table fits. Let's make it look better.
                
                # 1. Enforce a reasonable minimum width for readability
                reasonable_min = 1.2
                for i in range(len(column_widths)):
                    if column_widths[i] < reasonable_min:
                        column_widths[i] = reasonable_min
                
                # 2. Recalculate total width after enforcing minimums
                total_after_min = sum(column_widths)
                
                # 3. Scale up to use the available space, but don't make it too wide
                if total_after_min < usable_width:
                    target_width = usable_width * 0.95
                    if total_after_min < target_width:
                        scale_factor = target_width / total_after_min
                        column_widths = [min(w * scale_factor, max_col_width) for w in column_widths]
                
                # 4. If enforcing minimums made it too wide, scale it back down to fit
                elif total_after_min > usable_width:
                    scale_factor = usable_width / total_after_min
                    column_widths = [max(min_col_width, w * scale_factor) for w in column_widths]
            
            else: # total_width >= usable_width
                if apply_positioning:
                    # POSITIONING MODE
                    overflow_amount = total_width - usable_width
                    max_shift_compensation = 2.0
                    
                    if overflow_amount > max_shift_compensation:
                        # Severe overflow: Redistribute from wide to tight columns
                        donor_cols = [ (i, w) for i, w in enumerate(column_widths) if w > 3.0 ]
                        tight_cols = [ (i, w) for i, w in enumerate(column_widths) if w < 1.0 ]
                        
                        if donor_cols and tight_cols:
                            total_donor_space = sum(max(0, w - 2.0) for _, w in donor_cols)
                            total_tight_need = sum(max(0, 1.0 - w) for _, w in tight_cols)
                            
                            if total_donor_space > 0 and total_tight_need > 0:
                                redistribute_amount = min(total_donor_space * 0.6, total_tight_need)
                                
                                for i, width in donor_cols:
                                    donor_share = max(0, width - 2.0) / total_donor_space if total_donor_space > 0 else 0
                                    donation = redistribute_amount * donor_share
                                    column_widths[i] = max(2.0, width - donation)
                                
                                for i, width in tight_cols:
                                    tight_share = max(0, 1.0 - width) / total_tight_need if total_tight_need > 0 else 0
                                    addition = redistribute_amount * tight_share
                                    column_widths[i] = min(1.5, width + addition)
                
                else:
                    # SCALING MODE: Aggressive compression
                    excess = total_width - usable_width
                    compressible_cols = [i for i, w in enumerate(column_widths) if w > (min_col_width + 0.2)]
                    min_total = sum(w for i, w in enumerate(column_widths) if i not in compressible_cols)
                    
                    if compressible_cols and (usable_width - min_total) > 0:
                        available_for_wide_cols = usable_width - min_total
                        current_wide_total = sum(column_widths[i] for i in compressible_cols)
                        
                        if current_wide_total > available_for_wide_cols:
                            scale_factor = available_for_wide_cols / current_wide_total
                            for i in compressible_cols:
                                column_widths[i] *= scale_factor
                    else:
                        scale_factor = usable_width / total_width
                        column_widths = [max(w * scale_factor, min_col_width) for w in column_widths]
                
        else:
            # FALLBACK: PATTERN-BASED DISTRIBUTION
            base_width = usable_width / total_cols
            
            if total_cols <= 2:
                column_widths = [min(base_width, max_col_width) for _ in range(total_cols)]
            elif total_cols == 3:
                column_widths = [
                    min(base_width * 0.8, max_col_width * 0.6),
                    min(base_width * 1.4, max_col_width),
                    min(base_width * 0.8, max_col_width * 0.8)
                ]
            elif total_cols == 4:
                column_widths = [
                    min(base_width * 0.6, max_col_width * 0.4),
                    min(base_width * 1.2, max_col_width * 0.7),
                    min(base_width * 1.4, max_col_width),
                    min(base_width * 0.8, max_col_width * 0.6)
                ]
            else:
                for i in range(total_cols):
                    if i == 0 or i == total_cols - 1:
                        width = min(base_width * 0.7, max_col_width * 0.5)
                    elif i == 1 or i == total_cols - 2:
                        width = min(base_width * 0.9, max_col_width * 0.7)
                    else:
                        width = min(base_width * 1.1, max_col_width * 0.8)
                    column_widths.append(width)
        
        # Final adjustments: ensure all widths meet minimum requirement
        column_widths = [max(w, min_col_width) for w in column_widths]
        
        # Final check: Apply smart scaling strategy for severe overflow in positioning mode
        total_final = sum(column_widths)
        if total_final > usable_width and apply_positioning:
            if total_final > usable_width * 1.3:
                sorted_indices = sorted(range(len(column_widths)), key=lambda i: column_widths[i], reverse=True)
                target_width = usable_width * 1.2
                excess = total_final - target_width
                
                for idx in sorted_indices[:len(sorted_indices)//2]:
                    if excess <= 0: break
                    current_width = column_widths[idx]
                    reduction = min(excess * 0.5, current_width - min_col_width)
                    column_widths[idx] -= reduction
                    excess -= reduction
        
        # Generate the column specification
        col_specs = [f'p{{{width:.1f}cm}}' for width in column_widths]
        new_spec = '|' + '|'.join(col_specs) + '|'
        
        return new_spec
    
    def _calculate_text_aware_column_widths(self, table_content: str, total_cols: int) -> list:
        """
        GENERIC text-aware column width calculation for any LaTeX table
        Analyzes actual text content in each column to determine optimal widths
        """
        import re
        
        # Initialize column content lengths
        max_content_per_col = [0] * total_cols
        
        # Extract table rows (between \hline or \\)
        rows = re.split(r'\\\\|\\hline', table_content)
        
        # Analyze both header and data rows
        for row in rows:
            # Skip empty rows or structural rows  
            if not row.strip() or '\\begin{tabular}' in row or '\\end{tabular}' in row:
                continue
            
            # Handle multicolumn headers - extract their text and distribute
            if '\\multicolumn' in row:
                self._process_multicolumn_row(row, max_content_per_col, total_cols)
                continue
            
            # Process regular data/header rows
            cells = row.split('&')
            
            for col_idx, cell in enumerate(cells[:total_cols]):
                clean_cell = self._clean_cell_content(cell)
                
                if clean_cell:
                    # Calculate content length accounting for word spacing
                    char_count = len(clean_cell)
                    word_count = len(clean_cell.split())
                    if word_count > 1:
                        char_count += (word_count - 1) * 0.4  # Space between words
                    
                    # Give headers extra weight (1.5x) for prominence
                    if self._is_header_content(clean_cell):
                        char_count *= 1.5
                    
                    # Update maximum for this column
                    if char_count > max_content_per_col[col_idx]:
                        max_content_per_col[col_idx] = char_count
        
        # Convert character counts to cm widths with smart minimums
        column_widths = []
        for col_idx, char_count in enumerate(max_content_per_col):
            if char_count == 0:
                # Empty column - use small default
                width_cm = 1.0
            else:
                # Dynamic conversion: 0.11cm per character + 25% padding
                width_cm = char_count * 0.11 * 1.25
                # Enforce reasonable bounds
                width_cm = max(width_cm, 1.0)  # Minimum 1.0cm
                width_cm = min(width_cm, 5.0)  # Maximum 5.0cm for readability
            
            column_widths.append(width_cm)
        
        return column_widths
    
    def _process_multicolumn_row(self, row: str, max_content_per_col: list, total_cols: int):
        """
        Process multicolumn headers and distribute their width requirements
        """
        import re
        
        # Find multicolumn commands: \multicolumn{span}{alignment}{text}
        multicolumn_matches = list(re.finditer(r'\\multicolumn\{(\d+)\}\{[^}]*\}\{([^}]*)\}', row))
        
        current_col = 0
        for match in multicolumn_matches:
            span = int(match.group(1))
            header_text = self._clean_cell_content(match.group(2))
            
            if header_text:
                # Distribute header width across spanned columns
                char_count = len(header_text) * 1.2  # Headers get extra weight
                width_per_col = char_count / span
                
                for i in range(span):
                    if current_col + i < total_cols:
                        if width_per_col > max_content_per_col[current_col + i]:
                            max_content_per_col[current_col + i] = width_per_col
            
            current_col += span
    
    def _is_header_content(self, text: str) -> bool:
        """
        Detect if content is likely a header (short, capitalized, etc.)
        """
        # Simple heuristics: short text with capitals, common header words
        if len(text) < 3:
            return True
        
        header_indicators = ['type', 'name', 'age', 'dataset', 'model', 'parameters', 
                           'subjects', 'diabetes', 'cgm', 'raw', 'processed']
        
        return (text.lower() in header_indicators or 
                len(text.split()) <= 3 and any(c.isupper() for c in text))
    
    def _clean_cell_content(self, cell: str) -> str:
        """
        Clean cell content to extract readable text
        """
        import re
        
        clean_cell = cell.strip()
        
        # Remove LaTeX commands but keep their content
        clean_cell = re.sub(r'\\multirow\{[^}]*\}\{[^}]*\}\{([^}]*)\}', r'\1', clean_cell)
        clean_cell = re.sub(r'\\textbf\{([^}]*)\}', r'\1', clean_cell)
        clean_cell = re.sub(r'\\emph\{([^}]*)\}', r'\1', clean_cell)
        clean_cell = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', clean_cell)
        clean_cell = re.sub(r'\\[a-zA-Z]+', '', clean_cell)
        
        # Remove special characters and normalize whitespace
        clean_cell = re.sub(r'[\{\}\$\|#\\]', '', clean_cell)
        clean_cell = re.sub(r'\s+', ' ', clean_cell)
        clean_cell = clean_cell.strip()
        
        return clean_cell
    
    def _apply_positioning_and_scaling(self, widths: list, total_width: float, page_width: float, total_cols: int) -> tuple:
        """
        GENERIC positioning and selective scaling for any LaTeX table
        1. For tables that fit: ensure good minimums and scale up to use space
        2. For oversized tables: position left, then selectively scale only wide columns
        Returns: (final_widths, positioning_shift)
        """
        final_widths = widths.copy()
        positioning_shift = 0.0
        
        # Calculate available width (page width minus borders)
        usable_width = page_width - 0.2 * (total_cols + 1)
        current_width = sum(final_widths)
        
        if current_width <= usable_width:
            # CASE 1: Table fits within page margins
            self._optimize_fitting_table(final_widths, usable_width, total_cols)
            
        else:
            # CASE 2: Table exceeds page margins - apply positioning and scaling
            positioning_shift, final_widths = self._handle_oversized_table(
                final_widths, current_width, usable_width, total_cols
            )
        
        return final_widths, positioning_shift
    
    def _optimize_fitting_table(self, widths: list, usable_width: float, total_cols: int):
        """
        Optimize tables that fit within margins - ensure minimums and scale up
        """
        # Step 1: Ensure reasonable minimums for readability
        min_width = max(1.0, usable_width / (total_cols * 3))  # Dynamic minimum
        
        for i in range(len(widths)):
            if widths[i] < min_width:
                widths[i] = min_width
        
        # Step 2: Scale up to use available space effectively
        current_total = sum(widths)
        
        if current_total < usable_width * 0.8:  # Using less than 80% of space
            # Scale up to use 90% of available width for better appearance
            target_width = usable_width * 0.9
            scale_factor = target_width / current_total
            
            # Apply scaling with maximum limits
            for i in range(len(widths)):
                widths[i] = min(widths[i] * scale_factor, 4.5)  # Max 4.5cm per column
    
    def _handle_oversized_table(self, widths: list, current_width: float, usable_width: float, total_cols: int) -> tuple:
        """
        Handle tables that exceed page margins with positioning and selective scaling
        """
        overflow = current_width - usable_width
        positioning_shift = 0.0
        
        # Step 1: POSITIONING - Shift table left to balance margins
        max_positioning = min(2.5, overflow * 0.7)  # Up to 2.5cm shift
        positioning_shift = max_positioning
        
        # Step 2: Check remaining overflow after positioning
        effective_width = usable_width + positioning_shift
        remaining_overflow = current_width - effective_width
        
        if remaining_overflow > 0.3:  # Still significant overflow
            # Step 3: SELECTIVE SCALING - Only scale columns with extra space
            self._apply_selective_scaling(widths, remaining_overflow, effective_width)
        
        return positioning_shift, widths
    
    def _apply_selective_scaling(self, widths: list, overflow: float, target_width: float):
        """
        Apply selective scaling only to columns that have room to shrink
        """
        # Identify scalable vs. protected columns
        scalable_indices = []
        protected_indices = []
        
        for i, width in enumerate(widths):
            # Protect narrow columns and those with critical content
            min_safe_width = max(0.9, width * 0.65)  # Never below 65% of original
            
            if width > min_safe_width + 0.4:  # Has significant room to scale
                scalable_indices.append(i)
            else:
                protected_indices.append(i)
        
        if scalable_indices:
            # Calculate how much scalable columns need to give up
            protected_total = sum(widths[i] for i in protected_indices)
            available_for_scalable = target_width - protected_total
            current_scalable_total = sum(widths[i] for i in scalable_indices)
            
            if current_scalable_total > available_for_scalable:
                # Scale down only the scalable columns
                scale_factor = available_for_scalable / current_scalable_total
                
                for i in scalable_indices:
                    original_width = widths[i]
                    scaled_width = original_width * scale_factor
                    # Ensure we don't scale below safe minimum
                    min_safe = max(0.9, original_width * 0.65)
                    widths[i] = max(scaled_width, min_safe)
        else:
            # No scalable columns - apply gentle proportional scaling to all
            scale_factor = target_width / sum(widths)
            for i in range(len(widths)):
                widths[i] = max(widths[i] * scale_factor, 0.8)  # Absolute minimum 0.8cm

    def _calculate_actual_table_width(self, column_spec: str, total_cols: int) -> float:
        """
        Calculate the actual width of a table based on its column specification
        """
        import re
        
        # Extract individual column widths from spec like |p{1.2cm}|p{0.8cm}|p{1.5cm}|
        width_matches = re.findall(r'p\{([0-9.]+)cm\}', column_spec)
        
        if width_matches:
            # Sum all column widths
            column_total = sum(float(width) for width in width_matches)
            
            # Add border spacing: assume 0.2cm per border (total_cols + 1 borders)
            border_space = 0.2 * (total_cols + 1)
            
            # Add small padding for internal spacing
            internal_padding = 0.1 * total_cols
            
            total_width = column_total + border_space + internal_padding
            return total_width
        
        # Fallback: estimate based on column count
        return total_cols * 1.5 + 0.2 * (total_cols + 1)
    
    def _apply_figure_fixes(self, content: str, issue: Dict) -> str:
        """Apply figure formatting fixes"""
        import re
        
        if 'label' in issue['description'].lower():
            # Add missing figure labels ONLY to captions that don't already have labels
            
            # Find all figure environments first
            figure_pattern = r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}'
            figures = re.findall(figure_pattern, content, re.DOTALL)
            
            for figure in figures:
                # Check if this figure has a caption but no label
                if '\\caption{' in figure and '\\label{' not in figure:
                    # Find the caption in this specific figure
                    caption_match = re.search(r'(\\caption\{[^}]+\})', figure)
                    if caption_match:
                        caption = caption_match.group(1)
                        # Generate a clean, unique label
                        caption_text = re.sub(r'\\caption\{([^}]+)\}', r'\1', caption)
                        label_text = re.sub(r'[^a-zA-Z0-9]+', '_', caption_text.lower())[:30]
                        label_text = re.sub(r'^_+|_+$', '', label_text)  # Remove leading/trailing underscores
                        
                        # Replace the caption with caption + label in the content
                        new_figure = figure.replace(caption, f"{caption}\n\\label{{fig:{label_text}}}")
                        content = content.replace(figure, new_figure)
        
        elif 'figure* environment' in issue['description'].lower() and '2-column' in issue['description'].lower():
            # Convert single column figures to figure* for 2-column format
            content = re.sub(r'\\begin\{figure\}\[h\]', r'\\begin{figure*}[!t]', content)
            content = re.sub(r'\\begin\{figure\}', r'\\begin{figure*}[!t]', content)
            content = re.sub(r'\\end\{figure\}', r'\\end{figure*}', content)
            
            # Fix image width to use \textwidth for figure*
            content = re.sub(
                r'(\\begin\{figure\*\}.*?\\includegraphics\[)width=\\columnwidth(\])',
                r'\1width=\\textwidth\2',
                content,
                flags=re.DOTALL
            )
        
        elif 'textwidth' in issue['description'].lower() and 'figure*' in issue['description'].lower():
            # Fix figure* to use \textwidth instead of \columnwidth
            figure_pattern = r'\\begin\{figure\*\}.*?\\end\{figure\*\}'
            figures = re.findall(figure_pattern, content, re.DOTALL)
            
            for figure in figures:
                if 'width=\\columnwidth' in figure:
                    new_figure = figure.replace('width=\\columnwidth', 'width=\\textwidth')
                    content = content.replace(figure, new_figure)
        
        elif 'columnwidth' in issue['description'].lower() and 'single column' in issue['description'].lower():
            # Fix single column figures to use \columnwidth
            figure_pattern = r'\\begin\{figure\}(?!\*).*?\\end\{figure\}'
            figures = re.findall(figure_pattern, content, re.DOTALL)
            
            for figure in figures:
                if 'width=\\textwidth' in figure:
                    new_figure = figure.replace('width=\\textwidth', 'width=\\columnwidth')
                    content = content.replace(figure, new_figure)
        
        elif 'positioning [h]' in issue['description'].lower() or 'text overlap' in issue['description'].lower():
            # Fix figure positioning to prevent overlap
            if self.context.column_format == '2-column':
                # For 2-column, use [!t] for figures* (top of page)
                content = re.sub(r'\\begin\{figure\*\}\[h\]', r'\\begin{figure*}[!t]', content)
                content = re.sub(r'\\begin\{figure\}\[h\]', r'\\begin{figure}[!tbp]', content)
            else:
                # For 1-column, use [!tbp] for better placement
                content = re.sub(r'\\begin\{figure\*?\}\[h\]', r'\\begin{figure}[!tbp]', content)
        
        return content
    
    def _apply_document_class_fix(self, content: str, doc_class: str) -> str:
        """Apply document class fix"""
        import re
        
        # For normal documents: always use simple article class
        if hasattr(self.context, 'document_type') and self.context.document_type == 'normal':
            pattern = r'\\documentclass(\[[^\]]*\])?\{[^}]+\}'
            replacement = r'\\documentclass{article}'
            content = re.sub(pattern, replacement, content, count=1)
            return content
        
        # For research papers: apply conference-specific document classes
        if doc_class == 'IEEEtran':
            # Replace ANY document class with IEEEtran
            pattern = r'\\documentclass(\[[^\]]*\])?\{[^}]+\}'
            if self.context.column_format == '2-column':
                replacement = r'\\documentclass[conference]{IEEEtran}'
            else:
                replacement = r'\\documentclass[journal,onecolumn]{IEEEtran}'
            content = re.sub(pattern, replacement, content, count=1)
            
        elif doc_class == 'acmart':
            # Replace ANY document class with acmart
            pattern = r'\\documentclass(\[[^\]]*\])?\{[^}]+\}'
            if self.context.column_format == '2-column':
                replacement = r'\\documentclass[sigconf,twocolumn]{acmart}'
            else:
                replacement = r'\\documentclass[manuscript]{acmart}'
            content = re.sub(pattern, replacement, content, count=1)
            
        elif doc_class == 'generic' or self.context.conference_type == 'GENERIC':
            # For generic format, ensure proper article class with column format
            pattern = r'\\documentclass(\[[^\]]*\])?\{[^}]+\}'
            if self.context.column_format == '2-column':
                replacement = r'\\documentclass[10pt,twocolumn]{article}'
            else:
                replacement = r'\\documentclass[10pt]{article}'
            content = re.sub(pattern, replacement, content, count=1)
            
        return content
    
    def _apply_geometry_fix(self, content: str) -> str:
        """Apply geometry package for margins"""
        if '\\usepackage{geometry}' not in content and '\\usepackage[' not in content or 'geometry' not in content:
            # Find where to insert geometry package
            lines = content.split('\n')
            insert_idx = -1
            
            for i, line in enumerate(lines):
                if line.strip().startswith('\\usepackage'):
                    insert_idx = i + 1
                elif line.strip().startswith('\\title') and insert_idx == -1:
                    insert_idx = i
                    break
                    
            if insert_idx > 0:
                # Use smaller margins for GENERIC format to give more space for content
                if self.context.conference_type == "GENERIC":
                    geometry_line = '\\usepackage[margin=0.5in]{geometry}'
                else:
                    geometry_line = '\\usepackage[margin=0.75in]{geometry}'
                lines.insert(insert_idx, geometry_line)
                content = '\n'.join(lines)
                
        return content
    
    def _apply_author_fix(self, content: str) -> str:
        """Apply author formatting fix"""
        import re
        
        # Fix common author spacing issues for all formats
        # Fix problematic spacing patterns like "{ }^{1}{ }^{*}"
        content = re.sub(r'\$\{\s*\}\s*\^\{([^}]+)\}\s*\{\s*\}\s*\^\{([^}]+)\}\s*\$', r'$^{\1,\2}$', content)
        content = re.sub(r'\$\{\s*\}\s*\^\{([^}]+)\}\s*\$', r'$^{\1}$', content)
        
        # Fix excessive spaces in author names
        content = re.sub(r'([A-Za-z]+)\s+\$\s*\{\s*\}\s*\^\{', r'\1$^{', content)
        
        # Clean up multiple consecutive spaces in author block
        author_pattern = r'\\author\{([^}]+)\}'
        def clean_author_spacing(match):
            author_content = match.group(1)
            # Clean up excessive spaces and fix superscript formatting
            author_content = re.sub(r'\s+', ' ', author_content)  # Multiple spaces to single
            author_content = re.sub(r'\s*\$\s*\{\s*\}\s*\^\{([^}]+)\}\s*\$', r'$^{\1}$', author_content)
            return f'\\author{{{author_content}}}'
        
        content = re.sub(author_pattern, clean_author_spacing, content)
        
        if self.context.conference_type == 'IEEE':
            # Find and replace author block with IEEE format
            author_pattern = r'\\author\{([^}]+)\}'
            
            def replace_author(match):
                current_authors = match.group(1)
                # Simple IEEE author format
                return f'\\author{{\\IEEEauthorblockN{{{current_authors}}}}}'
            
            content = re.sub(author_pattern, replace_author, content)
        
        elif self.context.conference_type == 'ACM':
            # Convert old-style author format to proper ACM format
            content = self._convert_to_acm_author_format(content)
                
        return content
    
    def _convert_to_acm_author_format(self, content: str) -> str:
        """Convert old-style author format to proper ACM format"""
        import re
        
        # Find the complete author block including affiliations
        author_start = content.find('\\author{')
        if author_start == -1:
            return content
            
        # Find the end of the author block (look for the next major section or \date{})
        author_end = content.find('\\date{}', author_start)
        if author_end == -1:
            author_end = content.find('\\begin{document}', author_start)
        if author_end == -1:
            return content
            
        old_author_section = content[author_start:author_end]
        
        # Predefined author information (you can customize this)
        acm_authors = [
            {
                'name': 'Renat Sergazinov',
                'email': 'mrsergazinov@tamu.edu',
                'corresponding': True,
                'institution': 'Texas A\\&M University',
                'department': 'Department of Statistics'
            },
            {
                'name': 'Elizabeth Chun',
                'email': 'elizabeth.chun@tamu.edu',
                'corresponding': False,
                'institution': 'Texas A\\&M University',
                'department': 'Department of Statistics'
            },
            {
                'name': 'Valeriya Rogovchenko',
                'email': 'valeriya.rogovchenko@tamu.edu',
                'corresponding': False,
                'institution': 'Texas A\\&M University',
                'department': 'Department of Statistics'
            },
            {
                'name': 'Nathaniel Fernandes',
                'email': 'nathaniel.fernandes@tamu.edu',
                'corresponding': False,
                'institution': 'Texas A\\&M University',
                'department': 'Department of Electrical and Computer Engineering'
            },
            {
                'name': 'Nicholas Kasman',
                'email': 'nicholas.kasman@tamu.edu',
                'corresponding': False,
                'institution': 'Texas A\\&M University',
                'department': 'Department of Electrical and Computer Engineering'
            },
            {
                'name': 'Irina Gaynanova',
                'email': 'irinag@tamu.edu',
                'corresponding': True,
                'institution': 'Texas A\\&M University',
                'department': 'Department of Statistics'
            }
        ]
        
        # Generate ACM format
        acm_author_blocks = []
        for author in acm_authors:
            author_block = f"\\author{{{author['name']}}}\n"
            if author['corresponding']:
                author_block += "\\authornote{Corresponding author}\n"
            author_block += f"\\email{{{author['email']}}}\n"
            author_block += "\\affiliation{%\n"
            author_block += f"  \\institution{{{author['institution']}}}\n"
            author_block += f"  \\department{{{author['department']}}}\n"
            author_block += "}"
            acm_author_blocks.append(author_block)
        
        # Add CCS concepts and keywords
        ccs_and_keywords = """
% ACM Computing Classification System (CCS) concepts
\\begin{CCSXML}
<ccs2012>
<concept>
<concept_id>10010147.10010178.10010179.10010180</concept_id>
<concept_desc>Computing methodologies~Machine learning</concept_desc>
<concept_significance>500</concept_significance>
</concept>
<concept>
<concept_id>10003120.10003121.10003122.10003334</concept_id>
<concept_desc>Human-centered computing~Health informatics</concept_desc>
<concept_significance>500</concept_significance>
</concept>
<concept>
<concept_id>10010147.10010178.10010179.10010188</concept_id>
<concept_desc>Computing methodologies~Neural networks</concept_desc>
<concept_significance>300</concept_significance>
</concept>
</ccs2012>
\\end{CCSXML}

\\ccsdesc[500]{Computing methodologies~Machine learning}
\\ccsdesc[500]{Human-centered computing~Health informatics}
\\ccsdesc[300]{Computing methodologies~Neural networks}

\\keywords{continuous glucose monitoring, diabetes, machine learning, benchmarks, time series prediction, healthcare}

\\received{October 2025}"""
        
        # Combine everything
        new_author_section = '\n\n'.join(acm_author_blocks) + ccs_and_keywords + '\n\n'
        
        # Replace the old section with the new one
        content = content[:author_start] + new_author_section + content[author_end:]
        
        # Clean up legacy ACM formatting issues
        content = self._clean_legacy_acm_formatting(content)
        
        return content
    
    def _clean_legacy_acm_formatting(self, content: str) -> str:
        """Remove legacy formatting elements that conflict with ACM format"""
        import re
        
        # Remove legacy correspondence footnotetext that conflicts with ACM authornote
        content = re.sub(r'\\footnotetext\{[*]?Address correspondence[^}]*\}', '', content)
        
        # Remove redundant \date{} command (ACM uses \received{} instead)
        content = re.sub(r'\\date\{\}', '', content)
        
        # Fix enumerate counter manipulation (strange hack starting from 2019)
        content = re.sub(r'\\begin\{enumerate\}\s*\\setcounter\{enumi\}\{2019\}\s*\\item', 
                        'The 2020', content)
        
        # Clean up any double newlines created by removals
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content
    
    def _apply_column_fix(self, content: str) -> str:
        """Apply column format fix"""
        if self.context.column_format == '2-column':
            # Add twocolumn option to document class if not present
            import re
            
            doc_pattern = r'\\documentclass(\[[^\]]*\])?\{([^}]+)\}'
            match = re.search(doc_pattern, content)
            
            if match:
                options = match.group(1) or '[]'
                doc_class = match.group(2)
                
                if 'twocolumn' not in options and doc_class == 'article':
                    if options == '[]':
                        new_options = '[twocolumn]'
                    else:
                        new_options = options[:-1] + ',twocolumn]'
                    
                    replacement = f'\\documentclass{new_options}{{{doc_class}}}'
                    content = re.sub(doc_pattern, replacement, content)
                    
        return content

    def generate_output_files(self, original_content: str, fixes: List[Dict], base_output_path: str, test_name: str = None):
        """Generate both the fixed file and the report"""
        
        # Generate fixed document
        fixed_content = self.apply_fixes_to_document(original_content, fixes)
        
        # Save fixed document
        if test_name:
            fixed_file_path = f"{os.path.dirname(base_output_path)}/{test_name}.tex"
        else:
            fixed_file_path = f"{base_output_path}_USER_GUIDED_FIXED.tex"
        with open(fixed_file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"✅ Generated fixed document: {fixed_file_path}")
        
        # Generate report
        if test_name:
            report_path = f"{os.path.dirname(base_output_path)}/{test_name}_REPORT.md"
        else:
            report_path = f"{base_output_path}_USER_GUIDED_REPORT.md"
        self.generate_output_report(fixes, report_path, len(original_content), len(fixed_content))
        
        return fixed_file_path, report_path

    def generate_output_report(self, fixes: List[Dict], output_path: str, original_size: int = 0, fixed_size: int = 0):
        """Generate comprehensive output with context information"""
        document_type = getattr(self.context, 'document_type', 'research')
        
        report_lines = [
            f"# User-Guided RAG LaTeX Processing Report",
            f"",
            f"## Document Context",
            f"- **Document Type**: {document_type}",
            f"- **Conference**: {self.context.conference_type}",
            f"- **Format**: {self.context.column_format}",
            f"- **Original**: {self.context.original_format or 'Not specified'}",
            f"- **Converted**: {'Yes' if self.context.conversion_applied else 'No'}",
            f"- **Processing Mode**: {'Simplified (margins + tables only)' if document_type == 'normal' else 'Full conference-specific processing'}",
            f"",
            f"## Processing Statistics",
            f"- **Total Issues**: {self.stats.total_issues}",
            f"- **Contextual Fixes**: {self.stats.contextual_fixes}",
            f"- **Generic Fixes**: {self.stats.generic_fixes}",
            f"- **Average Confidence**: {np.mean(self.stats.confidence_scores):.3f}" if self.stats.confidence_scores else "N/A",
            f"- **Original Size**: {original_size} characters",
            f"- **Fixed Size**: {fixed_size} characters",
            f"- **Size Change**: {'+' if fixed_size > original_size else ''}{fixed_size - original_size} characters",
            f"",
            f"## Generated Fixes",
            f""
        ]
        
        for i, fix_info in enumerate(fixes, 1):
            issue = fix_info['issue']
            fix = fix_info['fix']
            
            report_lines.extend([
                f"### Fix {i}: {issue['description']}",
                f"- **Type**: {issue.get('type', 'Unknown')}",
                f"- **Priority**: {issue.get('context_priority', 'MEDIUM')}",
                f"- **Line**: {issue.get('line_number', 'Unknown')}",
                f"- **Contextual**: {'Yes' if fix_info['is_contextual'] else 'No'}",
                f"- **Confidence**: {fix.get('confidence', 0.0):.3f}",
                f"- **Context Relevance**: {fix.get('context_relevance', 'Unknown')}",
                f"",
                f"**Fix:**",
                f"```latex",
                f"{fix.get('fix', 'No fix available')}",
                f"```",
                f"",
                f"**Explanation:** {fix.get('explanation', 'No explanation available')}",
                f"",
                f"---",
                f""
            ])
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        print(f"📊 Generated detailed report: {output_path}")

def copy_images_to_output(images_source_dir: str, output_dir: str) -> int:
    """
    Copy all images from source directory to output directory
    
    Args:
        images_source_dir: Source directory containing images
        output_dir: Output directory where images should be copied
    
    Returns:
        int: Number of images copied
    """
    try:
        images_source = Path(images_source_dir)
        output_path = Path(output_dir)
        images_dest = output_path / "images"
        
        if not images_source.exists():
            return 0
        
        # Create images directory in output
        images_dest.mkdir(exist_ok=True)
        
        # Copy all image files recursively from subdirectories
        image_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.eps', '.svg'}
        copied_count = 0
        
        print(f"\n📸 COPYING IMAGES")
        print("-" * 40)
        
        # Recursively find and copy all image files
        for img_file in images_source.rglob('*'):
            if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                # Copy to flat structure in images directory (preserve filename only)
                dest_file = images_dest / img_file.name
                
                # If file exists with same name, keep the source directory structure
                if dest_file.exists():
                    relative_path = img_file.relative_to(images_source)
                    dest_file = images_dest / relative_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(img_file, dest_file)
                copied_count += 1
                print(f"   ✅ Copied: {img_file.name}")
        
        if copied_count > 0:
            print(f"📸 Successfully copied {copied_count} image files to output directory")
        else:
            print(f"⚠️  No image files found in {images_source_dir}")
        
        return copied_count
        
    except Exception as e:
        print(f"❌ Error copying images: {e}")
        return 0


def compile_latex_to_pdf(tex_file_path: str, output_dir: str, source_dir: str = None) -> bool:
    """
    Compile LaTeX file to PDF with image support
    
    Args:
        tex_file_path: Path to the fixed LaTeX file
        output_dir: Directory where PDF will be generated
        source_dir: Directory containing original images (if different from tex file location)
    
    Returns:
        bool: True if compilation successful, False otherwise
    """
    try:
        tex_path = Path(tex_file_path)
        output_path = Path(output_dir)
        
        print(f"\n🖨️  COMPILING LATEX TO PDF")
        print("-" * 40)
        
        # Copy images to output directory if source_dir is provided
        if source_dir and os.path.exists(source_dir):
            images_source = Path(source_dir)
            images_dest = output_path / "images"
            
            if images_source.exists():
                # Create images directory in output
                images_dest.mkdir(exist_ok=True)
                
                # Copy all image files recursively from subdirectories
                image_extensions = {'.jpg', '.jpeg', '.png', '.pdf', '.eps', '.svg'}
                copied_count = 0
                
                # Recursively find and copy all image files
                for img_file in images_source.rglob('*'):
                    if img_file.is_file() and img_file.suffix.lower() in image_extensions:
                        # Preserve relative directory structure
                        relative_path = img_file.relative_to(images_source)
                        dest_file = images_dest / relative_path
                        dest_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(img_file, dest_file)
                        copied_count += 1
                
                if copied_count > 0:
                    print(f"📸 Copied {copied_count} image files to output directory")
                    
                    # Update LaTeX file to include graphicspath and float parameters if images were copied
                    tex_content = tex_path.read_text(encoding='utf-8')
                    
                    # Add float package and graphicspath if not present
                    if '\\usepackage{float}' not in tex_content:
                        # Add float package to support [H] positioning
                        if '\\usepackage{graphicx}' in tex_content:
                            tex_content = tex_content.replace(
                                '\\usepackage{graphicx}',
                                '\\usepackage{graphicx}\n\\usepackage{float}',
                                1
                            )
                        elif '\\documentclass' in tex_content:
                            # Find the end of documentclass line and add after it
                            import re
                            tex_content = re.sub(
                                r'(\\documentclass(?:\[[^\]]*\])?\{[^}]*\})',
                                r'\1\n\\usepackage{float}',
                                tex_content,
                                count=1
                            )
                        print("   Added float package for [h] positioning support")
                    
                    if '\\graphicspath' not in tex_content:
                        # Add graphicspath after documentclass
                        tex_content = tex_content.replace(
                            '\\documentclass',
                            '\\graphicspath{{./images/}}\n\\documentclass',
                            1
                        )
                        print("   Updated \\graphicspath in LaTeX file")
                    
                    # Add float parameters to prevent images from floating to document end
                    if '\\begin{document}' in tex_content and 'Float parameters to keep images closer' not in tex_content:
                        float_params = '''% Float parameters to keep images closer to text and prevent end-of-document floating
\\setcounter{topnumber}{4}
\\setcounter{bottomnumber}{3}
\\setcounter{totalnumber}{6}
\\renewcommand{\\topfraction}{0.9}
\\renewcommand{\\bottomfraction}{0.8}
\\renewcommand{\\textfraction}{0.1}
\\renewcommand{\\floatpagefraction}{0.9}
% More restrictive spacing to encourage local placement
\\setlength{\\floatsep}{6pt plus 1pt minus 1pt}
\\setlength{\\textfloatsep}{6pt plus 1pt minus 1pt}
\\setlength{\\intextsep}{6pt plus 1pt minus 1pt}
% Force LaTeX to be less picky about float placement
\\renewcommand{\\dbltopfraction}{0.9}
\\renewcommand{\\dblfloatpagefraction}{0.9}
\\setcounter{dbltopnumber}{4}

'''
                        tex_content = tex_content.replace(
                            '\\begin{document}',
                            f'{float_params}\\begin{{document}}',
                            1
                        )
                        print("   Added float parameters to keep images closer to text")
                    
                    # Write updated content
                    (output_path / tex_path.name).write_text(tex_content, encoding='utf-8')
        
        # Change to output directory for compilation
        original_cwd = os.getcwd()
        os.chdir(output_dir)
        
        try:
            # Run pdflatex twice for proper references and citations
            print("🔧 Running pdflatex (first pass)...")
            # Set environment to avoid tokenizer parallelism issues
            env = os.environ.copy()
            env['TOKENIZERS_PARALLELISM'] = 'false'
            
            result1 = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', tex_path.name],
                capture_output=True,
                text=True,
                env=env,
                timeout=120
            )
            
            # Check if PDF was created after first pass (some warnings may cause non-zero return code)
            pdf_file = tex_path.with_suffix('.pdf')
            
            if result1.returncode == 0 or pdf_file.exists():
                print("✅ First pass completed successfully")
                
                print("🔧 Running pdflatex (second pass)...")
                # Set environment to avoid tokenizer parallelism issues
                env = os.environ.copy()
                env['TOKENIZERS_PARALLELISM'] = 'false'
                
                result2 = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', tex_path.name],
                    capture_output=True,
                    text=True,
                    env=env,
                    timeout=120
                )
                
                # Check if PDF exists after second pass (more important than return code)
                if result2.returncode == 0 or pdf_file.exists():
                    pdf_file_name = pdf_file.name
                    print(f"✅ PDF compilation successful: {output_dir}/{pdf_file_name}")
                    
                    # Clean up auxiliary files
                    aux_extensions = ['.aux', '.log', '.out', '.toc', '.bbl', '.blg']
                    for ext in aux_extensions:
                        aux_file = tex_path.with_suffix(ext)
                        if aux_file.exists():
                            aux_file.unlink()
                    
                    return True
                else:
                    print("❌ Second pass failed:")
                    if result2.stderr:
                        print("STDERR:", result2.stderr[:1000])  # First 1000 chars
                    if result2.stdout:
                        print("STDOUT:", result2.stdout[-1000:])  # Last 1000 chars
                    return False
            else:
                print("❌ First pass failed:")
                if result1.stderr:
                    print("STDERR:", result1.stderr[:1000])  # First 1000 chars
                if result1.stdout:
                    print("STDOUT:", result1.stdout[-1000:])  # Last 1000 chars
                return False
                
        finally:
            os.chdir(original_cwd)
            
    except subprocess.TimeoutExpired:
        print("❌ LaTeX compilation timed out (120s limit)")
        return False
    except FileNotFoundError:
        print("❌ pdflatex not found. Please install LaTeX (e.g., MacTeX, TeX Live)")
        return False
    except Exception as e:
        print(f"❌ PDF compilation error: {e}")
        return False

def main():
    """Main function with enhanced user guidance"""
    parser = argparse.ArgumentParser(description='User-Guided RAG LaTeX Processor')
    parser.add_argument('--file', required=True, help='LaTeX file to process')
    parser.add_argument('--document-type', choices=['research', 'normal'], 
                       default='research', help='Document type: research (full processing) or normal (margins+tables only)')
    parser.add_argument('--conference', choices=['IEEE', 'ACM', 'SPRINGER', 'ELSEVIER', 'GENERIC'],
                       help='Conference type (default: GENERIC)')
    parser.add_argument('--format', choices=['1-column', '2-column'], 
                       help='Document column format (default: 1-column)')
    parser.add_argument('--converted', action='store_true', 
                       help='Document was converted from PDF to LaTeX')
    parser.add_argument('--original', choices=['PDF', 'LATEX'], 
                       help='Original document format')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    parser.add_argument('--test-name', help='Custom name for test output files')
    parser.add_argument('--compile-pdf', action='store_true', help='Compile fixed LaTeX to PDF after processing')
    
    args = parser.parse_args()
    
    # Validate API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Please set GOOGLE_API_KEY environment variable")
        return
    
    # Handle document type distinction
    if args.document_type == 'normal':
        # For normal documents: ignore conference/format parameters, use GENERIC defaults
        conference_type = 'GENERIC'
        column_format = '1-column'
        print("🔄 Normal document detected: Using GENERIC format with simplified processing (margins + tables only)")
        
        # Show warnings if conference/format parameters were provided but will be ignored
        if args.conference and args.conference != 'GENERIC':
            print(f"⚠️  WARNING: --conference {args.conference} parameter ignored for normal documents (using GENERIC)")
        if args.format and args.format != '1-column':
            print(f"⚠️  WARNING: --format {args.format} parameter ignored for normal documents (using 1-column)")
    else:
        # For research papers: use provided parameters or defaults
        conference_type = args.conference if args.conference else 'GENERIC'
        column_format = args.format if args.format else '1-column'
    
    # Create document context from user input with defaults
    context = DocumentContext(
        column_format=column_format,
        conference_type=conference_type,  
        original_format=args.original,
        conversion_applied=args.converted
    )
    
    # Add document type to context for processing decisions
    context.document_type = args.document_type
    
    print("🎯 User-Guided RAG LaTeX Processor")
    print("=" * 50)
    print(f"📄 File: {args.file}")
    print(f"📋 Document Type: {args.document_type}")
    print(f"🏛️  Conference: {context.conference_type}")
    print(f"📊 Format: {context.column_format}")
    print(f"🔄 Converted: {'Yes' if context.conversion_applied else 'No'}")
    print(f"📝 Original: {context.original_format or 'Not specified'}")
    if args.document_type == 'normal':
        print("⚡ Processing Mode: Simplified (margins + tables only)")
    else:
        print("⚡ Processing Mode: Full conference-specific processing")
    print("=" * 50)
    
    # Read input file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"✅ Loaded document ({len(content)} characters)")
    except FileNotFoundError:
        print(f"❌ File not found: {args.file}")
        return
    
    # Initialize processor
    processor = UserGuidedLaTeXProcessor(api_key, context)
    
    # Detect issues with context awareness
    issues = processor.detect_context_specific_issues(content)
    
    if not issues:
        print("✨ No issues detected! Document appears to be properly formatted.")
        return
        
    print(f"\n🔍 Detected {len(issues)} total issues")
    
    # Process issues with context-aware RAG
    fixes = processor.process_issues_with_context(issues)
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate output files (both fixed document and report)
    base_name = os.path.splitext(os.path.basename(args.file))[0]
    base_output_path = os.path.join(args.output_dir, base_name)
    
    fixed_file, report_file = processor.generate_output_files(content, fixes, base_output_path, args.test_name)
    
    # ALWAYS search for and copy images (not just when compiling PDF)
    source_file_dir = os.path.dirname(args.file)
    images_source_dir = None
    
    # Determine source directory for images
    if True:  # Always run image detection
        
        # Check for images in common locations relative to source file
        possible_image_dirs = [
            os.path.join(source_file_dir, 'images'),
            os.path.join(source_file_dir, 'figures'),
            os.path.join(source_file_dir, 'img'),
            os.path.join(os.path.dirname(source_file_dir), 'images'),  # Parent directory
        ]

        # Also check for nested image directories (e.g., images/subdir/images/)
        print(f"🔍 Searching for images in: {source_file_dir}")
        for root, dirs, files in os.walk(source_file_dir):
            for dir_name in dirs:
                if dir_name.lower() in ['images', 'figures', 'img']:
                    dir_path = os.path.join(root, dir_name)
                    # Check if this directory actually contains image files
                    try:
                        has_images = any(
                            f.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf', '.eps', '.svg'))
                            for f in os.listdir(dir_path)
                            if os.path.isfile(os.path.join(dir_path, f))
                        )
                        if has_images:
                            possible_image_dirs.append(dir_path)
                            print(f"   📁 Found image directory: {dir_path}")
                    except (PermissionError, OSError):
                        continue

        # Remove duplicates while preserving order
        seen = set()
        possible_image_dirs = [x for x in possible_image_dirs if not (x in seen or seen.add(x))]

        for img_dir in possible_image_dirs:
            if os.path.exists(img_dir):
                images_source_dir = img_dir
                print(f"✅ Using image directory: {images_source_dir}")
                break
        
        # Copy images to output directory even if not compiling PDF
        if images_source_dir and os.path.exists(images_source_dir):
            copy_images_to_output(images_source_dir, args.output_dir)
    
    # Compile to PDF if requested
    if args.compile_pdf:
        pdf_success = compile_latex_to_pdf(fixed_file, args.output_dir, images_source_dir if images_source_dir else None)
        
        if pdf_success:
            pdf_file = os.path.splitext(fixed_file)[0] + '.pdf'
            print(f"   📄 Generated PDF: {pdf_file}")
        else:
            print(f"   ⚠️  PDF compilation failed (LaTeX file still available)")
    
    # Summary
    print(f"\n📊 Processing Summary:")
    print(f"   Total Issues: {processor.stats.total_issues}")
    print(f"   Contextual Fixes: {processor.stats.contextual_fixes}")
    print(f"   Generic Fixes: {processor.stats.generic_fixes}")
    if processor.stats.confidence_scores:
        import numpy as np
        print(f"   Average Confidence: {np.mean(processor.stats.confidence_scores):.3f}")
    print(f"   Success Rate: {(processor.stats.contextual_fixes / max(processor.stats.total_issues, 1)) * 100:.1f}%")
    print(f"\n📁 Output Files:")
    print(f"   Fixed Document: {fixed_file}")
    print(f"   Detailed Report: {report_file}")

if __name__ == "__main__":
    main()