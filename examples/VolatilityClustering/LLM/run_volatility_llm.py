#!/usr/bin/env python
"""VolatilityClustering LLM Simulation Runner.

Usage::

    python examples/VolatilityClustering/LLM/run_volatility_llm.py \
        -c configs/VolatilityClustering/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="VolatilityClustering",
        variant="LLM",
        default_config="configs/VolatilityClustering/LLM/simulation.yml",
        phenomenon="GARCH-like volatility persistence and clustering",
        load_env=True,
    )
