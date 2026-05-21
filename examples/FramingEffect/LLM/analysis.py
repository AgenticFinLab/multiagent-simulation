"""Analysis utilities for the FramingEffect LLM variant."""

from examples.FramingEffect.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    framing_asymmetry_ratio,
    framing_deviation_index,
    framing_volume_impact,
    load_simulation_data,
    rational_correction_efficiency,
    volatility_amplification_factor,
    wealth_distribution_index,
)
from examples.standard_rule_analysis import run_standard_analysis as _run_standard_analysis


def main():
    """Run FramingEffect LLM analysis using the standard output contract."""
    return _run_standard_analysis(
        "FramingEffect", "configs/FramingEffect/LLM/simulation.yml"
    )

__all__ = [
    "framing_deviation_index",
    "framing_asymmetry_ratio",
    "framing_volume_impact",
    "rational_correction_efficiency",
    "volatility_amplification_factor",
    "wealth_distribution_index",
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "main",
]


if __name__ == "__main__":
    main()
