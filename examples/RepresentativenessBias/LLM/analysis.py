"""Analysis utilities for the RepresentativenessBias LLM variant."""

from examples.RepresentativenessBias.Rule.analysis import (
    calculate_metrics,
    compute_agent_attribution,
    compute_base_rate_neglect,
    compute_bayesian_correction,
    compute_bias_onset,
    compute_contrarian_profitability,
    compute_mispricing,
    compute_pattern_volume,
    create_visualizations,
    load_simulation_data,
    main as _rule_main,
)

__all__ = [
    "compute_base_rate_neglect",
    "compute_pattern_volume",
    "compute_mispricing",
    "compute_bayesian_correction",
    "compute_contrarian_profitability",
    "compute_bias_onset",
    "compute_agent_attribution",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
]


def main():
    """Run RepresentativenessBias LLM analysis with the shared Rule pipeline."""
    return _rule_main()


__all__.append("main")


if __name__ == "__main__":
    main()
