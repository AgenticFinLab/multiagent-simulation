"""Persistent selection state for customized simulation bundles.

Serialises the user's agent selections, per-agent parameters, engine
choices, and LLM prompt overrides into a ``selection_state.json`` file
inside the bundle's *configs* directory. On re-entry (e.g. after a page
refresh or app restart), the state can be loaded back into
``st.session_state`` to restore the UI exactly where the user left off.

Schema (v1):
    {
        "version": 1,
        "scenario": "<ScenarioBase>",
        "bundle_name": "<slug-id-scenario>",
        "updated_at": "<ISO-8601>",
        "selected_agents": ["AgentType1", "AgentType2", ...],
        "engines": {"AgentType1": "LLM", "AgentType2": "Rule", ...},
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
"""

from __future__ import annotations

import datetime as _dt
import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

_STATE_FILENAME = "selection_state.json"
_SCHEMA_VERSION = 1


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
    )


def restore_state_to_session(
    *,
    bundle_name: str,
    project_root: Path,
) -> bool:
    """Load persisted state and inject it into ``st.session_state``.

    Returns:
        ``True`` if state was successfully restored, ``False`` otherwise.
    """
    import streamlit as st

    data = load_selection_state(bundle_name=bundle_name, project_root=project_root)
    if data is None:
        return False

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

    # Restore customized params.
    params = data.get("params", {})
    if params:
        st.session_state["customized_params"] = params

    # Restore market extras (future use).
    market_extras = data.get("market_extras")
    if market_extras:
        st.session_state["customized_market_extras"] = market_extras

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
