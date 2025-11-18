"""
RAG-based retriever for LaTeX fixes
Combines semantic search with metadata filtering
"""
from typing import List, Dict, Optional
from loguru import logger

from models import LatexIssue, RetrievedExample
from rag.knowledge_base import KnowledgeBaseManager
from config import settings


class RAGRetriever:
    """
    Retrieves relevant fixes and examples using RAG approach
    """
    
    def __init__(self):
        self.kb = KnowledgeBaseManager()
        
    def retrieve_fixes_for_issue(self, issue: LatexIssue, 
                                 document_format: str,
                                 top_k: int = None) -> List[RetrievedExample]:
        """
        Retrieve relevant fixes for a specific issue
        
        Args:
            issue: The detected LaTeX issue
            document_format: Target document format (IEEE, ACM, etc.)
            top_k: Number of examples to retrieve
        
        Returns:
            List of retrieved examples ranked by relevance
        """
        if top_k is None:
            top_k = settings.RETRIEVAL_TOP_K
        
        logger.info(f"Retrieving fixes for issue: {issue.type}")
        
        # Build query from issue
        query = self._build_query_from_issue(issue)
        
        # Define filters based on issue and document format
        filters = self._build_filters(issue, document_format)
        
        # Retrieve similar examples
        examples = self.kb.retrieve_similar_examples(
            query=query,
            filters=filters,
            top_k=top_k
        )
        
        # If not enough results with filters, try without filters
        if len(examples) < top_k:
            logger.info(f"Only found {len(examples)} with filters, searching without filters...")
            additional = self.kb.retrieve_similar_examples(
                query=query,
                filters=None,
                top_k=top_k - len(examples)
            )
            examples.extend(additional)
        
        # Re-rank based on relevance
        examples = self._rerank_examples(examples, issue, document_format)
        
        return examples[:top_k]
    
    def _build_query_from_issue(self, issue: LatexIssue) -> str:
        """Build semantic search query from issue"""
        query_parts = [
            issue.description,
            f"Element: {issue.element}",
        ]
        
        if issue.expected_format:
            query_parts.append(f"Expected: {issue.expected_format}")
        
        # Add type-specific context
        issue_type_str = issue.type.value if hasattr(issue.type, 'value') else str(issue.type)
        if issue_type_str in ["table_not_centered", "figure_not_centered"]:
            query_parts.append("centering floating elements")
        elif issue_type_str in ["author_block_incorrect", "title_not_centered"]:
            query_parts.append("author centering formatting")
        elif issue_type_str == "layout_mismatch":
            query_parts.append("two-column layout single column conversion")
        
        return " ".join(query_parts)
    
    def _build_filters(self, issue: LatexIssue, document_format: str) -> Dict:
        """Build metadata filters for retrieval"""
        filters = {}
        
        # Filter by element type
        element_map = {
            "author": "author_block",
            "table": "table",
            "figure": "figure",
            "title": "title"
        }
        
        # Extract base element name
        element_base = issue.element.split('_')[0]
        if element_base in element_map:
            filters["element"] = element_map[element_base]
        
        # Filter by document format if available
        if document_format and document_format != "generic":
            filters["format"] = document_format
        
        return filters
    
    def _rerank_examples(self, examples: List[RetrievedExample], 
                        issue: LatexIssue,
                        document_format: str) -> List[RetrievedExample]:
        """
        Re-rank retrieved examples based on additional criteria
        """
        def rank_score(example: RetrievedExample) -> float:
            score = example.similarity_score
            
            # Boost if format matches exactly
            if example.document_format == document_format:
                score *= 1.5
            
            # Boost if element type matches
            if issue.element.startswith(example.element_type):
                score *= 1.3
            
            # Boost templates over generic fixes
            if example.metadata.get("type") == "template":
                score *= 1.2
            
            return score
        
        # Sort by rank score
        examples.sort(key=rank_score, reverse=True)
        
        return examples
    
    def retrieve_complete_template(self, document_format: str) -> Dict[str, str]:
        """Retrieve complete document template for a format"""
        return self.kb.get_all_templates_for_format(document_format)
    
    def retrieve_fix_patterns(self, issue_type: str) -> List[Dict]:
        """Retrieve predefined fix patterns"""
        return self.kb.retrieve_fix_patterns(issue_type)
