#!/usr/bin/env python
"""GFC2008 RuleLLM Simulation Runner.

Usage::

    python examples/GFC2008/RuleLLM/run_gfc2008_rulellm.py \
        -c configs/GFC2008/RuleLLM/simulation.yml
"""

from masim.cli import run

if __name__ == "__main__":
    run(
        scenario="GFC2008",
        variant="RuleLLM",
        default_config="configs/GFC2008/RuleLLM/simulation.yml",
        phenomenon="2007-2009 financial crisis - Housing bubble burst triggered global recession",
        load_env=True,
    )
