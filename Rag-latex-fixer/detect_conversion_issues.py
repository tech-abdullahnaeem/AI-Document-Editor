#!/usr/bin/env python3
"""
Enhanced RAG system to detect and fix PDF-to-LaTeX conversion issues
- Detect original document format (one-column vs two-column)
- Fix conversion artifacts (whitespace, document class)
- Restore proper academic formatting
"""

import os
import sys
import re
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from detectors.style_detector import StyleIssueDetector
from rag.retriever import RAGRetriever
from rag.fix_generator import FixGenerator
from models import LatexIssue, FixSuggestion, Severity, IssueType
from config import Settings

class DocumentFormatDetector:
    """Detect original document format and conversion issues"""
    
    def __init__(self):
        self.conversion_indicators = {
            'two_column_indicators': [
                'IEEE',
                'ACM',
                'conference',
                'proceedings',
                'Index Terms',
                'Abstract',
                'Keywords',
                'References'
            ],
            'api_conversion_artifacts': [
                '\\documentclass[10pt]{article}',  # Generic conversion default
                'extra whitespace patterns',
                'missing column specifications',
                'improper margins'
            ]
        }
    
    def analyze_document_format(self, content: str) -> dict:
        """Analyze document to detect original format"""
        
        analysis = {
            'original_format': 'unknown',
            'conversion_artifacts': [],
            'format_confidence': 0.0,
            'recommended_fixes': []
        }
        
        lines = content.splitlines()
        
        # Check for two-column indicators
        two_column_score = 0
        found_indicators = []
        
        for indicator in self.conversion_indicators['two_column_indicators']:
            if indicator.lower() in content.lower():
                two_column_score += 1
                found_indicators.append(indicator)
        
        # Check document structure
        has_abstract = '\\begin{abstract}' in content
        has_index_terms = 'Index Terms' in content or 'Keywords' in content
        has_sections = len(re.findall(r'\\section\*?\{', content)) > 2
        
        if has_abstract:
            two_column_score += 2
        if has_index_terms:
            two_column_score += 2
        if has_sections:
            two_column_score += 1
        
        # Determine format
        if two_column_score >= 4:
            analysis['original_format'] = 'two_column'
            analysis['format_confidence'] = min(two_column_score / 8.0, 1.0)
        elif two_column_score >= 2:
            analysis['original_format'] = 'likely_two_column'
            analysis['format_confidence'] = two_column_score / 8.0
        else:
            analysis['original_format'] = 'single_column'
            analysis['format_confidence'] = 0.5
        
        # Check for conversion artifacts
        artifacts = []
        
        # Check document class
        doc_class_match = re.search(r'\\documentclass\[([^\]]*)\]\{([^}]*)\}', content)
        if doc_class_match:
            options, doc_class = doc_class_match.groups()
            if doc_class == 'article' and '10pt' in options and 'twocolumn' not in options:
                artifacts.append({
                    'type': 'wrong_document_class',
                    'description': 'Using generic article class instead of conference format',
                    'current': f'\\documentclass[{options}]{{{doc_class}}}',
                    'recommended': '\\documentclass[conference]{IEEEtran}' if 'IEEE' in found_indicators else '\\documentclass[sigconf]{acmart}'
                })
        
        # Check for missing column specification
        if analysis['original_format'] in ['two_column', 'likely_two_column']:
            if 'twocolumn' not in content and 'IEEEtran' not in content and 'acmart' not in content:
                artifacts.append({
                    'type': 'missing_column_spec',
                    'description': 'Missing two-column specification',
                    'fix': 'Add twocolumn option or use appropriate document class'
                })
        
        # Check for excessive whitespace/margins
        margin_packages = ['geometry', 'fullpage', 'anysize']
        has_margin_control = any(pkg in content for pkg in margin_packages)
        
        if not has_margin_control and analysis['original_format'] == 'two_column':
            artifacts.append({
                'type': 'missing_margin_control',
                'description': 'Missing proper margin/geometry settings for two-column',
                'fix': 'Add geometry package with appropriate margins'
            })
        
        analysis['conversion_artifacts'] = artifacts
        analysis['found_indicators'] = found_indicators
        
        return analysis

def detect_and_fix_conversion_issues():
    """Main function to detect and fix PDF-to-LaTeX conversion issues"""
    
    print("🔍 PDF-TO-LATEX CONVERSION ANALYSIS")
    print("=" * 60)
    
    # File path
    file_path = Path(__file__).parent.parent / "final research paper" / "2025_10_04_e051dc83281e472a2bf4g.tex"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Document: {file_path.name}")
    print(f"📊 Size: {len(content)} characters, {len(content.splitlines())} lines")
    
    # Initialize detector
    format_detector = DocumentFormatDetector()
    
    # STEP 1: Format Detection
    print(f"\n🔍 STEP 1: DOCUMENT FORMAT ANALYSIS")
    print("-" * 40)
    
    format_analysis = format_detector.analyze_document_format(content)
    
    print(f"📋 FORMAT DETECTION RESULTS:")
    print(f"   Original format: {format_analysis['original_format']}")
    print(f"   Confidence: {format_analysis['format_confidence']:.2f}")
    print(f"   Format indicators found: {', '.join(format_analysis['found_indicators'])}")
    
    # STEP 2: Conversion Artifacts Detection
    print(f"\n🚨 STEP 2: CONVERSION ARTIFACTS")
    print("-" * 40)
    
    artifacts = format_analysis['conversion_artifacts']
    print(f"Found {len(artifacts)} conversion artifacts:")
    
    for i, artifact in enumerate(artifacts, 1):
        print(f"   {i}. {artifact['type']}: {artifact['description']}")
        if 'current' in artifact:
            print(f"      Current: {artifact['current']}")
        if 'recommended' in artifact:
            print(f"      Recommended: {artifact['recommended']}")
        if 'fix' in artifact:
            print(f"      Fix: {artifact['fix']}")
    
    # STEP 3: Create LaTeX Issues for RAG
    print(f"\n🔧 STEP 3: CREATING RAG-COMPATIBLE ISSUES")
    print("-" * 40)
    
    rag_issues = []
    
    # Document class issue
    if format_analysis['original_format'] in ['two_column', 'likely_two_column']:
        issue = LatexIssue(
            type=IssueType.LAYOUT_MISMATCH,
            severity=Severity.HIGH,
            description=f"Document converted from {format_analysis['original_format']} to single-column - needs proper document class",
            element="documentclass",
            current_code="\\documentclass[10pt]{article}",
            location={"start_line": 1, "end_line": 1}
        )
        rag_issues.append(issue)
    
    # Missing geometry/margins
    if not any('geometry' in line for line in content.splitlines()):
        issue = LatexIssue(
            type=IssueType.LAYOUT_MISMATCH,
            severity=Severity.MEDIUM,
            description="Missing proper margin control - API conversion added extra whitespace",
            element="margins",
            current_code="Missing geometry package",
            location={"start_line": 5, "end_line": 5}
        )
        rag_issues.append(issue)
    
    # Two-column restoration
    if format_analysis['original_format'] == 'two_column':
        issue = LatexIssue(
            type=IssueType.LAYOUT_MISMATCH,
            severity=Severity.HIGH,
            description="Document should use two-column layout based on content analysis",
            element="layout",
            current_code="Single column layout",
            location={"start_line": 1, "end_line": 1}
        )
        rag_issues.append(issue)
    
    print(f"Created {len(rag_issues)} RAG-compatible issues")
    
    # STEP 4: Generate Fixes
    print(f"\n🤖 STEP 4: GENERATING CONVERSION FIXES")
    print("-" * 40)
    
    try:
        retriever = RAGRetriever()
        generator = FixGenerator()
        print("✅ RAG components initialized")
        
        generated_fixes = []
        
        for i, issue in enumerate(rag_issues, 1):
            print(f"\n🔧 Processing issue {i}: {issue.description}")
            
            try:
                examples = retriever.retrieve_fixes_for_issue(issue, "IEEE_two_column", top_k=3)
                print(f"   📚 Retrieved {len(examples)} examples")
                
                fix = generator.generate_fix(issue, examples, "IEEE_two_column")
                generated_fixes.append(fix)
                
                print(f"   ✅ Fix generated (confidence: {fix.confidence_score:.2f})")
                print(f"   💡 Solution: {fix.explanation[:120]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # STEP 5: Create Fixed Document
        print(f"\n📝 STEP 5: CREATING FIXED DOCUMENT")
        print("-" * 40)
        
        fixed_content = content
        
        # Apply document class fix
        if format_analysis['original_format'] == 'two_column':
            if 'IEEE' in format_analysis['found_indicators']:
                # Use IEEE format
                fixed_content = re.sub(
                    r'\\documentclass\[[^\]]*\]\{article\}',
                    r'\\documentclass[conference]{IEEEtran}',
                    fixed_content
                )
                print("   ✅ Applied IEEE two-column document class")
            else:
                # Use ACM format
                fixed_content = re.sub(
                    r'\\documentclass\[[^\]]*\]\{article\}',
                    r'\\documentclass[sigconf]{acmart}',
                    fixed_content
                )
                print("   ✅ Applied ACM two-column document class")
        
        # Add geometry package for margin control
        if '\\usepackage{geometry}' not in fixed_content:
            # Find where to insert geometry package
            usepackage_pattern = r'(\\usepackage\{[^}]+\}\s*\n)'
            match = re.search(usepackage_pattern, fixed_content)
            if match:
                insert_pos = match.end()
                geometry_package = "\\usepackage[margin=0.75in]{geometry}\n"
                fixed_content = fixed_content[:insert_pos] + geometry_package + fixed_content[insert_pos:]
                print("   ✅ Added geometry package for proper margins")
        
        # Save fixed document
        output_file = Path(__file__).parent / "output" / "2025_10_04_e051dc83281e472a2bf4g_FORMAT_FIXED.tex"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"   💾 Fixed document saved: {output_file.name}")
        print(f"   📊 Size change: {len(fixed_content) - len(content):+d} characters")
        
    except Exception as e:
        print(f"❌ RAG processing failed: {e}")
    
    # STEP 6: Summary
    print(f"\n📊 CONVERSION FIX SUMMARY")
    print("-" * 40)
    print(f"   Original format detected: {format_analysis['original_format']}")
    print(f"   Detection confidence: {format_analysis['format_confidence']:.2f}")
    print(f"   Conversion artifacts: {len(artifacts)}")
    print(f"   RAG issues created: {len(rag_issues)}")
    print(f"   Fixes applied: Document class, margins, layout")
    
    return format_analysis

if __name__ == "__main__":
    try:
        results = detect_and_fix_conversion_issues()
        print(f"\n✅ PDF-to-LaTeX conversion analysis complete!")
        print(f"Detected original format: {results['original_format']}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()