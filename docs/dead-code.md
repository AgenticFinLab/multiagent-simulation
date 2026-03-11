# Dead Code Analysis - masim/ Framework

Analysis of unused/dead code in the `masim/` framework directory.

---

## 1. Summary

| Category                 | Count | Status                        |
|--------------------------|-------|-------------------------------|
| SendReceiveProxy methods | 5     | ✅ Removed from Persona        |
| Factory functions        | 3     | ⚠️ Exported, unused internally |
| Simplified wrappers      | 2     | ⚠️ Exported, unused internally |
| ResourceProxy methods    | 5     | ⚠️ Exported, unused internally |

---

## 2. SendReceiveProxy (✅ REMOVED from Persona)

**Location**: `masim/proxy/general.py`

### Dead Methods

| Method          | Lines   | Status         |
|-----------------|---------|----------------|
| `send()`        | 74-88   | ❌ Never called |
| `broadcast()`   | 90-101  | ❌ Never called |
| `receive()`     | 103-116 | ❌ Never called |
| `subscribe()`   | 118-125 | ❌ Never called |
| `unsubscribe()` | 127-130 | ❌ Never called |

### Why Dead

Messages flow through `CommunicationChannel` directly, bypassing `SendReceiveProxy`:

```
Simulator.phase_dispatch()
    → CommunicationChannel.encode_and_deliver()
        → target_handle.receive_message.remote()  # Direct Ray call
            → PlayerPersona.receive_message()
                → player.on_inbound()
```

### Action Taken

Removed `self.communication: SendReceiveProxy` from `PlayerPersona`:
- `masim/persona/base.py` - removed type annotation
- `masim/persona/general.py` - removed instantiation

The `SendReceiveProxy` class is kept in `masim/proxy/general.py` as exported public API.

---

## 3. Factory Functions (⚠️ Exported but Unused)

**Location**: `masim/proxy/general.py`

| Function                     | Lines   | Status                    |
|------------------------------|---------|---------------------------|
| `create_default_proxies()`   | 479-488 | ⚠️ Never called internally |
| `create_minimal_proxies()`   | 491-498 | ⚠️ Never called internally |
| `create_proxies_for_owner()` | 501-523 | ⚠️ Never called internally |

### Evidence

```bash
grep -r "create_default_proxies\|create_minimal_proxies\|create_proxies_for_owner" masim/
# Only found in: exports, __all__, __init__.py
```

### Recommendation

- **Keep**: If intended as public API for users
- **Remove**: If not intended for external use

---

## 4. Simplified Wrapper Classes (⚠️ Exported but Unused)

**Location**: `masim/proxy/general.py`

| Class                   | Lines   | Status               |
|-------------------------|---------|----------------------|
| `SimpleStorageProxy`    | 531-540 | ⚠️ Never instantiated |
| `SimpleMonitoringProxy` | 543-555 | ⚠️ Never instantiated |

### Evidence

```bash
grep -r "SimpleStorageProxy\|SimpleMonitoringProxy" masim/
# Only found in: exports, __all__, __init__.py
```

### Recommendation

- **Keep**: If intended as convenience classes for users
- **Remove**: If not intended for external use

---

## 5. ResourceProxy Methods (⚠️ Unused Internally)

**Location**: `masim/proxy/general.py`

| Method                       | Lines   | Status         |
|------------------------------|---------|----------------|
| `fetch_resource()`           | 261-284 | ⚠️ Never called |
| `invoke_tool()`              | 286-302 | ⚠️ Never called |
| `list_available_resources()` | 304-313 | ⚠️ Never called |
| `connect()`                  | 315-319 | ⚠️ Never called |
| `disconnect()`               | 321-326 | ⚠️ Never called |

### Why Unused

`ResourceProxy` is designed for future MCP (Model Context Protocol) integration. The class is instantiated in `PlayerPersona`, but its methods are never invoked.

### Recommendation

- **Keep**: Designed for future MCP integration
- **Document**: Mark as "reserved for future use"

---

## 6. Verification Commands

```bash
# Check for SendReceiveProxy usage
grep -r "\.send\(\|\.broadcast\(\|\.receive\(" masim/

# Check for factory function calls
grep -r "create_default_proxies\|create_minimal_proxies" masim/

# Check for ResourceProxy method calls
grep -r "\.fetch_resource\|\.invoke_tool\|\.list_available" masim/
```

---

*Analysis of masim/ framework code. Last updated: 2026-03.*
