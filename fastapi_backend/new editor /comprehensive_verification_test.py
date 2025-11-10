"""
COMPREHENSIVE VERIFICATION TEST

This test:
1. Performs ALL operations (replace, remove, add, format)
2. Shows PROOF of each modification (before/after snippets)
3. Verifies changes in the .tex file
4. Makes all modifications BOLD for visibility
5. Compiles the final result to PDF
"""

import os
import re
from workflow import LatexEditorWorkflow
from pathlib import Path


class ComprehensiveVerificationTest:
    """Test all operations with detailed verification"""
    
    def __init__(self):
        self.tex_file = '/Users/abdullah/Desktop/Techinoid/final with fast api copy/input /glucobench/glucobench .tex'
        self.output_dir = './verification_test_output'
        self.workflow = LatexEditorWorkflow(output_dir=self.output_dir)
        
        # Read original content
        with open(self.tex_file, 'r', encoding='utf-8') as f:
            self.original_content = f.read()
        
        print(f"📖 Original file size: {len(self.original_content)} characters\n")
    
    def show_snippet(self, content: str, search_text: str, context_chars: int = 80):
        """Show a snippet of text with context"""
        # Find the text (case insensitive)
        pattern = re.compile(re.escape(search_text), re.IGNORECASE)
        match = pattern.search(content)
        
        if match:
            start = max(0, match.start() - context_chars)
            end = min(len(content), match.end() + context_chars)
            snippet = content[start:end]
            
            # Highlight the found text
            snippet = snippet.replace(match.group(), f">>>{match.group()}<<<")
            return snippet
        else:
            return f"[NOT FOUND: {search_text}]"
    
    def verify_modification(self, before_content: str, after_content: str, 
                          target: str, operation: str):
        """Verify that a modification was made"""
        
        print(f"\n{'─'*70}")
        print(f"VERIFICATION: {operation}")
        print(f"{'─'*70}")
        
        # Count occurrences
        before_count = len(re.findall(re.escape(target), before_content, re.IGNORECASE))
        after_count = len(re.findall(re.escape(target), after_content, re.IGNORECASE))
        
        print(f"Target: '{target}'")
        print(f"Before: {before_count} occurrences")
        print(f"After:  {after_count} occurrences")
        
        if operation == 'remove':
            expected_after = 0
            success = after_count < before_count
        elif operation == 'replace':
            success = after_count < before_count
        else:
            success = True
        
        if success:
            print("✅ VERIFIED")
        else:
            print("⚠️  WARNING: Unexpected result")
        
        # Show before/after snippets
        print(f"\nBEFORE snippet:")
        print(f"  {self.show_snippet(before_content, target)}")
        
        if after_count > 0 or operation != 'remove':
            print(f"\nAFTER snippet:")
            print(f"  {self.show_snippet(after_content, target)}")
        
        return success
    
    def test_all_operations(self):
        """Run comprehensive test with all operations"""
        
        print("\n" + "="*70)
        print("COMPREHENSIVE VERIFICATION TEST - ALL OPERATIONS")
        print("="*70)
        print(f"Input: {self.tex_file}")
        print(f"Output: {self.output_dir}")
        print("="*70 + "\n")
        
        current_content = self.original_content
        all_verifications = []
        operation_number = 0
        
        # ====================================================================
        # TEST 1: REPLACE OPERATIONS + BOLD
        # ====================================================================
        
        print("\n" + "="*70)
        print("TEST 1: REPLACE OPERATIONS (with bold formatting)")
        print("="*70)
        
        replace_tests = [
            ("accuracy", "precision"),
            ("dataset", "corpus"),
            ("model", "framework"),
        ]
        
        for old_word, new_word in replace_tests:
            operation_number += 1
            print(f"\n[{operation_number}] REPLACE: '{old_word}' → '{new_word}'")
            
            # Do replacement
            modified, result = self.workflow.editor.edit(
                current_content,
                f"replace '{old_word}' with '{new_word}'"
            )
            
            if result['success']:
                # Verify the replacement
                verified = self.verify_modification(
                    current_content, modified, old_word, 'replace'
                )
                all_verifications.append(('replace', old_word, new_word, verified))
                
                # Update content
                current_content = modified
                
                # Now make the new word BOLD
                operation_number += 1
                print(f"\n[{operation_number}] BOLD: '{new_word}'")
                
                current_content, bold_result = self.workflow.editor.edit(
                    current_content,
                    f"make '{new_word}' bold"
                )
                
                if bold_result['success']:
                    print(f"✅ Made '{new_word}' bold ({bold_result['changes']} occurrences)")
                    all_verifications.append(('bold', new_word, None, True))
            else:
                print(f"❌ Replace failed: {result.get('error')}")
                all_verifications.append(('replace', old_word, new_word, False))
        
        # ====================================================================
        # TEST 2: REMOVE OPERATIONS
        # ====================================================================
        
        print("\n" + "="*70)
        print("TEST 2: REMOVE OPERATIONS")
        print("="*70)
        
        remove_tests = [
            "however",
            "therefore",
            "moreover",
        ]
        
        for word in remove_tests:
            operation_number += 1
            print(f"\n[{operation_number}] REMOVE: '{word}'")
            
            before_content = current_content
            modified, result = self.workflow.editor.edit(
                current_content,
                f"remove the word '{word}'"
            )
            
            if result['success']:
                verified = self.verify_modification(
                    before_content, modified, word, 'remove'
                )
                all_verifications.append(('remove', word, None, verified))
                current_content = modified
            else:
                print(f"⚠️  Word '{word}' not found or remove failed")
                all_verifications.append(('remove', word, None, False))
        
        # ====================================================================
        # TEST 3: FORMAT OPERATIONS
        # ====================================================================
        
        print("\n" + "="*70)
        print("TEST 3: FORMAT OPERATIONS")
        print("="*70)
        
        format_tests = [
            ("glucose", "highlight", "yellow"),
            ("diabetes", "highlight", "red"),
            ("prediction", "bold", None),
            ("neural network", "bold", None),
            ("et al.", "italic", None),
        ]
        
        for text, format_type, color in format_tests:
            operation_number += 1
            
            if format_type == "highlight":
                query = f"highlight '{text}' in {color}"
                operation_desc = f"HIGHLIGHT: '{text}' in {color}"
            elif format_type == "bold":
                query = f"make '{text}' bold"
                operation_desc = f"BOLD: '{text}'"
            else:  # italic
                query = f"make '{text}' italic"
                operation_desc = f"ITALIC: '{text}'"
            
            print(f"\n[{operation_number}] {operation_desc}")
            
            before_content = current_content
            modified, result = self.workflow.editor.edit(current_content, query)
            
            if result['success']:
                print(f"✅ {format_type.upper()}: {result['changes']} occurrences")
                
                # Show proof in the content
                if format_type == "highlight":
                    proof_pattern = f"\\colorbox{{{color}}}"
                elif format_type == "bold":
                    proof_pattern = "\\textbf{"
                else:
                    proof_pattern = "\\textit{"
                
                proof_count = modified.count(proof_pattern) - before_content.count(proof_pattern)
                print(f"   Proof: Added {proof_count} {format_type} LaTeX commands")
                
                all_verifications.append((format_type, text, color, result['changes'] > 0))
                current_content = modified
            else:
                print(f"⚠️  Format failed: {result.get('error')}")
                all_verifications.append((format_type, text, color, False))
        
        # ====================================================================
        # SAVE AND COMPILE
        # ====================================================================
        
        print("\n" + "="*70)
        print("SAVING AND COMPILING FINAL DOCUMENT")
        print("="*70)
        
        # Save the modified content
        output_tex = os.path.join(self.output_dir, "comprehensive_verified.tex")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        with open(output_tex, 'w', encoding='utf-8') as f:
            f.write(current_content)
        
        print(f"💾 Saved modified .tex: {output_tex}")
        print(f"   File size: {len(current_content)} characters")
        print(f"   Change: {len(current_content) - len(self.original_content):+d} characters")
        
        # Compile to PDF
        print(f"\n🔨 Compiling to PDF...")
        pdf_path = self.workflow._compile_pdf(output_tex)
        
        if pdf_path:
            print(f"✅ PDF compiled: {pdf_path}")
            pdf_size = os.path.getsize(pdf_path)
            print(f"   PDF size: {pdf_size:,} bytes")
        else:
            print(f"❌ PDF compilation failed")
        
        # ====================================================================
        # FINAL SUMMARY
        # ====================================================================
        
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        
        successful = sum(1 for _, _, _, verified in all_verifications if verified)
        total = len(all_verifications)
        
        print(f"\nTotal Operations: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success Rate: {successful/total*100:.1f}%\n")
        
        print("Operation Breakdown:")
        operation_types = {}
        for op_type, _, _, verified in all_verifications:
            if op_type not in operation_types:
                operation_types[op_type] = {'total': 0, 'success': 0}
            operation_types[op_type]['total'] += 1
            if verified:
                operation_types[op_type]['success'] += 1
        
        for op_type, counts in sorted(operation_types.items()):
            success = counts['success']
            total = counts['total']
            print(f"  {op_type:12} {success}/{total} successful")
        
        print("\n" + "="*70)
        print("DETAILED VERIFICATION LOG")
        print("="*70)
        
        for i, (op_type, text, extra, verified) in enumerate(all_verifications, 1):
            status = "✅" if verified else "❌"
            if extra:
                print(f"{i:2}. {status} {op_type:12} '{text}' → '{extra}'")
            else:
                print(f"{i:2}. {status} {op_type:12} '{text}'")
        
        print("\n" + "="*70)
        print("OUTPUT FILES")
        print("="*70)
        print(f"📄 Modified .tex: {output_tex}")
        if pdf_path:
            print(f"📄 Compiled .pdf: {pdf_path}")
        print("="*70 + "\n")
        
        # ====================================================================
        # VISUAL COMPARISON
        # ====================================================================
        
        print("\n" + "="*70)
        print("VISUAL COMPARISON - LaTeX COMMANDS ADDED")
        print("="*70)
        
        # Count LaTeX formatting commands
        commands = {
            '\\textbf{': ('Bold', 0, 0),
            '\\textit{': ('Italic', 0, 0),
            '\\colorbox{yellow}': ('Yellow Highlight', 0, 0),
            '\\colorbox{red}': ('Red Highlight', 0, 0),
        }
        
        for cmd in commands:
            before_count = self.original_content.count(cmd)
            after_count = current_content.count(cmd)
            commands[cmd] = (commands[cmd][0], before_count, after_count)
        
        for cmd, (name, before, after) in commands.items():
            if after > before:
                print(f"  {name:20} Before: {before:3} → After: {after:3} (Added: {after-before:2})")
        
        print("="*70 + "\n")
        
        return {
            'total_operations': total,
            'successful_operations': successful,
            'tex_output': output_tex,
            'pdf_output': pdf_path,
            'verifications': all_verifications
        }


def main():
    """Run the comprehensive verification test"""
    
    test = ComprehensiveVerificationTest()
    result = test.test_all_operations()
    
    print("\n" + "="*70)
    print("🎉 COMPREHENSIVE TEST COMPLETE")
    print("="*70)
    print(f"✅ {result['successful_operations']}/{result['total_operations']} operations verified")
    print(f"📄 Output: {result['tex_output']}")
    print(f"📄 PDF: {result['pdf_output']}")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
