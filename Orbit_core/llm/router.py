"""
LLM Router - Uses OpenAI-compatible API (GitHub Models)
"""
from Orbit_core.llm.openai_client import OpenAIClient
from typing import List, Dict, Optional, Generator

class LLMRouter:
    def __init__(self, settings):
        self.settings = settings
        self.openai_client = None

        # Initialize OpenAI/GitHub API client
        if settings.OPENAI_API_KEY:
            try:
                base_url = getattr(settings, 'OPENAI_BASE_URL', None)
                self.openai_client = OpenAIClient(
                    settings.OPENAI_API_KEY, 
                    settings.OPENAI_MODEL,
                    base_url=base_url
                )
                print(f"✅ AI client initialized ({settings.OPENAI_MODEL})")
            except Exception as e:
                print(f"❌ AI client failed to initialize: {e}")
        else:
            print("❌ No API key provided. Please set OPENAI_API_KEY in .env file")

    def generate(self, prompt: str, context: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """Generate a response using the AI API."""
        system_prompt = self.settings.get_system_prompt()

        # Use OpenAI/GitHub API
        if self.openai_client:
            try:
                yield from self.openai_client.generate(system_prompt, prompt, context)
                return
            except Exception as e:
                print(f"❌ AI API failed: {e}")
                yield self._fallback_response(prompt)
        else:
            yield self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """Fallback response when no LLM is available."""
        return "I am running in a limited mode as no AI model is available. Please check your API key configuration."