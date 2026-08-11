#!/usr/bin/env python
"""AvailabilityBias Rule-Based Simulation Runner.

Usage::

    python examples/AvailabilityBias/Rule/run_availabilitybias.py \
        -c configs/AvailabilityBias/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AvailabilityBias",
        variant="Rule-Based",
        default_config="configs/AvailabilityBias/Rule/simulation.yml",
        phenomenon="Availability bias price distortions through recent event overweighting and media narratives",
        load_env=False,
    )
