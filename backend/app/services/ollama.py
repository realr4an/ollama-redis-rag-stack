from __future__ import annotations

from typing import Any

import json

import httpx


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout: int = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._timeout = httpx.Timeout(timeout, connect=15.0, read=timeout, write=15.0)
        self._client = httpx.AsyncClient(timeout=self._timeout)

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
        try:
            async with self._client.stream("POST", url, json=payload, timeout=self._timeout) as response:
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
        except httpx.ReadTimeout as exc:
            raise TimeoutError("Ollama generation timed out") from exc
        except httpx.HTTPError as exc:
            raise RuntimeError("Ollama generation failed") from exc

    async def aclose(self) -> None:
        await self._client.aclose()
