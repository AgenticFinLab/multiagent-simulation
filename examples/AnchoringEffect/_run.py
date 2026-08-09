"""Shared CLI runner for AnchoringEffect variants.

The four variants (Rule / LLM / RuleLLM / Rag) share an identical simulation
lifecycle: parse ``-c CONFIG``, load YAML → :class:`SimulationConfig`,
instantiate :class:`GeneralSimulator`, await ``setup → run → shutdown``.
Only three surface details differ across variants:

* the default config path,
* the human-readable variant label printed to the console,
* whether ``dotenv`` needs to be loaded for LLM-provider credentials.

This module centralises the shared skeleton so each variant's ``run_*.py``
collapses to a one-line entry point that supplies its own defaults. No
scenario-specific logic lives here — the variant shims stay authoritative
for their own defaults.
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Optional

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging

_PHENOMENON = (
    "Anchoring causes traders to insufficiently adjust from reference "
    "prices, creating slow price discovery"
)


async def _main(*, variant: str, default_config: str, load_env: bool) -> None:
    """Async body shared by every AnchoringEffect variant runner.

    Parameters
    ----------
    variant:
        Console-facing label used in the header banner (e.g. ``"Rule-Based"``,
        ``"LLM"``, ``"RuleLLM"``, ``"Rag"``).
    default_config:
        Path used when the caller does not pass ``-c``. Always a relative
        path under ``configs/AnchoringEffect/{Variant}/simulation.yml``.
    load_env:
        When ``True`` (LLM / RuleLLM / Rag) invoke ``dotenv.load_dotenv``
        so provider API keys enter the process env before :class:`Runner`
        instantiates the LLM client. Rule-only variants pass ``False``.
    """
    if load_env:
        # dotenv is a soft dep — only pull it in when actually needed so
        # the pure-rule path stays import-cheap.
        from dotenv import load_dotenv
        load_dotenv()
    setup_logging()

    parser = argparse.ArgumentParser(
        description=f"Run AnchoringEffect {variant} Simulation",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=default_config,
        help="Path to the simulation YAML config",
    )
    args = parser.parse_args()

    yaml_config = load_config(args.config)
    config = SimulationConfig(**yaml_config)

    banner = "=" * 70
    print(f"\n{banner}")
    print(f"AnchoringEffect Simulation - {variant} Agents")
    print(banner)
    print(f"Phenomenon: {_PHENOMENON}")
    print(f"Rounds:     {config.setting['total_rounds']}")
    print(banner + "\n")

    simulator = GeneralSimulator(config)
    try:
        await simulator.setup()
        await simulator.run()
        print(f"\n{banner}")
        print("Simulation Complete!")
        print(banner)
    finally:
        await simulator.shutdown()


def run(*, variant: str, default_config: str, load_env: bool = True) -> None:
    """Synchronous entry point invoked from each variant's ``run_*.py``.

    ``load_env`` defaults to ``True`` because three of the four variants
    are LLM-backed; the pure-rule shim opts out explicitly.
    """
    asyncio.run(_main(
        variant=variant,
        default_config=default_config,
        load_env=load_env,
    ))
