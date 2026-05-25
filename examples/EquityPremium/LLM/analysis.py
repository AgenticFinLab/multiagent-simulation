"""EquityPremium LLM analysis using the stock/bond allocation contract."""

from __future__ import annotations

import argparse
import os
from typing import Any, Dict

from masim.utils import load_config, load_results

from examples.EquityPremium.Rule.analysis import analyze_equity_premium, _load_data


def main() -> Dict[str, Any]:
    """Run EquityPremium LLM analysis."""
    parser = argparse.ArgumentParser(description="Analyze EquityPremium LLM simulation")
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default="configs/EquityPremium/LLM/simulation.yml",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    base_dir = os.path.dirname(config["setting"]["record_path"])
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)
    data = _load_data(results)
    return analyze_equity_premium(data, output_dir)


if __name__ == "__main__":
    main()
