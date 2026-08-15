from __future__ import annotations

import os

from masim.simulator.base import BaseSimulationRunner, BaseSimulator
from masim.simulator.general import GeneralSimulationRunner, GeneralSimulator
from masim.simulator.phased import NAMED_BARRIERS, PhasedSimulationRunner, PhasedSimulator
from h2epr.runtime.runner import (
    H2EPRSimulationRunner,
    H2EPRSimulator,
    _configure_local_only_ray_environment,
)


def test_exact_named_barrier_order() -> None:
    assert NAMED_BARRIERS == (
        "open_clock", "release_due_exogenous_and_timers", "build_observations_from_sealed_prestate",
        "operate_participants_in_parallel", "collect_all_intents_and_message_intents",
        "validate_and_reduce_intents_atomically", "commit_state_and_dispositions", "route_due_messages",
        "detect_generated_outcomes_and_stages", "validate_and_seal_tick",
    )


def test_paired_runtime_uses_masim_base_lifecycle(monkeypatch) -> None:
    assert issubclass(PhasedSimulator, BaseSimulator)
    assert issubclass(PhasedSimulationRunner, BaseSimulationRunner)
    assert H2EPRSimulationRunner.simulator_class is H2EPRSimulator
    monkeypatch.setenv("RAY_ENABLE_WINDOWS_OR_OSX_CLUSTER", "1")
    monkeypatch.setenv("RAY_USAGE_STATS_ENABLED", "1")
    _configure_local_only_ray_environment()
    assert os.environ["RAY_ENABLE_WINDOWS_OR_OSX_CLUSTER"] == "0"
    assert os.environ["RAY_USAGE_STATS_ENABLED"] == "0"


def test_general_pair_remains_distinct_and_importable() -> None:
    assert GeneralSimulationRunner is not H2EPRSimulationRunner
    assert GeneralSimulator is not H2EPRSimulator
