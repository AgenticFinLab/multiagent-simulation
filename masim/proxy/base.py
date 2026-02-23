"""
Base Proxy module for the Multi-Agent Simulation (MASim) framework.

This module provides abstract base classes and type definitions ONLY.
For concrete implementations, see `general.py`.

================================================================================
                          MODULE CONTENTS
================================================================================

Protocols:
    ObservableEntity     - Minimal interface for proxy owners (identity, save_state, etc.)

Dataclasses:
    ProxyResult          - Result wrapper for graceful degradation (success, data, error)
    SendReceiveConfig  - Config for SendReceiveProxy
    StorageConfig        - Config for StorageProxy
    ResourceConfig       - Config for ResourceProxy
    ObservabilityConfig  - Config for MonitoringProxy

Abstract Classes:
    BaseProxy            - Abstract base with owner weak reference pattern
    SendReceiveProxy   - Message routing: send, broadcast, subscribe
    StorageProxy         - State persistence: checkpoint, restore
    ResourceProxy        - MCP integration: fetch_resource, invoke_tool
    ObservabilityProxy   - Metrics/logging: log_event, record_metric

================================================================================
                           MODULE OVERVIEW
================================================================================

This module defines the four micro-proxy types that provide infrastructure
abstraction for Player entities (including coordinators):

    1. SendReceiveProxy - Message routing and reliable transmission
    2. StorageProxy       - State checkpoint and rollback
    3. ResourceProxy      - MCP (Model Context Protocol) connection management
    4. ObservabilityProxy - Metrics collection and structured logging

Key Components:
    - ObservableEntity: Protocol defining the minimal interface for proxy owners
    - ProxyResult: Result wrapper for graceful degradation
    - BaseProxy: Abstract base class for all proxy types
    - Four concrete proxy implementations

================================================================================
                      CORE DESIGN PHILOSOPHY
================================================================================

1. MICRO-PROXY PATTERN
   -------------------
   Each proxy has SINGLE RESPONSIBILITY with ≤5 core methods.

   Why "micro"?
   - Easy to understand (focused interface)
   - Easy to test (mock single proxy)
   - Easy to replace (swap implementations)
   - Easy to extend (add new proxy types)

   ┌─────────────────────────────────────────────────────────────────────┐
   │                    MICRO-PROXY INTERFACES                           │
   │                                                                     │
   │  SendReceiveProxy: send, broadcast, receive, subscribe, unsubscribe
   │  StorageProxy:       checkpoint, restore, list, delete, get_latest  │
   │  ResourceProxy:      fetch, invoke, list, connect, disconnect       │
   │  ObservabilityProxy: record_metric, log_event, start/stop_timer    │
   └─────────────────────────────────────────────────────────────────────┘

2. COMPOSITION OVER INHERITANCE
   ----------------------------
   Proxies are COMPOSED into entities (Players), not inherited.

   ┌───────────────────────────────────────────────────────────────────┐
   │  Owner (Player - may have role='coordinator' or 'player')        │
   │      │                                                            │
   │      │  ┌─────────────────────┐                                  │
   │      ├──│ SendReceiveProxy  │──┐                               │
   │      │  └─────────────────────┘  │                               │
   │      │  ┌─────────────────────┐  │                               │
   │      ├──│ StorageProxy        │──│ Each proxy holds             │
   │      │  └─────────────────────┘  │ WEAK REFERENCE               │
   │      │  ┌─────────────────────┐  │ back to owner                │
   │      ├──│ ResourceProxy       │──│                               │
   │      │  └─────────────────────┘  │                               │
   │      │  ┌─────────────────────┐  │                               │
   │      └──│ ObservabilityProxy  │──┘                               │
   │         └─────────────────────┘                                  │
   └───────────────────────────────────────────────────────────────────┘

   Benefits:
   - Clear ownership (owner controls proxy lifecycle)
   - No circular references (weak ref in proxy → owner)
   - Explicit assembly (no DI container magic)
   - Testable (inject mock proxies)

3. WEAK REFERENCE PATTERN
   ----------------------
   Proxies hold WEAK references to their owners to prevent memory leaks.

   Problem (without weak ref):
       Owner ────strong ref────► Proxy
       Proxy ────strong ref────► Owner  ← CIRCULAR! Neither can be GC'd

   Solution (with weak ref):
       Owner ────strong ref────► Proxy
       Proxy ────weak ref──────► Owner  ← Owner can be GC'd, proxy auto-invalidates

   Implementation:
       self._owner_ref = weakref.ref(owner)  # Weak reference
       owner = self._owner_ref()              # Returns None if GC'd

4. FAULT ISOLATION (ProxyResult Pattern)
   ------------------------------------
   Proxy failures MUST NOT crash the owner entity.

   ┌─────────────────────────────────────────────────────────────────────┐
   │                    FAULT ISOLATION PRINCIPLE                        │
   │                                                                     │
   │  Traditional (raises exception):                                   │
   │      try:                                                          │
   │          result = proxy.fetch_resource(uri)  # May throw!         │
   │      except ProxyError:                                            │
   │          # Owner must handle every possible exception             │
   │                                                                     │
   │  MASim Pattern (returns ProxyResult):                              │
   │      result = await proxy.fetch_resource(uri)  # Never throws     │
   │      if result.success:                                            │
   │          data = result.data                                        │
   │      else:                                                         │
   │          # Graceful degradation with error info                   │
   │          log(result.error_code, result.error_message)             │
   └─────────────────────────────────────────────────────────────────────┘

5. BACKEND AGNOSTIC
   ----------------
   Proxy interfaces hide implementation details (Ray, gRPC, Redis, etc.)

   The same proxy interface can be implemented with different backends:

   ┌────────────────────────────────────────────────────────────────────┐
   │  StorageProxy Interface                                            │
   │      │                                                             │
   │      ├──► MemoryStorageProxy (in-memory, for testing)             │
   │      ├──► FileStorageProxy (local filesystem)                     │
   │      ├──► RedisStorageProxy (distributed cache)                   │
   │      └──► S3StorageProxy (cloud object storage)                   │
   └────────────────────────────────────────────────────────────────────┘

================================================================================
                      ACCESS CONTROL (ObservableEntity)
================================================================================

Proxies can only access SPECIFIC methods on the owner, defined by the
ObservableEntity protocol. This is ACCESS CONTROL - proxies cannot call
arbitrary owner methods.

┌─────────────────────────────────────────────────────────────────────────────┐
│                     ACCESS CONTROL MATRIX                                    │
│                                                                              │
│  Proxy Type          │ Allowed Owner Access        │ Purpose                │
│  ────────────────────┼─────────────────────────────┼───────────────────────│
│  SendReceiveProxy  │ identity, on_message()      │ Message routing       │
│  StorageProxy        │ identity, save_state(),     │ State persistence     │
│                      │ load_state()                │                        │
│  ResourceProxy       │ identity, capabilities    │ Access control        │
│  ObservabilityProxy  │ identity, get_system_metrics()│ Monitoring          │
│                      │                               │                        │
│                                                                              │
│  Proxies CANNOT access:                                                      │
│  ✗ _internal_strategy()    ✗ _compute_decision()    ✗ _private_cache       │
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
                      PLAYER ROLE-BASED PROXY STRATEGIES
================================================================================

While all proxies share the same interface, implementations can differ
based on the Player's role (coordinator vs regular player):

┌─────────────────────────────────────────────────────────────────────────────┐
│              DIFFERENTIATED PROXY STRATEGIES                                 │
│                                                                              │
│  Proxy Type      │ Regular Player Strategy   │ Coordinator Strategy         │
│  ────────────────┼───────────────────────────┼─────────────────────────────│
│  Communication   │ Point-to-point optimized  │ Broadcast/aggregate optimized│
│                  │ Low latency focus         │ High throughput focus        │
│  ────────────────┼───────────────────────────┼─────────────────────────────│
│  Storage         │ Private, encrypted        │ Global, version-controlled  │
│                  │ Per-step checkpointing    │ Distributed snapshots       │
│  ────────────────┼───────────────────────────┼─────────────────────────────│
│  Resource        │ Capability-filtered       │ Global coordination         │
│                  │ Local caching             │ Request deduplication       │
│  ────────────────┼───────────────────────────┼─────────────────────────────│
│  Observability   │ Individual behavior audit │ System-level aggregation    │
│                  │ Strategy performance      │ Coordination impact analysis│
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
                          LIFECYCLE MANAGEMENT
================================================================================

Proxy lifecycle is tied to owner lifecycle through three phases:

    ┌────────────────────────────────────────────────────────────────────┐
    │  Phase 1: INITIALIZE                                               │
    │    - Owner creates proxy (or factory creates)                     │
    │    - Owner calls attach_*_proxy(proxy)                            │
    │    - Proxy records weak reference to owner                        │
    │    - Owner calls proxy.initialize() to setup resources           │
    │                                                                    │
    │  Phase 2: RUNTIME                                                  │
    │    - Owner calls proxy methods (send, checkpoint, fetch, etc.)   │
    │    - Proxy may callback owner (on_message, load_state)           │
    │    - All operations return ProxyResult (no exceptions)           │
    │                                                                    │
    │  Phase 3: SHUTDOWN                                                 │
    │    - Owner calls proxy.shutdown() to cleanup resources           │
    │    - Proxy flushes pending data (metrics, logs)                  │
    │    - When owner is GC'd, proxy weak ref becomes invalid          │
    └────────────────────────────────────────────────────────────────────┘

================================================================================
                           USAGE EXAMPLE
================================================================================

    # 1. Create proxy with configuration
    storage_config = StorageConfig(
        storage_backend="memory",
        max_checkpoints=50,
        encrypt_state=True  # Player privacy
    )
    storage_proxy = StorageProxy(storage_config)

    # 2. Attach to owner (establishes weak reference)
    player.attach_storage_proxy(storage_proxy)

    # 3. Initialize proxy resources
    await storage_proxy.initialize()

    # 4. Use proxy with graceful degradation
    result = await storage_proxy.checkpoint(label="before_trade")
    if result.success:
        checkpoint_id = result.data
        logger.info("    Checkpoint created: %s", checkpoint_id)
    else:
        logger.warning("    Checkpoint failed: %s", result.error_code)
        # Continue execution - don't crash!

    # 5. Shutdown when done
    await storage_proxy.shutdown()

================================================================================
"""

import weakref
from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Protocol,
    runtime_checkable,
    TYPE_CHECKING,
)

from masim.communication.base import Message

# ---------------------------------------------------------------------------
# TYPE_CHECKING Block
# ---------------------------------------------------------------------------
# These imports are only for static type checking (mypy, IDE hints).
# At runtime, they are NOT imported to avoid circular dependencies.
#
# Why this pattern?
# - proxy/base.py needs to reference Player types for type hints
# - But player/base.py imports from proxy/base.py
# - Circular import at runtime would crash Python
# - TYPE_CHECKING is False at runtime, True during type checking
# ---------------------------------------------------------------------------
if TYPE_CHECKING:
    from masim.player.base import BasePlayer


# =============================================================================
#            OBSERVABLE ENTITY PROTOCOL (ACCESS CONTROL INTERFACE)
# =============================================================================
#
# This protocol defines the MINIMAL INTERFACE that proxy owners must implement.
# It serves as an ACCESS CONTROL mechanism - proxies can ONLY access these
# methods, not arbitrary owner internals.
#
# Key Design Decisions:
# 1. @runtime_checkable enables isinstance() checks at runtime
# 2. Protocol (not ABC) allows structural subtyping (duck typing)
# 3. Minimal interface - only methods proxies actually need
# =============================================================================


@runtime_checkable
class ObservableEntity(Protocol):
    """
    Protocol defining the minimal interface for proxy owners.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                   OBSERVABLE ENTITY PROTOCOL                        │
    │                                                                     │
    │  This is the ACCESS CONTROL boundary between proxies and owners.   │
    │  Proxies can ONLY call methods defined in this protocol.           │
    │                                                                     │
    │  Any class implementing these methods can have proxies attached:   │
    │  - BasePlayer implements ObservableEntity                            │
    │  - Players with role='coordinator' also implement ObservableEntity   │
    │  - Test mocks can implement ObservableEntity                       │
    └─────────────────────────────────────────────────────────────────────┘

    Benefits of Protocol-based Access Control:
    ------------------------------------------
    1. EXPLICIT BOUNDARIES: Clear contract of what proxies can access
    2. TESTABILITY: Mock objects need only implement this interface
    3. DECOUPLING: Proxies don't depend on concrete Player classes
    4. DOCUMENTATION: Protocol IS the documentation of proxy-owner interface

    Access Control Matrix:
    ----------------------
    | Method             | Used By               | Purpose                    |
    |--------------------|-----------------------|----------------------------|
    | identity           | All proxies           | Entity identification      |
    | on_message()       | SendReceiveProxy    | Message delivery callback  |
    | save_state()       | StorageProxy          | Get state for checkpoint   |
    | load_state()       | StorageProxy          | Restore state from checkpoint|
    | capabilities      | ResourceProxy         | Access control for resources|
    """

    @property
    def identity(self) -> str:
        """
        Unique identifier for the entity.

        Used by:
            - All proxies for logging and tracking
            - Message routing (sender_id, recipient_id)
            - Checkpoint storage keys
            - Metrics tagging

        Returns:
            Unique string identifier (typically UUID or semantic ID)
        """
        ...

    def on_message(self, message: Message) -> None:
        """
        Callback invoked when a message arrives (SendReceiveProxy).

        This method is called by SendReceiveProxy when a message
        is delivered to this entity. The owner decides how to handle it.

        Args:
            message: The received Message object

        Note:
            This should NOT raise exceptions - failures should be
            handled internally to maintain fault isolation.
        """
        ...

    def save_state(self) -> Dict[str, Any]:
        """
        Return state that should be persisted (StorageProxy).

        Called by StorageProxy.checkpoint() to get the current state
        for persistence. The returned dict must be serializable.

        Returns:
            Dictionary of serializable state data

        Guidelines:
            - Include all state needed to restore entity behavior
            - Exclude transient caches that can be rebuilt
            - Exclude proxy references (not serializable)
            - Keep size reasonable for frequent checkpointing
        """
        ...

    def load_state(self, state: Dict[str, Any]) -> None:
        """
        Restore state from persisted data (StorageProxy).

        Called by StorageProxy.restore() to apply a previously
        checkpointed state. Must validate all required keys are present.

        Args:
            state: Dictionary of state data (from save_state())

        Note:
            State dict may be from older version - must validate keys explicitly
        """
        ...

    # capabilities: List[str] - direct attribute access for ResourceProxy


# =============================================================================
#               PROXY ERROR TYPES (FAULT ISOLATION)
# =============================================================================
#
# These exception types are used internally within proxies. However, the
# preferred pattern is to return ProxyResult instead of raising exceptions,
# to maintain fault isolation.
#
# When to use exceptions vs ProxyResult:
# - ProxyResult: Normal operations that may fail (network, storage)
# - Exception: Programming errors that indicate bugs (should crash)
# =============================================================================


class ProxyError(Exception):
    """
    Base exception for proxy-related errors.

    This is the parent class for all proxy exceptions. Use specific
    subclasses for different error conditions.

    Note:
        Prefer returning ProxyResult over raising exceptions for
        operations that may legitimately fail (network, storage, etc.)
    """

    ...


class ProxyNotInitializedError(ProxyError):
    """
    Raised when proxy operation is attempted before initialization.

    This indicates a programming error - the caller should have
    called initialize() before using the proxy.

    Example:
        proxy = StorageProxy(config)
        # BUG: Should call await proxy.initialize() first!
        await proxy.checkpoint()  # Raises ProxyNotInitializedError
    """

    ...


class ProxyOperationError(ProxyError):
    """
    Raised when a proxy operation fails (non-fatal).

    This indicates an operation failure that should be handled by
    the caller. Includes an error_code for programmatic handling.

    Attributes:
        error_code: Machine-readable error code (e.g., "NOT_FOUND")
        message: Human-readable error description
    """

    def __init__(self, message: str, error_code: str = "UNKNOWN"):
        super().__init__(message)
        self.error_code = error_code


@dataclass
class ProxyResult:
    """
    Result wrapper for proxy operations supporting graceful degradation.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                     PROXYRESULT PATTERN                             │
    │                                                                     │
    │  Instead of raising exceptions, proxy operations return ProxyResult│
    │  to allow the owner to handle failures gracefully.                 │
    │                                                                     │
    │  Success case:                                                      │
    │      result = await proxy.fetch_resource(uri)                      │
    │      if result.success:                                            │
    │          data = result.data  # Safe to use                        │
    │                                                                     │
    │  Failure case:                                                      │
    │      result = await proxy.fetch_resource(uri)                      │
    │      if not result.success:                                        │
    │          log(result.error_code)  # Handle gracefully              │
    │          return default_value    # Don't crash!                   │
    └─────────────────────────────────────────────────────────────────────┘

    Why not exceptions?
    -------------------
    1. EXPLICIT: Caller is forced to check success (can't forget try/catch)
    2. COMPOSABLE: Easy to chain operations and aggregate failures
    3. PREDICTABLE: No hidden control flow jumps
    4. SERIALIZABLE: Can be transmitted over network (Ray)

    Attributes:
        success: True if operation succeeded, False otherwise
        data: The result data (only valid if success=True)
        error_code: Machine-readable error code (if success=False)
        error_message: Human-readable error description (if success=False)
    """

    success: bool
    data: Any = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

    @classmethod
    def ok(cls, data: Any = None) -> "ProxyResult":
        """
        Create a successful result.

        Args:
            data: The result data to return

        Returns:
            ProxyResult with success=True and data set

        Example:
            return ProxyResult.ok(checkpoint_id)
        """
        return cls(success=True, data=data)

    @classmethod
    def fail(cls, error_code: str, message: str) -> "ProxyResult":
        """
        Create a failure result.

        Args:
            error_code: Machine-readable code (e.g., "NOT_FOUND", "TIMEOUT")
            message: Human-readable description

        Returns:
            ProxyResult with success=False and error info

        Example:
            return ProxyResult.fail("NOT_FOUND", f"Checkpoint {id} not found")
        """
        return cls(success=False, error_code=error_code, error_message=message)


# =============================================================================
#                          BASE PROXY TYPES
# =============================================================================


class ProxyType(Enum):
    """
    Enumeration of proxy types available in the framework.

    Each proxy type corresponds to a specific infrastructure concern:

    ┌─────────────────────────────────────────────────────────────────────┐
    │  ProxyType        │ Infrastructure Concern  │ Key Operations        │
    │───────────────────┼─────────────────────────┼──────────────────────│
    │  COMMUNICATION    │ Message passing         │ send, broadcast, recv │
    │  STORAGE          │ State persistence       │ checkpoint, restore   │
    │  RESOURCE         │ External resources      │ fetch, invoke         │
    │  OBSERVABILITY    │ Monitoring & logging    │ metrics, events       │
    └─────────────────────────────────────────────────────────────────────┘
    """

    # Message routing and delivery
    COMMUNICATION = auto()
    # State checkpointing and rollback
    STORAGE = auto()
    # MCP resource access
    RESOURCE = auto()
    # Metrics and structured logging
    OBSERVABILITY = auto()


@dataclass
class ProxyConfig:
    """
    Base configuration for all proxy types.

    This dataclass holds common configuration that applies to all proxies.
    Specific proxy types extend this with additional settings.

    Attributes:
        proxy_type: The type of proxy (COMMUNICATION, STORAGE, etc.)
        backend: Implementation backend ("ray", "grpc", "memory", etc.)
        retry_policy: Configuration for retry behavior on failures
        extras: Additional backend-specific configuration

    Retry Policy Keys:
        - max_retries: Maximum number of retry attempts (default: 3)
        - retry_delay_ms: Initial delay between retries (default: 100ms)
        - exponential_backoff: Whether to double delay each retry (default: True)

    Example:
        config = ProxyConfig(
            proxy_type=ProxyType.STORAGE,
            backend="redis",
            retry_policy={"max_retries": 5, "retry_delay_ms": 200},
            extras={"redis_url": "redis://localhost:6379"}
        )
    """

    proxy_type: ProxyType
    # Default to Ray-native implementation
    backend: str = "ray"
    retry_policy: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_retries": 3,
            "retry_delay_ms": 100,
            "exponential_backoff": True,
        }
    )
    extras: Dict[str, Any] = field(default_factory=dict)


# Type alias for owner entities
# All owners are Players (regular or coordinator role)
OwnerType = Union["BasePlayer", ObservableEntity]


class BaseProxy(ABC):
    """
    Abstract base class for all proxy types.

    ╔═════════════════════════════════════════════════════════════════════╗
    ║                        BASE PROXY DESIGN                            ║
    ╠═════════════════════════════════════════════════════════════════════╣
    ║                                                                      ║
    ║  BaseProxy provides the foundation for all concrete proxy types:    ║
    ║                                                                      ║
    ║  1. WEAK REFERENCE to owner (prevents circular dependency)          ║
    ║  2. LIFECYCLE management (initialize/shutdown)                      ║
    ║  3. CONFIGURATION storage                                            ║
    ║  4. OWNER ACCESS via ObservableEntity protocol                      ║
    ║                                                                      ║
    ╚═════════════════════════════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────────────────┐
    │                    WEAK REFERENCE PATTERN                           │
    │                                                                     │
    │  Problem without weak reference:                                    │
    │      Owner ──strong──► Proxy                                        │
    │      Proxy ──strong──► Owner  ← CIRCULAR! Memory leak!             │
    │                                                                     │
    │  Solution with weak reference:                                      │
    │      Owner ──strong──► Proxy                                        │
    │      Proxy ──weak────► Owner  ← Owner can be GC'd normally         │
    │                                                                     │
    │  When owner is garbage collected:                                   │
    │      self._owner_ref() returns None                                │
    │      Proxy gracefully handles missing owner                        │
    └─────────────────────────────────────────────────────────────────────┘

    Subclass Responsibilities:
    --------------------------
    Subclasses MUST implement:
        - initialize(): Set up proxy resources (connections, caches)
        - shutdown(): Clean up resources (close connections, flush data)

    Subclasses SHOULD:
        - Return ProxyResult from operations (not raise exceptions)
        - Check is_initialized before operations
        - Handle missing owner gracefully (owner may be GC'd)
    """

    def __init__(
        self,
        config: ProxyConfig,
        owner: Optional[OwnerType] = None,
    ):
        """
        Initialize the base proxy.

        Args:
            config: Configuration for this proxy type
            owner: Optional owner entity (can be set later via set_owner())

        Note:
            Owner can be None initially. Use set_owner() to attach later.
            This enables factory-created proxies to be attached after creation.
        """
        # Store configuration
        self.config = config
        self.proxy_type = config.proxy_type

        # Lifecycle flag - set to True by initialize()
        self.is_initialized: bool = False

        # =====================================================================
        # WEAK REFERENCE to owner
        # =====================================================================
        # We use weakref.ref() to avoid circular reference between owner and
        # proxy. This allows the owner to be garbage collected normally.
        #
        # If owner is GC'd, self.owner_ref() will return None instead of
        # raising an error. Proxy operations should handle this gracefully.
        # =====================================================================
        self.owner_ref: Optional[weakref.ref] = None
        if owner is not None:
            self.owner_ref = weakref.ref(owner)

    def get_owner(self) -> Optional[OwnerType]:
        """
        Get the owner entity via weak reference.

        Returns None if:
            - No owner was ever set (owner_ref is None)
            - Owner has been garbage collected (weak ref returns None)
        """
        if self.owner_ref is None:
            return None
        return self.owner_ref()  # Returns None if owner was GC'd

    def set_owner(self, owner: OwnerType) -> None:
        """
        Set or update the owner reference.

        This is called by the owner's attach_*_proxy() method to establish
        the bidirectional relationship. The proxy stores a WEAK reference
        to prevent circular dependency.

        Args:
            owner: The entity that owns this proxy

        Example:
            # In Player.attach_storage_proxy():
            def attach_storage_proxy(self, proxy: StorageProxy) -> None:
                self._storage_proxy = proxy  # Player holds strong ref
                proxy.set_owner(self)        # Proxy holds weak ref
        """
        self.owner_ref = weakref.ref(owner)

    @property
    def owner_id(self) -> Optional[str]:
        """
        Get the owner's identity if available.

        Convenience property that safely retrieves the owner's identity
        for logging, metrics tagging, and storage keys.

        Returns:
            Owner's identity string, or None if owner unavailable
        """
        owner = self.get_owner()
        return owner.identity if owner else None

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize proxy resources.

        Called once before the proxy is used. Subclasses should:
            - Establish connections (network, database)
            - Initialize caches
            - Set is_initialized = True

        Raises:
            ProxyNotInitializedError: If initialization fails
        """
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> None:
        """
        Shutdown proxy and release resources.

        Called when the owner is shutting down. Subclasses should:
            - Close connections
            - Flush pending data (metrics, logs)
            - Release memory
            - Set is_initialized = False

        Note:
            Should NOT raise exceptions - log errors instead
        """
        raise NotImplementedError


# =============================================================================
#                         COMMUNICATION PROXY
# =============================================================================
#
# SendReceiveProxy handles message routing and reliable transmission.
# It provides a unified interface for point-to-point and broadcast messaging.
#
# Key Design:
# - Decouples message production from consumption
# - Supports async callbacks for real-time message handling
# - Fault isolation via ProxyResult returns
# =============================================================================


@dataclass
class SendReceiveConfig(ProxyConfig):
    """
    Configuration for SendReceiveProxy.

    Extends ProxyConfig with communication-specific settings.

    Attributes:
        proxy_type: Fixed to COMMUNICATION (auto-set, not user-configurable)
        message_timeout_ms: Timeout for message delivery (default: 5000ms)
        enable_compression: Whether to compress large messages (default: True)
        max_message_size_bytes: Maximum message size (default: 10MB)
        record_path: Directory for message recording (default: None)
        is_record_messages: Whether to record sent messages (default: True)

    Example:
        config = SendReceiveConfig(
            message_timeout_ms=10000,  # 10 second timeout
            enable_compression=True,
            max_message_size_bytes=50 * 1024 * 1024,  # 50MB
            record_path="/path/to/records",
            record_messages=True
        )
    """

    # proxy_type is auto-set, not provided by user
    proxy_type: ProxyType = field(default=ProxyType.COMMUNICATION, init=False)
    message_timeout_ms: int = 5000  # 5 second default timeout
    enable_compression: bool = True  # Compress large messages
    max_message_size_bytes: int = 10 * 1024 * 1024  # 10MB default max
    # Message recording configuration
    record_path: Optional[str] = None  # Directory for message storage
    is_record_messages: bool = True  # Whether to record sent messages


# =============================================================================
#                            STORAGE PROXY
# =============================================================================
#
# StorageProxy handles state checkpointing and rollback. It enables:
# - Saving entity state at any point in time
# - Restoring to previous states (rollback)
# - Managing checkpoint history
#
# Key Design:
# - Calls owner.save_state() to get state
# - Calls owner.load_state() to restore state
# - Supports multiple backends (memory, file, Redis, S3)
# =============================================================================


@dataclass
class StorageConfig(ProxyConfig):
    """Configuration for StorageProxy."""

    proxy_type: ProxyType = field(default=ProxyType.STORAGE, init=False)
    checkpoint_dir: Optional[str] = None
    record_path: Optional[str] = None
    record_rounds: bool = True


# =============================================================================
#                           RESOURCE PROXY
# =============================================================================
#
# ResourceProxy handles MCP (Model Context Protocol) connection management
# and resource access. It provides a unified interface for:
# - Fetching external resources (data, files, API responses)
# - Invoking external tools (LLM, computation services)
# - Managing MCP server connections
#
# Key Design:
# - URI-based resource addressing (mcp://server/resource)
# - Response caching for performance
# - Access control via owner.capabilities
# =============================================================================


@dataclass
class ResourceConfig(ProxyConfig):
    """
    Configuration for ResourceProxy.

    Attributes:
        proxy_type: Fixed to RESOURCE
        mcp_servers: List of MCP server configurations to connect to
        connection_timeout_ms: Timeout for server connections
        enable_caching: Whether to cache resource responses
        cache_ttl_seconds: Cache time-to-live in seconds

    MCP Server Config Format:
        {
            "name": "market_data",
            "endpoint": "ws://localhost:8080",
            "capabilities": ["prices", "orderbook"]
        }

    Example:
        config = ResourceConfig(
            mcp_servers=[
                {"name": "market", "endpoint": "ws://market:8080"},
                {"name": "llm", "endpoint": "ws://llm:8080"}
            ],
            enable_caching=True,
            cache_ttl_seconds=60  # 1 minute cache
        )
    """

    proxy_type: ProxyType = field(default=ProxyType.RESOURCE, init=False)
    mcp_servers: List[Dict[str, Any]] = field(default_factory=list)
    connection_timeout_ms: int = 5000  # 5 second connection timeout
    enable_caching: bool = True  # Cache resource responses
    cache_ttl_seconds: int = 300  # 5 minute cache TTL


# ResourceProxy implementation is in general.py
# This section contains only the ResourceConfig dataclass above


# =============================================================================
#                        OBSERVABILITY PROXY
# =============================================================================
#
# ObservabilityProxy handles metrics collection and structured logging.
# It provides visibility into entity behavior without affecting core logic.
#
# Key Design:
# - Fire-and-forget operations (never fail, never block)
# - Structured data for machine processing
# - Timer support for performance measurement
# =============================================================================


@dataclass
class MonitoringConfig(ProxyConfig):
    """
    Configuration for MonitoringProxy.

    Attributes:
        proxy_type: Fixed to OBSERVABILITY
        metrics_backend: Backend for metrics storage ("memory", "prometheus", "statsd")
        logging_backend: Backend for logging ("structured", "json", "console")
        enable_tracing: Whether to enable distributed tracing
        log_level: Minimum log level ("DEBUG", "INFO", "WARNING", "ERROR")

    Example:
        config = MonitoringConfig(
            metrics_backend="prometheus",
            logging_backend="json",
            enable_tracing=True,
            log_level="INFO"
        )
    """

    proxy_type: ProxyType = field(default=ProxyType.OBSERVABILITY, init=False)
    metrics_backend: str = "memory"  # "memory", "prometheus", "statsd"
    logging_backend: str = "structured"  # "structured", "json", "console"
    log_dir: Optional[str] = None  # Directory for log files
    enable_tracing: bool = True  # Distributed tracing
    log_level: str = "INFO"  # Minimum log level


# MonitoringProxy implementation is in general.py
# This section contains only the MonitoringConfig dataclass above
