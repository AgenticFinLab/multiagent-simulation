"""MASim Proxy Module.

This module provides infrastructure abstraction through the micro-proxy pattern.
Proxies support weak references to owners and graceful degradation.

Base Classes and Types (base.py):
    - ObservableEntity: Protocol for proxy owners
    - BaseProxy: Abstract base class for all proxy types
    - ProxyType: Enum of proxy types
    - ProxyConfig: Base configuration for proxies
    - ProxyResult: Result wrapper for graceful degradation
    - Config dataclasses: SendReceiveConfig, StorageConfig, ResourceConfig, MonitoringConfig
    - Error types: ProxyError, ProxyNotInitializedError, ProxyOperationError
    - MessageType, MessagePriority: Enums for proxy-layer message routing
    - Message: Proxy-layer routed message (sender_id, recipient_id, payload, etc.)

Proxy Implementations (general.py):
    - SendReceiveProxy: Message routing and transmission
    - StorageProxy: State checkpoint and rollback
    - ResourceProxy: MCP resource access
    - MonitoringProxy: Metrics and structured logging

Helper Functions (general.py):
    - build_message_from_info(): Convert player-layer Info → proxy-layer Message
    - create_default_proxies(): Create all proxies with defaults
    - create_minimal_proxies(): Create just storage and monitoring
    - create_proxies_for_owner(): Create customized proxy set
    - SimpleStorageProxy: Simplified storage with defaults
    - SimpleMonitoringProxy: Simplified monitoring with defaults
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
    # Message types (proxy-layer)
    MessageType,
    MessagePriority,
    Message,
    # Config dataclasses
    SendReceiveConfig,
    StorageConfig,
    ResourceConfig,
    MonitoringConfig,
)

from masim.proxy.general import (
    # Proxy implementations
    SendReceiveProxy,
    StorageProxy,
    ResourceProxy,
    MonitoringProxy,
    # Message helper
    build_message_from_info,
    # Convenience functions
    create_default_proxies,
    create_minimal_proxies,
    create_proxies_for_owner,
    # Simplified wrappers
    SimpleStorageProxy,
    SimpleMonitoringProxy,
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
    # Message types (proxy-layer)
    "MessageType",
    "MessagePriority",
    "Message",
    # Communication
    "SendReceiveConfig",
    "SendReceiveProxy",
    # Storage
    "StorageConfig",
    "StorageProxy",
    # Resource
    "ResourceConfig",
    "ResourceProxy",
    # Monitoring
    "MonitoringConfig",
    "MonitoringProxy",
    # Message helper
    "build_message_from_info",
    # Convenience functions
    "create_default_proxies",
    "create_minimal_proxies",
    "create_proxies_for_owner",
    # Simplified wrappers
    "SimpleStorageProxy",
    "SimpleMonitoringProxy",
]
