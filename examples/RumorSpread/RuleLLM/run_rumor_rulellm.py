#!/usr/bin/env python
"""RumorSpread RuleLLM Simulation Runner.

Usage::

    python examples/RumorSpread/RuleLLM/run_rumor_rulellm.py \
        -c configs/RumorSpread/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="RumorSpread",
        variant="RuleLLM",
        default_config="configs/RumorSpread/RuleLLM/simulation.yml",
        phenomenon="Rumor propagation through serial transmission with distortion",
        load_env=True,
    )
