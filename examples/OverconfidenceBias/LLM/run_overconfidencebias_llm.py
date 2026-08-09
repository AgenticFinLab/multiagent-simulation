#!/usr/bin/env python
"""OverconfidenceBias LLM Simulation Runner.

Usage::

    python examples/OverconfidenceBias/LLM/run_overconfidencebias_llm.py \
        -c configs/OverconfidenceBias/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="OverconfidenceBias",
        variant="LLM",
        default_config="configs/OverconfidenceBias/LLM/simulation.yml",
        phenomenon="Overconfidence bias causes traders to overestimate precision and trade excessively",
        load_env=True,
    )
