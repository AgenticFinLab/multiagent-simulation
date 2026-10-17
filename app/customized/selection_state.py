"""Persistent selection state for customized simulation bundles.

Serialises the user's agent selections, per-agent parameters, engine
choices, and LLM prompt overrides into a ``selection_state.json`` file
inside the bundle's *configs* directory. On re-entry (e.g. after a page
refresh or app restart), the state can be loaded back into
``st.session_state`` to restore the UI exactly where the user left off.

Schema (v3 — roster_entries model; forward-compatible with v1 / v2):
    {
        "version": 3,
        "scenario": "<ScenarioBase>",
        "bundle_name": "<slug-id-scenario>",
        "updated_at": "<ISO-8601>",
        "roster_entries": [
            {
                "id": "e_ab12cd34",
                "agent_type": "NoiseTrader",
                "engine": "LLM",
                "num_instances": 3,
                "params": {"symbol1": value1, ...},
                "label": "Aggressive"
            },
            ...
        ],
        "total_rounds": 25,
        "market_extras": {
            "fundamental_value": 100.0,
            ...
        }
    }

Older files (v1 / v2) carry the flat ``selected_agents`` /
``engines`` / ``num_instances`` / ``params`` map instead of
``roster_entries``.  When those are loaded we transparently migrate to
the entry model — one entry per archetype with the previously-single
(engine, params, num_instances) tuple.
"""

from __future__ import annotations

import datetime as _dt
import json
import logging
from pathlib import Path
from typing import Any, Optional

from .roster import (
    RosterEntry,
    entries_from_dicts,
    entries_to_dicts,
    migrate_from_legacy_state,
)

logger = logging.getLogger(__name__)

_STATE_FILENAME = "selection_state.json"
_SCHEMA_VERSION = 3


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def save_selection_state(
    *,
    bundle_name: str,
    scenario_name: str,
    project_root: Path,
    roster_entries: list[RosterEntry],
    total_rounds: Optional[int] = None,
    market_extras: Optional[dict[str, Any]] = None,
) -> Path:
    """Persist the current UI selection state to disk.

    Args:
        bundle_name: bundle folder name (e.g. ``"myproj-a1b2c3d4-AnchoringEffect"``).
        scenario_name: locked scenario base name.
        project_root: the repo root (parent of ``configs/``).
        roster_entries: full list of :class:`RosterEntry` instances that
            represent the current roster (one entry per YAML block).
        total_rounds: optional edited round count from the variant-rounds
            widget. When ``None`` the scenario's shipped default applies.
        market_extras: optional market parameter overrides.

    Returns:
        Path to the written JSON file.
    """
    config_dir = (
        Path(project_root).resolve()
        / "configs"
        / "CUSTOMIZED_SIMULATION"
        / bundle_name
    )
    config_dir.mkdir(parents=True, exist_ok=True)
    out_path = config_dir / _STATE_FILENAME

    payload: dict[str, Any] = {
        "version": _SCHEMA_VERSION,
        "scenario": scenario_name,
        "bundle_name": bundle_name,
        "updated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "roster_entries": _sanitize_entries(entries_to_dicts(roster_entries)),
    }
    if total_rounds is not None:
        try:
            payload["total_rounds"] = int(total_rounds)
        except (TypeError, ValueError):
            pass
    if market_extras:
        payload["market_extras"] = dict(market_extras)

    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    logger.debug("Selection state saved → %s", out_path)
    return out_path


def load_selection_state(
    *,
    bundle_name: str,
    project_root: Path,
) -> Optional[dict[str, Any]]:
    """Load a previously persisted selection state from disk.

    Returns:
        The parsed state dict, or ``None`` if the file does not exist or
        is malformed.  The dict always carries a ``roster_entries`` key
        after normalisation, even when the on-disk file was v1 / v2 —
        migration happens transparently here.
    """
    config_dir = (
        Path(project_root).resolve()
        / "configs"
        / "CUSTOMIZED_SIMULATION"
        / bundle_name
    )
    state_path = config_dir / _STATE_FILENAME
    if not state_path.exists():
        return None

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to load selection state from %s: %s", state_path, exc)
        return None

    # Basic version check — future versions may need migration.
    version = data.get("version", 0)
    if version > _SCHEMA_VERSION:
        logger.warning(
            "selection_state.json version %d is newer than supported (%d); "
            "loading anyway but some fields may be ignored.",
            version,
            _SCHEMA_VERSION,
        )

    # Normalise to v3 shape: ensure `roster_entries` is always present.
    if "roster_entries" not in data:
        legacy_entries = migrate_from_legacy_state(
            selected_agents=data.get("selected_agents") or [],
            engines=data.get("engines") or {},
            num_instances=data.get("num_instances") or {},
            params=data.get("params") or {},
        )
        data["roster_entries"] = entries_to_dicts(legacy_entries)
        data["_migrated_from_version"] = version

    return data


def delete_selection_state(
    *,
    bundle_name: str,
    project_root: Path,
) -> None:
    """Remove the selection state file (e.g. after a successful launch)."""
    config_dir = (
        Path(project_root).resolve()
        / "configs"
        / "CUSTOMIZED_SIMULATION"
        / bundle_name
    )
    state_path = config_dir / _STATE_FILENAME
    if state_path.exists():
        state_path.unlink()
        logger.debug("Selection state deleted: %s", state_path)


# ----------------------------------------------------------------------
# Streamlit integration helpers
# ----------------------------------------------------------------------


def save_state_from_session(
    *,
    project_root: Path,
) -> Optional[Path]:
    """Extract relevant keys from ``st.session_state`` and persist.

    Reads the v3 ``roster_entries`` slot as the source of truth.  Also
    carries the scenario-keyed rounds widget and the market-extras
    overrides through unchanged.

    Returns:
        Path to the written file, or ``None`` if no bundle is active.
    """
    import streamlit as st

    from .roster import get_roster

    bundle_name = st.session_state.get("customized_bundle_name", "")
    scenario_name = st.session_state.get("selected_scenario_base", "")
    if not bundle_name or not scenario_name:
        return None

    roster = list(get_roster(st.session_state))

    # Collect the (possibly edited) round count driving this run. The
    # variant-rounds widget is keyed by scenario base — pull that first.
    total_rounds_val: Optional[int] = None
    rounds_raw = st.session_state.get(f"variant_rounds_{scenario_name}")
    if rounds_raw is None:
        rounds_raw = st.session_state.get("customized_total_rounds")
    if rounds_raw is not None:
        try:
            total_rounds_val = int(rounds_raw)
        except (TypeError, ValueError):
            total_rounds_val = None

    # Market extras (populated by the Market Parameters editor).
    market_extras: Optional[dict[str, Any]] = st.session_state.get(
        "customized_market_extras"
    )

    return save_selection_state(
        bundle_name=bundle_name,
        scenario_name=scenario_name,
        project_root=project_root,
        roster_entries=roster,
        total_rounds=total_rounds_val,
        market_extras=market_extras,
    )


def restore_state_to_session(
    *,
    bundle_name: str,
    project_root: Path,
) -> bool:
    """Load persisted state and inject it into ``st.session_state``.

    Clears any stale roster / legacy widget keys before restoring, so
    entries or archetype selections that are no longer in the saved state
    don't linger as ghost state.

    Returns:
        ``True`` if state was successfully restored, ``False`` otherwise.
    """
    import streamlit as st

    from .roster import ROSTER_KEY, set_roster

    data = load_selection_state(bundle_name=bundle_name, project_root=project_root)
    if data is None:
        return False

    # ── Clear stale per-archetype legacy widget keys before restoring ────
    # These once encoded the flat (archetype→engine, archetype→params …)
    # map. Now everything lives on the entry itself so we scrub them so
    # they cannot leak stale defaults into new widgets.
    stale_keys = [
        k for k in list(st.session_state.keys())
        if k.startswith("market_agent_")
        or k.startswith("market_engine_")
        or k.startswith("customized_num_instances_")
        or k.startswith("customized_input_")
        or k.startswith("customized_llm_")
        or k.startswith("entry_")  # scoped widget keys from previous session
    ]
    for k in stale_keys:
        try:
            del st.session_state[k]
        except KeyError:
            pass
    # Also drop the flat legacy customized_params dict — its content lives
    # inside each RosterEntry.params now.
    st.session_state.pop("customized_params", None)

    # ── Restore bundle/scenario context keys ───────────────────────────
    st.session_state["customized_bundle_name"] = data.get("bundle_name", bundle_name)
    if data.get("scenario"):
        st.session_state["selected_scenario_base"] = data["scenario"]

    # ── Restore the roster ───────────────────────────────────────────────
    entries = entries_from_dicts(data.get("roster_entries") or [])
    set_roster(st.session_state, entries)
    # Mirror the derived list of distinct agent_types (some legacy call
    # sites still read this — see the top-level catalog previews).
    seen: dict[str, None] = {}
    for e in entries:
        seen.setdefault(e.agent_type, None)
    st.session_state["selected_market_agents"] = list(seen.keys())

    # Restore the edited round count. We seed both the scenario-keyed
    # widget key AND the generic mirror, so whichever the customize page
    # reads on the next rerun sees the same value.
    total_rounds_val = data.get("total_rounds")
    scenario_name = data.get("scenario") or ""
    if total_rounds_val is not None:
        try:
            rounds_int = int(total_rounds_val)
        except (TypeError, ValueError):
            rounds_int = None
        if rounds_int is not None and rounds_int >= 1:
            if scenario_name:
                st.session_state[f"variant_rounds_{scenario_name}"] = rounds_int
            st.session_state["customized_total_rounds"] = rounds_int

    # Restore market extras.
    market_extras = data.get("market_extras")
    if market_extras is not None:
        st.session_state["customized_market_extras"] = market_extras
    else:
        st.session_state.pop("customized_market_extras", None)

    logger.debug(
        "Selection state restored for bundle '%s': %d entries (v%s)",
        bundle_name,
        len(entries),
        data.get("version", "?"),
    )
    _ = ROSTER_KEY  # silence unused import warning when reading state elsewhere
    return True


# ----------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------


def _sanitize_entries(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Ensure every param value in every entry is JSON-serialisable.

    Simple scalars pass through untouched; lists / dicts pass through
    (json.dump handles them); everything else is coerced to ``str`` so a
    stray numpy scalar or Path cannot break persistence.
    """
    clean: list[dict[str, Any]] = []
    for entry in entries:
        params = entry.get("params") or {}
        cleaned_params: dict[str, Any] = {}
        for symbol, value in params.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                cleaned_params[symbol] = value
            elif isinstance(value, (list, dict)):
                cleaned_params[symbol] = value
            else:
                cleaned_params[symbol] = str(value)
        clean.append({**entry, "params": cleaned_params})
    return clean
