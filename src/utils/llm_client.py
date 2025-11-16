import os
from typing import Optional
from dotenv import load_dotenv
import openai

load_dotenv()


class LLMClient:
    """Wrapper for OpenAI GPT API calls."""

    def __init__(self, model: Optional[str] = None):
        """Initialize LLM client.

        Args:
            model: Specific model name (optional, defaults to gpt-4o-mini)
        """
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = model or "gpt-4o-mini"


    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> str:
        """Generate a response from OpenAI GPT.

        Args:
            prompt: The user prompt. If json_mode=True, must explicitly request JSON in the prompt.
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-2.0). Lower = more deterministic. Default 0.7.
            max_tokens: Maximum tokens to generate
            json_mode: If True, forces model to return valid JSON. Prompt must mention JSON format.

        Returns:
            Generated text response (JSON string if json_mode=True)
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
