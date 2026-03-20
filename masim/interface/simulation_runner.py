"""Async simulation runner with progress streaming for Streamlit."""

import asyncio
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from masim.simulator.general import GeneralSimulator
from masim.simulator.base import SimulationConfig
from masim.utils.config import load_config, setup_logging


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


class SimulationRunner:
    """Wrapper for running simulations with progress callbacks."""

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

        total_rounds = self.config.setting.get("total_rounds", 1)

        try:
            for round_num in range(1, total_rounds + 1):
                if self._stop_requested:
                    self.status.message = "Simulation stopped by user"
                    break

                # Update status
                self.status.current_round = round_num
                self.status.progress_pct = (round_num / total_rounds) * 100
                self.status.message = f"Running round {round_num}/{total_rounds}..."

                if progress_callback:
                    progress_callback(self.status)

                # Run single round (this is a simplified version)
                # In reality, the simulator.run() runs all rounds at once
                # We need to hook into the simulator's round completion

                # For now, yield a simple update
                update = RoundUpdate(
                    round_num=round_num,
                    total_rounds=total_rounds,
                    agent_actions=[],  # Would need to extract from simulator
                    market_data=None,
                    messages=[],
                )
                yield update

                # Small delay to allow UI updates
                await asyncio.sleep(0.01)

            # Actually run the full simulation
            self.status.message = "Executing simulation..."
            if progress_callback:
                progress_callback(self.status)

            results = await self.simulator.run()

            self.status.state = "completed"
            self.status.progress_pct = 100.0
            self.status.message = "Simulation completed successfully!"
            self.status.current_round = total_rounds

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

    def stop(self):
        """Request simulation stop."""
        self._stop_requested = True
        self.status.message = "Stopping simulation..."


class MockSimulationRunner:
    """Mock runner for testing without actual simulation."""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = None
        self.status = SimulationStatus(state="idle")
        self._stop_requested = False

    async def setup(self) -> bool:
        """Mock setup."""
        try:
            yaml_config = load_config(self.config_path)
            self.config = SimulationConfig(**yaml_config)
            self.status.total_rounds = self.config.setting.get("total_rounds", 50)
            self.status = SimulationStatus(
                state="running", message="Setup complete (mock mode)"
            )
            return True
        except Exception as e:
            self.status = SimulationStatus(
                state="error", error=f"Setup failed: {str(e)}"
            )
            return False

    async def run(
        self, progress_callback: Optional[Callable[[SimulationStatus], None]] = None
    ) -> AsyncGenerator[RoundUpdate, None]:
        """Mock run with simulated progress."""
        total_rounds = (
            self.config.setting.get("total_rounds", 50) if self.config else 50
        )

        for round_num in range(1, total_rounds + 1):
            if self._stop_requested:
                break

            self.status.current_round = round_num
            self.status.progress_pct = (round_num / total_rounds) * 100
            self.status.message = f"Round {round_num}/{total_rounds}"

            if progress_callback:
                progress_callback(self.status)

            # Generate mock agent actions
            agent_actions = self._generate_mock_actions(round_num)

            yield RoundUpdate(
                round_num=round_num,
                total_rounds=total_rounds,
                agent_actions=agent_actions,
                market_data={"price": 100 + round_num * 0.5},
                messages=[],
            )

            # Simulate work
            await asyncio.sleep(0.05)

        self.status.state = "completed"
        self.status.progress_pct = 100.0
        self.status.message = "Mock simulation completed!"

        if progress_callback:
            progress_callback(self.status)

    def _generate_mock_actions(self, round_num: int) -> List[Dict[str, Any]]:
        """Generate mock agent actions for display."""
        import random

        agents = [
            ("Momentum Speculator", "momentum_speculator_1"),
            ("Rational Arbitrageur", "rational_arbitrageur_1"),
            ("Noise Trader", "noise_trader_1"),
            ("Fundamental Investor", "fundamental_investor_1"),
        ]

        actions = []
        for name, agent_id in agents:
            bid = round(random.uniform(95, 105), 2)
            qty = round(random.uniform(-20, 20), 1)
            actions.append(
                {
                    "agent_name": name,
                    "agent_id": agent_id,
                    "bid_price": bid,
                    "quantity": qty,
                    "action": "BUY" if qty > 0 else "SELL" if qty < 0 else "HOLD",
                }
            )

        return actions

    async def shutdown(self):
        """Mock shutdown."""
        pass

    def stop(self):
        """Request stop."""
        self._stop_requested = True


async def run_simulation_with_progress(
    config_path: str, use_mock: bool = False
) -> AsyncGenerator[SimulationStatus, None]:
    """Convenience function to run simulation and yield status updates.

    Args:
        config_path: Path to simulation config
        use_mock: If True, use mock runner for testing

    Yields:
        SimulationStatus updates
    """
    runner = (
        MockSimulationRunner(config_path) if use_mock else SimulationRunner(config_path)
    )

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
