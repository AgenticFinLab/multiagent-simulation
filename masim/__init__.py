"""MASim: Multi-Agent Simulation Framework

A domain-agnostic, behavior-semantics-driven multi-agent collaborative architecture.

Core Design Principles:
1. Role Semantics via Behavioral Contracts:
   - Player outputs Action (directly interpreted by environment)
   - Conductor outputs CoordinationDecision (influences Players indirectly)

2. Three-Layer Abstraction Model:
   - Player/Conductor (What): Core decision logic (HIDDEN)
   - Persona (When): Primary interface for Simulator
   - Proxy (How): Infrastructure primitives

3. Hierarchical Execution Model:
   - Simulator: round (orchestrates Personas)
   - PlayerPersona: operate (calls Player.turn internally)
   - Player: turn (for loop calling step)
   - Player: step (perceive→decide→act)
   - ConductorPersona: cycle (calls Conductor.cycle internally)

4. Infrastructure Decoupling via Micro-Proxy Pattern:
   - CommunicationProxy: Message routing and transmission
   - StorageProxy: State checkpoint and rollback
   - ResourceProxy: MCP protocol integration
   - ObservabilityProxy: Metrics and logging

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor) ──► BasePlayer (hidden)
    Simulator ─────► ConductorPersona (Ray Actor) ──► BaseConductor (hidden)

Usage:
    from masim import PlayerPersona, ConductorPersona, Action, CoordinationDecision
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

# Conductor module
from masim.conductor import (
    DecisionScope,
    CoordinationDecision,
    CycleResult,
    ConductorConfig,
    ConductorState,
    BaseConductor,
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
    ObservabilityConfig,
    ObservabilityProxy,
    ProxyFactory,
)

# Simulator module
from masim.simulator import (
    SimulatorStatus,
    RoundPhase,
    ExecutionClock,
    RayConfig,
    SimulationConfig,
    BaseSimulator,
)

# Persona module (infrastructure coordination layer)
from masim.persona import (
    BasePersona,
    PlayerPersona,
    ConductorPersona,
    PersonaConfig,
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
    # Conductor types
    "DecisionScope",
    "CoordinationDecision",
    "CycleResult",
    "ConductorConfig",
    "ConductorState",
    "BaseConductor",
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
    "ObservabilityConfig",
    "ObservabilityProxy",
    "ProxyFactory",
    # Simulator types
    "SimulatorStatus",
    "RoundPhase",
    "ExecutionClock",
    "RayConfig",
    "SimulationConfig",
    "BaseSimulator",
    # Persona types
    "BasePersona",
    "PlayerPersona",
    "ConductorPersona",
    "PersonaConfig",
]
