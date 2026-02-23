"""Random Value Averaging Demo - Message Passing Architecture

This demonstrates the topology-driven message passing architecture where:
- Coordinator generates a random value and broadcasts to players
- Players receive value, generate local random, compute average, send back
- This repeats for 3 rounds

Data Flow (Level-Based Execution per Round):
1. Level 0 (coordinator): generate value -> broadcast to players
2. Level 1 (players): receive value -> generate local -> average -> respond

Algorithm:
- Round 1: Coordinator generates random(0-1000), sends to players
- Players: receive value V, generate local L, compute avg = (V + L) / 2, send back
- Round 2+: Coordinator receives player averages, computes new value, broadcasts
"""

import logging
import random
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import (
    Action,
    Observation,
    StepResult,
)

logger = logging.getLogger("RandomAvgDemo")


class SimpleCoordinator(GeneralPlayer):
    """
    Coordinator that:
    1. Round 1: Generates random value 0-1000, broadcasts to players
    2. Round 2+: Receives player averages, computes new value, broadcasts
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        """Process received values from players."""
        round_num = observation.round
        print(f"\n[Coordinator] === Round {round_num} ===")
        self.state.custom_state["round"] = round_num

        # Process inbounds from players
        received_values = []
        if observation.inbounds:
            print(f"[Coordinator] Received {len(observation.inbounds)} responses:")
            for inb in observation.inbounds:
                value = inb.payload["average_value"]
                received_values.append(value)
                print(f"  - From {inb.sender_id}: average = {value:.2f}")

        self.state.custom_state["received_values"] = received_values

    async def decide(self) -> Dict[str, Any]:
        """Generate value and declare broadcast message."""
        round_num = self.state.custom_state["round"]
        received_values = self.state.custom_state["received_values"]

        # Generate new value
        if round_num == 1:
            # Round 1: Generate initial random value
            value = random.randint(0, 1000)
            print(f"[Coordinator] Generated initial value: {value}")
        else:
            # Round 2+: Compute average of received values
            value = int(sum(received_values) / len(received_values))
            print(f"[Coordinator] Computed average of {received_values}: {value}")

        self.state.custom_state["current_value"] = value

        # Prepare broadcast message
        message_content = {
            "value": value,
            "round": round_num,
        }

        print(f"[Coordinator] Broadcasting value: {value}")

        return {
            "outbound_messages": [
                {"payload": message_content, "content_type": "value_broadcast"}
            ],
            "broadcast_value": value,
            "round": round_num,
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        """Return action summarizing the broadcast."""
        return Action(
            action_type="coordinator_broadcast",
            payload=decision_payload,
            source_id=self.identity,
            extras={"role": "coordinator"},
        )


class SimplePlayer(GeneralPlayer):
    """
    Player that:
    1. Receives value from coordinator
    2. Generates local random value 0-1000
    3. Computes average of (received + local)
    4. Sends average back to coordinator
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        """Receive value from coordinator."""
        round_num = observation.round
        print(f"\n[{self.identity}] Round {round_num}")
        self.state.custom_state["round"] = round_num

        # Get value from coordinator's inbound
        if observation.inbounds:
            for inb in observation.inbounds:
                received_value = inb.payload["value"]
                self.state.custom_state["received_value"] = received_value
                print(
                    f"[{self.identity}] Received value from {inb.sender_id}: {received_value}"
                )

    async def decide(self) -> Dict[str, Any]:
        """Generate local value, compute average, declare response."""
        round_num = self.state.custom_state["round"]
        received_value = self.state.custom_state["received_value"]

        # Generate local random value
        local_value = random.randint(0, 1000)
        print(f"[{self.identity}] Generated local value: {local_value}")

        # Compute average
        average_value = (received_value + local_value) / 2
        print(
            f"[{self.identity}] Average of ({received_value} + {local_value}) / 2 = {average_value:.2f}"
        )

        # Store for logging
        self.state.custom_state["local_value"] = local_value
        self.state.custom_state["average_value"] = average_value

        # Prepare response
        response = {
            "from": self.identity,
            "round": round_num,
            "received_value": received_value,
            "local_value": local_value,
            "average_value": average_value,
        }

        print(f"[{self.identity}] Sending average {average_value:.2f} to coordinator")

        return {
            **response,
            "outbound_messages": [
                {"payload": response, "content_type": "value_response"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        """Return action with response info."""
        return Action(
            action_type="player_response",
            payload=decision_payload,
            source_id=self.identity,
            extras={"role": "player"},
        )
