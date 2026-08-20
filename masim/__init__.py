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
   - SendReceiveProxy: Message routing and transmission
   - StorageProxy: State checkpoint and rollback
   - ObservabilityProxy: Metrics and logging

Architecture:
    Simulator ─────► PlayerPersona (Ray Actor) ──► BasePlayer (hidden)

Usage:
    from masim import PlayerPersona, Action, GeneralPlayer
    from masim.communication import Message, MessageType
"""

__version__ = "0.0.1"


def _install_lmbase_output_compatibility() -> None:
    """Let legacy scenarios read a modern InferOutput as ``outputs[0]``.

    Current lmbase releases return one InferOutput directly from ``run()``.
    Older MASim scenarios expect the former batch-shaped result.  Providing a
    read-only compatibility property here keeps both calling conventions
    working without duplicating version checks across every scenario.
    """
    try:
        from lmbase.inference.base import InferOutput
    except ImportError:
        return

    fields = getattr(InferOutput, "__dataclass_fields__", {})
    if "outputs" not in fields and not hasattr(InferOutput, "outputs"):
        setattr(InferOutput, "outputs", property(lambda output: [output]))


_install_lmbase_output_compatibility()

# Player module
from masim.player import (
    PayloadType,
    ActionStatus,
    Action,
    LocalObservation,
    Observation,
    Info,
    StepResult,
    TurnResult,
    PlayerConfig,
    PlayerState,
    BasePlayer,
    GeneralPlayer,
)

# Communication module (message + channel wire layer)
from masim.communication import (
    Message,
    MessageType,
    MessagePriority,
    SimPacket,
    CommunicationChannel,
    GeneralCommunicationChannel,
    build_message_from_info,
)

# Proxy module (infrastructure proxy layer)
from masim.proxy import (
    ProxyType,
    ProxyConfig,
    BaseProxy,
    SendReceiveConfig,
    SendReceiveProxy,
    StorageConfig,
    StorageProxy,
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
)

__all__ = [
    "__version__",
    # Player types
    "PayloadType",
    "ActionStatus",
    "Action",
    "LocalObservation",
    "Observation",
    "Info",
    "StepResult",
    "TurnResult",
    "PlayerConfig",
    "PlayerState",
    "BasePlayer",
    "GeneralPlayer",
    # Communication types (message + channel wire layer)
    "Message",
    "MessageType",
    "MessagePriority",
    "SimPacket",
    "CommunicationChannel",
    "GeneralCommunicationChannel",
    "build_message_from_info",
    # Proxy types (infrastructure proxy layer)
    "ProxyType",
    "ProxyConfig",
    "BaseProxy",
    "SendReceiveConfig",
    "SendReceiveProxy",
    "StorageConfig",
    "StorageProxy",
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
]
