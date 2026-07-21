#!/usr/bin/env python
"""OverconfidenceBias LLM analysis using the standard output contract."""

from __future__ import annotations

import argparse
from typing import Any, Dict

from examples.OverconfidenceBias.Rule.analysis import (
    SCENARIO,
    analyze_overconfidencebias,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from masim.utils import load_config
from masim.evaluation import write_universal_summary

DEFAULT_CONFIG = "configs/OverconfidenceBias/LLM/simulation.yml"


def main(config_path: str | None = None) -> Dict[str, Any]:
    """Run OverconfidenceBias LLM analysis."""
    if config_path is None:
        parser = argparse.ArgumentParser(description="OverconfidenceBias LLM analysis")
        parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
        args = parser.parse_args()
        config_path = args.config
    config = load_config(config_path)
    data = load_simulation_data(config)
    output_dir = config["setting"]["record_path"].rsplit("/", 1)[0] + "/analysis"
    # [polish-hook-9] universal baseline invocation
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'LLM'
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
        scenario='OverconfidenceBias',
        variant=_variant,
        extra_summary={'scenario_metrics': summary}
            if isinstance(summary, dict) else None,
    )
    return analyze_overconfidencebias(data, config, output_dir)


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
