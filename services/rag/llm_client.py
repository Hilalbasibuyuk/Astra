
import os

import httpx
from apps.config import settings

class LLMServiceError(RuntimeError):
    """Raised when the local LLM cannot generate a response."""


class OllamaLLMClient:
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        self.base_url = (
            base_url or settings.ollama_base_url
        ).rstrip("/")

        self.model = model or settings.ollama_model

        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else settings.ollama_timeout_seconds
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "options": {
                "temperature": 0.1,
            },
        }

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise LLMServiceError(
                "Ollama could not generate a response. "
                "Check that Ollama is running and the model is available."
            ) from exc

        content = data.get("message", {}).get("content", "")

        if not isinstance(content, str) or not content.strip():
            raise LLMServiceError(
                "Ollama returned an empty response."
            )

        return content.strip()
