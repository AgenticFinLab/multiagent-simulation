#!/usr/bin/env python
"""OverconfidenceBias Rule-Based Simulation Runner.

Usage::

    python examples/OverconfidenceBias/Rule/run_overconfidencebias.py \
        -c configs/OverconfidenceBias/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="OverconfidenceBias",
        variant="Rule-Based",
        default_config="configs/OverconfidenceBias/Rule/simulation.yml",
        phenomenon="Overconfidence bias causes traders to overestimate precision and trade excessively",
        load_env=False,
    )
