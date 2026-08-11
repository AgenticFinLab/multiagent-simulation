#!/usr/bin/env python
"""AvailabilityBias RuleLLM Simulation Runner.

Usage::

    python examples/AvailabilityBias/RuleLLM/run_availabilitybias_rulellm.py \
        -c configs/AvailabilityBias/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="AvailabilityBias",
        variant="RuleLLM",
        default_config="configs/AvailabilityBias/RuleLLM/simulation.yml",
        phenomenon="Availability bias price distortions through recent event overweighting and media narratives",
        load_env=True,
    )
