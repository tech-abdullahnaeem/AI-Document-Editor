"""
Data models for LaTeX style issues and fixes
"""
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


class IssueType(str, Enum):
    """Types of LaTeX style/layout issues"""
    ALIGNMENT_ISSUE = "alignment_issue"
    LAYOUT_MISMATCH = "layout_mismatch"
    TABLE_NOT_CENTERED = "table_not_centered"
    TABLE_PLACEMENT_MISSING = "table_placement_missing"
    FIGURE_NOT_CENTERED = "figure_not_centered"
    AUTHOR_BLOCK_INCORRECT = "author_block_incorrect"
    COLUMN_WIDTH_WRONG = "column_width_wrong"
    INDENTATION_INCONSISTENT = "indentation_inconsistent"
    SPACING_INCORRECT = "spacing_incorrect"
    FLOAT_PLACEMENT_WRONG = "float_placement_wrong"
    TITLE_NOT_CENTERED = "title_not_centered"
    SECTION_FORMAT_WRONG = "section_format_wrong"
    FORMATTING_INCONSISTENT = "formatting_inconsistent"
    MATH_ENVIRONMENT_ERROR = "math_environment_error"  # Broken formulas from PDF conversion


class Severity(str, Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LatexIssue(BaseModel):
    """Represents a detected LaTeX style/layout issue"""
    type: IssueType
    severity: Severity
    description: str
    element: str  # e.g., "author", "table", "figure"
    location: Optional[Dict[str, int]] = None  # line numbers
    current_code: str
    context: Optional[str] = None  # surrounding code
    expected_format: Optional[str] = None
    
    class Config:
        use_enum_values = True


class RetrievedExample(BaseModel):
    """A retrieved example from knowledge base"""
    code: str
    description: str
    document_format: str
    element_type: str
    similarity_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FixSuggestion(BaseModel):
    """A suggested fix for a LaTeX issue"""
    original_code: str
    fixed_code: str
    explanation: str
    confidence_score: float
    retrieved_examples: List[RetrievedExample] = Field(default_factory=list)
    changes_made: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Results of validating a fix"""
    compilation_success: bool
    style_compliance_score: float
    improvements: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class DocumentAnalysis(BaseModel):
    """Complete analysis of a LaTeX document"""
    document_format: str
    detected_issues: List[LatexIssue] = Field(default_factory=list)
    document_structure: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FixReport(BaseModel):
    """Complete report of fixes applied"""
    original_latex: str
    fixed_latex: str
    issues_fixed: List[LatexIssue] = Field(default_factory=list)
    fixes_applied: List[FixSuggestion] = Field(default_factory=list)
    validation_result: Optional[ValidationResult] = None
    processing_time: float
    success: bool
