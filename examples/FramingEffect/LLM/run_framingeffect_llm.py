#!/usr/bin/env python
"""FramingEffect LLM Simulation Runner.

Usage::

    python examples/FramingEffect/LLM/run_framingeffect_llm.py \
        -c configs/FramingEffect/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="FramingEffect",
        variant="LLM",
        default_config="configs/FramingEffect/LLM/simulation.yml",
        phenomenon="Gain/loss frames elicit asymmetric risk attitudes, generating bias-driven order flow",
        load_env=True,
    )
