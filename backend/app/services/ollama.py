from __future__ import annotations

from typing import Any

import httpx


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def generate(self, prompt: str) -> dict[str, Any]:
        payload = {"model": self.model, "prompt": prompt}
        response = await self._client.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return data

    async def aclose(self) -> None:
        await self._client.aclose()
