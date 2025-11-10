"""
INTELLIGENT QUERY PARSER
Uses Gemini AI to understand user intent for ALL document editing operations.

Extracts:
- Operation type: replace, remove, add, format
- Action: For format (highlight, bold, italic)
- Target text: what to modify
- New text: replacement or addition content
- Location: section name, position
- Additional parameters: color, convert_to_latex, etc.
"""

import re
from typing import Dict, Optional
import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv
import json
import time


class QueryParser:
    """Parse natural language queries to extract formatting intent"""
    
    def __init__(self):
        """Initialize with API key rotation"""
        # Load .env file
        env_path = Path(__file__).parent.parent.parent / '.env'
        load_dotenv(env_path)
        
        # Collect all API keys
        self.api_keys = []
        self.key_names = []
        
        # Primary key
        primary_key = os.getenv('GEMINI_API_KEY')
        if primary_key and primary_key.strip():
            self.api_keys.append(primary_key)
            self.key_names.append('GEMINI_API_KEY')
        
        # Backup keys (API_KEY1 to API_KEY39)
        for i in range(1, 40):
            key = os.getenv(f'API_KEY{i}')
            if key and key.strip():
                self.api_keys.append(key)
                self.key_names.append(f'API_KEY{i}')
        
        # Rotation state
        self.current_key_index = 0
        self.total_keys = len(self.api_keys)
        self.rate_limited_keys = {}  # Track rate-limited keys with timestamps
        self.key_usage_count = [0] * self.total_keys
        self.successful_requests = [0] * self.total_keys
        self.rate_limit_reset_time = 60  # Reset rate limit status after 60 seconds
        
        if self.api_keys:
            # Configure Gemini with first key
            model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
            self.model_name = model_name
            genai.configure(api_key=self.api_keys[0])
            
            # Create generation config for longer outputs (reused for all API calls)
            self.generation_config = genai.types.GenerationConfig(
                max_output_tokens=4096,  # Much higher limit for complete JSON
                temperature=0.1,  # Low temperature for consistent structured output
                top_p=0.8,
                top_k=40,
            )
            
            print(f"  🤖 Query Parser initialized with {len(self.api_keys)} API keys")
            print(f"  📊 Estimated capacity: {self.total_keys * 15} queries/minute")
        else:
            self.generation_config = None
            print("  ⚠️  No API keys found - query parsing disabled")
    
    def _get_next_key(self) -> Optional[str]:
        """
        Get the next available API key in rotation.
        Skips rate-limited keys automatically.
        Automatically resets keys that have been rate-limited for more than reset_time seconds.
        
        Returns:
            Next available API key or None if all exhausted
        """
        if not self.api_keys:
            return None
        
        # Check and reset keys that have been rate-limited for long enough
        current_time = time.time()
        keys_to_reset = []
        for idx, limited_time in list(self.rate_limited_keys.items()):
            if current_time - limited_time >= self.rate_limit_reset_time:
                keys_to_reset.append(idx)
        
        if keys_to_reset:
            for idx in keys_to_reset:
                del self.rate_limited_keys[idx]
            print(f"  🔄 Reset {len(keys_to_reset)} rate-limited key(s) after cooldown")
        
        # If all keys are rate-limited, reset all
        if len(self.rate_limited_keys) >= self.total_keys:
            print(f"  ⚠️  All {self.total_keys} keys rate-limited - resetting all")
            self.rate_limited_keys.clear()
            return None
        
        # Find next non-rate-limited key
        attempts = 0
        while attempts < self.total_keys:
            current_idx = self.current_key_index
            key = self.api_keys[current_idx]
            
            # Move to next for next call
            self.current_key_index = (self.current_key_index + 1) % self.total_keys
            
            # Skip if rate-limited
            if current_idx in self.rate_limited_keys:
                attempts += 1
                continue
            
            # Track usage
            self.key_usage_count[current_idx] += 1
            
            # Reconfigure Gemini with new key (model will be created fresh in parse_query)
            genai.configure(api_key=key)
            
            return key
        
        return None
    
    def _mark_rate_limited(self, key: str):
        """Mark a key as rate-limited with timestamp"""
        try:
            idx = self.api_keys.index(key)
            self.rate_limited_keys[idx] = time.time()  # Store timestamp
            available = self.total_keys - len(self.rate_limited_keys)
            print(f"  ⚠️  {self.key_names[idx]} rate-limited | {available}/{self.total_keys} keys available (will reset in {self.rate_limit_reset_time}s)")
        except ValueError:
            pass
    
    def _mark_successful(self, key: str):
        """Mark a successful request and remove from rate-limited list if present"""
        try:
            idx = self.api_keys.index(key)
            self.successful_requests[idx] += 1
            # If this key was marked as rate-limited, remove it since it's working now
            if idx in self.rate_limited_keys:
                del self.rate_limited_keys[idx]
        except ValueError:
            pass
    
    def parse_query(self, user_query: str) -> Dict[str, any]:
        """
        Parse user's natural language query to extract editing intent.
        
        Supports ALL operations:
        - REPLACE: "replace X with Y", "change X to Y"
        - REMOVE: "remove X", "delete section X"
        - ADD: "add X to section Y", "insert X after Y"
        - FORMAT: "highlight X", "make X bold", "italicize X"
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Dictionary with:
            - operation: 'replace', 'remove', 'add', 'format'
            - action: specific method to call (e.g., 'replace_word', 'bold_sentence', 'remove_section')
            - target: the text/section to modify
            - new_text: replacement or new content (for replace/add)
            - target_type: 'word', 'phrase', 'sentence', 'section', 'paragraph'
            - format_action: 'highlight', 'bold', 'italic' (for format operation)
            - color: color for highlighting
            - section_name: section name (for add/remove section)
            - position: 'before', 'after', 'replace' (for add operation)
            - convert_to_latex: bool (for add/replace section content)
            - confidence: confidence score (0-1)
        """
        print(f"\n🔍 Parsing query: '{user_query[:80]}...'")
        
        if not self.api_keys or not self.generation_config:
            print("  ❌ AI model not available")
            return self._fallback_parse(user_query)
        
        # Construct comprehensive prompt for Gemini
        prompt = f"""Analyze this user query and extract the document editing intent.

USER QUERY: "{user_query}"

Extract the following information and respond ONLY with a valid JSON object:
{{
    "operation": "replace" | "remove" | "add" | "format" | "modify",
    "action": "specific_method_name",
    "target": "text or section to modify",
    "new_text": "replacement or new content (null if not applicable)",
    "target_type": "word" | "phrase" | "sentence" | "section" | "paragraph",
    "format_action": "highlight" | "bold" | "italic" (null if operation != format),
    "color": "yellow|red|green|blue|cyan|magenta|orange" (null if not highlight),
    "section_name": "section name" (null if not section operation),
    "position": "before" | "after" | "replace" (null if not add operation),
    "convert_to_latex": true | false,
    "confidence": 0.0 to 1.0
}}

OPERATION TYPES:

1. REPLACE - User wants to change existing text with exact new text
   Examples: "replace X with Y", "change accuracy to precision", "swap deep learning with neural networks"
   
2. REMOVE - User wants to delete content
   Examples: "remove the word dataset", "delete section Methods", "remove this sentence: X", "remove all tables", "delete table", "remove tables"
   IMPORTANT: When user says "remove/delete table/tables", use action="remove_table" NOT "remove_phrase"
   
3. ADD - User wants to insert new content
   Examples: "add X to section Y", "insert X after Introduction", "append X to Methods"
   
4. FORMAT - User wants to style text (highlight, bold, italic)
   Examples: "highlight accuracy in yellow", "make deep learning bold", "italicize ResNet"

5. MODIFY - User wants to improve/change section content using AI (NOT exact replacement)
   Examples: "modify related works to be more concise", "improve introduction focusing on X", "make methods section more professional"
   Keywords: "modify", "improve", "make better", "enhance", "refine", "revise", "update"

RULES:
1. operation: Determine the primary intent (replace, remove, add, format, or modify)
2. action: Construct the specific method name based on operation and target_type:
   - REPLACE: "replace_word", "replace_phrase", "replace_sentence", "replace_section_content", "replace_auto"
   - REMOVE: "remove_word", "remove_phrase", "remove_sentence", "remove_section", "remove_table", "remove_equation"
   - ADD: "add_section", "add_content_to_section"
   - FORMAT: "highlight_word", "highlight_phrase", "highlight_sentence", "highlight_paragraph",
             "bold_word", "bold_phrase", "bold_sentence", "bold_paragraph",
             "italic_word", "italic_phrase", "italic_sentence", "italic_paragraph"
   - MODIFY: "modify_section_ai" (always use this for modify operations)
3. target: Extract EXACT text/section user wants to modify
   - For "remove all tables" or "delete tables", target should be "all"
   - For "remove table", target should be "all" (default to removing all if not specific)
4. new_text: For replace/add - the new content; For modify - the instruction/focus
5. target_type: word, phrase, sentence, section, paragraph, table, or equation
   - Use "table" when user mentions table/tables/tabular
   - Use "equation" when user mentions equation/formula/math
6. format_action: Only for format operations
7. color: Only for highlight operations (default "yellow")
8. section_name: Extract section name for section-level operations
9. position: For add operations - where to insert (before/after/replace)
10. convert_to_latex: true if user provides plain text for section content
11. confidence: 0.0-1.0 based on clarity of query

EXAMPLES:

Query: "replace the word accuracy with precision"
Response: {{"operation": "replace", "action": "replace_word", "target": "accuracy", "new_text": "precision", "target_type": "word", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 1.0}}

Query: "remove section Results"
Response: {{"operation": "remove", "action": "remove_section", "target": "Results", "new_text": null, "target_type": "section", "format_action": null, "color": null, "section_name": "Results", "position": null, "convert_to_latex": false, "confidence": 0.95}}

Query: "remove all tables"
Response: {{"operation": "remove", "action": "remove_table", "target": "all", "new_text": null, "target_type": "table", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 0.95}}

Query: "delete table"
Response: {{"operation": "remove", "action": "remove_table", "target": "all", "new_text": null, "target_type": "table", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 0.9}}

Query: "remove tables"
Response: {{"operation": "remove", "action": "remove_table", "target": "all", "new_text": null, "target_type": "table", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 0.9}}

Query: "remove table with caption Test Results"
Response: {{"operation": "remove", "action": "remove_table", "target": "Test Results", "new_text": null, "target_type": "table", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 0.9}}

Query: "add this to Methods section: We used cross-validation"
Response: {{"operation": "add", "action": "add_content_to_section", "target": "Methods", "new_text": "We used cross-validation", "target_type": "section", "format_action": null, "color": null, "section_name": "Methods", "position": "replace", "convert_to_latex": true, "confidence": 0.9}}

Query: "highlight machine learning in red"
Response: {{"operation": "format", "action": "highlight_phrase", "target": "machine learning", "new_text": null, "target_type": "phrase", "format_action": "highlight", "color": "red", "section_name": null, "position": null, "convert_to_latex": false, "confidence": 1.0}}

Query: "change deep learning to neural networks in the entire document"
Response: {{"operation": "replace", "action": "replace_phrase", "target": "deep learning", "new_text": "neural networks", "target_type": "phrase", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 1.0}}

Query: "make the word dataset bold"
Response: {{"operation": "format", "action": "bold_word", "target": "dataset", "new_text": null, "target_type": "word", "format_action": "bold", "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 1.0}}

Query: "delete this sentence: The model failed to converge"
Response: {{"operation": "remove", "action": "remove_sentence", "target": "The model failed to converge", "new_text": null, "target_type": "sentence", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 0.95}}

Query: "replace Introduction section content with: This paper presents a novel approach"
Response: {{"operation": "replace", "action": "replace_section_content", "target": "Introduction", "new_text": "This paper presents a novel approach", "target_type": "section", "format_action": null, "color": null, "section_name": "Introduction", "position": null, "convert_to_latex": true, "confidence": 0.9}}

Query: "modify the related works section to be more professional and concise, focusing on key limitations"
Response: {{"operation": "modify", "action": "modify_section_ai", "target": "related works", "new_text": "be more professional and concise, focusing on key limitations", "target_type": "section", "format_action": null, "color": null, "section_name": "related works", "position": null, "convert_to_latex": false, "confidence": 0.9}}

Query: "improve introduction to highlight main contributions"
Response: {{"operation": "modify", "action": "modify_section_ai", "target": "introduction", "new_text": "highlight main contributions", "target_type": "section", "format_action": null, "color": null, "section_name": "introduction", "position": null, "convert_to_latex": false, "confidence": 0.85}}

Query: "italicize this paragraph: Machine learning has transformed healthcare..."
Response: {{"operation": "format", "action": "italic_paragraph", "target": "Machine learning has transformed healthcare...", "new_text": null, "target_type": "paragraph", "format_action": "italic", "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 0.85}}

Query: "remove the phrase 'not applicable'"
Response: {{"operation": "remove", "action": "remove_phrase", "target": "not applicable", "new_text": null, "target_type": "phrase", "format_action": null, "color": null, "section_name": null, "position": null, "convert_to_latex": false, "confidence": 0.9}}

Respond ONLY with the JSON object, no other text."""

        # Try with rotation on rate limit
        max_retries = min(5, self.total_keys)  # Try up to 5 different keys
        
        for attempt in range(max_retries):
            try:
                # Get current key (first attempt uses initial key)
                if attempt > 0:
                    current_key = self._get_next_key()
                    if not current_key:
                        print(f"  ❌ No more keys available after {attempt} attempts")
                        return self._fallback_parse(user_query)
                else:
                    current_key = self.api_keys[self.current_key_index]
                
                # Configure the API with the current key
                genai.configure(api_key=current_key)
                model = genai.GenerativeModel(
                    self.model_name,
                    generation_config=self.generation_config
                )
                
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                
                # Mark successful
                self._mark_successful(current_key)
                
                # Clean up response - remove markdown code blocks if present
                response_text = response_text.replace('```json', '').replace('```', '').strip()
                
                # Parse JSON
                result = json.loads(response_text)
                
                # Validate result
                if self._validate_result(result):
                    print(f"  ✅ Parsed successfully:")
                    print(f"     Operation: {result['operation']}")
                    print(f"     Action: {result['action']}")
                    print(f"     Target: '{result['target']}'")
                    print(f"     Type: {result['target_type']}")
                    if result.get('new_text'):
                        preview = result['new_text'][:50] + '...' if len(result['new_text']) > 50 else result['new_text']
                        print(f"     New text: '{preview}'")
                    if result.get('format_action'):
                        print(f"     Format: {result['format_action']}")
                    if result.get('color'):
                        print(f"     Color: {result['color']}")
                    if result.get('section_name'):
                        print(f"     Section: {result['section_name']}")
                    if result.get('position'):
                        print(f"     Position: {result['position']}")
                    print(f"     Confidence: {result['confidence']:.0%}")
                    return result
                else:
                    print(f"  ⚠️  Invalid result from AI, using fallback")
                    print(f"  Debug - Response: {response_text[:300]}")
                    return self._fallback_parse(user_query)
                    
            except json.JSONDecodeError as e:
                print(f"  ⚠️  JSON parse error: {e}")
                print(f"  Response: {response_text[:200]}")
                return self._fallback_parse(user_query)
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                
                # Check if it's a REAL rate limit error (not just gRPC warnings)
                # Look for specific Google API rate limit indicators
                is_rate_limit = (
                    ('429' in error_msg and 'resource' in error_msg.lower() and 'exhaust' in error_msg.lower()) or
                    ('RESOURCE_EXHAUSTED' in error_msg.upper()) or
                    ('ResourceExhausted' in error_msg) or
                    ('quota' in error_msg.lower() and 'exceeded' in error_msg.lower()) or
                    ('rate limit exceeded' in error_msg.lower())
                )
                
                # Ignore ALTS warnings - these are harmless gRPC messages
                if 'ALTS' in error_msg or 'alts_credentials' in error_msg:
                    # This is just a gRPC warning, not a real error
                    print(f"  ⚠️  Unexpected error during parsing: {error_type}: {error_msg[:100]}")
                    return self._fallback_parse(user_query)
                
                if is_rate_limit:
                    self._mark_rate_limited(current_key)
                    if attempt < max_retries - 1:
                        print(f"  🔄 Rotating to next key (attempt {attempt + 2}/{max_retries})")
                        continue
                    else:
                        print(f"  ⚠️  All retry attempts exhausted, using fallback")
                        return self._fallback_parse(user_query)
                else:
                    # Non-rate-limit error
                    print(f"  ⚠️  Error: {error_type}: {error_msg[:200]}")
                    return self._fallback_parse(user_query)
        
        # If we get here, all retries failed
        return self._fallback_parse(user_query)
    
    def _validate_result(self, result: Dict) -> bool:
        """Validate the parsed result"""
        required_keys = ['operation', 'action', 'target', 'target_type', 'confidence']
        
        # Check all required keys present
        if not all(key in result for key in required_keys):
            return False
        
        # Validate operation
        if result['operation'] not in ['replace', 'remove', 'add', 'format', 'modify']:
            return False
        
        # Validate action (should be a string and not empty)
        if not result['action'] or not isinstance(result['action'], str):
            return False
        
        # Validate target (should not be empty)
        if not result['target'] or not isinstance(result['target'], str):
            return False
        
        # Validate target_type
        if result['target_type'] not in ['word', 'phrase', 'sentence', 'section', 'paragraph', 'table', 'equation']:
            return False
        
        # Validate confidence
        if not (0 <= result['confidence'] <= 1):
            return False
        
        # Validate format_action if operation is format
        if result['operation'] == 'format':
            if 'format_action' not in result or result['format_action'] not in ['highlight', 'bold', 'italic']:
                return False
        
        return True
    
    def _fallback_parse(self, user_query: str) -> Dict[str, any]:
        """
        Fallback parsing using regex patterns when AI is unavailable.
        """
        print("  🔧 Using fallback pattern matching")
        
        query_lower = user_query.lower()
        
        # Determine operation type
        operation = 'format'  # default
        if any(word in query_lower for word in ['modify', 'improve', 'enhance', 'refine', 'revise', 'update', 'make better', 'rewrite']):
            operation = 'modify'
        elif any(word in query_lower for word in ['replace', 'change', 'swap', 'substitute']):
            operation = 'replace'
        elif any(word in query_lower for word in ['remove', 'delete', 'erase']):
            operation = 'remove'
        elif any(word in query_lower for word in ['add', 'insert', 'append', 'include']):
            operation = 'add'
        elif any(word in query_lower for word in ['highlight', 'bold', 'italic']):
            operation = 'format'
        
        # Determine format action (if format operation)
        format_action = None
        if operation == 'format':
            if 'bold' in query_lower:
                format_action = 'bold'
            elif 'italic' in query_lower:
                format_action = 'italic'
            else:
                format_action = 'highlight'
        
        # Extract target and new_text
        target = None
        new_text = None
        
        # Try to find text in quotes
        quote_matches = re.findall(r'["\']([^"\']+)["\']', user_query)
        
        if operation == 'replace' and len(quote_matches) >= 2:
            target = quote_matches[0]
            new_text = quote_matches[1]
        elif operation == 'replace':
            # Try pattern: "replace X with Y"
            match = re.search(r'replace\s+(.+?)\s+with\s+(.+?)(?:\s+in|\s*$)', query_lower)
            if match:
                target = match.group(1).strip()
                new_text = match.group(2).strip()
            else:
                # Try pattern: "change X to Y"
                match = re.search(r'change\s+(.+?)\s+to\s+(.+?)(?:\s+in|\s*$)', query_lower)
                if match:
                    target = match.group(1).strip()
                    new_text = match.group(2).strip()
        
        elif operation == 'remove':
            if quote_matches:
                target = quote_matches[0]
            else:
                # Try pattern: "remove X"
                match = re.search(r'(?:remove|delete)\s+(?:the\s+)?(?:word|phrase|sentence|section)?\s*(.+)', query_lower)
                if match:
                    target = match.group(1).strip()
        
        elif operation == 'add':
            # Check if adding a new section
            if 'new section' in query_lower or 'add section' in query_lower or re.search(r'section\s+["\']', user_query):
                target_type = 'section'
                
                # Try multiple patterns to extract section name
                # Pattern 1: section called/named 'X'
                match = re.search(r'section\s+(?:called|named)\s+["\']?([^"\']+?)["\']?\s+(?:before|after)', user_query, re.IGNORECASE)
                if not match:
                    # Pattern 2: section 'X' before/after
                    match = re.search(r'section\s+["\']([^"\']+)["\']?\s+(?:before|after)', user_query, re.IGNORECASE)
                if not match:
                    # Pattern 3: add 'X' section before/after
                    match = re.search(r'add\s+(?:section\s+)?["\']([^"\']+)["\']?\s+(?:section\s+)?(?:before|after)', user_query, re.IGNORECASE)
                
                if match:
                    # Found section name
                    section_name = match.group(1).strip()
                    target = section_name  # Store as target for now
                    
                    # Extract where to add it (the reference section)
                    pos_match = re.search(r'(?:before|after)\s+(?:the\s+)?(.+?)(?:\.|$)', user_query[match.end():], re.IGNORECASE)
                    if pos_match:
                        # The reference section becomes the target, section_name stays as is
                        reference_section = pos_match.group(1).strip()
                        # Don't swap - keep target as section_name, we'll handle this in validation
                        new_text = ""  # No description in this case
                    else:
                        new_text = ""
                else:
                    # Fallback: try general pattern
                    match = re.search(r'add\s+(.+?)\s+to\s+(?:section\s+)?(.+?)(?:\s*$)', query_lower, re.IGNORECASE)
                    if match:
                        new_text = match.group(1).strip()
                        target = match.group(2).strip()
            else:
                # Try pattern: "add X to section Y"
                match = re.search(r'add\s+(.+?)\s+to\s+(?:section\s+)?(.+?)(?:\s*$)', query_lower, re.IGNORECASE)
                if match:
                    new_text = match.group(1).strip()
                    target = match.group(2).strip()
                elif quote_matches:
                    new_text = quote_matches[0]
                    # Extract section name
                    match = re.search(r'(?:to|in)\s+(?:section\s+)?(\w+)', query_lower)
                    if match:
                        target = match.group(1)
        
        elif operation == 'format':
            if quote_matches:
                target = quote_matches[0]
            else:
                # Try to extract after keywords
                keywords = ['word', 'phrase', 'sentence', 'text', 'the']
                for keyword in keywords:
                    pattern = rf'{keyword}\s+(.+?)(?:\s+in\s+|\s+to\s+|$)'
                    match = re.search(pattern, query_lower)
                    if match:
                        target = match.group(1).strip()
                        break
        
        elif operation == 'modify':
            # For modify: extract section name and instruction
            # Pattern: "modify <section> to <instruction>"
            match = re.search(r'modify\s+(?:the\s+)?(.+?)\s+(?:section\s+)?(?:to|content|by)?\s*(.+)', query_lower)
            if match:
                target = match.group(1).strip()
                new_text = match.group(2).strip()  # instruction
            else:
                # Try: "improve/enhance <section> <instruction>"
                match = re.search(r'(?:improve|enhance|refine|revise)\s+(?:the\s+)?(.+?)\s+(?:section\s+)?(?:to|by)?\s*(.+)', query_lower)
                if match:
                    target = match.group(1).strip()
                    new_text = match.group(2).strip()
                else:
                    # Just get section name
                    words = query_lower.replace('modify', '').replace('improve', '').replace('section', '').strip().split()
                    if words:
                        target = words[0]
                        new_text = ' '.join(words[1:]) if len(words) > 1 else "make better"
        
        # If still no target, use heuristic
        if not target:
            target = user_query.split()[-1] if user_query.split() else user_query
        
        # Determine target type
        if operation == 'modify':
            target_type = 'section'  # modify is always for sections
        elif any(word in query_lower for word in ['table', 'tables', 'tabular']):
            target_type = 'table'
            # For table removal, default to "all" if not specific
            if operation == 'remove' and not any(word in query_lower for word in ['caption', 'label', 'with']):
                target = 'all'
        elif any(word in query_lower for word in ['equation', 'formula', 'math', 'equations']):
            target_type = 'equation'
            if operation == 'remove' and 'all' in query_lower:
                target = 'all'
        elif 'section' in query_lower or (target and target[0].isupper() and len(target.split()) == 1):
            target_type = 'section'
        elif 'paragraph' in query_lower:
            target_type = 'paragraph'
        elif any(word in query_lower for word in ['sentence', 'statement']):
            target_type = 'sentence'
        elif any(word in query_lower for word in ['word', 'term']):
            target_type = 'word'
        else:
            # Check if target ends with sentence punctuation
            if target and any(target.strip().endswith(p) for p in ['.', '!', '?', '."', '!"', '?"']):
                target_type = 'sentence'
            else:
                # Use word count heuristic
                word_count = len(target.split()) if target else 0
                if word_count == 1:
                    target_type = 'word'
                elif word_count <= 4:
                    target_type = 'phrase'
                elif word_count <= 15:
                    target_type = 'sentence'
                else:
                    target_type = 'paragraph'
        
        # Determine color (for highlight)
        color = None
        if format_action == 'highlight':
            color = 'yellow'  # default
            colors = ['red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'orange', 'pink']
            for c in colors:
                if c in query_lower:
                    color = c
                    break
        
        # Extract section name
        section_name = None
        if operation == 'add' and target_type == 'section':
            # For add section operations, try to extract both the new section name and reference section
            # Pattern: "Add section 'X' before/after Y"
            match = re.search(r'(?:add|create)\s+(?:a\s+)?(?:new\s+)?section\s+["\']?([^"\']+?)["\']?\s+(?:before|after)\s+(?:the\s+)?(.+?)(?:\.|$)', user_query, re.IGNORECASE)
            if match:
                section_name = match.group(1).strip()
                # Update target to be the reference section, not the new section name
                target = match.group(2).strip()
            else:
                # Fallback: section_name is same as target
                section_name = target
        elif target_type == 'section':
            section_name = target
        else:
            match = re.search(r'(?:section|in)\s+([A-Z]\w+)', user_query)
            if match:
                section_name = match.group(1)
        
        # Determine position for add operations
        position = None
        if operation == 'add':
            if 'before' in query_lower:
                position = 'before'
            elif 'after' in query_lower:
                position = 'after'
            else:
                position = 'replace'  # default - replace section content
        
        # Determine if content should be converted to LaTeX
        convert_to_latex = operation in ['add', 'replace'] and target_type == 'section'
        
        # Construct the action method name
        action = self._construct_action_name(operation, target_type, format_action)
        
        result = {
            'operation': operation,
            'action': action,
            'target': target,
            'new_text': new_text,
            'target_type': target_type,
            'format_action': format_action,
            'color': color,
            'section_name': section_name,
            'position': position,
            'convert_to_latex': convert_to_latex,
            'confidence': 0.6  # Lower confidence for fallback
        }
        
        print(f"  ✅ Fallback parse:")
        print(f"     Operation: {result['operation']}")
        print(f"     Action: {result['action']}")
        print(f"     Target: '{result['target']}'")
        if result.get('new_text'):
            print(f"     New text: '{result['new_text'][:50]}...'")
        
        return result
    
    def _construct_action_name(self, operation: str, target_type: str, format_action: str = None) -> str:
        """
        Construct the specific action method name based on operation type and target type.
        
        Args:
            operation: 'replace', 'remove', 'add', 'format', or 'modify'
            target_type: 'word', 'phrase', 'sentence', 'section', 'paragraph'
            format_action: 'highlight', 'bold', or 'italic' (for format operations)
            
        Returns:
            Method name string (e.g., 'replace_word', 'highlight_phrase', 'remove_section')
        """
        if operation == 'modify':
            return 'modify_section_ai'
        
        elif operation == 'replace':
            if target_type == 'section':
                return 'replace_section_content'
            else:
                return f'replace_{target_type}'
        
        elif operation == 'remove':
            return f'remove_{target_type}'
        
        elif operation == 'add':
            if target_type == 'section':
                return 'add_section'
            else:
                return 'add_content_to_section'
        
        elif operation == 'format':
            if format_action:
                return f'{format_action}_{target_type}'
            else:
                return f'highlight_{target_type}'  # default to highlight
        
        return 'unknown_action'
    
    def parse_batch_queries(self, queries: list) -> list:
        """
        Parse multiple queries at once.
        
        Args:
            queries: List of user queries
            
        Returns:
            List of parsed results
        """
        print(f"\n📋 Parsing {len(queries)} queries...")
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}]")
            result = self.parse_query(query)
            results.append(result)
        
        return results


# ============================================================================
# TEST FUNCTIONS
# ============================================================================

def test_query_parser():
    """Test the query parser with various queries covering ALL operations"""
    
    parser = QueryParser()
    
    test_queries = [
        # REPLACE operations
        "replace the word accuracy with precision",
        "change deep learning to neural networks",
        "replace 'machine learning' with 'artificial intelligence'",
        "swap CGM with continuous glucose monitor",
        
        # REMOVE operations
        "remove the word dataset",
        "delete section Results",
        "remove this sentence: The model failed to converge",
        "delete the phrase 'not applicable'",
        
        # ADD operations
        "add this to Methods section: We used cross-validation",
        "insert new content in Introduction: This paper presents a novel approach",
        "append to Discussion: Future work should explore this",
        "add 'Our methodology includes data preprocessing' to Methods",
        
        # FORMAT operations - Highlight
        "highlight the word accuracy in yellow",
        "highlight machine learning in red",
        "highlight this sentence: The model achieved 95% accuracy",
        
        # FORMAT operations - Bold
        "make 'deep learning' bold",
        "bold the phrase neural networks",
        "make this sentence bold: We achieved state-of-the-art results",
        
        # FORMAT operations - Italic
        "italicize machine learning",
        "make the word ResNet italic",
        "italicize the term convolutional neural networks",
        
        # Complex queries
        "replace Introduction section content with: This research addresses a critical gap",
        "remove all occurrences of the word 'significant'",
        "highlight 'high performance' in green and make it bold",
    ]
    
    print("="*80)
    print("COMPREHENSIVE QUERY PARSER TEST")
    print("Testing ALL Operations: REPLACE, REMOVE, ADD, FORMAT")
    print("="*80)
    
    results = parser.parse_batch_queries(test_queries)
    
    print("\n" + "="*80)
    print("SUMMARY OF PARSED QUERIES")
    print("="*80)
    
    # Group by operation
    operations = {'replace': [], 'remove': [], 'add': [], 'format': []}
    for query, result in zip(test_queries, results):
        operations[result['operation']].append((query, result))
    
    for op_type in ['replace', 'remove', 'add', 'format']:
        if operations[op_type]:
            print(f"\n{'='*80}")
            print(f"{op_type.upper()} OPERATIONS ({len(operations[op_type])} queries)")
            print('='*80)
            
            for i, (query, result) in enumerate(operations[op_type], 1):
                print(f"\n{i}. Query: {query}")
                print(f"   → Operation: {result['operation']}")
                print(f"   → Target: '{result['target']}'")
                print(f"   → Type: {result['target_type']}")
                
                if result.get('new_text'):
                    preview = result['new_text'][:60] + '...' if len(result['new_text']) > 60 else result['new_text']
                    print(f"   → New text: '{preview}'")
                
                if result.get('format_action'):
                    print(f"   → Format: {result['format_action']}")
                
                if result.get('color'):
                    print(f"   → Color: {result['color']}")
                
                if result.get('section_name'):
                    print(f"   → Section: {result['section_name']}")
                
                if result.get('position'):
                    print(f"   → Position: {result['position']}")
                
                if result.get('convert_to_latex'):
                    print(f"   → Convert to LaTeX: Yes")
                
                print(f"   → Confidence: {result['confidence']:.0%}")
    
    print("\n" + "="*80)
    print("✅ Query Parser Test Complete")
    print(f"   Total queries tested: {len(test_queries)}")
    print(f"   REPLACE: {len(operations['replace'])}")
    print(f"   REMOVE: {len(operations['remove'])}")
    print(f"   ADD: {len(operations['add'])}")
    print(f"   FORMAT: {len(operations['format'])}")
    print("="*80)


if __name__ == '__main__':
    test_query_parser()
