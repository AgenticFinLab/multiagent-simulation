"""Discovery-based agent catalog for the Customized Simulation Builder.

This module replaces the former ``agent_catalog.yml`` + loader pair with a
*pure introspection* layer over :mod:`masim.agents`. Every piece of metadata
the marketplace UI and bundle writer need now lives **on the canonical agent
classes themselves**, so there is exactly one source of truth and no risk of
drift between a sidecar YAML and the code.

Per-archetype metadata layout (see :mod:`masim.agents._base`):

* ``STRATEGY``           — archetype identifier (shared between Rule and LLM
                            siblings). Used as the catalog key.
* ``DISPLAY_NAME``       — UI label (declared on the Rule class).
* ``SUMMARY``            — one-line description (declared on the Rule class).
* ``REQUIRES_FEATURES``  — tuple of feature names from
                            ``scenario_features.yml`` (declared on the Rule
                            class; defaults to ``()``).
* ``DEFAULT_SYS_PROMPT`` — canonical LLM system prompt (declared on the LLM
                            class).
* ``DEFAULT_USER_PROMPT``— canonical LLM user-template prompt (declared on
                            the LLM class).

Engine resolution:
    * ``Rule``    → the canonical Rule class.
    * ``LLM``     → the canonical LLM class.
    * ``RuleLLM`` → reuses the canonical Rule class (rule executes the order;
                    LLM annotates the reasoning).

An archetype is "supported" for an engine only when the corresponding class
exists. There is no notion of a "niche archetype with no class" — if a
canonical class is not yet implemented, the archetype simply does not appear
in discovery (and therefore not in the UI).

The public API is preserved 1:1 with the previous YAML-backed loader so call
sites (``config_writer.py``, ``scenario_features.py``, ``agent_market.py``)
need no functional changes.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Iterable, Optional

from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer
from masim.agents._coordinator_base import CanonicalMarketCoordinator


_AGENTS_PACKAGE = "masim.agents"


@dataclass(frozen=True)
class AgentEntry:
    """One archetype's row in the catalog (discovered, not parsed)."""

    archetype: str
    display_name: str
    summary: str
    supported_engines: tuple[str, ...]
    requires_market_features: tuple[str, ...]
    canonical_classes: dict[str, str] = field(default_factory=dict)
    default_prompts: dict[str, dict[str, str]] = field(default_factory=dict)

    def is_engine_supported(self, engine: str) -> bool:
        return engine in self.supported_engines

    def has_canonical_class(self, engine: str) -> bool:
        return engine in self.canonical_classes and bool(
            self.canonical_classes.get(engine)
        )

    def class_path(self, engine: str) -> Optional[str]:
        path = self.canonical_classes.get(engine)
        return path or None

    def prompts_for(self, engine: str) -> tuple[str, str]:
        block = self.default_prompts.get(engine) or {}
        sys_msg = str(block.get("sys") or "").strip()
        user_msg = str(block.get("user") or "").strip()
        return sys_msg, user_msg


# ---------------------------------------------------------------------------
# Discovery internals
# ---------------------------------------------------------------------------


def _iter_agent_modules() -> Iterable:
    """Yield each importable sub-module under :mod:`masim.agents`."""
    pkg = importlib.import_module(_AGENTS_PACKAGE)
    for info in pkgutil.iter_modules(pkg.__path__):
        # Skip private helpers (``_base``, ``_state``) to keep discovery cheap;
        # those modules expose the base classes and standard market state, not
        # canonical archetypes.
        if info.name.startswith("_"):
            continue
        yield importlib.import_module(f"{_AGENTS_PACKAGE}.{info.name}")


def _is_concrete_subclass(obj, base) -> bool:
    return (
        inspect.isclass(obj)
        and issubclass(obj, base)
        and obj is not base
        # ``STRATEGY`` must be overridden — base classes carry placeholder values.
        and getattr(obj, "STRATEGY", base.STRATEGY) != base.STRATEGY
    )


def _class_path(cls) -> str:
    return f"{cls.__module__}:{cls.__qualname__}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def load_agent_catalog(path: Optional[str] = None) -> dict[str, AgentEntry]:
    """Return ``{archetype: AgentEntry}`` discovered from :mod:`masim.agents`.

    The ``path`` parameter is accepted for backwards compatibility but is
    ignored — the catalog is now derived from class metadata, not a YAML file.

    Discovers three class families:
      * ``CanonicalRulePlayer`` subclasses — investor Rule agents
      * ``CanonicalLLMPlayer`` subclasses — investor LLM agents
      * ``CanonicalMarketCoordinator`` subclasses — market coordinators
    """
    del path  # discovery is path-free

    rule_classes: dict[str, type] = {}
    llm_classes: dict[str, type] = {}
    coordinator_classes: dict[str, type] = {}

    for module in _iter_agent_modules():
        for _, cls in inspect.getmembers(module, inspect.isclass):
            if cls.__module__ != module.__name__:
                continue  # skip re-imported symbols
            if _is_concrete_subclass(cls, CanonicalRulePlayer):
                rule_classes.setdefault(cls.STRATEGY, cls)
            elif _is_concrete_subclass(cls, CanonicalLLMPlayer):
                llm_classes.setdefault(cls.STRATEGY, cls)
            elif _is_concrete_subclass(cls, CanonicalMarketCoordinator):
                coordinator_classes.setdefault(cls.STRATEGY, cls)

    archetypes = sorted(set(rule_classes) | set(llm_classes) | set(coordinator_classes))
    out: dict[str, AgentEntry] = {}
    for archetype in archetypes:
        rule_cls = rule_classes.get(archetype)
        llm_cls = llm_classes.get(archetype)
        coord_cls = coordinator_classes.get(archetype)

        # Coordinator path — single class, always Rule engine.
        if coord_cls is not None:
            display_name = getattr(coord_cls, "DISPLAY_NAME", "") or archetype
            summary = getattr(coord_cls, "SUMMARY", "") or ""
            requires = tuple(getattr(coord_cls, "BROADCAST_FIELDS", ()) or ())
            canonical: dict[str, str] = {"Rule": _class_path(coord_cls)}
            out[archetype] = AgentEntry(
                archetype=archetype,
                display_name=str(display_name),
                summary=str(summary),
                supported_engines=("Rule",),
                requires_market_features=requires,
                canonical_classes=canonical,
                default_prompts={},
            )
            continue

        # Investor path — Rule + LLM siblings.
        # Display metadata: prefer Rule class (always present for implemented
        # archetypes); fall back to LLM class if Rule is missing.
        meta_src = rule_cls or llm_cls
        display_name = getattr(meta_src, "DISPLAY_NAME", "") or archetype
        summary = getattr(meta_src, "SUMMARY", "") or ""
        requires = tuple(getattr(meta_src, "REQUIRES_FEATURES", ()) or ())

        canonical = {}
        if rule_cls is not None:
            canonical["Rule"] = _class_path(rule_cls)
            # RuleLLM reuses the Rule executor; the LLM only contributes
            # commentary, so the bundle writer points players.yml at the Rule
            # class with LLM extras attached.
            canonical["RuleLLM"] = _class_path(rule_cls)
        if llm_cls is not None:
            canonical["LLM"] = _class_path(llm_cls)

        prompts: dict[str, dict[str, str]] = {}
        if llm_cls is not None:
            sys_p = str(getattr(llm_cls, "DEFAULT_SYS_PROMPT", "") or "").strip()
            user_p = str(getattr(llm_cls, "DEFAULT_USER_PROMPT", "") or "").strip()
            if sys_p or user_p:
                prompts["LLM"] = {"sys": sys_p, "user": user_p}
                # Mirror the LLM prompts onto RuleLLM so the marketplace can
                # surface the same default text when the user picks the hybrid
                # engine. (The Rule executor ignores prompts at runtime.)
                prompts["RuleLLM"] = {"sys": sys_p, "user": user_p}

        # The engine order matters for UI display: Rule, LLM, RuleLLM.
        engine_order = ("Rule", "LLM", "RuleLLM")
        engines = tuple(e for e in engine_order if e in canonical)

        out[archetype] = AgentEntry(
            archetype=archetype,
            display_name=str(display_name),
            summary=str(summary),
            supported_engines=engines,
            requires_market_features=requires,
            canonical_classes=canonical,
            default_prompts=prompts,
        )
    return out


def get_agent_entry(archetype: str) -> Optional[AgentEntry]:
    """Return the catalog entry for ``archetype`` (``None`` when missing)."""
    return load_agent_catalog().get(archetype)


def is_archetype_supported(archetype: str, engine: str) -> bool:
    """Return ``True`` when discovery found a canonical class for the engine."""
    entry = get_agent_entry(archetype)
    if entry is None:
        return False
    return entry.is_engine_supported(engine)


def get_canonical_class_path(archetype: str, engine: str) -> Optional[str]:
    """Return ``module:Class`` for ``(archetype, engine)`` (``None`` if unmapped).

    A ``None`` return means the archetype is unknown or the engine is not
    implemented for it. The bundle writer uses this signal to abort with a
    clear error rather than emit a broken bundle.
    """
    entry = get_agent_entry(archetype)
    if entry is None:
        return None
    return entry.class_path(engine)


def get_default_prompts(archetype: str, engine: str) -> tuple[str, str]:
    """Return ``(sys_prompt, user_prompt)`` strings for the textarea pre-fill.

    Both elements are empty strings when no default is shipped for the
    ``(archetype, engine)`` pair (e.g. the engine is ``Rule`` only).
    """
    entry = get_agent_entry(archetype)
    if entry is None:
        return "", ""
    return entry.prompts_for(engine)


def supported_engines(archetype: str) -> tuple[str, ...]:
    """Return the engines declared for the archetype."""
    entry = get_agent_entry(archetype)
    if entry is None:
        return ()
    return entry.supported_engines


def required_features(archetype: str) -> tuple[str, ...]:
    """Return the market features the archetype depends on."""
    entry = get_agent_entry(archetype)
    if entry is None:
        return ()
    return entry.requires_market_features


def all_archetypes() -> Iterable[str]:
    """Iterate the archetype names declared in the catalog."""
    return tuple(load_agent_catalog().keys())


__all__ = [
    "AgentEntry",
    "load_agent_catalog",
    "get_agent_entry",
    "is_archetype_supported",
    "get_canonical_class_path",
    "get_default_prompts",
    "supported_engines",
    "required_features",
    "all_archetypes",
]
