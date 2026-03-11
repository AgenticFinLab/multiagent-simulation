# MASim Framework Memory Usage Analysis

Analysis of memory allocation and usage patterns in the `masim/` framework code.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component-Level Analysis](#2-component-level-analysis)
3. [Memory Growth Classification](#3-memory-growth-classification)
4. [Risk Assessment](#4-risk-assessment)
5. [Memory Estimation](#5-memory-estimation)

---

## 1. Architecture Overview

### 1.1 Memory Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MEMORY ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Simulator (Driver Process)                                                 │
│     ├── history: HistoryBuffer              [Bounded, hot/cold]             │
│     ├── player_persona_handles: Dict        [O(N) references]               │
│     ├── topology: TopologyGraph             [O(V + E)]                      │
│     └── communication: CommunicationChannel [Buffer → disk]                 │
│                                                                              │
│  PlayerPersona × N (Ray Actors)                                             │
│     ├── storage: StorageProxy               [Buffer → disk]                 │
│     ├── monitoring: MonitoringProxy         [2 × HistoryBuffer]             │
│     ├── resource: ResourceProxy             [TTL-bounded cache]             │
│     └── player: BasePlayer                                                  │
│           ├── inbounds: List[Inbound]       [Transient, cleared/round]      │
│           ├── pending_outbounds: List       [Transient, cleared/round]      │
│           └── state: PlayerState                                            │
│                 └── custom_state: Dict      [Framework: O(1), User: ⚠️]     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Hot/Cold Storage Architecture

```
┌─────────────────┐  overflow   ┌─────────────────────────────┐
│   Hot (deque)   │ ─────────►  │  Cold (BlockBasedStoreManager) │
│  maxlen=N       │             │  (JSON blocks on disk)      │
└─────────────────┘             └─────────────────────────────┘
```

| Tier     | Location       | Access | Capacity  | Growth    |
|----------|----------------|--------|-----------|-----------|
| **Hot**  | Memory (deque) | O(1)   | Bounded   | O(1)      |
| **Cold** | Disk (JSON)    | O(n)   | Unbounded | O(rounds) |

---

## 2. Component-Level Analysis

### 2.1 HistoryBuffer

**Source**: `masim/utils/history.py`

```python
class HistoryBuffer:
    hot: deque                    # maxlen=entry_limit
    cold_store: BlockBasedStoreManager  # Disk-based
    _pending_cold: List           # Batch buffer before flush
    cold_count: int               # Counter
    total_count: int              # Counter
```

| Field           | Type                     | Memory                    | Notes             |
|-----------------|--------------------------|---------------------------|-------------------|
| `hot`           | `deque(maxlen=N)`        | O(N × item_size)          | Fixed upper bound |
| `_pending_cold` | `List`                   | O(block_size × item_size) | Flushed when full |
| `cold_store`    | `BlockBasedStoreManager` | ~0                        | Disk-only         |
| `cold_count`    | `int`                    | 8 bytes                   | Counter           |
| `total_count`   | `int`                    | 8 bytes                   | Counter           |

**Configuration**:
| Parameter     | Default | Description            |
|---------------|---------|------------------------|
| `entry_limit` | 100     | Max items in hot deque |
| `block_size`  | 50      | Items per disk block   |

---

### 2.2 StorageProxy

**Source**: `masim/proxy/general.py`

```python
class StorageProxy:
    _message_stores: Dict[str, BlockBasedStoreManager]  # Per-player
    _turn_stores: Dict[str, BlockBasedStoreManager]     # Per-player
```

| Field             | Type                                | Memory                        | Notes                  |
|-------------------|-------------------------------------|-------------------------------|------------------------|
| `_message_stores` | `Dict[str, BlockBasedStoreManager]` | O(N × block_size × msg_size)  | N players, buffer only |
| `_turn_stores`    | `Dict[str, BlockBasedStoreManager]` | O(N × block_size × turn_size) | N players, buffer only |

**Per-Player Buffer**:
- Message buffer: `block_size` × ~500 bytes
- Turn buffer: `block_size` × ~1KB

---

### 2.3 MonitoringProxy

**Source**: `masim/proxy/general.py`

```python
class MonitoringProxy:
    _metrics: HistoryBuffer   # entry_limit from config
    _events: HistoryBuffer    # entry_limit from config
    _timers: Dict[str, float] # Active timers
```

| Field      | Type               | Memory                 | Notes          |
|------------|--------------------|------------------------|----------------|
| `_metrics` | `HistoryBuffer`    | O(entry_limit × ~200B) | Bounded        |
| `_events`  | `HistoryBuffer`    | O(entry_limit × ~200B) | Bounded        |
| `_timers`  | `Dict[str, float]` | O(active_timers × 16B) | Typically < 10 |

**Default Memory** (entry_limit=100):
- Metrics hot: 100 × 200B = ~20KB
- Events hot: 100 × 200B = ~20KB
- Total: ~40KB per MonitoringProxy

---

### 2.4 ResourceProxy

**Source**: `masim/proxy/general.py`

```python
class ResourceProxy:
    _connections: Dict[str, Any]        # MCP server metadata
    _resource_cache: Dict[str, tuple]   # (data, timestamp)
```

| Field             | Type               | Memory     | Notes          |
|-------------------|--------------------|------------|----------------|
| `_connections`    | `Dict[str, Any]`   | O(servers) | Small metadata |
| `_resource_cache` | `Dict[str, tuple]` | Variable   | TTL-bounded    |

**TTL Mechanism**: Cache entries expire after `cache_ttl_seconds`, preventing unbounded growth.

---

### 2.5 PlayerState (✅ Framework Safe, ⚠️ User Risk)

**Source**: `masim/player/base.py`

```python
class PlayerState:
    turn_count: int                   # 8 bytes
    last_observation: Observation     # Reference only
    last_action: Action               # Reference only
    custom_state: Dict[str, Any]      # Framework: O(1), User: ⚠️
    # Timing fields: ~100 bytes total
```

| Field              | Type             | Memory              | Risk         |
|--------------------|------------------|---------------------|--------------|
| `turn_count`       | `int`            | 8 bytes             | None         |
| `last_observation` | `Observation`    | Reference           | None         |
| `last_action`      | `Action`         | Reference           | None         |
| `custom_state`     | `Dict[str, Any]` | **Framework: O(1)** | User code: ⚠️ |

**✅ Framework Usage** (in `GeneralPlayer.perceive()`):
```python
# OVERWRITES each round - O(1), safe
self.state.custom_state["last_observation"] = observation.data
self.state.custom_state["prev_action"] = prev_result.action
```

**⚠️ User Code Risk**: If user subclass appends to lists without bounds.

---

### 2.6 BasePlayer

**Source**: `masim/player/base.py`

```python
class BasePlayer:
    name: str                         # ~50 bytes
    identity: str                     # ~50 bytes
    group_tags: List[str]             # ~100 bytes
    config: PlayerConfig              # ~500 bytes
    state: PlayerState                # See 2.6
    inbounds: List[Inbound]           # Transient
    pending_outbounds: List[Outbound] # Transient
    expected_senders: Set[str]        # O(in-degree)
    capabilities: List[str]           # ~100 bytes
    topology_targets: List[str]       # O(out-degree)
```

| Field               | Type             | Memory        | Lifecycle                            |
|---------------------|------------------|---------------|--------------------------------------|
| `inbounds`          | `List[Inbound]`  | Transient     | Cleared via `get_pending_inbounds()` |
| `pending_outbounds` | `List[Outbound]` | Transient     | Cleared via `collect_outbounds()`    |
| `expected_senders`  | `Set[str]`       | O(in-degree)  | Static after init                    |
| `topology_targets`  | `List[str]`      | O(out-degree) | Static after init                    |

---

### 2.7 BaseSimulator

**Source**: `masim/simulator/base.py`

```python
class BaseSimulator:
    config: SimulationConfig          # ~1KB
    simulation_id: str                # ~50 bytes
    status: SimulatorStatus           # enum
    current_round: int                # 8 bytes
    current_phase: RoundPhase         # enum
    round_clock: ExecutionClock       # ~100 bytes
    player_persona_handles: Dict      # O(N) references
    history: HistoryBuffer            # Bounded
    topology: TopologyGraph           # O(V + E)
    communication: CommunicationChannel  # See 2.9
```

| Field                    | Type                     | Memory               | Notes           |
|--------------------------|--------------------------|----------------------|-----------------|
| `player_persona_handles` | `Dict[str, ActorHandle]` | O(N × 100B)          | References only |
| `history`                | `HistoryBuffer`          | O(entry_limit × 1KB) | Bounded         |
| `topology`               | `TopologyGraph`          | O(V + E)             | Static          |
| `communication`          | `CommunicationChannel`   | See below            | Buffer → disk   |

---

### 2.8 CommunicationChannel

**Source**: `masim/communication/base.py`

```python
class CommunicationChannel:
    config: Dict[str, Any]
    storage_path: str
    message_store: BlockBasedStoreManager  # block_size=500
```

| Field           | Type                     | Memory            | Notes                        |
|-----------------|--------------------------|-------------------|------------------------------|
| `message_store` | `BlockBasedStoreManager` | O(500 × msg_size) | Buffer only, flushes to disk |

**Buffer Size**: Up to 500 messages × ~500 bytes = ~250KB before flush.

---

### 2.10 PlayerPersona

**Source**: `masim/persona/general.py`

```python
class PlayerPersona:
    player_class: type                # Reference only
    player_config: PlayerConfig       # ~500 bytes
    config: Dict                      # ~1KB
    player: BasePlayer                # See 2.7
    storage: StorageProxy             # See 2.3
    monitoring: MonitoringProxy       # See 2.4
    communication: SendReceiveProxy   # See 2.2
    resource: ResourceProxy           # See 2.5
    topology: TopologyGraph           # O(V + E)
    peer_handles: Dict                # O(out-degree)
```

**Total per Persona** (framework overhead):
- BasePlayer core: ~5KB
- StorageProxy buffers: ~75KB
- MonitoringProxy hot: ~40KB
- ResourceProxy cache: ~10KB

**≈ 130KB per PlayerPersona** (framework only)

---

## 3. Memory Growth Classification

### 3.1 Constant O(1) - No growth with rounds

| Component                          | Size Factor | Location             |
|------------------------------------|-------------|----------------------|
| `Simulator.player_persona_handles` | O(N)        | `simulator/base.py`  |
| `Simulator.topology`               | O(V + E)    | `simulator/base.py`  |
| `PlayerPersona.peer_handles`       | O(degree)   | `persona/general.py` |
| `BasePlayer.expected_senders`      | O(degree)   | `player/base.py`     |
| `PlayerState.last_observation`     | O(1)        | `player/base.py`     |
| `PlayerState.last_action`          | O(1)        | `player/base.py`     |

### 3.2 Bounded O(k) - Configurable upper bound

| Component                                   | Bound       | Configuration                  |
|---------------------------------------------|-------------|--------------------------------|
| `Simulator.history.hot`                     | entry_limit | `setting.entry_limit`          |
| `MonitoringProxy._metrics.hot`              | entry_limit | `MonitoringConfig.entry_limit` |
| `MonitoringProxy._events.hot`               | entry_limit | `MonitoringConfig.entry_limit` |
| `StorageProxy._*_stores` buffer             | block_size  | `StorageConfig.entry_limit`    |
| `CommunicationChannel.message_store` buffer | 500         | Hardcoded                      |
| `HistoryBuffer._pending_cold`               | block_size  | Constructor param              |

### 3.3 Transient - Cleared each round

| Component                      | Clear Point              | Location             |
|--------------------------------|--------------------------|----------------------|
| `BasePlayer.inbounds`          | `get_pending_inbounds()` | `player/general.py`  |
| `BasePlayer.pending_outbounds` | `collect_outbounds()`    | `persona/general.py` |

### 3.4 Risk Summary

| Component                           | Framework Risk | User Code Risk | Notes                                  |
|-------------------------------------|----------------|----------------|----------------------------------------|
| `PlayerState.custom_state`          | ✅ **NONE**     | ⚠️ HIGH         | Framework overwrites, users may append |
| `SendReceiveProxy.pending_messages` | ✅ **NONE**     | N/A            | Dead code - never used                 |
| `ResourceProxy._resource_cache`     | ✅ Low          | N/A            | TTL prevents growth                    |

---

## 4. Risk Assessment

### 4.1 ✅ Framework Risk: NONE

After code path analysis, **no unbounded memory risks exist in the framework itself**.

| Component          | Status | Evidence                                                         |
|--------------------|--------|------------------------------------------------------------------|
| `custom_state`     | ✅ Safe | Framework overwrites `last_observation`/`prev_action` each round |
| `pending_messages` | ✅ Safe | Dead code - `send()`/`receive()` never called                    |
| `_resource_cache`  | ✅ Safe | TTL-based expiration                                             |
| `_pending_cold`    | ✅ Safe | Flushed on shutdown                                              |

### 4.2 ⚠️ User Code Risk

**The only memory risk comes from user code** that extends `GeneralPlayer`:

```python
# ⚠️ User anti-pattern (NOT in framework)
class UserPlayer(GeneralPlayer):
    async def perceive(self, observation, ...):
        # BAD: Appending without bounds
        self.state.custom_state.setdefault("history", []).append(data)
```

**Mitigation**: Users should use `HistoryBuffer` for time-series data.

### 4.3 Dead Code: SendReceiveProxy

`SendReceiveProxy` is instantiated but **never used**:
- `send()`, `receive()`, `broadcast()` - never called
- `pending_messages` - always empty `{}`

**Recommendation**: Consider removing or documenting as reserved for future use.

---

## 5. Memory Estimation

### 5.1 Framework Baseline (N players)

```
Framework Memory = Simulator + N × Persona

Simulator:
  = config(1KB) + handles(N×100B) + history_hot(L×1KB) + topology(1KB) + comm_buffer(250KB)
  ≈ 260KB + N × 0.1KB

Persona (per actor):
  = player(5KB) + storage_buf(75KB) + monitoring_hot(40KB) + comm(~0KB) + resource(10KB)
  ≈ 130KB

Total Framework:
  ≈ 260KB + N × 130KB

Example (8 players):
  ≈ 260KB + 8 × 130KB = 1.3MB
```

### 5.2 Scaling Behavior

| Rounds  | Framework Memory | Notes                   |
|---------|------------------|-------------------------|
| 100     | ~1.3MB           | Baseline                |
| 1,000   | ~1.3MB           | Hot/cold keeps constant |
| 10,000  | ~1.3MB           | Only disk grows         |
| 100,000 | ~1.3MB           | Framework memory O(1)   |

**Key Insight**: Framework memory is **O(1)** with respect to rounds due to hot/cold architecture.

---

## 6. Conclusion

### ✅ Framework Memory Safety: VERIFIED

After comprehensive code path analysis, the `masim/` framework has **zero unbounded memory risks**.

| Component                       | Initial Assessment | Final Status  | Evidence                                   |
|---------------------------------|--------------------|---------------|--------------------------------------------|
| `PlayerState.custom_state`      | ⚠️ HIGH             | ✅ **NO RISK** | Framework overwrites (O(1)), never appends |
| `ResourceProxy._resource_cache` | Low                | ✅ Safe        | TTL-based expiration                       |
| `HistoryBuffer._pending_cold`   | Low                | ✅ Safe        | Flushed on shutdown                        |

### Key Findings

1. **custom_state framework usage is O(1)**:
   ```python
   # GeneralPlayer.perceive() - OVERWRITES, not appends
   self.state.custom_state["last_observation"] = observation.data  # O(1)
   self.state.custom_state["prev_action"] = prev_result.action     # O(1)
   ```

2. **Only user code can cause unbounded growth** - by extending `GeneralPlayer` and appending to lists without bounds.

3. **Framework memory is O(1)** with respect to rounds due to hot/cold architecture.

### Recommendations

1. **Provide HistoryBuffer** guidance for users storing time-series data
2. **Framework is production-ready** for long-running simulations (100,000+ rounds)

---

## Appendix: File Reference

| File                          | Memory Components                         |
|-------------------------------|-------------------------------------------|
| `masim/utils/history.py`      | `HistoryBuffer`                           |
| `masim/simulator/base.py`     | `BaseSimulator.history`, `ExecutionClock` |
| `masim/proxy/general.py`      | All proxy implementations                 |
| `masim/proxy/base.py`         | Proxy config dataclasses                  |
| `masim/player/base.py`        | `PlayerState`, `BasePlayer`               |
| `masim/persona/general.py`    | `PlayerPersona` proxy composition         |
| `masim/communication/base.py` | `CommunicationChannel.message_store`      |

---

*Analysis of masim/ framework code. Last updated: 2026-03.*
