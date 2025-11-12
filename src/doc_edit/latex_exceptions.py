"""
Custom exceptions for LaTeX editing operations
Provides specific error types for better error handling and user feedback
"""


class LaTeXEditingError(Exception):
    """Base exception for all LaTeX editing errors"""
    pass


class MathModeError(LaTeXEditingError):
    """
    Raised when an operation cannot be performed safely in math mode
    
    Example: Trying to highlight text that appears inside $...$ or equation environments
    """
    
    def __init__(self, message: str, position: int = None, context: str = None):
        self.position = position
        self.context = context
        super().__init__(message)
    
    def __str__(self):
        msg = super().__str__()
        if self.position is not None:
            msg += f" at position {self.position}"
        if self.context:
            msg += f"\nContext: {self.context}"
        return msg


class StructureError(LaTeXEditingError):
    """
    Raised when LaTeX document structure is invalid or cannot be parsed
    
    Example: Unmatched braces, missing \end{document}, malformed environments
    """
    
    def __init__(self, message: str, line_number: int = None, details: str = None):
        self.line_number = line_number
        self.details = details
        super().__init__(message)
    
    def __str__(self):
        msg = super().__str__()
        if self.line_number is not None:
            msg += f" at line {self.line_number}"
        if self.details:
            msg += f"\nDetails: {self.details}"
        return msg


class ValidationError(LaTeXEditingError):
    """
    Raised when modifications fail validation checks
    
    Example: Not all word occurrences were replaced, syntax errors after editing
    """
    
    def __init__(self, message: str, expected: any = None, actual: any = None):
        self.expected = expected
        self.actual = actual
        super().__init__(message)
    
    def __str__(self):
        msg = super().__str__()
        if self.expected is not None and self.actual is not None:
            msg += f"\nExpected: {self.expected}, Actual: {self.actual}"
        return msg


class SectionNotFoundError(LaTeXEditingError):
    """
    Raised when a requested section cannot be found
    
    Example: Trying to remove "Related Work" section that doesn't exist
    """
    
    def __init__(self, section_title: str, available_sections: list = None):
        self.section_title = section_title
        self.available_sections = available_sections
        message = f"Section '{section_title}' not found"
        if available_sections:
            message += f"\nAvailable sections: {', '.join(available_sections)}"
        super().__init__(message)


class CompilationError(LaTeXEditingError):
    """
    Raised when LaTeX compilation fails
    
    Example: PDF generation fails due to syntax errors introduced by edits
    """
    
    def __init__(self, message: str, log_excerpt: str = None, error_lines: list = None):
        self.log_excerpt = log_excerpt
        self.error_lines = error_lines
        super().__init__(message)
    
    def __str__(self):
        msg = super().__str__()
        if self.error_lines:
            msg += f"\nError at lines: {', '.join(map(str, self.error_lines))}"
        if self.log_excerpt:
            msg += f"\nLog excerpt:\n{self.log_excerpt}"
        return msg


class ParserNotInitializedError(LaTeXEditingError):
    """
    Raised when an operation requires a parser but it hasn't been initialized
    
    Example: Calling safe_highlight_word() before parse_document_structure()
    """
    
    def __init__(self, operation: str):
        self.operation = operation
        message = f"Parser not initialized. Call parse_document_structure() before {operation}"
        super().__init__(message)


class UnsafeOperationError(LaTeXEditingError):
    """
    Raised when an operation would break LaTeX document structure
    
    Example: Trying to delete content that would orphan child sections
    """
    
    def __init__(self, message: str, suggestion: str = None):
        self.suggestion = suggestion
        super().__init__(message)
    
    def __str__(self):
        msg = super().__str__()
        if self.suggestion:
            msg += f"\nSuggestion: {self.suggestion}"
        return msg


# Error recovery helpers
class ErrorRecovery:
    """Helper class for error recovery suggestions"""
    
    @staticmethod
    def suggest_math_mode_fix(word: str, position: int) -> str:
        """Suggest how to highlight text in math mode"""
        return f"To highlight '{word}' at position {position}, use \\text{{{word}}} wrapper first, then apply highlighting"
    
    @staticmethod
    def suggest_structure_fix(error_type: str) -> str:
        """Suggest fixes for structure errors"""
        suggestions = {
            "unmatched_braces": "Check for missing {{ or }} in LaTeX commands",
            "missing_end": "Ensure all \\begin{{env}} have matching \\end{{env}}",
            "nested_math": "Check for nested $ $ delimiters or mixed math modes",
            "malformed_command": "Verify LaTeX command syntax: \\command{arg}"
        }
        return suggestions.get(error_type, "Review LaTeX syntax and structure")
    
    @staticmethod
    def suggest_validation_fix(expected: int, actual: int, operation: str) -> str:
        """Suggest fixes for validation failures"""
        if expected > actual:
            return f"{operation} incomplete: {expected-actual} occurrences missed. Try re-running or check for edge cases."
        elif actual > expected:
            return f"{operation} over-applied: {actual-expected} extra modifications. Check for unintended matches."
        return "Verification failed. Check operation parameters."


# Example usage and tests
if __name__ == "__main__":
    print("Testing LaTeX Editing Exceptions\n")
    
    # Test MathModeError
    try:
        raise MathModeError(
            "Cannot highlight 'glucose' in math mode",
            position=1234,
            context="$glucose_{level}$"
        )
    except MathModeError as e:
        print(f"✓ MathModeError: {e}\n")
    
    # Test StructureError
    try:
        raise StructureError(
            "Unmatched braces detected",
            line_number=45,
            details="Missing closing brace for \\section command"
        )
    except StructureError as e:
        print(f"✓ StructureError: {e}\n")
    
    # Test ValidationError
    try:
        raise ValidationError(
            "Word replacement incomplete",
            expected=5,
            actual=3
        )
    except ValidationError as e:
        print(f"✓ ValidationError: {e}\n")
    
    # Test SectionNotFoundError
    try:
        raise SectionNotFoundError(
            "Related Work",
            available_sections=["Introduction", "Methods", "Results", "Conclusion"]
        )
    except SectionNotFoundError as e:
        print(f"✓ SectionNotFoundError: {e}\n")
    
    # Test error recovery
    print("Error Recovery Suggestions:")
    print(f"  Math mode: {ErrorRecovery.suggest_math_mode_fix('glucose', 1234)}")
    print(f"  Structure: {ErrorRecovery.suggest_structure_fix('unmatched_braces')}")
    print(f"  Validation: {ErrorRecovery.suggest_validation_fix(5, 3, 'Replacement')}")
    
    print("\n✅ All exception tests passed!")
