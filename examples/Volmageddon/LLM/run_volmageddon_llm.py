#!/usr/bin/env python
"""Volmageddon LLM Simulation Runner.

Usage::

    python examples/Volmageddon/LLM/run_volmageddon_llm.py \
        -c configs/Volmageddon/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="Volmageddon",
        variant="LLM",
        default_config="configs/Volmageddon/LLM/simulation.yml",
        phenomenon="February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours",
        load_env=True,
    )
