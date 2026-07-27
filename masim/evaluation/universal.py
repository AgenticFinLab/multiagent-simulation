"""Universal Metric Aggregator — the Layer A entry point for scenario analysis.

This module is the single call every scenario's ``analysis.py`` MUST invoke
to satisfy Polish Hook 9 (universal-baseline coverage) declared in
``masim/skills/polish-simulation-pipeline.md §8.3``.

It runs the full 36-metric registered baseline (``STANDARD_METRICS``) from
``masim.evaluation.finance``, groups the results by category, writes a
schema-conformant ``summary.json`` block, and produces the four universal
PNG dashboards defined by the ``masim.evaluation.pipeline`` visualization
contract.

Design principles:

- Fail loud on structural problems (missing config, unwritable output dir).
- Fail soft on missing data fields (records ``_unavailable`` per metric via
  the registry's ``MetricUnavailable`` machinery — this is how the coverage
  floor gets counted).
- Never mutate the caller's data dict.
- Return the summary dict so scenario ``analysis.py`` can extend it with
  Layer B (scenario) and Layer C (variant) blocks before writing the final
  file.

Public entry points
-------------------

- :func:`compute_universal_metrics` — pure computation; returns the
  ``universal_metrics`` sub-tree without touching disk.
- :func:`write_universal_summary` — full contract: computes metrics,
  emits the four universal PNGs, writes ``summary.json`` (or merges into
  an existing dict), and returns the merged summary.

Anchor
------

See ``masim/skills/polish-simulation-pipeline.md §8.6`` for the three-layer
metric taxonomy (Layer A universal / Layer B scenario / Layer C variant).
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Dict, List, Mapping, Optional, Tuple

from masim.evaluation.finance import (
    STANDARD_METRICS,
    register_standard_metrics,
)
from masim.evaluation.pipeline import create_standard_visualizations
from masim.evaluation.registry import MetricsRegistry


# ---------------------------------------------------------------------------
# Category ordering — mirrors the Hook 9 schema and §8.6 Layer A tables.
# ---------------------------------------------------------------------------

CATEGORY_ORDER: Tuple[str, ...] = (
    "price_dynamics",
    "information_efficiency",
    "statistical_inference",
    "tail_risk",
    "agent_behaviour",
    "microstructure",
)


def _build_registry() -> MetricsRegistry:
    """Build a fresh registry loaded with all 36 standard metrics."""
    registry = MetricsRegistry()
    register_standard_metrics(registry)
    return registry


def _config_hash(config: Mapping[str, Any]) -> str:
    """Return a short deterministic hash of the config dict."""
    canonical = json.dumps(config, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()[:12]


def _group_by_category(
    raw_metrics: Dict[str, Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """Group raw ``{metric_name: result}`` output by the metric's category.

    Uses ``STANDARD_METRICS`` as the source of truth for the category lookup
    so that the returned dict's category key ordering is deterministic and
    matches §8.6 Layer A.
    """
    by_name = {m.name: m for m in STANDARD_METRICS}
    grouped: Dict[str, Dict[str, Any]] = {cat: {} for cat in CATEGORY_ORDER}
    for metric_name, result in raw_metrics.items():
        metric = by_name.get(metric_name)
        if metric is None:
            # Unknown metric — put it in a synthetic bucket rather than drop it.
            grouped.setdefault("_other", {})[metric_name] = result
            continue
        grouped[metric.category][metric_name] = result
    return grouped


def _coverage_stats(
    raw_metrics: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Count numeric-vs-unavailable-vs-error results for the coverage floor."""
    n_numeric = 0
    n_unavailable = 0
    n_error = 0
    unavailable_names: List[str] = []
    error_names: List[str] = []
    for name, result in raw_metrics.items():
        if not isinstance(result, dict):
            n_numeric += 1
            continue
        if "_unavailable" in result:
            n_unavailable += 1
            unavailable_names.append(name)
        elif "_error" in result:
            n_error += 1
            error_names.append(name)
        else:
            n_numeric += 1
    return {
        "n_registered": len(raw_metrics),
        "n_numeric": n_numeric,
        "n_unavailable": n_unavailable,
        "n_error": n_error,
        "coverage_floor_met": n_numeric >= 20,
        "unavailable_metrics": unavailable_names,
        "error_metrics": error_names,
    }


def _collect_references() -> Dict[str, List[str]]:
    """Return ``{metric_name: [reference, ...]}`` for the 36 Layer A metrics."""
    return {m.name: list(m.references) for m in STANDARD_METRICS}


def _series_to_round_dict(series: Any) -> Dict[int, float]:
    """Convert a list/tuple series to ``{round: value}`` (1-indexed).

    Returns an empty dict if the input isn't a list/tuple/mapping at all.
    Raises ``ValueError`` if the input HAS a list/mapping shape but its
    values cannot be coerced to ``(int, float)`` — silently swallowing this
    used to hide scenario-level bugs (e.g. NaN-string values) and cause
    metrics to be reported as ``_unavailable`` when they should be
    ``_error``.
    """
    if isinstance(series, Mapping):
        try:
            return {int(k): float(v) for k, v in series.items()}
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"_series_to_round_dict: mapping has non-numeric values: {exc}"
            ) from exc
    if isinstance(series, (list, tuple)):
        out: Dict[int, float] = {}
        for i, v in enumerate(series):
            try:
                out[i + 1] = float(v)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"_series_to_round_dict: index {i} value {v!r} is not "
                    f"numeric: {exc}"
                ) from exc
        return out
    return {}


def _normalize_data(data: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a shallow copy of ``data`` with canonical financial series shapes.

    Scenario analysis modules disagree on the shape of price/fundamental/volume
    series (some emit a ``{round: value}`` dict, others a plain list). This
    helper promotes common alternatives into the canonical dict form so that
    :func:`compute_universal_metrics` and
    :func:`~masim.evaluation.pipeline.create_standard_visualizations` can run
    against either shape without their caller having to reshape upstream.

    The caller's dict is not mutated.
    """
    normalized: Dict[str, Any] = dict(data)

    # market_prices — canonical Dict[int, float]
    if not normalized.get("market_prices"):
        for alt_key in ("prices", "price_series", "price"):
            candidate = normalized.get(alt_key)
            promoted = _series_to_round_dict(candidate)
            if promoted:
                normalized["market_prices"] = promoted
                break

    # fundamentals — canonical Dict[int, float]
    if not normalized.get("fundamentals"):
        for alt_key in ("fundamental_series", "fundamental_values"):
            candidate = normalized.get(alt_key)
            promoted = _series_to_round_dict(candidate)
            if promoted:
                normalized["fundamentals"] = promoted
                normalized["_fundamentals_source"] = f"promoted_from:{alt_key}"
                break
        else:
            # Deliberately DO NOT auto-broadcast a scalar
            # market_parameters.fundamental_value to every round.
            #
            # For dynamic-fundamental scenarios (AssetBubble, MomentumEffect,
            # ReversalEffect, GFC2008, etc.) the fundamental should evolve
            # over time (dividend growth, regime shifts, announcement
            # shocks). Broadcasting a constant lies about the baseline and
            # falsifies price_deviation_ts / mad_pct / half_life_threshold /
            # under_revision_ratio / price_efficiency_ratio /
            # forecast_error_persistence — all of which read from
            # normalized["fundamentals"].
            #
            # We record the scalar under a hint key so scenarios that
            # explicitly want the scalar baseline (rare) can promote it
            # themselves in their analysis.py.
            mp = normalized.get("market_parameters")
            if isinstance(mp, Mapping) and "fundamental_value" in mp:
                try:
                    normalized["_fundamentals_scalar_hint"] = float(
                        mp["fundamental_value"]
                    )
                    normalized["_fundamentals_source"] = "scalar_hint_only"
                except (TypeError, ValueError):
                    normalized["_fundamentals_source"] = "scalar_hint_bad_value"
            else:
                normalized["_fundamentals_source"] = "missing"

    # volumes — canonical Dict[int, float]
    if not normalized.get("volumes"):
        for alt_key in ("volume_series", "volume"):
            candidate = normalized.get(alt_key)
            promoted = _series_to_round_dict(candidate)
            if promoted:
                normalized["volumes"] = promoted
                break

    # investor_quantities / investor_bids — leave alone unless obviously wrong
    for key in ("investor_quantities", "investor_bids"):
        if key not in normalized:
            normalized[key] = {}

    return normalized


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compute_universal_metrics(
    data: Mapping[str, Any],
    config: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute the full 36-metric Layer A baseline.

    Parameters
    ----------
    data : Mapping
        The canonical MASim data dict produced by
        :func:`masim.evaluation.data_loader.load_data`.
    config : Mapping, optional
        The scenario configuration dict. Passed through to metric functions
        that need parameters (e.g., rolling window sizes). May be ``None``
        for smoke tests.

    Returns
    -------
    dict with keys:
        ``by_category``    : Dict[category, Dict[metric_name, result]]
        ``coverage``       : coverage-floor statistics (see ``_coverage_stats``)
        ``references``     : Dict[metric_name, List[str]] (primary sources)
        ``metric_order``   : List[str] — metric names in registration order
        ``raw``            : registry's raw ``compute_all`` output (for debugging)
    """
    registry = _build_registry()
    config_dict = dict(config) if config is not None else {}
    raw = registry.compute_all(dict(data), config_dict)
    raw_metrics = raw["metrics"]
    return {
        "by_category": _group_by_category(raw_metrics),
        "coverage": _coverage_stats(raw_metrics),
        "references": _collect_references(),
        "metric_order": [m.name for m in STANDARD_METRICS],
        "raw": raw,
    }


def write_universal_summary(
    data: Mapping[str, Any],
    config: Mapping[str, Any],
    output_dir: str,
    scenario: str,
    variant: str = "Rule",
    extra_summary: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    """Compute Layer A metrics, draw universal PNGs, and write ``summary.json``.

    This is the single call declared by Polish Hook 9. Every scenario's
    ``analysis.py`` MUST invoke it once per run.

    Parameters
    ----------
    data : Mapping
        Canonical MASim data dict (from
        :func:`masim.evaluation.data_loader.load_data`).
    config : Mapping
        The scenario configuration dict. MUST NOT be ``None`` in production
        runs — required for reproducibility (used to hash ``config_hash``).
    output_dir : str
        Directory to write ``summary.json`` and PNG dashboards into.
        Created if missing.
    scenario : str
        Scenario name (e.g. "AssetBubble"). Recorded in ``summary.json``.
    variant : str, default "Rule"
        Variant name (Rule / LLM / RuleLLM / Rag). Recorded in
        ``summary.json`` and used by Hook 12 parity diffing.
    extra_summary : Mapping, optional
        Scenario-specific (Layer B) or variant-specific (Layer C) blocks
        to merge into the written ``summary.json``. Callers use this to
        add ``scenario_metrics``, ``variant_extras``, ``validation``, and
        any additional keys. Universal top-level keys already set by this
        function will win a name collision, so callers should namespace
        their additions.

    Returns
    -------
    dict
        The final ``summary.json`` content that was written to disk. Callers
        can inspect it, patch it, and re-write if further post-processing
        is needed.
    """
    if not scenario:
        raise ValueError("scenario name is required")
    if config is None:
        raise ValueError(
            "config is required for universal summary "
            "(needed for config_hash reproducibility)"
        )
    os.makedirs(output_dir, exist_ok=True)

    normalized = _normalize_data(data)
    universal = compute_universal_metrics(normalized, config)

    # --- render the four universal PNG dashboards ---------------------------
    #
    # ``create_standard_visualizations`` writes: 00_investor_bids.png,
    # 01_{scenario}_dynamics.png, 02_{scenario}_analysis.png, 03_summary.png
    #
    files_written: List[str] = []
    if normalized.get("market_prices"):
        try:
            files_written = list(
                create_standard_visualizations(scenario, normalized, output_dir)
            )
        except Exception as exc:  # noqa: BLE001 — see docstring; PNG failure must not block summary.json
            universal["coverage"]["visualization_error"] = f"{type(exc).__name__}: {exc}"
    else:
        universal["coverage"]["skipped_reason"] = "no_price_series"

    # --- assemble Hook 11-compliant summary.json ----------------------------
    market_prices = normalized.get("market_prices") or {}
    summary: Dict[str, Any] = {
        "scenario": scenario,
        "variant": variant,
        "config_hash": _config_hash(config),
        "n_rounds": len(market_prices),
        "universal_metrics": universal["by_category"],
        "universal_coverage": universal["coverage"],
        "scenario_metrics": {},        # populated by Layer B caller
        "variant_extras": {},          # populated by Layer C caller
        "validation": {                # placeholder; Layer B/§6 overwrites
            "passed": None,
            "score": None,
            "criteria": {},
        },
        "files_written": files_written,
        "references": {
            "universal": universal["references"],
            "scenario": {},            # populated by Layer B caller
        },
    }

    if extra_summary:
        for key, value in extra_summary.items():
            if key in ("scenario", "variant", "config_hash", "n_rounds",
                       "universal_metrics", "universal_coverage"):
                # Universal keys are authoritative; skip caller overrides.
                continue
            if key == "files_written":
                # Merge file lists rather than clobber.
                existing = set(summary["files_written"])
                for f in value or ():
                    if f not in existing:
                        summary["files_written"].append(f)
                        existing.add(f)
                continue
            if key == "references" and isinstance(value, Mapping):
                for ref_key, ref_val in value.items():
                    if ref_key == "universal":
                        continue  # authoritative
                    summary["references"][ref_key] = ref_val
                continue
            summary[key] = value

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    if summary_path not in summary["files_written"]:
        summary["files_written"].append(summary_path)

    return summary


__all__ = [
    "CATEGORY_ORDER",
    "compute_universal_metrics",
    "write_universal_summary",
]
