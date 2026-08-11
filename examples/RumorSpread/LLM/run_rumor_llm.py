#!/usr/bin/env python
"""RumorSpread LLM Simulation Runner.

Usage::

    python examples/RumorSpread/LLM/run_rumor_llm.py \
        -c configs/RumorSpread/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="RumorSpread",
        variant="LLM",
        default_config="configs/RumorSpread/LLM/simulation.yml",
        phenomenon="Rumor propagation through serial transmission with distortion",
        load_env=True,
    )
