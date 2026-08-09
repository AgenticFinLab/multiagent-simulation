#!/usr/bin/env python
"""HerdEffect LLM Simulation Runner.

Usage::

    python examples/HerdEffect/LLM/run_herd_llm.py \
        -c configs/HerdEffect/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="HerdEffect",
        variant="LLM",
        default_config="configs/HerdEffect/LLM/simulation.yml",
        phenomenon="Emergent herding from heterogeneous investors converging on shared price-return signals",
        load_env=True,
    )
