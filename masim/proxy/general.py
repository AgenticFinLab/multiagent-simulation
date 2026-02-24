"""
General Proxy Implementations for MASim Framework.

This module provides concrete proxy implementations:
    - SendReceiveProxy: Message routing (send, broadcast, receive)
    - StorageProxy: State checkpoint/restore using BlockBasedStoreManager
    - ResourceProxy: MCP resource access
    - MonitoringProxy: Metrics and logging

Base classes and configs are in base.py; implementations are here.
"""

import os
import time
from collections import deque
from datetime import datetime
from typing import Any, Awaitable, Callable, Dict, List, Optional, TYPE_CHECKING

from masim.proxy.base import (
    # Types
    ProxyType,
    OwnerType,
    BaseProxy,
    ProxyResult,
    # Configs
    SendReceiveConfig,
    StorageConfig,
    ResourceConfig,
    MonitoringConfig,
)
from masim.communication.base import Message
from lmbase.utils.tools import BlockBasedStoreManager

if TYPE_CHECKING:
    pass


# =============================================================================
#                       COMMUNICATION PROXY
# =============================================================================


class SendReceiveProxy(BaseProxy):
    """
    Proxy for message routing and reliable transmission.

    Core Methods:
        1. send()       - Send to specific recipient
        2. broadcast()  - Send to multiple recipients
        3. receive()    - Retrieve pending messages
        4. subscribe()  - Register for real-time delivery
        5. unsubscribe()- Remove subscription
    """

    def __init__(
        self,
        config: Optional[SendReceiveConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config or SendReceiveConfig(), owner)
        self.config: SendReceiveConfig = config or SendReceiveConfig()
        self.subscriptions: Dict[str, Callable[[Message], Awaitable[None]]] = {}
        self.pending_messages: Dict[str, List[Message]] = {}

    async def initialize(self) -> None:
        self.is_initialized = True

    async def shutdown(self) -> None:
        self.subscriptions.clear()
        self.pending_messages.clear()
        self.is_initialized = False

    async def send(self, message: Message) -> ProxyResult:
        """Send a message to a specific recipient."""
        if not message.recipient_id:
            return ProxyResult.fail(
                "INVALID_RECIPIENT", "Message must have recipient_id"
            )

        if message.recipient_id not in self.pending_messages:
            self.pending_messages[message.recipient_id] = []
        self.pending_messages[message.recipient_id].append(message)

        if message.recipient_id in self.subscriptions:
            await self.subscriptions[message.recipient_id](message)

        return ProxyResult.ok()

    async def broadcast(
        self, message: Message, scope: Optional[str] = None
    ) -> ProxyResult:
        """Broadcast a message to multiple recipients."""
        message.extras["broadcast_scope"] = scope or "all"

        for recipient_id in list(self.pending_messages.keys()):
            self.pending_messages[recipient_id].append(message)
            if recipient_id in self.subscriptions:
                await self.subscriptions[recipient_id](message)

        return ProxyResult.ok()

    async def receive(self, entity_id: str) -> List[Message]:
        """Receive pending messages for an entity."""
        if entity_id in self.pending_messages:
            messages = self.pending_messages[entity_id].copy()
        else:
            messages = []
        self.pending_messages[entity_id] = []

        owner = self.get_owner()
        if owner and hasattr(owner, "on_message"):
            for msg in messages:
                owner.on_message(msg)

        return messages

    async def subscribe(
        self, entity_id: str, callback: Callable[[Message], Awaitable[None]]
    ) -> bool:
        """Subscribe to messages with a callback for real-time delivery."""
        self.subscriptions[entity_id] = callback
        if entity_id not in self.pending_messages:
            self.pending_messages[entity_id] = []
        return True

    async def unsubscribe(self, entity_id: str) -> bool:
        """Unsubscribe from real-time message delivery."""
        self.subscriptions.pop(entity_id, None)
        return True


# =============================================================================
#                          STORAGE PROXY
# =============================================================================


class StorageProxy(BaseProxy):
    """Proxy for state persistence using BlockBasedStoreManager."""

    def __init__(
        self,
        config: StorageConfig,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config, owner)
        self.config: StorageConfig = config
        self._message_stores: Dict[str, BlockBasedStoreManager] = {}
        self._turn_stores: Dict[str, BlockBasedStoreManager] = {}

    def _get_base_path(self, player_id: str) -> str:
        """Get base path for player storage: {record_path}/{player_id}"""
        return os.path.join(self.config.record_path, player_id)

    def _get_message_store(self, player_id: str) -> BlockBasedStoreManager:
        """Get or create message store for player."""
        if player_id not in self._message_stores:
            msg_dir = os.path.join(self._get_base_path(player_id), "messages")
            os.makedirs(msg_dir, exist_ok=True)
            self._message_stores[player_id] = BlockBasedStoreManager(
                folder=msg_dir, file_format="json", block_size=500
            )
        return self._message_stores[player_id]

    def _get_turn_store(self, player_id: str) -> BlockBasedStoreManager:
        """Get or create turn store for player."""
        if player_id not in self._turn_stores:
            turn_dir = os.path.join(self._get_base_path(player_id), "turns")
            os.makedirs(turn_dir, exist_ok=True)
            self._turn_stores[player_id] = BlockBasedStoreManager(
                folder=turn_dir, file_format="json", block_size=500
            )
        return self._turn_stores[player_id]

    def record_message(
        self, player_id: str, round_num: int, message: Any, direction: str
    ) -> None:
        """Record a message using BlockBasedStoreManager."""
        if not self.config.record_rounds:
            return

        serialized_message = (
            message.to_dict() if hasattr(message, "to_dict") else message
        )

        timestamp = datetime.now()
        record = {
            "round_num": round_num,
            "direction": direction,
            "timestamp": timestamp.isoformat(),
            "message": serialized_message,
        }
        # Format: msg_r{round}_{MMDDHHMMSS}
        # e.g., msg_r000001_0221143052
        savename = f"msg_r{round_num:06d}_{timestamp.strftime('%m%d%H%M%S')}"
        self._get_message_store(player_id).save(savename=savename, data=record)

    def record_turn_result(
        self, player_id: str, round_num: int, turn_result: Any
    ) -> None:
        """Record turn result using BlockBasedStoreManager."""
        if not self.config.record_rounds:
            return
        serialized_result = (
            turn_result.to_dict() if hasattr(turn_result, "to_dict") else turn_result
        )
        timestamp = datetime.now()
        record = {
            "round_num": round_num,
            "timestamp": timestamp.isoformat(),
            "turn_result": serialized_result,
        }
        # Format: turn_r{round}_{MMDDHHMMSS}
        # e.g., turn_r000001_0221143052
        savename = f"turn_r{round_num:06d}_{timestamp.strftime('%m%d%H%M%S')}"
        self._get_turn_store(player_id).save(savename=savename, data=record)

    async def initialize(self) -> None:
        self.is_initialized = True

    async def shutdown(self) -> None:
        for store in self._message_stores.values():
            store.flush()
        for store in self._turn_stores.values():
            store.flush()
        self.is_initialized = False


# =============================================================================
#                          RESOURCE PROXY
# =============================================================================


class ResourceProxy(BaseProxy):
    """Proxy for MCP connection management and resource access."""

    def __init__(
        self,
        config: Optional[ResourceConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config or ResourceConfig(), owner)
        self.config: ResourceConfig = config or ResourceConfig()
        self._connections: Dict[str, Any] = {}
        self._resource_cache: Dict[str, tuple] = {}

    async def initialize(self) -> None:
        for server_config in self.config.mcp_servers:
            server_name = server_config["name"]
            self._connections[server_name] = {
                "config": server_config,
                "connected": True,
            }
        self.is_initialized = True

    async def shutdown(self) -> None:
        self._connections.clear()
        self._resource_cache.clear()
        self.is_initialized = False

    async def fetch_resource(self, resource_uri: str) -> ProxyResult:
        """Fetch a resource via MCP protocol."""
        if self.config.enable_caching:
            cached = self._check_cache(resource_uri)
            if cached is not None:
                return ProxyResult.ok(cached)

        server_name, _ = self._parse_uri(resource_uri)

        if server_name not in self._connections:
            return ProxyResult.fail(
                "NOT_CONNECTED", f"Not connected to MCP server: {server_name}"
            )

        result = {
            "uri": resource_uri,
            "data": {},
            "timestamp": datetime.now().isoformat(),
        }

        if self.config.enable_caching:
            self._cache_result(resource_uri, result)

        return ProxyResult.ok(result)

    async def invoke_tool(
        self, tool_name: str, args: Dict[str, Any], server: Optional[str] = None
    ) -> ProxyResult:
        """Invoke an external tool via MCP."""
        target_server = server or (
            list(self._connections.keys())[0] if self._connections else None
        )
        if not target_server or target_server not in self._connections:
            return ProxyResult.fail("NO_SERVER", "No connected MCP server")

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
        """List available resources from connected servers."""
        servers = [server] if server else list(self._connections.keys())
        return [
            {"server": srv, "resources": []}
            for srv in servers
            if srv in self._connections
        ]

    async def connect(self, server_config: Dict[str, Any]) -> bool:
        """Connect to an MCP server."""
        server_name = server_config["name"]
        self._connections[server_name] = {"config": server_config, "connected": True}
        return True

    async def disconnect(self, server_name: str) -> bool:
        """Disconnect from an MCP server."""
        if server_name not in self._connections:
            return False
        del self._connections[server_name]
        return True

    def _parse_uri(self, uri: str) -> tuple:
        """Parse MCP URI into (server_name, resource_path)."""
        if not uri.startswith("mcp://"):
            raise ValueError(f"Invalid MCP URI format: {uri}")
        path = uri[6:]
        parts = path.split("/", 1)
        return parts[0], parts[1] if len(parts) > 1 else ""

    def _check_cache(self, uri: str) -> Optional[Any]:
        """Check cache for a resource."""
        if uri in self._resource_cache:
            data, ts = self._resource_cache[uri]
            if time.time() - ts < self.config.cache_ttl_seconds:
                return data
            del self._resource_cache[uri]
        return None

    def _cache_result(self, uri: str, data: Any) -> None:
        """Cache a resource result."""
        self._resource_cache[uri] = (data, time.time())


# =============================================================================
#                        MONITORING PROXY
# =============================================================================


class MonitoringProxy(BaseProxy):
    """Proxy for metrics collection and structured logging.

    Memory Optimization:
    - Uses deque(maxlen=METRICS_LIMIT) to prevent unbounded memory growth
    - Recent metrics/events kept in memory for quick access
    - Old data automatically evicted (can be persisted separately if needed)
    """

    # Default limit for in-memory metrics/events
    METRICS_LIMIT = 50
    EVENTS_LIMIT = 50

    def __init__(
        self,
        config: Optional[MonitoringConfig] = None,
        owner: Optional[OwnerType] = None,
    ):
        super().__init__(config or MonitoringConfig(), owner)
        self.config: MonitoringConfig = config or MonitoringConfig()
        # Use deque with maxlen to prevent unbounded memory growth
        self._metrics: deque = deque(maxlen=self.METRICS_LIMIT)
        self._events: deque = deque(maxlen=self.EVENTS_LIMIT)
        self._timers: Dict[str, float] = {}

    async def initialize(self) -> None:
        self.is_initialized = True

    async def shutdown(self) -> None:
        self.is_initialized = False

    async def record_metric(
        self, name: str, value: Any, tags: Optional[Dict[str, str]] = None
    ) -> None:
        """Record a metric (fire-and-forget, never fails)."""
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
        """Log a structured event (fire-and-forget, never fails)."""
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
        """Start a named timer for measuring operation duration."""
        self._timers[name] = time.time()

    async def stop_timer(self, name: str) -> float:
        """Stop a timer and return duration in milliseconds."""
        if name not in self._timers:
            return 0.0

        duration_ms = (time.time() - self._timers.pop(name)) * 1000
        await self.record_metric(f"timer_{name}", duration_ms, {"unit": "ms"})
        return duration_ms

    async def get_metrics(
        self, name_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recorded metrics."""
        result = self._metrics
        if name_filter:
            result = [m for m in result if m["name"].startswith(name_filter)]
        return result

    async def get_events(
        self, event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recorded events."""
        result = self._events
        if event_type:
            result = [e for e in result if e["event_type"] == event_type]
        return result


# =============================================================================
#                       CONVENIENCE FUNCTIONS
# =============================================================================


def create_default_proxies(
    owner: Optional[OwnerType] = None,
) -> Dict[ProxyType, BaseProxy]:
    """Create a complete set of proxies with default configurations."""
    return {
        ProxyType.COMMUNICATION: SendReceiveProxy(SendReceiveConfig(), owner),
        ProxyType.STORAGE: StorageProxy(StorageConfig(), owner),
        ProxyType.RESOURCE: ResourceProxy(ResourceConfig(), owner),
        ProxyType.OBSERVABILITY: MonitoringProxy(MonitoringConfig(), owner),
    }


def create_minimal_proxies(
    owner: Optional[OwnerType] = None,
) -> Dict[ProxyType, BaseProxy]:
    """Create a minimal proxy set with just storage and observability."""
    return {
        ProxyType.STORAGE: StorageProxy(StorageConfig(), owner),
        ProxyType.OBSERVABILITY: MonitoringProxy(MonitoringConfig(), owner),
    }


def create_proxies_for_owner(
    owner: OwnerType,
    include_communication: bool = True,
    include_storage: bool = True,
    include_resource: bool = True,
    include_monitoring: bool = True,
) -> Dict[ProxyType, BaseProxy]:
    """Create a customized proxy set for a specific owner."""
    proxies = {}

    if include_communication:
        proxies[ProxyType.COMMUNICATION] = SendReceiveProxy(SendReceiveConfig(), owner)

    if include_storage:
        proxies[ProxyType.STORAGE] = StorageProxy(StorageConfig(), owner)

    if include_resource:
        proxies[ProxyType.RESOURCE] = ResourceProxy(ResourceConfig(), owner)

    if include_monitoring:
        proxies[ProxyType.OBSERVABILITY] = MonitoringProxy(MonitoringConfig(), owner)

    return proxies


# =============================================================================
#                      SIMPLIFIED PROXY WRAPPERS
# =============================================================================


class SimpleStorageProxy(StorageProxy):
    """Simplified StorageProxy with sensible defaults."""

    def __init__(self, owner: Optional[OwnerType] = None):
        config = StorageConfig(
            checkpoint_dir="checkpoints",
            record_path="records",
            record_rounds=True,
        )
        super().__init__(config, owner)


class SimpleMonitoringProxy(MonitoringProxy):
    """Simplified MonitoringProxy with sensible defaults."""

    def __init__(self, owner: Optional[OwnerType] = None):
        config = MonitoringConfig(
            metrics_backend="memory",
            logging_backend="structured",
            enable_tracing=False,
            log_level="INFO",
        )
        super().__init__(config, owner)


# Re-export
__all__ = [
    # Proxy implementations
    "SendReceiveProxy",
    "StorageProxy",
    "ResourceProxy",
    "MonitoringProxy",
    # Convenience functions
    "create_default_proxies",
    "create_minimal_proxies",
    "create_proxies_for_owner",
    # Simplified wrappers
    "SimpleStorageProxy",
    "SimpleMonitoringProxy",
]
