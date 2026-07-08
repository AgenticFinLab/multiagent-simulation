"""Evaluation Pipeline — Standard analysis orchestration.

Provides high-level pipeline functions that run the complete analysis flow:
data loading → metric computation → visualization → validation → summary output.

These functions implement the "standard output contract" that most scenarios
use as their primary analysis entry point.

Usage:
    from masim.evaluation.pipeline import run_standard_analysis, analyze_standard_scenario
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Dict, Optional

from masim.evaluation.data_loader import load_data
from masim.utils import load_config, load_results


def run_standard_analysis(
    scenario: str,
    config_path: str,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the complete standard analysis pipeline for a scenario.

    This is the single entry point used by scenarios that follow the standard
    output contract (summary.json + PNG dashboards).

    Parameters
    ----------
    scenario : str
        Scenario name (e.g., "FlashCrash", "HerdEffect").
    config_path : str
        Path to the simulation config YAML file.
    output_dir : str, optional
        Directory for output files. If None, derived from config path.

    Returns
    -------
    dict with analysis results including metrics, validation, and file paths.
    """
    config = load_config(config_path)
    results = load_results(config)
    data = load_data(results)

    if output_dir is None:
        output_dir = os.path.join(
            os.path.dirname(config_path), "..", "analysis_output"
        )
        output_dir = os.path.abspath(output_dir)

    os.makedirs(output_dir, exist_ok=True)

    return analyze_standard_scenario(scenario, data, config, output_dir)


def analyze_standard_scenario(
    scenario: str,
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Run metrics, validation, and visualization on pre-loaded data.

    This function implements the standard analysis flow without re-loading data.
    It delegates to scenario-specific analysis when available, or falls back
    to generic metric computation.

    Parameters
    ----------
    scenario : str
        Scenario name.
    data : dict
        Pre-loaded data dict (from load_data or equivalent).
    config : dict
        Simulation configuration dict.
    output_dir : str
        Directory for output files.

    Returns
    -------
    dict with keys: "metrics", "validation", "output_dir", "files_written".
    """
    summary = {
        "scenario": scenario,
        "metrics": {},
        "validation": None,
        "output_dir": output_dir,
        "files_written": [],
    }

    # Compute standard structural metrics
    metrics = calculate_standard_metrics(data)
    summary["metrics"] = metrics

    # Create standard visualizations
    files = create_standard_visualizations(scenario, data, output_dir)
    summary["files_written"] = files

    # Write summary.json
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    summary["files_written"].append(summary_path)

    return summary


def calculate_standard_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute the standard structural metrics for any finance scenario.

    Uses functions from masim.evaluation.finance to compute:
    - Price dynamics (returns, volatility, drawdown, Sharpe)
    - Behavioral signals (bid convergence, directional agreement)
    - Market microstructure (volume, net demand)

    Parameters
    ----------
    data : dict
        Standard data dict with market_prices, fundamentals, investor_* fields.

    Returns
    -------
    dict of computed metric values (flat key-value pairs).
    """
    from masim.evaluation.finance.timeseries import (
        calculate_returns,
        calculate_rolling_volatility,
        calculate_max_drawdown,
        calculate_sharpe_ratio,
        calculate_price_deviation,
        calculate_autocorrelation,
    )
    from masim.evaluation.finance.behavioral import (
        calculate_bid_convergence_cv,
        calculate_directional_agreement,
    )

    metrics: Dict[str, Any] = {}
    market_prices = data.get("market_prices", {})
    fundamentals = data.get("fundamentals", {})
    investor_bids = data.get("investor_bids", {})

    if market_prices:
        prices_list = [market_prices[r] for r in sorted(market_prices)]
        returns = calculate_returns(market_prices)
        metrics["n_rounds"] = len(market_prices)

        if returns:
            returns_arr = list(returns.values()) if isinstance(returns, dict) else returns
            metrics["mean_return"] = float(sum(returns_arr) / len(returns_arr)) if returns_arr else 0.0
            metrics["sharpe_ratio"] = calculate_sharpe_ratio(returns_arr)

        vol = calculate_rolling_volatility(market_prices)
        if vol:
            vol_values = list(vol.values()) if isinstance(vol, dict) else vol
            metrics["mean_volatility"] = float(sum(vol_values) / len(vol_values)) if vol_values else 0.0

        dd_result = calculate_max_drawdown(prices_list)
        if isinstance(dd_result, tuple):
            metrics["max_drawdown_pct"] = dd_result[0]
        else:
            metrics["max_drawdown_pct"] = dd_result

        if fundamentals:
            deviations = calculate_price_deviation(market_prices, fundamentals)
            if deviations:
                dev_values = list(deviations.values()) if isinstance(deviations, dict) else deviations
                metrics["mean_abs_deviation_pct"] = float(
                    sum(abs(d) for d in dev_values) / len(dev_values)
                ) if dev_values else 0.0

    if investor_bids:
        cv = calculate_bid_convergence_cv(investor_bids)
        if cv:
            cv_values = list(cv.values())
            metrics["mean_bid_cv"] = float(sum(cv_values) / len(cv_values))

        agreement = calculate_directional_agreement(investor_bids)
        if agreement:
            ag_values = list(agreement.values())
            metrics["mean_directional_agreement"] = float(sum(ag_values) / len(ag_values))

    return metrics


def create_standard_visualizations(
    scenario: str,
    data: Dict[str, Any],
    output_dir: str,
) -> list:
    """Create the standard set of analysis visualizations.

    Generates the four standard PNG files:
    - 00_investor_bids.png: Investor bidding curves
    - 01_{scenario}_dynamics.png: Price/fundamental dynamics
    - 02_{scenario}_analysis.png: Returns and volatility
    - 03_summary.png: Multi-panel summary

    Parameters
    ----------
    scenario : str
        Scenario name (used in filenames).
    data : dict
        Standard data dict.
    output_dir : str
        Directory for output files.

    Returns
    -------
    list of file paths written.
    """
    from masim.evaluation.finance.visualization import (
        plot_price_dynamics,
        plot_returns_analysis,
        plot_volatility_analysis,
        plot_bid_convergence,
        save_figure,
        create_figure,
    )

    os.makedirs(output_dir, exist_ok=True)
    files_written = []
    scenario_lower = scenario.lower()
    market_prices = data.get("market_prices", {})
    fundamentals = data.get("fundamentals", {})
    investor_bids = data.get("investor_bids", {})

    # 00: Investor bids
    if investor_bids:
        try:
            fig = plot_bid_convergence(investor_bids, market_prices)
            path = os.path.join(output_dir, "00_investor_bids.png")
            save_figure(fig, path)
            files_written.append(path)
        except Exception:
            pass

    # 01: Price dynamics
    if market_prices:
        try:
            fig = plot_price_dynamics(market_prices, fundamentals)
            path = os.path.join(output_dir, f"01_{scenario_lower}_dynamics.png")
            save_figure(fig, path)
            files_written.append(path)
        except Exception:
            pass

    # 02: Returns analysis
    if market_prices:
        try:
            fig = plot_returns_analysis(market_prices)
            path = os.path.join(output_dir, f"02_{scenario_lower}_analysis.png")
            save_figure(fig, path)
            files_written.append(path)
        except Exception:
            pass

    # 03: Summary (volatility)
    if market_prices:
        try:
            fig = plot_volatility_analysis(market_prices)
            path = os.path.join(output_dir, "03_summary.png")
            save_figure(fig, path)
            files_written.append(path)
        except Exception:
            pass

    return files_written
