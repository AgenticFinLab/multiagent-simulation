# Dead Code Analysis - masim/ Framework

Comprehensive audit of unused/dead code in the `masim/` framework.

**Scope**: Only `masim/` directory (framework code), excluding examples.
**Status**: Analysis only - no code modifications.

---

## 1. Executive Summary

| Category       | Dead Count | Exported API | Total  |
|----------------|------------|--------------|--------|
| proxy/         | 17         | 5            | 22     |
| player/        | 4          | 0            | 4      |
| persona/       | 1          | 0            | 1      |
| simulator/     | 3          | 0            | 3      |
| communication/ | 1          | 0            | 1      |
| utils/         | 4          | 3            | 7      |
| **TOTAL**      | **30**     | **8**        | **38** |

---

## 2. Proxy Module (`masim/proxy/`)

### 2.1 SendReceiveProxy - ALL Methods Dead (✅ Removed from Persona)

**File**: `masim/proxy/general.py`

| Method          | Line | Called? | Evidence                             |
|-----------------|------|---------|--------------------------------------|
| `send()`        | 74   | ❌ NO    | `grep "\.send\(" → 0 matches`        |
| `broadcast()`   | 90   | ❌ NO    | `grep "\.broadcast\(" → 0 matches`   |
| `receive()`     | 103  | ❌ NO    | `grep "\.receive\(" → 0 matches`     |
| `subscribe()`   | 118  | ❌ NO    | `grep "\.subscribe\(" → 0 matches`   |
| `unsubscribe()` | 127  | ❌ NO    | `grep "\.unsubscribe\(" → 0 matches` |

**Root Cause**: Messages bypass SendReceiveProxy entirely:
```
CommunicationChannel.encode_and_deliver() → receive_message.remote()
```

**Action Taken**: Removed `self.communication: SendReceiveProxy` from PlayerPersona.

---

### 2.2 ResourceProxy - ALL Methods Dead

**File**: `masim/proxy/general.py`

| Method                       | Line | Called? | Evidence                                |
|------------------------------|------|---------|-----------------------------------------|
| `fetch_resource()`           | 261  | ❌ NO    | `grep "\.fetch_resource\(" → 0 matches` |
| `invoke_tool()`              | 286  | ❌ NO    | `grep "\.invoke_tool\(" → 0 matches`    |
| `list_available_resources()` | 304  | ❌ NO    | `grep "\.list_available\(" → 0 matches` |
| `connect()`                  | 315  | ❌ NO    | `grep "\.connect\(" → 0 matches`        |
| `disconnect()`               | 321  | ❌ NO    | `grep "\.disconnect\(" → 0 matches`     |

**Why Exists**: Reserved for future MCP (Model Context Protocol) integration.

---

### 2.3 MonitoringProxy - Retrieval Methods Dead

**File**: `masim/proxy/general.py`

| Method              | Line | Called? | Evidence                                 |
|---------------------|------|---------|------------------------------------------|
| `record_metric()`   | 406  | ✅ YES   | Called in persona/general.py:206         |
| `log_event()`       | 420  | ✅ YES   | Called in persona/general.py:153         |
| `start_timer()`     | 434  | ✅ YES   | Called in persona/general.py:187         |
| `stop_timer()`      | 438  | ✅ YES   | Called in persona/general.py:209         |
| `get_metrics()`     | 447  | ❌ NO    | `grep "\.get_metrics\(" → 0 matches`     |
| `get_events()`      | 456  | ❌ NO    | `grep "\.get_events\(" → 0 matches`      |
| `get_all_metrics()` | 465  | ❌ NO    | `grep "\.get_all_metrics\(" → 0 matches` |
| `get_all_events()`  | 469  | ❌ NO    | `grep "\.get_all_events\(" → 0 matches`  |

**Why Exists**: Retrieval API for external monitoring tools.

---

### 2.4 Factory Functions - Never Called Internally

**File**: `masim/proxy/general.py`

| Function                     | Line | Called? | Evidence        |
|------------------------------|------|---------|-----------------|
| `create_default_proxies()`   | 479  | ❌ NO    | Only in exports |
| `create_minimal_proxies()`   | 491  | ❌ NO    | Only in exports |
| `create_proxies_for_owner()` | 501  | ❌ NO    | Only in exports |

**Status**: Exported as public API in `__all__`.

---

### 2.5 Simplified Wrapper Classes - Never Instantiated

**File**: `masim/proxy/general.py`

| Class                   | Line | Instantiated? | Evidence        |
|-------------------------|------|---------------|-----------------|
| `SimpleStorageProxy`    | 531  | ❌ NO          | Only in exports |
| `SimpleMonitoringProxy` | 543  | ❌ NO          | Only in exports |

**Status**: Exported as public API in `__all__`.

---

## 3. Player Module (`masim/player/`)

### 3.1 GeneralPlayer - Dead Methods

**File**: `masim/player/general.py`

| Method          | Line | Called? | Evidence                                 |
|-----------------|------|---------|------------------------------------------|
| `can_send_to()` | 236  | ❌ NO    | `grep "can_send_to\(" → only definition` |
| `in_group()`    | 286  | ❌ NO    | `grep "in_group\(" → only definition`    |

**Why Exists**: Utility methods for subclass implementations.

---

### 3.2 PlayerState - Dead Methods

**File**: `masim/player/base.py`

| Method               | Line | Called? | Evidence                             |
|----------------------|------|---------|--------------------------------------|
| `step_reset()`       | 451  | ❌ NO    | `grep "\.step_reset\(" → 0 matches`  |
| `update_turn()`      | 484  | ❌ NO    | `grep "\.update_turn\(" → 0 matches` |
| `turn_tick_start()`  | 439  | ✅ YES   | Called in general.py:174             |
| `turn_tick_end()`    | 443  | ✅ YES   | Called in general.py:190             |
| `step_tick_start()`  | 458  | ✅ YES   | Called in general.py:138             |
| `step_tick_end()`    | 462  | ✅ YES   | Called in general.py:145             |
| `update_step()`      | 489  | ✅ YES   | Called in general.py:144             |
| `get_turn_metrics()` | 494  | ✅ YES   | Called in persona/general.py:240     |
| `get_step_metrics()` | 471  | ✅ YES   | Called in persona/general.py:241     |

---

### 3.3 PlayerConfig - Dead Property

**File**: `masim/player/base.py`

| Property           | Line | Called? | Evidence                                |
|--------------------|------|---------|-----------------------------------------|
| `is_coordinator()` | 375  | ❌ NO    | `grep "\.is_coordinator\(" → 0 matches` |

---

## 4. Persona Module (`masim/persona/`)

### 4.1 PlayerPersona - Dead Methods

**File**: `masim/persona/general.py`

| Method                 | Line | Called? | Evidence                                    |
|------------------------|------|---------|---------------------------------------------|
| `get_state_snapshot()` | 225  | ❌ NO    | `grep "\.get_state_snapshot\(" → 0 matches` |

**Why Exists**: Debugging/monitoring API.

---

## 5. Simulator Module (`masim/simulator/`)

### 5.1 GeneralSimulator - Dead Methods

**File**: `masim/simulator/general.py`

| Method                | Line | Called? | Evidence                                   |
|-----------------------|------|---------|--------------------------------------------|
| `get_round_history()` | 538  | ❌ NO    | `grep "\.get_round_history\(" → 0 matches` |
| `get_status()`        | 545  | ❌ NO    | `grep "\.get_status\(" → 0 matches`        |
| `get_player_handle()` | 559  | ❌ NO    | `grep "\.get_player_handle\(" → 0 matches` |

**Why Exists**: External monitoring/debugging API.

---

## 6. Communication Module (`masim/communication/`)

### 6.1 Message - Dead Methods

**File**: `masim/communication/base.py`

| Method           | Line | Called? | Evidence                              |
|------------------|------|---------|---------------------------------------|
| `is_broadcast()` | 158  | ❌ NO    | `grep "\.is_broadcast\(" → 0 matches` |

---

## 7. Utils Module (`masim/utils/`)

### 7.1 HistoryBuffer - Dead Methods

**File**: `masim/utils/history.py`

| Method         | Line | Called? | Evidence                         |
|----------------|------|---------|----------------------------------|
| `to_list()`    | 285  | ❌ NO    | `grep "\.to_list\(" → 0 matches` |
| `recent()`     | 290  | ❌ NO    | `grep "\.recent\(" → 0 matches`  |
| `get_recent()` | 241  | ✅ YES   | Used internally                  |
| `get_all()`    | 256  | ✅ YES   | Used in proxy/general.py         |

---

### 7.2 TopologyGraph - Dead Methods

**File**: `masim/utils/topology.py`

| Method       | Line | Called? | Evidence                          |
|--------------|------|---------|-----------------------------------|
| `to_ascii()` | 382  | ❌ NO    | `grep "\.to_ascii\(" → 0 matches` |

---

### 7.3 Factory Function - Never Called Internally

**File**: `masim/utils/history.py`

| Function                  | Line | Called? | Evidence        |
|---------------------------|------|---------|-----------------|
| `create_history_buffer()` | 307  | ❌ NO    | Only in exports |

**Status**: Exported as public API.

---

### 7.4 ConnectionValidator - Never Instantiated Externally

**File**: `masim/utils/config.py`

| Class                 | Line | Used? | Evidence                          |
|-----------------------|------|-------|-----------------------------------|
| `ConnectionValidator` | 280  | ❌ NO  | Only in its own docstring example |

**Dead Methods within ConnectionValidator**:
| Method            | Line | Called? |
|-------------------|------|---------|
| `can_send()`      | 305  | ❌ NO    |
| `can_broadcast()` | 320  | ❌ NO    |
| `get_targets()`   | 332  | ❌ NO    |
| `validate_send()` | 346  | ❌ NO    |

---

## 8. Categorization Summary

### 8.1 Definitely Dead (Remove Candidates)

| Location                | Item                            | Reason                   |
|-------------------------|---------------------------------|--------------------------|
| `proxy/general.py`      | `SendReceiveProxy` methods      | Messages bypass entirely |
| `player/general.py`     | `can_send_to()`                 | Never called             |
| `player/general.py`     | `in_group()`                    | Never called             |
| `player/base.py`        | `PlayerState.step_reset()`      | Never called             |
| `player/base.py`        | `PlayerState.update_turn()`     | Never called             |
| `player/base.py`        | `PlayerConfig.is_coordinator()` | Never called             |
| `communication/base.py` | `Message.is_broadcast()`        | Never called             |
| `utils/history.py`      | `HistoryBuffer.to_list()`       | Never called             |
| `utils/history.py`      | `HistoryBuffer.recent()`        | Never called             |
| `utils/topology.py`     | `TopologyGraph.to_ascii()`      | Never called             |
| `utils/config.py`       | `ConnectionValidator` class     | Never instantiated       |

### 8.2 Reserved for Future (Keep)

| Location           | Item                    | Purpose         |
|--------------------|-------------------------|-----------------|
| `proxy/general.py` | `ResourceProxy` methods | MCP integration |

### 8.3 Public API (Keep - Exported)

| Location           | Item                      | Export    |
|--------------------|---------------------------|-----------|
| `proxy/general.py` | Factory functions         | `__all__` |
| `proxy/general.py` | `SimpleStorageProxy`      | `__all__` |
| `proxy/general.py` | `SimpleMonitoringProxy`   | `__all__` |
| `utils/history.py` | `create_history_buffer()` | `__all__` |

### 8.4 Monitoring/Debug API (Keep)

| Location               | Item                                  | Purpose    |
|------------------------|---------------------------------------|------------|
| `proxy/general.py`     | `get_metrics()`, `get_events()`       | Monitoring |
| `persona/general.py`   | `get_state_snapshot()`                | Debugging  |
| `simulator/general.py` | `get_status()`, `get_round_history()` | Debugging  |

---

## 9. Verification Commands

```bash
# Find all method definitions
grep -rn "def [a-z_]*(" masim/ --include="*.py"

# Check usage of specific method
grep -rn "\.method_name\(" masim/

# Find classes never instantiated
grep -rn "ClassName\(" masim/

# Full dead code audit
python -m pylint --disable=all --enable=W0611,W0612,W0613 masim/
```

---

## 10. Statistics

- **Total Functions/Methods Analyzed**: ~150
- **Definitely Dead**: 11
- **Reserved for Future**: 5
- **Exported Public API**: 8
- **Monitoring/Debug API**: 6
- **Dead Code Percentage**: ~7%

---

*Analysis of masim/ framework code only. Last updated: 2026-03.*
*Status: DOCUMENTATION ONLY - No code modifications made.*
