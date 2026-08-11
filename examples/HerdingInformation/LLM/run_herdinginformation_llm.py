#!/usr/bin/env python
"""HerdingInformation LLM Simulation Runner.

Usage::

    python examples/HerdingInformation/LLM/run_herdinginformation_llm.py \
        -c configs/HerdingInformation/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="HerdingInformation",
        variant="LLM",
        default_config="configs/HerdingInformation/LLM/simulation.yml",
        phenomenon="Information cascade - individuals ignore private signals and follow the crowd",
        load_env=True,
    )
