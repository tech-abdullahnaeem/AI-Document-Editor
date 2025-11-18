"""
SIMPLE REPLACEMENT ENGINE
No complex logic, no parsers, no object systems.
Just direct string replacement with smart handling.
"""

import re
from typing import Tuple, Optional
import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv


class APIKeyRotator:
    """
    Enhanced API key rotation system for efficient use of all 39 keys.
    
    Features:
    - Automatic detection of all available keys (GEMINI_API_KEY + API_KEY1-39)
    - Smart rotation that distributes load evenly across all keys
    - Rate limit tracking per key to avoid hitting the same exhausted key
    - Automatic skip of recently rate-limited keys
    - Per-key cooldown period after rate limit
    """
    
    def __init__(self):
        """Load all API keys from .env file and initialize rotation state"""
        # Load .env file
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(env_path)
        
        # Collect all API keys
        self.api_keys = []
        self.key_names = []  # For debugging/logging
        
        # Primary key
        primary_key = os.getenv('GEMINI_API_KEY')
        if primary_key and primary_key.strip():
            self.api_keys.append(primary_key)
            self.key_names.append('GEMINI_API_KEY')
        
        # Backup keys (API_KEY1 to API_KEY39)
        for i in range(1, 40):
            key = os.getenv(f'API_KEY{i}')
            if key and key.strip():  # Only add non-empty keys
                self.api_keys.append(key)
                self.key_names.append(f'API_KEY{i}')
        
        # Rotation state
        self.current_index = 0
        self.total_keys = len(self.api_keys)
        
        # Rate limit tracking
        self.rate_limited_keys = set()  # Indices of rate-limited keys
        self.key_usage_count = [0] * self.total_keys  # Track usage per key
        self.successful_requests = [0] * self.total_keys  # Track successful requests
        
        if self.api_keys:
            print(f"  🔑 Loaded {self.total_keys} API keys for rotation")
            print(f"  📊 Estimated capacity: {self.total_keys * 50} requests/day (50 per key)")
    
    def get_next_key(self) -> Optional[str]:
        """
        Get the next available API key in rotation.
        Automatically skips rate-limited keys and distributes load evenly.
        
        Returns:
            Next available API key or None if all keys exhausted
        """
        if not self.api_keys:
            return None
        
        # If all keys are rate-limited, reset and try again
        if len(self.rate_limited_keys) >= self.total_keys:
            print(f"  ⚠️  All {self.total_keys} keys hit rate limits - resetting cooldown")
            self.rate_limited_keys.clear()
            return None
        
        # Find next non-rate-limited key
        attempts = 0
        while attempts < self.total_keys:
            key = self.api_keys[self.current_index]
            key_name = self.key_names[self.current_index]
            current_idx = self.current_index
            
            # Move to next key for next call
            self.current_index = (self.current_index + 1) % self.total_keys
            
            # Skip if rate-limited
            if current_idx in self.rate_limited_keys:
                attempts += 1
                continue
            
            # Track usage
            self.key_usage_count[current_idx] += 1
            
            return key
        
        # All keys are rate-limited
        print(f"  ❌ All {self.total_keys} keys are rate-limited")
        return None
    
    def get_current_key(self) -> Optional[str]:
        """Get current API key without rotating"""
        if not self.api_keys:
            return None
        return self.api_keys[self.current_index]
    
    def mark_rate_limited(self, key: str):
        """
        Mark a key as rate-limited to avoid using it again.
        
        Args:
            key: The API key that hit rate limit
        """
        try:
            idx = self.api_keys.index(key)
            self.rate_limited_keys.add(idx)
            key_name = self.key_names[idx]
            available = self.total_keys - len(self.rate_limited_keys)
            print(f"  ⚠️  {key_name} rate-limited | {available}/{self.total_keys} keys still available")
        except ValueError:
            pass
    
    def mark_successful(self, key: str):
        """
        Mark a successful request for a key.
        
        Args:
            key: The API key that completed successfully
        """
        try:
            idx = self.api_keys.index(key)
            self.successful_requests[idx] += 1
        except ValueError:
            pass
    
    def get_stats(self) -> dict:
        """
        Get rotation statistics for monitoring.
        
        Returns:
            Dictionary with rotation statistics
        """
        return {
            'total_keys': self.total_keys,
            'available_keys': self.total_keys - len(self.rate_limited_keys),
            'rate_limited_keys': len(self.rate_limited_keys),
            'total_usage': sum(self.key_usage_count),
            'total_successful': sum(self.successful_requests),
            'key_usage_distribution': dict(zip(self.key_names, self.key_usage_count)),
            'key_success_rate': dict(zip(self.key_names, self.successful_requests))
        }
    
    def reset_rate_limits(self):
        """Reset all rate limit flags - useful for new hour/day"""
        self.rate_limited_keys.clear()
        print(f"  🔄 Rate limits reset - all {self.total_keys} keys available again")


class SimpleReplacer:
    """Dead simple replacement - no overcomplicated logic"""
    
    def __init__(self, use_api_rotation: bool = True):
        """
        Initialize with API key rotation for Gemini conversions.
        
        Args:
            use_api_rotation: Whether to use API key rotation (default: True)
        """
        self.model = None
        self.api_rotator = None
        
        if use_api_rotation:
            self.api_rotator = APIKeyRotator()
            if self.api_rotator and self.api_rotator.api_keys:
                # Get model name from .env or use default
                env_path = Path(__file__).parent.parent.parent / '.env'
                load_dotenv(env_path)
                model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
                
                # Configure with first key
                first_key = self.api_rotator.get_current_key()
                genai.configure(api_key=first_key)
                self.model = genai.GenerativeModel(model_name)
                print(f"  🤖 Gemini API configured with {len(self.api_rotator.api_keys)} rotating keys")
            else:
                print("  ⚠️  No Gemini API keys found - plain text to LaTeX conversion disabled")
    
    def replace_word(self, content: str, old_word: str, new_word: str) -> Tuple[str, int]:
        """
        Replace ALL exact occurrences of a word.
        Simple regex with word boundaries.
        
        Args:
            content: LaTeX document content
            old_word: Word to replace
            new_word: Replacement word
            
        Returns:
            (modified_content, replacement_count)
        """
        print(f"\n🔄 Replacing word: '{old_word}' → '{new_word}'")
        
        # Word boundary pattern - exact match only
        pattern = r'\b' + re.escape(old_word) + r'\b'
        
        # Find all matches
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ No occurrences found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start (avoid offset issues)
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            matched_word = content[start:end]
            
            # Preserve case
            replacement = self._preserve_case(matched_word, new_word)
            
            modified = modified[:start] + replacement + modified[end:]
        
        print(f"  ✅ Replaced {count} occurrences")
        return modified, count
    
    def replace_phrase(self, content: str, old_phrase: str, new_phrase: str) -> Tuple[str, int]:
        """
        Replace ALL exact occurrences of a phrase (multi-word).
        Handles spaces and punctuation.
        
        Args:
            content: LaTeX document content
            old_phrase: Phrase to replace
            new_phrase: Replacement phrase
            
        Returns:
            (modified_content, replacement_count)
        """
        print(f"\n🔄 Replacing phrase: '{old_phrase}' → '{new_phrase}'")
        
        # Escape special regex characters
        pattern = re.escape(old_phrase)
        
        # Find all matches (case-insensitive)
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        count = len(matches)
        
        if count == 0:
            print(f"  ❌ No occurrences found")
            return content, 0
        
        print(f"  📍 Found {count} occurrences")
        
        # Replace from end to start
        modified = content
        for match in reversed(matches):
            start, end = match.span()
            matched_phrase = content[start:end]
            
            # Preserve case of first word
            replacement = self._preserve_case(matched_phrase, new_phrase)
            
            modified = modified[:start] + replacement + modified[end:]
        
        print(f"  ✅ Replaced {count} occurrences")
        return modified, count
    
    def replace_sentence(self, content: str, old_sentence: str, new_sentence: str) -> Tuple[str, int]:
        """
        Replace a sentence. More flexible matching - allows partial match.
        
        Args:
            content: LaTeX document content
            old_sentence: Sentence to replace (can be partial)
            new_sentence: Replacement sentence
            
        Returns:
            (modified_content, replacement_count)
        """
        print(f"\n🔄 Replacing sentence: '{old_sentence[:50]}...' → '{new_sentence[:50]}...'")
        
        # Try exact match first
        if old_sentence in content:
            modified = content.replace(old_sentence, new_sentence)
            count = content.count(old_sentence)
            print(f"  ✅ Exact match - Replaced {count} occurrence(s)")
            return modified, count
        
        # Try case-insensitive
        pattern = re.escape(old_sentence)
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        if matches:
            count = len(matches)
            print(f"  📍 Found {count} case-insensitive match(es)")
            
            modified = content
            for match in reversed(matches):
                start, end = match.span()
                modified = modified[:start] + new_sentence + modified[end:]
            
            print(f"  ✅ Replaced {count} occurrence(s)")
            return modified, count
        
        # If still no match, try fuzzy matching with first few words
        words = old_sentence.split()
        if len(words) >= 3:
            # Try matching first 5-7 words
            partial = ' '.join(words[:min(5, len(words))])
            pattern = re.escape(partial)
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            
            if matches:
                print(f"  ⚠️  Partial match found with first words: '{partial}'")
                # Ask user or use AI to find full sentence
                if self.model:
                    return self._ai_replace_sentence(content, old_sentence, new_sentence)
        
        print(f"  ❌ No match found for sentence")
        return content, 0
    
    def replace_section_content(self, content: str, section_name: str, new_content: str, 
                               convert_to_latex: bool = True) -> Tuple[str, int]:
        """
        Replace the content of a LaTeX section.
        Finds \section{name} and replaces everything until next \section.
        
        Args:
            content: LaTeX document content
            section_name: Name of section to replace
            new_content: New content for the section (can be plain text or LaTeX)
            convert_to_latex: If True, convert plain text to LaTeX format using AI
            
        Returns:
            (modified_content, replacement_count)
        """
        print(f"\n🔄 Replacing section content: '{section_name}'")
        
        # Pattern to find section
        # Matches: \section{Section Name} ... (content until next section)
        pattern = r'(\\(?:sub)*section\*?\{[^}]*' + re.escape(section_name) + r'[^}]*\})(.*?)(?=\\(?:sub)*section|\Z)'
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not match:
            print(f"  ❌ Section '{section_name}' not found")
            return content, 0
        
        # Replace content but keep section header
        section_header = match.group(1)
        old_content = match.group(2)
        
        # Convert plain text to LaTeX if needed
        if convert_to_latex and self.model:
            print(f"  🤖 Converting plain text to LaTeX format...")
            latex_content = self._convert_to_latex(new_content, section_name)
            if latex_content:
                new_content = latex_content
                print(f"  ✅ Conversion successful")
            else:
                print(f"  ⚠️  Conversion failed, using original text")
        
        # Build new section
        new_section = section_header + '\n' + new_content + '\n\n'
        
        # Replace in document
        modified = content[:match.start()] + new_section + content[match.end():]
        
        print(f"  ✅ Replaced section content")
        return modified, 1
    
    def replace_auto(self, content: str, old_text: str, new_text: str) -> Tuple[str, int]:
        """
        AUTO-DETECT: Automatically detect if it's a word, phrase, or sentence.
        
        Args:
            content: LaTeX document content
            old_text: Text to replace
            new_text: Replacement text
            
        Returns:
            (modified_content, replacement_count)
        """
        # Count words
        word_count = len(old_text.split())
        
        if word_count == 1:
            # Single word - use word replacement
            return self.replace_word(content, old_text, new_text)
        elif word_count <= 4:
            # Short phrase (2-4 words) - use phrase replacement
            return self.replace_phrase(content, old_text, new_text)
        else:
            # Long phrase/sentence (5+ words) - use sentence replacement
            return self.replace_sentence(content, old_text, new_text)
    
    def get_rotation_stats(self) -> Optional[dict]:
        """
        Get API key rotation statistics.
        
        Returns:
            Dictionary with rotation statistics or None if no rotator
        """
        if self.api_rotator:
            return self.api_rotator.get_stats()
        return None
    
    def reset_rate_limits(self):
        """Reset all API key rate limit flags"""
        if self.api_rotator:
            self.api_rotator.reset_rate_limits()
    
    def _preserve_case(self, original: str, replacement: str) -> str:
        """
        Preserve the case of the original text in the replacement.
        
        Examples:
            'CGM' -> 'GLUCOSE MONITOR' becomes 'Glucose Monitor'
            'cgm' -> 'glucose monitor' becomes 'glucose monitor'
            'Cgm' -> 'Glucose monitor' becomes 'Glucose monitor'
        """
        if not original:
            return replacement
        
        # All caps
        if original.isupper():
            # For multi-word replacements with all caps, use Title Case
            if ' ' in replacement or '-' in original:
                return replacement.title()
            return replacement.upper()
        
        # First letter capitalized
        if original[0].isupper():
            return replacement.capitalize()
        
        # All lowercase
        return replacement.lower()
    
    def _convert_to_latex(self, plain_text: str, section_name: str = "") -> Optional[str]:
        """
        Convert plain text to properly formatted LaTeX content using AI with enhanced key rotation.
        
        Uses all 39 available API keys efficiently:
        - Automatically rotates through all keys
        - Skips rate-limited keys
        - Tracks success/failure per key
        - Provides detailed progress feedback
        
        Args:
            plain_text: Plain text content from user
            section_name: Name of section for context
            
        Returns:
            LaTeX formatted content or None if conversion fails
        """
        if not self.model or not self.api_rotator:
            return None
        
        prompt = f"""Convert this plain text into properly formatted LaTeX content.

REQUIREMENTS:
1. Preserve all the information from the plain text
2. Use proper LaTeX formatting:
   - Use \\textbf{{}} for bold text
   - Use \\textit{{}} for italic text
   - Use \\subsection{{}} or \\subsection*{{}} for subsections if needed
   - Use \\begin{{itemize}} ... \\end{{itemize}} for bullet lists
   - Use \\begin{{enumerate}} ... \\end{{enumerate}} for numbered lists
   - Escape special characters: %, &, $, #, _, {{, }}, ~, ^, \\
   - Use proper paragraph breaks (double newline)
3. Keep the content scientific and formal
4. Do NOT add \\section{{}} tags (section header already exists)
5. Return ONLY the LaTeX code, no explanations

{f"Section context: {section_name}" if section_name else ""}

PLAIN TEXT:
{plain_text}

LATEX OUTPUT:"""

        # Try with all available keys
        max_retries = self.api_rotator.total_keys
        stats = self.api_rotator.get_stats()
        print(f"  📊 Starting conversion with {stats['available_keys']}/{stats['total_keys']} keys available")
        
        for attempt in range(max_retries):
            try:
                # Get next available key
                current_key = self.api_rotator.get_next_key()
                
                if not current_key:
                    print(f"  ❌ No more keys available after {attempt} attempts")
                    break
                
                # Reconfigure with new key
                genai.configure(api_key=current_key)
                
                if attempt > 0:
                    stats = self.api_rotator.get_stats()
                    print(f"  🔄 Attempt {attempt + 1}/{max_retries} | {stats['available_keys']} keys remaining")
                
                # Make API call
                response = self.model.generate_content(prompt)
                latex_output = response.text.strip()
                
                # Mark successful request
                self.api_rotator.mark_successful(current_key)
                
                # Clean up the response - remove code blocks if AI added them
                latex_output = latex_output.replace('```latex', '').replace('```', '').strip()
                
                # Basic validation - check if it looks like LaTeX
                if '\\' in latex_output or latex_output == plain_text:
                    stats = self.api_rotator.get_stats()
                    print(f"  ✅ Conversion successful (Total: {stats['total_successful']} successes)")
                    return latex_output
                
                return None
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a rate limit error
                if 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower() or '429' in error_msg:
                    # Mark this key as rate-limited
                    self.api_rotator.mark_rate_limited(current_key)
                    
                    if attempt < max_retries - 1:
                        continue  # Try next key
                    else:
                        print(f"  ❌ All {max_retries} API keys exhausted")
                        return None
                else:
                    # Other error - don't retry with different keys
                    print(f"  ⚠️  AI conversion error: {e}")
                    return None
        
        return None
    
    def _ai_replace_sentence(self, content: str, old_sentence: str, new_sentence: str) -> Tuple[str, int]:
        """
        Use AI to find and replace a sentence when exact matching fails.
        Uses enhanced API key rotation for maximum reliability.
        
        Args:
            content: LaTeX document content
            old_sentence: Sentence to find
            new_sentence: Replacement sentence
            
        Returns:
            (modified_content, replacement_count)
        """
        if not self.model or not self.api_rotator:
            print("  ❌ AI model not available for fuzzy matching")
            return content, 0
        
        print("  🤖 Using AI to find sentence...")
        
        prompt = f"""Find the exact location of this sentence in the text:

TARGET SENTENCE: "{old_sentence}"

TEXT:
{content[:2000]}...

Reply with ONLY the exact sentence as it appears in the text, or "NOT FOUND" if you can't find it.
No explanations."""

        # Try with all available keys
        max_retries = min(self.api_rotator.total_keys, 10)  # Try up to 10 keys for sentence matching
        
        for attempt in range(max_retries):
            try:
                # Get next available key
                current_key = self.api_rotator.get_next_key()
                
                if not current_key:
                    print(f"  ❌ No more keys available after {attempt} attempts")
                    break
                
                # Reconfigure with new key
                genai.configure(api_key=current_key)
                
                if attempt > 0:
                    stats = self.api_rotator.get_stats()
                    print(f"  🔄 Retrying with next key ({stats['available_keys']} keys available)")
                
                response = self.model.generate_content(prompt)
                found_sentence = response.text.strip()
                
                # Mark successful request
                self.api_rotator.mark_successful(current_key)
                
                if found_sentence == "NOT FOUND" or not found_sentence:
                    print("  ❌ AI couldn't find the sentence")
                    return content, 0
                
                # Try to replace what AI found
                if found_sentence in content:
                    modified = content.replace(found_sentence, new_sentence, 1)
                    print(f"  ✅ AI found and replaced: '{found_sentence[:50]}...'")
                    return modified, 1
                
                return content, 0
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a rate limit error
                if 'quota' in error_msg.lower() or 'rate limit' in error_msg.lower() or '429' in error_msg:
                    # Mark this key as rate-limited
                    self.api_rotator.mark_rate_limited(current_key)
                    
                    if attempt < max_retries - 1:
                        continue  # Try next key
                    else:
                        stats = self.api_rotator.get_stats()
                        print(f"  ❌ Exhausted {attempt + 1} keys ({stats['rate_limited_keys']} rate-limited)")
                        return content, 0
                else:
                    # Other error - don't retry
                    print(f"  ❌ AI error: {e}")
                    return content, 0
        
        return content, 0


# ============================================================================
# SIMPLE TEST FUNCTIONS
# ============================================================================

def test_simple_replacer():
    """Test the simple replacer with sample content"""
    
    sample_latex = r"""
\section{Introduction}
CGM devices are important. The CGM helps patients monitor glucose levels.
We tested multiple CGM systems in our study.

\section{Methods}
The dataset contains patient records. We used three datasets for validation.
This dataset is publicly available.

\section{Results}
Deep learning models showed good performance. The deep learning approach 
outperformed traditional methods. Deep learning is the future.
"""

    replacer = SimpleReplacer()
    
    print("="*80)
    print("TEST 1: Word Replacement")
    print("="*80)
    result, count = replacer.replace_word(sample_latex, 'CGM', 'glucose monitor')
    print(f"Replacements: {count}")
    print(f"Result preview: {result[:200]}...")
    
    print("\n" + "="*80)
    print("TEST 2: Phrase Replacement")
    print("="*80)
    result, count = replacer.replace_phrase(result, 'deep learning', 'neural network')
    print(f"Replacements: {count}")
    print(f"Result preview: {result[200:400]}...")
    
    print("\n" + "="*80)
    print("TEST 3: Auto Replacement")
    print("="*80)
    result, count = replacer.replace_auto(result, 'dataset', 'data collection')
    print(f"Replacements: {count}")


if __name__ == '__main__':
    test_simple_replacer()
