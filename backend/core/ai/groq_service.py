import os
import logging
import json
from typing import Optional, Dict, List, Any
from .base import AIProvider

logger = logging.getLogger(__name__)

class GroqProvider(AIProvider):
    """
    Groq AI Provider implementation using Llama 3.1 models.
    """
    DEFAULT_MODEL = "llama-3.1-8b-instant"

    def __init__(self, api_key: Optional[str] = None):
        self.client = None
        self.api_key = api_key or os.environ.get('GROQ_API_KEY')
        
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info("✅ GroqProvider initialized.")
            except ImportError:
                logger.warning("⚠️ Groq library not installed.")
            except Exception as e:
                logger.error(f"❌ Failed to initialize GroqProvider: {e}")
        else:
            logger.warning("⚠️ GROQ_API_KEY not set.")

    def generate_text(self, 
                      prompt: str, 
                      system_prompt: Optional[str] = None, 
                      model: Optional[str] = None,
                      **kwargs) -> Optional[str]:
        
        if not self.client:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        try:
            completion = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1024),
                top_p=kwargs.get('top_p', 1.0),
                stream=False
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Groq generate_text failed: {e}")
            return None

    def generate_json(self, 
                      prompt: str, 
                      schema: Optional[Dict] = None, # Not used by Groq directly in this mode, but interface contract
                      system_prompt: Optional[str] = None,
                      model: Optional[str] = None,
                      **kwargs) -> Optional[Dict]:
        
        if not self.client:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        try:
            completion = self.client.chat.completions.create(
                model=model or self.DEFAULT_MODEL,
                messages=messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 1024),
                top_p=kwargs.get('top_p', 1.0),
                stream=False,
                response_format={"type": "json_object"}
            )
            content = completion.choices[0].message.content
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Groq generate_json parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"Groq generate_json failed: {e}")
            return None
