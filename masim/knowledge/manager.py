"""masim.knowledge.manager — Centralized knowledge management for simulations

KnowledgeManager provides centralized document processing and caching for
multi-agent simulations. It ensures that:

1. Documents are processed only once, regardless of how many agents need them
2. PDF processing happens during simulation initialization, not during agent operation
3. All agents share the same processed documents and RAG indexes
4. No duplicate API calls to MinerU or other external services

Can be initialized from a knowledge_config dict (from players.yml ``knowledge:``
section) or from explicit path arguments for backward compatibility.

Usage:
    from masim.knowledge.manager import KnowledgeManager

    # New: Initialize from config dict (recommended)
    manager = KnowledgeManager.from_config(knowledge_config)

    # Legacy: Initialize with explicit paths
    manager = KnowledgeManager(docs_dir="examples/document-sources")

    # Process all documents once during simulation setup
    manager.prepare_all_documents()

    # Build shared RAG index
    manager.build_shared_rag_index()

    # Agents can then load pre-processed documents
    docs = manager.get_processed_documents(agent_id)

Architecture:
    Simulation Setup Phase:
        1. Collect all document requirements from all agents
        2. Identify unique PDFs that need processing
        3. Process each PDF once with MinerU
        4. Build shared RAG indexes

    Simulation Run Phase:
        1. Agents load pre-processed documents from shared cache
        2. No duplicate processing or API calls
        3. Each agent gets its own RAG index copy (if needed)
"""

from __future__ import annotations

import logging
import os
import shutil
from typing import Any, Dict, List, Optional, Set

from masim.knowledge.loader import KnowledgeLoader, _parse_pdf
from masim.knowledge.store import KnowledgeStore

logger = logging.getLogger("masim.knowledge.manager")


class KnowledgeManager:
    """Centralized knowledge management for multi-agent simulations.

    Ensures documents are processed only once during simulation initialization,
    preventing duplicate API calls and resource contention among agents.

    Can be constructed via:
    - ``KnowledgeManager(docs_dir=...)``  — legacy explicit paths
    - ``KnowledgeManager.from_config(knowledge_config)`` — config-driven (recommended)

    Parameters
    ----------
    docs_dir : str
        Root directory for all documents (shared storage).
    source_subdir : str
        Subdirectory for original source documents (default: "source").
    processed_subdir : str
        Subdirectory for MinerU processed output (default: "MinerU_processed").
    rag_index_subdir : str
        Subdirectory for shared RAG indexes (default: "rag_index").
    """

    def __init__(
        self,
        docs_dir: str,
        source_subdir: str = "source",
        processed_subdir: str = "MinerU_processed",
        rag_index_subdir: str = "rag_index",
    ) -> None:
        self.docs_dir = docs_dir
        self.source_dir = os.path.join(docs_dir, source_subdir)
        self.processed_dir = os.path.join(docs_dir, processed_subdir)
        self.rag_index_dir = os.path.join(docs_dir, rag_index_subdir)

        # Store global RAG config for building shared index
        self._global_rag_config: Dict[str, Any] = {}

        # Ensure directories exist
        os.makedirs(self.source_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.rag_index_dir, exist_ok=True)

        # Track document requirements per agent
        self._agent_requirements: Dict[str, Dict[str, Any]] = {}

        # Track unique PDFs that need processing
        self._unique_pdfs: Set[str] = set()

        # Track processed PDFs (path -> success)
        self._processed_pdfs: Dict[str, bool] = {}

        logger.info(
            "[KNOWLEDGE_MANAGER] Initialized with docs_dir=%s, "
            "source=%s, processed=%s, rag_index=%s",
            docs_dir,
            self.source_dir,
            self.processed_dir,
            self.rag_index_dir,
        )

    @classmethod
    def from_config(cls, knowledge_config: Dict[str, Any]) -> "KnowledgeManager":
        """Create a KnowledgeManager from a ``knowledge:`` config dict.

        Reads ``global_uri``, ``preprocessing.output_position``, and
        ``rag.output_position`` from the config to derive all paths.
        Also stores the global RAG config for later use in
        ``build_shared_rag_index()``.

        Parameters
        ----------
        knowledge_config : dict
            The ``knowledge:`` section from players.yml.

        Returns
        -------
        KnowledgeManager
            A new instance configured from the YAML config.
        """
        global_uri = knowledge_config.get(
            "global_uri", knowledge_config.get("uri", "examples/document-sources")
        )
        preproc = knowledge_config.get("preprocessing", {})
        processed_subdir = preproc.get("output_position", "MinerU_processed")
        rag_config = knowledge_config.get("rag", {})
        rag_index_subdir = rag_config.get("output_position", "rag_index")

        mgr = cls(
            docs_dir=global_uri,
            source_subdir="source",
            processed_subdir=processed_subdir,
            rag_index_subdir=rag_index_subdir,
        )
        mgr._global_rag_config = rag_config
        return mgr

    def register_agent_requirements(
        self,
        agent_id: str,
        rag_config: Dict[str, Any],
    ) -> None:
        """Register document requirements for an agent.

        This collects all document sources (PDFs, URLs, etc.) that an agent
        needs for its RAG system. The actual processing happens later in
        prepare_all_documents().

        Parameters
        ----------
        agent_id : str
            Unique identifier for the agent.
        rag_config : dict
            RAG configuration from the agent's config (rag section).
        """
        self._agent_requirements[agent_id] = rag_config.copy()

        # Collect unique PDFs from url_csv
        url_csv = rag_config.get("url_csv")
        if url_csv and os.path.isfile(url_csv):
            self._collect_pdfs_from_csv(url_csv)

        # Collect PDFs from source directory
        if os.path.isdir(self.source_dir):
            for fname in os.listdir(self.source_dir):
                if fname.lower().endswith(".pdf"):
                    pdf_path = os.path.join(self.source_dir, fname)
                    self._unique_pdfs.add(pdf_path)

        logger.info(
            "[KNOWLEDGE_MANAGER] Registered requirements for %s, "
            "total unique PDFs: %d",
            agent_id,
            len(self._unique_pdfs),
        )

    def _collect_pdfs_from_csv(self, csv_path: str) -> None:
        """Collect PDF file paths from a CSV file."""
        import csv

        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    source_type = (
                        (row.get("source_type") or row.get("source") or "web")
                        .lower()
                        .strip()
                    )
                    url = row.get("url") or row.get("URL") or ""
                    url = url.strip()

                    if source_type == "file" and url.lower().endswith(".pdf"):
                        # Handle both absolute and relative paths
                        if os.path.isabs(url):
                            pdf_path = url
                        else:
                            pdf_path = os.path.join(self.docs_dir, url)

                        if os.path.exists(pdf_path):
                            self._unique_pdfs.add(pdf_path)
                        else:
                            logger.warning(
                                "[KNOWLEDGE_MANAGER] PDF from CSV not found: %s",
                                pdf_path,
                            )
        except Exception as exc:
            logger.error(
                "[KNOWLEDGE_MANAGER] Failed to read CSV %s: %s",
                csv_path,
                exc,
            )

    def prepare_all_documents(
        self,
        fail_fast: bool = False,
        skip_existing: bool = True,
    ) -> Dict[str, bool]:
        """Process all unique documents once during simulation setup.

        This is the main method that should be called during simulation
        initialization. It ensures each PDF is processed only once,
        regardless of how many agents need it.

        Parameters
        ----------
        fail_fast : bool
            If True, raise exception on processing failure.
            If False, log warning and continue with other PDFs.
        skip_existing : bool
            If True, skip PDFs that have already been processed.
            If False, re-process all PDFs.

        Returns
        -------
        Dict[str, bool]
            Mapping of PDF path to processing success status.
        """
        logger.info(
            "[KNOWLEDGE_MANAGER] Preparing %d unique PDFs...",
            len(self._unique_pdfs),
        )

        loader = KnowledgeLoader(fail_fast=fail_fast)

        for pdf_path in sorted(self._unique_pdfs):
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]

            # Check if already processed
            if skip_existing:
                cached_md = os.path.join(self.processed_dir, pdf_name, f"{pdf_name}.md")
                if os.path.isfile(cached_md):
                    logger.info(
                        "[KNOWLEDGE_MANAGER] PDF already processed: %s",
                        pdf_path,
                    )
                    self._processed_pdfs[pdf_path] = True
                    continue

            # Process PDF with MinerU
            logger.info(
                "[KNOWLEDGE_MANAGER] Processing PDF: %s",
                pdf_path,
            )
            try:
                text = _parse_pdf(
                    pdf_path,
                    fail_fast=fail_fast,
                    processed_dir=self.processed_dir,
                )
                self._processed_pdfs[pdf_path] = text is not None

                if text:
                    logger.info(
                        "[KNOWLEDGE_MANAGER] Successfully processed %s (%d chars)",
                        pdf_path,
                        len(text),
                    )
                else:
                    logger.warning(
                        "[KNOWLEDGE_MANAGER] Failed to process %s",
                        pdf_path,
                    )

            except Exception as exc:
                self._processed_pdfs[pdf_path] = False
                logger.error(
                    "[KNOWLEDGE_MANAGER] Error processing %s: %s",
                    pdf_path,
                    exc,
                )
                if fail_fast:
                    raise

        # Summary
        success_count = sum(1 for v in self._processed_pdfs.values() if v)
        logger.info(
            "[KNOWLEDGE_MANAGER] Document preparation complete: "
            "%d/%d PDFs processed successfully",
            success_count,
            len(self._unique_pdfs),
        )

        return self._processed_pdfs.copy()

    def get_processed_documents(
        self,
        agent_id: str,
    ) -> List[Any]:
        """Get processed documents for a specific agent.

        This should be called by agents during their initialization
        to load pre-processed documents.

        Parameters
        ----------
        agent_id : str
            The agent's unique identifier.

        Returns
        -------
        List[KnowledgeDocument]
            List of processed documents for the agent.
        """
        if agent_id not in self._agent_requirements:
            logger.warning(
                "[KNOWLEDGE_MANAGER] No requirements registered for %s",
                agent_id,
            )
            return []

        # Load from processed directory
        loader = KnowledgeLoader()
        docs = loader.load_from_dir(self.processed_dir)

        logger.info(
            "[KNOWLEDGE_MANAGER] Loaded %d processed documents for %s",
            len(docs),
            agent_id,
        )

        return docs

    def build_shared_rag_index(
        self,
        embed_type: Optional[str] = None,
        embed_model: Optional[str] = None,
        embed_api_key: Optional[str] = None,
        embed_api_base: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Optional[KnowledgeStore]:
        """Build a shared RAG index from all processed documents.

        This creates a single RAG index that can be shared among all agents,
        avoiding duplicate index building.

        Config values are resolved in this priority order:
        1. Explicit arguments passed to this method
        2. Values from ``knowledge.rag`` in the YAML config (stored at init)
        3. Built-in defaults

        Template variables like ``{{ HUNYUAN_API_KEY }}`` in embed_api_key
        are resolved automatically from environment variables.

        Parameters
        ----------
        embed_type : str, optional
            Embedding type (e.g., "litellm", "huggingface").
        embed_model : str, optional
            Embedding model name.
        embed_api_key : str, optional
            API key for embedding service.
        embed_api_base : str, optional
            API base URL for embedding service.
        chunk_size : int, optional
            Chunk size for document splitting.
        chunk_overlap : int, optional
            Chunk overlap for document splitting.

        Returns
        -------
        KnowledgeStore or None
            The built knowledge store, or None if no documents available.
        """
        # Resolve config: explicit args > global_rag_config > defaults
        from masim.knowledge.resource_manager import ResourceManager

        def _resolve(key: str, default: Any, explicit: Any = None) -> Any:
            if explicit is not None:
                return explicit
            if key in self._global_rag_config:
                val = self._global_rag_config[key]
                # Resolve template variables for api_key
                if key == "embed_api_key":
                    return ResourceManager.resolve_template_var(val)
                return val
            return default

        _embed_type = _resolve("embed_type", "litellm", embed_type)
        _embed_model = _resolve("embed_model", "openai/hunyuan-embedding", embed_model)
        _embed_api_key = _resolve("embed_api_key", "", embed_api_key)
        _embed_api_base = _resolve("embed_api_base", "", embed_api_base)
        _chunk_size = int(_resolve("chunk_size", 512, chunk_size))
        _chunk_overlap = int(_resolve("chunk_overlap", 64, chunk_overlap))

        # Check if index already exists
        if os.path.isdir(self.rag_index_dir) and os.listdir(self.rag_index_dir):
            logger.info(
                "[KNOWLEDGE_MANAGER] Loading existing shared RAG index from %s",
                self.rag_index_dir,
            )
            store = KnowledgeStore(
                embed_type=_embed_type,
                embed_model_name=_embed_model,
                embed_api_key=_embed_api_key,
                embed_api_base=_embed_api_base,
                persist_dir=self.rag_index_dir,
            )
            store.load(self.rag_index_dir)
            return store

        # Load all processed documents
        loader = KnowledgeLoader()
        docs = loader.load_from_dir(self.processed_dir)

        if not docs:
            logger.warning(
                "[KNOWLEDGE_MANAGER] No documents available for RAG index",
            )
            return None

        # Build RAG index
        logger.info(
            "[KNOWLEDGE_MANAGER] Building shared RAG index from %d documents...",
            len(docs),
        )

        store = KnowledgeStore(
            embed_type=_embed_type,
            embed_model_name=_embed_model,
            embed_api_key=_embed_api_key,
            embed_api_base=_embed_api_base,
            persist_dir=self.rag_index_dir,
            chunk_size=_chunk_size,
            chunk_overlap=_chunk_overlap,
        )
        store.build(docs)

        logger.info(
            "[KNOWLEDGE_MANAGER] Shared RAG index built and saved to %s",
            self.rag_index_dir,
        )

        return store

    def copy_rag_index_to_agent(
        self,
        agent_id: str,
        agent_workspace_dir: str,
    ) -> bool:
        """Copy the shared RAG index to an agent's local workspace.

        Parameters
        ----------
        agent_id : str
            The agent's unique identifier.
        agent_workspace_dir : str
            The agent's local workspace directory.

        Returns
        -------
        bool
            True if copy successful, False otherwise.
        """
        if not os.path.isdir(self.rag_index_dir):
            logger.warning(
                "[KNOWLEDGE_MANAGER] No shared RAG index to copy for %s",
                agent_id,
            )
            return False

        local_rag_dir = os.path.join(agent_workspace_dir, "rag_index")

        try:
            # Remove existing local index if present
            if os.path.isdir(local_rag_dir):
                shutil.rmtree(local_rag_dir)

            # Copy shared index to local workspace
            shutil.copytree(self.rag_index_dir, local_rag_dir)

            logger.info(
                "[KNOWLEDGE_MANAGER] Copied RAG index to %s workspace: %s",
                agent_id,
                local_rag_dir,
            )
            return True

        except Exception as exc:
            logger.error(
                "[KNOWLEDGE_MANAGER] Failed to copy RAG index for %s: %s",
                agent_id,
                exc,
            )
            return False

    def get_processing_summary(self) -> Dict[str, Any]:
        """Get summary of document processing status.

        Returns
        -------
        dict
            Summary including total PDFs, processed count, failed count, etc.
        """
        total = len(self._unique_pdfs)
        processed = sum(1 for v in self._processed_pdfs.values() if v)
        failed = total - processed

        return {
            "total_unique_pdfs": total,
            "processed_successfully": processed,
            "failed": failed,
            "registered_agents": len(self._agent_requirements),
            "docs_dir": self.docs_dir,
            "processed_dir": self.processed_dir,
            "rag_index_dir": self.rag_index_dir,
        }
