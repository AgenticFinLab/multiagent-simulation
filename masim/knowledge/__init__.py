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
                       embedding (Hunyuan via LiteLLM by default)

Three typed data classes carry data between the layers:

    KnowledgeDocument — one parsed document (text + provenance metadata)
    KnowledgeQuery    — a retrieval request (query text + top_k)
    KnowledgeResult   — retrieved chunks + formatted_text property

Two management classes coordinate shared and per-agent resources:

    ResourceManager   — config-driven resource management (reads players.yml)
                        Resolves global_uri, resource_csv, private_knowledge
    KnowledgeManager  — centralized document processing and shared RAG index

Config-driven workflow (recommended):
    1. ResourceManager(knowledge_config) — reads knowledge: section from players.yml
    2. resource_manager.prepare_shared_resources() — pre-process all PDFs
    3. KnowledgeManager.from_config(knowledge_config) — build shared RAG index
    4. resource_manager.resolve_agent_knowledge(agent_id, private_knowledge)
       — merge global defaults + per-agent overrides for each agent

Fail-Fast Behavior
------------------
By default, both KnowledgeLoader and KnowledgeStore operate in fail-fast mode.
Any error (missing file, failed URL fetch, embedding failure) will raise a
RuntimeError with a detailed message. This ensures users are immediately
aware of configuration or environment issues.

To enable graceful degradation (useful for optional documents):

    loader = KnowledgeLoader(fail_fast=False)

Logging
-------
All operations log detailed information with the [KNOWLEDGE_LOADER] and
[KNOWLEDGE_STORE] prefixes. Each log entry shows exactly which file, URL,
or resource was accessed and whether the operation succeeded or failed.

Agent-autonomous document selection
-----------------------------------
Agents can autonomously select appropriate documents based on their identity:

    from masim.knowledge import KnowledgeLoader, resolve_agent_type

    # Determine agent_type from identity
    agent_type = resolve_agent_type("ragllm_momentum_1")  # → "momentum_speculator"

    # Load documents appropriate for this agent type
    loader = KnowledgeLoader()  # fail_fast=True by default
    docs = loader.load_for_agent("ragllm_momentum_1", save_dir="path/to/cache")

Typical usage in a player perceive() initializer
------------------------------------------------

    from masim.knowledge import (
        KnowledgeLoader, KnowledgeStore, ResourceManager,
        KnowledgeQuery, KnowledgeResult,
    )
    from masim.knowledge.manager import KnowledgeManager

    # ResourceManager resolves config from players.yml
    resource_manager = ResourceManager(knowledge_config)
    resolved = resource_manager.resolve_agent_knowledge(
        agent_id="ragllm_momentum_1",
        private_knowledge=private_knowledge_config,
        record_path="EXPERIMENT/AssetBubble/Rag/records",
    )

    # Build or load RAG store using resolved config
    rag = resolved["rag"]
    store = KnowledgeStore(
        embed_model_name=rag["embed_model"],
        embed_api_key=rag["embed_api_key"],
        embed_api_base=rag["embed_api_base"],
        embed_type=rag["embed_type"],
        persist_dir=resolved["local_rag_dir"],
    )

    # Each decision round:
    q = KnowledgeQuery(text="momentum strategy at price=120, bubble_ratio=1.3x",
                       top_k=3, round_num=42)
    result = store.query(q)
    rag_context = result.formatted_text   # inject into LLM prompt
"""

from .loader import KnowledgeLoader, resolve_agent_type, DEFAULT_CATALOG_PATH
from .store import KnowledgeStore
from .manager import KnowledgeManager
from .resource_manager import ResourceManager, create_backend
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
    "KnowledgeManager",
    "ResourceManager",
    "create_backend",
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
