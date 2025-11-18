"""
LLM-based fix generator
Uses retrieved examples to generate context-aware fixes
"""
import os
import re
from typing import List, Dict, Optional
import google.generativeai as genai
from loguru import logger

from models import LatexIssue, FixSuggestion, RetrievedExample
from config import settings


def get_enum_value(enum_field):
    """Helper to safely get enum value"""
    return enum_field.value if hasattr(enum_field, 'value') else str(enum_field)


class FixGenerator:
    """
    Generate LaTeX fixes using LLM with retrieved examples
    """
    
    def __init__(self):
        # Configure Gemini
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.primary_model = genai.GenerativeModel(settings.PRIMARY_MODEL)
            self.fallback_model = genai.GenerativeModel(settings.FALLBACK_MODEL)
        else:
            logger.warning("GEMINI_API_KEY not set. Fix generation will be limited.")
            self.primary_model = None
            self.fallback_model = None
    
    def generate_fix(self, issue: LatexIssue, 
                    retrieved_examples: List[RetrievedExample],
                    document_format: str,
                    context: Optional[str] = None) -> FixSuggestion:
        """
        Generate a fix for a specific issue using retrieved examples
        
        Args:
            issue: The detected issue
            retrieved_examples: Examples retrieved from knowledge base
            document_format: Target format (IEEE, ACM, etc.)
            context: Additional context (surrounding code)
        
        Returns:
            FixSuggestion with generated fix
        """
        logger.info(f"Generating fix for: {issue.type}")
        
        # Build prompt
        prompt = self._build_prompt(issue, retrieved_examples, document_format, context)
        
        # Generate with LLM
        fixed_code, confidence = self._generate_with_llm(prompt, issue.current_code)
        
        # Extract changes made
        changes = self._identify_changes(issue.current_code, fixed_code)
        
        return FixSuggestion(
            original_code=issue.current_code,
            fixed_code=fixed_code,
            explanation=self._generate_explanation(issue, changes),
            confidence_score=confidence,
            retrieved_examples=retrieved_examples,
            changes_made=changes
        )
    
    def _build_prompt(self, issue: LatexIssue,
                     examples: List[RetrievedExample],
                     document_format: str,
                     context: Optional[str]) -> str:
        """Build comprehensive prompt for LLM"""
        
        # Format examples
        examples_text = self._format_examples(examples)
        
        prompt = f"""You are a LaTeX formatting expert specializing in {document_format} style.

ISSUE DETECTED:
Type: {get_enum_value(issue.type)}
Severity: {get_enum_value(issue.severity)}
Description: {issue.description}
Element: {issue.element}

INCORRECT CODE (from API output):
```latex
{issue.current_code}
```

CORRECT EXAMPLES FROM {document_format.upper()} TEMPLATES:
{examples_text}

{f"SURROUNDING CONTEXT:" if context else ""}
{f"```latex{chr(10)}{context}{chr(10)}```" if context else ""}

REQUIREMENTS:
- Document Format: {document_format}
- {issue.expected_format if issue.expected_format else "Follow standard LaTeX best practices"}

YOUR TASK:
Fix the incorrect code to match the {document_format} style requirements shown in the examples above.

SPECIFIC FIXES NEEDED:
"""
        
        # Add type-specific instructions
        issue_type_str = get_enum_value(issue.type)
        if issue_type_str == "table_not_centered":
            prompt += """- Add \\centering command after \\begin{table}
- Ensure proper placement parameters [htbp]
- Check table width is appropriate for document layout
"""
        elif issue_type_str == "figure_not_centered":
            prompt += """- Add \\centering command after \\begin{figure}
- Ensure proper placement parameters [htbp]
- Verify figure width is appropriate
"""
        elif issue_type_str == "author_block_incorrect":
            prompt += """- Use proper centering for author block
- Follow format-specific author commands if applicable
- Ensure proper spacing and alignment
"""
        elif issue_type_str == "column_width_wrong":
            prompt += """- Replace \\linewidth with \\columnwidth for two-column documents
- Adjust widths for proper column fitting
- Consider using spanning environment if needed
"""
        
        prompt += """
OUTPUT INSTRUCTIONS:
1. Provide ONLY the corrected LaTeX code
2. Do NOT include markdown code blocks or explanations
3. Maintain all original content, only fix formatting/structure
4. Follow the style shown in the examples exactly
5. Ensure the fix is minimal and precise

CORRECTED CODE:
"""
        
        return prompt
    
    def _format_examples(self, examples: List[RetrievedExample]) -> str:
        """Format retrieved examples for prompt"""
        if not examples:
            return "No specific examples found. Use LaTeX best practices."
        
        formatted = []
        for i, example in enumerate(examples[:3], 1):  # Show top 3
            formatted.append(f"""
Example {i} ({example.document_format} - Similarity: {example.similarity_score:.2f}):
Description: {example.description}
```latex
{example.code}
```
""")
        
        return "\n".join(formatted)
    
    def _generate_with_llm(self, prompt: str, original_code: str) -> tuple[str, float]:
        """Generate fix using LLM"""
        if not self.primary_model:
            logger.warning("No LLM model available, returning original code")
            return original_code, 0.0
        
        try:
            # Try primary model
            response = self.primary_model.generate_content(prompt)
            fixed_code = self._extract_code_from_response(response.text)
            confidence = 0.9
            
        except Exception as e:
            logger.warning(f"Primary model failed: {e}, trying fallback...")
            try:
                response = self.fallback_model.generate_content(prompt)
                fixed_code = self._extract_code_from_response(response.text)
                confidence = 0.7
            except Exception as e2:
                logger.error(f"Fallback model also failed: {e2}")
                fixed_code = original_code
                confidence = 0.0
        
        return fixed_code, confidence
    
    def _extract_code_from_response(self, response_text: str) -> str:
        """Extract LaTeX code from LLM response"""
        # Remove markdown code blocks if present
        code = response_text.strip()
        
        # Remove ```latex and ``` markers
        code = re.sub(r'^```latex\s*\n', '', code)
        code = re.sub(r'^```\s*\n', '', code)
        code = re.sub(r'\n```\s*$', '', code)
        
        # Remove any leading/trailing explanations
        # Look for LaTeX commands as indicators of code
        if '\\' in code:
            # Try to extract just the LaTeX portion
            lines = code.split('\n')
            latex_lines = []
            in_latex = False
            
            for line in lines:
                if '\\' in line or in_latex:
                    latex_lines.append(line)
                    in_latex = True
                elif in_latex and line.strip() == '':
                    latex_lines.append(line)
            
            if latex_lines:
                code = '\n'.join(latex_lines).strip()
        
        return code
    
    def _identify_changes(self, original: str, fixed: str) -> List[str]:
        """Identify what changed between original and fixed code"""
        changes = []
        
        # Check for added centering
        if '\\centering' in fixed and '\\centering' not in original:
            changes.append("Added \\centering command")
        
        if '\\begin{center}' in fixed and '\\begin{center}' not in original:
            changes.append("Added centering environment")
        
        # Check for placement parameters
        placement_pattern = r'\\begin\{(?:table|figure)\*?\}\[([htbp]+)\]'
        old_placement = re.search(placement_pattern, original)
        new_placement = re.search(placement_pattern, fixed)
        
        if new_placement and not old_placement:
            changes.append(f"Added placement parameters [{new_placement.group(1)}]")
        elif new_placement and old_placement and new_placement.group(1) != old_placement.group(1):
            changes.append(f"Changed placement from [{old_placement.group(1)}] to [{new_placement.group(1)}]")
        
        # Check for width changes
        if '\\columnwidth' in fixed and '\\linewidth' in original:
            changes.append("Changed \\linewidth to \\columnwidth")
        
        # Check for spanning environment
        if ('table*' in fixed or 'figure*' in fixed) and \
           ('table*' not in original and 'figure*' not in original):
            changes.append("Changed to column-spanning environment")
        
        # Check for format-specific commands
        if '\\IEEEauthorblock' in fixed and '\\IEEEauthorblock' not in original:
            changes.append("Applied IEEE author formatting")
        
        return changes if changes else ["Formatting adjustments applied"]
    
    def _generate_explanation(self, issue: LatexIssue, changes: List[str]) -> str:
        """Generate human-readable explanation"""
        explanation = f"Fixed {get_enum_value(issue.type)}: {issue.description}\n\n"
        explanation += "Changes made:\n"
        for change in changes:
            explanation += f"- {change}\n"
        
        return explanation
