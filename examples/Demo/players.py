"""Simple Coordinator Demo - Message Passing Architecture

This demonstrates the topology-driven message passing architecture where:
- Players declare outbound messages in decide() result
- Persona dispatches messages via topology after operate()
- Players receive messages via on_message() (immediately injected by Persona)
- Players access messages via get_pending_messages()

Data Flow (Level-Based Execution):
1. Level 0 (coordinator): execute -> declare outbound_messages -> dispatch
2. Level 1 (players): receive via on_message() -> perceive() calls get_pending_messages()
3. Messages flow WITHIN THE SAME ROUND (intra-round delivery via ray.get)

Key Design Pattern:
- Notifications = execution triggers (minimal metadata)
- Messages = actual data flow (via message_inbox, immediately injected by Persona)
- Player is PURE domain logic (no infrastructure coupling)
- Routing is topology-driven (Player doesn't specify targets)
- Persona handles ALL communication (receive/send), Player handles logic

Architecture:
- Demo players inherit from GeneralPlayer (general.py) not BasePlayer (base.py)
- base.py = abstract contracts, general.py = ready-to-use implementations
- Player has is_proceed() to check if ready based on received messages
"""

import logging
from typing import Any, Dict, Optional

from masim.player.general import GeneralPlayer
from masim.player.base import (
    Action,
    Observation,
    StepResult,
)

logger = logging.getLogger("SimpleDemo")


class SimpleCoordinator(GeneralPlayer):
    """
    Coordinator that:
    1. Declares broadcast message in decide()
    2. Persona dispatches to all connected players
    3. Receives responses via get_pending_messages()

    Uses declarative message passing:
    - decide() returns 'outbound_messages' list
    - Persona handles actual dispatch via topology
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        """Store round info and check for received responses."""
        round_num = observation.round
        print(f"\n[Coordinator] === Round {round_num} ===")
        self.state.set_custom("round", round_num)

        # Check messages from inbox (immediately injected by Persona via on_message())
        messages = self.get_pending_messages()
        if messages:
            print(
                f"[Coordinator] Received {len(messages)} messages from previous round:"
            )
            for msg in messages:
                print(f"  - From {msg.sender_id}: {msg.payload}")

    async def decide(self) -> Dict[str, Any]:
        """Declare broadcast message to send to all players."""
        round_num = self.state.get_custom("round")
        message_content = {
            "message": f"Hello from Coordinator! Round {round_num}",
            "round": round_num,
        }

        # Get targets for logging
        targets = self.topology_targets
        print(f"[Coordinator] Topology targets: {targets}")
        print("[Coordinator] Declaring broadcast message")

        # Return outbound messages (Persona will dispatch to topology targets)
        return {
            "outbound_messages": [
                {"payload": message_content, "content_type": "broadcast"}
            ],
            "broadcast_targets": len(targets),
            "round": round_num,
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        """Return action summarizing the broadcast."""
        return Action(
            action_type="coordinator_broadcast",
            payload=decision_payload,
            source_id=self.identity,
            metadata={"role": "coordinator"},
        )


class SimplePlayer(GeneralPlayer):
    """
    Player that:
    1. Receives message from coordinator via on_message() (immediate injection)
    2. Accesses messages in perceive() via get_pending_messages()
    3. Declares response message in decide()
    4. Persona dispatches response back to coordinator

    Uses declarative message passing:
    - decide() returns 'outbound_messages' list
    - Persona handles actual dispatch via topology
    """

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        """Check for messages from coordinator."""
        round_num = observation.round
        print(f"\n[{self.identity}] Round {round_num}")
        self.state.set_custom("round", round_num)

        # Check messages from inbox (immediately injected by Persona via on_message())
        messages = self.get_pending_messages()
        if messages:
            print(f"[{self.identity}] Received {len(messages)} messages:")
            for msg in messages:
                print(f"  - From {msg.sender_id}: {msg.payload}")
                self.state.set_custom("coordinator_message", msg.payload)

    async def decide(self) -> Dict[str, Any]:
        """Declare response message to send to coordinator."""
        round_num = self.state.get_custom("round")

        # Increment local counter
        if not self.state.has_custom("local_counter"):
            self.state.set_custom("local_counter", 0)
        counter = self.state.get_custom("local_counter") + 1
        self.state.set_custom("local_counter", counter)

        # Prepare response
        response = {
            "from": self.identity,
            "round": round_num,
            "counter": counter,
            "message": f"Response from {self.identity}, counter={counter}",
        }

        # Check targets for logging
        targets = self.topology_targets
        print(f"[{self.identity}] My targets: {targets}")

        # Declare outbound message (Persona will dispatch to topology targets)
        outbound = []
        if self.can_send_to("coordinator"):
            outbound.append({"payload": response, "content_type": "response"})
            print(
                f"[{self.identity}] Declaring response (will be sent to topology targets)"
            )
        else:
            print(f"[{self.identity}] Cannot send to coordinator (not in topology)")

        return {
            **response,
            "outbound_messages": outbound,
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        """Return action with response info."""
        return Action(
            action_type="player_response",
            payload=decision_payload,
            source_id=self.identity,
            metadata={"role": "player"},
        )
