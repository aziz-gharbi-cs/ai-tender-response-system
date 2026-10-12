from typing import Any
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models

from app.core.config import settings
from app.domain.interfaces.vector_store import VectorStore


class QdrantVectorStore(VectorStore):
    """
    Qdrant implementation of the application's VectorStore interface.
    """

    def __init__(self) -> None:
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
        )

        self.collection_name = settings.qdrant_collection

    @staticmethod
    def _point_id(document_id: str) -> str:
        return str(uuid5(NAMESPACE_URL, document_id))

    def ensure_collection(
        self,
        vector_size: int,
    ) -> None:
        """Create the Qdrant collection if it doesn't exist."""

        collections = self.client.get_collections()

        exists = any(
            collection.name == self.collection_name
            for collection in collections.collections
        )

        if exists:
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE,
            ),
        )

    async def add_documents(
        self,
        documents: list[dict[str, Any]],
    ) -> None:
        """Store vectorized document chunks."""

        if not documents:
            return

        first_vector = documents[0].get("vector")

        if not first_vector:
            raise ValueError(
                "Each document must contain a 'vector'."
            )

        self.ensure_collection(
            vector_size=len(first_vector),
        )

        points = [
            models.PointStruct(
                id=self._point_id(str(document["id"])),
                vector=document["vector"],
                payload={
                    **document.get("payload", {}),
                    "chunk_id": document["id"],
                },
            )
            for document in documents
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    async def similarity_search(
        self,
        query_vector: list[float],
        *,
        top_k: int = 5,
        document_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search Qdrant, optionally restricting results to one document."""

        query_filter = None
        if document_id is not None:
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        ).points

        return [
            {
                "id": result.id,
                "score": result.score,
                "payload": result.payload or {},
            }
            for result in results
        ]
