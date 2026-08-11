#!/usr/bin/env python
"""RepresentativenessBias Rule-Based Simulation Runner.

Usage::

    python examples/RepresentativenessBias/Rule/run_representativenessbias.py \
        -c configs/RepresentativenessBias/Rule/simulation.yml
"""

from masim.simulator.general import run

if __name__ == "__main__":
    run(
        scenario="RepresentativenessBias",
        variant="Rule-Based",
        default_config="configs/RepresentativenessBias/Rule/simulation.yml",
        phenomenon="Small-sample pattern matching causes overgeneralization of recent returns as regime shifts",
        load_env=False,
    )
