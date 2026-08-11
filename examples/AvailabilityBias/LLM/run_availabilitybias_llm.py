#!/usr/bin/env python
"""AvailabilityBias LLM Simulation Runner.

Usage::

    python examples/AvailabilityBias/LLM/run_availabilitybias_llm.py \
        -c configs/AvailabilityBias/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AvailabilityBias",
        variant="LLM",
        default_config="configs/AvailabilityBias/LLM/simulation.yml",
        phenomenon="Availability bias price distortions through recent event overweighting and media narratives",
        load_env=True,
    )
