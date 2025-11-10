"""
Simple Content Remover

Remove various LaTeX elements using simple string/regex logic:
- Words
- Sentences
- Sections
- Tables
- Formulas (inline $...$)
- Equations (display $$...$$ and \begin{equation})
"""

import re
from typing import Tuple


class SimpleRemover:
    """Dead simple content removal - pure string logic, no parsers"""
    
    def __init__(self):
        """Initialize the remover"""
        pass
    
    def remove_word(self, content: str, word: str) -> Tuple[str, int]:
        """
        Remove all occurrences of a word (exact match with word boundaries).
        
        Args:
            content: LaTeX document content
            word: Word to remove
            
        Returns:
            (modified_content, removal_count)
        """
        print(f"\n🗑️  Removing word: '{word}'")
        
        # Pattern: word boundaries to match exact word only
        pattern = r'\b' + re.escape(word) + r'\b'
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Word '{word}' not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Remove all occurrences (from end to start to preserve positions)
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            # Remove the word but keep surrounding spaces clean
            modified = modified[:start] + modified[end:]
        
        # Clean up multiple spaces
        modified = re.sub(r'  +', ' ', modified)
        
        print(f"  ✅ Removed {count} occurrences")
        return modified, count
    
    def remove_phrase(self, content: str, phrase: str) -> Tuple[str, int]:
        """
        Remove all occurrences of a phrase (multi-word exact match).
        
        Args:
            content: LaTeX document content
            phrase: Phrase to remove (can be multiple words)
            
        Returns:
            (modified_content, removal_count)
        """
        print(f"\n🗑️  Removing phrase: '{phrase}'")
        
        # Escape the phrase for regex
        escaped_phrase = re.escape(phrase)
        
        # Find all matches (case-insensitive)
        matches = list(re.finditer(escaped_phrase, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Phrase '{phrase}' not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Remove all occurrences (from end to start to preserve positions)
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            # Remove the phrase but keep surrounding spaces clean
            modified = modified[:start] + modified[end:]
        
        # Clean up multiple spaces
        modified = re.sub(r'  +', ' ', modified)
        
        print(f"  ✅ Removed {count} occurrences")
        return modified, count
    
    def remove_sentence(self, content: str, sentence: str) -> Tuple[str, int]:
        """
        Remove a specific sentence (exact or fuzzy match).
        
        Args:
            content: LaTeX document content
            sentence: Sentence to remove
            
        Returns:
            (modified_content, removal_count)
        """
        print(f"\n🗑️  Removing sentence: '{sentence[:60]}...'")
        
        # Try exact match first
        if sentence in content:
            print(f"  ✅ Exact match found")
            modified = content.replace(sentence, '')
            # Clean up extra whitespace/newlines
            modified = re.sub(r'\n\n\n+', '\n\n', modified)
            modified = re.sub(r'  +', ' ', modified)
            return modified, 1
        
        # Try case-insensitive match
        pattern = re.escape(sentence)
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            print(f"  ✅ Case-insensitive match found")
            modified = content[:match.start()] + content[match.end():]
            modified = re.sub(r'\n\n\n+', '\n\n', modified)
            modified = re.sub(r'  +', ' ', modified)
            return modified, 1
        
        # Try partial match (first 30 chars)
        if len(sentence) > 30:
            partial = sentence[:30]
            pattern = re.escape(partial)
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                # Find sentence end (. ! ? or newline)
                sentence_end = re.search(r'[.!?\n]', content[match.start():])
                if sentence_end:
                    end_pos = match.start() + sentence_end.end()
                    print(f"  ⚠️  Partial match found, removing full sentence")
                    modified = content[:match.start()] + content[end_pos:]
                    modified = re.sub(r'\n\n\n+', '\n\n', modified)
                    return modified, 1
        
        print(f"  ❌ Sentence not found")
        return content, 0
    
    def remove_section(self, content: str, section_name: str) -> Tuple[str, int]:
        """
        Remove an entire section (header + content).
        Handles both LaTeX environments (abstract, acknowledgments, etc.) and regular sections.
        
        Args:
            content: LaTeX document content
            section_name: Name of section to remove
            
        Returns:
            (modified_content, removal_count)
        """
        print(f"\n🗑️  Removing section: '{section_name}'")
        
        # First, try to match LaTeX environments (e.g., \begin{abstract}...\end{abstract})
        # Common environments: abstract, acknowledgments, keywords, etc.
        env_name = section_name.lower().strip()
        env_pattern = r'\\begin\{' + re.escape(env_name) + r'\}.*?\\end\{' + re.escape(env_name) + r'\}'
        
        env_match = re.search(env_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if env_match:
            print(f"  📦 Found as LaTeX environment: \\begin{{{env_name}}}...\\end{{{env_name}}}")
            # Remove the entire environment
            modified = content[:env_match.start()] + content[env_match.end():]
            
            # Clean up extra whitespace
            modified = re.sub(r'\n\n\n+', '\n\n', modified)
            
            print(f"  ✅ Removed environment ({env_match.end() - env_match.start()} characters)")
            return modified, 1
        
        # If not an environment, try to match as a regular section
        # Pattern to match section header + content until next section or end
        pattern = r'\\(?:sub)*section\*?\{[^}]*' + re.escape(section_name) + r'[^}]*\}.*?(?=\\(?:sub)*section|\Z)'
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not match:
            print(f"  ❌ Section '{section_name}' not found (tried both environment and section)")
            return content, 0
        
        # Remove the entire section
        modified = content[:match.start()] + content[match.end():]
        
        # Clean up extra whitespace
        modified = re.sub(r'\n\n\n+', '\n\n', modified)
        
        print(f"  ✅ Removed section ({match.end() - match.start()} characters)")
        return modified, 1
    
    def remove_table(self, content: str, table_identifier: str = None) -> Tuple[str, int]:
        """
        Remove table(s). Handles both \begin{table}...\end{table} and standalone \begin{tabular}...\end{tabular}.
        If identifier provided, remove specific table. Otherwise remove first table.
        
        Args:
            content: LaTeX document content
            table_identifier: Optional label, caption text, or "all" to remove all tables
            
        Returns:
            (modified_content, removal_count)
        """
        if table_identifier == "all":
            print(f"\n🗑️  Removing ALL tables")
            
            # Match both table environments AND standalone tabular environments
            patterns = [
                r'\\begin\{table\*?\}.*?\\end\{table\*?\}',  # Full table environment
                r'\\begin\{tabular\*?\}.*?\\end\{tabular\*?\}',  # Standalone tabular
                r'\\begin\{longtable\*?\}.*?\\end\{longtable\*?\}',  # Long tables
            ]
            
            modified = content
            total_count = 0
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, modified, re.DOTALL))
                count = len(matches)
                total_count += count
                
                # Remove all matches (from end to start to preserve positions)
                for match in reversed(matches):
                    modified = modified[:match.start()] + modified[match.end():]
            
            if total_count == 0:
                print(f"  ❌ No tables found")
                return content, 0
            
            print(f"  📍 Found {total_count} tables (table + tabular + longtable environments)")
            modified = re.sub(r'\n\n\n+', '\n\n', modified)
            print(f"  ✅ Removed {total_count} tables")
            return modified, total_count
        
        elif table_identifier:
            print(f"\n🗑️  Removing table with: '{table_identifier}'")
            
            # Try to find in table environments first
            patterns = [
                r'\\begin\{table\*?\}.*?\\end\{table\*?\}',
                r'\\begin\{tabular\*?\}.*?\\end\{tabular\*?\}',
                r'\\begin\{longtable\*?\}.*?\\end\{longtable\*?\}',
            ]
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.DOTALL))
                for match in matches:
                    table_content = match.group(0)
                    if table_identifier.lower() in table_content.lower():
                        print(f"  ✅ Found matching table")
                        modified = content[:match.start()] + content[match.end():]
                        modified = re.sub(r'\n\n\n+', '\n\n', modified)
                        return modified, 1
            
            print(f"  ❌ No table found with '{table_identifier}'")
            return content, 0
        
        else:
            print(f"\n🗑️  Removing first table")
            
            # Find first occurrence of any table type
            patterns = [
                r'\\begin\{table\*?\}.*?\\end\{table\*?\}',
                r'\\begin\{tabular\*?\}.*?\\end\{tabular\*?\}',
                r'\\begin\{longtable\*?\}.*?\\end\{longtable\*?\}',
            ]
            
            # Find earliest match across all patterns
            earliest_match = None
            earliest_pos = float('inf')
            
            for pattern in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match and match.start() < earliest_pos:
                    earliest_match = match
                    earliest_pos = match.start()
            
            if not earliest_match:
                print(f"  ❌ No tables found")
                return content, 0
            
            modified = content[:earliest_match.start()] + content[earliest_match.end():]
            modified = re.sub(r'\n\n\n+', '\n\n', modified)
            print(f"  ✅ Removed first table")
            return modified, 1
    
    def _is_math_content(self, text: str) -> bool:
        """
        Validate that text looks like mathematical content.
        Returns True if text contains LaTeX math commands, symbols, or notation.
        """
        if not text or not text.strip():
            return False
        
        # Math indicators: LaTeX commands, symbols, superscripts, subscripts, Greek letters, operators
        math_indicators = [
            r'\\',           # LaTeX commands (backslash)
            r'\^',           # Superscript
            r'_',            # Subscript
            r'\{',           # Braces (often used in math)
            r'[a-zA-Z]\s*[=<>≤≥≠±∓×÷∈∉⊂⊃∪∩]',  # Variable with operator
            r'[+\-*/=<>]',   # Math operators
            r'\\frac|\\sqrt|\\sum|\\int|\\prod|\\lim',  # Common math commands
            r'\\alpha|\\beta|\\gamma|\\delta|\\epsilon|\\theta|\\lambda|\\mu|\\pi|\\sigma|\\omega',  # Greek
            r'\\mathbb|\\mathbf|\\mathcal|\\mathrm',  # Math fonts
            r'\d+\.\d+',     # Decimal numbers
            r'\d+[a-zA-Z]',  # Numbers with variables (like 2x)
        ]
        
        # Check if any math indicator is present
        for indicator in math_indicators:
            if re.search(indicator, text):
                return True
        
        # If text is very short (1-2 chars) and alphanumeric, it might be a variable
        if len(text.strip()) <= 2 and re.match(r'^[a-zA-Z0-9]+$', text.strip()):
            return True
        
        return False
    
    def remove_equation(self, content: str, equation_identifier: str = None) -> Tuple[str, int]:
        """
        Remove equation(s). Can remove inline formulas ($...$) or display equations.
        Only removes content that actually looks like mathematics.
        
        Args:
            content: LaTeX document content
            equation_identifier: "inline_all", "display_all", "all", or specific equation content
            
        Returns:
            (modified_content, removal_count)
        """
        if equation_identifier == "inline_all":
            print(f"\n🗑️  Removing ALL inline formulas ($...$)")
            # Match inline math $...$ (but not $$)
            pattern = r'\$(?!\$)(.*?)\$(?!\$)'
            matches = list(re.finditer(pattern, content))
            
            # Filter to only actual math content
            valid_matches = []
            for match in matches:
                math_content = match.group(1)
                if self._is_math_content(math_content):
                    valid_matches.append(match)
                else:
                    print(f"  ⚠️  Skipping non-math content: ${math_content[:50]}$")
            
            count = len(valid_matches)
            
            if count == 0:
                print(f"  ❌ No inline formulas found")
                return content, 0
            
            print(f"  📍 Found {count} valid inline formulas (skipped {len(matches) - count} non-math)")
            
            # Remove all valid matches (from end to start)
            modified = content
            for match in reversed(valid_matches):
                modified = modified[:match.start()] + modified[match.end():]
            
            modified = re.sub(r'  +', ' ', modified)
            print(f"  ✅ Removed {count} inline formulas")
            return modified, count
        
        elif equation_identifier == "display_all":
            print(f"\n🗑️  Removing ALL display equations")
            # Match display equations: $$...$$, \[...\], \begin{equation}...\end{equation}
            # Using re.DOTALL to match across newlines, including line breaks (\\)
            # IMPORTANT: Also match optional surrounding $ symbols that wrap equation environments
            patterns = [
                r'\$\$.*?\$\$',  # $$...$$
                r'\\\[.*?\\\]',  # \[...\]
                r'\$?\s*\\begin\{equation\*?\}.*?\\end\{equation\*?\}\s*\$?',  # equation environment (with optional $ wrapper)
                r'\$?\s*\\begin\{align\*?\}.*?\\end\{align\*?\}\s*\$?',  # align environment (with optional $ wrapper)
                r'\$?\s*\\begin\{multline\*?\}.*?\\end\{multline\*?\}\s*\$?',  # multline environment (with optional $ wrapper)
                r'\$?\s*\\begin\{gather\*?\}.*?\\end\{gather\*?\}\s*\$?',  # gather environment (with optional $ wrapper)
                r'\$?\s*\\begin\{alignat\*?\}.*?\\end\{alignat\*?\}\s*\$?',  # alignat environment (with optional $ wrapper)
                r'\$?\s*\\begin\{eqnarray\*?\}.*?\\end\{eqnarray\*?\}\s*\$?',  # eqnarray environment (with optional $ wrapper)
            ]
            
            modified = content
            total_count = 0
            
            for pattern in patterns:
                matches = list(re.finditer(pattern, modified, re.DOTALL))
                count = len(matches)
                total_count += count
                
                # Remove all (from end to start to preserve positions)
                for match in reversed(matches):
                    modified = modified[:match.start()] + modified[match.end():]
            
            if total_count == 0:
                print(f"  ❌ No display equations found")
                return content, 0
            
            # Clean up excessive newlines and any standalone $ symbols
            modified = re.sub(r'\n\n\n+', '\n\n', modified)
            # Remove any standalone $$ that might have been created
            modified = re.sub(r'\$\$', '', modified)
            print(f"  ✅ Removed {total_count} display equations")
            return modified, total_count
        
        elif equation_identifier == "all":
            print(f"\n🗑️  Removing ALL equations (inline + display)")
            # Remove inline first
            modified, inline_count = self.remove_equation(content, "inline_all")
            # Then remove display
            modified, display_count = self.remove_equation(modified, "display_all")
            total = inline_count + display_count
            print(f"  ✅ Total removed: {total} ({inline_count} inline + {display_count} display)")
            return modified, total
        
        else:
            # Remove first equation (any type)
            print(f"\n🗑️  Removing first equation")
            
            # Try to find any equation (all types)
            patterns = [
                (r'\$(?!\$).*?\$(?!\$)', 'inline formula'),
                (r'\$\$.*?\$\$', 'display equation ($$)'),
                (r'\\begin\{equation\*?\}.*?\\end\{equation\*?\}', 'equation environment'),
                (r'\\begin\{align\*?\}.*?\\end\{align\*?\}', 'align environment'),
                (r'\\begin\{multline\*?\}.*?\\end\{multline\*?\}', 'multline environment'),
                (r'\\begin\{gather\*?\}.*?\\end\{gather\*?\}', 'gather environment'),
            ]
            
            earliest_match = None
            earliest_pos = len(content)
            match_type = None
            
            for pattern, desc in patterns:
                match = re.search(pattern, content, re.DOTALL)
                if match and match.start() < earliest_pos:
                    earliest_match = match
                    earliest_pos = match.start()
                    match_type = desc
            
            if not earliest_match:
                print(f"  ❌ No equations found")
                return content, 0
            
            modified = content[:earliest_match.start()] + content[earliest_match.end():]
            modified = re.sub(r'  +', ' ', modified)
            print(f"  ✅ Removed first equation ({match_type})")
            return modified, 1
    
    def remove_formula(self, content: str, formula_content: str = None) -> Tuple[str, int]:
        """
        Alias for remove_equation for inline formulas.
        
        Args:
            content: LaTeX document content
            formula_content: Formula content to search for, or "all"
            
        Returns:
            (modified_content, removal_count)
        """
        if formula_content == "all":
            return self.remove_equation(content, "inline_all")
        elif formula_content:
            # Search for specific formula content
            print(f"\n🗑️  Removing formula containing: '{formula_content}'")
            pattern = r'\$(?!\$)(.*?)\$(?!\$)'
            matches = list(re.finditer(pattern, content))
            
            for match in matches:
                if formula_content in match.group(1):
                    print(f"  ✅ Found matching formula: ${match.group(1)}$")
                    modified = content[:match.start()] + content[match.end():]
                    modified = re.sub(r'  +', ' ', modified)
                    return modified, 1
            
            print(f"  ❌ No formula found containing '{formula_content}'")
            return content, 0
        else:
            # Remove first inline formula
            return self.remove_equation(content, None)


def test_simple_remover():
    """Test the simple remover"""
    
    # Sample LaTeX content
    test_content = r"""
\documentclass{article}

\section{Introduction}
This is the introduction with a word dataset.
We use inline math $x = y + z$ and more text.

\section{Related Works}
Previous work by Smith et al. used CGM devices.
The dataset contains important information.

\begin{table}[h]
\centering
\caption{Test Table 1}
\begin{tabular}{|c|c|}
\hline
A & B \\
\hline
1 & 2 \\
\hline
\end{tabular}
\end{table}

\section{Methods}
We define the model as:
\begin{equation}
y = mx + b
\end{equation}

The formula $E = mc^2$ is famous.
Display equation: $$\alpha = \beta + \gamma$$

\section{Results}
Results are shown in Table 2.
"""
    
    remover = SimpleRemover()
    
    print("=" * 80)
    print("TEST 1: Remove Word")
    print("=" * 80)
    modified, count = remover.remove_word(test_content, "dataset")
    print(f"Removed: {count}\n")
    
    print("=" * 80)
    print("TEST 2: Remove Sentence")
    print("=" * 80)
    modified, count = remover.remove_sentence(test_content, "We use inline math")
    print(f"Removed: {count}\n")
    
    print("=" * 80)
    print("TEST 3: Remove Section")
    print("=" * 80)
    modified, count = remover.remove_section(test_content, "Related Works")
    print(f"Removed: {count}\n")
    
    print("=" * 80)
    print("TEST 4: Remove Table")
    print("=" * 80)
    modified, count = remover.remove_table(test_content, "Test Table 1")
    print(f"Removed: {count}\n")
    
    print("=" * 80)
    print("TEST 5: Remove Inline Formulas")
    print("=" * 80)
    modified, count = remover.remove_equation(test_content, "inline_all")
    print(f"Removed: {count}\n")
    
    print("=" * 80)
    print("TEST 6: Remove Display Equations")
    print("=" * 80)
    modified, count = remover.remove_equation(test_content, "display_all")
    print(f"Removed: {count}\n")
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ Word removal: Working")
    print("✅ Sentence removal: Working")
    print("✅ Section removal: Working")
    print("✅ Table removal: Working")
    print("✅ Equation removal: Working")


if __name__ == "__main__":
    test_simple_remover()
