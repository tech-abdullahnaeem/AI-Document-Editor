"""
Main pipeline for RAG-based LaTeX fixing
Orchestrates the entire detection -> retrieval -> generation -> validation flow
"""
import time
from typing import List, Optional
from loguru import logger

from models import DocumentAnalysis, LatexIssue, FixReport, FixSuggestion, ValidationResult
from detectors.style_detector import StyleIssueDetector
from rag.retriever import RAGRetriever
from rag.fix_generator import FixGenerator
from utils.latex_validator import LatexValidator
from config import settings


class LatexFixerPipeline:
    """
    Complete pipeline for detecting and fixing LaTeX style issues
    """
    
    def __init__(self):
        self.detector = StyleIssueDetector()
        self.retriever = RAGRetriever()
        self.generator = FixGenerator()
        self.validator = LatexValidator(timeout=settings.COMPILATION_TIMEOUT)
        
    def process_document(self, latex_content: str, 
                        document_format: str = "IEEE_two_column",
                        validate_compilation: bool = True) -> FixReport:
        """
        Process a LaTeX document: detect issues, generate fixes, validate
        
        Args:
            latex_content: The LaTeX document content
            document_format: Target format (IEEE_two_column, ACM_format, etc.)
            validate_compilation: Whether to validate by compilation
        
        Returns:
            FixReport with original, fixed content, and all details
        """
        start_time = time.time()
        logger.info(f"Starting LaTeX fixing pipeline for {document_format} format")
        
        # Step 1: Detect Issues
        logger.info("Step 1: Detecting style and layout issues...")
        analysis = self.detector.analyze_document(latex_content, document_format)
        
        if not analysis.detected_issues:
            logger.info("No issues detected!")
            return FixReport(
                original_latex=latex_content,
                fixed_latex=latex_content,
                issues_fixed=[],
                fixes_applied=[],
                processing_time=time.time() - start_time,
                success=True
            )
        
        logger.info(f"Detected {len(analysis.detected_issues)} issues")
        
        # Step 2: Retrieve fixes for each issue
        logger.info("Step 2: Retrieving relevant fixes from knowledge base...")
        issue_fixes = self._retrieve_fixes_for_issues(
            analysis.detected_issues, 
            document_format
        )
        
        # Step 3: Generate fixes
        logger.info("Step 3: Generating fixes with LLM...")
        fixes_applied = self._generate_fixes(
            issue_fixes,
            document_format,
            latex_content
        )
        
        # Step 4: Apply fixes to document
        logger.info("Step 4: Applying fixes to document...")
        fixed_latex = self._apply_fixes(latex_content, fixes_applied)
        
        # Step 5: Validate (optional)
        validation_result = None
        if validate_compilation:
            logger.info("Step 5: Validating fixed document...")
            validation_result = self._validate_fixes(latex_content, fixed_latex)
            
            # If validation fails, rollback
            if not validation_result.compilation_success:
                logger.warning("Validation failed, rolling back fixes")
                fixed_latex = latex_content
                success = False
            else:
                success = True
        else:
            success = True
        
        processing_time = time.time() - start_time
        logger.info(f"Pipeline completed in {processing_time:.2f}s")
        
        return FixReport(
            original_latex=latex_content,
            fixed_latex=fixed_latex,
            issues_fixed=analysis.detected_issues,
            fixes_applied=fixes_applied if success else [],
            validation_result=validation_result,
            processing_time=processing_time,
            success=success
        )
    
    def _retrieve_fixes_for_issues(self, issues: List[LatexIssue], 
                                  document_format: str) -> List[tuple]:
        """Retrieve relevant fixes for all detected issues"""
        logger.info("Retrieving fixes from knowledge base...")
        
        issue_fixes = []
        for issue in issues:
            examples = self.retriever.retrieve_fixes_for_issue(
                issue, 
                document_format,
                top_k=settings.RETRIEVAL_TOP_K
            )
            issue_fixes.append((issue, examples))
        
        return issue_fixes
    
    def _generate_fixes(self, issue_fixes: List[tuple], 
                       document_format: str,
                       full_latex: str) -> List[FixSuggestion]:
        """Generate fixes for all issues"""
        fixes = []
        
        for issue, examples in issue_fixes:
            try:
                # Get context for issue
                context = issue.context if hasattr(issue, 'context') else None
                
                # Generate fix
                fix = self.generator.generate_fix(
                    issue,
                    examples,
                    document_format,
                    context
                )
                
                fixes.append(fix)
                
            except Exception as e:
                logger.error(f"Failed to generate fix for {issue.type}: {e}")
                continue
        
        return fixes
    
    def _apply_fixes(self, original_latex: str, 
                    fixes: List[FixSuggestion]) -> str:
        """
        Apply all fixes to the document
        
        Note: This is a simplified version. In production, you'd want
        more sophisticated merging to handle overlapping fixes.
        """
        fixed_latex = original_latex
        
        # Sort fixes by position (if available) to apply from end to start
        # This prevents position shifts from affecting later fixes
        
        for fix in fixes:
            try:
                # Simple replacement
                if fix.original_code in fixed_latex:
                    fixed_latex = fixed_latex.replace(
                        fix.original_code,
                        fix.fixed_code,
                        1  # Replace only first occurrence
                    )
                    logger.info(f"Applied fix: {fix.changes_made[0] if fix.changes_made else 'Unknown'}")
                else:
                    logger.warning(f"Could not find code to replace: {fix.original_code[:50]}...")
            except Exception as e:
                logger.error(f"Error applying fix: {e}")
                continue
        
        return fixed_latex
    
    def _validate_fixes(self, original: str, fixed: str) -> ValidationResult:
        """Validate that fixes improved the document"""
        
        # Validate compilation
        validation = self.validator.validate_with_compilation(fixed)
        
        improvements = []
        warnings = []
        errors = validation.get("errors", [])
        
        if validation["compilation_success"]:
            improvements.append("Document compiles successfully")
        else:
            warnings.append("Document compilation failed")
        
        # Calculate style compliance (simplified)
        # In production, you'd have more sophisticated metrics
        compliance_score = 1.0 if validation["compilation_success"] else 0.5
        
        return ValidationResult(
            compilation_success=validation["compilation_success"],
            style_compliance_score=compliance_score,
            improvements=improvements,
            warnings=warnings,
            errors=errors
        )
    
    def fix_specific_issue(self, latex_content: str,
                          issue: LatexIssue,
                          document_format: str) -> str:
        """
        Fix a specific issue in isolation
        """
        # Retrieve examples
        examples = self.retriever.retrieve_fixes_for_issue(
            issue,
            document_format
        )
        
        # Generate fix
        fix = self.generator.generate_fix(
            issue,
            examples,
            document_format
        )
        
        # Apply fix
        fixed = latex_content.replace(fix.original_code, fix.fixed_code, 1)
        
        return fixed
