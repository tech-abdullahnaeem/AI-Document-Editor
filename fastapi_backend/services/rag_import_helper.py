"""
Helper module to import RAG components without model conflicts
This module isolates RAG imports to prevent conflicts with FastAPI models
"""

import os
import sys
from pathlib import Path
import importlib.util


def import_rag_modules():
    """
    Import RAG modules in an isolated way to avoid model conflicts
    Returns tuple: (ContextAwareRAGFixer, DocumentContext, UserGuidedLaTeXProcessor, success)
    """
    # Get RAG directory
    parent_dir = Path(__file__).parent.parent.parent
    rag_dir = parent_dir / "Rag latex fixer"
    
    # Save original state
    original_cwd = os.getcwd()
    original_path = sys.path.copy()
    
    # CRITICAL: Temporarily hide conflicting modules to prevent import conflicts
    # NOTE: Do NOT include 'os' or 'sys' as they are needed by the import process
    modules_to_backup = {}
    conflicting_modules = ['models', 'utils', 'config', 'api', 'cli']
    
    for module_name in conflicting_modules:
        if module_name in sys.modules:
            modules_to_backup[module_name] = sys.modules[module_name]
            del sys.modules[module_name]
    
    try:
        # Change to RAG directory and set it as first in path
        os.chdir(str(rag_dir))
        sys.path.insert(0, str(rag_dir))
        
        # Now import - Python will find Rag latex fixer/models.py first
        from enhanced_user_guided_rag import ContextAwareRAGFixer, DocumentContext
        from user_guided_comprehensive_rag import UserGuidedLaTeXProcessor
        
        print("✅ RAG components loaded successfully (isolated import)")
        print(f"   ContextAwareRAGFixer: {ContextAwareRAGFixer}")
        print(f"   DocumentContext: {DocumentContext}")
        print(f"   UserGuidedLaTeXProcessor: {UserGuidedLaTeXProcessor}")
        return ContextAwareRAGFixer, DocumentContext, UserGuidedLaTeXProcessor, True
        
    except Exception as e:
        print(f"⚠️  Warning: RAG components not available: {e}")
        print(f"    Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None, None, None, False
        
    finally:
        # Restore original state
        os.chdir(original_cwd)
        sys.path = original_path
        
        # Restore backed up modules
        for module_name, module_obj in modules_to_backup.items():
            sys.modules[module_name] = module_obj
