#!/usr/bin/env python
"""LossAversion RuleLLM analysis using the shared behavioral contract."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

from examples.LossAversion.Rule.analysis import (
    analyze_lossaversion,
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
from masim.utils import load_config
from masim.evaluation import write_universal_summary

DEFAULT_CONFIG = "configs/LossAversion/RuleLLM/simulation.yml"


def main() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="Analyze LossAversion RuleLLM results")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()
    config = load_config(args.config)
    data = load_simulation_data(config)
    output_dir = Path(config["setting"]["record_path"]).parent / "analysis"
    # Compute the 36-metric Layer A baseline and write summary.json
    # + four universal PNG dashboards. The variant is derived from
    # the config path so shared-main re-exports still report right.
    _variant = 'RuleLLM'
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
    return analyze_lossaversion(data, config, str(output_dir))


__all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations", "main"]


if __name__ == "__main__":
    main()
