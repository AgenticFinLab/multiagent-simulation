#!/usr/bin/env python
"""BlackMonday1987 Rule-Based Simulation Runner.

Usage::

    python examples/BlackMonday1987/Rule/run_blackmonday1987.py \
        -c configs/BlackMonday1987/Rule/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="BlackMonday1987",
        variant="Rule-Based",
        default_config="configs/BlackMonday1987/Rule/simulation.yml",
        phenomenon="October 19, 1987 stock market crash - Dow fell 22.6% in one day",
        load_env=False,
    )
