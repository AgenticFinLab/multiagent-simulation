#!/usr/bin/env python
"""RepresentativenessBias LLM Simulation Runner.

Usage::

    python examples/RepresentativenessBias/LLM/run_representativenessbias_llm.py \
        -c configs/RepresentativenessBias/LLM/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="RepresentativenessBias",
        variant="LLM",
        default_config="configs/RepresentativenessBias/LLM/simulation.yml",
        phenomenon="Small-sample pattern matching causes overgeneralization of recent returns as regime shifts",
        load_env=True,
    )
