"""MASim Proxy Module.

This module provides infrastructure abstraction through the micro-proxy pattern.
Proxies support weak references to owners and graceful degradation.

Base Classes and Types (base.py):
    - ObservableEntity: Protocol for proxy owners
    - BaseProxy: Abstract base class for all proxy types
    - ProxyType: Enum of proxy types
    - ProxyConfig: Base configuration for proxies
    - ProxyResult: Result wrapper for graceful degradation
    - Config dataclasses: SendReceiveConfig, StorageConfig, MonitoringConfig
    - Error types: ProxyError, ProxyNotInitializedError, ProxyOperationError

Proxy Implementations (general.py):
    - SendReceiveProxy: Message routing and transmission
    - StorageProxy: State checkpoint and rollback
    - MonitoringProxy: Metrics and structured logging

Message-layer types (Message, MessageType, MessagePriority) and the
Info → Message helper (build_message_from_info) live in
masim.communication.base / masim.communication.general — proxy is a
consumer of those types, not their owner.
"""

from masim.proxy.base import (
    # Observable Entity Protocol
    ObservableEntity,
    # Error types
    ProxyError,
    ProxyNotInitializedError,
    ProxyOperationError,
    ProxyResult,
    # Base proxy types
    ProxyType,
    ProxyConfig,
    BaseProxy,
    OwnerType,
    # Config dataclasses
    SendReceiveConfig,
    StorageConfig,
    MonitoringConfig,
)

from masim.proxy.general import (
    # Proxy implementations
    SendReceiveProxy,
    StorageProxy,
    MonitoringProxy,
)

__all__ = [
    # Observable Entity Protocol
    "ObservableEntity",
    # Error types
    "ProxyError",
    "ProxyNotInitializedError",
    "ProxyOperationError",
    "ProxyResult",
    # Base proxy types
    "ProxyType",
    "ProxyConfig",
    "BaseProxy",
    "OwnerType",
    # Communication proxy
    "SendReceiveConfig",
    "SendReceiveProxy",
    # Storage proxy
    "StorageConfig",
    "StorageProxy",
    # Monitoring proxy
    "MonitoringConfig",
    "MonitoringProxy",
]
