#!/usr/bin/env python3
"""
Enhanced RAG LaTeX Fixer with User-Guided Context
Allows users to specify document format and conference type for targeted fixes
"""

import os
import sys
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import google.generativeai as genai
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import argparse

@dataclass
class DocumentContext:
    """User-provided context about the document"""
    column_format: str  # "1-column" or "2-column"
    conference_type: str  # "IEEE", "ACM", "SPRINGER", "ELSEVIER", "GENERIC"
    original_format: Optional[str] = None  # "PDF" or "LATEX" 
    conversion_applied: bool = False  # True if PDF was converted to LaTeX

@dataclass
class LaTeXExample:
    """Enhanced LaTeX example with context filtering"""
    problem: str
    solution: str
    context: str
    conference_tags: List[str]  # ["IEEE", "ACM", etc.]
    format_tags: List[str]      # ["1-column", "2-column"]
    issue_type: str            # "formatting", "conversion", "structure"

class ContextAwareRAGFixer:
    """Enhanced RAG system with user context awareness"""
    
    def __init__(self, api_key: str):
        """Initialize with API key and load context-aware examples"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.examples = []
        self.index = None
        self.load_context_aware_examples()
        self.build_vector_index()
    
    def load_context_aware_examples(self):
        """Load LaTeX examples with context tags"""
        self.examples = [
            # IEEE Conference Examples
            LaTeXExample(
                problem="Author names not centered in IEEE format",
                solution="Use \\author{\\IEEEauthorblockN{Name1}\\and\\IEEEauthorblockN{Name2}} for IEEE",
                context="IEEE conference papers require specific author formatting",
                conference_tags=["IEEE"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="IEEE paper has wrong document class after PDF conversion",
                solution="Change \\documentclass[10pt]{article} to \\documentclass[conference]{IEEEtran}",
                context="PDF to LaTeX conversion often uses generic article class instead of IEEEtran",
                conference_tags=["IEEE"],
                format_tags=["2-column"],
                issue_type="conversion"
            ),
            LaTeXExample(
                problem="IEEE paper missing proper column formatting",
                solution="Add \\usepackage{multicol} and \\begin{multicols}{2}...\\end{multicols} for 2-column IEEE",
                context="IEEE conference papers are typically 2-column format",
                conference_tags=["IEEE"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            
            # ACM Conference Examples  
            LaTeXExample(
                problem="ACM paper author formatting incorrect",
                solution="Use \\author{\\authornote{Author 1}\\affiliation{Institution}} for ACM format",
                context="ACM has specific author and affiliation formatting requirements",
                conference_tags=["ACM"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="ACM document class missing after conversion",
                solution="Change to \\documentclass[sigconf]{acmart} for ACM conference format",
                context="ACM papers require acmart document class with sigconf option",
                conference_tags=["ACM"],
                format_tags=["2-column"],
                issue_type="conversion"
            ),
            
            # Springer Examples
            LaTeXExample(
                problem="Springer paper margins too wide after PDF conversion",
                solution="Add \\usepackage[margin=1in]{geometry} for Springer format compliance",
                context="Springer has specific margin requirements that differ from generic articles",
                conference_tags=["SPRINGER"],
                format_tags=["1-column"],
                issue_type="conversion"
            ),
            
            # Column Format Specific Examples
            LaTeXExample(
                problem="Two-column document converted to single column with extra whitespace",
                solution="Add \\usepackage[twocolumn,margin=0.75in]{geometry} to restore 2-column format",
                context="PDF to LaTeX conversion often loses original column formatting",
                conference_tags=["IEEE", "ACM"],
                format_tags=["2-column"],
                issue_type="conversion"
            ),
            LaTeXExample(
                problem="Single column document has inappropriate narrow margins",
                solution="Use \\usepackage[margin=1in]{geometry} for proper 1-column spacing",
                context="Single column documents need wider margins for readability",
                conference_tags=["SPRINGER", "ELSEVIER"],
                format_tags=["1-column"],
                issue_type="formatting"
            ),
            
            # Generic Conversion Issues
            LaTeXExample(
                problem="PDF conversion added extra spacing and paragraph breaks",
                solution="Remove extra \\vspace commands and consolidate paragraph breaks",
                context="PDF to LaTeX conversion often introduces unwanted spacing",
                conference_tags=["GENERIC"],
                format_tags=["1-column", "2-column"],
                issue_type="conversion"
            ),
            
            # Add more context-aware examples...
            LaTeXExample(
                problem="Table formatting broken in IEEE 2-column layout",
                solution="Use \\begin{table*}[!t] for tables spanning both columns in IEEE format",
                context="IEEE 2-column papers need special table handling for wide tables",
                conference_tags=["IEEE"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Figure placement issues in ACM single column",
                solution="Use \\begin{figure}[!htb] with proper sizing for ACM 1-column format",
                context="ACM single column has specific figure placement requirements",
                conference_tags=["ACM"],
                format_tags=["1-column"],
                issue_type="formatting"
            ),
            
            # Table Formatting Examples
            LaTeXExample(
                problem="Wide table covering second column text in IEEE 2-column format",
                solution="Use \\begin{table*}[!t] and \\centering with proper column widths: |c|l|p{4cm}|p{3cm}|",
                context="IEEE 2-column papers need table* environment for wide tables to span both columns",
                conference_tags=["IEEE"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Table placement interfering with text flow in IEEE 2-column format",
                solution="Use \\begin{table*}[!tb] with stfloats package and adjusted float parameters to keep table closer to reference text",
                context="IEEE 2-column format requires table* with stfloats package, [!tb] positioning, and float parameter adjustments (dbltopnumber=2, dbltopfraction=0.9, dblfloatpagefraction=0.7) to prevent tables from floating to last page",
                conference_tags=["IEEE"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Table positioning [h] causes layout issues",
                solution="Change \\begin{table}[h] to \\begin{table}[t] for IEEE standard positioning at page top",
                context="IEEE format prefers tables at top of page with [t] positioning for professional appearance and consistent layout",
                conference_tags=["IEEE"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Table uses \\begin{center} instead of \\centering",
                solution="Replace \\begin{center}...\\end{center} with \\centering for IEEE format",
                context="IEEE style guide recommends \\centering over center environment in tables",
                conference_tags=["IEEE"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Table missing proper label for referencing",
                solution="Add \\label{tab:descriptive_name} after \\caption for proper referencing",
                context="All tables should have labels for academic paper referencing",
                conference_tags=["IEEE", "ACM", "SPRINGER"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Table column widths not specified causing overflow",
                solution="Use p{width} columns: \\begin{tabular}{|c|l|p{4cm}|p{3cm}|} for controlled widths",
                context="Fixed column widths prevent table overflow in constrained layouts",
                conference_tags=["IEEE", "ACM"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            
            # Image Sizing and Placement Examples
            LaTeXExample(
                problem="Large image width may cause figure to float to document end. Consider using smaller width (0.8\\textwidth or 0.7\\textwidth) for better placement",
                solution="Replace width=\\textwidth with width=0.7\\textwidth or width=0.8\\textwidth to prevent figure from floating to end",
                context="Large images in LaTeX often get pushed to document end due to float placement algorithm. Smaller widths help keep figures closer to referencing text",
                conference_tags=["IEEE", "ACM", "SPRINGER"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Figure missing size specification. Add width parameter to control placement and prevent floating to document end",
                solution="Add width=0.7\\textwidth to \\includegraphics for better size control: \\includegraphics[width=0.7\\textwidth]{filename}",
                context="Images without size specifications can cause unpredictable placement. Explicit width helps LaTeX place figures optimally",
                conference_tags=["IEEE", "ACM", "SPRINGER"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Figure* environment should use \\textwidth for proper sizing across both columns",
                solution="Change width=\\columnwidth to width=0.8\\textwidth in figure* environment for proper two-column spanning",
                context="Figure* spans both columns so should use textwidth-based sizing, not columnwidth",
                conference_tags=["IEEE", "ACM"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Single column figure should use \\columnwidth instead of \\textwidth",
                solution="Change width=\\textwidth to width=0.9\\columnwidth for single column figures",
                context="Single column figures should be sized relative to column width, not full text width",
                conference_tags=["IEEE", "ACM"],
                format_tags=["2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Image positioning should use [!ht] or [!htbp] to prevent floating to document end. Missing restrictive positioning to keep image close to text",
                solution="Change \\begin{figure*}[!t] to \\begin{figure*}[!ht] or add [!htbp] positioning to keep images on current or next page only",
                context="Restrictive positioning [!ht] forces images to stay on current page (here) or next page top, preventing them from floating to document end",
                conference_tags=["IEEE", "ACM", "SPRINGER"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            ),
            LaTeXExample(
                problem="Figure positioning [h] can cause text overlap. Use [!tbp] or [!t] for better placement",
                solution="Replace [h] with [!ht] for better positioning that keeps figure close without overlap",
                context="[!ht] positioning allows figure on current page (here) or top of next page, preventing distant floating",
                conference_tags=["IEEE", "ACM", "SPRINGER"],
                format_tags=["1-column", "2-column"],
                issue_type="formatting"
            )
        ]
        
        print(f"✅ Loaded {len(self.examples)} context-aware LaTeX examples")
    
    def build_vector_index(self):
        """Build FAISS index from examples with error handling"""
        try:
            texts = [f"{ex.problem} {ex.solution} {ex.context}" for ex in self.examples]
            embeddings = self.encoder.encode(texts)
            
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype('float32'))
            
            print(f"✅ Built FAISS index with {len(texts)} examples")
        except Exception as e:
            print(f"⚠️ FAISS index building failed: {e}")
            print("⚠️ Continuing without vector search capabilities")
            self.index = None
    
    def filter_examples_by_context(self, context: DocumentContext) -> List[int]:
        """Filter examples based on user-provided context"""
        relevant_indices = []
        
        for i, example in enumerate(self.examples):
            # Check conference match
            conference_match = (context.conference_type in example.conference_tags or 
                              "GENERIC" in example.conference_tags)
            
            # Check format match
            format_match = context.column_format in example.format_tags
            
            # Prioritize conversion issues if document was converted
            conversion_priority = (context.conversion_applied and 
                                 example.issue_type == "conversion")
            
            # Include if matches context or has high priority
            if conference_match and format_match:
                relevant_indices.append(i)
            elif conversion_priority:
                relevant_indices.append(i)
                
        return relevant_indices
    
    def retrieve_contextual_examples(self, query: str, context: DocumentContext, 
                                   top_k: int = 5) -> List[Tuple[LaTeXExample, float]]:
        """Retrieve examples filtered by context"""
        # First filter by context
        relevant_indices = self.filter_examples_by_context(context)
        
        if not relevant_indices:
            print(f"⚠️  No examples found for {context.conference_type} {context.column_format}")
            relevant_indices = list(range(len(self.examples)))  # Fallback to all
        
        # If FAISS index is not available, return relevant examples by context only
        if self.index is None:
            print("⚠️ Using context-only matching (no vector search)")
            contextual_results = []
            for idx in relevant_indices[:top_k]:
                contextual_results.append((self.examples[idx], 1.0))
            return contextual_results
        
        try:
            # Encode query
            query_embedding = self.encoder.encode([query])
            faiss.normalize_L2(query_embedding)
            
            # Search in full index
            scores, indices = self.index.search(query_embedding.astype('float32'), 
                                              min(top_k * 2, len(self.examples)))
        except Exception as e:
            print(f"⚠️ Vector search failed: {e}")
            # Fallback to context-only matching
            contextual_results = []
            for idx in relevant_indices[:top_k]:
                contextual_results.append((self.examples[idx], 1.0))
            return contextual_results
        
        # Filter results to context-relevant examples
        contextual_results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx in relevant_indices:
                contextual_results.append((self.examples[idx], float(score)))
                if len(contextual_results) >= top_k:
                    break
        
        # If not enough contextual results, add best general matches
        if len(contextual_results) < top_k:
            for idx, score in zip(indices[0], scores[0]):
                if idx not in relevant_indices and len(contextual_results) < top_k:
                    contextual_results.append((self.examples[idx], float(score)))
        
        return contextual_results
    
    def generate_contextual_fix(self, issue: str, context: DocumentContext, 
                              examples: List[Tuple[LaTeXExample, float]]) -> Dict:
        """Generate fix with context awareness"""
        
        context_prompt = f"""
You are a LaTeX expert specializing in {context.conference_type} conference papers.

DOCUMENT CONTEXT:
- Conference: {context.conference_type}
- Format: {context.column_format}
- Original: {context.original_format or 'Unknown'}
- Converted: {'Yes' if context.conversion_applied else 'No'}

ISSUE TO FIX: {issue}

RELEVANT EXAMPLES:
"""
        
        for i, (example, score) in enumerate(examples, 1):
            context_prompt += f"""
Example {i} (similarity: {score:.3f}):
Problem: {example.problem}
Solution: {example.solution}
Context: {example.context}
Tags: {', '.join(example.conference_tags + example.format_tags)}
---"""
        
        context_prompt += f"""

Please provide a specific fix for this {context.conference_type} {context.column_format} document.
Focus on {context.conference_type}-specific formatting requirements.

Respond with JSON:
{{
    "fix": "exact LaTeX code to apply",
    "explanation": "why this fix is appropriate for {context.conference_type} {context.column_format}",
    "confidence": 0.0-1.0,
    "context_relevance": "how well this addresses {context.conference_type} requirements"
}}
"""
        
        try:
            response = self.model.generate_content(context_prompt)
            response_text = response.text.strip()
            
            # Extract JSON
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    "fix": "Unable to parse fix",
                    "explanation": "JSON parsing failed",
                    "confidence": 0.0,
                    "context_relevance": "Low"
                }
                
        except Exception as e:
            return {
                "fix": f"Error generating fix: {str(e)}",
                "explanation": "API call failed",
                "confidence": 0.0,
                "context_relevance": "None"
            }

def main():
    """Enhanced main function with user context input"""
    parser = argparse.ArgumentParser(description='Context-Aware RAG LaTeX Fixer')
    parser.add_argument('--file', required=True, help='LaTeX file to fix')
    parser.add_argument('--conference', choices=['IEEE', 'ACM', 'SPRINGER', 'ELSEVIER', 'GENERIC'],
                       required=True, help='Conference type')
    parser.add_argument('--format', choices=['1-column', '2-column'], 
                       required=True, help='Document column format')
    parser.add_argument('--converted', action='store_true', 
                       help='Document was converted from PDF to LaTeX')
    parser.add_argument('--original', choices=['PDF', 'LATEX'], 
                       help='Original document format')
    
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ Please set GOOGLE_API_KEY environment variable")
        return
    
    # Create document context
    context = DocumentContext(
        column_format=args.format,
        conference_type=args.conference,
        original_format=args.original,
        conversion_applied=args.converted
    )
    
    print(f"🎯 Context-Aware RAG LaTeX Fixer")
    print(f"📄 File: {args.file}")
    print(f"🏛️  Conference: {context.conference_type}")
    print(f"📊 Format: {context.column_format}")
    print(f"🔄 Converted: {'Yes' if context.conversion_applied else 'No'}")
    print("-" * 50)
    
    # Initialize RAG system
    rag_fixer = ContextAwareRAGFixer(api_key)
    
    # Read file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {args.file}")
        return
    
    # Demo: Test with a sample issue
    test_issue = "Author names are not properly formatted and margins are too wide"
    
    print(f"🔍 Testing with issue: {test_issue}")
    
    # Retrieve contextual examples
    examples = rag_fixer.retrieve_contextual_examples(test_issue, context, top_k=3)
    
    print(f"\n📚 Retrieved {len(examples)} contextual examples:")
    for i, (example, score) in enumerate(examples, 1):
        print(f"{i}. [{', '.join(example.conference_tags)}] [{', '.join(example.format_tags)}] "
              f"(Score: {score:.3f})")
        print(f"   Problem: {example.problem}")
        print(f"   Solution: {example.solution}")
        print()
    
    # Generate contextual fix
    fix_result = rag_fixer.generate_contextual_fix(test_issue, context, examples)
    
    print("🛠️  Generated Fix:")
    print(f"Fix: {fix_result['fix']}")
    print(f"Explanation: {fix_result['explanation']}")
    print(f"Confidence: {fix_result['confidence']}")
    print(f"Context Relevance: {fix_result['context_relevance']}")

if __name__ == "__main__":
    main()