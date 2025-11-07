from __future__ import annotations

import json
from typing import Iterable

import redis
from redis.commands.search.field import TagField, TextField, VectorField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import ResponseError


class RedisVectorStore:
    def __init__(
        self,
        client: redis.Redis,
        index_name: str,
        vector_field: str = "embedding",
        prefix: str = "doc",
        dim: int = 384,
    ) -> None:
        self.client = client
        self.index_name = index_name
        self.vector_field = vector_field
        self.prefix = prefix
        self.dim = dim

    def ensure_index(self) -> None:
        index = self.client.ft(self.index_name)
        try:
            index.info()
            return
        except ResponseError:
            pass

        schema = (
            TextField("text"),
            TagField("namespace"),
            TextField("metadata"),
            VectorField(
                self.vector_field,
                "HNSW",
                {
                    "TYPE": "FLOAT32",
                    "DIM": self.dim,
                    "DISTANCE_METRIC": "COSINE",
                },
            ),
        )
        definition = IndexDefinition(prefix=[f"{self.prefix}:"] , index_type=IndexType.HASH)
        index.create_index(schema, definition=definition)

    def upsert(self, *, namespace: str, documents: list[dict]) -> int:
        pipe = self.client.pipeline(transaction=False)
        for doc in documents:
            key = f"{self.prefix}:{doc['id']}"
            payload = {
                "text": doc["text"],
                "namespace": namespace,
                "metadata": json.dumps(doc.get("metadata", {})),
                self.vector_field: self._to_bytes(doc["embedding"]),
            }
            pipe.hset(key, mapping=payload)
        pipe.execute()
        return len(documents)

    def similarity_search(self, *, namespace: str, vector: list[float], top_k: int) -> list[dict]:
        query = Query(
            f"(@namespace:{{{namespace}}})=>[KNN {top_k} @{self.vector_field} $vec AS score]"
        ).return_fields("text", "metadata", "score")
        params = {"vec": self._to_bytes(vector)}
        results = self.client.ft(self.index_name).search(query, query_params=params)
        chunks = []
        for doc in results.docs:
            metadata = doc.metadata
            if isinstance(metadata, bytes):
                metadata = metadata.decode("utf-8")
            text = doc.text
            if isinstance(text, bytes):
                text = text.decode("utf-8", errors="ignore")
            doc_id = doc.id.decode("utf-8") if isinstance(doc.id, bytes) else doc.id
            chunks.append(
                {
                    "id": doc_id.replace(f"{self.prefix}:", ""),
                    "text": text,
                    "score": float(doc.score),
                    "metadata": json.loads(metadata) if metadata else {},
                }
            )
        return chunks

    def _to_bytes(self, vector: Iterable[float]) -> bytes:
        import array

        return array.array("f", vector).tobytes()
