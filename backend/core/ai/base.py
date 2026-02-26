from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class AIProvider(ABC):
    """Abstract base class for AI providers (Groq, Gemini, OpenAI)."""

    @abstractmethod
    def generate_text(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None, 
                      model: Optional[str] = None,
                      **kwargs) -> Optional[str]:
        """Generate text completion."""
        pass

    @abstractmethod
    def generate_json(self, 
                      prompt: str, 
                      schema: Optional[Dict] = None,
                      system_prompt: Optional[str] = None,
                      model: Optional[str] = None,
                      **kwargs) -> Optional[Dict]:
        """Generate structured JSON output."""
        pass
