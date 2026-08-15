"""One generic MASim Player shell and its narrow Persona owner."""

from __future__ import annotations

import copy
from typing import Any, Mapping

from masim.integrations.event_process import ObservationEnvelope
from masim.player.base import Action, LocalObservation, Observation, PlayerConfig
from masim.player.general import GeneralPlayer

from .policy import RulePolicyV1


class RuleParticipantPlayer(GeneralPlayer):
    """A single shell parameterized by ParticipantArtifact/action-space data."""

    def __init__(self, config: PlayerConfig):
        super().__init__(config)
        self.policy = RulePolicyV1(
            config.identity,
            tuple(config.extras["allowed_actions"]),
            config.extras["run_id"],
            config.extras["run_seed"],
        )

    async def perceive(self, observation: Observation, prev_result=None) -> None:
        self.state.custom_state["observation"] = copy.deepcopy(observation.data)

    async def decide(self) -> dict[str, Any]:
        action, messages = self.policy.decide(self.state.custom_state["observation"])
        return {
            "action_intent": action.to_dict(),
            "message_intents": [item.to_dict() for item in messages],
        }

    async def act(self, decision_payload: dict[str, Any]) -> Action:
        tick = decision_payload["action_intent"]["logical_tick"]
        return Action(
            action_type="event_process_intent_batch",
            payload=copy.deepcopy(decision_payload),
            source_id=self.identity,
            timestamp=f"logical-tick:{tick}",
            extras={"scientific_timestamp": "logical_only", "schema": "h2epr.g3.intent_batch.v1"},
        )

    async def operate_envelope(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        validated = ObservationEnvelope(**envelope)
        observation = Observation(
            local=LocalObservation(data=validated.to_dict(), timestamp=f"logical-tick:{validated.logical_tick}"),
            inbounds=[],
            round=validated.logical_tick,
        )
        result = await self.step(observation)
        return {
            "actor_id": self.identity,
            "decision_record": copy.deepcopy(result.decision_payload),
            "action": result.action.to_dict(),
            "operation_count": self.state.step_count,
        }


class RuleParticipantPersona:
    """Ray actor boundary: owns and hides one RuleParticipantPlayer."""

    def __init__(self, player_config: dict[str, Any]):
        self.player = RuleParticipantPlayer(PlayerConfig(**player_config))

    async def initialize(self) -> None:
        await self.player.initialize()

    async def operate(self, envelope: Mapping[str, Any]) -> dict[str, Any]:
        return await self.player.operate_envelope(copy.deepcopy(dict(envelope)))

    async def shutdown(self) -> None:
        await self.player.shutdown()
