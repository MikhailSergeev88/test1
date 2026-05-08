"""
RAG (Retrieval Augmented Generation) pipeline implementation.
Handles document chunking, embedding, and retrieval.
"""

import hashlib
from typing import List, Optional, Tuple
from dataclasses import dataclass

import numpy as np
from structlog import get_logger

from app.config.settings import settings

logger = get_logger(__name__)


@dataclass
class RetrievedChunk:
    """Represents a retrieved document chunk."""

    content: str
    document_title: str
    document_id: int
    chunk_index: int
    similarity_score: float
    metadata: dict


class EmbeddingService:
    """Service for generating embeddings."""

    def __init__(self):
        self._model = None
        self._model_name = settings.embedding_model

    def _load_model(self):
        """Lazy load embedding model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
                logger.info("Embedding model loaded", model=self._model_name)
            except ImportError:
                logger.warning("sentence-transformers not installed, using mock embeddings")
                self._model = "mock"

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        self._load_model()

        if self._model == "mock":
            # Mock embedding for fallback
            return np.random.randn(384).astype(np.float32)

        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """Generate embeddings for multiple texts."""
        self._load_model()

        if self._model == "mock":
            return [np.random.randn(384).astype(np.float32) for _ in texts]

        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return [emb.astype(np.float32) for emb in embeddings]


class DocumentChunker:
    """Service for chunking documents."""

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or settings.rag_chunk_size
        self.chunk_overlap = chunk_overlap or settings.rag_chunk_overlap

    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> List[Tuple[str, dict]]:
        """
        Split text into chunks with overlap.

        Returns list of (chunk_content, chunk_metadata) tuples.
        """
        chunks = []
        
        # Simple paragraph-based chunking
        paragraphs = text.split('\n\n')
        current_chunk = ""
        current_metadata = metadata or {}

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) > self.chunk_size:
                # Save current chunk if it exists
                if current_chunk:
                    chunks.append((current_chunk.strip(), current_metadata.copy()))
                
                # Start new chunk with overlap
                if self.chunk_overlap > 0 and current_chunk:
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + "\n\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # Add final chunk
        if current_chunk:
            chunks.append((current_chunk.strip(), current_metadata.copy()))

        return chunks

    def chunk_text_fixed(self, text: str, metadata: Optional[dict] = None) -> List[Tuple[str, dict]]:
        """Split text into fixed-size chunks with overlap."""
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = text.rfind('.', start, end)
                last_newline = text.rfind('\n', start, end)
                break_point = max(last_period, last_newline)
                if break_point > start:
                    end = break_point + 1

            chunk = text[start:end].strip()
            if chunk:
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata['start_pos'] = start
                chunk_metadata['end_pos'] = end
                chunks.append((chunk, chunk_metadata))

            start = end - self.chunk_overlap if end < text_length else text_length

        return chunks


class RAGPipeline:
    """Main RAG pipeline for retrieval and generation."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.chunker = DocumentChunker()
        self._vector_store = None

    async def initialize(self) -> None:
        """Initialize the RAG pipeline."""
        logger.info("Initializing RAG pipeline")
        # Vector store will be initialized via database repository

    def compute_content_hash(self, content: str) -> str:
        """Compute hash of content for change detection."""
        return hashlib.sha256(content.encode()).hexdigest()

    async def retrieve(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None,
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User query
            top_k: Number of results to return
            threshold: Similarity threshold

        Returns:
            List of retrieved chunks
        """
        top_k = top_k or settings.rag_top_k_results
        threshold = threshold or settings.rag_similarity_threshold

        logger.info("Retrieving chunks", query=query[:50], top_k=top_k)

        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)

        # TODO: Implement pgvector similarity search
        # For now, return empty list - will be implemented with database integration
        # This requires pgvector extension and proper SQL queries

        logger.warning("Vector search not yet implemented, returning empty results")
        return []

    async def retrieve_with_reranking(
        self,
        query: str,
        top_k: int = None,
        rerank_top_k: int = 3,
    ) -> List[RetrievedChunk]:
        """
        Retrieve and rerank chunks.

        Args:
            query: User query
            top_k: Initial number of results
            rerank_top_k: Final number of results after reranking

        Returns:
            List of reranked chunks
        """
        # Initial retrieval
        chunks = await self.retrieve(query, top_k=top_k or top_k * 2)

        if len(chunks) <= rerank_top_k:
            return chunks

        # Simple reranking based on keyword match score
        # In production, use cross-encoder model
        query_terms = set(query.lower().split())
        
        for chunk in chunks:
            content_terms = set(chunk.content.lower().split())
            overlap = len(query_terms & content_terms)
            chunk.similarity_score += overlap * 0.1  # Boost by term overlap

        # Sort by combined score
        chunks.sort(key=lambda x: x.similarity_score, reverse=True)
        
        return chunks[:rerank_top_k]

    def format_context(self, chunks: List[RetrievedChunk]) -> str:
        """Format retrieved chunks as context for LLM."""
        if not chunks:
            return ""

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Документ {i}: {chunk.document_title}]\n"
                f"{chunk.content}\n"
            )

        return "\n---\n".join(context_parts)

    def format_sources(self, chunks: List[RetrievedChunk]) -> dict:
        """Format sources for citation."""
        sources = []
        for chunk in chunks:
            sources.append({
                "document_title": chunk.document_title,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "similarity_score": round(chunk.similarity_score, 3),
            })
        return {"sources": sources, "count": len(sources)}


# Global RAG pipeline instance
_rag_pipeline: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    """Get global RAG pipeline instance."""
    global _rag_pipeline
    if _rag_pipeline is None:
        _rag_pipeline = RAGPipeline()
    return _rag_pipeline


async def initialize_rag() -> None:
    """Initialize global RAG pipeline."""
    pipeline = get_rag_pipeline()
    await pipeline.initialize()
