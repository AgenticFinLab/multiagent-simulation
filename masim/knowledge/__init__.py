"""masim.knowledge — Agent knowledge acquisition and retrieval

Provides the complete knowledge infrastructure for agents that need to
ground their decisions in domain-specific professional information.

All professional, financial, or domain-specific information needed by agents
should be acquired and retrieved through this module.

Architecture
------------
Two abstract base classes define the contracts (in base.py):

    BaseKnowledgeLoader  — acquire documents from any source
    BaseKnowledgeStore   — index documents and answer queries

Two concrete implementations are provided:

    KnowledgeLoader  — PDF/Markdown files, URL-CSV, explicit URLs,
                       or LLM-suggested autonomous discovery
    KnowledgeStore   — LlamaIndex VectorStoreIndex with OpenAI-compatible
                       embedding (ARK ByteDance by default)

Three typed data classes carry data between the layers:

    KnowledgeDocument — one parsed document (text + provenance metadata)
    KnowledgeQuery    — a retrieval request (query text + top_k)
    KnowledgeResult   — retrieved chunks + formatted_text property

Agent-autonomous document selection
-----------------------------------
Agents can autonomously select appropriate documents based on their identity:

    from masim.knowledge import KnowledgeLoader, resolve_agent_type

    # Determine agent_type from identity
    agent_type = resolve_agent_type("ragllm_momentum_1")  # → "momentum_speculator"

    # Load documents appropriate for this agent type
    loader = KnowledgeLoader()
    docs = loader.load_for_agent("ragllm_momentum_1", save_dir="path/to/cache")

Typical usage in a player perceive() initializer
------------------------------------------------

    from masim.knowledge import (
        KnowledgeLoader, KnowledgeStore,
        KnowledgeQuery, KnowledgeResult,
    )

    loader = KnowledgeLoader()
    docs   = loader.suggest_and_download(persona_desc, llm_client,
                                          save_dir="path/to/cache")
    store  = KnowledgeStore(
        embed_model_name="doubao-embedding-text-24071",
        embed_api_key=os.getenv("ARK_API_KEY"),
        embed_api_base="https://ark.cn-beijing.volces.com/api/v3",
        persist_dir="path/to/index",
    )
    store.build(docs)

    # Each decision round:
    q = KnowledgeQuery(text="momentum strategy at price=120, bubble_ratio=1.3x",
                       top_k=3, round_num=42)
    result = store.query(q)
    rag_context = result.formatted_text   # inject into LLM prompt
"""

from .loader import KnowledgeLoader, resolve_agent_type, DEFAULT_CATALOG_PATH
from .store import KnowledgeStore
from .base import (
    BaseKnowledgeLoader,
    BaseKnowledgeStore,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeResult,
    KnowledgeSourceType,
)

__all__ = [
    # Concrete implementations
    "KnowledgeLoader",
    "KnowledgeStore",
    # Agent-autonomous document selection
    "resolve_agent_type",
    "DEFAULT_CATALOG_PATH",
    # Abstract base classes (for custom implementations)
    "BaseKnowledgeLoader",
    "BaseKnowledgeStore",
    # Data types
    "KnowledgeDocument",
    "KnowledgeQuery",
    "KnowledgeResult",
    "KnowledgeSourceType",
]
