from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:  # pragma: no cover
    from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str, device: str | None = None):
        self.model_name = model_name
        self._model: "SentenceTransformer | None" = None
        self._device = device

    @property
    def model(self) -> "SentenceTransformer":
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name, device=self._device)
        return self._model

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        text_list = list(texts)
        if not text_list:
            return []
        embeddings = self.model.encode(text_list, convert_to_numpy=False, normalize_embeddings=True)
        return [list(map(float, vector)) for vector in embeddings]

    def embed_query(self, text: str) -> list[float]:
        vector = self.embed([text])
        return vector[0] if vector else []
