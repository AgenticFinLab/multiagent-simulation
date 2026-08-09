"""masim.knowledge.resource_manager — Resource management for multi-agent RAG

Configuration Schema (players.yml):

knowledge:
  backend: "local"
  global_uri: "examples/document-sources"
  resource_csv:
    - "examples/document-sources/books.csv"
    - "examples/document-sources/source"
  preprocessing:
    parser: "mineru"
    timeout_per_page: 30
    max_pages: 250
    output_position: "MinerU_processed"
  rag:
    output_position: "rag_index"
    embed_type: "litellm"
    embed_model: "openai/hunyuan-embedding"
    embed_api_key: "{{ HUNYUAN_API_KEY }}"
    embed_api_base: "https://api.hunyuan.cloud.tencent.com/v1"
    chunk_size: 512
    chunk_overlap: 64

Each agent:
  private_knowledge:
    from_global_resources:
      - "MinerU_processed"
    local_resources:
      local_uri: ""
      local_resources: []
    rag:
      from_global_index_dir:
        - "rag_index"
      local_index_dir: ""
      embed_type: "litellm"
      embed_model: "openai/hunyuan-embedding"
      ...

Deployment:
  Single machine:  backend=local,  global_uri="/path/to/docs"
  Multi-server:    backend=shared, global_uri="/mnt/nfs/docs"
  Cloud:           backend=remote, global_uri="s3://bucket/prefix"

Config Resolution Flow:
  1. ResourceManager reads knowledge: section from players.yml
  2. global_uri replaces old uri field; resource_csv replaces old resources list
  3. resolve_agent_knowledge() merges global rag defaults with per-agent overrides
  4. Agents receive fully-resolved path/config dicts at initialization
"""

from __future__ import annotations

import logging
import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

logger = logging.getLogger("masim.knowledge.resource_manager")


class ResourceBackend(ABC):
    """Abstract base for resource storage backends."""

    @abstractmethod
    def exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def get_path(self, path: str) -> str:
        pass

    @abstractmethod
    def put(self, local_path: str, dest_path: str) -> bool:
        pass

    @abstractmethod
    def list_files(self, path: str, pattern: str = "*") -> List[str]:
        pass


class LocalBackend(ResourceBackend):
    """Local filesystem backend (single machine)."""

    def __init__(self, base_uri: str):
        self.base_uri = Path(base_uri)

    def exists(self, path: str) -> bool:
        return (self.base_uri / path).exists()

    def get_path(self, path: str) -> str:
        return str(self.base_uri / path)

    def put(self, local_path: str, dest_path: str) -> bool:
        dest = self.base_uri / dest_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if os.path.isdir(local_path):
            shutil.copytree(local_path, str(dest), dirs_exist_ok=True)
        else:
            shutil.copy2(local_path, str(dest))
        return True

    def list_files(self, path: str, pattern: str = "*") -> List[str]:
        p = self.base_uri / path
        if not p.exists():
            return []
        return [
            str(f.relative_to(self.base_uri)) for f in p.glob(pattern) if f.is_file()
        ]


class SharedBackend(ResourceBackend):
    """Shared filesystem backend (NFS/SMB) with local caching."""

    def __init__(self, mount_uri: str, local_cache: str = ".cache/shared"):
        self.mount_uri = Path(mount_uri)
        self.local_cache = Path(local_cache)
        self.local_cache.mkdir(parents=True, exist_ok=True)

    def exists(self, path: str) -> bool:
        return (self.mount_uri / path).exists() or (self.local_cache / path).exists()

    def get_path(self, path: str) -> str:
        cache_path = self.local_cache / path
        if cache_path.exists():
            return str(cache_path)
        shared_path = self.mount_uri / path
        if shared_path.exists():
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            if shared_path.is_dir():
                shutil.copytree(str(shared_path), str(cache_path), dirs_exist_ok=True)
            else:
                shutil.copy2(str(shared_path), str(cache_path))
            return str(cache_path)
        return str(shared_path)

    def put(self, local_path: str, dest_path: str) -> bool:
        dest = self.mount_uri / dest_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        if os.path.isdir(local_path):
            shutil.copytree(local_path, str(dest), dirs_exist_ok=True)
        else:
            shutil.copy2(local_path, str(dest))
        return True

    def list_files(self, path: str, pattern: str = "*") -> List[str]:
        p = self.mount_uri / path
        if not p.exists():
            return []
        return [
            str(f.relative_to(self.mount_uri)) for f in p.glob(pattern) if f.is_file()
        ]


class RemoteBackend(ResourceBackend):
    """Remote object storage backend (S3/OSS) with local caching."""

    def __init__(self, remote_uri: str, local_cache: str = ".cache/remote"):
        self.remote_uri = remote_uri
        self.local_cache = Path(local_cache)
        self.local_cache.mkdir(parents=True, exist_ok=True)
        parsed = urlparse(remote_uri)
        self.scheme = parsed.scheme
        self.bucket = parsed.netloc
        self.prefix = parsed.path.strip("/")

    def exists(self, path: str) -> bool:
        return (self.local_cache / path).exists()

    def get_path(self, path: str) -> str:
        cache_path = self.local_cache / path
        if cache_path.exists():
            return str(cache_path)
        logger.warning("[RemoteBackend] Resource not in cache: %s", path)
        return str(cache_path)

    def put(self, local_path: str, dest_path: str) -> bool:
        logger.info(
            "[RemoteBackend] Would upload %s to %s/%s",
            local_path,
            self.remote_uri,
            dest_path,
        )
        return False

    def list_files(self, path: str, pattern: str = "*") -> List[str]:
        p = self.local_cache / path
        if not p.exists():
            return []
        return [
            str(f.relative_to(self.local_cache)) for f in p.glob(pattern) if f.is_file()
        ]


def create_backend(backend_type: str, uri: str, **kwargs) -> ResourceBackend:
    """Create a resource backend based on type and URI."""
    if backend_type == "auto":
        if uri.startswith(("s3://", "oss://", "gs://")):
            backend_type = "remote"
        elif "://" in uri:
            backend_type = "shared"
        else:
            backend_type = "local"
    if backend_type == "local":
        return LocalBackend(uri)
    elif backend_type == "shared":
        return SharedBackend(uri, kwargs.get("local_cache", ".cache/shared"))
    elif backend_type == "remote":
        return RemoteBackend(uri, kwargs.get("local_cache", ".cache/remote"))
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


class ResourceManager:
    """Resource manager for multi-agent knowledge systems.

    Reads the ``knowledge:`` section from players.yml and provides:
    - Shared document pre-processing (PDF → Markdown via MinerU)
    - Per-agent knowledge resolution (merge global defaults + private overrides)
    - Path computation for processed dirs, RAG index dirs, and agent workspaces

    Parameters
    ----------
    knowledge_config : dict
        The ``knowledge:`` section from players.yml.  Supports both the
        new schema (``global_uri``, ``resource_csv``) and the legacy schema
        (``uri``, ``resources``) for backward compatibility.
    """

    def __init__(self, knowledge_config: Dict[str, Any]):
        self.config = knowledge_config
        backend_type = knowledge_config.get("backend", "local")
        # NEW: global_uri; LEGACY: uri
        uri = knowledge_config.get(
            "global_uri", knowledge_config.get("uri", "examples/document-sources")
        )
        self.global_uri = uri
        self.backend = create_backend(backend_type, uri)
        preproc = knowledge_config.get("preprocessing", {})
        self.parser = preproc.get("parser", "mineru")
        self.timeout_per_page = preproc.get("timeout_per_page", 30)
        self.max_pages = preproc.get("max_pages", 250)
        self.output_position = preproc.get("output_position", "MinerU_processed")
        # NEW: resource_csv list; LEGACY: resources list
        self.resource_csv = knowledge_config.get(
            "resource_csv", knowledge_config.get("resources", [])
        )
        # Global RAG defaults (shared by all agents unless overridden)
        self.global_rag = knowledge_config.get("rag", {})
        logger.info(
            "[ResourceManager] Initialized: backend=%s, global_uri=%s, "
            "preprocessing_output=%s, rag_output=%s, resource_csv=%d entries",
            type(self.backend).__name__,
            self.global_uri,
            self.output_position,
            self.global_rag.get("output_position", "rag_index"),
            len(self.resource_csv),
        )

    @property
    def uri(self) -> str:
        """Backward-compatible alias for global_uri."""
        return self.global_uri

    @property
    def processed_dir(self) -> str:
        """Full path to the MinerU processed output directory."""
        return os.path.join(self.global_uri, self.output_position)

    @property
    def shared_rag_dir(self) -> str:
        """Full path to the shared RAG index directory under global_uri."""
        rag_output = self.global_rag.get("output_position", "rag_index")
        return os.path.join(self.global_uri, rag_output)

    # ------------------------------------------------------------------
    # Template variable resolution
    # ------------------------------------------------------------------

    @staticmethod
    def resolve_template_var(value: str) -> str:
        """Resolve ``{{ ENV_VAR }}`` template variables in config values.

        If *value* matches the pattern ``{{ VAR_NAME }}``, the
        corresponding environment variable is looked up.  Otherwise the
        original string is returned unchanged.

        Parameters
        ----------
        value : str
            A config value that may contain a ``{{ ... }}`` template.

        Returns
        -------
        str
            The resolved string, or the original if no template found.
        """
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            env_name = value[2:-2].strip()
            resolved = os.getenv(env_name, "")
            if not resolved:
                logger.warning(
                    "[ResourceManager] Template {{ %s }} not found in env; "
                    "using empty string",
                    env_name,
                )
            return resolved
        return value

    # ------------------------------------------------------------------
    # RAG config merge: global defaults + per-agent overrides
    # ------------------------------------------------------------------

    def resolve_agent_rag(self, private_rag: Dict[str, Any]) -> Dict[str, Any]:
        """Merge global RAG defaults with per-agent overrides.

        The merged result replaces relative dirs with absolute paths:
        - from_global_index_dir entries → global_uri/<entry>
        - local_index_dir → <local_uri>/rag_index/ (if local_uri known)

        Parameters
        ----------
        private_rag : dict
            The agent's ``private_knowledge.rag`` section.  Values here
            take precedence over ``knowledge.rag`` defaults.

        Returns
        -------
        dict
            Fully-resolved RAG config dict with absolute paths.
        """
        merged = dict(self.global_rag)  # start with global defaults
        merged.update(private_rag)  # per-agent overrides win

        # Resolve from_global_index_dir → absolute paths
        global_index_dirs = merged.pop("from_global_index_dir", None)
        if global_index_dirs:
            merged["shared_rag_index_dirs"] = [
                os.path.join(self.global_uri, d) for d in global_index_dirs
            ]

        # Resolve embed_api_key template
        if "embed_api_key" in merged:
            merged["embed_api_key"] = self.resolve_template_var(merged["embed_api_key"])

        # local_index_dir is resolved later when local_uri is known
        return merged

    # ------------------------------------------------------------------
    # Per-agent knowledge resolution
    # ------------------------------------------------------------------

    def resolve_agent_knowledge(
        self,
        agent_id: str,
        private_knowledge: Dict[str, Any],
        record_path: str = "",
    ) -> Dict[str, Any]:
        """Resolve the full knowledge configuration for a single agent.

        This method is the single entry-point that agents call during
        initialization.  It merges global and per-agent configs, resolves
        all paths to absolute form, and returns a self-contained dict
        that the agent can use directly.

        Parameters
        ----------
        agent_id : str
            The agent's unique identity (e.g. ``"ragllm_momentum_1"``).
        private_knowledge : dict
            The agent's ``private_knowledge`` section from players.yml.
        record_path : str
            Experiment output directory (used for auto-generating local_uri).

        Returns
        -------
        dict
            Fully-resolved knowledge configuration with keys:

            - ``global_uri``: Absolute path to shared document root
            - ``processed_dir``: Absolute path to MinerU output
            - ``shared_rag_dir``: Absolute path to shared RAG index
            - ``local_uri``: Absolute path to agent-local workspace
            - ``local_processed_dir``: Absolute path to local processed copy
            - ``local_rag_dir``: Absolute path to local RAG index
            - ``from_global_resources``: List of global resource sub-dirs to inherit
            - ``rag``: Fully merged and resolved RAG config dict
        """
        # --- local_uri resolution ---
        local_res = private_knowledge.get("local_resources", {})
        local_uri = local_res.get("local_uri", "")
        if not local_uri:
            # Auto-generate: EXPERIMENT/<scenario>/agents/<agent_id>/
            if record_path:
                path_parts = record_path.split(os.sep)
                if len(path_parts) >= 3:
                    scenario = os.path.join(*path_parts[:3])
                else:
                    scenario = record_path
            else:
                scenario = "EXPERIMENT"
            local_uri = os.path.join(scenario, "agents", agent_id)
        local_uri = os.path.normpath(local_uri)

        # --- from_global_resources ---
        from_global = private_knowledge.get("from_global_resources", [])

        # --- local_resources (agent-specific files/URLs) ---
        local_res_list = local_res.get("local_resources", [])

        # --- RAG merge ---
        private_rag = private_knowledge.get("rag", {})
        resolved_rag = self.resolve_agent_rag(private_rag)

        # Resolve local_index_dir
        local_index_dir = resolved_rag.pop("local_index_dir", "")
        if not local_index_dir:
            local_index_dir = os.path.join(local_uri, "rag_index")
        elif not os.path.isabs(local_index_dir):
            local_index_dir = os.path.join(local_uri, local_index_dir)
        resolved_rag["local_index_dir"] = os.path.normpath(local_index_dir)

        # Build the result
        result = {
            "global_uri": self.global_uri,
            "processed_dir": self.processed_dir,
            "shared_rag_dir": self.shared_rag_dir,
            "local_uri": local_uri,
            "local_processed_dir": os.path.join(local_uri, self.output_position),
            "local_rag_dir": resolved_rag["local_index_dir"],
            "from_global_resources": from_global,
            "local_resources": local_res_list,
            "rag": resolved_rag,
        }

        logger.info(
            "[ResourceManager] Resolved knowledge for %s:\n"
            "  global_uri=%s\n  processed_dir=%s\n  shared_rag_dir=%s\n"
            "  local_uri=%s\n  local_rag_dir=%s\n"
            "  from_global_resources=%s",
            agent_id,
            result["global_uri"],
            result["processed_dir"],
            result["shared_rag_dir"],
            result["local_uri"],
            result["local_rag_dir"],
            result["from_global_resources"],
        )

        return result

    # ------------------------------------------------------------------
    # Shared resource preparation (PDF pre-processing)
    # ------------------------------------------------------------------

    def prepare_shared_resources(self, fail_fast: bool = False) -> Dict[str, bool]:
        """Prepare all shared resources (download + parse PDFs).

        Scans resource_csv entries (CSV files and directories) under
        global_uri to discover PDFs, then processes them with MinerU.
        Already-processed PDFs are skipped.
        """
        from masim.knowledge.loader import _parse_pdf

        results = {}
        pdf_files = self._collect_shared_pdfs()
        processed_dir = self.processed_dir
        os.makedirs(processed_dir, exist_ok=True)

        for pdf_path in sorted(pdf_files):
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            cached_md = os.path.join(processed_dir, pdf_name, f"{pdf_name}.md")
            if os.path.isfile(cached_md):
                logger.info("[ResourceManager] Already processed: %s", pdf_name)
                results[pdf_path] = True
                continue
            logger.info("[ResourceManager] Processing: %s", pdf_path)
            try:
                text = _parse_pdf(
                    pdf_path, fail_fast=fail_fast, processed_dir=processed_dir
                )
                results[pdf_path] = text is not None
                if text:
                    logger.info(
                        "[ResourceManager] Processed %s (%d chars)", pdf_name, len(text)
                    )
                else:
                    logger.warning("[ResourceManager] Failed to process %s", pdf_name)
            except Exception as exc:
                results[pdf_path] = False
                logger.error("[ResourceManager] Error processing %s: %s", pdf_path, exc)
                if fail_fast:
                    raise

        success = sum(1 for v in results.values() if v)
        logger.info(
            "[ResourceManager] Shared resources ready: %d/%d", success, len(results)
        )
        return results

    # ------------------------------------------------------------------
    # PDF discovery from resource_csv
    # ------------------------------------------------------------------

    def _collect_shared_pdfs(self) -> List[str]:
        """Collect all shared PDFs from resource_csv entries.

        Each entry in resource_csv can be:
        - A CSV file path: rows with source_type=file and .pdf URLs are collected
        - A directory path: all .pdf files inside are auto-discovered
        - A dict with ``type``/``path`` or ``type``/``paths`` (legacy format)
        """
        pdf_files = []
        for entry in self.resource_csv:
            if isinstance(entry, dict):
                # Legacy format: {type: "file", paths: [...]} or {type: "url_csv", path: "..."}
                res_type = entry.get("type", "")
                if res_type == "file":
                    for path in entry.get("paths", []):
                        full_path = os.path.join(self.global_uri, path)
                        if os.path.isfile(full_path) and full_path.lower().endswith(
                            ".pdf"
                        ):
                            pdf_files.append(full_path)
                        elif not os.path.isfile(full_path):
                            logger.warning(
                                "[ResourceManager] File not found: %s", full_path
                            )
                elif res_type == "url_csv":
                    csv_path = entry.get("path", "")
                    pdf_files.extend(self._collect_pdfs_from_csv(csv_path))
            elif isinstance(entry, str):
                # New format: string path — could be CSV file or directory
                full = entry if os.path.isabs(entry) else entry
                if os.path.isdir(full):
                    # Directory: auto-discover PDF files
                    pdf_files.extend(self._discover_pdfs_in_dir(full))
                elif os.path.isfile(full) and full.lower().endswith(".csv"):
                    # CSV file: collect PDF paths from rows
                    pdf_files.extend(self._collect_pdfs_from_csv(full))
                elif not os.path.exists(full):
                    logger.warning(
                        "[ResourceManager] resource_csv entry not found: %s", full
                    )
            else:
                logger.warning(
                    "[ResourceManager] Unknown resource_csv entry type: %s", type(entry)
                )
        return pdf_files

    def _discover_pdfs_in_dir(self, dir_path: str) -> List[str]:
        """Recursively discover PDF files in a directory."""
        pdfs = []
        if not os.path.isdir(dir_path):
            return pdfs
        for root, _dirs, files in os.walk(dir_path):
            for fname in sorted(files):
                if fname.lower().endswith(".pdf"):
                    pdfs.append(os.path.join(root, fname))
        return pdfs

    def _collect_pdfs_from_csv(self, csv_path: str) -> List[str]:
        import csv as csv_mod

        pdfs = []
        if not os.path.isfile(csv_path):
            logger.warning("[ResourceManager] CSV not found: %s", csv_path)
            return pdfs
        try:
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv_mod.DictReader(f)
                for row in reader:
                    url = (row.get("url") or row.get("URL") or "").strip()
                    source_type = (
                        (row.get("source_type") or row.get("source") or "web")
                        .lower()
                        .strip()
                    )
                    if source_type == "file" and url.lower().endswith(".pdf"):
                        if os.path.isabs(url):
                            pdfs.append(url)
                        else:
                            full = os.path.join(self.global_uri, url)
                            if os.path.isfile(full):
                                pdfs.append(full)
        except Exception as exc:
            logger.error("[ResourceManager] Failed to read CSV %s: %s", csv_path, exc)
        return pdfs

    # ------------------------------------------------------------------
    # Document loading & copying helpers
    # ------------------------------------------------------------------

    def get_processed_documents(self, agent_id: str = "") -> List[Any]:
        from masim.knowledge.loader import KnowledgeLoader

        loader = KnowledgeLoader()
        processed_dir = self.processed_dir
        if not os.path.isdir(processed_dir) or not os.listdir(processed_dir):
            logger.warning(
                "[ResourceManager] No processed documents at %s for %s",
                processed_dir,
                agent_id,
            )
            return []
        docs = loader.load_from_dir(processed_dir)
        logger.info("[ResourceManager] Loaded %d documents for %s", len(docs), agent_id)
        return docs

    def copy_to_agent_local(self, agent_id: str, local_uri: str) -> bool:
        """Copy processed documents from shared dir to agent-local workspace."""
        processed_dir = self.processed_dir
        if not os.path.isdir(processed_dir):
            return False
        local_processed = os.path.join(local_uri, self.output_position)
        os.makedirs(local_processed, exist_ok=True)
        try:
            for item in os.listdir(processed_dir):
                src = os.path.join(processed_dir, item)
                dst = os.path.join(local_processed, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            logger.info(
                "[ResourceManager] Copied processed docs to %s local: %s",
                agent_id,
                local_processed,
            )
            return True
        except Exception as exc:
            logger.error(
                "[ResourceManager] Failed to copy to %s local: %s", agent_id, exc
            )
            return False

    def copy_shared_rag_to_agent(self, agent_id: str, local_rag_dir: str) -> bool:
        """Copy shared RAG index to an agent's local workspace.

        Parameters
        ----------
        agent_id : str
            Agent identifier for logging.
        local_rag_dir : str
            Destination directory for the local RAG index copy.

        Returns
        -------
        bool
            True if copy was successful, False otherwise.
        """
        shared_dir = self.shared_rag_dir
        if not os.path.isdir(shared_dir):
            logger.info(
                "[ResourceManager] No shared RAG index to copy for %s", agent_id
            )
            return False
        try:
            os.makedirs(local_rag_dir, exist_ok=True)
            for item in os.listdir(shared_dir):
                if item.startswith("."):
                    continue
                src = os.path.join(shared_dir, item)
                dst = os.path.join(local_rag_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            logger.info(
                "[ResourceManager] Copied shared RAG index to %s local: %s",
                agent_id,
                local_rag_dir,
            )
            return True
        except Exception as exc:
            logger.error(
                "[ResourceManager] Failed to copy RAG to %s local: %s", agent_id, exc
            )
            return False
