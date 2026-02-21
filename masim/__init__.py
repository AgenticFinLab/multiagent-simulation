"""MASim: Multi-Agent Simulation Framework

A domain-agnostic, behavior-semantics-driven multi-agent collaborative architecture.

Core Design Principles:
1. Role-Based Player Design:
   - All agents are Players with perceive → decide → act pattern
   - Coordinator functionality is a role configuration, not a separate type
   - Players with role='coordinator' handle multi-agent coordination

2. Three-Layer Abstraction Model:
   - Player (What): Core decision logic (HIDDEN)
   - Persona (When): Primary interface for Simulator
   - Proxy (How): Infrastructure primitives

3. Hierarchical Execution Model:
   - Simulator: round (orchestrates Personas)
   - PlayerPersona: operate (calls Player.turn internally)
   - Player: turn (for loop calling step)
   - Player: step (perceive→decide→act)

4. Infrastructure Decoupling via Micro-Proxy Pattern:
   - CommunicationProxy: Message routing and transmission
   - StorageProxy: State checkpoint and rollback
   - ResourceProxy: MCP protocol integration
   - ObservabilityProxy: Metrics and logging

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor) ──► BasePlayer (hidden)

Usage:
    from masim import PlayerPersona, Action
    from masim.communication import Message, MessageType
    from masim.proxy import CommunicationProxy, ResourceProxy
"""

__version__ = "0.0.1"

# Player module
from masim.player import (
    PayloadType,
    ActionStatus,
    Action,
    Observation,
    StepResult,
    TurnResult,
    PlayerConfig,
    PlayerState,
    BasePlayer,
)

# Communication module
from masim.communication import (
    MessageType,
    MessagePriority,
    Message,
    ProtocolOutbound,
    RouteInfo,
    BaseProtocol,
    JsonProtocol,
    MessageRouter,
)

# Proxy module
from masim.proxy import (
    ProxyType,
    ProxyConfig,
    BaseProxy,
    CommunicationConfig,
    CommunicationProxy,
    StorageConfig,
    StorageProxy,
    ResourceConfig,
    ResourceProxy,
    MonitoringConfig,
    MonitoringProxy,
)

# Simulator module
from masim.simulator import (
    SimulatorStatus,
    RoundPhase,
    ExecutionClock,
    SimulationConfig,
    BaseSimulator,
)

# Persona module (infrastructure coordination layer)
from masim.persona import (
    BasePersona,
    PlayerPersona,
)

# Utils module
from masim.utils import (
    load_config,
    validate_config,
    build_connection_matrix,
    ConnectionValidator,
)

__all__ = [
    "__version__",
    # Player types
    "PayloadType",
    "ActionStatus",
    "Action",
    "Observation",
    "StepResult",
    "TurnResult",
    "PlayerConfig",
    "PlayerState",
    "BasePlayer",
    # Communication types
    "MessageType",
    "MessagePriority",
    "Message",
    "ProtocolOutbound",
    "RouteInfo",
    "BaseProtocol",
    "JsonProtocol",
    "MessageRouter",
    # Proxy types
    "ProxyType",
    "ProxyConfig",
    "BaseProxy",
    "CommunicationConfig",
    "CommunicationProxy",
    "StorageConfig",
    "StorageProxy",
    "ResourceConfig",
    "ResourceProxy",
    "MonitoringConfig",
    "MonitoringProxy",
    # Simulator types
    "SimulatorStatus",
    "RoundPhase",
    "ExecutionClock",
    "SimulationConfig",
    "BaseSimulator",
    # Persona types
    "BasePersona",
    "PlayerPersona",
    # Utils
    "load_config",
    "validate_config",
    "build_connection_matrix",
    "ConnectionValidator",
]
