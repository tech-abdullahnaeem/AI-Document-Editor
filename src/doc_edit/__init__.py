"""
Document Editing Agent - Minimal exports for compiler service
"""

__version__ = "0.1.0"
__author__ = "Abdullah"

# Only export what's actually used by the API
from .latex_compiler import LaTeXCompiler

__all__ = [
    "LaTeXCompiler",
]
