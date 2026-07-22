#!/usr/bin/env python
"""LossAversion analysis with scenario-specific behavioral metrics."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, Tuple

import numpy as np

from masim.evaluation.data_loader import _batch_to_rounds, _load_data
from masim.evaluation.pipeline import (
    calculate_standard_metrics,
    create_standard_visualizations,
)
from masim.utils import load_config, load_results
from masim.evaluation import write_universal_summary


SCENARIO = "LossAversion"
DEFAULT_CONFIG = "configs/LossAversion/Rule/simulation.yml"
STANDARD_OUTPUT_FILES = (
    "summary.json",
    "00_investor_bids.png",
    "01_lossaversion_dynamics.png",
    "02_lossaversion_analysis.png",
    "03_summary.png",
)


def load_simulation_data(config: Dict[str, Any]) -> Dict[str, Any]:
    """Load results into the canonical evaluation data contract."""
    return _load_data(load_results(config))


def _payload(value: Dict[str, Any]) -> Dict[str, Any]:
    nested = value.get("decision_payload") if isinstance(value, dict) else None
    return nested if isinstance(nested, dict) else value


def _iter_agent_payloads(
    data: Dict[str, Any], stem: str
) -> Iterable[Tuple[str, int, Dict[str, Any]]]:
    for agent_id, rounds in data["investor_payloads"].items():
        if stem not in agent_id:
            continue
        for round_num, raw in rounds.items():
            payload = _payload(raw)
            if isinstance(payload, dict):
                yield agent_id, int(round_num), payload


def _configured_lambda(config: Dict[str, Any]) -> float:
    for entry in config["players"].values():
        if "loss_averse_investor" in entry["config"]["identity"]:
            return float(entry["config"]["extras"]["loss_aversion_lambda"])
    raise ValueError("loss-averse investor configuration is missing")


def _disposition_effect(data: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    gain_fractions = []
    loss_fractions = []
    for _, _, payload in _iter_agent_payloads(data, "loss_averse_investor"):
        if payload["action"] != "sell" or float(payload["quantity"]) <= 0:
            continue
        price = float(payload["bid_price"])
        entry = float(payload["entry_price"])
        quantity = float(payload["quantity"])
        post_position = float(payload["position"])
        pre_position = post_position + quantity
        fraction = quantity / pre_position if pre_position > 0 else 0.0
        (gain_fractions if price > entry else loss_fractions).append(fraction)
    gain_rate = mean(gain_fractions) if gain_fractions else 0.0
    loss_rate = mean(loss_fractions) if loss_fractions else 0.0
    index = gain_rate / loss_rate if loss_rate > 0 else (math.inf if gain_rate > 0 else 0.0)
    return index, {
        "mean_gain_realization_fraction": gain_rate,
        "mean_loss_realization_fraction": loss_rate,
        "gain_sell_events": len(gain_fractions),
        "loss_sell_events": len(loss_fractions),
    }


def _break_even_ratio(data: Dict[str, Any]) -> float:
    loss_buys = []
    other_buys = []
    for _, _, payload in _iter_agent_payloads(data, "break_even_trader"):
        if payload["action"] != "buy" or float(payload["quantity"]) <= 0:
            continue
        price = float(payload["bid_price"])
        entry = float(payload["entry_price"])
        quantity = float(payload["quantity"])
        pnl = (price - entry) / entry if entry > 0 else 0.0
        (loss_buys if pnl < 0 else other_buys).append(quantity)
    if not loss_buys:
        return 0.0
    baseline = mean(other_buys) if other_buys else 1.0
    return mean(loss_buys) / max(baseline, 1.0)


def _wealth_penalty(data: Dict[str, Any], config: Dict[str, Any]) -> float:
    prices = data["market_prices"]
    if not prices:
        return 0.0
    final_price = float(prices[max(prices)])

    initial_wealth: Dict[str, float] = {}
    for entry in config["players"].values():
        identity = entry["config"]["identity"]
        extras = entry["config"]["extras"]
        if "initial_cash" in extras:
            initial_wealth[identity] = float(extras["initial_cash"]) + (
                float(extras["initial_position"]) * float(extras["initial_price"])
            )

    def normalized_terminal_wealth(stems: Tuple[str, ...]) -> list[float]:
        wealth_ratios = []
        for agent_id, rounds in data["investor_payloads"].items():
            if not any(stem in agent_id for stem in stems) or not rounds:
                continue
            payload = _payload(rounds[max(rounds)])
            if "cash" in payload and "position" in payload:
                terminal = float(payload["cash"]) + float(payload["position"]) * final_price
                wealth_ratios.append(terminal / initial_wealth[agent_id])
        return wealth_ratios

    biased = normalized_terminal_wealth(("loss_averse_investor", "break_even_trader"))
    rational = normalized_terminal_wealth(("rational_trader",))
    return mean(biased) / mean(rational) if biased and rational and mean(rational) else 0.0


def _volatility_amplification(
    data: Dict[str, Any], shock_rounds: set[int]
) -> float:
    prices = data["market_prices"]
    rounds = sorted(prices)
    if len(rounds) < 3:
        return 0.0
    returns = {
        rounds[i]: (float(prices[rounds[i]]) / float(prices[rounds[i - 1]]) - 1.0)
        for i in range(1, len(rounds))
        if float(prices[rounds[i - 1]]) > 0
    }
    active = set()
    for stem in ("loss_averse_investor", "break_even_trader"):
        for _, round_num, payload in _iter_agent_payloads(data, stem):
            if payload["action"] != "hold" and float(payload["quantity"]) > 0:
                active.add(round_num)
    active_returns = [returns[r] for r in returns if r in active and r not in shock_rounds]
    inactive_returns = [returns[r] for r in returns if r not in active and r not in shock_rounds]
    if len(active_returns) < 2 or len(inactive_returns) < 2:
        return 0.0
    inactive_vol = float(np.std(inactive_returns, ddof=1))
    return float(np.std(active_returns, ddof=1)) / inactive_vol if inactive_vol > 0 else math.inf


def calculate_metrics(
    data: Dict[str, Any], config: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """Calculate structural and LossAversion acceptance metrics."""
    standard_data = dict(data)
    fundamental_series = data["fundamentals"]
    if not fundamental_series:
        raise ValueError("fundamental series is empty")
    standard_data["fundamentals"] = float(
        fundamental_series[min(fundamental_series)]
    )
    metrics = calculate_standard_metrics(standard_data)
    disposition, details = _disposition_effect(data)
    shock_rounds: set[int] = set()
    if config is not None:
        for entry in config["players"].values():
            if entry["config"]["role"] == "coordinator":
                shock_rounds = {
                    int(round_num)
                    for round_num in entry["config"]["extras"]["shock_schedule"]
                }
                break
    metrics.update(
        {
            "loss_aversion_index": _configured_lambda(config) if config else None,
            "disposition_effect_index": disposition,
            "break_even_risk_ratio": _break_even_ratio(data),
            "wealth_penalty_index": _wealth_penalty(data, config) if config else None,
            "volatility_amplification_factor": _volatility_amplification(
                data, shock_rounds
            ),
            **details,
        }
    )
    return metrics


def create_visualizations(data: Dict[str, Any], output_path: str) -> list[str]:
    """Create the fixed standard visualization set."""
    fundamental_series = data["fundamentals"]
    if not fundamental_series:
        raise ValueError("fundamental series is empty")
    standard_data = dict(data)
    standard_data["fundamentals"] = float(
        fundamental_series[min(fundamental_series)]
    )
    return create_standard_visualizations(SCENARIO, standard_data, output_path)


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def analyze_lossaversion(
    data: Dict[str, Any], config: Dict[str, Any], output_dir: str
) -> Dict[str, Any]:
    """Compute metrics, validation, plots, and machine-readable summary."""
    metrics = calculate_metrics(data, config)
    validation = {
        "loss_aversion_index": _finite(metrics["loss_aversion_index"])
        and 1.8 <= metrics["loss_aversion_index"] <= 2.8,
        "disposition_effect_index": _finite(metrics["disposition_effect_index"])
        and metrics["disposition_effect_index"] > 1.0,
        "break_even_risk_ratio": _finite(metrics["break_even_risk_ratio"])
        and metrics["break_even_risk_ratio"] > 1.0,
        "wealth_penalty_index": _finite(metrics["wealth_penalty_index"])
        and metrics["wealth_penalty_index"] < 1.0,
        "volatility_amplification_factor": _finite(
            metrics["volatility_amplification_factor"]
        )
        and 0.1 < metrics["volatility_amplification_factor"] < 4.0,
    }
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    files = create_visualizations(data, str(output))
    summary = {
        "scenario": SCENARIO,
        "metrics": metrics,
        "validation": validation,
        "all_acceptance_metrics_pass": all(validation.values()),
        "output_dir": str(output),
        "files_written": files,
    }
    summary_path = output / "summary.json"
    summary["files_written"].append(str(summary_path))
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'Rule'
    _cfg_path = locals().get('args', None)
    _cfg_path = getattr(_cfg_path, 'config', None) if _cfg_path else None
    if isinstance(_cfg_path, str):
        for _v in ('RuleLLM', 'Rule', 'LLM', 'Rag'):
            if f'/{_v}/' in _cfg_path or _cfg_path.endswith(f'/{_v}'):
                _variant = _v
                break
    _universal = write_universal_summary(
        data,
        config,
        output_dir,
        scenario='LossAversion',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return summary


def main() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Analyze LossAversion results")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    output_dir = Path(config["setting"]["record_path"]).parent / "analysis"
    return analyze_lossaversion(data, config, str(output_dir))


__all__ = [
    "_batch_to_rounds", "_load_data", "load_simulation_data", "calculate_metrics",
    "create_visualizations", "analyze_lossaversion", "STANDARD_OUTPUT_FILES", "main",
]


if __name__ == "__main__":
    main()
