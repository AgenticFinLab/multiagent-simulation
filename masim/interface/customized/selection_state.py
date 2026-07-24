"""Persistent selection state for customized simulation bundles.

Serialises the user's agent selections, per-agent parameters, engine
choices, and LLM prompt overrides into a ``selection_state.json`` file
inside the bundle's *configs* directory. On re-entry (e.g. after a page
refresh or app restart), the state can be loaded back into
``st.session_state`` to restore the UI exactly where the user left off.

Schema (v2 — backward-compatible with v1):
    {
        "version": 2,
        "scenario": "<ScenarioBase>",
        "bundle_name": "<slug-id-scenario>",
        "updated_at": "<ISO-8601>",
        "selected_agents": ["AgentType1", "AgentType2", ...],
        "engines": {"AgentType1": "LLM", "AgentType2": "Rule", ...},
        "num_instances": {"AgentType1": 3, "AgentType2": 1, ...},
        "total_rounds": 25,
        "params": {
            "AgentType1": {
                "LLM": {"symbol1": value1, "symbol2": value2, ...}
            },
            ...
        },
        "market_extras": {
            "fundamental_value": 100.0,
            ...
        }
    }

The v2 additions ``num_instances`` (per-agent instance counts) and
``total_rounds`` (variant-rounds widget) ensure that the on-disk state
truly captures what the user configured. Without them, a page refresh
would silently reset instance counts to 1 and rounds to the scenario
default even though the shipped players.yml recorded the correct values.
"""

from __future__ import annotations

import datetime as _dt
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_STATE_FILENAME = "selection_state.json"
_SCHEMA_VERSION = 2


# ----------------------------------------------------------------------
# Public API
# ----------------------------------------------------------------------


def save_selection_state(
    *,
    bundle_name: str,
    scenario_name: str,
    project_root: Path,
    selected_agents: list[str],
    engines: dict[str, str],
    params: dict[str, dict[str, dict[str, Any]]],
    market_extras: Optional[dict[str, Any]] = None,
    num_instances: Optional[dict[str, int]] = None,
    total_rounds: Optional[int] = None,
) -> Path:
    """Persist the current UI selection state to disk.

    Args:
        bundle_name: bundle folder name (e.g. ``"myproj-a1b2c3d4-AnchoringEffect"``).
        scenario_name: locked scenario base name.
        project_root: the repo root (parent of ``configs/``).
        selected_agents: list of selected agent_type strings.
        engines: mapping of agent_type → chosen engine string.
        params: nested dict: ``{agent_type: {engine: {symbol: value}}}``.
        market_extras: optional market parameter overrides.
        num_instances: optional mapping of agent_type → integer instance
            count. Values ≤0 or missing entries default to 1 on restore.
        total_rounds: optional edited round count from the variant-rounds
            widget. When ``None`` the scenario's shipped default applies.

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
        "selected_agents": list(selected_agents),
        "engines": dict(engines),
        "params": _sanitize_params(params),
    }
    if market_extras:
        payload["market_extras"] = dict(market_extras)
    if num_instances:
        # Persist only positive integer overrides — silently drop entries
        # for agents that are no longer selected so the state file stays
        # tightly aligned with ``selected_agents``.
        cleaned_instances: dict[str, int] = {}
        for agent_type in selected_agents:
            raw = num_instances.get(agent_type)
            if raw is None:
                continue
            try:
                value = int(raw)
            except (TypeError, ValueError):
                continue
            if value >= 1:
                cleaned_instances[agent_type] = value
        if cleaned_instances:
            payload["num_instances"] = cleaned_instances
    if total_rounds is not None:
        try:
            payload["total_rounds"] = int(total_rounds)
        except (TypeError, ValueError):
            pass

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
        is malformed.
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

    This is a convenience wrapper intended to be called from the UI layer.
    It reads the canonical session state keys used by the customize page
    and delegates to :func:`save_selection_state`.

    Returns:
        Path to the written file, or ``None`` if no bundle is active.
    """
    import streamlit as st

    bundle_name = st.session_state.get("customized_bundle_name", "")
    scenario_name = st.session_state.get("selected_scenario_base", "")
    if not bundle_name or not scenario_name:
        return None

    # Collect selected agent types.
    selected_agents: list[str] = list(
        st.session_state.get("selected_market_agents", [])
    )

    # Collect per-agent engine selections.
    engines: dict[str, str] = {}
    for agent_type in selected_agents:
        engine_key = f"market_engine_{agent_type}"
        engines[agent_type] = st.session_state.get(engine_key, "Rule")

    # Collect per-agent instance counts (spinner widget). Missing / non-
    # numeric values simply fall back to 1 on restore, so we don't need to
    # emit a value when the widget hasn't been touched.
    num_instances: dict[str, int] = {}
    for agent_type in selected_agents:
        raw = st.session_state.get(f"customized_num_instances_{agent_type}")
        if raw is None:
            continue
        try:
            value = int(raw)
        except (TypeError, ValueError):
            continue
        if value >= 1:
            num_instances[agent_type] = value

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

    # Collect customized params (nested dict from the customize dialog).
    params: dict[str, dict[str, dict[str, Any]]] = dict(
        st.session_state.get("customized_params", {})
    )

    # Market extras (to be populated when market editing is implemented).
    market_extras: Optional[dict[str, Any]] = st.session_state.get(
        "customized_market_extras"
    )

    return save_selection_state(
        bundle_name=bundle_name,
        scenario_name=scenario_name,
        project_root=project_root,
        selected_agents=selected_agents,
        engines=engines,
        params=params,
        market_extras=market_extras,
        num_instances=num_instances,
        total_rounds=total_rounds_val,
    )


def restore_state_to_session(
    *,
    bundle_name: str,
    project_root: Path,
) -> bool:
    """Load persisted state and inject it into ``st.session_state``.

    Clears any stale ``market_agent_*`` and ``market_engine_*`` keys
    before restoring, so previously-selected agents that are no longer
    in the saved state don't linger as ghost selections.

    Returns:
        ``True`` if state was successfully restored, ``False`` otherwise.
    """
    import streamlit as st

    data = load_selection_state(bundle_name=bundle_name, project_root=project_root)
    if data is None:
        return False

    # ── Clear stale per-agent keys before restoring ──────────────────────
    stale_keys = [
        k for k in list(st.session_state.keys())
        if k.startswith("market_agent_")
        or k.startswith("market_engine_")
        or k.startswith("customized_num_instances_")
    ]
    for k in stale_keys:
        del st.session_state[k]

    # ── Restore bundle/scenario context keys ───────────────────────────
    # These are required by save_state_from_session; without them a
    # clear()+restore cycle leaves the session unable to persist again.
    st.session_state["customized_bundle_name"] = data.get("bundle_name", bundle_name)
    if data.get("scenario"):
        st.session_state["selected_scenario_base"] = data["scenario"]

    # Restore selected agents.
    selected_agents = data.get("selected_agents", [])
    st.session_state["selected_market_agents"] = list(selected_agents)

    # Restore per-agent checkbox state (so the grid shows them as checked).
    for agent_type in selected_agents:
        st.session_state[f"market_agent_{agent_type}"] = True

    # Restore engine selections.
    engines = data.get("engines", {})
    for agent_type, engine in engines.items():
        st.session_state[f"market_engine_{agent_type}"] = engine

    # Restore per-agent instance counts (v2+). Absent entries default to 1
    # so old v1 state files simply behave as they did before.
    num_instances = data.get("num_instances", {}) or {}
    for agent_type in selected_agents:
        raw = num_instances.get(agent_type, 1)
        try:
            value = int(raw)
        except (TypeError, ValueError):
            value = 1
        if value < 1:
            value = 1
        st.session_state[f"customized_num_instances_{agent_type}"] = value

    # Restore the edited round count (v2+). We seed both the scenario-
    # keyed widget key AND the generic mirror, so whichever the customize
    # page reads on the next rerun will see the same value.
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

    # Restore customized params.
    params = data.get("params", {})
    if params:
        st.session_state["customized_params"] = params

    # Restore market extras.
    market_extras = data.get("market_extras")
    if market_extras is not None:
        st.session_state["customized_market_extras"] = market_extras
    else:
        st.session_state.pop("customized_market_extras", None)

    logger.debug(
        "Selection state restored for bundle '%s': %d agents",
        bundle_name,
        len(selected_agents),
    )
    return True


# ----------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------


def _sanitize_params(
    params: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """Ensure all param values are JSON-serializable."""
    clean: dict[str, dict[str, dict[str, Any]]] = {}
    for agent_type, engine_dict in params.items():
        clean[agent_type] = {}
        for engine, symbol_dict in engine_dict.items():
            clean[agent_type][engine] = {}
            for symbol, value in symbol_dict.items():
                # Convert non-serializable types to their string form.
                if isinstance(value, (str, int, float, bool, type(None))):
                    clean[agent_type][engine][symbol] = value
                elif isinstance(value, (list, dict)):
                    clean[agent_type][engine][symbol] = value
                else:
                    clean[agent_type][engine][symbol] = str(value)
    return clean
