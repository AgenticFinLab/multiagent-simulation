"""Universal scenario runner — eliminates per-variant boilerplate.

Every standard simulation scenario follows an identical lifecycle:
    parse CLI → load YAML → build SimulationConfig → setup → run → shutdown

The only differences across 180 ``run_*.py`` files are:

* **scenario** — the human-readable scenario name (e.g. ``"ArchegosCollapse"``)
* **variant** — agent variant label (``"Rule"`` / ``"LLM"`` / ``"RuleLLM"`` / ``"Rag"``)
* **default_config** — default path to the YAML config
* **phenomenon** — one-line description printed in the banner (optional)
* **load_env** — whether to call ``dotenv.load_dotenv()`` for API keys

This module provides :func:`run` that encapsulates the shared skeleton so each
variant's ``run_*.py`` collapses to a ~10-line thin shim.

Example thin shim (``examples/ArchegosCollapse/Rule/run_archegsoscollapse.py``)::

    from masim.cli import run

    if __name__ == "__main__":
        run(
            scenario="ArchegosCollapse",
            variant="Rule",
            default_config="configs/ArchegosCollapse/Rule/simulation.yml",
            phenomenon="Archegos lost $20B, triggering block trade fire sales",
            load_env=False,
        )

For complex runners (e.g. Rag variants with knowledge pre-processing), use the
lower-level :func:`create_simulator` helper and add custom phases around it.
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Optional

from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging


_BANNER_WIDTH = 70


def _print_banner(
    scenario: str,
    variant: str,
    total_rounds: int,
    phenomenon: Optional[str] = None,
) -> None:
    """Print the standard simulation startup banner."""
    sep = "=" * _BANNER_WIDTH
    print(f"\n{sep}")
    print(f"{scenario} Simulation - {variant} Agents")
    print(sep)
    if phenomenon:
        print(f"Phenomenon: {phenomenon}")
    print(f"Rounds:     {total_rounds}")
    print(f"{sep}\n")


async def _main(
    *,
    scenario: str,
    variant: str,
    default_config: str,
    phenomenon: Optional[str] = None,
    load_env: bool,
) -> None:
    """Async body shared by every standard scenario runner."""
    if load_env:
        from dotenv import load_dotenv

        load_dotenv()

    setup_logging()

    parser = argparse.ArgumentParser(
        description=f"Run {scenario} {variant} Simulation",
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

    _print_banner(scenario, variant, config.setting["total_rounds"], phenomenon)

    simulator = GeneralSimulator(config)
    try:
        await simulator.setup()
        await simulator.run()
        sep = "=" * _BANNER_WIDTH
        print(f"\n{sep}")
        print("Simulation Complete!")
        print(sep)
    finally:
        await simulator.shutdown()


def run(
    *,
    scenario: str,
    variant: str,
    default_config: str,
    phenomenon: Optional[str] = None,
    load_env: bool = True,
) -> None:
    """Synchronous entry point invoked from each variant's ``run_*.py``.

    Parameters
    ----------
    scenario:
        Human-readable scenario name (e.g. ``"ArchegosCollapse"``).
    variant:
        Variant label for the console banner (e.g. ``"Rule-Based"``,
        ``"LLM"``, ``"RuleLLM"``, ``"Rag"``).
    default_config:
        Config path used when caller omits ``-c``. Always relative from
        project root (e.g. ``"configs/ArchegosCollapse/Rule/simulation.yml"``).
    phenomenon:
        One-line description printed in the banner. Optional — omit for
        shorter output.
    load_env:
        When ``True`` (LLM / RuleLLM / Rag) invoke ``dotenv.load_dotenv``
        before simulation starts. Rule-only variants pass ``False``.
    """
    asyncio.run(
        _main(
            scenario=scenario,
            variant=variant,
            default_config=default_config,
            phenomenon=phenomenon,
            load_env=load_env,
        )
    )


def create_simulator(config_path: str, *, load_env: bool = True) -> GeneralSimulator:
    """Lower-level helper for complex runners that need custom phases.

    Returns a configured but NOT yet setup simulator. The caller is
    responsible for ``await simulator.setup()`` / ``run()`` / ``shutdown()``.

    This is useful for Rag variants that need knowledge pre-processing
    between config loading and simulation start.
    """
    if load_env:
        from dotenv import load_dotenv

        load_dotenv()

    setup_logging()
    yaml_config = load_config(config_path)
    config = SimulationConfig(**yaml_config)
    return GeneralSimulator(config)
