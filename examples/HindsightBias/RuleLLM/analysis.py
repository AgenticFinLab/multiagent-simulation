"""Analysis utilities for the HindsightBias RuleLLM variant."""

from examples.HindsightBias.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    hindsight_bias_index,
    load_simulation_data,
    narrative_correction_efficiency,
    outcome_bias_index,
    overconfidence_wealth_penalty,
    volatility_amplification_factor,
    wealth_distribution_index,
)
from examples.standard_rule_analysis import run_standard_analysis as _run_standard_analysis


def main():
    """Run HindsightBias RuleLLM analysis using the standard output contract."""
    return _run_standard_analysis(
        "HindsightBias", "configs/HindsightBias/RuleLLM/simulation.yml"
    )

__all__ = [
    "hindsight_bias_index",
    "outcome_bias_index",
    "narrative_correction_efficiency",
    "volatility_amplification_factor",
    "overconfidence_wealth_penalty",
    "wealth_distribution_index",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "main",
]


if __name__ == "__main__":
    main()
