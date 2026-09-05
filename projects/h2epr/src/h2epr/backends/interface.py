"""The backend boundary shared by Rule, LLM, and RuleLLM."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from h2epr.masim_kernel import ActionIntent, MessageIntent


DecisionResult = tuple[ActionIntent, tuple[MessageIntent, ...]]


class DecisionBackend(Protocol):
    backend_name: str
    implementation_id: str

    async def setup(self) -> None:
        """Acquire backend-local resources without changing scientific state."""

    async def decide(
        self, observations: Mapping[str, Mapping[str, object]]
    ) -> dict[str, DecisionResult]:
        """Return exactly one primary intent per active actor."""

    async def shutdown(self) -> None:
        """Release backend-local resources."""

    def decision_projection(self, logical_tick: int, actor_id: str) -> dict[str, Any]:
        """Return the typed, traceable projection of a decision already made."""
