#!/usr/bin/env python
"""DispositionEffect LLM Simulation Runner.

Usage::

    python examples/DispositionEffect/LLM/run_disposition_llm.py \
        -c configs/DispositionEffect/LLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="DispositionEffect",
        variant="LLM",
        default_config="configs/DispositionEffect/LLM/simulation.yml",
        phenomenon="Loss aversion causes investors to sell winners too early and hold losers too long",
        load_env=True,
    )
