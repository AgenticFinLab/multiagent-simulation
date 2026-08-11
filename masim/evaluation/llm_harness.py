"""Shared LLM analysis harness — eliminates per-scenario boilerplate.

All LLM-variant ``analysis.py`` files share two blocks of duplicated code:

1. **Action-distribution injection** (~10 lines): runs
   :func:`~masim.evaluation.analyze_action_distribution`, merges into
   ``summary.json``, and attaches to the in-memory summary dict.

2. **Universal-summary tail** (~11 lines): variant-detection from config path
   + :func:`~masim.evaluation.write_universal_summary` for Layer-A 36-metric
   baseline + four universal PNG dashboards.

This module provides:

* :func:`finalize_llm_analysis` — replaces blocks 1+2 in a single call.
* :func:`run_llm_analysis` — full entry-point that replaces the *entire*
  ``main()`` for standard Pattern-A files (argparse + load + analyze +
  finalize).
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
from typing import Any, Callable, Dict, Optional

from masim.evaluation.finance.llm_action_distribution import (
    analyze_action_distribution,
)
from masim.evaluation.universal import write_universal_summary
from masim.utils import load_config, load_results


def _detect_variant(config_path: Optional[str]) -> str:
    """Derive the simulation variant from the config file path."""
    if not isinstance(config_path, str):
        return "LLM"
    for variant in ("RuleLLM", "Rule", "LLM", "Rag"):
        if f"/{variant}/" in config_path or config_path.endswith(f"/{variant}"):
            return variant
    return "LLM"


def finalize_llm_analysis(
    data: Any,
    config: Dict[str, Any],
    output_dir: str,
    scenario: str,
    summary: Any,
    *,
    results: Any = None,
    config_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Shared LLM analysis finalization: action-distribution + universal summary.

    Parameters
    ----------
    data : Any
        Loaded simulation data (passed through to ``write_universal_summary``).
    config : dict
        Parsed YAML simulation config.
    output_dir : str
        Path to write analysis artifacts.
    scenario : str
        Human-readable scenario name (e.g. ``"CarryTradeUnwind"``).
    summary : dict or Any
        Scenario-specific metrics dict returned by the ``analyze_*`` function.
    results : optional
        Raw :func:`~masim.utils.load_results` object. If provided, used
        for :func:`~masim.evaluation.analyze_action_distribution`. If *None*,
        action-distribution audit is skipped.
    config_path : str, optional
        Config file path for variant detection. If omitted, defaults to "LLM".

    Returns
    -------
    dict
        The universal summary dict produced by ``write_universal_summary``.
    """
    # ── Action-distribution injection ────────────────────────────────────
    if results is not None:
        action_dist = analyze_action_distribution(results)
        summary_path = os.path.join(output_dir, "summary.json")
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                persisted = json.load(f)
        except (OSError, ValueError):
            persisted = summary if isinstance(summary, dict) else {}
        persisted["llm_action_distribution"] = action_dist
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(persisted, f, indent=2, default=str)
        if isinstance(summary, dict):
            summary["llm_action_distribution"] = action_dist

    # ── Universal summary (Layer-A 36-metric baseline) ───────────────────
    variant = _detect_variant(config_path)
    universal = write_universal_summary(
        data,
        config,
        output_dir,
        scenario=scenario,
        variant=variant,
        extra_summary={"scenario_metrics": summary}
        if isinstance(summary, dict)
        else None,
    )
    return universal


def run_llm_analysis(
    *,
    scenario: str,
    default_config: str,
    analyze_fn: Callable,
    load_data_fn: Callable,
    analyze_kwargs: Optional[Dict[str, Any]] = None,
) -> None:
    """Full LLM analysis entry-point for standard Pattern-A files.

    Encapsulates the entire ``main()`` body shared by most LLM analysis scripts:

        argparse → load_config → load_results → load_data → analyze →
        finalize (action-dist + universal summary)

    Parameters
    ----------
    scenario : str
        Human-readable scenario name.
    default_config : str
        Default path to YAML config.
    analyze_fn : callable
        Scenario-specific analysis function imported from ``Rule/analysis.py``.
        Accepts either ``(data, config, output_dir)`` or ``(data, output_dir)``.
    load_data_fn : callable
        Data-loading function imported from ``Rule/analysis.py``.
        Accepts ``(results,)`` and returns the data dict.
    analyze_kwargs : dict, optional
        Extra keyword arguments passed to ``analyze_fn`` (e.g. ``variant``).
    """
    parser = argparse.ArgumentParser(
        description=f"Analyze {scenario} LLM simulation results"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=default_config,
        help="Path to simulation config file",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = load_data_fn(results)

    # Call analyze_fn — handle both 2-arg and 3-arg signatures gracefully.
    extra = analyze_kwargs or {}
    sig = inspect.signature(analyze_fn)
    params = [
        p
        for p in sig.parameters.values()
        if p.default is inspect.Parameter.empty
        and p.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    ]
    if len(params) >= 3:
        summary = analyze_fn(data, config, output_dir, **extra)
    else:
        summary = analyze_fn(data, output_dir, **extra)

    finalize_llm_analysis(
        data,
        config,
        output_dir,
        scenario,
        summary,
        results=results,
        config_path=args.config,
    )
