#!/usr/bin/env python
"""RepresentativenessBias RuleLLM Simulation Runner.

Usage::

    python examples/RepresentativenessBias/RuleLLM/run_representativenessbias_rulellm.py \
        -c configs/RepresentativenessBias/RuleLLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="RepresentativenessBias",
        variant="RuleLLM",
        default_config="configs/RepresentativenessBias/RuleLLM/simulation.yml",
        phenomenon="Small-sample pattern matching causes overgeneralization of recent returns as regime shifts",
        load_env=True,
    )
