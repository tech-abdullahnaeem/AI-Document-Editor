"""
INTEGRATED DOCUMENT EDITOR
Combines QueryParser with all editing functionalities.

Natural language interface for document editing:
- Parse user query with AI
- Execute appropriate editing action
- Return formatted result
"""

import time
from typing import Dict, Tuple, Optional
from query_parser import QueryParser
from replace import SimpleReplacer
from format import SimpleFormatter
from remove import SimpleRemover
from add import SimpleAdder
from modify import SimpleModifier


class DocumentEditor:
    """
    Unified document editor with natural language interface.
    
    Workflow:
    1. User provides natural language query
    2. QueryParser extracts intent and action
    3. Appropriate editor (Replace/Format/Remove/Add) executes action
    4. Return modified content and status
    """
    
    def __init__(self):
        """Initialize all editing components"""
        print("\n" + "="*70)
        print("INITIALIZING DOCUMENT EDITOR")
        print("="*70)
        
        # Initialize query parser
        self.parser = QueryParser()
        
        # Initialize editing engines
        self.replacer = SimpleReplacer()
        self.formatter = SimpleFormatter()
        self.remover = SimpleRemover()
        self.adder = SimpleAdder()
        self.modifier = SimpleModifier()
        
        print("="*70)
        print("✅ DOCUMENT EDITOR READY")
        print("="*70 + "\n")
    
    def edit(self, content: str, user_query: str) -> Tuple[str, Dict]:
        """
        Main entry point - parse query and execute editing action.
        
        Args:
            content: LaTeX document content
            user_query: Natural language query from user
            
        Returns:
            Tuple of (modified_content, result_info)
            
        Example:
            >>> editor = DocumentEditor()
            >>> content, info = editor.edit(latex_content, "highlight 'accuracy' in yellow")
            >>> print(info['operation'])  # 'format'
            >>> print(info['changes'])    # 3 (replacements made)
        """
        print("\n" + "="*70)
        print(f"USER QUERY: {user_query}")
        print("="*70)
        
        # Parse the query
        parsed = self.parser.parse_query(user_query)
        
        if not parsed:
            return content, {
                'success': False,
                'error': 'Failed to parse query',
                'operation': None
            }
        
        # Extract action details
        operation = parsed['operation']
        action = parsed['action']
        target = parsed['target']
        target_type = parsed['target_type']
        
        print(f"\n📋 Executing: {action}")
        print(f"   Operation: {operation}")
        print(f"   Target: '{target}'")
        print(f"   Type: {target_type}")
        
        # Execute the appropriate action
        try:
            if operation == 'replace':
                result_content, result_info = self._execute_replace(content, parsed)
            elif operation == 'format':
                result_content, result_info = self._execute_format(content, parsed)
            elif operation == 'remove':
                result_content, result_info = self._execute_remove(content, parsed)
            elif operation == 'add':
                result_content, result_info = self._execute_add(content, parsed)
            elif operation == 'modify':
                result_content, result_info = self._execute_modify(content, parsed)
            else:
                return content, {
                    'success': False,
                    'error': f'Unknown operation: {operation}',
                    'operation': operation
                }
            
            # Add parsed info to result
            result_info.update({
                'operation': operation,
                'action': action,
                'parsed_query': parsed
            })
            
            print("\n" + "="*70)
            print(f"✅ {action.upper()} COMPLETE")
            print("="*70 + "\n")
            
            return result_content, result_info
            
        except Exception as e:
            print(f"\n❌ Error executing {action}: {e}")
            import traceback
            traceback.print_exc()
            
            return content, {
                'success': False,
                'error': str(e),
                'operation': operation,
                'action': action
            }
    
    def _execute_replace(self, content: str, parsed: Dict) -> Tuple[str, Dict]:
        """Execute replace operation"""
        action = parsed['action']
        target = parsed['target']
        new_text = parsed['new_text']
        target_type = parsed['target_type']
        
        # Map action to replacer method
        if action == 'replace_word':
            modified, count = self.replacer.replace_word(content, target, new_text)
        elif action == 'replace_phrase':
            modified, count = self.replacer.replace_phrase(content, target, new_text)
        elif action == 'replace_sentence':
            modified, count = self.replacer.replace_sentence(content, target, new_text)
        elif action == 'replace_section_content':
            section = parsed.get('section_name', target)
            convert = parsed.get('convert_to_latex', False)
            modified, count = self.replacer.replace_section_content(
                content, section, new_text, convert_to_latex=convert
            )
        else:
            # Auto-detect
            modified, count = self.replacer.replace_auto(content, target, new_text)
        
        return modified, {
            'success': True,  # Always succeed, even with 0 changes (just means no matches)
            'changes': count,
            'method': action
        }
    
    def _execute_format(self, content: str, parsed: Dict) -> Tuple[str, Dict]:
        """Execute format operation"""
        action = parsed['action']
        target = parsed['target']
        format_type = parsed['format_action']
        color = parsed.get('color', 'yellow')
        target_type = parsed['target_type']
        
        # Map action to formatter method
        method_map = {
            # Highlight
            'highlight_word': lambda: self.formatter.highlight_word(content, target, color),
            'highlight_phrase': lambda: self.formatter.highlight_phrase(content, target, color),
            'highlight_sentence': lambda: self.formatter.highlight_sentence(content, target, color),
            'highlight_paragraph': lambda: self.formatter.highlight_paragraph(content, target, color),
            
            # Bold
            'bold_word': lambda: self.formatter.bold_word(content, target),
            'bold_phrase': lambda: self.formatter.bold_phrase(content, target),
            'bold_sentence': lambda: self.formatter.bold_sentence(content, target),
            'bold_paragraph': lambda: self.formatter.bold_paragraph(content, target),
            
            # Italic
            'italic_word': lambda: self.formatter.italic_word(content, target),
            'italic_phrase': lambda: self.formatter.italic_phrase(content, target),
            'italic_sentence': lambda: self.formatter.italic_sentence(content, target),
            'italic_paragraph': lambda: self.formatter.italic_paragraph(content, target),
        }
        
        if action in method_map:
            modified, count = method_map[action]()
        else:
            # Fallback to auto-detect
            if format_type == 'bold':
                modified, count = self.formatter.bold_auto(content, target)
            elif format_type == 'italic':
                modified, count = self.formatter.italic_auto(content, target)
            else:
                modified, count = self.formatter.highlight_auto(content, target, color)
        
        return modified, {
            'success': True,  # Always succeed, even with 0 changes (just means no matches)
            'changes': count,
            'method': action,
            'format_type': format_type,
            'color': color if format_type == 'highlight' else None
        }
    
    def _execute_remove(self, content: str, parsed: Dict) -> Tuple[str, Dict]:
        """Execute remove operation"""
        action = parsed['action']
        target = parsed['target']
        target_type = parsed['target_type']
        
        # Map action to remover method
        if action == 'remove_word':
            modified, count = self.remover.remove_word(content, target)
        elif action == 'remove_phrase':
            modified, count = self.remover.remove_phrase(content, target)
        elif action == 'remove_sentence':
            modified, count = self.remover.remove_sentence(content, target)
        elif action == 'remove_section':
            section = parsed.get('section_name', target)
            modified, count = self.remover.remove_section(content, section)
        elif action == 'remove_table':
            # Support "all" or specific table identifier
            table_id = target if target else None
            modified, count = self.remover.remove_table(content, table_id)
        elif action == 'remove_equation':
            # Support different equation types
            eq_type = target if target else None
            modified, count = self.remover.remove_equation(content, eq_type)
        else:
            # Fallback: try to detect what to remove based on target
            if target_type == 'table':
                modified, count = self.remover.remove_table(content, target)
            elif target_type == 'equation':
                modified, count = self.remover.remove_equation(content, target)
            else:
                # Generic removal based on target text
                modified, count = self.remover.remove_phrase(content, target)
        
        return modified, {
            'success': True,  # Always succeed, even with 0 changes (just means no matches)
            'changes': count,
            'method': action
        }
    
    def _execute_add(self, content: str, parsed: Dict) -> Tuple[str, Dict]:
        """Execute add operation"""
        action = parsed['action']
        target = parsed.get('target', '')  # The section to add after (for positioning)
        section_name = parsed.get('section_name', target)  # The NEW section name
        new_text = parsed['new_text']  # The content/description
        position = parsed.get('position', 'after')
        
        # Clean target section name - remove common words that might be included
        if target:
            # Remove trailing words like "section", "the", etc.
            target_cleaned = target.strip()
            for word in [' section', ' Section', ' SECTION', 'the ', 'The ', 'a ']:
                target_cleaned = target_cleaned.replace(word, '').strip()
            target = target_cleaned
        
        # Map action to adder method
        if action == 'add_section':
            # Add a new section
            # section_name is the NAME of the new section
            # target is where to position it (after which section)
            # new_text is the CONTENT/DESCRIPTION of the new section
            
            # Use smart section addition for better positioning and AI content generation
            print(f"\n🎯 Adding section with smart positioning:")
            print(f"  Section Name: {section_name}")
            print(f"  Description: {new_text}")
            if target:
                print(f"  Target: {target}")
            if position:
                print(f"  Position: {position}")
            modified, count = self.adder.add_section_smart(
                content, section_name, new_text, 
                target_section_hint=target if target else None,
                position_hint=position if position else None
            )
            
        elif action == 'add_content_to_section':
            # Add content to existing section
            # position can be "start" or "end"
            modified, count = self.adder.add_content_to_section(
                content, target, new_text, position="end"
            )
        else:
            # Default to add_content_to_section
            modified, count = self.adder.add_content_to_section(
                content, target, new_text, position="end"
            )
        
        return modified, {
            'success': True,  # Always succeed, even with 0 changes (just means section not found)
            'changes': count,
            'method': action,
            'position': position
        }
    
    def _execute_modify(self, content: str, parsed: Dict) -> Tuple[str, Dict]:
        """Execute modify operation - AI-powered section improvement"""
        action = parsed['action']
        section_name = parsed.get('section_name', parsed['target'])
        instruction = parsed.get('new_text', parsed.get('instruction', ''))
        
        # Use AI to modify the section
        modified, count = self.modifier.modify_section_ai(
            content, 
            section_name, 
            instruction
        )
        
        return modified, {
            'success': True,  # Always succeed, AI operations always complete
            'changes': count,
            'method': action,
            'instruction': instruction
        }
    
    def batch_edit(self, content: str, queries: list, delay: float = 1.5) -> Tuple[str, list]:
        """
        Execute multiple editing operations in sequence with delays.
        
        Args:
            content: LaTeX document content
            queries: List of natural language queries
            delay: Delay in seconds between operations (default: 1.5s)
            
        Returns:
            Tuple of (final_content, list_of_results)
        """
        print("\n" + "="*70)
        print(f"BATCH EDITING: {len(queries)} operations")
        print(f"Delay between operations: {delay}s")
        print(f"Estimated time: ~{len(queries) * delay / 60:.1f} minutes")
        print("="*70)
        
        current_content = content
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}] Processing: '{query}'")
            
            # Add delay before each operation (except first)
            if i > 1:
                print(f"  ⏳ Waiting {delay}s to avoid rate limits...")
                time.sleep(delay)
            
            modified, result = self.edit(current_content, query)
            
            if result['success']:
                current_content = modified
                results.append(result)
                print(f"  ✅ Success: {result['changes']} changes")
            else:
                results.append(result)
                print(f"  ⚠️  Failed: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*70)
        print(f"BATCH COMPLETE: {sum(1 for r in results if r['success'])}/{len(queries)} succeeded")
        print("="*70 + "\n")
        
        return current_content, results


def main():
    """Demo usage"""
    # Sample LaTeX content
    sample_latex = r"""
\documentclass{article}
\begin{document}

\section{Introduction}
Machine learning is a powerful tool. Deep learning has revolutionized AI.
The accuracy of our model is 95\%.

\section{Methods}
We used a neural network with 10 layers. The dataset contains 1000 samples.

\section{Results}
The results show significant improvement. Machine learning outperformed traditional methods.

\end{document}
"""
    
    # Create editor
    editor = DocumentEditor()
    
    # Test single edit
    print("\n" + "="*70)
    print("DEMO: Single Edit")
    print("="*70)
    
    modified, result = editor.edit(sample_latex, "highlight 'Machine learning' in yellow")
    print(f"\nResult: {result}")
    
    # Test batch edit
    print("\n" + "="*70)
    print("DEMO: Batch Edit")
    print("="*70)
    
    queries = [
        "replace 'accuracy' with 'precision'",
        "make 'neural network' bold",
        "remove the word 'significant'",
    ]
    
    final_content, results = editor.batch_edit(sample_latex, queries)
    print(f"\nFinal results: {len([r for r in results if r['success']])} successful")


if __name__ == "__main__":
    main()
