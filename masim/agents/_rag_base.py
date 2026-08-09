"""Canonical base for RAG-augmented LLM agents.

:class:`CanonicalRagPlayer` extends :class:`CanonicalLLMPlayer` with a
per-round knowledge-retrieval step whose result is injected into the
user template as ``{rag_context}`` before the LLM call.  Every
scenario-side ``Rag/players.py`` should be a re-export module that
subclasses :class:`CanonicalRagPlayer` (or the shipped
:class:`CanonicalLLMPlayer` sub-tree) rather than reimplementing the
``perceive/decide/act`` skeleton, the RAG index bootstrap, or the
pickle-safe reconstruction logic.

Design rationale
----------------

The RAG plumbing (load / shared-copy / build / persist) is entirely
scenario-agnostic: what changes between scenarios is only the
retrieval *query* (which needs to mention the scenario's market
signals: e.g. ``anchoring bias trading strategy when: price=..., fundamental=...``).
That query is exposed as the :meth:`_build_rag_query` hook so
subclasses override a single method rather than duplicating ~200 lines
of infrastructure.

Everything else — LLM client bootstrap, schema-validated retries,
strict finalization (cash/inventory clipping, positive-``bid_price``
enforcement), truthful-``agent_state`` outbound injection — is
inherited from :class:`CanonicalLLMPlayer`.  A missing ``bid_price``
still hits :func:`masim.format.finalize.finalize_llm_order` and there
is NO ``bid_price <= 0 → state.price`` silent fallback anywhere in
this file.

Public surface
--------------

* :data:`RAG_FALLBACK_MESSAGE` — the sentinel string emitted when the
  RAG store is unavailable or returns no documents.  Scenario audits
  (e.g. ``examples/AnchoringEffect/Rag/analysis.py``) import this to
  detect Retrieval-Failure rounds; the value must remain stable across
  releases.
* :class:`CanonicalRagPlayer` — the base class.
* :meth:`CanonicalRagPlayer._build_rag_query` — scenario override hook.
"""

from __future__ import annotations

import logging
import os
import shutil
from typing import Any, Dict, Optional

from masim.agents._base import CanonicalLLMPlayer
from masim.format.state import StandardMarketState

logger = logging.getLogger("masim.agents.rag")


# Module-level sentinel returned when RAG retrieval yields no documents.
# Scenario ``analysis.py`` files import this constant to detect
# Retrieval-Failure rounds, so the value MUST remain stable across
# releases (see e.g. ``examples/AnchoringEffect/Rag/analysis.py`` and
# the analysis-bases §3 Knowledge-Effect diagnostics).
RAG_FALLBACK_MESSAGE: str = "(No relevant knowledge retrieved this round.)"


class CanonicalRagPlayer(CanonicalLLMPlayer):
    """Base class for RAG-augmented, scenario-agnostic LLM agents.

    Contract summary
    ----------------
    * Reads the same ``extras["llm"]`` block as :class:`CanonicalLLMPlayer`
      (``lm_name``, ``generation_config``, ``sys_message``, ``user_message``).
    * Additionally requires ``extras["private_knowledge"]["rag"]``
      (RAG config: docs_dir, embed_type, embed_model, embed_api_key,
      embed_api_base, chunk_size, chunk_overlap, top_k, plus
      ``mineru_output_dir`` / ``shared_rag_index_dir`` when the caller
      does not pre-populate ``extras["knowledge"]``).
    * The ``{rag_context}`` template placeholder in ``user_message``
      is populated automatically each round.  Absent RAG results fall
      back to :data:`RAG_FALLBACK_MESSAGE` (stored in
      ``custom_state["last_rag_context"]`` so downstream analyses can
      detect it).

    Subclass hooks
    --------------
    * :meth:`_build_rag_query` — override to tailor the retrieval query
      to a specific scenario's market signals.  Default query mentions
      only fields present on every :class:`StandardMarketState`
      (``price``, ``prev_price``, ``fundamental``, ``deviation``).
    """

    STRATEGY: str = "CanonicalRagPlayer"

    # ------------------------------------------------------------------
    # Retrieval hook (scenario-specific)
    # ------------------------------------------------------------------

    def _build_rag_query(self, state: StandardMarketState) -> str:
        """Return the retrieval query string for this round.

        Default implementation mentions only fields guaranteed by the
        canonical broadcast contract (:mod:`masim.format.state`) so
        every scenario gets a sensible baseline.  Behavioural /
        micro-structure scenarios (Anchoring, Herding, FlashCrash, …)
        should override to weave in their own signal vocabulary — but
        keep the query short (a few sentences at most) so the RAG
        index's chunk-level similarity remains meaningful.
        """
        parts = [
            f"trading strategy when price={state.price:.4g}",
            f"prev_price={state.prev_price:.4g}",
        ]
        # `fundamental` / `deviation` may legitimately be NaN when the
        # scenario has no intrinsic value; guard so the query stays
        # human-readable.
        if state.fundamental == state.fundamental:  # not NaN
            parts.append(f"fundamental={state.fundamental:.4g}")
        if state.deviation == state.deviation:  # not NaN
            parts.append(f"deviation={state.deviation:+.2%}")
        return "; ".join(parts)

    # ------------------------------------------------------------------
    # RAG retrieval + prompt injection
    # ------------------------------------------------------------------

    def _retrieve_rag_context(self, state: StandardMarketState) -> str:
        """Query the RAG store and return the formatted-text context.

        Returns :data:`RAG_FALLBACK_MESSAGE` when the store is
        unavailable / empty; every result — including the fallback —
        is stashed in ``custom_state["last_rag_context"]`` so scenario
        audits can detect Retrieval-Failure rounds after the fact.
        """
        from masim.knowledge import KnowledgeQuery

        store = self._ensure_rag_store()
        if store is None or not store.is_built():
            self.state.custom_state["last_rag_context"] = RAG_FALLBACK_MESSAGE
            return RAG_FALLBACK_MESSAGE

        rag_cfg: Dict[str, Any] = self.state.custom_state.get("rag_cfg", {}) or {}
        top_k = int(rag_cfg.get("top_k", 3))

        query = KnowledgeQuery(
            text=self._build_rag_query(state),
            top_k=top_k,
            round_num=state.round,
            agent_id=self.identity,
        )
        try:
            result = store.query(query)
            text = result.formatted_text or RAG_FALLBACK_MESSAGE
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "[%s] RAG query failed (%s); emitting fallback context.",
                self.identity,
                exc,
            )
            text = RAG_FALLBACK_MESSAGE
        self.state.custom_state["last_rag_context"] = text
        return text

    def _format_user_prompt(
        self,
        user_template: str,
        state: StandardMarketState,
    ) -> str:
        """Inject ``{rag_context}`` alongside the standard market vars.

        Called by :meth:`CanonicalLLMPlayer._run_llm`; RAG scenarios
        override this hook rather than the whole ``_run_llm`` skeleton
        so schema-validated retries and category-aware finalisation
        continue to work unchanged.
        """
        rag_context = self._retrieve_rag_context(state)
        template_vars = dict(state.template_vars())
        template_vars["rag_context"] = rag_context
        return user_template.format(**template_vars)

    # ------------------------------------------------------------------
    # Lazy RAG-store bootstrap (mirrors CanonicalLLMPlayer._ensure_client)
    # ------------------------------------------------------------------

    def _ensure_rag_store(self):
        """Return a live :class:`KnowledgeStore`, building it on first use.

        Bootstrap order (unchanged from the legacy hand-rolled RAG code):

        1. If ``custom_state['rag_store']`` is set (either from prior
           call this process or reconstructed by :meth:`__setstate__`),
           return it.
        2. Resolve the agent's knowledge tree via
           :class:`~masim.knowledge.ResourceManager`.
        3. Instantiate :class:`~masim.knowledge.KnowledgeStore`.
        4. Load the local index if present; else copy any shared index
           to local; else build from ``processed_dir``.
        5. On successful build, replicate to the shared cache so peer
           agents in the same run avoid a duplicate build.

        Fail-loud on ``extras["private_knowledge"]["rag"]`` missing —
        a RAG agent without a RAG config is a scenario mis-wiring.
        """
        cached = self.state.custom_state.get("rag_store")
        if cached is not None:
            return cached

        extras = self.config.extras
        private_knowledge = extras.get("private_knowledge") or {}
        rag_cfg_raw = private_knowledge.get("rag")
        if not rag_cfg_raw:
            raise RuntimeError(
                f"[{self.identity}] CanonicalRagPlayer: "
                f"extras.private_knowledge.rag is required for RAG agents. "
                f"Ensure the scenario's players.yml provides the RAG "
                f"configuration block (docs_dir, embed_type, embed_model, "
                f"top_k, ...)."
            )

        # ── Load the .env file if any so embed_api_key / ARK_API_KEY
        # style variables reach os.environ before we probe them.
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv()
        except Exception:  # noqa: BLE001
            pass

        from masim.knowledge import (
            KnowledgeLoader,
            KnowledgeStore,
            ResourceManager,
        )

        record_path = extras.get("record_path", "")

        knowledge_config = extras.get("knowledge") or {
            "backend": "local",
            "global_uri": rag_cfg_raw["docs_dir"],
            "preprocessing": {
                "parser": "mineru",
                "output_position": rag_cfg_raw["mineru_output_dir"],
            },
            "rag": {
                "output_position": rag_cfg_raw["shared_rag_index_dir"],
            },
        }
        resource_manager = ResourceManager(knowledge_config)

        agent_knowledge = resource_manager.resolve_agent_knowledge(
            agent_id=self.identity,
            private_knowledge=private_knowledge or {
                "from_global_resources": ["MinerU_processed"],
                "local_resources": {"local_uri": "", "local_resources": []},
                "rag": rag_cfg_raw,
            },
            record_path=record_path,
        )

        processed_dir = agent_knowledge["processed_dir"]
        shared_rag_dir = agent_knowledge["shared_rag_dir"]
        local_uri = agent_knowledge["local_uri"]
        local_rag_dir = agent_knowledge["local_rag_dir"]
        resolved_rag = agent_knowledge["rag"]

        os.makedirs(local_uri, exist_ok=True)
        os.makedirs(local_rag_dir, exist_ok=True)

        embed_type = resolved_rag["embed_type"]
        embed_model = resolved_rag["embed_model"]
        embed_api_base = resolved_rag["embed_api_base"]
        embed_api_key = resolved_rag["embed_api_key"]
        chunk_size = int(resolved_rag["chunk_size"])
        chunk_overlap = int(resolved_rag["chunk_overlap"])

        if not embed_api_key:
            if embed_type == "litellm":
                embed_api_key = os.getenv("HUNYUAN_API_KEY", "")
            elif embed_type == "openai":
                embed_api_key = os.getenv("ARK_API_KEY", "")

        store = KnowledgeStore(
            embed_model_name=embed_model,
            embed_api_key=embed_api_key,
            embed_api_base=embed_api_base,
            embed_type=embed_type,
            persist_dir=local_rag_dir,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # 1. Local first
        if os.path.isdir(local_rag_dir):
            index_files = [
                f for f in os.listdir(local_rag_dir) if not f.startswith(".")
            ]
            if index_files:
                try:
                    store.load(local_rag_dir)
                    self._register_rag(store, resolved_rag)
                    logger.info(
                        "[%s] Loaded local RAG index (%d files)",
                        self.identity,
                        len(index_files),
                    )
                    return store
                except Exception as exc:  # noqa: BLE001
                    logger.warning(
                        "[%s] Failed to load local index (%s); trying shared",
                        self.identity,
                        exc,
                    )

        # 2. Shared copy
        shared_dirs = (
            resolved_rag["shared_rag_index_dirs"]
            if "shared_rag_index_dirs" in resolved_rag
            else []
        )
        if not shared_dirs and os.path.isdir(shared_rag_dir):
            shared_dirs = [shared_rag_dir]

        for s_dir in shared_dirs:
            if not os.path.isdir(s_dir):
                continue
            shared_files = [f for f in os.listdir(s_dir) if not f.startswith(".")]
            if not shared_files:
                continue
            try:
                for item in shared_files:
                    src = os.path.join(s_dir, item)
                    dst = os.path.join(local_rag_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                store.load(local_rag_dir)
                self._register_rag(store, resolved_rag)
                logger.info(
                    "[%s] Copied shared RAG index to local", self.identity
                )
                return store
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "[%s] Failed to copy shared index (%s); building",
                    self.identity,
                    exc,
                )

        # 3. Build from processed_dir
        loader = KnowledgeLoader()
        if os.path.isdir(processed_dir) and os.listdir(processed_dir):
            docs = loader.load_from_dir(processed_dir)
        else:
            raise RuntimeError(
                f"[{self.identity}] No processed documents available for "
                f"RAG in {processed_dir}."
            )
        store.build(docs)

        # 4. Replicate to shared cache (best-effort)
        try:
            os.makedirs(shared_rag_dir, exist_ok=True)
            for item in os.listdir(local_rag_dir):
                if item.startswith("."):
                    continue
                src = os.path.join(local_rag_dir, item)
                dst = os.path.join(shared_rag_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "[%s] Failed to copy to shared location: %s",
                self.identity,
                exc,
            )

        self._register_rag(store, resolved_rag)
        return store

    def _register_rag(self, store, resolved_rag: Dict[str, Any]) -> None:
        """Stash the live store + config for reuse and pickle rehydration."""
        self.state.custom_state["rag_store"] = store
        self.state.custom_state["rag_cfg"] = resolved_rag

    # ------------------------------------------------------------------
    # Pickling — drop the live handles, allow lazy reconstruction
    # ------------------------------------------------------------------

    def __getstate__(self):
        # Reuse the LLM-base drop of ``llm_client`` first, then strip
        # the RAG store on top.  Both are lazily reconstructed on next
        # access via :meth:`_ensure_client` / :meth:`_ensure_rag_store`.
        state = super().__getstate__()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            custom.pop("rag_store", None)
            state["state"].custom_state = custom
        return state


__all__ = [
    "CanonicalRagPlayer",
    "RAG_FALLBACK_MESSAGE",
]
