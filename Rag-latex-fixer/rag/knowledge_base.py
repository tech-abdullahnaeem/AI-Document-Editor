"""
Knowledge Base Manager for RAG system
Handles loading, indexing, and retrieval of LaTeX patterns and fixes
"""
import json
import pickle
from pathlib import Path
from typing import List, Dict, Optional, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from loguru import logger

from config import settings
from models import RetrievedExample


class KnowledgeBaseManager:
    """
    Manages the knowledge base of LaTeX patterns, fixes, and templates
    """
    
    def __init__(self):
        self.kb_dir = settings.KNOWLEDGE_BASE_DIR
        self.embedding_model = None
        self.faiss_index = None
        self.metadata = []
        
        # Load data
        self._load_knowledge_base()
        
    def _load_knowledge_base(self):
        """Load all knowledge base components"""
        logger.info("Loading knowledge base...")
        
        # Load JSON files
        self.error_patterns = self._load_json("error_patterns.json")
        self.citation_styles = self._load_json("citation_styles.json")
        self.formatting_rules = self._load_json("formatting_rules.json")
        self.latex_commands = self._load_json("latex_commands.json")
        
        # Load templates
        self.templates = self._load_templates()
        
        # Load or create embeddings
        self._load_or_create_embeddings()
        
        logger.info(f"Knowledge base loaded. {len(self.metadata)} examples indexed.")
    
    def _load_json(self, filename: str) -> Dict:
        """Load a JSON file from knowledge base"""
        file_path = self.kb_dir / filename
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Load all template files"""
        templates = {}
        templates_dir = self.kb_dir / "templates"
        
        if not templates_dir.exists():
            logger.warning(f"Templates directory not found: {templates_dir}")
            return templates
        
        for template_dir in templates_dir.iterdir():
            if template_dir.is_dir():
                format_name = template_dir.name
                templates[format_name] = {}
                
                for tex_file in template_dir.glob("*.tex"):
                    element_name = tex_file.stem
                    templates[format_name][element_name] = tex_file.read_text(encoding='utf-8')
        
        return templates
    
    def _load_or_create_embeddings(self):
        """Load existing embeddings or create new ones"""
        embeddings_file = self.kb_dir / "embeddings_cache.pkl"
        index_file = self.kb_dir / "faiss_index.bin"
        
        if embeddings_file.exists() and index_file.exists():
            logger.info("Loading existing embeddings and FAISS index...")
            try:
                with open(embeddings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.metadata = data['metadata']
                
                self.faiss_index = faiss.read_index(str(index_file))
                logger.info("Embeddings loaded successfully")
                return
            except Exception as e:
                logger.warning(f"Failed to load embeddings: {e}. Creating new ones...")
        
        # Create new embeddings
        self._create_embeddings()
    
    def _create_embeddings(self):
        """Create embeddings for all examples in knowledge base"""
        logger.info("Creating embeddings for knowledge base...")
        
        # Initialize embedding model
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Collect all examples
        examples = []
        metadata = []
        
        # Add templates
        for format_name, elements in self.templates.items():
            for element_name, code in elements.items():
                examples.append(code)
                metadata.append({
                    "type": "template",
                    "format": format_name,
                    "element": element_name,
                    "code": code,
                    "description": f"{element_name} template for {format_name}"
                })
        
        # Add fix patterns
        fixes_dir = self.kb_dir / "fixes"
        if fixes_dir.exists():
            for fix_file in fixes_dir.glob("*.json"):
                fix_data = self._load_json(f"fixes/{fix_file.name}")
                for fix_name, fix_info in fix_data.items():
                    if isinstance(fix_info, dict) and "example" in fix_info:
                        examples.append(fix_info["example"])
                        metadata.append({
                            "type": "fix",
                            "fix_name": fix_name,
                            "code": fix_info["example"],
                            "description": fix_info.get("description", ""),
                            "category": fix_file.stem
                        })
        
        if not examples:
            logger.warning("No examples found to embed!")
            self.metadata = []
            return
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(examples)} examples...")
        embeddings = self.embedding_model.encode(examples, show_progress_bar=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(embeddings.astype('float32'))
        
        self.metadata = metadata
        
        # Save embeddings and index
        self._save_embeddings()
        
        logger.info(f"Created embeddings for {len(examples)} examples")
    
    def _save_embeddings(self):
        """Save embeddings and FAISS index to disk"""
        embeddings_file = self.kb_dir / "embeddings_cache.pkl"
        index_file = self.kb_dir / "faiss_index.bin"
        
        with open(embeddings_file, 'wb') as f:
            pickle.dump({'metadata': self.metadata}, f)
        
        faiss.write_index(self.faiss_index, str(index_file))
        logger.info("Embeddings saved to disk")
    
    def retrieve_similar_examples(self, query: str, 
                                  filters: Optional[Dict[str, Any]] = None,
                                  top_k: int = 5) -> List[RetrievedExample]:
        """
        Retrieve similar examples using semantic search
        
        Args:
            query: The query text (e.g., error description or code snippet)
            filters: Optional metadata filters (e.g., {"format": "IEEE_two_column"})
            top_k: Number of examples to retrieve
        
        Returns:
            List of retrieved examples with similarity scores
        """
        if self.faiss_index is None or not self.metadata:
            logger.warning("Knowledge base not initialized or empty")
            return []
        
        # Initialize embedding model if needed
        if self.embedding_model is None:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Embed query
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search in FAISS
        # Retrieve more results to allow for filtering
        search_k = top_k * 3 if filters else top_k
        distances, indices = self.faiss_index.search(
            query_embedding.reshape(1, -1).astype('float32'), 
            search_k
        )
        
        # Convert to similarity scores (FAISS returns L2 distances)
        similarities = 1 / (1 + distances[0])
        
        # Collect results
        results = []
        for idx, similarity in zip(indices[0], similarities):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                
                # Apply filters if provided
                if filters:
                    if not self._matches_filters(meta, filters):
                        continue
                
                results.append(RetrievedExample(
                    code=meta.get("code", ""),
                    description=meta.get("description", ""),
                    document_format=meta.get("format", "generic"),
                    element_type=meta.get("element", meta.get("fix_name", "unknown")),
                    similarity_score=float(similarity),
                    metadata=meta
                ))
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def _matches_filters(self, metadata: Dict, filters: Dict) -> bool:
        """Check if metadata matches all filters"""
        for key, value in filters.items():
            if metadata.get(key) != value:
                return False
        return True
    
    def get_template(self, format_name: str, element_name: str) -> Optional[str]:
        """Get a specific template"""
        return self.templates.get(format_name, {}).get(element_name)
    
    def get_all_templates_for_format(self, format_name: str) -> Dict[str, str]:
        """Get all templates for a specific format"""
        return self.templates.get(format_name, {})
    
    def retrieve_fix_patterns(self, issue_type: str) -> List[Dict]:
        """Retrieve fix patterns for a specific issue type"""
        fixes_dir = self.kb_dir / "fixes"
        all_fixes = []
        
        for fix_file in fixes_dir.glob("*.json"):
            fix_data = self._load_json(f"fixes/{fix_file.name}")
            for fix_name, fix_info in fix_data.items():
                if isinstance(fix_info, dict):
                    if issue_type.lower() in fix_name.lower() or \
                       issue_type.lower() in fix_file.stem.lower():
                        all_fixes.append({
                            "name": fix_name,
                            "category": fix_file.stem,
                            **fix_info
                        })
        
        return all_fixes
    
    def refresh_embeddings(self):
        """Regenerate all embeddings (useful after adding new templates)"""
        logger.info("Refreshing embeddings...")
        self._create_embeddings()
