from __future__ import annotations

from typing import Protocol

import httpx

from app.core.config import get_settings


class EmbeddingProvider(Protocol):
    async def embed_texts(self, texts: list[str]) -> list[list[float]]: ...


class LLMProvider(Protocol):
    async def answer(self, prompt: str) -> str: ...


class OpenAICompatibleEmbeddingProvider:
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for embeddings")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.openai_api_base}/embeddings",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={"model": settings.openai_embedding_model, "input": texts},
            )
            response.raise_for_status()
            payload = response.json()
            return [item["embedding"] for item in payload.get("data", [])]


class OpenAICompatibleLLMProvider:
    async def answer(self, prompt: str) -> str:
        settings = get_settings()
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for assistant responses")
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{settings.openai_api_base}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an incident investigation assistant. Clearly separate facts from inferences and do not overstate certainty.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
            )
            response.raise_for_status()
            payload = response.json()
            return payload["choices"][0]["message"]["content"]


def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.embedding_provider == "openai_compatible":
        return OpenAICompatibleEmbeddingProvider()
    raise RuntimeError(f"Unsupported embedding provider: {settings.embedding_provider}")


def get_llm_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleLLMProvider()
    raise RuntimeError(f"Unsupported LLM provider: {settings.llm_provider}")
