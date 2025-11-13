"""
Serviços do Sistema GED
"""
from .ai_client import (
    extract_text,
    classify_document,
    summarize_text,
    search_semantic,
    suggest_responsavel
)

__all__ = [
    'extract_text',
    'classify_document',
    'summarize_text',
    'search_semantic',
    'suggest_responsavel'
]
