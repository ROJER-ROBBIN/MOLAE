import os
from abc import ABC, abstractmethod
from google import genai
from google.genai import types

class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_message: str) -> str:
        pass

class GeminiProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gemini-2.5-flash")
        # Ensure we don't crash the server at init if the key is missing; let it fail at runtime
        self.client = genai.Client(api_key=api_key) if api_key else None

    def generate_response(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            raise ValueError("Configuration Error: GEMINI_API_KEY is missing.")
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                )
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"LLM Provider Error: {str(e)}")

def get_llm_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "gemini").lower()
    if provider_name == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")
