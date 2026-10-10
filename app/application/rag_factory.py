from app.core.config import settings
from app.infrastructure.vectorstore.qdrant import QdrantVectorStore
from app.rag.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from app.rag.reranking.bge import BGEReranker
from app.rag.retrieval.service import RetrievalService


def create_retrieval_service() -> RetrievalService:
    """Build the RAG retrieval pipeline with reranking enabled."""
    embedding_provider = SentenceTransformerEmbedding()
    vector_store = QdrantVectorStore()
    reranker = BGEReranker(
        model_name=settings.reranker_model,
        device=settings.reranker_device,
    )

    return RetrievalService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        reranker=reranker,
    )
