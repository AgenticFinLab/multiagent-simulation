"""Loader for ``scenario_features.yml`` plus the roster compatibility check.

The Customized Simulation Builder Step 2 uses this module to:

1. Disable scenario cards whose declared ``market_features`` cannot satisfy
   the union of ``requires_market_features`` across the user's selected
   roster.
2. Surface a precise reason for each disabled scenario (which agent triggered
   the restriction and which feature is missing).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable, Optional

import yaml

from .agent_catalog import required_features


_FEATURES_PATH = Path(__file__).resolve().parent / "scenario_features.yml"


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def load_scenario_features(path: Optional[str] = None) -> dict[str, set[str]]:
    """Return ``{scenario: {market_feature, ...}}``.

    Scenarios omitted from the YAML are treated as having an empty feature
    set (i.e. standard market state only).
    """
    target = Path(path) if path else _FEATURES_PATH
    if not target.exists():
        return {}
    raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        return {}

    out: dict[str, set[str]] = {}
    for scenario, body in raw.items():
        features: list[str] = []
        if isinstance(body, dict):
            mf = body.get("market_features") or []
            if isinstance(mf, (list, tuple)):
                features = [str(f) for f in mf]
        out[str(scenario)] = set(features)
    return out


def scenario_market_features(scenario: str) -> set[str]:
    """Return the feature set of ``scenario`` (empty set when unlisted)."""
    return set(load_scenario_features().get(scenario, set()))


# ---------------------------------------------------------------------------
# Compatibility check
# ---------------------------------------------------------------------------


def is_scenario_compatible(
    scenario: str,
    roster: Iterable[str],
) -> tuple[bool, list[str]]:
    """Return ``(is_compatible, reasons)`` for a roster against a scenario.

    ``roster`` is an iterable of archetype names (e.g.
    ``["NoiseTrader", "AnchoringBiasInvestor"]``). The check passes when every
    archetype's ``requires_market_features`` set is a subset of the scenario's
    ``market_features``. ``reasons`` lists each blocking pair as a
    human-readable string; the list is empty on success.
    """
    provided = scenario_market_features(scenario)
    reasons: list[str] = []
    for archetype in roster:
        needed = set(required_features(archetype))
        missing = needed - provided
        if missing:
            features = ", ".join(f"`{f}`" for f in sorted(missing))
            reasons.append(
                f"{archetype} needs {features} which {scenario} does not provide"
            )
    return (not reasons), reasons


__all__ = [
    "load_scenario_features",
    "scenario_market_features",
    "is_scenario_compatible",
]
