#!/usr/bin/env python
"""CurrencyCrisis Rule-Based Simulation Runner.

Usage::

    python examples/CurrencyCrisis/Rule/run_currencycrisis.py \
        -c configs/CurrencyCrisis/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="CurrencyCrisis",
        variant="Rule-Based",
        default_config="configs/CurrencyCrisis/Rule/simulation.yml",
        phenomenon="Self-fulfilling speculative attacks deplete central-bank reserves and force peg abandonment",
        load_env=False,
    )
