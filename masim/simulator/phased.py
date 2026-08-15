"""Opt-in paired simulator/runner for atomic named-barrier runtimes.

The standard GeneralSimulator is intentionally untouched.  A project injects
an engine implementing the small lifecycle below through SimulationConfig.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from masim.simulator.base import (
    BaseSimulationRunner,
    BaseSimulator,
    RoundPhase,
    SimulationConfig,
    SimulatorStatus,
)


NAMED_BARRIERS = (
    "open_clock",
    "release_due_exogenous_and_timers",
    "build_observations_from_sealed_prestate",
    "operate_participants_in_parallel",
    "collect_all_intents_and_message_intents",
    "validate_and_reduce_intents_atomically",
    "commit_state_and_dispositions",
    "route_due_messages",
    "detect_generated_outcomes_and_stages",
    "validate_and_seal_tick",
)


class PhasedSimulator(BaseSimulator):
    """Adapter from BaseSimulator lifecycle to an injected phased engine."""

    def __init__(self, config: SimulationConfig):
        super().__init__(config)
        factory = config.setting.get("phased_engine_factory")
        if not callable(factory):
            raise ValueError("phased_engine_factory_required")
        self.engine = factory()

    def _launch_player_personas(self) -> Dict[str, Any]:
        return self.engine.launch_participants()

    async def setup(self) -> None:
        self.player_persona_handles = self._launch_player_personas()
        await self.engine.setup(self.player_persona_handles)
        self.status = SimulatorStatus.READY

    async def run(self) -> List[Dict[str, Any]]:
        self.status = SimulatorStatus.RUNNING
        results = []
        for tick in self.engine.logical_ticks:
            results.append(await self.run_round(tick))
        self.status = SimulatorStatus.TERMINATED
        return results

    async def run_round(self, round_num: int) -> Dict[str, Any]:
        self.current_round = round_num
        self.current_phase = RoundPhase.EXECUTING
        result = await self.engine.run_tick(round_num, NAMED_BARRIERS)
        self.current_phase = RoundPhase.COMPLETE
        return result

    async def shutdown(self) -> None:
        await self.engine.shutdown()
        self.status = SimulatorStatus.TERMINATED

    def phase_execute(self, round_num: int, level_handles: Dict[str, Any]) -> Dict[str, Any]:
        return self.engine.phase_execute(round_num, level_handles)

    def phase_collect(self, execute_result: Dict[str, Any]) -> Dict[str, Any]:
        return self.engine.phase_collect(execute_result)

    def phase_dispatch(self, all_info_lists: List[List[Dict[str, Any]]]) -> None:
        self.engine.phase_dispatch(all_info_lists)

    def get_status(self) -> Dict[str, Any]:
        return {"status": self.status.name, "round": self.current_round, "phase": self.current_phase.name}

    def get_round_history(self, round_num: int) -> Optional[Dict[str, Any]]:
        return self.engine.get_tick_result(round_num)

    def get_player_handle(self, player_id: str) -> Optional[Any]:
        return self.player_persona_handles.get(player_id)


class PhasedSimulationRunner(BaseSimulationRunner):
    """Runner paired with PhasedSimulator; projects may bind a subclass."""

    simulator_class = PhasedSimulator

    def _build_simulator(self, config: SimulationConfig) -> BaseSimulator:
        return self.simulator_class(config)
