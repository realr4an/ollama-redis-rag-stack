from __future__ import annotations

from typing import Any

import json

import httpx


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def generate(
        self,
        prompt: str,
        model: str | None = None,
        temperature: float | None = None,
    ) -> dict[str, Any]:
        payload = {
            "model": model or self.model,
            "prompt": prompt,
            "stream": True,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        url = f"{self.base_url}/api/generate"
        async with self._client.stream("POST", url, json=payload) as response:
            response.raise_for_status()
            chunks: list[str] = []
            meta: dict[str, Any] = {}
            async for line in response.aiter_lines():
                if not line:
                    continue
                data = json.loads(line)
                if data.get("done"):
                    meta = data
                    break
                chunks.append(data.get("response", ""))
            return {"response": "".join(chunks), "meta": meta}

    async def aclose(self) -> None:
        await self._client.aclose()
