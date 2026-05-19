"""
API Bridge Module - Integração com Legal AI Backend
Fornece cliente HTTP para comunicação com FastAPI do Legal AI
"""

from .client import LegalAIClient

__all__ = ['LegalAIClient']
