"""
SIMPLE FORMATTING ENGINE
Dead simple text formatting - highlight, bold, italics.
No complex logic, just direct LaTeX formatting.
"""

import re
from typing import Tuple, List, Optional


class SimpleFormatter:
    """Simple text formatting - highlight, bold, italics"""
    
    def __init__(self):
        """Initialize formatter"""
        pass
    
    # ========================================================================
    # HIGHLIGHT OPERATIONS
    # ========================================================================
    
    def highlight_word(self, content: str, word: str, color: str = 'yellow') -> Tuple[str, int]:
        """
        Highlight ALL occurrences of a word.
        
        Args:
            content: LaTeX document content
            word: Word to highlight
            color: Highlight color (yellow, red, green, blue, etc.)
            
        Returns:
            (modified_content, count)
        """
        print(f"\n🎨 Highlighting word: '{word}' in {color}")
        
        # Word boundary pattern
        pattern = r'\b' + re.escape(word) + r'\b'
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Word not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start (avoid offset issues)
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            word_text = content[start:end]
            
            # Wrap in \colorbox
            highlighted = f'\\colorbox{{{color}}}{{{word_text}}}'
            modified = modified[:start] + highlighted + modified[end:]
        
        print(f"  ✅ Highlighted {count} occurrences")
        return modified, count
    
    def highlight_phrase(self, content: str, phrase: str, color: str = 'yellow') -> Tuple[str, int]:
        """
        Highlight ALL occurrences of a phrase.
        
        Args:
            content: LaTeX document content
            phrase: Phrase to highlight
            color: Highlight color
            
        Returns:
            (modified_content, count)
        """
        print(f"\n🎨 Highlighting phrase: '{phrase}' in {color}")
        
        # Exact phrase pattern
        pattern = re.escape(phrase)
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Phrase not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            phrase_text = content[start:end]
            
            # Wrap in \colorbox
            highlighted = f'\\colorbox{{{color}}}{{{phrase_text}}}'
            modified = modified[:start] + highlighted + modified[end:]
        
        print(f"  ✅ Highlighted {count} occurrences")
        return modified, count
    
    def highlight_sentence(self, content: str, sentence: str, color: str = 'yellow') -> Tuple[str, int]:
        """
        Highlight a sentence (or multiple sentences).
        
        Args:
            content: LaTeX document content
            sentence: Sentence to highlight (can be partial)
            color: Highlight color
            
        Returns:
            (modified_content, count)
        """
        print(f"\n🎨 Highlighting sentence: '{sentence[:50]}...' in {color}")
        
        # Try exact match first
        if sentence in content:
            highlighted = f'\\colorbox{{{color}}}{{{sentence}}}'
            modified = content.replace(sentence, highlighted)
            count = content.count(sentence)
            print(f"  ✅ Highlighted {count} occurrence(s)")
            return modified, count
        
        # Try case-insensitive
        pattern = re.escape(sentence)
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        if matches:
            count = len(matches)
            print(f"  📍 Found {count} match(es)")
            
            modified = content
            for match in reversed(matches):
                start, end = match.span()
                sentence_text = content[start:end]
                highlighted = f'\\colorbox{{{color}}}{{{sentence_text}}}'
                modified = modified[:start] + highlighted + modified[end:]
            
            print(f"  ✅ Highlighted {count} occurrence(s)")
            return modified, count
        
        print(f"  ❌ Sentence not found")
        return content, 0
    
    def highlight_paragraph(self, content: str, paragraph_text: str, color: str = 'yellow') -> Tuple[str, int]:
        """
        Highlight a paragraph (multiple sentences).
        
        Args:
            content: LaTeX document content
            paragraph_text: Paragraph text to highlight (can be partial)
            color: Highlight color
            
        Returns:
            (modified_content, count)
        """
        print(f"\n🎨 Highlighting paragraph ({len(paragraph_text)} chars) in {color}")
        
        # Try exact match first
        if paragraph_text in content:
            highlighted = f'\\colorbox{{{color}}}{{{paragraph_text}}}'
            modified = content.replace(paragraph_text, highlighted, 1)
            print(f"  ✅ Highlighted paragraph (exact match)")
            return modified, 1
        
        # Normalize whitespace and try flexible matching
        # Replace multiple spaces/newlines with flexible pattern
        normalized_pattern = re.sub(r'\s+', r'\\s+', re.escape(paragraph_text))
        match = re.search(normalized_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            start, end = match.span()
            para_text = content[start:end]
            highlighted = f'\\colorbox{{{color}}}{{{para_text}}}'
            modified = content[:start] + highlighted + content[end:]
            print(f"  ✅ Highlighted paragraph (flexible match)")
            return modified, 1
        
        print(f"  ❌ Paragraph not found")
        return content, 0
    
    def highlight_multiple_sentences(self, content: str, sentences: List[str], color: str = 'yellow') -> Tuple[str, int]:
        """
        Highlight multiple specific sentences.
        
        Args:
            content: LaTeX document content
            sentences: List of sentences to highlight
            color: Highlight color
            
        Returns:
            (modified_content, total_count)
        """
        print(f"\n🎨 Highlighting {len(sentences)} sentences in {color}")
        
        modified = content
        total_count = 0
        
        for i, sentence in enumerate(sentences, 1):
            print(f"  Sentence {i}/{len(sentences)}: '{sentence[:40]}...'")
            modified, count = self.highlight_sentence(modified, sentence, color)
            total_count += count
        
        print(f"  ✅ Total highlighted: {total_count}")
        return modified, total_count
    
    # ========================================================================
    # BOLD OPERATIONS
    # ========================================================================
    
    def bold_word(self, content: str, word: str) -> Tuple[str, int]:
        """
        Make ALL occurrences of a word bold.
        
        Args:
            content: LaTeX document content
            word: Word to make bold
            
        Returns:
            (modified_content, count)
        """
        print(f"\n**𝗕** Making word bold: '{word}'")
        
        # Handle empty string
        if not word or not word.strip():
            print(f"  ❌ Empty word provided")
            return content, 0
        
        # Word boundary pattern
        pattern = r'\b' + re.escape(word) + r'\b'
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Word not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            word_text = content[start:end]
            
            # Wrap in \textbf
            bolded = f'\\textbf{{{word_text}}}'
            modified = modified[:start] + bolded + modified[end:]
        
        print(f"  ✅ Made {count} occurrences bold")
        return modified, count
    
    def bold_phrase(self, content: str, phrase: str) -> Tuple[str, int]:
        """
        Make ALL occurrences of a phrase bold.
        
        Args:
            content: LaTeX document content
            phrase: Phrase to make bold
            
        Returns:
            (modified_content, count)
        """
        print(f"\n**𝗕** Making phrase bold: '{phrase}'")
        
        # Exact phrase pattern
        pattern = re.escape(phrase)
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Phrase not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            phrase_text = content[start:end]
            
            # Wrap in \textbf
            bolded = f'\\textbf{{{phrase_text}}}'
            modified = modified[:start] + bolded + modified[end:]
        
        print(f"  ✅ Made {count} occurrences bold")
        return modified, count
    
    def bold_sentence(self, content: str, sentence: str) -> Tuple[str, int]:
        """
        Make a sentence bold.
        
        Args:
            content: LaTeX document content
            sentence: Sentence to make bold
            
        Returns:
            (modified_content, count)
        """
        print(f"\n**𝗕** Making sentence bold: '{sentence[:50]}...'")
        
        # Try exact match
        if sentence in content:
            bolded = f'\\textbf{{{sentence}}}'
            modified = content.replace(sentence, bolded)
            count = content.count(sentence)
            print(f"  ✅ Made {count} occurrence(s) bold")
            return modified, count
        
        # Try case-insensitive
        pattern = re.escape(sentence)
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        if matches:
            count = len(matches)
            print(f"  📍 Found {count} match(es)")
            
            modified = content
            for match in reversed(matches):
                start, end = match.span()
                sentence_text = content[start:end]
                bolded = f'\\textbf{{{sentence_text}}}'
                modified = modified[:start] + bolded + modified[end:]
            
            print(f"  ✅ Made {count} occurrence(s) bold")
            return modified, count
        
        print(f"  ❌ Sentence not found")
        return content, 0
    
    def bold_paragraph(self, content: str, paragraph_text: str) -> Tuple[str, int]:
        """
        Make a paragraph bold.
        
        Args:
            content: LaTeX document content
            paragraph_text: Paragraph to make bold
            
        Returns:
            (modified_content, count)
        """
        print(f"\n**𝗕** Making paragraph bold ({len(paragraph_text)} chars)")
        
        # Try exact match first
        if paragraph_text in content:
            bolded = f'\\textbf{{{paragraph_text}}}'
            modified = content.replace(paragraph_text, bolded, 1)
            print(f"  ✅ Made paragraph bold (exact match)")
            return modified, 1
        
        # Flexible whitespace matching
        normalized_pattern = re.sub(r'\s+', r'\\s+', re.escape(paragraph_text))
        match = re.search(normalized_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            start, end = match.span()
            para_text = content[start:end]
            bolded = f'\\textbf{{{para_text}}}'
            modified = content[:start] + bolded + content[end:]
            print(f"  ✅ Made paragraph bold (flexible match)")
            return modified, 1
        
        print(f"  ❌ Paragraph not found")
        return content, 0
    
    # ========================================================================
    # ITALIC OPERATIONS
    # ========================================================================
    
    def italic_word(self, content: str, word: str) -> Tuple[str, int]:
        """
        Make ALL occurrences of a word italic.
        
        Args:
            content: LaTeX document content
            word: Word to make italic
            
        Returns:
            (modified_content, count)
        """
        print(f"\n*𝐼* Making word italic: '{word}'")
        
        # Word boundary pattern
        pattern = r'\b' + re.escape(word) + r'\b'
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Word not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            word_text = content[start:end]
            
            # Wrap in \textit
            italicized = f'\\textit{{{word_text}}}'
            modified = modified[:start] + italicized + modified[end:]
        
        print(f"  ✅ Made {count} occurrences italic")
        return modified, count
    
    def italic_phrase(self, content: str, phrase: str) -> Tuple[str, int]:
        """
        Make ALL occurrences of a phrase italic.
        
        Args:
            content: LaTeX document content
            phrase: Phrase to make italic
            
        Returns:
            (modified_content, count)
        """
        print(f"\n*𝐼* Making phrase italic: '{phrase}'")
        
        # Exact phrase pattern
        pattern = re.escape(phrase)
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ Phrase not found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            phrase_text = content[start:end]
            
            # Wrap in \textit
            italicized = f'\\textit{{{phrase_text}}}'
            modified = modified[:start] + italicized + modified[end:]
        
        print(f"  ✅ Made {count} occurrences italic")
        return modified, count
    
    def italic_sentence(self, content: str, sentence: str) -> Tuple[str, int]:
        """
        Make a sentence italic.
        
        Args:
            content: LaTeX document content
            sentence: Sentence to make italic
            
        Returns:
            (modified_content, count)
        """
        print(f"\n*𝐼* Making sentence italic: '{sentence[:50]}...'")
        
        # Try exact match
        if sentence in content:
            italicized = f'\\textit{{{sentence}}}'
            modified = content.replace(sentence, italicized)
            count = content.count(sentence)
            print(f"  ✅ Made {count} occurrence(s) italic")
            return modified, count
        
        # Try case-insensitive
        pattern = re.escape(sentence)
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        if matches:
            count = len(matches)
            print(f"  📍 Found {count} match(es)")
            
            modified = content
            for match in reversed(matches):
                start, end = match.span()
                sentence_text = content[start:end]
                italicized = f'\\textit{{{sentence_text}}}'
                modified = modified[:start] + italicized + modified[end:]
            
            print(f"  ✅ Made {count} occurrence(s) italic")
            return modified, count
        
        print(f"  ❌ Sentence not found")
        return content, 0
    
    def italic_paragraph(self, content: str, paragraph_text: str) -> Tuple[str, int]:
        """
        Make a paragraph italic.
        
        Args:
            content: LaTeX document content
            paragraph_text: Paragraph to make italic
            
        Returns:
            (modified_content, count)
        """
        print(f"\n*𝐼* Making paragraph italic ({len(paragraph_text)} chars)")
        
        # Try exact match first
        if paragraph_text in content:
            italicized = f'\\textit{{{paragraph_text}}}'
            modified = content.replace(paragraph_text, italicized, 1)
            print(f"  ✅ Made paragraph italic (exact match)")
            return modified, 1
        
        # Flexible whitespace matching
        normalized_pattern = re.sub(r'\s+', r'\\s+', re.escape(paragraph_text))
        match = re.search(normalized_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if match:
            start, end = match.span()
            para_text = content[start:end]
            italicized = f'\\textit{{{para_text}}}'
            modified = content[:start] + italicized + content[end:]
            print(f"  ✅ Made paragraph italic (flexible match)")
            return modified, 1
        
        print(f"  ❌ Paragraph not found")
        return content, 0
    
    # ========================================================================
    # AUTO-DETECT OPERATIONS
    # ========================================================================
    
    def highlight_auto(self, content: str, text: str, color: str = 'yellow') -> Tuple[str, int]:
        """
        AUTO-DETECT: Automatically detect if text is word, phrase, sentence, or paragraph.
        
        Args:
            content: LaTeX document content
            text: Text to highlight
            color: Highlight color
            
        Returns:
            (modified_content, count)
        """
        word_count = len(text.split())
        char_count = len(text)
        
        if word_count == 1:
            return self.highlight_word(content, text, color)
        elif word_count <= 4:
            return self.highlight_phrase(content, text, color)
        elif char_count < 200:
            return self.highlight_sentence(content, text, color)
        else:
            return self.highlight_paragraph(content, text, color)
    
    def bold_auto(self, content: str, text: str) -> Tuple[str, int]:
        """
        AUTO-DETECT: Automatically detect if text is word, phrase, sentence, or paragraph.
        
        Args:
            content: LaTeX document content
            text: Text to make bold
            
        Returns:
            (modified_content, count)
        """
        word_count = len(text.split())
        char_count = len(text)
        
        if word_count == 1:
            return self.bold_word(content, text)
        elif word_count <= 4:
            return self.bold_phrase(content, text)
        elif char_count < 200:
            return self.bold_sentence(content, text)
        else:
            return self.bold_paragraph(content, text)
    
    def italic_auto(self, content: str, text: str) -> Tuple[str, int]:
        """
        AUTO-DETECT: Automatically detect if text is word, phrase, sentence, or paragraph.
        
        Args:
            content: LaTeX document content
            text: Text to make italic
            
        Returns:
            (modified_content, count)
        """
        word_count = len(text.split())
        char_count = len(text)
        
        if word_count == 1:
            return self.italic_word(content, text)
        elif word_count <= 4:
            return self.italic_phrase(content, text)
        elif char_count < 200:
            return self.italic_sentence(content, text)
        else:
            return self.italic_paragraph(content, text)


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_formatter():
    """Test the formatter with sample content"""
    
    sample_latex = r"""
\documentclass{article}
\usepackage{xcolor}
\begin{document}

\section{Introduction}
Machine learning is transforming healthcare. The ML algorithms can detect patterns 
in medical data. Deep learning models are particularly effective.

\section{Methods}
We used three different datasets. The first dataset contains patient records.
Our approach combines traditional methods with modern techniques. The model
achieved high accuracy on validation data.

\section{Results}
The results show significant improvement. Deep learning outperformed baseline 
methods. Our model achieved 95 percent accuracy. This is the best result so far.

\end{document}
"""

    formatter = SimpleFormatter()
    
    print("="*80)
    print("TEST 1: Highlight Word")
    print("="*80)
    result, count = formatter.highlight_word(sample_latex, 'machine learning', 'yellow')
    
    print("\n" + "="*80)
    print("TEST 2: Bold Phrase")
    print("="*80)
    result, count = formatter.bold_phrase(result, 'deep learning')
    
    print("\n" + "="*80)
    print("TEST 3: Italic Word")
    print("="*80)
    result, count = formatter.italic_word(result, 'dataset')
    
    print("\n" + "="*80)
    print("TEST 4: Highlight Sentence")
    print("="*80)
    result, count = formatter.highlight_sentence(result, 'The results show significant improvement.', 'green')
    
    print("\n" + "="*80)
    print("TEST 5: Auto-detect Formatting")
    print("="*80)
    result, count = formatter.bold_auto(result, 'accuracy')
    
    print("\n" + "="*80)
    print("FINAL RESULT PREVIEW")
    print("="*80)
    print(result[:500] + "...")
    
    return result


if __name__ == '__main__':
    test_formatter()
