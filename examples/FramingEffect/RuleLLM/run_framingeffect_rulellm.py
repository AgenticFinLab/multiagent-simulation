#!/usr/bin/env python
"""FramingEffect RuleLLM Simulation Runner.

Usage::

    python examples/FramingEffect/RuleLLM/run_framingeffect_rulellm.py \
        -c configs/FramingEffect/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="FramingEffect",
        variant="RuleLLM",
        default_config="configs/FramingEffect/RuleLLM/simulation.yml",
        phenomenon="Gain/loss frames elicit asymmetric risk attitudes, generating bias-driven order flow",
        load_env=True,
    )
