#!/usr/bin/env python
"""EndowmentEffect LLM Simulation Runner.

Usage::

    python examples/EndowmentEffect/LLM/run_endowmenteffect_llm.py \
        -c configs/EndowmentEffect/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="EndowmentEffect",
        variant="LLM",
        default_config="configs/EndowmentEffect/LLM/simulation.yml",
        phenomenon="Ownership-induced loss aversion suppresses trade volume and inflates transaction prices",
        load_env=True,
    )
