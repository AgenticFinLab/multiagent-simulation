"""
Base Knowledge module for the Multi-Agent Simulation (MASim) framework.

================================================================================
                          MODULE CONTENTS
================================================================================

Dataclasses:
    KnowledgeDocument  - Atomic unit of acquired knowledge (text + metadata)
    KnowledgeQuery     - A retrieval request from an agent at decision time
    KnowledgeResult    - Retrieved knowledge chunks returned to the agent

Enums:
    KnowledgeSourceType - Categorizes how a document was originally acquired

Abstract Classes:
    BaseKnowledgeLoader - Contract for all document acquisition implementations
    BaseKnowledgeStore  - Contract for all knowledge indexing/retrieval implementations

For concrete implementations, see:
    loader.py  →  KnowledgeLoader   (LLM-suggested URLs + local files + CSV)
    store.py   →  KnowledgeStore    (LlamaIndex VectorStoreIndex + ARK embeddings)

================================================================================
                           MODULE OVERVIEW
================================================================================

The masim.knowledge module provides the knowledge infrastructure layer for
agents in the MASim framework. It decouples two concerns:

    1. ACQUISITION  (BaseKnowledgeLoader)
       How does an agent gather documents relevant to its persona?
       Sources: local files (PDF, Markdown), URLs from CSV, LLM-suggested URLs.

    2. RETRIEVAL    (BaseKnowledgeStore)
       Given a query describing the current market context, which knowledge
       fragments are most relevant to include in the agent's decision prompt?

Together they implement a Retrieval-Augmented Generation (RAG) pipeline
embedded within each agent's decision loop:

    Agent init  ──►  BaseKnowledgeLoader.acquire()
                         │
                         ▼
                     KnowledgeDocument list
                         │
                         ▼
                     BaseKnowledgeStore.build(docs)
                         │  (persisted to disk for resume support)
                         ▼

    Each round  ──►  BaseKnowledgeStore.query(KnowledgeQuery)
                         │
                         ▼
                     KnowledgeResult  ──►  injected into LLM prompt

================================================================================
                        DESIGN PHILOSOPHY
================================================================================

1. SEPARATION OF ACQUISITION AND RETRIEVAL
   ─────────────────────────────────────────
   Loading/fetching documents (BaseKnowledgeLoader) is kept strictly separate
   from indexing and querying (BaseKnowledgeStore).

   This enables independent replacement: e.g., swap a web-scraping loader for
   a financial data API loader, while keeping the same vector store backend.

2. PERSISTENCE AND RESUME SUPPORT
   ──────────────────────────────────
   BaseKnowledgeStore defines persist_dir — a directory where the index is saved
   after build(). On resume, load() reloads from disk, skipping re-indexing.
   BaseKnowledgeLoader defines docs_save_dir — a cache directory where fetched
   documents are stored as .txt files. On resume, cached files are reused
   without making new network calls.

3. SOURCE PRIORITY CHAIN
   ──────────────────────────
   Document acquisition follows a deterministic priority order:
       docs_dir (local files) > url_csv (CSV-specified URLs) > LLM-suggested URLs
   If none are configured, the agent autonomously discovers relevant resources
   by asking its own LLM for URL recommendations based on its persona.

4. EXTENSIBILITY CONTRACT
   ──────────────────────────
   All custom implementations MUST inherit from BaseKnowledgeLoader or
   BaseKnowledgeStore and implement their abstract methods. This guarantees
   that any loader/store pair can be plugged into any agent that uses
   _initialize_rag() in RagLLMInvestor or similar patterns.

5. DATACLASS-FIRST TYPING
   ──────────────────────────
   All data passed between the two layers uses typed dataclasses, not raw dicts.
   This makes knowledge pipeline logic self-documenting and IDE-friendly.

================================================================================
                        ARCHITECTURE DIAGRAM
================================================================================

    ┌───────────────────────────────────────────────────────────────────────┐
    │                          Agent (RagLLMInvestor)                       │
    │                                                                       │
    │  perceive() ──────────────────────────────────────────────────────┐  │
    │                                                                    │  │
    │  ┌─────────────────────────────┐    ┌────────────────────────┐    │  │
    │  │    BaseKnowledgeLoader      │    │   BaseKnowledgeStore   │    │  │
    │  │  ─────────────────────────  │    │  ──────────────────── │    │  │
    │  │  acquire() ──► [KnowledgeDocs] ──► build(docs)           │    │  │
    │  │                             │    │  persist(persist_dir)  │    │  │
    │  └─────────────────────────────┘    └────────────────────────┘    │  │
    │                                              │                     │  │
    │  decide()  ◄─────────── KnowledgeResult ◄── query(KnowledgeQuery) │  │
    │                                                                    │  │
    └────────────────────────────────────────────────────────────────────┘  │
                                                                             │
                                                                        (init once)

================================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional


# =============================================================================
#                            ENUMS
# =============================================================================


class KnowledgeSourceType(Enum):
    """
    Categorizes how a KnowledgeDocument was originally acquired.

    Used in KnowledgeDocument.source_type to trace provenance and to
    inform caching/reload decisions.

    Values
    ------
    LOCAL_FILE
        Document was loaded from a local file on disk (PDF or Markdown).
        Path is available in metadata["source"].

    WEB_URL
        Document was fetched from a remote URL.
        URL is available in metadata["url"] or metadata["source"].

    WEB_URL_CSV
        Document was fetched from a URL read out of a CSV file
        (the url_csv source in the RAG config).

    LLM_SUGGESTED
        URL was autonomously suggested by the agent's LLM based on
        its persona, then fetched. This is the default when no
        docs_dir or url_csv is configured.

    CACHED
        Document was loaded from a previously-saved local cache file
        (resume support). Original source type may be any of the above.

    PLACEHOLDER
        Synthetic placeholder document inserted when no real documents
        could be acquired, to prevent the index from being empty.
    """

    LOCAL_FILE = auto()
    WEB_URL = auto()
    WEB_URL_CSV = auto()
    LLM_SUGGESTED = auto()
    CACHED = auto()
    PLACEHOLDER = auto()


# =============================================================================
#                          CORE DATA TYPES
# =============================================================================


@dataclass
class KnowledgeDocument:
    """
    Atomic unit of acquired knowledge — a single parsed document.

    A KnowledgeDocument wraps a text corpus (the actual content) with
    provenance metadata (where it came from, when it was acquired, what
    type of source it represents). It is the data type exchanged between
    BaseKnowledgeLoader and BaseKnowledgeStore.

    Attributes
    ----------
    text : str
        The full text content of the document. For PDFs, this is the
        concatenation of all pages. For web pages, this is the cleaned
        main body text extracted by BeautifulSoup.

    source : str
        A string identifier for the document origin. For local files,
        this is the absolute file path. For web content, this is the URL.

    source_type : KnowledgeSourceType
        Enum indicating how this document was acquired.
        Defaults to KnowledgeSourceType.WEB_URL.

    title : str
        Human-readable title for the document. For LLM-suggested URLs,
        this is the title the LLM provided. For local files, this is
        the filename. May be empty string if unknown.

    acquired_at : str
        ISO-8601 timestamp of when this document was acquired.
        Auto-set to current time at creation.

    metadata : Dict[str, Any]
        Arbitrary additional metadata. Common keys:
            - "filename"  : original filename (LOCAL_FILE only)
            - "url"       : the exact URL fetched (WEB_URL variants)
            - "cached"    : True if loaded from disk cache (CACHED only)
            - "agent_id"  : ID of the agent that requested this document

    Notes
    -----
    KnowledgeDocument is immutable by convention after creation.
    Do not modify its fields after passing it to BaseKnowledgeStore.build().

    Conversion to llama_index.core.Document is handled inside KnowledgeStore
    and is an implementation detail not exposed at this interface level.
    """

    text: str
    source: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.WEB_URL
    title: str = ""
    acquired_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate that text is non-empty."""
        if not isinstance(self.text, str):
            raise TypeError(
                f"KnowledgeDocument.text must be str, got {type(self.text).__name__}"
            )
        if not self.text.strip():
            raise ValueError(
                "KnowledgeDocument.text must not be empty or whitespace-only"
            )

    def char_count(self) -> int:
        """Return the number of characters in the document text."""
        return len(self.text)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dictionary (for logging / storage)."""
        return {
            "source": self.source,
            "source_type": self.source_type.name,
            "title": self.title,
            "acquired_at": self.acquired_at,
            "char_count": self.char_count(),
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return (
            f"KnowledgeDocument("
            f"title={self.title!r}, "
            f"source_type={self.source_type.name}, "
            f"chars={self.char_count()}"
            f")"
        )


@dataclass
class KnowledgeQuery:
    """
    A retrieval request submitted by an agent at decision time.

    The agent constructs a KnowledgeQuery from the current market state and
    passes it to BaseKnowledgeStore.query(). The store uses the text field
    as the semantic search query against the embedded knowledge index.

    Attributes
    ----------
    text : str
        The natural-language search query. Typically a description of the
        current market situation, e.g.:
            "investment strategy when price=120.50, P/F ratio=1.35x,
             momentum=+2.1% this round, net_demand=+15.2"
        The store will embed this string and return the most semantically
        similar chunks from the knowledge index.

    top_k : int
        Maximum number of text chunks to retrieve. Defaults to 3.
        Corresponds to the "top_k" field in the agent's RAG config.

    round_num : Optional[int]
        The simulation round number at which this query was issued.
        Used for logging and debugging only — does not affect retrieval.

    agent_id : Optional[str]
        The identity of the agent issuing the query.
        Used for logging and debugging only.

    context : Dict[str, Any]
        Optional structured market data to accompany the text query.
        Implementations MAY use this for metadata filtering (e.g., only
        retrieve documents tagged with a specific theme). Default behavior
        ignores context and uses text only.

    Notes
    -----
    KnowledgeQuery is a value object — it carries no mutable state and
    is discarded after use. Create a new instance each round.
    """

    text: str
    top_k: int = 3
    round_num: Optional[int] = None
    agent_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate query parameters."""
        if not self.text.strip():
            raise ValueError("KnowledgeQuery.text must not be empty")
        if self.top_k < 1:
            raise ValueError(f"KnowledgeQuery.top_k must be >= 1, got {self.top_k}")

    def __repr__(self) -> str:
        return (
            f"KnowledgeQuery("
            f"text={self.text[:60]!r}…, "
            f"top_k={self.top_k}, "
            f"round={self.round_num}"
            f")"
        )


@dataclass
class KnowledgeResult:
    """
        Retrieved knowledge chunks returned by BaseKnowledgeStore.query().

        Wraps the ranked list of text chunks most relevant to a KnowledgeQuery,
        plus metadata about the retrieval. The agent injects the formatted_text
        property directly into its LLM prompt.

        Attributes
        ----------
        chunks : List[str]
            Ordered list of retrieved text chunks (most relevant first).
            Each chunk is a sub-section of a KnowledgeDocument, produced by
            the text splitter configured in BaseKnowledgeStore.

        query : KnowledgeQuery
            The original query that produced these results. Retained for
            logging, debugging, and potential re-ranking.

        retrieved_at : str
            ISO-8601 timestamp of when the retrieval was performed.

        is_empty : bool
            True if no relevant chunks were found, or if the store was not
            built. When True, formatted_text returns a fallback message.

        Notes
        -----
        Use the formatted_text property to obtain the prompt-ready string.
        Do not concatenate chunks manually — formatted_text applies the
        standard separator (

    ---

    ) used across all agents.
    """

    chunks: List[str]
    query: KnowledgeQuery
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def is_empty(self) -> bool:
        """Return True if no chunks were retrieved."""
        return len(self.chunks) == 0

    @property
    def formatted_text(self) -> str:
        """
                Return a single prompt-ready string from all retrieved chunks.

                Chunks are joined by the standard separator ``

        ---

        ``.
                If no chunks were retrieved, returns a polite fallback message
                so the LLM prompt still contains a well-formed section.

                Returns
                -------
                str
                    Multi-chunk string for injection into the LLM user prompt.

                Example
                -------
                If chunks = ["Momentum investing involves...", "Trend-following..."]:

                    "Momentum investing involves...

                    ---

                    Trend-following..."
        """
        if self.is_empty:
            return "(No relevant knowledge retrieved for this decision.)"
        return "\n\n---\n\n".join(self.chunks)

    def __len__(self) -> int:
        """Return the number of retrieved chunks."""
        return len(self.chunks)

    def __repr__(self) -> str:
        return (
            f"KnowledgeResult("
            f"chunks={len(self.chunks)}, "
            f"query={self.query.text[:40]!r}…"
            f")"
        )


# =============================================================================
#                   ABSTRACT BASE CLASSES
# =============================================================================


class BaseKnowledgeLoader(ABC):
    """
    Abstract base class for all knowledge acquisition implementations.

    A BaseKnowledgeLoader is responsible for locating and parsing documents
    relevant to a specific agent persona. It defines the contract for all
    loaders — regardless of their source (local files, web pages, databases,
    financial APIs, etc.).

    ───────────────────────────────────────────────────────────────────────────
    RESPONSIBILITY BOUNDARY
    ───────────────────────────────────────────────────────────────────────────
    BaseKnowledgeLoader:
        ✓  Acquires raw documents and returns KnowledgeDocument objects
        ✓  Handles source-specific parsing (PDF text extraction, HTML cleaning)
        ✓  Implements caching/deduplication of fetched content
        ✗  Does NOT build vector indexes (that is BaseKnowledgeStore's job)
        ✗  Does NOT perform semantic search or ranking

    ───────────────────────────────────────────────────────────────────────────
    SOURCE PRIORITY CHAIN (implemented in concrete KnowledgeLoader)
    ───────────────────────────────────────────────────────────────────────────
    When acquire() is called, sources are tried in this order:

        1. LOCAL DIRECTORY (docs_dir)
           Load all PDF and .md files found recursively under the folder.
           Highest priority — deterministic, no network required.

        2. URL CSV (url_csv)
           Read URLs from a CSV file with a "url" column and fetch them.

        3. EXPLICIT URLS (urls)
           Fetch a caller-provided list of URLs.

        4. LLM-DIRECTED WEB SEARCH (default)
           The agent's LLM generates targeted search queries based on its
           persona (NOT hallucinated URLs). A web search tool (DuckDuckGo)
           executes each query and returns real, verified URLs. Content is
           then fetched from those URLs and cached to docs_save_dir.
           This is the tool-use pattern: LLM → search queries → search
           engine → real URLs → fetch → KnowledgeDocument list.

    ───────────────────────────────────────────────────────────────────────────
    CACHING STRATEGY
    ───────────────────────────────────────────────────────────────────────────
    Fetched web content is saved to docs_save_dir as .txt files. On the next
    call with the same save_dir, cached files are reloaded without network
    access. This supports the simulation resume mechanism.

    ───────────────────────────────────────────────────────────────────────────
    SUBCLASSING GUIDE
    ───────────────────────────────────────────────────────────────────────────
    To create a custom loader (e.g. pulling from a Bloomberg terminal or a
    financial database), subclass BaseKnowledgeLoader and implement:

        def load_from_dir(self, folder: str) -> List[KnowledgeDocument]:
            # Return documents loaded from local files

        def load_from_urls(self, urls: List[str]) -> List[KnowledgeDocument]:
            # Return documents fetched from the given URLs

        def load_from_url_csv(self, csv_path: str) -> List[KnowledgeDocument]:
            # Return documents from URLs listed in a CSV file

        def suggest_and_download(self, persona_desc, llm_client, ...) -> List[KnowledgeDocument]:
            # Ask LLM to suggest URLs, fetch, and cache them

    All four methods must return List[KnowledgeDocument].
    """

    # ------------------------------------------------------------------
    # Abstract interface (must implement in subclass)
    # ------------------------------------------------------------------

    @abstractmethod
    def load_from_dir(self, folder: str) -> List[KnowledgeDocument]:
        """
        Load all supported documents recursively from a local directory.

        Supported formats (at minimum): PDF (.pdf), Markdown (.md).
        Implementations may additionally support .txt, .html, .docx, etc.

        Parameters
        ----------
        folder : str
            Absolute or relative path to the root directory. The loader
            should walk subdirectories recursively.

        Returns
        -------
        List[KnowledgeDocument]
            One KnowledgeDocument per successfully parsed file, with
            source_type=KnowledgeSourceType.LOCAL_FILE.
            Returns an empty list if the folder does not exist.

        Notes
        -----
        Failures on individual files should be logged and skipped —
        do not raise an exception for a single bad file.
        """
        raise NotImplementedError

    @abstractmethod
    def load_from_urls(self, urls: List[str]) -> List[KnowledgeDocument]:
        """
        Fetch and parse a list of web-page URLs.

        Parameters
        ----------
        urls : List[str]
            List of HTTP/HTTPS URL strings to download. Empty strings
            and malformed URLs should be silently skipped.

        Returns
        -------
        List[KnowledgeDocument]
            One KnowledgeDocument per successfully fetched URL, with
            source_type=KnowledgeSourceType.WEB_URL.
            Returns an empty list if all fetches fail.

        Notes
        -----
        Implementations should include a polite inter-request delay
        (e.g. 0.3–0.5 s) to avoid rate-limiting. Failures on individual
        URLs should be logged and skipped.
        """
        raise NotImplementedError

    @abstractmethod
    def load_from_url_csv(self, csv_path: str) -> List[KnowledgeDocument]:
        """
        Read URLs from a CSV file (column named "url") and fetch them.

        The CSV must contain at least one column named "url" or "URL".
        Rows with empty URL fields are silently skipped.

        Parameters
        ----------
        csv_path : str
            Path to the CSV file.

        Returns
        -------
        List[KnowledgeDocument]
            One KnowledgeDocument per successfully fetched URL, with
            source_type=KnowledgeSourceType.WEB_URL_CSV.
            Returns an empty list if the file cannot be read.
        """
        raise NotImplementedError

    @abstractmethod
    def suggest_and_download(
        self,
        persona_desc: str,
        llm_client: Any,
        n_urls: int = 5,
        save_dir: Optional[str] = None,
    ) -> List[KnowledgeDocument]:
        """
        Ask the LLM to suggest relevant URLs, then fetch and cache them.

        This is the autonomous knowledge discovery path. It is used when
        no docs_dir or url_csv is configured — i.e., the agent chooses
        its own reference materials based on its persona.

        If save_dir already contains cached .txt files from a previous run,
        those are returned directly (no new network calls). This supports
        the simulation resume mechanism without re-fetching.

        Parameters
        ----------
        persona_desc : str
            A description of the agent's persona, investment style, and
            financial theory. Used as the LLM prompt seed. Typically the
            first 300 characters of the system prompt.

        llm_client : Any
            An LLM client object with a .run([InferInput]) method that
            returns an object with a .response str attribute. In practice,
            a LangChainAPIInference instance.

        n_urls : int
            Number of URLs to ask the LLM to suggest. Default 5.

        save_dir : Optional[str]
            Directory to cache downloaded documents as .txt files.
            If None, documents are returned but not cached.
            If provided and already populated, cached files are reloaded.

        Returns
        -------
        List[KnowledgeDocument]
            One KnowledgeDocument per successfully fetched URL, with
            source_type=KnowledgeSourceType.LLM_SUGGESTED (or CACHED
            if loaded from disk cache).
            Returns an empty list if the LLM call or all fetches fail.
        """
        raise NotImplementedError


class BaseKnowledgeStore(ABC):
    """
    Abstract base class for all knowledge indexing and retrieval implementations.

    A BaseKnowledgeStore accepts a list of KnowledgeDocument objects, builds
    a searchable index over them, and responds to KnowledgeQuery requests
    with KnowledgeResult objects containing the most relevant text chunks.

    ───────────────────────────────────────────────────────────────────────────
    RESPONSIBILITY BOUNDARY
    ───────────────────────────────────────────────────────────────────────────
    BaseKnowledgeStore:
        ✓  Indexes KnowledgeDocument content (chunking + embedding)
        ✓  Persists the index to disk and reloads it on resume
        ✓  Responds to KnowledgeQuery with semantically relevant chunks
        ✗  Does NOT fetch or parse documents (that is BaseKnowledgeLoader's job)
        ✗  Does NOT call the LLM for synthesis — returns raw text chunks only

    ───────────────────────────────────────────────────────────────────────────
    INDEXING PIPELINE
    ───────────────────────────────────────────────────────────────────────────

        KnowledgeDocument list
              │
              ▼
        text chunking  ──►  SentenceSplitter(chunk_size=512, chunk_overlap=64)
              │
              ▼
        embedding      ──►  OpenAI-compatible API (e.g., ARK doubao-embedding)
              │
              ▼
        vector index   ──►  LlamaIndex VectorStoreIndex
              │
              ▼
        persist        ──►  persist_dir / (JSON files on disk)

    ───────────────────────────────────────────────────────────────────────────
    RETRIEVAL PIPELINE
    ───────────────────────────────────────────────────────────────────────────

        KnowledgeQuery.text
              │
              ▼
        embed query    ──►  same embedding model as indexing
              │
              ▼
        similarity     ──►  cosine similarity over VectorStoreIndex
              │
              ▼
        top-k nodes    ──►  KnowledgeResult.chunks (ordered by relevance)

    ───────────────────────────────────────────────────────────────────────────
    RESUME SUPPORT
    ───────────────────────────────────────────────────────────────────────────
    On first run:
        build(docs)  →  builds and persists the index to persist_dir.
    On resume:
        load()  →  reloads from persist_dir, skipping re-embedding.

    Callers (e.g. RagLLMInvestor._initialize_rag) should check
    os.path.isdir(persist_dir) before deciding to build vs. load.

    ───────────────────────────────────────────────────────────────────────────
    SUBCLASSING GUIDE
    ───────────────────────────────────────────────────────────────────────────
    To implement a custom store (e.g. using ChromaDB, FAISS standalone,
    Pinecone, etc.), subclass BaseKnowledgeStore and implement:

        def build(self, documents: List[KnowledgeDocument]) -> None:
            # Chunk documents, embed, build index, persist to persist_dir

        def load(self, persist_dir: Optional[str] = None) -> None:
            # Reload a previously-persisted index from disk

        def query(self, query: KnowledgeQuery) -> KnowledgeResult:
            # Embed the query, retrieve top-k chunks, return KnowledgeResult

        def is_built(self) -> bool:
            # Return True if the index has been built or loaded

    The embed_model_name, embed_api_key, embed_api_base, embed_type, and persist_dir
    constructor parameters are the standard interface — new subclasses
    should accept the same kwargs for config-driven instantiation.
    """

    def __init__(
        self,
        embed_model_name: str,
        embed_api_key: str,
        embed_api_base: str,
        embed_type: Optional[str] = None,
        persist_dir: Optional[str] = None,
    ) -> None:
        """
        Initialize the knowledge store with embedding and persistence config.

        Parameters
        ----------
        embed_model_name : str
            Embedding model identifier. For HuggingFace embeddings, use
            sentence-transformers model names (e.g., ``"BAAI/bge-small-en-v1.5"``).
            For OpenAI-compatible APIs, use the endpoint ID.

        embed_api_key : str
            API key for OpenAI-compatible embedding endpoint. Ignored for
            HuggingFace embeddings.

        embed_api_base : str
            Base URL for OpenAI-compatible embedding service. Ignored for
            HuggingFace embeddings.

        embed_type : Optional[str]
            "huggingface" for local embeddings (no API key required) or
            "openai_compatible" for API-based embeddings. If None, auto-detects
            based on whether embed_api_key is provided.

        persist_dir : Optional[str]
            Directory path for persisting and reloading the index.
            If None, the index is kept in memory only and will not
            survive process restarts.
        """
        self.embed_model_name = embed_model_name
        self.embed_api_key = embed_api_key
        self.embed_api_base = embed_api_base
        self.embed_type = embed_type
        self.persist_dir = persist_dir

    # ------------------------------------------------------------------
    # Abstract interface (must implement in subclass)
    # ------------------------------------------------------------------

    @abstractmethod
    def build(self, documents: List[KnowledgeDocument]) -> None:
        """
        Build the knowledge index from a list of KnowledgeDocument objects.

        This method should:
          1. Convert KnowledgeDocument.text into indexable units (chunks)
          2. Embed each chunk using the configured embedding model
          3. Store the resulting vectors in a searchable index structure
          4. Persist the index to persist_dir (if configured)

        If documents is empty, the implementation should insert a single
        placeholder document so the index is valid and queries don't crash.

        Parameters
        ----------
        documents : List[KnowledgeDocument]
            Documents acquired by a BaseKnowledgeLoader. May be empty
            if all acquisition attempts failed.

        Notes
        -----
        After build() returns, is_built() must return True.
        build() should NOT be called if the index was already loaded via
        load() — check is_built() before calling.
        """
        raise NotImplementedError

    @abstractmethod
    def load(self, persist_dir: Optional[str] = None) -> None:
        """
        Load a previously persisted index from disk.

        Parameters
        ----------
        persist_dir : Optional[str]
            Directory to load from. If None, falls back to the
            persist_dir provided at construction time.

        Raises
        ------
        FileNotFoundError
            If the directory does not exist or does not contain a
            valid persisted index.

        Notes
        -----
        After load() returns, is_built() must return True.
        """
        raise NotImplementedError

    @abstractmethod
    def query(self, query: KnowledgeQuery) -> KnowledgeResult:
        """
        Retrieve the most relevant knowledge chunks for a given query.

        This is called by the agent once per decision round. The query
        describes the current market situation; the store returns the
        most semantically similar chunks from its index.

        Parameters
        ----------
        query : KnowledgeQuery
            Contains the search text, top_k count, and optional context.

        Returns
        -------
        KnowledgeResult
            Retrieved chunks in relevance order. If the store is not
            built or retrieval fails, returns a KnowledgeResult with
            an empty chunks list (is_empty=True).

        Notes
        -----
        This method must never raise an exception — it should return
        a KnowledgeResult(chunks=[], ...) on any internal error.
        Callers rely on KnowledgeResult.formatted_text for a
        fallback message when is_empty=True.
        """
        raise NotImplementedError

    @abstractmethod
    def is_built(self) -> bool:
        """
        Return True if the index has been successfully built or loaded.

        Returns
        -------
        bool
            True after a successful build() or load() call.
            False before any index has been established.
        """
        raise NotImplementedError
