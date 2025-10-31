"""
OpenAI-compatible client for cloud-based LLM inference (supports GitHub Models)
"""
import openai
from typing import List, Dict, Generator, Optional

class OpenAIClient:
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        if not api_key:
            raise ValueError("API key not provided.")
        
        # Initialize client with optional custom base URL (for GitHub Models)
        if base_url:
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = openai.OpenAI(api_key=api_key)
        
        self.model = model

    def generate(self, system_prompt: str, prompt: str, context: List[Dict] = None) -> Generator[str, None, None]:
        """Generate a streaming response using the OpenAI-compatible API."""
        messages = [{"role": "system", "content": system_prompt}]
        if context:
            messages.extend(context)
        messages.append({"role": "user", "content": prompt})

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            for chunk in stream:
                # Handle different response formats
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        yield delta.content
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error communicating with API: {error_msg}")
            
            # Provide helpful error messages
            if "404" in error_msg or "not found" in error_msg.lower():
                yield f"Error: Model '{self.model}' not found. Please check the model name and try again."
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                yield "Error: Invalid API key. Please check your API key configuration."
            elif "rate" in error_msg.lower() or "quota" in error_msg.lower():
                yield "Error: API rate limit exceeded. Please try again later."
            else:
                yield f"An error occurred with the AI API: {error_msg}"