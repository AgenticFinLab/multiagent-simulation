"""Simulation runner with two execution modes: Default and Customized.

This module is the central orchestration layer for running multi-agent
financial simulations. It supports two workflows:

Workflows
---------

1. **Default mode** — run a shipped scenario as-is:

   ```python
   import asyncio
   from masim.interface.simulation_runner import SimulationRunner

   async def main():
       runner = SimulationRunner.from_scenario("AssetBubble", variant="Rule")
       if not await runner.setup():
           return
       async for update in runner.run():
           print(f"Round {update.round_num}")
       await runner.shutdown()

   asyncio.run(main())
   ```

2. **Customized mode** — pick agents from AGENT_POOL, generate a bundle, run:

   ```python
   from masim.interface.simulation_runner import SimulationRunner
   from masim.interface.customized import CustomizedAgentSelection

   selections = [
       CustomizedAgentSelection(
           archetype="noise-trader", display_name="Noise Trader",
           engine="Rule", params={}, num_instances=3,
       ),
       CustomizedAgentSelection(
           archetype="momentum-trader", display_name="Momentum Trader",
           engine="LLM", params={}, num_instances=2,
       ),
   ]
   runner = SimulationRunner.from_customized("AssetBubble", selections)
   ```

3. **Via Streamlit Web UI (Recommended):**

   Launch the web interface and select a scenario:

   ```bash
   cd /path/to/multiagent-simulation
   streamlit run masim/interface/app.py
   ```

   Then:
   - Stage 1: Select a scenario from the grid (e.g., AssetBubble, HerdEffect)
   - Stage 2: Click a variant chip (Default) or "Customize my roster" (Customized)
   - View real-time progress and results in the simulation workspace

4. **Discovery helpers** (standalone, no Streamlit needed):

   ```python
   from masim.interface.simulation_runner import (
       discover_available_scenarios,
       discover_variants,
       list_agent_pool,
   )

   scenarios = discover_available_scenarios()   # ['AnchoringEffect', ...]
   variants = discover_variants("AssetBubble")  # ['Rule', 'LLM', 'RuleLLM']
   agents = list_agent_pool()                   # [{'name': 'noise-trader', ...}, ...]
   ```

Classes
-------
- SimulationRunner: Main async runner with factory constructors
- RoundUpdate: Dataclass for per-round updates
- SimulationStatus: Dataclass for simulation state

Integration
-----------
- Used by: masim/interface/app.py (Streamlit web UI)
- Depends on: masim/simulator/general.py, masim/interface/customized/
- Progress callbacks enable real-time UI updates in Streamlit
"""

import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

import ray

logger = logging.getLogger(__name__)

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig, SimulatorStatus
from masim.utils.config import load_config, setup_logging


# ---------------------------------------------------------------------------
# Directory constants
# ---------------------------------------------------------------------------

_CONFIGS_DIR = project_root / "configs"
_EXAMPLES_DIR = project_root / "examples"
_AGENT_POOL_DIR = project_root / "masim" / "agents" / "defines"
_EXCLUDED_DIRS = {"TEMPLATES", "__pycache__", "Demo", "CUSTOMIZED_SIMULATION"}


# ---------------------------------------------------------------------------
# Scenario & agent discovery utilities
# ---------------------------------------------------------------------------


# NOTE: The former _customized_bundle_import_root / _prepend_python_path
# helpers (which injected examples/CUSTOMIZED_SIMULATION/{bundle}/ into
# sys.path + PYTHONPATH + Ray runtime_env for short-path imports like
# "Rule.players:Market") were deleted. All yaml references in bundles are
# now full dotted paths (examples.CUSTOMIZED_SIMULATION.{bundle}.Default.…)
# and the file-based fallback in masim.agents._base._load_module_by_file /
# masim.utils.config.load_class resolves them without any sys.path mutation.


def discover_available_scenarios() -> List[str]:
    """List all scenario names available under configs/.

    Returns:
        Sorted list of scenario base names (e.g. ['AnchoringEffect', 'AssetBubble', ...]).
    """
    if not _CONFIGS_DIR.exists():
        return []
    return sorted(
        d.name
        for d in _CONFIGS_DIR.iterdir()
        if d.is_dir() and d.name not in _EXCLUDED_DIRS and not d.name.startswith(".")
    )


def discover_variants(scenario_name: str) -> List[str]:
    """List variants (Rule, LLM, RuleLLM, Rag) available for a scenario.

    Args:
        scenario_name: Base scenario name (e.g. 'AssetBubble').

    Returns:
        List of variant names that have a simulation.yml, e.g. ['Rule', 'LLM'].
    """
    scenario_dir = _CONFIGS_DIR / scenario_name
    if not scenario_dir.exists():
        return []
    return sorted(
        d.name
        for d in scenario_dir.iterdir()
        if d.is_dir() and (d / "simulation.yml").exists()
    )


def list_agent_pool() -> List[Dict[str, Any]]:
    """List available agent archetypes from masim/agents/defines/finance/.

    Each entry contains:
        - name: filename stem (e.g. 'noise-trader')
        - path: absolute path to the .md file
        - archetype: extracted from the Summary table (or derived from name)
        - time_horizon: extracted from Summary table if present
        - risk_tolerance: extracted from Summary table if present

    Returns:
        List of agent metadata dicts, sorted by name.
    """
    finance_dir = _AGENT_POOL_DIR / "finance"
    if not finance_dir.exists():
        return []

    agents: List[Dict[str, Any]] = []
    for md_file in sorted(finance_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        agents.append({
            "name": md_file.stem,
            "path": str(md_file),
            "archetype": _extract_field(content, "Archetype") or md_file.stem,
            "time_horizon": _extract_field(content, "Time Horizon") or "",
            "risk_tolerance": _extract_field(content, "Risk Tolerance") or "",
        })
    return agents


def _extract_field(markdown: str, field: str) -> str:
    """Extract a value from a markdown Summary table row."""
    pattern = rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|\s*$"
    match = re.search(pattern, markdown, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


@dataclass
class RoundUpdate:
    """Update from a single simulation round."""

    round_num: int
    total_rounds: int
    agent_actions: List[Dict[str, Any]]
    market_data: Optional[Dict[str, Any]] = None
    messages: List[Dict[str, Any]] = None


@dataclass
class SimulationStatus:
    """Current status of simulation."""

    state: str  # "idle", "running", "completed", "error"
    current_round: int = 0
    total_rounds: int = 0
    progress_pct: float = 0.0
    message: str = ""
    error: Optional[str] = None
    elapsed_seconds: float = 0.0
    eta_seconds: Optional[float] = None
    average_round_seconds: Optional[float] = None


class SimulationRunner:
    """Async simulation runner with Default and Customized mode support.

    Construction:
        - ``SimulationRunner(config_path)``          — direct config path
        - ``SimulationRunner.from_scenario(name)``   — Default mode (shipped scenario)
        - ``SimulationRunner.from_customized(...)``  — Customized mode (AGENT_POOL)
    """

    def __init__(self, config_path: str):
        """Initialize runner with config path.

        Args:
            config_path: Path to simulation.yml config file
        """
        self.config_path = config_path
        self.simulator: Optional[GeneralSimulator] = None
        self.config: Optional[SimulationConfig] = None
        self.status = SimulationStatus(state="idle")
        self._stop_requested = False

    # ------------------------------------------------------------------
    # Factory constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_scenario(
        cls, scenario_name: str, variant: str = "Rule"
    ) -> "SimulationRunner":
        """Default mode: run a shipped scenario from configs/.

        Resolves *scenario_name* + *variant* to the corresponding
        ``configs/{scenario_name}/{variant}/simulation.yml``.

        Args:
            scenario_name: Base scenario name (e.g. 'AssetBubble').
            variant: Decision-engine variant ('Rule', 'LLM', 'RuleLLM', 'Rag').

        Returns:
            A configured SimulationRunner ready for ``setup()`` → ``run()``.

        Raises:
            FileNotFoundError: When the resolved config file does not exist.
        """
        config_path = _CONFIGS_DIR / scenario_name / variant / "simulation.yml"
        if not config_path.exists():
            raise FileNotFoundError(
                f"No simulation config found at {config_path}. "
                f"Available variants for '{scenario_name}': "
                f"{discover_variants(scenario_name) or '(none)'}"
            )
        return cls(str(config_path))

    @classmethod
    def from_customized(
        cls,
        scenario_name: str,
        agent_selections: List[Any],
    ) -> "SimulationRunner":
        """Customized mode: build a bundle from AGENT_POOL selections, then run.

        Generates a self-contained simulation bundle via
        :func:`masim.interface.customized.write_customized_bundle`, then
        returns a runner pointing at the generated config.

        Args:
            scenario_name: Base scenario to inherit market/round settings from.
            agent_selections: List of ``CustomizedAgentSelection`` objects
                describing the chosen agents, engines, and parameters.

        Returns:
            A configured SimulationRunner whose ``config_path`` points to
            the freshly generated ``simulation.yml``.

        Raises:
            ValueError: Roster is incompatible with the chosen scenario.
            FileNotFoundError: Base scenario config is missing.
        """
        from masim.interface.customized import write_customized_bundle

        result = write_customized_bundle(
            selections=agent_selections,
            scenario_name=scenario_name,
            project_root=project_root,
        )
        return cls(str(result.simulation_yaml))

    async def setup(self) -> bool:
        """Setup the simulation.

        Returns:
            True if setup successful
        """
        try:
            self.status = SimulationStatus(
                state="running", message="Loading configuration..."
            )

            yaml_config = load_config(self.config_path)
            self.config = SimulationConfig(**yaml_config)

            self.status.total_rounds = self.config.setting.get("total_rounds", 0)

            self.simulator = GeneralSimulator(self.config)
            await self.simulator.setup()

            self.status.message = "Setup complete, starting simulation..."
            return True

        except Exception as e:
            self.status = SimulationStatus(
                state="error", error=f"Setup failed: {str(e)}"
            )
            return False

    def clear_records(self) -> None:
        """Remove existing experiment records so the simulation starts fresh.

        Can be called BEFORE ``setup()`` — reads ``record_path`` directly from
        the YAML config file.  Removes the directory tree and recreates it empty.
        """
        import shutil

        import yaml as _yaml

        try:
            with open(self.config_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            # Strip !include directives so yaml.safe_load doesn't choke
            lines = []
            for line in content.split("\n"):
                if "!include" in line:
                    key = line.split(":")[0]
                    lines.append(f"{key}: {{}}")
                else:
                    lines.append(line)
            raw = _yaml.safe_load("\n".join(lines))
            record_path = (raw or {}).get("setting", {}).get("record_path", "")
        except Exception:
            record_path = ""

        if not record_path:
            return
        # record_path is relative to project root
        abs_record = project_root / record_path
        if abs_record.exists():
            shutil.rmtree(abs_record)
            logger.info("Cleared previous records at %s", abs_record)
        abs_record.mkdir(parents=True, exist_ok=True)

    async def run(
        self, progress_callback: Optional[Callable[[SimulationStatus], None]] = None
    ) -> AsyncGenerator[RoundUpdate, None]:
        """Run simulation with progress updates.

        Args:
            progress_callback: Optional callback for status updates

        Yields:
            RoundUpdate for each completed round
        """
        if not self.simulator or not self.config:
            self.status = SimulationStatus(state="error", error="Simulation not set up")
            if progress_callback:
                progress_callback(self.status)
            return

        total_rounds = self.config.setting["total_rounds"]
        record_path = self.config.setting["record_path"]

        try:
            # Mirror GeneralSimulator.run() resume detection, but execute the
            # rounds here so progress updates represent completed real work.
            completed_on_disk = self.simulator._detect_resume_round(record_path)
            start_round = completed_on_disk + 1
            run_started = time.monotonic()
            completed_this_run = 0
            self.simulator.status = SimulatorStatus.RUNNING

            if start_round > total_rounds:
                self.status = SimulationStatus(
                    state="completed",
                    current_round=total_rounds,
                    total_rounds=total_rounds,
                    progress_pct=100.0,
                    message="All rounds already exist on disk.",
                    elapsed_seconds=0.0,
                    eta_seconds=0.0,
                    average_round_seconds=0.0,
                )
                return

            for round_num in range(start_round, total_rounds + 1):
                if self._stop_requested:
                    self.status.state = "stopped"
                    self.status.message = "Simulation stopped by user"
                    break

                await self.simulator.run_round(round_num)
                completed_this_run += 1
                elapsed = time.monotonic() - run_started
                average_round_seconds = elapsed / completed_this_run
                eta_seconds = average_round_seconds * (total_rounds - round_num)

                # Update only after a real round has completed.
                self.status.state = "running"
                self.status.current_round = round_num
                self.status.total_rounds = total_rounds
                self.status.progress_pct = (round_num / total_rounds) * 100
                self.status.elapsed_seconds = elapsed
                self.status.eta_seconds = eta_seconds
                self.status.average_round_seconds = average_round_seconds
                self.status.message = f"Completed real round {round_num}/{total_rounds}"

                if progress_callback:
                    progress_callback(self.status)

                update = RoundUpdate(
                    round_num=round_num,
                    total_rounds=total_rounds,
                    agent_actions=[],
                    market_data=None,
                    messages=[],
                )
                yield update

            if not self._stop_requested:
                self.simulator.status = SimulatorStatus.TERMINATED
                self.status.state = "completed"
                self.status.progress_pct = 100.0
                self.status.message = "Simulation completed successfully!"
                self.status.current_round = total_rounds
                self.status.eta_seconds = 0.0

                if progress_callback:
                    progress_callback(self.status)

        except Exception as e:
            self.status = SimulationStatus(
                state="error", error=f"Simulation failed: {str(e)}"
            )
            if progress_callback:
                progress_callback(self.status)
            raise

    async def shutdown(self):
        """Shutdown the simulator."""
        if self.simulator:
            await self.simulator.shutdown()
            self.simulator = None
        if ray.is_initialized():
            ray.shutdown()

    def stop(self):
        """Request simulation stop."""
        self._stop_requested = True
        self.status.message = "Stopping simulation..."


async def run_simulation_with_progress(
    config_path: str,
) -> AsyncGenerator[SimulationStatus, None]:
    """Convenience function to run simulation and yield status updates.

    Args:
        config_path: Path to simulation config

    Yields:
        SimulationStatus updates
    """
    runner = SimulationRunner(config_path)

    # Setup
    if not await runner.setup():
        yield runner.status
        return

    # Run with status callback
    def on_status_update(status: SimulationStatus):
        # This is called internally, we capture via the generator
        pass

    try:
        async for update in runner.run(on_status_update):
            yield runner.status
    except Exception as e:
        runner.status.state = "error"
        runner.status.error = str(e)
        yield runner.status
    finally:
        await runner.shutdown()

    # Final status
    yield runner.status
