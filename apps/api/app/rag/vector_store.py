from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import get_settings


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.collection = settings.qdrant_collection
        self.client = QdrantClient(host=settings.qdrant_host, port=settings.qdrant_port)

    def ensure_collection(self, vector_size: int = 3072) -> None:
        existing = [c.name for c in self.client.get_collections().collections]
        if self.collection not in existing:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
            )

    def upsert(self, points: list[qmodels.PointStruct]) -> None:
        if points:
            self.client.upsert(collection_name=self.collection, points=points)

    def search(self, vector: list[float], limit: int = 8):
        return self.client.search(collection_name=self.collection, query_vector=vector, limit=limit)
