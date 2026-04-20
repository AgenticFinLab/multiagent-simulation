"""masim.knowledge.store — Concrete knowledge store implementation

Implements BaseKnowledgeStore using LlamaIndex VectorStoreIndex with
built-in LlamaIndex embedding backends:

1. HuggingFace local embeddings (default, no API key required)
   - Uses sentence-transformers models like "BAAI/bge-small-en-v1.5"
   - Runs entirely locally, no network calls
   - Recommended for offline development and testing

2. OpenAI embeddings (including compatible endpoints)
   - Requires API key, optionally custom base URL
   - Supports OpenAI, DeepSeek, etc.
   - Use when you have access to an OpenAI-compatible embedding API

3. LiteLLM embeddings (Hunyuan only)
   - Unified API for Hunyuan embedding
   - Hunyuan: model="openai/hunyuan-embedding", api_base="https://api.hunyuan.cloud.tencent.com/v1"
   - Use HUNYUAN_API_KEY env var

4. Volcengine embeddings (ByteDance/Doubao ARK) - DEPRECATED
   - Not supported, use Hunyuan instead

Indexing pipeline:
    KnowledgeDocument list
        → SentenceSplitter(chunk_size=512, chunk_overlap=64)
        → Embedding (HuggingFace, OpenAI, or LiteLLM)
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
    llama_index_embeddings_litellm (optional, for Hunyuan embedding)
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

    Fail-Fast Behavior
    ------------------
    By default, operations will raise exceptions rather than silently failing.
    This ensures users are immediately aware of issues with:
    - Missing API keys
    - Invalid embedding models
    - Empty document lists
    - Corrupt persisted indexes

    Embedding Backends
    ------------------
    1. HuggingFace (default, embed_type="huggingface"):
       - Local embeddings, no API key required
       - Default model: "BAAI/bge-small-en-v1.5" (384 dimensions, fast)
       - Set embed_model_name to any sentence-transformers model

    2. OpenAI (embed_type="openai"):
       - Requires embed_api_key, optionally embed_api_base for custom endpoints
       - Supports OpenAI, DeepSeek, and other OpenAI-compatible APIs
       - Set embed_model_name to your model/endpoint ID

    3. LiteLLM (embed_type="litellm", Hunyuan only):
       - Unified API for Hunyuan embedding
       - Hunyuan: embed_model_name="openai/hunyuan-embedding", embed_api_base="https://api.hunyuan.cloud.tencent.com/v1"
       - Requires HUNYUAN_API_KEY env var

    4. Volcengine (embed_type="volcengine") - DEPRECATED:
       - Not supported, use Hunyuan instead

    Parameters
    ----------
    embed_model_name:
        Embedding model identifier. For HuggingFace, use sentence-transformers
        model names (e.g., ``"BAAI/bge-small-en-v1.5"``). For LiteLLM/Hunyuan,
        use ``"openai/hunyuan-embedding"``. For OpenAI, use model names like
        ``"text-embedding-3-small"``.
    embed_api_key:
        API key for embedding endpoint. Ignored for HuggingFace.
        For Hunyuan, can also use HUNYUAN_API_KEY env var.
    embed_api_base:
        Base URL for OpenAI-compatible endpoint. Required for Hunyuan
        (``"https://api.hunyuan.cloud.tencent.com/v1"``). Ignored for HuggingFace.
    embed_type:
        "huggingface" (default), "openai", "litellm" (Hunyuan only),
        or "volcengine" (deprecated, not supported).
        If not specified, auto-detects based on whether embed_api_key is provided.
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
            logger.info(
                "[KNOWLEDGE_STORE] Initializing HuggingFace embedding: model=%s",
                embed_model_name,
            )
            try:
                embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
                logger.info(
                    "[KNOWLEDGE_STORE] SUCCESS - HuggingFace embedding loaded: model=%s",
                    embed_model_name,
                )
            except Exception as exc:
                error_msg = f"Failed to load HuggingFace embedding model '{embed_model_name}': {type(exc).__name__}: {exc}"
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")
        elif embed_type == "openai":
            if not embed_api_key:
                error_msg = (
                    f"KnowledgeStore: embed_type={embed_type!r} requires embed_api_key. "
                    f"Set embed_type='huggingface' for local embeddings (no API key)."
                )
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise ValueError(f"[KNOWLEDGE_STORE] {error_msg}")
            # Import here to avoid dependency if not used
            from llama_index.embeddings.openai import OpenAIEmbedding

            logger.info(
                "[KNOWLEDGE_STORE] Initializing OpenAI embedding: model=%s, api_base=%s",
                embed_model_name,
                embed_api_base or "(default)",
            )
            try:
                embed_model = OpenAIEmbedding(
                    model=embed_model_name,
                    api_key=embed_api_key,
                    api_base=embed_api_base,
                )
                logger.info(
                    "[KNOWLEDGE_STORE] SUCCESS - OpenAI embedding configured: model=%s",
                    embed_model_name,
                )
            except Exception as exc:
                error_msg = f"Failed to initialize OpenAI embedding model '{embed_model_name}': {type(exc).__name__}: {exc}"
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")
        elif embed_type == "volcengine":
            # For Volcengine/Doubao embeddings
            # Try embed_api_key first, then fall back to ARK_API_KEY env var
            volcengine_key = embed_api_key or os.getenv("ARK_API_KEY", "")
            if not volcengine_key:
                error_msg = (
                    f"KnowledgeStore: embed_type={embed_type!r} requires embed_api_key "
                    f"or ARK_API_KEY environment variable. "
                    f"Set embed_type='huggingface' for local embeddings (no API key)."
                )
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise ValueError(f"[KNOWLEDGE_STORE] {error_msg}")
            # Import here to avoid dependency if not used
            try:
                from llama_index.embeddings.volcengine import VolcengineEmbeddings
            except ImportError:
                error_msg = (
                    "llama-index-embeddings-volcengine not installed. "
                    "Run: pip install llama-index-embeddings-volcengine"
                )
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")

            logger.info(
                "[KNOWLEDGE_STORE] Initializing Volcengine embedding: model=%s",
                embed_model_name,
            )
            try:
                embed_model = VolcengineEmbeddings(
                    model=embed_model_name,
                    api_key=volcengine_key,
                )
                logger.info(
                    "[KNOWLEDGE_STORE] SUCCESS - Volcengine embedding configured: model=%s",
                    embed_model_name,
                )
            except Exception as exc:
                error_msg = f"Failed to initialize Volcengine embedding model '{embed_model_name}': {type(exc).__name__}: {exc}"
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")
        elif embed_type == "litellm":
            # For LiteLLM unified embedding API (Hunyuan only)
            # Hunyuan: model="openai/hunyuan-embedding", api_base="https://api.hunyuan.cloud.tencent.com/v1"
            litellm_key = embed_api_key or os.getenv("HUNYUAN_API_KEY", "")
            if not litellm_key:
                error_msg = (
                    f"KnowledgeStore: embed_type={embed_type!r} requires embed_api_key "
                    f"or HUNYUAN_API_KEY environment variable. "
                    f"Note: Currently only Hunyuan embedding is supported via LiteLLM. "
                    f"Set embed_type='huggingface' for local embeddings (no API key)."
                )
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise ValueError(f"[KNOWLEDGE_STORE] {error_msg}")
            # Import here to avoid dependency if not used
            try:
                from llama_index.embeddings.litellm import LiteLLMEmbedding
            except ImportError:
                error_msg = (
                    "llama-index-embeddings-litellm not installed. "
                    "Run: pip install llama-index-embeddings-litellm"
                )
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")

            logger.info(
                "[KNOWLEDGE_STORE] Initializing LiteLLM embedding: model=%s, api_base=%s",
                embed_model_name,
                embed_api_base or "(default)",
            )
            try:
                # Build kwargs for LiteLLMEmbedding
                litellm_kwargs = {
                    "model_name": embed_model_name,
                    "api_key": litellm_key,
                }
                # Add api_base if provided (needed for custom endpoints like Hunyuan)
                if embed_api_base:
                    litellm_kwargs["api_base"] = embed_api_base

                embed_model = LiteLLMEmbedding(**litellm_kwargs)
                logger.info(
                    "[KNOWLEDGE_STORE] SUCCESS - LiteLLM embedding configured: model=%s",
                    embed_model_name,
                )
            except Exception as exc:
                error_msg = f"Failed to initialize LiteLLM embedding model '{embed_model_name}': {type(exc).__name__}: {exc}"
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")
        else:
            error_msg = f"KnowledgeStore: unknown embed_type={embed_type!r}. Use 'huggingface', 'openai', 'volcengine' (deprecated), or 'litellm' (recommended for Doubao)."
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise ValueError(f"[KNOWLEDGE_STORE] {error_msg}")

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
        RuntimeError
            If embedding or indexing fails.

        Notes
        -----
        After building, the index is automatically persisted to
        ``persist_dir`` (if configured).
        """
        if not documents:
            error_msg = (
                "KnowledgeStore.build: no documents provided. "
                "RAG requires at least one document to build an index. "
                "Check that document loading succeeded (API keys, network, file paths, etc.)"
            )
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise ValueError(f"[KNOWLEDGE_STORE] {error_msg}")

        logger.info(
            "[KNOWLEDGE_STORE] build: starting index build for %d document(s)",
            len(documents),
        )

        # Convert KnowledgeDocument → LlamaIndex Document
        llama_docs: List[Document] = []
        for idx, kd in enumerate(documents):
            logger.info(
                "[KNOWLEDGE_STORE] build: doc %d/%d - source=%s, chars=%d, title=%s",
                idx + 1,
                len(documents),
                kd.source,
                len(kd.text),
                kd.title or "(none)",
            )
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

        logger.info(
            "[KNOWLEDGE_STORE] build: chunking documents with chunk_size=%d, overlap=%d",
            self._chunk_size,
            self._chunk_overlap,
        )
        splitter = SentenceSplitter(
            chunk_size=self._chunk_size,
            chunk_overlap=self._chunk_overlap,
        )

        try:
            logger.info(
                "[KNOWLEDGE_STORE] build: creating vector index (this may take a moment for large documents)..."
            )
            self._index = VectorStoreIndex.from_documents(
                llama_docs,
                transformations=[splitter],
                show_progress=False,
            )
            logger.info(
                "[KNOWLEDGE_STORE] build: SUCCESS - vector index created from %d document(s)",
                len(llama_docs),
            )
        except Exception as exc:
            error_msg = f"Failed to build vector index: {type(exc).__name__}: {exc}"
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")

        if self.persist_dir:
            logger.info(
                "[KNOWLEDGE_STORE] build: persisting index to %s", self.persist_dir
            )
            try:
                os.makedirs(self.persist_dir, exist_ok=True)
                self._index.storage_context.persist(persist_dir=self.persist_dir)
                logger.info(
                    "[KNOWLEDGE_STORE] build: SUCCESS - index persisted to %s",
                    self.persist_dir,
                )
            except Exception as exc:
                error_msg = f"Failed to persist index to {self.persist_dir}: {type(exc).__name__}: {exc}"
                logger.error("[KNOWLEDGE_STORE] %s", error_msg)
                raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")

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
        RuntimeError
            If the index cannot be loaded (corrupt or incompatible).
        """
        target = persist_dir or self.persist_dir
        if not target:
            error_msg = "KnowledgeStore.load: no persist_dir specified (parameter and instance both None)"
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise FileNotFoundError(f"[KNOWLEDGE_STORE] {error_msg}")

        if not os.path.isdir(target):
            error_msg = f"KnowledgeStore.load: persist_dir not found: {target!r}"
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise FileNotFoundError(f"[KNOWLEDGE_STORE] {error_msg}")

        logger.info("[KNOWLEDGE_STORE] load: loading index from %s", target)
        try:
            storage_context = StorageContext.from_defaults(persist_dir=target)
            self._index = load_index_from_storage(storage_context)
            logger.info(
                "[KNOWLEDGE_STORE] load: SUCCESS - index loaded from %s", target
            )
        except FileNotFoundError:
            error_msg = f"KnowledgeStore.load: index files not found in {target}"
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise
        except Exception as exc:
            error_msg = (
                f"Failed to load index from {target}: {type(exc).__name__}: {exc}"
            )
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")

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

        Raises
        ------
        RuntimeError
            If the store has not been built or loaded.
        """
        if self._index is None:
            error_msg = (
                "KnowledgeStore.query: store not built. "
                "Call build(documents) or load(persist_dir) before querying."
            )
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")

        logger.info(
            "[KNOWLEDGE_STORE] query: searching for top_k=%d, round=%s, query_text='%s'",
            query.top_k,
            query.round_num,
            query.text[:100] + "..." if len(query.text) > 100 else query.text,
        )
        try:
            retriever = self._index.as_retriever(similarity_top_k=query.top_k)
            nodes = retriever.retrieve(query.text)
            chunks = [node.get_content() for node in nodes] if nodes else []
            logger.info(
                "[KNOWLEDGE_STORE] query: SUCCESS - retrieved %d chunk(s) for round=%s",
                len(chunks),
                query.round_num,
            )
            if chunks:
                for i, chunk in enumerate(chunks):
                    logger.debug(
                        "[KNOWLEDGE_STORE] query: chunk %d preview: %s",
                        i + 1,
                        chunk[:100] + "..." if len(chunk) > 100 else chunk,
                    )
            return KnowledgeResult(chunks=chunks, query=query)
        except Exception as exc:
            error_msg = (
                f"KnowledgeStore.query: retrieval error: {type(exc).__name__}: {exc}"
            )
            logger.error("[KNOWLEDGE_STORE] %s", error_msg)
            raise RuntimeError(f"[KNOWLEDGE_STORE] {error_msg}")

    # ------------------------------------------------------------------
    # State helpers
    # ------------------------------------------------------------------

    def is_built(self) -> bool:
        """Return True if the store has been built or loaded."""
        built = self._index is not None
        logger.debug("[KNOWLEDGE_STORE] is_built: %s", built)
        return built

    def is_initialized(self) -> bool:
        """Check if the store is ready for use (built or loaded).

        Returns
        -------
        bool
            True if the store can be queried, False otherwise.
        """
        return self._index is not None

    def __repr__(self) -> str:
        return (
            f"KnowledgeStore(built={self.is_built()}, "
            f"embed_type={self._embed_type}, "
            f"embed_model={self._embed_model_name}, "
            f"persist_dir={self.persist_dir!r})"
        )
