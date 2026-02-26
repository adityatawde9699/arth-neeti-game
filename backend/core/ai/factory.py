from typing import Optional
from .base import AIProvider
from .groq_service import GroqProvider

_provider_instance: Optional[AIProvider] = None

def get_ai_provider() -> AIProvider:
    """
    Factory method to get the configured AI provider.
    Currently defaults to Groq, but can be extended for Gemini/OpenAI.
    """
    global _provider_instance
    if _provider_instance is None:
        # Check env or config to decide provider
        # For now, default to Groq
        _provider_instance = GroqProvider()
    
    return _provider_instance

def reset_ai_provider():
    """Reset singleton (for testing)."""
    global _provider_instance
    _provider_instance = None
