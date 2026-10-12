from app.core.config import settings
from app.infrastructure.vectorstore.qdrant import QdrantVectorStore
from app.rag.chunking.semantic import SemanticChunker
from app.rag.embeddings.sentence_transformer import (
    SentenceTransformerEmbedding,
)
from app.rag.ingestion.service import IngestionService
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


def create_ingestion_service() -> IngestionService:
    """Build the document ingestion pipeline."""
    embedding_provider = SentenceTransformerEmbedding()
    vector_store = QdrantVectorStore()

    return IngestionService(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )


def create_tender_ingestion_service():
    """Build the complete tender document ingestion service."""
    from app.application.document_service import DocumentService
    from app.application.tender_ingestion_service import TenderIngestionService

    return TenderIngestionService(
        document_service=DocumentService(),
        chunker=SemanticChunker(),
        ingestion_service=create_ingestion_service(),
    )
