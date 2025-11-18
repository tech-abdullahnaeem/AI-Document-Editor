"""
Simple Add Module for LaTeX Documents
Uses pure string manipulation and regex - no parsers, no complex dependencies.

Provides functionality to add:
- Sentences (at start of section, after section, at end of document)
- Sections (at start, at end, after specific section)
- Section content (add content to existing section)
"""

import re
from typing import Tuple, Optional


class SimpleAdder:
    """
    Simple string-based adder for LaTeX documents.
    Uses pure regex and string slicing - no parsers.
    """
    
    def __init__(self):
        """Initialize the SimpleAdder."""
        pass
    
    # ========================================================================
    # SENTENCE ADDITION
    # ========================================================================
    
    def add_sentence_at_section_start(self, content: str, section_name: str, 
                                      sentence: str) -> Tuple[str, int]:
        """
        Add a sentence at the START of a specific section.
        
        Args:
            content: LaTeX document content
            section_name: Name of the section (e.g., "Introduction", "Related works")
            sentence: Sentence to add (will add proper spacing)
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding sentence at START of section: '{section_name}'")
        
        # Find the section
        # Pattern: \section{name} followed by content
        pattern = r'(\\(?:sub)*section\*?\{[^}]*' + re.escape(section_name) + r'[^}]*\})\s*'
        
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            print(f"  ❌ Section '{section_name}' not found")
            return content, 0
        
        # Insert sentence right after section header
        insert_pos = match.end()
        
        # Ensure sentence ends with period and has proper spacing
        if not sentence.strip().endswith('.'):
            sentence = sentence.strip() + '.'
        
        # Add sentence with newline
        modified = content[:insert_pos] + '\n' + sentence.strip() + ' ' + content[insert_pos:]
        
        print(f"  ✅ Added sentence at position {insert_pos}")
        return modified, 1
    
    def add_sentence_after_section(self, content: str, section_name: str, 
                                   sentence: str) -> Tuple[str, int]:
        """
        Add a sentence at the END of a specific section (before next section).
        
        Args:
            content: LaTeX document content
            section_name: Name of the section
            sentence: Sentence to add
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding sentence at END of section: '{section_name}'")
        
        # Find the section and its content
        # Pattern: section header + content until next section or end
        pattern = r'(\\(?:sub)*section\*?\{[^}]*' + re.escape(section_name) + r'[^}]*\})(.*?)(?=\\(?:sub)*section|\Z)'
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if not match:
            print(f"  ❌ Section '{section_name}' not found")
            return content, 0
        
        # Insert position is at the end of section content (before next section)
        insert_pos = match.end(2)  # End of group 2 (section content)
        
        # Ensure sentence ends with period
        if not sentence.strip().endswith('.'):
            sentence = sentence.strip() + '.'
        
        # Add sentence with newline before next section
        modified = content[:insert_pos] + '\n' + sentence.strip() + '\n' + content[insert_pos:]
        
        print(f"  ✅ Added sentence at end of section")
        return modified, 1
    
    def add_sentence_at_document_end(self, content: str, sentence: str) -> Tuple[str, int]:
        """
        Add a sentence at the END of the document.
        
        Args:
            content: LaTeX document content
            sentence: Sentence to add
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding sentence at END of document")
        
        # Ensure sentence ends with period
        if not sentence.strip().endswith('.'):
            sentence = sentence.strip() + '.'
        
        # Find \end{document} if it exists
        end_doc_match = re.search(r'\\end\{document\}', content)
        
        if end_doc_match:
            # Add before \end{document}
            insert_pos = end_doc_match.start()
            modified = content[:insert_pos] + '\n' + sentence.strip() + '\n\n' + content[insert_pos:]
            print(f"  ✅ Added sentence before \\end{{document}}")
        else:
            # Add at very end
            modified = content.rstrip() + '\n\n' + sentence.strip() + '\n'
            print(f"  ✅ Added sentence at document end")
        
        return modified, 1
    
    # ========================================================================
    # SECTION ADDITION
    # ========================================================================
    
    def add_section_at_start(self, content: str, section_name: str, 
                            section_content: str = "") -> Tuple[str, int]:
        """
        Add a new section at the START of the document (after abstract/before first section).
        
        Args:
            content: LaTeX document content
            section_name: Name of the new section
            section_content: Content of the section (optional)
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding section at START: '{section_name}'")
        
        # Find first section
        first_section = re.search(r'\\(?:sub)*section\*?\{', content)
        
        if not first_section:
            print(f"  ❌ No existing sections found")
            return content, 0
        
        # Create new section
        new_section = f"\\section{{{section_name}}}\n"
        if section_content:
            new_section += section_content.strip() + '\n'
        new_section += '\n'
        
        # Insert before first section
        insert_pos = first_section.start()
        modified = content[:insert_pos] + new_section + content[insert_pos:]
        
        print(f"  ✅ Added section at start")
        return modified, 1
    
    def add_section_at_end(self, content: str, section_name: str, 
                          section_content: str = "") -> Tuple[str, int]:
        """
        Add a new section at the END of the document.
        
        Args:
            content: LaTeX document content
            section_name: Name of the new section
            section_content: Content of the section (optional)
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding section at END: '{section_name}'")
        
        # Create new section
        new_section = f"\n\\section{{{section_name}}}\n"
        if section_content:
            new_section += section_content.strip() + '\n'
        
        # Find \end{document} if it exists
        end_doc_match = re.search(r'\\end\{document\}', content)
        
        if end_doc_match:
            # Add before \end{document}
            insert_pos = end_doc_match.start()
            modified = content[:insert_pos] + new_section + '\n' + content[insert_pos:]
            print(f"  ✅ Added section before \\end{{document}}")
        else:
            # Add at very end
            modified = content.rstrip() + '\n' + new_section
            print(f"  ✅ Added section at document end")
        
        return modified, 1
    
    def add_section_after(self, content: str, after_section: str, 
                         new_section_name: str, section_content: str = "") -> Tuple[str, int]:
        """
        Add a new section AFTER a specific existing section.
        
        Args:
            content: LaTeX document content
            after_section: Name of the section to add after (e.g., "Data", "Related works")
            new_section_name: Name of the new section
            section_content: Content of the section (optional)
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding section '{new_section_name}' AFTER '{after_section}'")
        
        # Find the target section and its content
        # Pattern matches: section header + content until next section or \end{document} or end of string
        pattern = r'(\\(?:sub)*section\*?\{[^}]*' + re.escape(after_section) + r'[^}]*\})(.*?)(?=\\(?:sub)*section|\\end\{document\}|\Z)'
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if not match:
            print(f"  ❌ Section '{after_section}' not found")
            return content, 0
        
        # Create new section
        new_section = f"\n\\section{{{new_section_name}}}\n"
        if section_content:
            new_section += section_content.strip() + '\n'
        new_section += '\n'
        
        # Insert after the target section (at end of its content)
        insert_pos = match.end()
        modified = content[:insert_pos] + new_section + content[insert_pos:]
        
        print(f"  ✅ Added section after '{after_section}'")
        return modified, 1
    
    # ========================================================================
    # SECTION CONTENT ADDITION
    # ========================================================================
    
    def add_content_to_section(self, content: str, section_name: str, 
                              new_content: str, position: str = "end") -> Tuple[str, int]:
        """
        Add content to an existing section.
        
        Args:
            content: LaTeX document content
            section_name: Name of the section to add content to
            new_content: Content to add
            position: Where to add ("start" or "end" of section)
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        if position == "start":
            return self.add_content_to_section_start(content, section_name, new_content)
        else:
            return self.add_content_to_section_end(content, section_name, new_content)
    
    def add_content_to_section_start(self, content: str, section_name: str, 
                                     new_content: str) -> Tuple[str, int]:
        """
        Add content at the START of a section (right after section header).
        
        Args:
            content: LaTeX document content
            section_name: Name of the section
            new_content: Content to add
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding content at START of section: '{section_name}'")
        
        # Find the section
        pattern = r'(\\(?:sub)*section\*?\{[^}]*' + re.escape(section_name) + r'[^}]*\})\s*'
        
        match = re.search(pattern, content, re.IGNORECASE)
        if not match:
            print(f"  ❌ Section '{section_name}' not found")
            return content, 0
        
        # Insert content right after section header
        insert_pos = match.end()
        
        # Add content with proper spacing
        modified = content[:insert_pos] + '\n' + new_content.strip() + '\n\n' + content[insert_pos:]
        
        print(f"  ✅ Added {len(new_content)} characters at section start")
        return modified, 1
    
    def add_content_to_section_end(self, content: str, section_name: str, 
                                   new_content: str) -> Tuple[str, int]:
        """
        Add content at the END of a section (before next section).
        
        Args:
            content: LaTeX document content
            section_name: Name of the section
            new_content: Content to add
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        print(f"\n➕ Adding content at END of section: '{section_name}'")
        
        # Find the section and its content
        pattern = r'(\\(?:sub)*section\*?\{[^}]*' + re.escape(section_name) + r'[^}]*\})(.*?)(?=\\(?:sub)*section|\Z)'
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if not match:
            print(f"  ❌ Section '{section_name}' not found")
            return content, 0
        
        # Insert at end of section content
        insert_pos = match.end(2)
        
        # Add content with proper spacing
        modified = content[:insert_pos] + '\n' + new_content.strip() + '\n' + content[insert_pos:]
        
        print(f"  ✅ Added {len(new_content)} characters at section end")
        return modified, 1
    
    def add_section_smart(self, content: str, section_name: str, description: str = "", 
                         target_section_hint: str = None, position_hint: str = None) -> Tuple[str, int]:
        """
        Intelligently add a section by automatically determining the best position
        and generating relevant content using AI.
        
        Args:
            content: LaTeX document content
            section_name: Name of the section to add (e.g., "Future Works", "Limitations")
            description: Description of desired content (optional, used for AI generation)
            target_section_hint: Optional target section name from parsed query (e.g., "Limitations", "3 Data")
            position_hint: Optional position from parsed query ('before' or 'after')
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        import google.generativeai as genai
        import os
        from dotenv import load_dotenv
        
        # Load environment variables from parent directory
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        load_dotenv(env_path)
        
        print(f"\n🤖 Smart Section Addition:")
        print(f"  Section: {section_name}")
        print(f"  Description: {description}")
        
        # Step 1: Determine best position
        section_lower = section_name.lower()
        target_section = None
        position = "before"  # Default position relative to target
        
        # PRIORITY 1: Use explicitly provided target and position from parsed query
        if target_section_hint and position_hint:
            target_section = target_section_hint
            position = position_hint
            print(f"  📍 Positioning: {position_hint.capitalize()} '{target_section_hint}' (from query)")
        # PRIORITY 2: Smart positioning based on section name patterns
        elif any(word in section_lower for word in ["future", "future work", "future direction"]):
            target_section = "Conclusion"
            position = "before"
            print(f"  📍 Positioning: Before '{target_section}'")
        elif any(word in section_lower for word in ["limitation", "limitations"]):
            # Try to place before Future Works or Conclusion
            if re.search(r'\\(?:sub)*section\*?\{[^}]*future[^}]*\}', content, re.IGNORECASE):
                target_section = "Future"
                position = "before"
            else:
                target_section = "Conclusion"
                position = "before"
            print(f"  📍 Positioning: Before '{target_section}'")
        elif any(word in section_lower for word in ["acknowledgment", "acknowledgement"]):
            # Always at the very end
            target_section = None  # Use add_section_at_end
            print(f"  📍 Positioning: End of document")
        elif any(word in section_lower for word in ["related work", "background", "literature"]):
            target_section = "Introduction"
            position = "after"
            print(f"  📍 Positioning: After '{target_section}'")
        else:
            # Default: Try before Conclusion, or at end if no Conclusion
            if re.search(r'\\(?:sub)*section\*?\{[^}]*conclusion[^}]*\}', content, re.IGNORECASE):
                target_section = "Conclusion"
                position = "before"
                print(f"  📍 Positioning: Before '{target_section}' (default)")
            else:
                target_section = None
                print(f"  📍 Positioning: End of document (default)")
        
        # Step 2: Generate content using AI if description provided
        section_content = ""
        if description and description.strip():
            try:
                # Load environment variables (same location as main.py)
                from dotenv import load_dotenv
                from pathlib import Path
                
                # .env is in the parent directory of fastapi_backend
                # Path: /Users/.../final with fast api copy/.env
                env_path = Path.cwd().parent / '.env'
                if not env_path.exists():
                    # Fallback: try from __file__ location
                    env_path = Path(__file__).parent.parent.parent / '.env'
                
                load_dotenv(env_path)
                print(f"  📁 Loading .env from: {env_path}")
                
                # Get API keys from environment (same pattern as QueryParser)
                api_keys = []
                
                # Try primary key first
                primary_key = os.getenv('GEMINI_API_KEY')
                if primary_key and primary_key.strip():
                    api_keys.append(primary_key)
                
                # Try numbered keys (API_KEY1 to API_KEY39)
                for i in range(1, 40):
                    key = os.getenv(f'API_KEY{i}')
                    if key and key.strip():
                        api_keys.append(key)
                
                if not api_keys:
                    print(f"  ⚠️ No Gemini API keys found, using description as content")
                    section_content = description
                else:
                    print(f"  🔑 Found {len(api_keys)} API key(s)")
                    
                    # Generate content with AI
                    import random
                    
                    # Prepare prompt
                    prompt = f"""You are writing content for a LaTeX academic document.

Section Name: {section_name}
Description: {description}

Generate 2-3 paragraphs of professional academic content for this section. 
The content should be:
- Well-structured and coherent
- Appropriate for an academic paper
- Related to the description provided
- Written in LaTeX format (you can use \\cite{{}} for citations if needed)
- 150-300 words in length

Only return the section content, no additional formatting or section headers."""
                    
                    # Try with key rotation (up to 3 attempts)
                    max_retries = 3
                    generation_success = False
                    
                    for attempt in range(max_retries):
                        try:
                            selected_key = random.choice(api_keys)
                            genai.configure(api_key=selected_key)
                            # Use Gemini 2.5 Flash for better quality
                            model = genai.GenerativeModel("gemini-2.5-flash")
                            
                            print(f"  🤖 Generating content (attempt {attempt + 1}/{max_retries})...")
                            response = model.generate_content(prompt)
                            section_content = response.text.strip()
                            print(f"  ✅ Generated {len(section_content)} characters of content")
                            print(f"  Preview: {section_content[:100]}...")
                            generation_success = True
                            break
                            
                        except Exception as retry_error:
                            if "quota" in str(retry_error).lower() or "429" in str(retry_error):
                                print(f"  ⚠️ Quota exceeded on attempt {attempt + 1}, trying another key...")
                                # Remove the failed key from list for this session
                                if selected_key in api_keys:
                                    api_keys.remove(selected_key)
                                if not api_keys:
                                    print(f"  ❌ All keys exhausted")
                                    break
                                continue
                            else:
                                # Other error, don't retry
                                print(f"  ❌ Generation error: {type(retry_error).__name__}")
                                break
                    
                    if not generation_success:
                        print(f"  Using description as content")
                        section_content = description
                    
            except Exception as e:
                print(f"  ❌ Setup failed: {type(e).__name__}: {str(e)[:100]}")
                print(f"  Using description as content")
                section_content = description
        else:
            print(f"  ℹ️ No description provided, creating empty section")
            section_content = ""
        
        # Step 3: Add the section at determined position
        if target_section is None:
            # Add at end
            return self.add_section_at_end(content, section_name, section_content)
        else:
            # Find the target section
            pattern = r'\\(?:sub)*section\*?\{[^}]*' + re.escape(target_section.lower()) + r'[^}]*\}'
            match = re.search(pattern, content, re.IGNORECASE)
            
            if not match:
                print(f"  ⚠️ Target section '{target_section}' not found, adding at end")
                return self.add_section_at_end(content, section_name, section_content)
            
            if position == "before":
                # Add before the target section
                insert_pos = match.start()
                new_section = f"\n\\section{{{section_name}}}\n{section_content}\n\n"
                modified = content[:insert_pos] + new_section + content[insert_pos:]
                print(f"  ✅ Added section '{section_name}' before '{target_section}'")
                return modified, 1
            else:  # position == "after"
                return self.add_section_after(content, target_section, section_name, section_content)
    
    # ========================================================================
    # AUTO-DETECTION AND UTILITY
    # ========================================================================
    
    def add_auto(self, content: str, item_type: str, **kwargs) -> Tuple[str, int]:
        """
        Auto-detect and add based on item type.
        
        Args:
            content: LaTeX document content
            item_type: Type of addition ("sentence_start", "sentence_end", "section_start", 
                      "section_end", "section_after", "content_start", "content_end")
            **kwargs: Additional arguments based on type
        
        Returns:
            Tuple of (modified_content, success_count)
        """
        if item_type == "sentence_start":
            return self.add_sentence_at_section_start(
                content, kwargs.get('section_name'), kwargs.get('sentence')
            )
        elif item_type == "sentence_end":
            return self.add_sentence_after_section(
                content, kwargs.get('section_name'), kwargs.get('sentence')
            )
        elif item_type == "sentence_document_end":
            return self.add_sentence_at_document_end(content, kwargs.get('sentence'))
        elif item_type == "section_start":
            return self.add_section_at_start(
                content, kwargs.get('section_name'), kwargs.get('section_content', '')
            )
        elif item_type == "section_end":
            return self.add_section_at_end(
                content, kwargs.get('section_name'), kwargs.get('section_content', '')
            )
        elif item_type == "section_after":
            return self.add_section_after(
                content, kwargs.get('after_section'), 
                kwargs.get('section_name'), kwargs.get('section_content', '')
            )
        elif item_type == "content_start":
            return self.add_content_to_section_start(
                content, kwargs.get('section_name'), kwargs.get('new_content')
            )
        elif item_type == "content_end":
            return self.add_content_to_section_end(
                content, kwargs.get('section_name'), kwargs.get('new_content')
            )
        else:
            print(f"  ❌ Unknown item type: {item_type}")
            return content, 0


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example LaTeX document
    sample_doc = r"""
\documentclass{article}
\begin{document}

\section{Introduction}
This is the introduction section with some content.

\section{Related works}
This section discusses related works.

\section{Data}
This section describes the data used.

\end{document}
"""
    
    adder = SimpleAdder()
    
    print("=" * 80)
    print("TESTING SIMPLE ADDER")
    print("=" * 80)
    
    # Test 1: Add sentence at start of section
    modified, count = adder.add_sentence_at_section_start(
        sample_doc, "Introduction", 
        "This is a new first sentence"
    )
    
    # Test 2: Add sentence at end of section
    modified, count = adder.add_sentence_after_section(
        modified, "Related works",
        "This concludes the related works section"
    )
    
    # Test 3: Add new section after Data
    modified, count = adder.add_section_after(
        modified, "Data", "Methodology",
        "This section describes our methodology."
    )
    
    # Test 4: Add content to section
    modified, count = adder.add_content_to_section_end(
        modified, "Introduction",
        "Additional paragraph for introduction section."
    )
    
    print("\n" + "=" * 80)
    print("FINAL MODIFIED DOCUMENT:")
    print("=" * 80)
    print(modified)
