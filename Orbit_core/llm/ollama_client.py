"""
Ollama client for local LLM inference
"""

import requests
import json
from typing import List, Dict, Generator

class OllamaClient:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/generate"
        self.chat_url = f"{base_url}/api/chat"
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(self.base_url, timeout=2)
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, system_prompt: str = "") -> Generator[str, None, None]:
        """Generate a streaming response from a prompt."""
        try:
            # OPTIMIZED for RTX 3050 - Fast responses
            speed_system = "Answer directly and concisely. For math, give just the answer."
            if system_prompt:
                full_system = f"{speed_system} {system_prompt}"
            else:
                full_system = speed_system
            
            full_prompt = f"{full_system}\\n{prompt}"
            payload = {
                "model": self.model, 
                "prompt": full_prompt, 
                "stream": True,
                "keep_alive": -1,  # CRITICAL: Keep model loaded after response
                "options": {
                    "temperature": 0.3,      # Slight randomness
                    "top_p": 0.9,            # Better sampling
                    "top_k": 40,             # More choices for better quality
                    "num_predict": 100,      # Allow longer responses (was too short at 40)
                    "repeat_penalty": 1.1,
                    "num_ctx": 2048,         # INCREASED: Better context for home automation
                    "num_thread": 8,         # INCREASED: Use all i5-12450H threads for speed
                    "num_gpu": 99,           # Force GPU usage for all layers
                    "num_batch": 512,        # Batch processing for throughput
                    "stop": ["\\n\\n", "<|im_end|>", "</s>"]  # Multiple stop tokens
                }
            }
            
            # INCREASED TIMEOUT: First query may take longer (model loading)
            # Subsequent queries will be <2s with keep_alive=-1
            with requests.post(self.api_url, json=payload, stream=True, timeout=30) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            yield chunk.get("response", "")
                            if chunk.get("done"):
                                break
                else:
                    yield f"Error: Ollama returned status {response.status_code}"
        except requests.exceptions.Timeout:
            yield "⏱️  Ollama timeout (>30s). Model may be loading for first time. Try: 'ollama run qwen2.5:3b' in separate terminal to keep model loaded."
        except requests.exceptions.RequestException:
            yield "❌ Ollama connection failed. Is it running? Start with: ollama serve"
        except KeyboardInterrupt:
            yield "⏹️  Cancelled by user"
            raise  # Re-raise to propagate
        except Exception as e:
            yield f"Error: {str(e)}"

    def chat(self, messages: List[Dict], system_prompt: str = "") -> Generator[str, None, None]:
        """Chat with a streaming response and conversation context."""
        try:
            chat_messages = []
            # OPTIMIZED for RTX 3050 - Fast responses
            speed_system = "Answer directly and concisely. For math, give just the answer."
            if system_prompt:
                full_system = f"{speed_system} {system_prompt}"
            else:
                full_system = speed_system
                
            chat_messages.append({"role": "system", "content": full_system})
            chat_messages.extend(messages)
            
            payload = {
                "model": self.model, 
                "messages": chat_messages, 
                "stream": True,
                "keep_alive": -1,  # CRITICAL: Keep model loaded after response
                "options": {
                    "temperature": 0.3,      # Slight randomness
                    "top_p": 0.9,            # Better sampling
                    "top_k": 40,             # More choices for better quality
                    "num_predict": 100,      # Allow longer responses
                    "repeat_penalty": 1.1,
                    "num_ctx": 2048,         # INCREASED: Better context
                    "num_thread": 8,         # INCREASED: Use all CPU threads
                    "num_gpu": 99,           # Force GPU usage
                    "num_batch": 512,        # Batch processing
                    "stop": ["\\n\\n", "<|im_end|>", "</s>"]  # Multiple stop tokens
                }
            }
            
            # INCREASED TIMEOUT for first query
            with requests.post(self.chat_url, json=payload, stream=True, timeout=30) as response:
                if response.status_code == 200:
                    for line in response.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            yield chunk.get("message", {}).get("content", "")
                            if chunk.get("done"):
                                break
                else:
                    yield f"Error: Ollama returned status {response.status_code}"
        except requests.exceptions.Timeout:
            yield "⏱️  Ollama timeout (>30s). Model may be loading for first time. Try: 'ollama run qwen2.5:3b' in separate terminal to keep model loaded."
        except requests.exceptions.RequestException:
            yield "❌ Ollama connection failed. Is it running? Start with: ollama serve"
        except KeyboardInterrupt:
            yield "⏹️  Cancelled by user"
            raise  # Re-raise to propagate
        except Exception as e:
            yield f"Error: {str(e)}"

    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except:
            return []