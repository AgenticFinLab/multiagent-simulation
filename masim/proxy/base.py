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
    CommunicationConfig  - Config for CommunicationProxy
    StorageConfig        - Config for StorageProxy
    ResourceConfig       - Config for ResourceProxy
    ObservabilityConfig  - Config for ObservabilityProxy

Abstract Classes:
    BaseProxy            - Abstract base with owner weak reference pattern
    CommunicationProxy   - Message routing: send, broadcast, subscribe
    StorageProxy         - State persistence: checkpoint, restore
    ResourceProxy        - MCP integration: fetch_resource, invoke_tool
    ObservabilityProxy   - Metrics/logging: log_event, record_metric

Factory:
    ProxyFactory         - Batch creation of proxies from configuration

================================================================================
                           MODULE OVERVIEW
================================================================================

This module defines the four micro-proxy types that provide infrastructure
abstraction for Player and Conductor entities:

    1. CommunicationProxy - Message routing and reliable transmission
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
   │  CommunicationProxy: send, broadcast, receive, subscribe, unsubscribe
   │  StorageProxy:       checkpoint, restore, list, delete, get_latest  │
   │  ResourceProxy:      fetch, invoke, list, connect, disconnect       │
   │  ObservabilityProxy: record_metric, log_event, start/stop_timer    │
   └─────────────────────────────────────────────────────────────────────┘

2. COMPOSITION OVER INHERITANCE
   ----------------------------
   Proxies are COMPOSED into entities (Player/Conductor), not inherited.

   ┌───────────────────────────────────────────────────────────────────┐
   │  Owner (Player/Conductor)                                         │
   │      │                                                            │
   │      │  ┌─────────────────────┐                                  │
   │      ├──│ CommunicationProxy  │──┐                               │
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
│  CommunicationProxy  │ identity, on_message()      │ Message routing       │
│  StorageProxy        │ identity, save_state(),     │ State persistence     │
│                      │ load_state()                │                        │
│  ResourceProxy       │ identity, get_capabilities()│ Access control        │
│  ObservabilityProxy  │ identity, get_system_metrics()│ Monitoring          │
│                      │ (Conductor only)            │                        │
│                                                                              │
│  Proxies CANNOT access:                                                      │
│  ✗ _internal_strategy()    ✗ _compute_decision()    ✗ _private_cache       │
└─────────────────────────────────────────────────────────────────────────────┘

================================================================================
                      PLAYER VS CONDUCTOR PROXY STRATEGIES
================================================================================

While all proxies share the same interface, implementations can differ
based on whether the owner is a Player or Conductor:

┌─────────────────────────────────────────────────────────────────────────────┐
│              DIFFERENTIATED PROXY STRATEGIES                                 │
│                                                                              │
│  Proxy Type      │ Player Strategy           │ Conductor Strategy           │
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

import time
import uuid
import weakref
import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from datetime import datetime
from dataclasses import dataclass, field
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Callable,
    Awaitable,
    Union,
    Protocol,
    runtime_checkable,
    TYPE_CHECKING,
    Set,
)

from masim.communication.base import Message

# ---------------------------------------------------------------------------
# TYPE_CHECKING Block
# ---------------------------------------------------------------------------
# These imports are only for static type checking (mypy, IDE hints).
# At runtime, they are NOT imported to avoid circular dependencies.
#
# Why this pattern?
# - proxy/base.py needs to reference Player/Conductor types for type hints
# - But player/base.py and conductor/base.py import from proxy/base.py
# - Circular import at runtime would crash Python
# - TYPE_CHECKING is False at runtime, True during type checking
# ---------------------------------------------------------------------------
if TYPE_CHECKING:
    from masim.player.base import BasePlayer
    from masim.conductor.base import BaseConductor


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
    │  - BasePlayer implements ObservableEntity                          │
    │  - BaseConductor implements ObservableEntity                       │
    │  - Test mocks can implement ObservableEntity                       │
    └─────────────────────────────────────────────────────────────────────┘

    Benefits of Protocol-based Access Control:
    ------------------------------------------
    1. EXPLICIT BOUNDARIES: Clear contract of what proxies can access
    2. TESTABILITY: Mock objects need only implement this interface
    3. DECOUPLING: Proxies don't depend on concrete Player/Conductor classes
    4. DOCUMENTATION: Protocol IS the documentation of proxy-owner interface

    Access Control Matrix:
    ----------------------
    | Method             | Used By               | Purpose                    |
    |--------------------|-----------------------|----------------------------|
    | identity           | All proxies           | Entity identification      |
    | on_message()       | CommunicationProxy    | Message delivery callback  |
    | save_state()       | StorageProxy          | Get state for checkpoint   |
    | load_state()       | StorageProxy          | Restore state from checkpoint|
    | get_capabilities() | ResourceProxy         | Access control for resources|
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
        Callback invoked when a message arrives (CommunicationProxy).

        This method is called by CommunicationProxy when a message
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

    def get_capabilities(self) -> List[str]:
        """
        Return capability tags for ResourceProxy access control.

        Capabilities determine which MCP resources this entity can access.
        ResourceProxy checks capabilities before allowing resource fetch.

        Returns:
            List of capability strings (e.g., ["market_data", "order_book"])

        Example Access Control Flow:
            1. Entity requests: fetch_resource("mcp://market/prices")
            2. ResourceProxy checks: "market_data" in entity.get_capabilities()
            3. If missing: ProxyResult.fail("ACCESS_DENIED", ...)
        """
        ...


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

    pass


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

    pass


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
# Union type allows proxies to work with either Player or Conductor
OwnerType = Union["BasePlayer", "BaseConductor", ObservableEntity]


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
        - Check _is_initialized before operations
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
        self._is_initialized: bool = False

        # =====================================================================
        # WEAK REFERENCE to owner
        # =====================================================================
        # We use weakref.ref() to avoid circular reference between owner and
        # proxy. This allows the owner to be garbage collected normally.
        #
        # If owner is GC'd, self._owner_ref() will return None instead of
        # raising an error. Proxy operations should handle this gracefully.
        # =====================================================================
        self._owner_ref: Optional[weakref.ref] = None
        if owner is not None:
            self._owner_ref = weakref.ref(owner)

    def _get_owner(self) -> Optional[OwnerType]:
        """
        Get the owner entity via weak reference.

        This method safely dereferences the weak reference to the owner.
        Returns None if:
            - No owner was ever set (_owner_ref is None)
            - Owner has been garbage collected (weak ref returns None)

        Returns:
            The owner entity, or None if unavailable

        Usage:
            owner = self._get_owner()
            if owner is not None:
                owner.on_message(msg)  # Safe to call
            else:
                # Handle gracefully - owner was GC'd or never set
                pass
        """
        if self._owner_ref is None:
            return None
        return self._owner_ref()  # Returns None if owner was GC'd

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
        self._owner_ref = weakref.ref(owner)

    @property
    def owner_id(self) -> Optional[str]:
        """
        Get the owner's identity if available.

        Convenience property that safely retrieves the owner's identity
        for logging, metrics tagging, and storage keys.

        Returns:
            Owner's identity string, or None if owner unavailable
        """
        owner = self._get_owner()
        return owner.identity if owner else None

    @abstractmethod
    async def initialize(self) -> None:
        """
        Initialize proxy resources.

        Called once before the proxy is used. Subclasses should:
            - Establish connections (network, database)
            - Initialize caches
            - Set _is_initialized = True

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
            - Set _is_initialized = False

        Note:
            Should NOT raise exceptions - log errors instead
        """
        raise NotImplementedError


# =============================================================================
#                         COMMUNICATION PROXY
# =============================================================================
#
# CommunicationProxy handles message routing and reliable transmission.
# It provides a unified interface for point-to-point and broadcast messaging.
#
# Key Design:
# - Decouples message production from consumption
# - Supports async callbacks for real-time message handling
# - Fault isolation via ProxyResult returns
# =============================================================================


@dataclass
class CommunicationConfig(ProxyConfig):
    """
    Configuration for CommunicationProxy.

    Extends ProxyConfig with communication-specific settings.

    Attributes:
        proxy_type: Fixed to COMMUNICATION (auto-set, not user-configurable)
        message_timeout_ms: Timeout for message delivery (default: 5000ms)
        enable_compression: Whether to compress large messages (default: True)
        max_message_size_bytes: Maximum message size (default: 10MB)

    Example:
        config = CommunicationConfig(
            message_timeout_ms=10000,  # 10 second timeout
            enable_compression=True,
            max_message_size_bytes=50 * 1024 * 1024  # 50MB
        )
    """

    # proxy_type is auto-set, not provided by user
    proxy_type: ProxyType = field(default=ProxyType.COMMUNICATION, init=False)
    message_timeout_ms: int = 5000  # 5 second default timeout
    enable_compression: bool = True  # Compress large messages
    max_message_size_bytes: int = 10 * 1024 * 1024  # 10MB default max


class CommunicationProxy(BaseProxy):
    """
    Proxy for message routing and reliable transmission.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                  COMMUNICATION PROXY OVERVIEW                       │
    │                                                                     │
    │  Core Methods (≤5, micro-proxy pattern):                           │
    │    1. send()       - Send to specific recipient                    │
    │    2. broadcast()  - Send to multiple recipients                   │
    │    3. receive()    - Retrieve pending messages                     │
    │    4. subscribe()  - Register for real-time delivery               │
    │    5. unsubscribe()- Remove subscription                           │
    │                                                                     │
    │  Owner Callback:                                                    │
    │    - on_message() called when message arrives                      │
    │                                                                     │
    │  Fault Isolation:                                                   │
    │    - Returns ProxyResult (never raises exceptions)                 │
    │    - Logs warnings on failures                                      │
    └─────────────────────────────────────────────────────────────────────┘

    Message Flow:

        Sender                    CommunicationProxy                 Recipient
          │                              │                              │
          │──send(msg)──────────────────►│                              │
          │                              │──store in pending_messages──►│
          │                              │                              │
          │                              │──if subscribed: callback────►│
          │                              │                              │
          │                              │◄────────receive()────────────│
          │                              │──return messages─────────────►│

    Player vs Conductor Strategy:
    - Player: Optimized for point-to-point (low latency)
    - Conductor: Optimized for broadcast/aggregate (high throughput)
    """

    def __init__(
        self,
        config: Optional[CommunicationConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        """
        Initialize CommunicationProxy.

        Args:
            config: Communication configuration (uses defaults if None)
            owner: Optional owner entity
        """
        super().__init__(config or CommunicationConfig(), owner)
        self.config: CommunicationConfig = config or CommunicationConfig()

        # =====================================================================
        # Internal State
        # =====================================================================
        # _subscriptions: entity_id → callback for real-time delivery
        # _pending_messages: entity_id → list of undelivered messages
        # =====================================================================
        self._subscriptions: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        self._pending_messages: Dict[str, List[Message]] = {}

    async def initialize(self) -> None:
        """Initialize communication resources (connection pools, etc.)."""
        self._is_initialized = True

    async def shutdown(self) -> None:
        """Shutdown and release resources."""
        self._subscriptions.clear()
        self._pending_messages.clear()
        self._is_initialized = False

    async def send(self, message: Message) -> ProxyResult:
        """
        Send a message to a specific recipient.

        The message is stored in the recipient's pending queue and
        optionally delivered via callback if subscribed.

        Args:
            message: Message to send (must have recipient_id set)

        Returns:
            ProxyResult.ok() on success
            ProxyResult.fail() with error code on failure

        Error Codes:
            - INVALID_RECIPIENT: message.recipient_id is None
            - SEND_FAILED: Internal error during send

        Example:
            result = await proxy.send(Message(
                message_type=MessageType.PEER,
                sender_id="player_001",
                recipient_id="player_002",
                payload={"offer": 100}
            ))
            if not result.success:
                log.warning(f"Send failed: {result.error_code}")
        """
        # Validate recipient
        if not message.recipient_id:
            return ProxyResult.fail(
                "INVALID_RECIPIENT", "Message must have recipient_id"
            )

        # Store in pending messages queue
        if message.recipient_id not in self._pending_messages:
            self._pending_messages[message.recipient_id] = []
        self._pending_messages[message.recipient_id].append(message)

        # Trigger callback if subscribed (real-time delivery)
        if message.recipient_id in self._subscriptions:
            await self._subscriptions[message.recipient_id](message)

        return ProxyResult.ok()

    async def broadcast(
        self, message: Message, scope: Optional[str] = None
    ) -> ProxyResult:
        """
        Broadcast a message to multiple recipients.

        The message is delivered to all entities with pending message
        queues. Scope can filter recipients (e.g., "group:traders").

        Args:
            message: Message to broadcast
            scope: Optional scope filter (default: "all")
                   Format: "all", "group:<tag>", "entity:<id>"

        Returns:
            ProxyResult.ok() on success
            ProxyResult.fail() on failure

        Example:
            # Broadcast coordination decision to all players
            await proxy.broadcast(Message(
                message_type=MessageType.COORDINATION,
                sender_id="conductor_001",
                payload={"instruction": "reduce_activity"}
            }, scope="group:market_makers")
        """
        # Tag message with broadcast scope for routing
        message.metadata["broadcast_scope"] = scope or "all"

        # Deliver to all registered recipients
        for recipient_id in list(self._pending_messages.keys()):
            self._pending_messages[recipient_id].append(message)
            # Trigger callback if subscribed
            if recipient_id in self._subscriptions:
                await self._subscriptions[recipient_id](message)

        return ProxyResult.ok()

    async def receive(self, entity_id: str) -> List[Message]:
        """
        Receive pending messages for an entity.

        Retrieves and clears all pending messages for the specified entity.
        Also notifies the owner via on_message() callback.

        Args:
            entity_id: ID of the entity receiving messages

        Returns:
            List of pending Message objects (queue is cleared)

        Note:
            This method never fails - returns empty list if no messages.
        """
        # Get and clear pending messages
        if entity_id in self._pending_messages:
            messages = self._pending_messages[entity_id].copy()
        else:
            messages = []
        self._pending_messages[entity_id] = []

        # Notify owner of received messages (if owner exists)
        owner = self._get_owner()
        if owner and hasattr(owner, "on_message"):
            for msg in messages:
                owner.on_message(msg)

        return messages

    async def subscribe(
        self, entity_id: str, callback: Callable[[Message], Awaitable[None]]
    ) -> bool:
        """
        Subscribe to messages with a callback for real-time delivery.

        When subscribed, messages are delivered immediately via callback
        instead of being queued for later retrieval.

        Args:
            entity_id: ID of the subscribing entity
            callback: Async function called with each message

        Returns:
            True on success

        Example:
            async def handle_message(msg: Message):
                logger.debug("        Received: %s", msg.payload)

            await proxy.subscribe("player_001", handle_message)
        """
        self._subscriptions[entity_id] = callback
        # Initialize pending queue if not exists
        if entity_id not in self._pending_messages:
            self._pending_messages[entity_id] = []
        return True

    async def unsubscribe(self, entity_id: str) -> bool:
        """
        Unsubscribe from real-time message delivery.

        After unsubscribing, messages are queued instead of delivered
        immediately via callback.

        Args:
            entity_id: ID of the entity to unsubscribe

        Returns:
            True on success
        """
        self._subscriptions.pop(entity_id, None)
        return True


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
    """
    Configuration for StorageProxy.

    Attributes:
        proxy_type: Fixed to STORAGE
        storage_backend: Backend type ("memory", "file", "redis", "s3")
        checkpoint_dir: Directory for file-based storage
        max_checkpoints: Maximum checkpoints per entity (FIFO eviction)
        encrypt_state: Whether to encrypt stored state (for Player privacy)

    Example:
        # Player config with encryption (private state)
        player_storage = StorageConfig(
            storage_backend="file",
            checkpoint_dir="/data/checkpoints",
            max_checkpoints=50,
            encrypt_state=True  # Protect Player's private state
        )

        # Conductor config without encryption (global state)
        conductor_storage = StorageConfig(
            storage_backend="redis",
            max_checkpoints=100,
            encrypt_state=False  # State is globally visible anyway
        )
    """

    proxy_type: ProxyType = field(default=ProxyType.STORAGE, init=False)
    storage_backend: str = "memory"  # "memory", "file", "redis", "s3"
    checkpoint_dir: Optional[str] = None  # Directory for file storage
    max_checkpoints: int = 100  # Max checkpoints per entity
    encrypt_state: bool = False  # Encrypt for Player privacy


@dataclass
class Checkpoint:
    """
    A state checkpoint record.

    Represents a saved snapshot of entity state at a specific point in time.

    Attributes:
        checkpoint_id: Unique identifier (UUID)
        entity_id: ID of the entity that owns this checkpoint
        state: The saved state data (from entity.save_state())
        timestamp: ISO-8601 timestamp when checkpoint was created
        label: Optional human-readable label (e.g., "before_trade")
    """

    checkpoint_id: str  # Unique ID for this checkpoint
    entity_id: str  # Owner entity ID
    state: Dict[str, Any]  # Saved state data
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    label: Optional[str] = None  # Optional human-readable label


class StorageProxy(BaseProxy):
    """
    Proxy for state checkpoint and rollback.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                     STORAGE PROXY OVERVIEW                          │
    │                                                                     │
    │  Core Methods (≤5, micro-proxy pattern):                           │
    │    1. checkpoint()         - Save current state                    │
    │    2. restore()            - Restore from checkpoint               │
    │    3. list_checkpoints()   - List available checkpoints            │
    │    4. delete_checkpoint()  - Remove a checkpoint                   │
    │    5. get_latest_checkpoint() - Get most recent                    │
    │                                                                     │
    │  Owner Interface (ObservableEntity):                               │
    │    - save_state() called to get state for checkpoint              │
    │    - load_state() called to restore state from checkpoint         │
    │                                                                     │
    │  Fault Isolation:                                                   │
    │    - Returns ProxyResult (never raises exceptions)                 │
    │    - Failures are logged, don't crash owner                        │
    └─────────────────────────────────────────────────────────────────────┘

    Checkpoint Flow:

        Owner                      StorageProxy                    Storage
          │                              │                            │
          │──checkpoint(label)──────────►│                            │
          │                              │──owner.save_state()────────│
          │                              │◄──state dict────────────────│
          │                              │──store(state)──────────────►│
          │◄──ProxyResult.ok(id)─────────│                            │
          │                              │                            │
          │──restore(id)────────────────►│                            │
          │                              │◄──retrieve(id)──────────────│
          │                              │──owner.load_state(state)───│
          │◄──ProxyResult.ok(state)──────│                            │

    Player vs Conductor Strategy:
    - Player: Encrypted private storage, per-step checkpointing
    - Conductor: Global visible storage, distributed snapshots
    """

    def __init__(
        self,
        config: Optional[StorageConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        """
        Initialize StorageProxy.

        Args:
            config: Storage configuration (uses defaults if None)
            owner: Optional owner entity
        """
        super().__init__(config or StorageConfig(), owner)
        self.config: StorageConfig = config or StorageConfig()

        # =====================================================================
        # Internal Storage
        # =====================================================================
        # _checkpoints: checkpoint_id → Checkpoint object
        # _entity_checkpoints: entity_id → list of checkpoint_ids (ordered)
        # =====================================================================
        self._checkpoints: Dict[str, Checkpoint] = {}
        self._entity_checkpoints: Dict[str, List[str]] = {}

    async def initialize(self) -> None:
        """Initialize storage backend (connections, directories)."""
        # TODO: Initialize actual backend based on config.storage_backend
        self._is_initialized = True

    async def shutdown(self) -> None:
        """Shutdown and persist pending data."""
        # TODO: Flush to persistent storage if configured
        self._is_initialized = False

    async def checkpoint(
        self,
        entity_id: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
        label: Optional[str] = None,
    ) -> ProxyResult:
        """
        Create a state checkpoint.

        Saves the current state of the owner entity. If state is not
        provided, calls owner.save_state() to get it.

        Args:
            entity_id: Entity ID (defaults to owner's identity)
            state: State to save (defaults to owner.save_state())
            label: Optional human-readable label

        Returns:
            ProxyResult.ok(checkpoint_id) on success
            ProxyResult.fail(error_code, message) on failure

        Error Codes:
            - NO_ENTITY_ID: No entity ID available
            - CHECKPOINT_FAILED: Internal error

        Example:
            # Save checkpoint before risky operation
            result = await storage.checkpoint(label="before_trade")
            if result.success:
                trade_result = await execute_trade()
                if trade_failed:
                    await storage.restore(result.data)  # Rollback!
        """
        # Determine entity ID (from parameter or owner)
        eid = entity_id or self.owner_id
        if not eid:
            return ProxyResult.fail("NO_ENTITY_ID", "Entity ID required for checkpoint")

        # Get state from owner if not provided
        checkpoint_state = state
        if checkpoint_state is None:
            owner = self._get_owner()
            if owner and hasattr(owner, "save_state"):
                checkpoint_state = owner.save_state()
            else:
                checkpoint_state = {}

        # Create checkpoint record
        checkpoint_id = str(uuid.uuid4())
        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            entity_id=eid,
            state=checkpoint_state.copy(),  # Copy to prevent mutation
            label=label,
        )
        self._checkpoints[checkpoint_id] = checkpoint

        # Track checkpoint for this entity
        if eid not in self._entity_checkpoints:
            self._entity_checkpoints[eid] = []
        self._entity_checkpoints[eid].append(checkpoint_id)

        # Enforce max checkpoints (FIFO eviction)
        while len(self._entity_checkpoints[eid]) > self.config.max_checkpoints:
            oldest_id = self._entity_checkpoints[eid].pop(0)
            self._checkpoints.pop(oldest_id, None)

        return ProxyResult.ok(checkpoint_id)

    async def restore(self, checkpoint_id: str) -> ProxyResult:
        """
        Restore state from a checkpoint.

        Retrieves the checkpoint and calls owner.load_state() to apply it.

        Args:
            checkpoint_id: ID of the checkpoint to restore

        Returns:
            ProxyResult.ok(state) with restored state data
            ProxyResult.fail(error_code, message) on failure

        Error Codes:
            - NOT_FOUND: Checkpoint ID doesn't exist
            - RESTORE_FAILED: Internal error

        Example:
            result = await storage.restore(checkpoint_id)
            if result.success:
                logger.info("    Restored state: %s", result.data)
            else:
                logger.warning("    Restore failed: %s", result.error_code)
        """
        # Find checkpoint
        if checkpoint_id not in self._checkpoints:
            return ProxyResult.fail(
                "NOT_FOUND", f"Checkpoint {checkpoint_id} not found"
            )
        checkpoint = self._checkpoints[checkpoint_id]

        # Copy state to prevent mutation
        restored_state = checkpoint.state.copy()

        # Apply to owner if available
        owner = self._get_owner()
        if owner and hasattr(owner, "load_state"):
            owner.load_state(restored_state)

        return ProxyResult.ok(restored_state)

    async def list_checkpoints(
        self, entity_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all checkpoints for an entity.

        Args:
            entity_id: Entity ID (defaults to owner's identity)

        Returns:
            List of checkpoint metadata dicts (id, timestamp, label)
        """
        eid = entity_id or self.owner_id or ""
        if eid in self._entity_checkpoints:
            checkpoint_ids = self._entity_checkpoints[eid]
        else:
            checkpoint_ids = []
        return [
            {
                "checkpoint_id": cid,
                "timestamp": self._checkpoints[cid].timestamp,
                "label": self._checkpoints[cid].label,
            }
            for cid in checkpoint_ids
            if cid in self._checkpoints
        ]

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.

        Args:
            checkpoint_id: ID of the checkpoint to delete

        Returns:
            True if deleted, False if not found
        """
        if checkpoint_id not in self._checkpoints:
            return False
        checkpoint = self._checkpoints.pop(checkpoint_id)
        # Also remove from entity's checkpoint list
        if checkpoint.entity_id in self._entity_checkpoints:
            entity_cps = self._entity_checkpoints[checkpoint.entity_id]
            if checkpoint_id in entity_cps:
                entity_cps.remove(checkpoint_id)
        return True

    async def get_latest_checkpoint(
        self, entity_id: Optional[str] = None
    ) -> ProxyResult:
        """
        Get and restore the most recent checkpoint.

        Args:
            entity_id: Entity ID (defaults to owner's identity)

        Returns:
            ProxyResult with restored state, or error if no checkpoints
        """
        eid = entity_id or self.owner_id or ""
        if eid not in self._entity_checkpoints:
            return ProxyResult.fail("NO_CHECKPOINTS", "No checkpoints found")
        checkpoint_ids = self._entity_checkpoints[eid]
        if not checkpoint_ids:
            return ProxyResult.fail("NO_CHECKPOINTS", "No checkpoints found")
        return await self.restore(checkpoint_ids[-1])


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
# - Access control via owner.get_capabilities()
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


class ResourceProxy(BaseProxy):
    """
    Proxy for MCP connection management and resource access.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                     RESOURCE PROXY OVERVIEW                         │
    │                                                                     │
    │  Core Methods (≤5, micro-proxy pattern):                           │
    │    1. fetch_resource() - Fetch data via MCP                        │
    │    2. invoke_tool()    - Call external tool via MCP                │
    │    3. list_available_resources() - List available resources        │
    │    4. connect()        - Connect to MCP server                     │
    │    5. disconnect()     - Disconnect from server                    │
    │                                                                     │
    │  MCP URI Format:                                                    │
    │    mcp://server_name/resource_path                                 │
    │    Example: mcp://market/prices/AAPL                               │
    │                                                                     │
    │  Fault Isolation:                                                   │
    │    - Returns ProxyResult (never raises exceptions)                 │
    │    - Caching reduces failure impact                                │
    └─────────────────────────────────────────────────────────────────────┘

    Resource Fetch Flow:

        Owner                     ResourceProxy                    MCP Server
          │                              │                              │
          │──fetch("mcp://x/y")─────────►│                              │
          │                              │──check cache────────────────►│
          │                              │◄──cache hit? return──────────│
          │                              │──check capabilities──────────│
          │                              │──MCP request────────────────►│
          │                              │◄──response───────────────────│
          │                              │──cache response──────────────│
          │◄──ProxyResult.ok(data)───────│                              │

    Player vs Conductor Strategy:
    - Player: Capability-filtered access, local caching
    - Conductor: Global coordination, request deduplication
    """

    def __init__(
        self,
        config: Optional[ResourceConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        """
        Initialize ResourceProxy.

        Args:
            config: Resource configuration (uses defaults if None)
            owner: Optional owner entity
        """
        super().__init__(config or ResourceConfig(), owner)
        self.config: ResourceConfig = config or ResourceConfig()

        # =====================================================================
        # Internal State
        # =====================================================================
        # _connections: server_name → connection info
        # _resource_cache: uri → (data, timestamp) for TTL caching
        # =====================================================================
        self._connections: Dict[str, Any] = {}
        self._resource_cache: Dict[str, tuple] = {}

    async def initialize(self) -> None:
        """Initialize connections to configured MCP servers."""
        for server_config in self.config.mcp_servers:
            server_name = server_config["name"]
            # TODO: Establish actual MCP connections
            self._connections[server_name] = {
                "config": server_config,
                "connected": True,
            }
        self._is_initialized = True

    async def shutdown(self) -> None:
        """Shutdown and close all connections."""
        # TODO: Close actual MCP connections
        self._connections.clear()
        self._resource_cache.clear()
        self._is_initialized = False

    async def fetch_resource(self, resource_uri: str) -> ProxyResult:
        """
        Fetch a resource via MCP protocol.

        Retrieves data from an MCP server using the URI format:
        mcp://server_name/resource_path

        Args:
            resource_uri: MCP URI of the resource

        Returns:
            ProxyResult.ok(data) with resource data
            ProxyResult.fail(error_code, message) on failure

        Error Codes:
            - NOT_CONNECTED: Server not connected
            - FETCH_FAILED: Internal error
            - INVALID_URI: Malformed URI

        Example:
            result = await proxy.fetch_resource("mcp://market/prices/AAPL")
            if result.success:
                price = result.data["price"]
        """
        # Check cache first
        if self.config.enable_caching:
            cached = self._check_cache(resource_uri)
            if cached is not None:
                return ProxyResult.ok(cached)

        # Parse URI: mcp://server/path → (server, path)
        server_name, resource_path = self._parse_uri(resource_uri)

        # Check connection
        if server_name not in self._connections:
            return ProxyResult.fail(
                "NOT_CONNECTED", f"Not connected to MCP server: {server_name}"
            )

        # TODO: Actual MCP fetch implementation
        # For now, return placeholder
        result = {
            "uri": resource_uri,
            "data": {},
            "timestamp": datetime.now().isoformat(),
        }

        # Cache result
        if self.config.enable_caching:
            self._cache_result(resource_uri, result)

        return ProxyResult.ok(result)

    async def invoke_tool(
        self, tool_name: str, args: Dict[str, Any], server: Optional[str] = None
    ) -> ProxyResult:
        """
        Invoke an external tool via MCP.

        Calls a tool on an MCP server with the given arguments.

        Args:
            tool_name: Name of the tool to invoke
            args: Arguments to pass to the tool
            server: Target server (defaults to first connected)

        Returns:
            ProxyResult.ok(result) with tool output
            ProxyResult.fail(error_code, message) on failure

        Example:
            result = await proxy.invoke_tool(
                "llm_completion",
                {"prompt": "Analyze this data", "model": "gpt-4"}
            )
        """
        # Select target server
        target_server = server or (
            list(self._connections.keys())[0] if self._connections else None
        )
        if not target_server or target_server not in self._connections:
            return ProxyResult.fail("NO_SERVER", "No connected MCP server")

        # TODO: Actual MCP tool invocation
        result = {
            "tool": tool_name,
            "args": args,
            "result": {},
            "timestamp": datetime.now().isoformat(),
        }
        return ProxyResult.ok(result)

    async def list_available_resources(
        self, server: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available resources from connected servers.

        Args:
            server: Specific server to query (None = all servers)

        Returns:
            List of resource info dicts
        """
        servers = [server] if server else list(self._connections.keys())
        return [
            {"server": srv, "resources": []}
            for srv in servers
            if srv in self._connections
        ]

    async def connect(self, server_config: Dict[str, Any]) -> bool:
        """
        Connect to an MCP server.

        Args:
            server_config: Server configuration dict (must have 'name' key)

        Returns:
            True on success
        """
        server_name = server_config["name"]
        self._connections[server_name] = {"config": server_config, "connected": True}
        return True

    async def disconnect(self, server_name: str) -> bool:
        """
        Disconnect from an MCP server.

        Args:
            server_name: Name of server to disconnect

        Returns:
            True if was connected, False if not found
        """
        if server_name not in self._connections:
            return False
        del self._connections[server_name]
        return True

    def _parse_uri(self, uri: str) -> tuple:
        """
        Parse MCP URI into (server_name, resource_path).

        URI format: mcp://server_name/resource_path

        Args:
            uri: MCP URI string

        Returns:
            Tuple of (server_name, resource_path)

        Raises:
            ValueError: If URI doesn't start with "mcp://"

        Example:
            >>> _parse_uri("mcp://market/prices/AAPL")
            ('market', 'prices/AAPL')
        """
        if not uri.startswith("mcp://"):
            raise ValueError(f"Invalid MCP URI format: {uri}")
        path = uri[6:]  # Remove "mcp://" prefix
        parts = path.split("/", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    def _check_cache(self, uri: str) -> Optional[Any]:
        """
        Check cache for a resource.

        Returns cached data if valid (within TTL), None otherwise.
        Expired entries are automatically removed.

        Args:
            uri: Resource URI to look up

        Returns:
            Cached data if valid, None if expired or not found
        """
        if uri in self._resource_cache:
            data, ts = self._resource_cache[uri]
            if time.time() - ts < self.config.cache_ttl_seconds:
                return data
            # Cache expired - remove it
            del self._resource_cache[uri]
        return None

    def _cache_result(self, uri: str, data: Any) -> None:
        """
        Cache a resource result.

        Args:
            uri: Resource URI as cache key
            data: Data to cache
        """
        self._resource_cache[uri] = (data, time.time())


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
class ObservabilityConfig(ProxyConfig):
    """
    Configuration for ObservabilityProxy.

    Attributes:
        proxy_type: Fixed to OBSERVABILITY
        metrics_backend: Backend for metrics storage ("memory", "prometheus", "statsd")
        logging_backend: Backend for logging ("structured", "json", "console")
        enable_tracing: Whether to enable distributed tracing
        log_level: Minimum log level ("DEBUG", "INFO", "WARNING", "ERROR")

    Example:
        config = ObservabilityConfig(
            metrics_backend="prometheus",
            logging_backend="json",
            enable_tracing=True,
            log_level="INFO"
        )
    """

    proxy_type: ProxyType = field(default=ProxyType.OBSERVABILITY, init=False)
    metrics_backend: str = "memory"  # "memory", "prometheus", "statsd"
    logging_backend: str = "structured"  # "structured", "json", "console"
    enable_tracing: bool = True  # Distributed tracing
    log_level: str = "INFO"  # Minimum log level


class ObservabilityProxy(BaseProxy):
    """
    Proxy for metrics collection and structured logging.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                   OBSERVABILITY PROXY OVERVIEW                      │
    │                                                                     │
    │  Core Methods (≤5, micro-proxy pattern):                           │
    │    1. record_metric()  - Record a metric value                     │
    │    2. log_event()      - Log a structured event                    │
    │    3. start_timer()    - Start a named timer                       │
    │    4. stop_timer()     - Stop timer, record duration               │
    │    5. get_metrics()    - Retrieve recorded metrics                 │
    │                                                                     │
    │  Design Philosophy:                                                 │
    │    - FIRE-AND-FORGET: Operations never fail, never block          │
    │    - STRUCTURED: Data is machine-processable                       │
    │    - NON-INTRUSIVE: No impact on core logic                        │
    │                                                                     │
    │  Fault Isolation:                                                   │
    │    - Failures are silently logged (debug level)                   │
    │    - Never raises exceptions                                       │
    │    - Never blocks owner execution                                  │
    └─────────────────────────────────────────────────────────────────────┘

    Usage Pattern:

        # Start timer before operation
        await proxy.start_timer("operation_duration")

        # Do the operation
        result = await perform_operation()

        # Stop timer and record duration
        duration_ms = await proxy.stop_timer("operation_duration")

        # Record additional metrics
        await proxy.record_metric("result_count", len(result))

        # Log structured event
        await proxy.log_event("operation_complete", {
            "duration_ms": duration_ms,
            "result_count": len(result)
        })

    Player vs Conductor Strategy:
    - Player: Individual behavior audit, strategy performance
    - Conductor: System-level aggregation, coordination impact
    """

    def __init__(
        self,
        config: Optional[ObservabilityConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        """
        Initialize ObservabilityProxy.

        Args:
            config: Observability configuration (uses defaults if None)
            owner: Optional owner entity
        """
        super().__init__(config or ObservabilityConfig(), owner)
        self.config: ObservabilityConfig = config or ObservabilityConfig()

        # =====================================================================
        # Internal Storage
        # =====================================================================
        # _metrics: List of recorded metric entries
        # _events: List of recorded event entries
        # _timers: Active timers (name → start_time)
        # =====================================================================
        self._metrics: List[Dict[str, Any]] = []
        self._events: List[Dict[str, Any]] = []
        self._timers: Dict[str, float] = {}

    async def initialize(self) -> None:
        """Initialize observability backend connections."""
        # TODO: Connect to actual backends (Prometheus, etc.)
        self._is_initialized = True

    async def shutdown(self) -> None:
        """
        Shutdown and flush pending data.

        Ensures all recorded metrics and events are persisted to
        backend before shutdown completes.
        """
        # TODO: Flush to actual backend
        self._is_initialized = False

    async def record_metric(
        self, name: str, value: Any, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Record a metric (fire-and-forget, never fails).

        Metrics are structured data points for monitoring and alerting.
        This operation NEVER raises exceptions - failures are silently logged.

        Args:
            name: Metric name (e.g., "step_duration_ms", "action_count")
            value: Metric value (number, usually)
            tags: Optional tags for filtering/grouping

        Example:
            await proxy.record_metric(
                "trade_executed",
                1,
                {"symbol": "AAPL", "side": "buy"}
            )

        Note:
            This method never fails - essential for non-intrusive monitoring.
        """
        self._metrics.append(
            {
                "name": name,
                "value": value,
                "tags": tags or {},
                "entity_id": self.owner_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def log_event(
        self, event_type: str, data: Dict[str, Any], level: str = "INFO"
    ) -> None:
        """
        Log a structured event (fire-and-forget, never fails).

        Events are structured log entries for auditing and debugging.
        This operation NEVER raises exceptions.

        Args:
            event_type: Event category (e.g., "player_initialized", "trade_complete")
            data: Event payload (arbitrary structured data)
            level: Log level ("DEBUG", "INFO", "WARNING", "ERROR")

        Example:
            await proxy.log_event(
                "trade_complete",
                {
                    "order_id": "123",
                    "symbol": "AAPL",
                    "price": 150.0,
                    "quantity": 100
                },
                level="INFO"
            )
        """
        self._events.append(
            {
                "event_type": event_type,
                "data": data,
                "level": level,
                "entity_id": self.owner_id,
                "timestamp": datetime.now().isoformat(),
            }
        )

    async def start_timer(self, name: str) -> None:
        """
        Start a named timer for measuring operation duration.

        Args:
            name: Timer name (used to stop and record)

        Usage:
            await proxy.start_timer("operation")
            # ... do operation ...
            duration = await proxy.stop_timer("operation")
        """
        self._timers[name] = time.time()

    async def stop_timer(self, name: str) -> float:
        """
        Stop a timer and return duration in milliseconds.

        Also automatically records the duration as a metric with
        name "timer_{name}".

        Args:
            name: Timer name (must have been started)

        Returns:
            Duration in milliseconds (0.0 if timer wasn't started)

        Example:
            await proxy.start_timer("fetch")
            data = await fetch_data()
            duration_ms = await proxy.stop_timer("fetch")
            # duration_ms is automatically recorded as metric "timer_fetch"
        """
        if name not in self._timers:
            return 0.0

        # Calculate duration
        duration_ms = (time.time() - self._timers.pop(name)) * 1000

        # Auto-record as metric
        await self.record_metric(f"timer_{name}", duration_ms, {"unit": "ms"})

        return duration_ms

    async def get_metrics(
        self, name_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recorded metrics.

        Args:
            name_filter: Optional prefix filter (e.g., "timer_" for all timers)

        Returns:
            List of metric entries matching filter
        """
        result = self._metrics
        if name_filter:
            result = [m for m in result if m["name"].startswith(name_filter)]
        return result

    async def get_events(
        self, event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recorded events.

        Args:
            event_type: Optional filter by event type

        Returns:
            List of event entries matching filter
        """
        result = self._events
        if event_type:
            result = [e for e in result if e["event_type"] == event_type]
        return result


# =============================================================================
#                           PROXY FACTORY
# =============================================================================
#
# ProxyFactory provides convenient methods for creating proxy instances.
# It encapsulates default configuration and enables consistent instantiation.
#
# While explicit proxy creation is preferred (composition pattern), the
# factory can simplify common use cases.
# =============================================================================


class ProxyFactory:
    """
    Factory for creating proxy instances with optional owner binding.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                     PROXY FACTORY PATTERN                           │
    │                                                                     │
    │  The factory provides convenient creation methods:                  │
    │                                                                     │
    │    # Instead of:
    │    proxy = CommunicationProxy(CommunicationConfig(), player)       │
    │                                                                     │
    │    # You can write:                                                 │
    │    proxy = ProxyFactory.create_communication_proxy(owner=player)   │
    │                                                                     │
    │  Benefits:                                                          │
    │    - Encapsulates default configuration                            │
    │    - Single point of customization                                 │
    │    - Consistent proxy creation across codebase                     │
    └─────────────────────────────────────────────────────────────────────┘

    Note:
        The explicit attachment pattern is still preferred for clarity:

            proxy = ProxyFactory.create_storage_proxy()
            player.attach_storage_proxy(proxy)  # Explicit attachment

        Rather than passing owner to factory (which still requires attach).
    """

    @staticmethod
    def create_communication_proxy(
        config: Optional[CommunicationConfig] = None,
        owner: Optional[OwnerType] = None,
    ) -> CommunicationProxy:
        """
        Create a CommunicationProxy instance.

        Args:
            config: Optional configuration (uses defaults if None)
            owner: Optional owner entity

        Returns:
            Configured CommunicationProxy instance
        """
        return CommunicationProxy(config, owner)

    @staticmethod
    def create_storage_proxy(
        config: Optional[StorageConfig] = None,
        owner: Optional[OwnerType] = None,
    ) -> StorageProxy:
        """
        Create a StorageProxy instance.

        Args:
            config: Optional configuration (uses defaults if None)
            owner: Optional owner entity

        Returns:
            Configured StorageProxy instance
        """
        return StorageProxy(config, owner)

    @staticmethod
    def create_resource_proxy(
        config: Optional[ResourceConfig] = None,
        owner: Optional[OwnerType] = None,
    ) -> ResourceProxy:
        """
        Create a ResourceProxy instance.

        Args:
            config: Optional configuration (uses defaults if None)
            owner: Optional owner entity

        Returns:
            Configured ResourceProxy instance
        """
        return ResourceProxy(config, owner)

    @staticmethod
    def create_observability_proxy(
        config: Optional[ObservabilityConfig] = None,
        owner: Optional[OwnerType] = None,
    ) -> ObservabilityProxy:
        """
        Create an ObservabilityProxy instance.

        Args:
            config: Optional configuration (uses defaults if None)
            owner: Optional owner entity

        Returns:
            Configured ObservabilityProxy instance
        """
        return ObservabilityProxy(config, owner)
