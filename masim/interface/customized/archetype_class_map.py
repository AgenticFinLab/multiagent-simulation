"""Loader and accessors for the curated archetype→class binding map."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml


_MAP_PATH = Path(__file__).resolve().parent / "archetype_class_map.yml"


@dataclass(frozen=True)
class ArchetypeBinding:
    """A concrete (archetype, engine) → existing class binding."""

    archetype: str
    engine: str
    class_path: str
    remap: dict[str, str] = field(default_factory=dict)
    # ``module:VARIABLE`` references to the prompt strings shipped with
    # the example codebase (LLM/RuleLLM/Rag engines only). Empty when
    # the engine has no prompt component (e.g. pure ``Rule``).
    sys_prompt_ref: str = ""
    user_prompt_ref: str = ""

    def kwarg_name(self, symbol: str) -> str:
        """Translate a handbook symbol into the class kwarg name.

        Falls back to a sanitised version of the symbol when no explicit
        remap entry is present.
        """
        if symbol in self.remap:
            return self.remap[symbol]
        # Conservative default: treat the raw symbol as the kwarg name
        # whenever it already looks like a valid Python identifier.
        if symbol.isidentifier():
            return symbol
        # Strip any non-identifier characters (e.g. greek letters) and
        # fall back to the resulting ASCII identifier.  If nothing is
        # left, return the raw symbol so the caller can decide.
        ident = "".join(ch for ch in symbol if ch.isalnum() or ch == "_")
        return ident or symbol


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


@lru_cache(maxsize=1)
def load_archetype_class_map(path: Optional[str] = None) -> dict[str, dict[str, dict]]:
    """Return the parsed YAML mapping (archetype → engine → entry).

    ``entry`` is itself a dict with at least ``class`` (dotted import
    path) and an optional ``remap`` (symbol → kwarg).
    """
    target = Path(path) if path else _MAP_PATH
    if not target.exists():
        return {}
    raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return {}
    # Defensive copy so callers cannot mutate the cached map.
    out: dict[str, dict[str, dict]] = {}
    for archetype, engines in raw.items():
        if not isinstance(engines, dict):
            continue
        engine_map: dict[str, dict] = {}
        for engine, entry in engines.items():
            if not isinstance(entry, dict):
                continue
            cls = entry.get("class")
            if not cls:
                continue
            engine_map[engine] = {
                "class": cls,
                "remap": dict(entry.get("remap") or {}),
                "sys_prompt": entry.get("sys_prompt", "") or "",
                "user_prompt": entry.get("user_prompt", "") or "",
            }
        if engine_map:
            out[archetype] = engine_map
    return out


@lru_cache(maxsize=128)
def _load_prompt_value(ref: str) -> str:
    """Import and return the prompt string at ``module:VARIABLE``.

    Returns the empty string when the reference is empty, malformed,
    or fails to import — the caller treats that as "no default".
    Cached because Streamlit re-runs the page on every interaction
    and re-importing prompt modules every time would be wasteful.
    """
    if not ref or ":" not in ref:
        return ""
    module_path, var_name = ref.rsplit(":", 1)
    try:
        module = importlib.import_module(module_path)
    except Exception:
        return ""
    value = getattr(module, var_name, None)
    return value if isinstance(value, str) else ""


def load_default_prompts(
    archetype: str,
    engine: str,
    *,
    map_path: Optional[str] = None,
) -> tuple[str, str]:
    """Return ``(sys_prompt, user_prompt)`` strings for an archetype + engine.

    Both fields are empty strings when the binding does not declare a
    prompt source or the import fails. Used by the Streamlit panel to
    pre-fill the editable textareas so users can SEE the shipped
    default prompt rather than guessing from a placeholder.
    """
    table = load_archetype_class_map(map_path)
    entry = (table.get(archetype) or {}).get(engine) or {}
    sys_ref = entry.get("sys_prompt", "") or ""
    user_ref = entry.get("user_prompt", "") or ""
    return _load_prompt_value(sys_ref), _load_prompt_value(user_ref)


def resolve_archetype_binding(
    archetype: str,
    engine: str,
    *,
    map_path: Optional[str] = None,
) -> Optional[ArchetypeBinding]:
    """Look up a binding; return ``None`` when no entry exists.

    The lookup falls back to the ``Rule`` engine if the requested engine
    is missing, since the rule-based variant is always present in the
    example codebase and provides a working class for the simulator.
    """
    table = load_archetype_class_map(map_path)
    engines = table.get(archetype) or {}
    entry = engines.get(engine) or engines.get("Rule")
    if not entry:
        return None
    chosen_engine = engine if engine in engines else ("Rule" if "Rule" in engines else next(iter(engines)))
    return ArchetypeBinding(
        archetype=archetype,
        engine=chosen_engine,
        class_path=entry["class"],
        remap=dict(entry.get("remap") or {}),
        sys_prompt_ref=entry.get("sys_prompt", "") or "",
        user_prompt_ref=entry.get("user_prompt", "") or "",
    )


def is_archetype_mapped(archetype: str, *, map_path: Optional[str] = None) -> bool:
    """``True`` when at least one engine binding exists for ``archetype``."""
    return archetype in load_archetype_class_map(map_path)
