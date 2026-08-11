#!/usr/bin/env python
"""RumorSpread Rule-Based Simulation Runner.

Usage::

    python examples/RumorSpread/Rule/run_rumor.py \
        -c configs/RumorSpread/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="RumorSpread",
        variant="Rule-Based",
        default_config="configs/RumorSpread/Rule/simulation.yml",
        phenomenon="Rumor propagation through serial transmission with distortion",
        load_env=False,
    )
