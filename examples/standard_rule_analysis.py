"""Shared standard analysis utilities for lightweight financial scenarios.

Architecture
~~~~~~~~~~~~
This module is the **scenario-level** analysis framework that orchestrates:

- CLI entry point with argparse (``run_standard_analysis``);
- structured validation console report (``validate_standard_metrics``);
- four fixed PNG visualizations (``create_standard_visualizations``);
- ``summary.json`` + universal summary hook (``analyze_standard_scenario``);
- extensible metric registry (``MetricsRegistry``).

The lower-level **framework toolkit** lives in :mod:`masim.evaluation`, which
provides reusable primitives (data loading, metric computation, timeseries
analysis, finance-specific validation). This module delegates to
:func:`masim.evaluation.write_universal_summary` for Hook 9/11 compliance.

When adding new analysis capabilities:
- Framework-general utilities → :mod:`masim.evaluation`
- Scenario-specific orchestration → this module or per-scenario ``analysis.py``
"""

from __future__ import annotations

from dataclasses import dataclass, field
import argparse
import json
import os
from typing import Any, Callable, Dict, Iterable, List, Tuple

import matplotlib.pyplot as plt
import numpy as np

from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary
from masim.evaluation.data_loader import batch_to_rounds


# ---------------------------------------------------------------------------
# Extensible metrics registry (used by scenarios such as AnchoringEffect)
# ---------------------------------------------------------------------------
#
# A scenario authors a `metrics.py` module that imports `Metric` and
# `MetricsRegistry`, defines small computation functions of the form
# `def fn(data: dict, config: dict) -> dict[str, Any]`, wraps each in a
# `Metric` instance, and registers it. The analysis CLI then iterates with
# `registry.compute_all(data, config)` and never has to be edited when a new
# metric is added.
#
# Each metric function MUST return a dict whose keys match its declared
# `output_keys`. If the metric cannot be computed for the available data
# (missing series, insufficient rounds, etc.) the function should raise
# `MetricUnavailable`; the driver records the reason and continues.


class MetricUnavailable(Exception):
    """Raised by a metric function when its inputs are missing or insufficient."""


@dataclass(frozen=True)
class Metric:
    """Description of a single registered metric.

    Attributes
    ----------
    name        : Snake-case identifier, e.g. ``"mad_pct"``.
    category    : Coarse grouping. Scenarios may define their own categories
                  but the canonical taxonomy is::

                      price_dynamics, anchoring_specific, agent_behaviour,
                      microstructure, statistical_inference, phase_decomposition.
    fn          : Callable ``fn(data, config) -> dict``.
    output_keys : Tuple of keys the function is expected to populate.
    references  : Citation strings (academic basis or analysis-bases.md anchor).
    description : One-line human-readable summary.
    """

    name: str
    category: str
    fn: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
    output_keys: Tuple[str, ...]
    references: Tuple[str, ...] = ()
    description: str = ""


class MetricsRegistry:
    """In-memory registry of `Metric` instances, queryable by category.

    The registry is intentionally simple: scenarios import a single module-level
    instance, register all metrics at import time, and the analysis driver
    enumerates them.
    """

    def __init__(self) -> None:
        self._metrics: Dict[str, Metric] = {}

    def register(self, metric: Metric) -> None:
        """Add a metric to the registry. Raises if the name already exists."""
        if metric.name in self._metrics:
            raise ValueError(
                f"Metric '{metric.name}' is already registered. "
                "Choose a unique name or remove the prior registration."
            )
        self._metrics[metric.name] = metric

    def names(self) -> List[str]:
        return list(self._metrics)

    def by_category(self) -> Dict[str, List[Metric]]:
        """Group metrics by their declared category, preserving insertion order."""
        grouped: Dict[str, List[Metric]] = {}
        for metric in self._metrics.values():
            grouped.setdefault(metric.category, []).append(metric)
        return grouped

    def get(self, name: str) -> Metric:
        return self._metrics[name]

    def compute_all(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run every registered metric and return a structured result dict.

        Returns
        -------
        dict
            ``{category: {metric_name: {output_key: value, ...}, ...}, ...}``
            plus an ``"_unavailable"`` key listing metrics that raised
            :class:`MetricUnavailable` together with the reason.
        """
        results: Dict[str, Dict[str, Any]] = {}
        unavailable: Dict[str, str] = {}
        for metric in self._metrics.values():
            try:
                output = metric.fn(data, config)
            except MetricUnavailable as exc:
                unavailable[metric.name] = str(exc)
                continue
            if not isinstance(output, dict):
                raise TypeError(
                    f"Metric '{metric.name}' must return a dict, got "
                    f"{type(output).__name__}."
                )
            missing = [key for key in metric.output_keys if key not in output]
            if missing:
                raise ValueError(
                    f"Metric '{metric.name}' did not return declared keys: "
                    f"{missing}."
                )
            results.setdefault(metric.category, {})[metric.name] = output
        out: Dict[str, Any] = dict(results)
        if unavailable:
            out["_unavailable"] = unavailable
        return out

    def flatten(self, computed: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten ``compute_all`` output into ``{metric_name: outputs}``."""
        flat: Dict[str, Any] = {}
        for category, metrics in computed.items():
            if category == "_unavailable":
                continue
            for name, outputs in metrics.items():
                flat[name] = outputs
        return flat

    def iter_metrics(self) -> Iterable[Metric]:
        return iter(self._metrics.values())


_BID_COLORS = [
    "#3a86ff",
    "#ff006e",
    "#8338ec",
    "#06d6a0",
    "#fb5607",
    "#ff595e",
    "#1982c4",
    "#6a4c93",
    "#ffca3a",
    "#8ac926",
]


@dataclass
class StandardValidationResult:
    """Generic structural validation result for standardized analyses."""

    is_valid: bool
    score: float
    criteria: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    interpretation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "score": round(self.score, 4),
            "criteria": self.criteria,
            "interpretation": self.interpretation,
        }


def _market_data_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return market data from a turn payload, supporting nested and flat shapes."""
    market_data = payload.get("market_data")
    if isinstance(market_data, dict):
        return market_data
    return payload


def _market_players(results: Any) -> Dict[str, Any]:
    """Return coordinator-like market players across historical role labels."""
    players: Dict[str, Any] = {}
    players.update(results.players_by_role("coordinator"))
    players.update(results.players_by_role("market"))
    if hasattr(results, "players") and "market" in results.players:
        players.setdefault("market", results.players["market"])
    return players


def _load_data(results: Any) -> Dict[str, Any]:
    """Extract market and investor data from `SimulationResults`."""
    market_prices: Dict[int, float] = {}
    fundamentals: Dict[int, float] = {}
    volumes: Dict[int, float] = {}
    investor_quantities: Dict[str, Dict[int, float]] = {}
    investor_bids: Dict[str, Dict[int, float]] = {}

    for player in _market_players(results).values():
        if "price" in player.batch_store_names:
            market_prices.update(batch_to_rounds(player.batch("price").all()))
        if "fundamental" in player.batch_store_names:
            fundamentals.update(batch_to_rounds(player.batch("fundamental").all()))
        if "volume" in player.batch_store_names:
            volumes.update(batch_to_rounds(player.batch("volume").all()))
        for round_num, payload in player.turns.payloads().items():
            market_data = _market_data_from_payload(payload)
            if round_num not in market_prices and "price" in market_data:
                market_prices[round_num] = float(market_data["price"])
            if round_num not in fundamentals:
                if "fundamental" in market_data:
                    fundamentals[round_num] = float(market_data["fundamental"])
                elif "fundamental_value" in market_data:
                    fundamentals[round_num] = float(market_data["fundamental_value"])
            if round_num not in volumes and "volume" in market_data:
                volumes[round_num] = float(market_data["volume"])

    for pid, player in results.players_by_role("player").items():
        quantities = player.turns.field("quantity")
        if quantities:
            investor_quantities[pid] = quantities
        bids = player.turns.field("bid_price")
        if bids:
            investor_bids[pid] = bids

    return {
        "market_prices": market_prices,
        "fundamentals": fundamentals,
        "volumes": volumes,
        "investor_quantities": investor_quantities,
        "investor_bids": investor_bids,
    }


def _series(data: Dict[int, float]) -> list[float]:
    """Return values sorted by round."""
    return [float(data[round_num]) for round_num in sorted(data)]


def _coordinator_extras(config: Dict[str, Any]) -> Dict[str, Any]:
    """Return coordinator extras from a resolved simulation config."""
    for key, player in config.get("players", {}).items():
        player_config = player.get("config", {})
        extras = player_config.get("extras", {})
        if player_config.get("role") == "coordinator":
            return extras
        if key == "market" and "fundamental_value" in extras:
            return extras
    return {}


def _ensure_fundamentals_from_config(
    data: Dict[str, Any],
    config: Dict[str, Any],
) -> None:
    """Populate missing fundamentals from coordinator config when possible."""
    if data["fundamentals"] or not data["market_prices"]:
        return

    extras = _coordinator_extras(config)
    if "fundamental_value" not in extras:
        return

    base_value = float(extras["fundamental_value"])
    growth = float(extras["fundamental_growth"]) if "fundamental_growth" in extras else 0.0
    data["fundamentals"] = {
        round_num: base_value * ((1.0 + growth) ** round_num)
        for round_num in sorted(data["market_prices"])
    }


def calculate_standard_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate generic structural market metrics."""
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    volumes = data["volumes"]
    if not market_prices:
        raise ValueError("No market price data recorded")
    if not fundamentals:
        raise ValueError("No fundamental data recorded")

    prices = np.array(_series(market_prices), dtype=float)
    fundamental_values = np.array(_series(fundamentals), dtype=float)
    if len(prices) != len(fundamental_values):
        raise ValueError("Price and fundamental series lengths differ")
    if np.any(fundamental_values == 0):
        raise ValueError("Fundamental series contains zero values")

    returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else np.array([])
    deviations = (prices - fundamental_values) / fundamental_values
    volume_values = _series(volumes) if volumes else []

    return {
        "price_metrics": {
            "initial": float(prices[0]),
            "final": float(prices[-1]),
            "min": float(np.min(prices)),
            "max": float(np.max(prices)),
            "mean": float(np.mean(prices)),
            "total_rounds": int(len(prices)),
        },
        "deviation_metrics": {
            "max_abs_deviation_pct": float(np.max(np.abs(deviations)) * 100),
            "mean_abs_deviation_pct": float(np.mean(np.abs(deviations)) * 100),
            "final_deviation_pct": float(deviations[-1] * 100),
        },
        "return_metrics": {
            "max_drawdown_pct": float(np.min(returns) * 100) if len(returns) else 0.0,
            "volatility_pct": float(np.std(returns) * 100) if len(returns) else 0.0,
            "annualized_volatility_pct": (
                float(np.std(returns) * np.sqrt(252) * 100) if len(returns) else 0.0
            ),
        },
        "volume_metrics": {
            "total_volume": float(sum(volume_values)) if volume_values else 0.0,
            "mean_volume": float(np.mean(volume_values)) if volume_values else 0.0,
        },
    }


def _score_range(value: float, lower: float, upper: float) -> float:
    """Score a scalar against a bounded acceptable interval."""
    if lower <= value <= upper:
        return 1.0
    if value < lower:
        return max(0.0, value / lower) if lower > 0 else 0.0
    return max(0.0, 1.0 - (value - upper) / max(upper, 1.0))


def validate_standard_metrics(
    scenario: str,
    metrics: Dict[str, Any],
    total_rounds: int,
) -> StandardValidationResult:
    """Validate generic structural quality for a completed scenario run."""
    finite_prices = all(
        np.isfinite(value)
        for value in [
            metrics["price_metrics"]["initial"],
            metrics["price_metrics"]["final"],
            metrics["price_metrics"]["min"],
            metrics["price_metrics"]["max"],
        ]
    )
    round_score = _score_range(float(total_rounds), 150.0, 100000.0)
    finite_score = 1.0 if finite_prices else 0.0
    deviation = metrics["deviation_metrics"]["max_abs_deviation_pct"]
    deviation_score = _score_range(deviation, 0.01, 500.0)
    volatility = metrics["return_metrics"]["annualized_volatility_pct"]
    volatility_score = _score_range(volatility, 0.0, 1000.0)

    criteria = {
        "Full-Round Completion": {
            "value": total_rounds,
            "target": ">=150 recorded market rounds; 200 expected for full experiments",
            "score": round(round_score, 3),
            "passed": round_score >= 0.99,
        },
        "Finite Price Path": {
            "value": bool(finite_prices),
            "target": "all price summary values finite",
            "score": round(finite_score, 3),
            "passed": finite_prices,
        },
        "Observable Price Deviation": {
            "value": round(deviation, 3),
            "target": "0.01% to 500% absolute deviation",
            "score": round(deviation_score, 3),
            "passed": deviation_score >= 0.5,
        },
        "Volatility Sanity": {
            "value": round(volatility, 3),
            "target": "0% to 1000% annualized volatility",
            "score": round(volatility_score, 3),
            "passed": volatility_score >= 0.5,
        },
    }
    weights = {
        "Full-Round Completion": 0.35,
        "Finite Price Path": 0.30,
        "Observable Price Deviation": 0.20,
        "Volatility Sanity": 0.15,
    }
    score = sum(criteria[name]["score"] * weight for name, weight in weights.items())
    is_valid = score >= 0.5 and finite_prices and total_rounds > 0
    verdict = "VALID" if is_valid else "INVALID"
    interpretation = "\n".join(
        [
            f"=== {scenario} SIMULATION VALIDATION: {verdict} ===",
            f"Overall Fit Score: {score:.1%} (threshold: 50%)",
            "",
            "[1] Full-Round Completion",
            f"    Observed: {total_rounds} rounds",
            "    Expected: >=150 recorded market rounds (200 for full experiments)",
            f"    Score: {round_score:.1%}",
            "    Assessment: "
            + ("OPTIMAL - market records are present." if round_score >= 0.99 else "INSUFFICIENT - run is incomplete."),
            "",
            "[2] Finite Price Path",
            f"    Observed: {finite_prices}",
            "    Expected: all price summaries finite",
            f"    Score: {finite_score:.1%}",
            "    Assessment: "
            + ("OPTIMAL - price series is numeric." if finite_prices else "INSUFFICIENT - price series has invalid values."),
            "",
            "[3] Observable Price Deviation",
            f"    Observed: {deviation:.2f}%",
            "    Expected: nonzero but bounded deviation",
            f"    Score: {deviation_score:.1%}",
            "    Assessment: structural deviation check completed.",
            "",
            "[4] Volatility Sanity",
            f"    Observed: {volatility:.2f}%",
            "    Expected: bounded annualized volatility",
            f"    Score: {volatility_score:.1%}",
            "    Assessment: structural volatility check completed.",
            "",
            "[SUMMARY]",
            f"The {scenario} run produced a structurally analyzable market path.",
            "Scenario-specific mechanism validity should be assessed with the metrics in analysis-bases.md.",
            f"Fit Score: {score:.1%}",
        ]
    )
    return StandardValidationResult(is_valid, score, criteria, interpretation)


def create_standard_visualizations(
    scenario: str,
    data: Dict[str, Any],
    output_dir: str,
) -> None:
    """Create the fixed four-figure analysis output set."""
    os.makedirs(output_dir, exist_ok=True)
    market_prices = data["market_prices"]
    fundamentals = data["fundamentals"]
    volumes = data["volumes"]
    investor_quantities = data["investor_quantities"]
    investor_bids = data["investor_bids"]
    if not market_prices:
        raise ValueError("No market price data recorded")
    if not fundamentals:
        raise ValueError("No fundamental data recorded")

    rounds = sorted(market_prices)
    prices = np.array([market_prices[round_num] for round_num in rounds], dtype=float)
    fundamental_values = np.array(
        [fundamentals[round_num] for round_num in rounds], dtype=float
    )
    deviations = (prices - fundamental_values) / fundamental_values * 100
    returns = np.diff(prices) / prices[:-1] * 100 if len(prices) > 1 else np.array([])
    scenario_key = scenario.lower()

    fig0, ax0 = plt.subplots(figsize=(16, 8))
    ax0.plot(rounds, prices, color="#f0a500", linewidth=2.5, label="Market Price", zorder=10)
    ax0.plot(rounds, fundamental_values, color="darkgreen", linestyle="--", label="Fundamental")
    for index, (pid, bids) in enumerate(sorted(investor_bids.items())):
        bid_rounds = sorted(bids)
        bid_values = [float(bids[round_num]) for round_num in bid_rounds]
        ax0.plot(
            bid_rounds,
            bid_values,
            marker="o",
            markersize=2,
            linewidth=0.9,
            color=_BID_COLORS[index % len(_BID_COLORS)],
            alpha=0.8,
            label=pid,
        )
    ax0.set_title(f"{scenario} - Investor Bidding Curves")
    ax0.set_xlabel("Round")
    ax0.set_ylabel("Price")
    ax0.grid(True, alpha=0.3)
    ax0.legend(loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=4, fontsize=8)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "00_investor_bids.png"), dpi=150, bbox_inches="tight")
    plt.close()

    fig1, axes1 = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    axes1[0].plot(rounds, prices, label="Price", color="#d1495b")
    axes1[0].plot(rounds, fundamental_values, label="Fundamental", color="#00798c", linestyle="--")
    axes1[0].set_ylabel("Price")
    axes1[0].legend()
    axes1[0].grid(True, alpha=0.3)
    axes1[1].plot(rounds, deviations, color="#7b2cbf")
    axes1[1].axhline(0, color="black", linestyle="--", linewidth=0.8)
    axes1[1].set_xlabel("Round")
    axes1[1].set_ylabel("Deviation (%)")
    axes1[1].grid(True, alpha=0.3)
    fig1.suptitle(f"{scenario} - Price Dynamics")
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, f"01_{scenario_key}_dynamics.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    fig2, axes2 = plt.subplots(1, 2, figsize=(14, 5))
    axes2[0].plot(rounds[1:], returns, color="#2a9d8f") if len(returns) else axes2[0].text(0.5, 0.5, "No returns", ha="center")
    axes2[0].set_title("Returns")
    axes2[0].set_xlabel("Round")
    axes2[0].set_ylabel("Return (%)")
    axes2[0].grid(True, alpha=0.3)
    axes2[1].hist(deviations, bins=min(30, max(5, len(deviations) // 4)), color="#457b9d", alpha=0.75)
    axes2[1].set_title("Deviation Distribution")
    axes2[1].set_xlabel("Deviation (%)")
    axes2[1].grid(True, alpha=0.3)
    fig2.suptitle(f"{scenario} - Structural Analysis")
    plt.tight_layout()
    plt.savefig(
        os.path.join(output_dir, f"02_{scenario_key}_analysis.png"),
        dpi=150,
        bbox_inches="tight",
    )
    plt.close()

    fig3, axes3 = plt.subplots(1, 2, figsize=(14, 5))
    if investor_quantities:
        labels = []
        totals = []
        for pid, quantities in sorted(investor_quantities.items()):
            labels.append(pid)
            totals.append(sum(abs(float(value)) for value in quantities.values()))
        axes3[0].bar(labels, totals, color="#264653")
        axes3[0].tick_params(axis="x", labelrotation=45)
        axes3[0].set_ylabel("Absolute Quantity")
    else:
        axes3[0].text(0.5, 0.5, "No investor quantity records", ha="center")
    axes3[0].set_title("Agent Trading Volume")
    residual = prices - fundamental_values
    axes3[1].plot(rounds, residual, color="#e76f51")
    axes3[1].axhline(0, color="black", linestyle="--", linewidth=0.8)
    axes3[1].set_title("Price Residual")
    axes3[1].set_xlabel("Round")
    axes3[1].set_ylabel("Price - Fundamental")
    axes3[1].grid(True, alpha=0.3)
    fig3.suptitle(f"{scenario} - Summary")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "03_summary.png"), dpi=150, bbox_inches="tight")
    plt.close()


def analyze_standard_scenario(
    scenario: str,
    data: Dict[str, Any],
    config: Dict[str, Any],
    output_dir: str,
    variant: str = "Rule",
) -> Dict[str, Any]:
    """Run standard metrics, validation, plots, and JSON output."""
    _ensure_fundamentals_from_config(data, config)
    metrics = calculate_standard_metrics(data)
    total_rounds = metrics["price_metrics"]["total_rounds"]
    validation = validate_standard_metrics(scenario, metrics, total_rounds)
    create_standard_visualizations(scenario, data, output_dir)
    summary = {
        "scenario": scenario,
        "record_path": config["setting"]["record_path"],
        "total_rounds": total_rounds,
        "metrics": metrics,
        "validation": validation.to_dict(),
    }
    with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print("\n" + "=" * 50)
    print(f"{scenario.upper()} ANALYSIS")
    print("=" * 50)
    print(f"Total Rounds: {total_rounds}  (target: 200 for full experiments)")
    print(
        "Max Abs Deviation: "
        f"{metrics['deviation_metrics']['max_abs_deviation_pct']:.2f}%"
    )
    print(
        "Annualized Volatility: "
        f"{metrics['return_metrics']['annualized_volatility_pct']:.2f}%"
    )
    print(f"\nVALIDATION: {validation.interpretation}")
    print(f"Fit Score: {validation.score:.1%}")

    # ------------------------------------------------------------------
    # Polish Hook 9: universal Layer A baseline. Writes summary.json in
    # the Hook 11 schema (overwriting the legacy summary.json above).
    # ------------------------------------------------------------------
    write_universal_summary(
        data,
        config,
        output_dir,
        scenario=scenario,
        variant=variant,
        extra_summary={
            "scenario_metrics": metrics,
            "validation": validation.to_dict(),
        },
    )
    return summary


def _derive_variant_from_config_path(config_path: str) -> str:
    """Best-effort variant inference from a canonical config path.

    A canonical config path looks like
    ``configs/{Scenario}/{Variant}/simulation.yml``. This helper returns
    the variant if one of the four canonical names appears in the path;
    otherwise returns ``"Rule"`` as the conservative default.
    """
    parts = os.path.normpath(config_path).split(os.sep)
    for candidate in ("RuleLLM", "Rule", "LLM", "Rag"):
        if candidate in parts:
            return candidate
    return "Rule"


def run_standard_analysis(
    scenario: str,
    default_config: str,
    variant: str | None = None,
) -> Dict[str, Any]:
    """Run standard analysis for a scenario config path."""
    parser = argparse.ArgumentParser(description=f"Analyze {scenario} simulation results")
    parser.add_argument("-c", "--config", type=str, default=default_config)
    args = parser.parse_args()
    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)
    results = load_results(config)
    data = _load_data(results)
    resolved_variant = variant or _derive_variant_from_config_path(args.config)
    return analyze_standard_scenario(scenario, data, config, output_dir, resolved_variant)
