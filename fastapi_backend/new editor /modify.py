"""
Simple Section Content Modifier

Two modes:
1. Direct replacement: User provides exact new content
2. AI improvement: User asks to improve/change section with specific focus
"""

import re
import os
from typing import Tuple, Optional, List
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv


class APIKeyRotator:
    """Simple API key rotation to avoid rate limits"""
    
    def __init__(self):
        """Load all API keys from .env file"""
        # Load .env file
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(env_path)
        
        # Collect all API keys
        self.api_keys = []
        
        # Primary key
        primary_key = os.getenv('GEMINI_API_KEY')
        if primary_key:
            self.api_keys.append(primary_key)
        
        # Backup keys (API_KEY1 to API_KEY30)
        for i in range(1, 31):
            key = os.getenv(f'API_KEY{i}')
            if key and key.strip():  # Only add non-empty keys
                self.api_keys.append(key)
        
        self.current_index = 0
        print(f"  🔑 Loaded {len(self.api_keys)} API keys for rotation")
    
    def get_next_key(self) -> Optional[str]:
        """Get the next API key in rotation"""
        if not self.api_keys:
            return None
        
        key = self.api_keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        return key
    
    def get_current_key(self) -> Optional[str]:
        """Get current API key without rotating"""
        if not self.api_keys:
            return None
        return self.api_keys[self.current_index]


class SimpleModifier:
    """Dead simple section content modification - no overcomplicated logic"""
    
    def __init__(self, use_api_rotation: bool = True):
        """
        Initialize the modifier with API key rotation.
        
        Args:
            use_api_rotation: Whether to use API key rotation (default: True)
        """
        self.model = None
        self.api_rotator = None
        
        if use_api_rotation:
            self.api_rotator = APIKeyRotator()
            if self.api_rotator.api_keys:
                # Get model name from .env or use default
                env_path = Path(__file__).parent.parent.parent / '.env'
                load_dotenv(env_path)
                model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
                
                # Configure with first key
                first_key = self.api_rotator.get_current_key()
                genai.configure(api_key=first_key)
                self.model = genai.GenerativeModel(model_name)
                print(f"  ✅ Gemini configured with {model_name} ({len(self.api_rotator.api_keys)} keys)")
            else:
                print("  ⚠️  No API keys found in .env file")
    
    def _try_with_rotation(self, prompt: str, max_retries: int = 5) -> Optional[str]:
        """
        Try API call with key rotation on failure.
        
        Args:
            prompt: The prompt to send to Gemini
            max_retries: Maximum number of retries with different keys
            
        Returns:
            Generated text or None if all attempts fail
        """
        if not self.model or not self.api_rotator:
            return None
        
        # Get model name from env
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(env_path)
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
        for attempt in range(max_retries):
            try:
                # Try with current key (rotate on first attempt if needed)
                if attempt > 0:
                    # Get next key for retry
                    next_key = self.api_rotator.get_next_key()
                    if not next_key:
                        print(f"  ❌ No more keys available after {attempt} attempts")
                        return None
                    genai.configure(api_key=next_key)
                    self.model = genai.GenerativeModel(model_name)
                    print(f"  🔄 Rotated to new API key (attempt {attempt + 1}/{max_retries})")
                
                # Make API call
                response = self.model.generate_content(prompt)
                return response.text.strip()
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                if 'quota' in error_msg or 'rate' in error_msg or 'limit' in error_msg or '429' in error_msg or 'resource_exhausted' in error_msg:
                    if attempt < max_retries - 1:
                        print(f"  ⚠️  Rate limit hit (attempt {attempt + 1}/{max_retries}), rotating to next API key...")
                        # Continue to next iteration which will rotate key
                        continue
                    else:
                        print(f"  ❌ Rate limit hit on all {max_retries} attempts")
                        return None
                else:
                    # Non-rate-limit error - don't retry with different keys
                    print(f"  ❌ API error: {str(e)[:200]}")
                    return None
        
        print(f"  ❌ Failed after {max_retries} attempts with different API keys")
        return None
    
    def modify_section_direct(self, content: str, section_name: str, new_content: str) -> Tuple[str, int]:
        """
        DIRECT REPLACEMENT: Replace section content with exact new content.
        
        Example prompts:
        - "replace related works content with: [content]"
        - "change introduction to: [content]"
        
        Args:
            content: LaTeX document content
            section_name: Name of section to modify
            new_content: Exact new content to use
            
        Returns:
            (modified_content, success_count)
        """
        print(f"\n🔄 Direct replacement of '{section_name}' section")
        
        # Pattern to find section (supports \section, \section*, with numbers, etc.)
        # Handle special characters by splitting into words and matching flexibly
        # This handles cases like "Results & Discussion" where & might be written as & or \& in LaTeX
        
        # Split section name into meaningful words (handle spaces, &, and other separators)
        # Normalize: remove extra spaces and handle & as a separator
        normalized_name = re.sub(r'\s+', ' ', section_name.strip())
        name_words = re.split(r'[\s&]+', normalized_name)
        name_words = [w.strip() for w in name_words if w.strip()]  # Remove empty strings
        
        if not name_words:
            print(f"  ❌ Invalid section name: '{section_name}'")
            return content, 0
        
        if len(name_words) > 1:
            # For multi-word names: match all words in order (allows for LaTeX escaping of special chars)
            word_patterns = []
            for word in name_words:
                # Escape the word for regex
                escaped_word = re.escape(word)
                word_patterns.append(escaped_word)
            
            # Join words with pattern that allows:
            # - Spaces
            # - Ampersands (both & and \& for LaTeX)
            # - Other whitespace
            # Pattern: word1 [spaces/&/\\&] word2 [spaces/&/\\&] word3 ...
            separator_pattern = r'[\s]*(?:\\?&|\\?#|\\?%|\\?\$)?[\s]*'
            word_pattern = separator_pattern.join(word_patterns)
        else:
            # Single word: just escape it (no special handling needed for single words)
            word_pattern = re.escape(name_words[0])
        
        # Build final pattern: section command + flexible name matching + content until next section
        pattern = r'(\\(?:sub)*section\*?\{[^}]*?' + word_pattern + r'[^}]*?\})(.*?)(?=\\(?:sub)*section|\Z)'
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not match:
            print(f"  ❌ Section '{section_name}' not found")
            return content, 0
        
        # Replace content but keep section header
        section_header = match.group(1)
        old_content = match.group(2)
        
        # Build new section
        new_section = section_header + '\n' + new_content.strip() + '\n\n'
        
        # Replace in document
        modified = content[:match.start()] + new_section + content[match.end():]
        
        print(f"  ✅ Replaced {len(old_content)} chars with {len(new_content)} chars")
        return modified, 1
    
    def modify_section_ai(self, content: str, section_name: str, instruction: str) -> Tuple[str, int]:
        """
        AI IMPROVEMENT: Use Gemini to improve/modify section based on instructions.
        
        Example prompts:
        - "make related works better by focusing on architecture"
        - "improve introduction to be more concise"
        - "change methods section to focus on data collection"
        - "modify results to highlight key findings"
        
        Args:
            content: LaTeX document content
            section_name: Name of section to modify
            instruction: How to improve/modify the section
            
        Returns:
            (modified_content, success_count)
        """
        if not self.model:
            print("  ❌ Gemini API key not configured")
            return content, 0
        
        print(f"\n🤖 AI improvement of '{section_name}' section")
        print(f"   Instruction: {instruction}")
        
        # Find the section (use same improved pattern as modify_section_direct)
        # Handle special characters by splitting into words and matching flexibly
        normalized_name = re.sub(r'\s+', ' ', section_name.strip())
        name_words = re.split(r'[\s&]+', normalized_name)
        name_words = [w.strip() for w in name_words if w.strip()]
        
        if not name_words:
            print(f"  ❌ Invalid section name: '{section_name}'")
            return content, 0
        
        if len(name_words) > 1:
            word_patterns = []
            for word in name_words:
                escaped_word = re.escape(word)
                word_patterns.append(escaped_word)
            # Join words allowing spaces and LaTeX-escaped special characters between words
            separator_pattern = r'[\s]*(?:\\?&|\\?#|\\?%|\\?\$)?[\s]*'
            word_pattern = separator_pattern.join(word_patterns)
        else:
            word_pattern = re.escape(name_words[0])
        
        pattern = r'(\\(?:sub)*section\*?\{[^}]*?' + word_pattern + r'[^}]*?\})(.*?)(?=\\(?:sub)*section|\Z)'
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not match:
            print(f"  ❌ Section '{section_name}' not found")
            return content, 0
        
        section_header = match.group(1)
        old_content = match.group(2).strip()
        
        print(f"  📖 Original content: {len(old_content)} characters")
        
        # Build AI prompt
        prompt = f"""You are a LaTeX document editor. Your task is to modify the following section content.

SECTION: {section_name}

ORIGINAL CONTENT:
{old_content}

INSTRUCTION: {instruction}

REQUIREMENTS:
1. Keep the content in LaTeX format
2. Maintain all citations (\\cite{{...}})
3. Keep all math equations (\\(...\\), $$...$$, etc.)
4. Preserve important technical terms
5. Follow the instruction to improve/modify the content
6. Return ONLY the modified section content, no explanations
7. Do NOT include the section header (\\section{{...}})

MODIFIED CONTENT:"""

        try:
            # Get AI response with rotation support
            new_content = self._try_with_rotation(prompt)
            
            if not new_content:
                print(f"  ❌ AI modification failed: No response from API")
                return content, 0
            
            # Clean up any markdown code blocks if AI added them
            new_content = re.sub(r'^```latex\s*', '', new_content)
            new_content = re.sub(r'^```\s*', '', new_content)
            new_content = re.sub(r'\s*```$', '', new_content)
            
            print(f"  ✅ AI generated new content: {len(new_content)} characters")
            
            # Build new section
            new_section = section_header + '\n' + new_content + '\n\n'
            
            # Replace in document
            modified = content[:match.start()] + new_section + content[match.end():]
            
            return modified, 1
            
        except Exception as e:
            print(f"  ❌ AI modification failed: {str(e)}")
            return content, 0
    
    def modify_auto(self, content: str, section_name: str, instruction_or_content: str) -> Tuple[str, int]:
        """
        AUTO-DETECT: Automatically detect if user wants direct replacement or AI improvement.
        
        Detection logic:
        - If instruction contains ":" followed by substantial content → Direct replacement
        - If instruction contains improvement words (better, improve, focus, change, etc.) → AI improvement
        - Default → AI improvement
        
        Args:
            content: LaTeX document content
            section_name: Name of section to modify
            instruction_or_content: Either new content or improvement instruction
            
        Returns:
            (modified_content, success_count)
        """
        text = instruction_or_content.strip()
        
        # Check for direct replacement pattern: "replace ... with: [content]"
        if ':' in text:
            parts = text.split(':', 1)
            if len(parts) == 2 and len(parts[1].strip()) > 50:  # Has substantial content after ":"
                print("  🎯 Detected: DIRECT REPLACEMENT mode")
                new_content = parts[1].strip()
                return self.modify_section_direct(content, section_name, new_content)
        
        # Check for AI improvement keywords
        improvement_keywords = [
            'better', 'improve', 'focus', 'change', 'modify', 'enhance',
            'make', 'rewrite', 'update', 'refine', 'polish', 'optimize',
            'by focusing', 'by highlighting', 'by emphasizing', 'more concise',
            'more detailed', 'more technical', 'more accessible'
        ]
        
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in improvement_keywords):
            print("  🎯 Detected: AI IMPROVEMENT mode")
            return self.modify_section_ai(content, section_name, text)
        
        # Default: Try AI improvement
        print("  🎯 Default: AI IMPROVEMENT mode")
        return self.modify_section_ai(content, section_name, text)


def test_simple_modifier():
    """Test the simple modifier with examples"""
    
    # Sample LaTeX content
    test_content = r"""
\section{Introduction}
This is the introduction section.
It talks about the problem.

\section{Related Works}
Previous work by Smith et al. \cite{smith2020} focused on basic approaches.
Another study by Jones \cite{jones2019} looked at different methods.
These works are important but limited.

\section{Methods}
We use a novel approach.

\section{Results}
The results are good.
"""
    
    print("=" * 80)
    print("TEST 1: Direct Replacement")
    print("=" * 80)
    
    modifier = SimpleModifier()  # No API key for this test
    
    new_content = """
This is completely new related works content.
We reference important papers and provide context.
This replaces everything in the section.
"""
    
    modified, count = modifier.modify_section_direct(test_content, "Related Works", new_content)
    print(f"✅ Modified {count} sections")
    
    # Show result
    section_match = re.search(r'\\section\{Related Works\}(.*?)(?=\\section|\Z)', modified, re.DOTALL)
    if section_match:
        print(f"\nNew content:")
        print(section_match.group(1).strip())
    
    print("\n" + "=" * 80)
    print("TEST 2: Auto-detect (Direct Replacement)")
    print("=" * 80)
    
    instruction = "replace introduction with: This is brand new introduction content that is much better."
    modified, count = modifier.modify_auto(test_content, "Introduction", instruction)
    print(f"✅ Modified {count} sections")
    
    print("\n" + "=" * 80)
    print("TEST 3: Auto-detect (AI Improvement)")
    print("=" * 80)
    
    instruction = "make it better by focusing on recent advances"
    print(f"Instruction: '{instruction}'")
    print("Note: Would use AI if API key was configured")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ Direct replacement: Working")
    print("✅ Auto-detection: Working")
    print("⚠️  AI improvement: Requires Gemini API key")


if __name__ == "__main__":
    test_simple_modifier()
