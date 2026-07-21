"""EchoChamber Simulation Analysis

Analyzes echo chamber polarization simulation results, including opinion
dynamics, cluster separation, and polarize/depolarize activity.

Detects:
    - Polarization amplification and persistence
    - Cluster separation growth (echo chamber formation)
    - Depolarization effectiveness lag
    - Opinion convergence vs polarization divergence

Usage:
    python -m examples.EchoChamber.Rule.analysis -c configs/EchoChamber/Rule/simulation.yml
"""

import argparse
import json
import os
from typing import Any, Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from masim.utils.config import load_config
from masim.evaluation import write_universal_summary


def load_simulation_data(config: dict) -> dict:
    """Load simulation data from experiment records.

    Reads the opinion environment agent's batch stores for polarization,
    mean_opinion, cluster_separation, polarize_count, and depolarize_count
    time series.

    Returns:
        dict with keys: polarization, mean_opinion, cluster_separation,
        polarize_count, depolarize_count, agent_opinions (dict mapping
        agent_id -> opinion list)
    """
    record_path = config["setting"]["record_path"]
    data = {
        "polarization": [],
        "mean_opinion": [],
        "cluster_separation": [],
        "polarize_count": [],
        "depolarize_count": [],
        "agent_opinions": {},
    }

    env_path = os.path.join(record_path, "environment")
    if not os.path.isdir(env_path):
        raise FileNotFoundError(
            f"Environment records not found at {env_path}. Run the simulation first."
        )
    for metric in [
        "polarization",
        "mean_opinion",
        "cluster_separation",
        "polarize_count",
        "depolarize_count",
    ]:
        metric_path = os.path.join(env_path, metric)
        data[metric] = _load_metric_values(metric_path)

    agent_ids = [agent_id for agent_id in config["players"] if agent_id != "environment"]
    for agent_id in sorted(agent_ids):
        opinion_path = os.path.join(record_path, agent_id, "opinion")
        data["agent_opinions"][agent_id] = _load_metric_values(opinion_path)

    if not data["agent_opinions"]:
        raise ValueError(f"No agent opinion records found under {record_path}")

    return data


def _load_metric_values(metric_path: str) -> List[float]:
    """Load sorted metric values from a batch store directory."""
    if not os.path.isdir(metric_path):
        raise FileNotFoundError(f"Required metric directory not found: {metric_path}")
    values = []

    files = [
        filename
        for filename in os.listdir(metric_path)
        if filename.startswith("batch_block_") and filename.endswith(".json")
    ]
    files.sort(
        key=lambda filename: int(filename.removeprefix("batch_block_").removesuffix(".json"))
    )

    for filename in files:
        filepath = os.path.join(metric_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
            if isinstance(content, list):
                values.extend(content)
            elif isinstance(content, dict):
                for block_values in content.values():
                    if isinstance(block_values, list):
                        values.extend(block_values)
                    elif isinstance(block_values, (int, float)):
                        values.append(float(block_values))
                    else:
                        raise TypeError(
                            f"Unsupported metric block in {filepath}: {type(block_values)}"
                        )
            elif isinstance(content, (int, float)):
                values.append(float(content))
            else:
                raise TypeError(f"Unsupported metric payload in {filepath}: {type(content)}")

    if not values:
        raise ValueError(f"No metric values found in {metric_path}")

    return values


def _require_numeric_series(values: List[float], metric_name: str) -> np.ndarray:
    """Return a finite numeric series or fail with a useful contract error."""
    if not values:
        raise ValueError(f"{metric_name} must contain at least one value")
    series = np.asarray(values, dtype=float)
    if not np.all(np.isfinite(series)):
        raise ValueError(f"{metric_name} contains non-finite values")
    return series


def compute_polarization_amplification(polarization: List[float]) -> float:
    """Compute peak polarization divided by its positive initial level."""
    series = _require_numeric_series(polarization, "polarization")
    if series[0] <= 0.0:
        raise ValueError("initial polarization must be positive for amplification")
    return float(np.max(series) / series[0])


def compute_polarization_persistence(polarization: List[float]) -> float:
    """Compute mean polarization over the second half of the run."""
    series = _require_numeric_series(polarization, "polarization")
    return float(np.mean(series[len(series) // 2 :]))


def compute_cluster_separation(cluster_series: List[float]) -> Dict[str, float]:
    """Summarize maximum, final, and mean cluster separation."""
    series = _require_numeric_series(cluster_series, "cluster_separation")
    return {
        "max": float(np.max(series)),
        "final": float(series[-1]),
        "average": float(np.mean(series)),
    }


def compute_polarize_activity(polarize_counts: List[int]) -> float:
    """Return the total number of polarizing actions."""
    series = _require_numeric_series(polarize_counts, "polarize_count")
    return float(np.sum(series))


def compute_depolarize_activity(depolarize_counts: List[int]) -> float:
    """Return the total number of depolarizing actions."""
    series = _require_numeric_series(depolarize_counts, "depolarize_count")
    return float(np.sum(series))


def compute_opinion_dispersion(agent_opinions: Dict[str, List[float]]) -> float:
    """Compute population standard deviation of agents' terminal opinions."""
    if not agent_opinions:
        raise ValueError("agent_opinions must contain at least one agent")
    terminal = [
        _require_numeric_series(values, f"opinion[{agent_id}]")[-1]
        for agent_id, values in sorted(agent_opinions.items())
    ]
    return float(np.std(terminal))


def compute_api_quality(
    actions: List[Dict[str, Any]], rag_contexts: List[str]
) -> Dict[str, float]:
    """Validate special-schema actions and report optional RAG coverage."""
    if not actions:
        raise ValueError("actions must contain at least one action")
    valid_types = {"polarize", "neutral", "depolarize"}
    valid_count = 0
    for action in actions:
        if action["action_type"] in valid_types and 0.0 <= action["intensity"] <= 1.0:
            valid_count += 1
    retrieval_coverage = 0.0
    if rag_contexts:
        retrieval_coverage = sum(bool(context.strip()) for context in rag_contexts) / len(
            rag_contexts
        )
    return {
        "valid_action_rate": valid_count / len(actions),
        "retrieval_coverage": retrieval_coverage,
    }


def calculate_metrics(data: dict) -> dict:
    """Calculate echo chamber polarization simulation metrics.

    Args:
        data: Simulation data from load_simulation_data.

    Returns:
        dict with polarization, opinion, cluster, and activity metrics.
    """
    polarization = _require_numeric_series(data["polarization"], "polarization")
    mean_opinion = _require_numeric_series(data["mean_opinion"], "mean_opinion")
    cluster_separation = _require_numeric_series(
        data["cluster_separation"], "cluster_separation"
    )
    polarize_count = _require_numeric_series(data["polarize_count"], "polarize_count")
    depolarize_count = _require_numeric_series(
        data["depolarize_count"], "depolarize_count"
    )

    lengths = {
        len(polarization), len(mean_opinion), len(cluster_separation),
        len(polarize_count), len(depolarize_count)
    }
    if len(lengths) != 1:
        raise ValueError(f"Environment metric lengths disagree: {sorted(lengths)}")

    total_rounds = len(polarization)

    peak_polarization = float(np.max(polarization))
    peak_round = int(np.argmax(polarization))
    final_polarization = float(polarization[-1])

    polarization_persistence = compute_polarization_persistence(data["polarization"])
    polarization_amplification = compute_polarization_amplification(
        data["polarization"]
    )
    cluster_metrics = compute_cluster_separation(data["cluster_separation"])
    total_polarize = compute_polarize_activity(data["polarize_count"])
    total_depolarize = compute_depolarize_activity(data["depolarize_count"])
    avg_polarize = float(np.mean(polarize_count))
    avg_depolarize = float(np.mean(depolarize_count))
    if total_polarize == 0.0:
        raise ValueError("depolarize/polarize ratio is undefined: no polarize actions")
    depolarize_ratio = total_depolarize / total_polarize

    depolarize_lag = 0.0
    if len(polarize_count) > 5 and len(depolarize_count) > 5:
        cross_corr = np.correlate(
            polarize_count - np.mean(polarize_count),
            depolarize_count - np.mean(depolarize_count),
            mode="full",
        )
        n = len(polarize_count)
        lags = np.arange(-n + 1, n)
        pos_mask = lags >= 0
        if np.any(pos_mask):
            pos_corr = cross_corr[pos_mask]
            pos_lags = lags[pos_mask]
            if len(pos_corr) > 0:
                depolarize_lag = float(pos_lags[np.argmax(pos_corr)])

    final_mean_opinion = float(mean_opinion[-1])

    return {
        "polarization": {
            "initial": float(polarization[0]),
            "peak": peak_polarization,
            "peak_round": peak_round,
            "final": final_polarization,
            "persistence_second_half": round(polarization_persistence, 4),
            "amplification_ratio": round(polarization_amplification, 4),
        },
        "opinion": {
            "final_mean": round(final_mean_opinion, 4),
        },
        "cluster": {
            "max_separation": round(cluster_metrics["max"], 4),
            "final_separation": round(cluster_metrics["final"], 4),
            "avg_separation": round(cluster_metrics["average"], 4),
        },
        "activity": {
            "total_polarize_events": round(total_polarize, 1),
            "total_depolarize_events": round(total_depolarize, 1),
            "avg_polarize_per_round": round(avg_polarize, 2),
            "avg_depolarize_per_round": round(avg_depolarize, 2),
            "depolarize_to_polarize_ratio": round(depolarize_ratio, 4),
            "depolarize_lag_rounds": round(depolarize_lag, 1),
        },
        "opinion_dispersion": round(
            compute_opinion_dispersion(data["agent_opinions"]), 4
        ),
        "total_rounds": total_rounds,
    }


def create_visualizations(data: dict, output_dir: str) -> None:
    """Create analysis plots for echo chamber simulation.

    Generates:
        1. Polarization dynamics over time
        2. Mean opinion and cluster separation over time
        3. Polarize vs depolarize activity per round
        4. Per-agent opinion trajectories (showing echo chamber formation)
    """
    polarization = _require_numeric_series(data["polarization"], "polarization")
    mean_opinion = _require_numeric_series(data["mean_opinion"], "mean_opinion")
    cluster_separation = _require_numeric_series(
        data["cluster_separation"], "cluster_separation"
    )
    polarize_count = _require_numeric_series(data["polarize_count"], "polarize_count")
    depolarize_count = _require_numeric_series(
        data["depolarize_count"], "depolarize_count"
    )

    rounds = np.arange(len(polarization))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "EchoChamber Simulation Analysis",
        fontsize=14,
        fontweight="bold",
    )

    # Panel 1: Polarization dynamics
    axes[0, 0].plot(
        rounds, polarization, color="red", linewidth=2, label="Polarization Index"
    )
    axes[0, 0].axhline(
        y=0.5,
        color="gray",
        linestyle="--",
        linewidth=1,
        alpha=0.5,
        label="High Polarization Threshold",
    )
    axes[0, 0].fill_between(
        rounds,
        polarization,
        alpha=0.15,
        color="red",
    )
    axes[0, 0].set_title("Population Polarization Over Time")
    axes[0, 0].set_xlabel("Round")
    axes[0, 0].set_ylabel("Polarization Index")
    axes[0, 0].set_ylim(-0.05, 1.05)
    axes[0, 0].legend(loc="upper left", fontsize=8)
    axes[0, 0].grid(True, alpha=0.3)

    # Panel 2: Mean opinion and cluster separation
    if len(mean_opinion) > 0:
        ax2a = axes[0, 1]
        ax2b = ax2a.twinx()
        ax2a.plot(rounds, mean_opinion, color="blue", linewidth=2, label="Mean Opinion")
        ax2a.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)
        ax2a.set_ylabel("Mean Opinion", color="blue")
        ax2a.set_ylim(-1.1, 1.1)
        if len(cluster_separation) > 0:
            ax2b.plot(
                rounds,
                cluster_separation,
                color="orange",
                linewidth=2,
                label="Cluster Separation",
            )
            ax2b.set_ylabel("Cluster Separation", color="orange")
            ax2b.set_ylim(-0.05, 2.1)
        ax2a.set_title("Mean Opinion & Cluster Separation")
        ax2a.set_xlabel("Round")
        lines1, labels1 = ax2a.get_legend_handles_labels()
        lines2, labels2 = ax2b.get_legend_handles_labels()
        ax2a.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=8)
        ax2a.grid(True, alpha=0.3)

    # Panel 3: Polarize vs Depolarize activity
    if len(polarize_count) > 0 and len(depolarize_count) > 0:
        bar_width = max(1, len(rounds) // 50)
        axes[1, 0].bar(
            rounds,
            polarize_count,
            width=bar_width,
            color="red",
            alpha=0.6,
            label="Polarize Actions",
        )
        axes[1, 0].bar(
            rounds,
            -depolarize_count,
            width=bar_width,
            color="green",
            alpha=0.6,
            label="Depolarize Actions",
        )
        axes[1, 0].axhline(y=0, color="black", linewidth=0.5)
        axes[1, 0].set_title("Polarize vs Depolarize Activity")
        axes[1, 0].set_xlabel("Round")
        axes[1, 0].set_ylabel("Number of Agents")
        axes[1, 0].legend(loc="upper right", fontsize=8)
        axes[1, 0].grid(True, alpha=0.3)

    # Panel 4: Per-agent opinion trajectories
    agent_opinions = data["agent_opinions"]
    # pylint: disable=no-member
    colors = plt.cm.coolwarm(np.linspace(0, 1, max(len(agent_opinions), 1)))
    for idx, (agent_id, agent_opinion) in enumerate(sorted(agent_opinions.items())):
        agent_series = _require_numeric_series(agent_opinion, f"opinion[{agent_id}]")
        agent_rounds = np.arange(len(agent_series))
        color_val = (agent_series[-1] + 1) / 2  # Map [-1,1] to [0,1]
        axes[1, 1].plot(
            agent_rounds,
            agent_series,
            # pylint: disable=no-member
            color=plt.cm.coolwarm(color_val),
            alpha=0.6,
            linewidth=1,
            label=agent_id[:15],
        )
    axes[1, 1].axhline(y=0, color="black", linestyle="--", linewidth=1, alpha=0.7)
    axes[1, 1].set_title("Individual Agent Opinion Trajectories")
    axes[1, 1].set_xlabel("Round")
    axes[1, 1].set_ylabel("Personal Opinion")
    axes[1, 1].set_ylim(-1.1, 1.1)
    if len(agent_opinions) <= 10:
        axes[1, 1].legend(loc="upper right", fontsize=6, ncol=2)
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    output_paths = [
        os.path.join(output_dir, "00_investor_bids.png"),
        os.path.join(output_dir, "01_echochamber_dynamics.png"),
        os.path.join(output_dir, "02_echochamber_analysis.png"),
        os.path.join(output_dir, "03_summary.png"),
    ]
    for output_path in output_paths:
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved analysis plots to {output_dir}")


def main():
    """Run EchoChamber analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze EchoChamber simulation results",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EchoChamber/Rule/simulation.yml",
        help="Path to simulation configuration file (YAML)",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    data = load_simulation_data(config)

    metrics = calculate_metrics(data)

    analysis_dir = os.path.join(os.path.dirname(config["setting"]["record_path"]), "analysis")
    os.makedirs(analysis_dir, exist_ok=True)

    create_visualizations(data, analysis_dir)

    polarization_values = _require_numeric_series(data["polarization"], "polarization")
    opinion_values = [
        value for values in data["agent_opinions"].values() for value in values
    ]
    opinions = _require_numeric_series(opinion_values, "agent_opinions")
    polarization_in_bounds = bool(
        np.all((polarization_values >= 0.0) & (polarization_values <= 1.0))
    )
    opinions_in_bounds = bool(np.all((opinions >= -1.0) & (opinions <= 1.0)))
    is_valid = polarization_in_bounds and opinions_in_bounds
    score = float(polarization_in_bounds + opinions_in_bounds) / 2.0
    status_text = "VALID" if is_valid else "INVALID"
    validation = {
        "score": score,
        "is_valid": is_valid,
        "criteria": {
            "Polarization Bounds": {
                "value": [float(np.min(polarization_values)), float(np.max(polarization_values))],
                "target": "all values in [0, 1]",
                "passed": polarization_in_bounds,
            },
            "Opinion Bounds": {
                "value": [float(np.min(opinions)), float(np.max(opinions))],
                "target": "all values in [-1, 1]",
                "passed": opinions_in_bounds,
            },
        },
        "interpretation": f"=== ECHO CHAMBER SIMULATION VALIDATION: {status_text} ===",
    }
    metrics["validation"] = validation
    summary = {
        "scenario": "EchoChamber",
        "total_rounds": metrics["total_rounds"],
        "metrics": metrics,
        "validation": validation,
    }
    summary_path = os.path.join(analysis_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 50)
    print("ECHO CHAMBER ANALYSIS")
    print("=" * 50)
    if metrics:
        p = metrics["polarization"]
        cl = metrics["cluster"]
        a = metrics["activity"]
        print(f"Peak Polarization: {p['peak']:.3f} (round {p['peak_round']})")
        print(f"Final Polarization: {p['final']:.3f}")
        print(f"Amplification: {p['amplification_ratio']:.2f}x from initial")
        print(f"Max Cluster Separation: {cl['max_separation']:.3f}")
        print(f"Final Cluster Separation: {cl['final_separation']:.3f}")
        print(f"Depolarize/Polarize Ratio: {a['depolarize_to_polarize_ratio']:.3f}")
        print(f"Depolarize Lag: {a['depolarize_lag_rounds']:.0f} rounds")
    print(f"\nResults saved to {analysis_dir}")
    # [polish-hook-9] universal baseline invocation
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
        scenario='EchoChamber',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )



__all__ = [
    "load_simulation_data",
    "compute_polarization_amplification",
    "compute_polarization_persistence",
    "compute_cluster_separation",
    "compute_polarize_activity",
    "compute_depolarize_activity",
    "compute_opinion_dispersion",
    "compute_api_quality",
    "calculate_metrics",
    "create_visualizations",
]


if __name__ == "__main__":
    main()
