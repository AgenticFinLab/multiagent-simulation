"""Roster-entry data model for the customized simulation builder.

The Customize page used to store one configuration *per (archetype, engine)*
pair in ``st.session_state`` — encoded via the flat keys
``market_agent_{type}``, ``market_engine_{type}``,
``customized_num_instances_{type}`` and ``customized_params[type][engine]``.
That model made it impossible to express a common research need: the same
archetype appearing multiple times with *different* configurations (e.g.
"3 NoiseTraders on the Aggressive preset **and** 2 NoiseTraders on the
Cautious preset"), and it prevented the user from removing one specific
group of instances without also destroying the others.

This module introduces a new, first-class **roster-entry** model:

    roster_entries: list[RosterEntry]

Each :class:`RosterEntry` represents one YAML block in the generated
``players.yml`` — it owns its own engine, instance count, handbook
parameters and (optionally) LLM prompt overrides.  A single archetype
can appear in any number of entries; entries are keyed by a stable
opaque ``id`` so the UI can Edit / Duplicate / Remove one row without
disturbing the others.

The rest of the interface (widget keys, bundle writer, persistence) is
adapted to walk this list.  Legacy v1 / v2 session-state and
``selection_state.json`` files migrate transparently: a v2 selection
with 3 archetypes becomes 3 entries with 1 default configuration each.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Iterable, Optional

# Session-state key under which the roster lives. Keeping this centralised
# so every caller reads/writes the same slot and cannot drift.
ROSTER_KEY = "roster_entries"


# The five reserved keys the LLM engine dialog stashes inside ``params``.
# Duplicated here (rather than imported from :mod:`config_writer`) so this
# module has no import-time dependency on the writer.  If the writer ever
# grows a new reserved sentinel, add it in both places.
_LLM_LM_KEY = "__llm_lm_name__"
_LLM_TEMP_KEY = "__llm_temperature__"
_LLM_TOKENS_KEY = "__llm_max_tokens__"
_LLM_SYS_KEY = "__llm_system_prompt__"
_LLM_USR_KEY = "__llm_user_prompt__"
_LLM_RESERVED = frozenset({
    _LLM_LM_KEY, _LLM_TEMP_KEY, _LLM_TOKENS_KEY, _LLM_SYS_KEY, _LLM_USR_KEY,
})


@dataclass
class RosterEntry:
    """One roster line in the customized market lineup.

    Attributes:
        id: Stable opaque identifier (``"e_<uuid4-hex[:8]>"``).  Used to
            scope Streamlit widget keys and to survive list reordering.
        agent_type: Archetype id (matches ``agent_catalog`` and the profile
            filename stem, e.g. ``"NoiseTrader"``).
        engine: Decision engine (``"Rule"``, ``"LLM"``, ``"RuleLLM"``,
            ``"Rag"``).
        num_instances: How many copies of this configured agent to spawn
            when the bundle is written.
        params: Handbook ``symbol → value`` map. May also contain the
            reserved ``__llm_*__`` sentinels — the bundle writer routes
            those into ``extras.llm`` and ``prompts.py``.
        label: Optional human-friendly nickname for the entry ("Aggressive",
            "Cautious", …).  When present the UI shows it beside the
            archetype name; otherwise falls back to a positional badge
            like "#2".
    """

    id: str
    agent_type: str
    engine: str
    num_instances: int = 1
    params: dict[str, Any] = field(default_factory=dict)
    label: Optional[str] = None

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """JSON-serialisable representation for persistence."""
        return {
            "id": self.id,
            "agent_type": self.agent_type,
            "engine": self.engine,
            "num_instances": int(self.num_instances),
            "params": dict(self.params),
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RosterEntry":
        """Rebuild an entry from disk. Missing fields fall back to defaults."""
        eid = str(data.get("id") or new_entry_id())
        agent_type = str(data.get("agent_type", "") or "")
        engine = str(data.get("engine", "Rule") or "Rule")
        try:
            ninst = int(data.get("num_instances", 1) or 1)
        except (TypeError, ValueError):
            ninst = 1
        if ninst < 1:
            ninst = 1
        raw_params = data.get("params") or {}
        params = dict(raw_params) if isinstance(raw_params, dict) else {}
        label = data.get("label")
        if label is not None:
            label = str(label)
        return cls(
            id=eid,
            agent_type=agent_type,
            engine=engine,
            num_instances=ninst,
            params=params,
            label=label,
        )


# ----------------------------------------------------------------------
# ID generation
# ----------------------------------------------------------------------


def new_entry_id() -> str:
    """Return a fresh short opaque entry id (``"e_" + 8 hex chars``)."""
    return "e_" + uuid.uuid4().hex[:8]


# ----------------------------------------------------------------------
# List operations (pure functions over a list[RosterEntry])
# ----------------------------------------------------------------------


def add_entry(
    entries: list[RosterEntry],
    *,
    agent_type: str,
    engine: str = "Rule",
    num_instances: int = 1,
    params: Optional[dict[str, Any]] = None,
    label: Optional[str] = None,
) -> RosterEntry:
    """Append a fresh entry and return it.

    Mutates ``entries`` in place so the caller can save the same list
    reference back to ``st.session_state``.  The new entry receives a
    unique :func:`new_entry_id`.
    """
    entry = RosterEntry(
        id=new_entry_id(),
        agent_type=agent_type,
        engine=engine,
        num_instances=max(1, int(num_instances) if num_instances else 1),
        params=dict(params or {}),
        label=label,
    )
    entries.append(entry)
    return entry


def remove_entry(entries: list[RosterEntry], entry_id: str) -> bool:
    """Delete the entry with ``entry_id``.

    Returns ``True`` when a match was found and removed, else ``False``.
    Missing ids are silently ignored so double-clicks from Streamlit's
    rerun cycle cannot raise.
    """
    for i, e in enumerate(entries):
        if e.id == entry_id:
            entries.pop(i)
            return True
    return False


def duplicate_entry(
    entries: list[RosterEntry], entry_id: str
) -> Optional[RosterEntry]:
    """Insert a fresh entry immediately after ``entry_id`` with copied fields.

    The clone receives a new id (so widget state stays scoped) and — when
    a label is set — a ``" (copy)"`` suffix so the two entries are
    visually distinguishable in the roster list.  Returns the new entry
    on success or ``None`` when the source id is unknown.
    """
    for i, src in enumerate(entries):
        if src.id != entry_id:
            continue
        clone_label: Optional[str]
        if src.label:
            clone_label = f"{src.label} (copy)"
        else:
            clone_label = None
        clone = RosterEntry(
            id=new_entry_id(),
            agent_type=src.agent_type,
            engine=src.engine,
            num_instances=int(src.num_instances),
            params=dict(src.params),
            label=clone_label,
        )
        entries.insert(i + 1, clone)
        return clone
    return None


def update_entry(
    entries: list[RosterEntry],
    entry_id: str,
    **fields: Any,
) -> Optional[RosterEntry]:
    """Update the named fields of ``entry_id``.

    Accepts any subset of ``engine``, ``num_instances``, ``params`` and
    ``label``.  ``agent_type`` and ``id`` are immutable by design — to
    change the archetype the caller should remove and re-add.  Returns
    the mutated entry, or ``None`` when the id is unknown.
    """
    for e in entries:
        if e.id != entry_id:
            continue
        if "engine" in fields:
            new_eng = fields["engine"]
            if new_eng:
                e.engine = str(new_eng)
        if "num_instances" in fields:
            try:
                ninst = int(fields["num_instances"] or 1)
            except (TypeError, ValueError):
                ninst = 1
            e.num_instances = max(1, ninst)
        if "params" in fields:
            raw = fields["params"] or {}
            if isinstance(raw, dict):
                e.params = dict(raw)
        if "label" in fields:
            lbl = fields["label"]
            e.label = None if lbl in (None, "") else str(lbl)
        return e
    return None


def find_entry(
    entries: list[RosterEntry], entry_id: str
) -> Optional[RosterEntry]:
    """Return the entry matching ``entry_id`` or ``None``."""
    for e in entries:
        if e.id == entry_id:
            return e
    return None


def entries_for_type(
    entries: Iterable[RosterEntry], agent_type: str
) -> list[RosterEntry]:
    """Return every entry whose ``agent_type`` matches (list order preserved)."""
    return [e for e in entries if e.agent_type == agent_type]


def unique_agent_types(entries: Iterable[RosterEntry]) -> list[str]:
    """Distinct archetypes referenced by the roster, in first-seen order."""
    seen: dict[str, None] = {}
    for e in entries:
        seen.setdefault(e.agent_type, None)
    return list(seen.keys())


def total_instances(
    entries: Iterable[RosterEntry], agent_type: Optional[str] = None
) -> int:
    """Sum ``num_instances`` across entries (optionally filtered by type)."""
    return sum(
        int(e.num_instances)
        for e in entries
        if agent_type is None or e.agent_type == agent_type
    )


# ----------------------------------------------------------------------
# Migration from legacy (v1 / v2) session-state and disk formats
# ----------------------------------------------------------------------


def migrate_from_legacy_state(
    *,
    selected_agents: Iterable[str],
    engines: dict[str, str],
    num_instances: dict[str, int],
    params: dict[str, dict[str, dict[str, Any]]],
) -> list[RosterEntry]:
    """Produce a roster from the flat legacy session-state fields.

    Each archetype in ``selected_agents`` becomes exactly one entry.
    The entry's params come from ``params[type][engine]`` when present
    (empty dict otherwise), and the engine / instance count come from
    their respective per-archetype maps.

    This function is deliberately idempotent: passing already-migrated
    input twice produces the same list of two-entry-per-archetype
    output only if the caller also duplicated the flat state (which is
    not something the UI ever does).  Callers should invoke migration
    exactly once, at the point where the legacy state is read for the
    first time.
    """
    entries: list[RosterEntry] = []
    for agent_type in selected_agents:
        if not agent_type:
            continue
        engine = str(engines.get(agent_type, "Rule") or "Rule")
        try:
            ninst = int(num_instances.get(agent_type, 1) or 1)
        except (TypeError, ValueError):
            ninst = 1
        if ninst < 1:
            ninst = 1
        per_engine = (params or {}).get(agent_type, {}) or {}
        entry_params = per_engine.get(engine, {}) or {}
        entries.append(
            RosterEntry(
                id=new_entry_id(),
                agent_type=agent_type,
                engine=engine,
                num_instances=ninst,
                params=dict(entry_params),
                label=None,
            )
        )
    return entries


def entries_to_dicts(entries: Iterable[RosterEntry]) -> list[dict[str, Any]]:
    """Serialise a roster for JSON persistence."""
    return [e.to_dict() for e in entries]


def entries_from_dicts(data: Iterable[dict[str, Any]]) -> list[RosterEntry]:
    """Rebuild a roster from JSON-loaded dicts, skipping malformed items."""
    out: list[RosterEntry] = []
    for item in data or []:
        if not isinstance(item, dict):
            continue
        if not item.get("agent_type"):
            continue
        out.append(RosterEntry.from_dict(item))
    return out


# ----------------------------------------------------------------------
# Streamlit session-state helpers
# ----------------------------------------------------------------------


def get_roster(session_state: Any) -> list[RosterEntry]:
    """Return the live roster list from ``st.session_state``.

    Ensures the slot is a ``list[RosterEntry]`` — silently coerces
    JSON-loaded dicts (e.g. after a page refresh) and clears the slot
    when a stale type slips through.  Callers should treat the returned
    list as mutable and write back to the same slot only when they
    replace the reference (not required for in-place ``append`` / ``pop``).
    """
    raw = session_state.get(ROSTER_KEY)
    if raw is None:
        session_state[ROSTER_KEY] = []
        return session_state[ROSTER_KEY]
    if isinstance(raw, list):
        # Coerce dicts (persisted form) to RosterEntry lazily so a fresh
        # session that loaded state before the ROSTER_KEY was normalised
        # doesn't crash the first render.
        coerced: list[RosterEntry] = []
        needs_replace = False
        for item in raw:
            if isinstance(item, RosterEntry):
                coerced.append(item)
            elif isinstance(item, dict):
                coerced.append(RosterEntry.from_dict(item))
                needs_replace = True
            else:
                needs_replace = True  # drop garbage
        if needs_replace:
            session_state[ROSTER_KEY] = coerced
            return coerced
        return raw  # type: ignore[return-value]
    # Unknown type — reset to an empty list defensively.
    session_state[ROSTER_KEY] = []
    return session_state[ROSTER_KEY]


def set_roster(session_state: Any, entries: list[RosterEntry]) -> None:
    """Replace the entire roster (used by restore & bulk operations)."""
    session_state[ROSTER_KEY] = list(entries)


def clear_roster(session_state: Any) -> None:
    """Drop every entry (Clear-selection button)."""
    session_state[ROSTER_KEY] = []
