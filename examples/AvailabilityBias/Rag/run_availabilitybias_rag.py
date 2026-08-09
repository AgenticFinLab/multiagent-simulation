#!/usr/bin/env python
"""AvailabilityBias Rag Simulation Runner.

Usage::

    python examples/AvailabilityBias/Rag/run_availabilitybias_rag.py \
        -c configs/AvailabilityBias/Rag/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="AvailabilityBias",
        variant="Rag",
        default_config="configs/AvailabilityBias/Rag/simulation.yml",
        phenomenon="Availability bias price distortions through recent event overweighting and media narratives",
        load_env=True,
    )
