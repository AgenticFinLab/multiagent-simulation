"""masim.knowledge.store — Concrete knowledge store implementation

Implements BaseKnowledgeStore using LlamaIndex VectorStoreIndex with
built-in LlamaIndex embedding backends:

1. HuggingFace local embeddings (default, no API key required)
   - Uses sentence-transformers models like "BAAI/bge-small-en-v1.5"
   - Runs entirely locally, no network calls
   - Recommended for offline development and testing

2. OpenAI embeddings (including compatible endpoints)
   - Requires API key, optionally custom base URL
   - Supports OpenAI, ARK/ByteDance, DeepSeek, etc.
   - Use when you have access to an OpenAI-compatible embedding API

Indexing pipeline:
    KnowledgeDocument list
        → SentenceSplitter(chunk_size=512, chunk_overlap=64)
        → Embedding (HuggingFace or OpenAI)
        → LlamaIndex VectorStoreIndex
        → persisted to persist_dir

Retrieval pipeline:
    KnowledgeQuery.text
        → embed with same model
        → cosine similarity search
        → KnowledgeResult(chunks=[...])

For the abstract interface and full design documentation, see base.py.

Dependencies:
    llama_index_core
    llama_index_embeddings_huggingface
    llama_index_embeddings_openai (optional, for OpenAI backend)
"""

from __future__ import annotations

import logging
import os
from typing import Any, List, Optional

from llama_index.core import (
    Document,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core import Settings as LlamaSettings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from masim.knowledge.base import (
    BaseKnowledgeStore,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeResult,
)

logger = logging.getLogger("masim.knowledge.store")

# Default HuggingFace embedding model (local, no API key required)
DEFAULT_EMBED_MODEL = "BAAI/bge-small-en-v1.5"


class KnowledgeStore(BaseKnowledgeStore):
    """Persistent vector knowledge store: build / persist / load / query.

    Wraps LlamaIndex VectorStoreIndex with built-in embedding backends.
    Once built, the store can be persisted to disk and reloaded on subsequent
    runs (supporting the simulation resume mechanism).

    Embedding Backends
    ------------------
    1. HuggingFace (default, embed_type="huggingface"):
       - Local embeddings, no API key required
       - Default model: "BAAI/bge-small-en-v1.5" (384 dimensions, fast)
       - Set embed_model_name to any sentence-transformers model

    2. OpenAI (embed_type="openai"):
       - Requires embed_api_key, optionally embed_api_base for custom endpoints
       - Supports OpenAI, ARK/ByteDance, DeepSeek, and other OpenAI-compatible APIs
       - Set embed_model_name to your model/endpoint ID

    Parameters
    ----------
    embed_model_name:
        Embedding model identifier. For HuggingFace, use sentence-transformers
        model names (e.g., ``"BAAI/bge-small-en-v1.5"``). For OpenAI, use the
        model name or endpoint ID (e.g., ``"text-embedding-3-small"``).
    embed_api_key:
        API key for OpenAI endpoint. Ignored for HuggingFace.
    embed_api_base:
        Base URL for OpenAI-compatible endpoint. Use this for non-OpenAI
        providers (ARK, DeepSeek, etc.). Ignored for HuggingFace.
    embed_type:
        "huggingface" (default) or "openai". If not specified, auto-detects
        based on whether embed_api_key is provided.
    persist_dir:
        Optional directory to persist / reload the index. If ``None`` the
        index is kept in memory only.
    chunk_size:
        Token-level chunk size for ``SentenceSplitter`` (default 512).
    chunk_overlap:
        Overlap between adjacent chunks (default 64).
    """

    def __init__(
        self,
        embed_model_name: str = DEFAULT_EMBED_MODEL,
        embed_api_key: str = "",
        embed_api_base: str = "",
        embed_type: Optional[str] = None,
        persist_dir: Optional[str] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 64,
    ) -> None:
        # Auto-detect embed_type if not specified
        if embed_type is None:
            embed_type = "openai" if embed_api_key else "huggingface"

        super().__init__(
            embed_model_name=embed_model_name,
            embed_api_key=embed_api_key,
            embed_api_base=embed_api_base,
            persist_dir=persist_dir,
        )
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._index: Optional[VectorStoreIndex] = None
        self._embed_type = embed_type
        self._embed_model_name = embed_model_name

        # Set up embedding model based on type
        if embed_type == "huggingface":
            embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
            logger.info(
                "KnowledgeStore using HuggingFace embedding: model=%s",
                embed_model_name,
            )
        elif embed_type == "openai":
            if not embed_api_key:
                raise ValueError(
                    f"KnowledgeStore: embed_type={embed_type!r} requires embed_api_key. "
                    f"Set embed_type='huggingface' for local embeddings (no API key)."
                )
            # Import here to avoid dependency if not used
            from llama_index.embeddings.openai import OpenAIEmbedding

            embed_model = OpenAIEmbedding(
                model=embed_model_name,
                api_key=embed_api_key,
                api_base=embed_api_base,
            )
            logger.info(
                "KnowledgeStore using OpenAI embedding: model=%s, base=%s",
                embed_model_name,
                embed_api_base or "(default)",
            )
        else:
            raise ValueError(
                f"KnowledgeStore: unknown embed_type={embed_type!r}. "
                f"Use 'huggingface' or 'openai'."
            )

        LlamaSettings.embed_model = embed_model

        logger.info(
            "KnowledgeStore configured: persist_dir=%s",
            persist_dir or "(memory only)",
        )

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build(self, documents: List[KnowledgeDocument]) -> None:
        """Build the vector index from a list of KnowledgeDocument objects.

        Converts each KnowledgeDocument to a LlamaIndex Document, chunks
        with SentenceSplitter, embeds, and stores in a VectorStoreIndex.

        Parameters
        ----------
        documents:
            Documents returned by ``KnowledgeLoader`` (List[KnowledgeDocument]).
            Must contain at least one document.

        Raises
        ------
        ValueError
            If documents is empty. RAG requires at least one document.

        Notes
        -----
        After building, the index is automatically persisted to
        ``persist_dir`` (if configured).
        """
        # Convert KnowledgeDocument → LlamaIndex Document
        llama_docs: List[Document] = []
        for kd in documents:
            llama_docs.append(
                Document(
                    text=kd.text,
                    metadata={
                        "source": kd.source,
                        "source_type": kd.source_type.name,
                        "title": kd.title,
                        "acquired_at": kd.acquired_at,
                        **kd.metadata,
                    },
                )
            )

        if not llama_docs:
            raise ValueError(
                "KnowledgeStore.build: no documents provided. "
                "RAG requires at least one document to build an index. "
                "Check that document loading succeeded (API keys, network, etc.)"
            )

        splitter = SentenceSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )

        logger.info(
            "KnowledgeStore.build: indexing %d document(s) with chunk_size=%d …",
            len(llama_docs),
            self._chunk_size,
        )

        self._index = VectorStoreIndex.from_documents(
            llama_docs,
            transformations=[splitter],
            show_progress=False,
        )

        if self.persist_dir:
            os.makedirs(self.persist_dir, exist_ok=True)
            self._index.storage_context.persist(persist_dir=self.persist_dir)
            logger.info("KnowledgeStore.build: index persisted to %s", self.persist_dir)

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load(self, persist_dir: Optional[str] = None) -> None:
        """Load a previously persisted index from disk.

        Parameters
        ----------
        persist_dir:
            Directory to load from. Falls back to the ``persist_dir``
            supplied at construction time.

        Raises
        ------
        FileNotFoundError
            If the directory does not exist or is not a valid index.
        """
        target = persist_dir or self.persist_dir
        if not target or not os.path.isdir(target):
            raise FileNotFoundError(
                f"KnowledgeStore.load: persist_dir not found: {target!r}"
            )

        logger.info("KnowledgeStore.load: loading index from %s", target)
        storage_context = StorageContext.from_defaults(persist_dir=target)
        self._index = load_index_from_storage(storage_context)
        logger.info("KnowledgeStore.load: index loaded successfully")

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(self, query: KnowledgeQuery) -> KnowledgeResult:
        """Retrieve the most relevant knowledge chunks for a KnowledgeQuery.

        Parameters
        ----------
        query:
            A ``KnowledgeQuery`` built from the current market context.
            ``query.text`` is embedded and searched; ``query.top_k``
            controls how many chunks are returned.

        Returns
        -------
        KnowledgeResult
            Retrieved chunks in relevance order. ``is_empty`` is True
            if the store is not built or no matching chunks are found.
        """
        if self._index is None:
            logger.warning(
                "KnowledgeStore.query: store not built; returning empty result"
            )
            return KnowledgeResult(chunks=[], query=query)

        try:
            retriever = self._index.as_retriever(similarity_top_k=query.top_k)
            nodes = retriever.retrieve(query.text)
            chunks = [node.get_content() for node in nodes] if nodes else []
            logger.debug(
                "KnowledgeStore.query: retrieved %d chunk(s) for round=%s",
                len(chunks),
                query.round_num,
            )
            return KnowledgeResult(chunks=chunks, query=query)
        except Exception as exc:
            logger.error("KnowledgeStore.query: retrieval error: %s", exc)
            return KnowledgeResult(chunks=[], query=query)

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def is_built(self) -> bool:
        """Return True if the store has been built or loaded."""
        return self._index is not None

    def __repr__(self) -> str:
        return (
            f"KnowledgeStore(built={self.is_built()}, "
            f"persist_dir={self.persist_dir!r})"
        )
