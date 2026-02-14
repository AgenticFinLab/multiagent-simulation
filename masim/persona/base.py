"""MASim Persona Layer - Base Classes and Interfaces

The Persona is the PRIMARY EXTERNAL INTERFACE for simulation entities.
Simulator interacts ONLY with Persona - Player/Conductor are hidden internal
implementation details.

================================================================================
                          MODULE CONTENTS
================================================================================

Dataclasses:
    PersonaConfig       - Configuration: auto_checkpoint, debug_mode, env_overrides

Abstract Classes:
    BasePersona         - Abstract base with proxy aggregation and lifecycle hooks

For concrete implementations, see general.py:
    PlayerPersona       - Wraps BasePlayer, exposes operate()
    ConductorPersona    - Wraps BaseConductor, exposes notify()/cycle()

================================================================================
                            ARCHITECTURE
================================================================================

    Simulator ─────► PlayerPersona (Ray Actor)
                          │
                          └──► BasePlayer (internal, hidden)

    Simulator ─────► ConductorPersona (Ray Actor)
                          │
                          └──► BaseConductor (internal, hidden)

Key Design Principles:
    1. ENCAPSULATION: Persona OWNS and hides Player/Conductor
    2. FACADE PATTERN: Persona aggregates all proxies + domain logic
    3. SINGLE INTERFACE: Simulator only sees Persona's operate()/cycle()
    4. INFRASTRUCTURE: All observability, storage, communication via Persona

================================================================================
                        EXECUTION FLOW
================================================================================

PlayerPersona (called by Simulator):
│
└── operate(observation, num_steps)
    │
    └── Player.turn(observation, num_steps)  [internal]
        │
        └── for i in range(num_steps):
            └── Player.step()  [perceive → decide → act]
                └── Returns: StepResult
        └── Returns: TurnResult

ConductorPersona (called by Simulator):
│
├── notify(round_num, player_ids)          # Conductor → Players
│   └── Conductor.notify()  [internal]
│       └── Returns: Dict[player_id → notification_dict]
│
├── receive_responses(responses)               # Players → Conductor (builds response_pool)
│   └── Conductor.on_response_received()  [internal]
│
└── cycle()                                 # Process response_pool
    └── Conductor.cycle()  [internal]
        │
        ├── analyze(responses)   ── Analyze responses and system state
        └── coordinate()         ── Produce CoordinationDecision
        └── Returns: CycleResult

================================================================================
                    PROXY AGGREGATION (Four Proxies)
================================================================================

    BasePersona
        │
        ├── _communication: CommunicationProxy  (send, broadcast, subscribe)
        ├── _storage: StorageProxy              (checkpoint, restore)
        ├── _resource: ResourceProxy            (fetch_resource, invoke_tool)
        └── _observability: ObservabilityProxy  (log_event, record_metric)

Persona exposes convenience methods that delegate to proxies:
    - fetch_resource(uri) → ResourceProxy.fetch()
    - log_event(name, data) → ObservabilityProxy.log_event()
"""

from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from masim.proxy.base import (
        CommunicationProxy,
        StorageProxy,
        ResourceProxy,
        ObservabilityProxy,
    )


# =============================================================================
#                           CONFIGURATION
# =============================================================================


@dataclass
class PersonaConfig:
    """
    Configuration for Persona behavior.

    Kept minimal - complex policies (retry, caching) belong in Proxy layer.
    """

    # Whether to auto-checkpoint after each step/cycle.
    auto_checkpoint: bool = False

    # Enable verbose logging for debugging.
    debug_mode: bool = False

    # Environment variable overrides for Ray actors.
    env_overrides: Dict[str, str] = field(default_factory=dict)


# =============================================================================
#                          BASE PERSONA
# =============================================================================


class BasePersona(ABC):
    """
    Abstract base class for infrastructure coordination.

    Persona serves as the PRIMARY INTERFACE that Simulator interacts with.
    It encapsulates and hides the core domain entity (Player/Conductor)
    while exposing a clean API for simulation orchestration.

    Design Principle:
        Simulator → Persona (visible) → Player/Conductor (hidden)

    Persona is responsible for:
        1. Creating and owning the domain entity
        2. Aggregating all proxy references
        3. Providing operate()/cycle() interface to Simulator
        4. Managing lifecycle (initialize, shutdown)
        5. Infrastructure operations (logging, checkpointing, etc.)
    """

    def __init__(self, config: Optional[PersonaConfig] = None):
        """
        Initialize base Persona.

        Args:
            config: Persona configuration (uses defaults if None)
        """
        # Configuration
        self._config = config or PersonaConfig()

        # Proxy references (Facade aggregation)
        self._communication: Optional["CommunicationProxy"] = None
        self._storage: Optional["StorageProxy"] = None
        self._resource: Optional["ResourceProxy"] = None
        self._observability: Optional["ObservabilityProxy"] = None

        # Lifecycle flags
        self._is_initialized: bool = False

    # =========================================================================
    #                      PROXY ACCESS
    # =========================================================================

    @property
    def communication(self) -> Optional["CommunicationProxy"]:
        """Access CommunicationProxy for message routing."""
        return self._communication

    @property
    def storage(self) -> Optional["StorageProxy"]:
        """Access StorageProxy for state persistence."""
        return self._storage

    @property
    def resource(self) -> Optional["ResourceProxy"]:
        """Access ResourceProxy for MCP resources."""
        return self._resource

    @property
    def observability(self) -> Optional["ObservabilityProxy"]:
        """Access ObservabilityProxy for metrics/logging."""
        return self._observability

    # =========================================================================
    #                    PROXY ATTACHMENT
    # =========================================================================

    def set_communication(self, proxy: "CommunicationProxy") -> None:
        """Attach CommunicationProxy."""
        self._communication = proxy

    def set_storage(self, proxy: "StorageProxy") -> None:
        """Attach StorageProxy."""
        self._storage = proxy

    def set_resource(self, proxy: "ResourceProxy") -> None:
        """Attach ResourceProxy."""
        self._resource = proxy

    def set_observability(self, proxy: "ObservabilityProxy") -> None:
        """Attach ObservabilityProxy."""
        self._observability = proxy

    # =========================================================================
    #                    INFRASTRUCTURE OPERATIONS
    # =========================================================================

    async def fetch_resource(self, uri: str, fallback: Any = None) -> Any:
        """
        Fetch a resource via MCP protocol.

        Args:
            uri: Resource URI (e.g., "mcp://market/prices")
            fallback: Value to return if fetch fails

        Returns:
            Resource data if successful, fallback otherwise
        """
        if not self._resource:
            return fallback

        result = await self._resource.fetch_resource(uri)
        return result.data if result.success else fallback

    async def invoke_tool(
        self, tool_name: str, args: Dict[str, Any], fallback: Any = None
    ) -> Any:
        """
        Invoke an external tool via MCP protocol.

        Args:
            tool_name: Name of the tool
            args: Tool arguments
            fallback: Value to return if invocation fails

        Returns:
            Tool result if successful, fallback otherwise
        """
        if not self._resource:
            return fallback

        result = await self._resource.invoke_tool(tool_name, args)
        return result.data if result.success else fallback

    async def log_event(self, event_name: str, data: Dict[str, Any]) -> None:
        """Log a structured event."""
        if self._observability:
            await self._observability.log_event(event_name, data)

    async def record_metric(self, metric_name: str, value: Any) -> None:
        """Record a metric value."""
        if self._observability:
            await self._observability.record_metric(metric_name, value)
