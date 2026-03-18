# Configuration Reference: simulation.yml, players.yml, persona.yml, topology.yml

This document describes every configuration field across all four YAML files that
define a simulation scenario. Fields are explained in terms of their meaning,
effect on framework behavior, and relationships to other fields and source code.

---

## File Overview and Relationships

```
configs/[SCENARIO]/
    simulation.yml     ← top-level orchestration config (Ray, rounds, paths)
        !include players.yml   ← per-player identity, class, extras, persona
            !include persona.yml   ← proxy subsystem settings (storage, monitoring, comm)
        !include topology.yml  ← communication graph (who talks to whom, execution order)
```

All four files are loaded together by `masim/utils/config.py:load_config()` and
assembled into a single `SimulationConfig` dataclass
(`masim/simulator/base.py:SimulationConfig`). The simulator then uses this config
to initialize Ray actors and run rounds.

**Path consistency rule**: `setting.record_path` (simulation.yml),
`extras.record_path` (players.yml), and `proxy.storage.record_path` (persona.yml)
must all point to the same root directory. They are set independently because
different subsystems write to sub-paths within that root.

---

## simulation.yml

### `setting` section

| Field                   | Type   | Description                                                                                                                                                                                                                                                                                                                                           |
|-------------------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                  | string | Unique identifier for this run. Used as the prefix for Ray actor names (format: `name::player_id`). Also appears in log messages.                                                                                                                                                                                                                     |
| `description`           | string | Human-readable description. Not read by the framework; for documentation only.                                                                                                                                                                                                                                                                        |
| `total_rounds`          | int    | Total number of rounds to execute. `GeneralSimulator.run()` loops `range(1, total_rounds+1)`. The simulation stops exactly at this count — there is no early-stop mechanism.                                                                                                                                                                          |
| `round_history_limit`   | int    | Maximum number of round results kept in hot RAM. Implemented as a `HistoryBuffer` deque with this size (`masim/utils/history.py`). **Critical**: `simulator.run()` returns `self.history.recent` which contains only these last N entries — NOT all rounds. Older entries are spilled to disk under `record_path/history/`. Rule of thumb: keep at 3. |
| `record_path`           | string | Root output directory for all simulation artifacts: `history/`, `diagrams/`, and any player record files. Must be consistent with `extras.record_path` in players.yml and `proxy.storage.record_path` in persona.yml.                                                                                                                                 |
| `save_diagram_interval` | int    | Save a topology diagram image every N rounds to `record_path/diagrams/`. Set 0 to disable. Higher frequency increases disk I/O. Diagrams show message flow overlaid on the topology graph.                                                                                                                                                            |

### `environment` section

| Field         | Type   | Description                                                                                                                                                                 |
|---------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `dotenv_path` | string | Path to `.env` file loaded via `python-dotenv` at startup. Required for LLM simulations (must contain `ARK_API_KEY`). Rule-based simulations can ignore this.               |
| `workspace`   | string | Working directory for all relative paths in this config. `"."` means the project root — the directory you run `python` from. All other paths are resolved relative to this. |

### `ray` section

The `ray` section configures the Ray distributed computing cluster. All values
are passed to `ray.init()` in `masim/simulator/general.py:ensure_ray()`.

#### Core cluster settings

| Field          | Type           | Description                                                                                                                                                                        |
|----------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `address`      | string \| null | Ray cluster address to connect to. `null` = start a new local cluster. Set to `"auto"` or `"ray://host:port"` to connect to an existing remote cluster.                            |
| `namespace`    | string         | Ray namespace for actor isolation. Actors in different namespaces cannot see each other. Use a unique value per experiment to avoid actor name collisions between concurrent runs. |
| `actor_prefix` | string \| null | Reserved prefix for actor name construction. `null` = use `setting.name` as prefix. Actor names are formed as `{prefix}::{player_id}`.                                             |

#### Resource allocation

| Field                 | Type        | Description                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|-----------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `num_cpus`            | int         | Number of logical CPUs reserved for this Ray cluster. **Must be set explicitly** — do not use null. Derivation: `N_investors_in_largest_level + 1` (all investors run in parallel at topology level 1; +1 for OS/driver process). Source: `_resolve_num_cpus()` in `masim/simulator/general.py`.                                                                                                                                               |
| `num_gpus`            | int \| null | Number of GPUs to reserve. `null` = 0. Rule-based simulations never use GPUs. LLM simulations use remote API inference — also set to `null`.                                                                                                                                                                                                                                                                                                   |
| `object_store_memory` | int         | Size in bytes of the Ray Plasma shared-memory object store. **Must be set explicitly** — do not use null. This is the memory pool for all objects crossing actor boundaries via `ray.get()`. Derivation: `(N_players*2 + N_msgs) * 64KB * 10`, minimum 128 MB for rule-based, 512 MB for LLM. See the RESOURCE SIZING PROTOCOL in the TEMPLATE for the full formula. Source: `_resolve_object_store_memory()` in `masim/simulator/general.py`. |

**What goes into the object store**: Only objects returned from Ray remote calls
cross the store boundary. Per round: `N_players` TurnResult objects (phase 2),
`N_players` pending_info lists (phase 3 collect), `N_messages` Message objects
(phase 3 dispatch). Ray's minimum allocation is 64 KB per object regardless of
actual payload size. All references are freed after `ray.get()` completes within
the same phase, so peak in-flight = one phase at a time.

**What does NOT go into the object store**: Actor-internal state — `custom_state`
HistoryBuffers, hot deques, player fields — lives entirely in each actor's heap.

#### Logging and observability

| Field               | Type   | Description                                                                                                                                                                                                                                                                            |
|---------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `include_dashboard` | bool   | Start the Ray web dashboard (http://localhost:8265). Set `false` to skip dashboard startup and save resources.                                                                                                                                                                         |
| `logging_level`     | string | Ray's internal log level: `"debug"`, `"info"`, `"warning"`, `"error"`. Controls log volume from Ray's own internals (scheduler, object store, etc.). Application logs (from players.py) are controlled by Python's `logging` module separately.                                        |
| `log_to_driver`     | bool   | Forward all actor stdout/stderr to the driver process. Set `false` to suppress actor output (reduces log noise and buffer pressure). The previous session identified accumulated print() output in actors as a memory pressure source. Keep `false` unless debugging a specific actor. |

#### `actor_options` sub-section

Applied per `PlayerPersona` actor at launch time via `RemotePersona.options()`.

| Field              | Type | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|--------------------|------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `max_restarts`     | int  | How many times Ray automatically restarts a crashed actor before giving up. Covers out-of-memory kills, segfaults, and node failures. `3` = tolerate 3 crashes. Set `0` to disable auto-restart. After exhausting restarts, the exception propagates to the simulator.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `max_task_retries` | int  | How many times Ray automatically retries a failed *remote task call* (e.g., a timeout on a single `operate.remote()` call). Does NOT apply to actor crashes (covered by `max_restarts`). `1` = retry once on transient failure.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `max_concurrency`  | int  | Max number of tasks that can be queued + executing inside one actor simultaneously. Each `PlayerPersona` actor is single-threaded (asyncio event loop). Ray queues excess task calls. **Rule-based**: set `4` — one active `operate()` + up to 3 queued admin calls (`initialize`, `set_topology`, `set_peer_handles`). CPU-bound logic does not benefit from higher concurrency inside one thread. **LLM**: set `10` — LLM API calls `await` HTTP responses (I/O-bound), so while one `operate()` is waiting for the API, other queued admin calls can be processed, reducing head-of-line blocking. **Implementation note**: this field is currently reserved in config but not yet wired into `RemotePlayerPersona.options()` at `masim/simulator/general.py` line 298. |

#### `runtime_env` sub-section

| Field         | Type           | Description                                                                                                                                                                                                      |
|---------------|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `working_dir` | string \| null | Override working directory for actor subprocesses. `null` = inherit the workspace from `environment.workspace`. Useful for remote Ray clusters with different filesystem layouts.                                |
| `pip`         | list           | Extra Python packages to install in the actor runtime environment. Used when running actors on a remote cluster that lacks some local dependencies.                                                              |
| `env_vars`    | dict           | Environment variables injected into each actor process. Example: `{MY_VAR: "value"}` makes `os.environ["MY_VAR"]` available inside actor code. For API keys, prefer `.env` + `dotenv_path` over hardcoding here. |

#### `serialization` sub-section

| Field                         | Type | Description                                                                                                                                                                                                                     |
|-------------------------------|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `use_arrow`                   | bool | Use Apache Arrow IPC format for Ray object serialization instead of pickle. Arrow is significantly faster for numeric arrays and simple dicts. Keep `true`.                                                                     |
| `register_custom_serializers` | bool | Register custom pickle serializers for framework domain objects (`TurnResult`, `Message`, `Info`, etc.) via `masim/utils/serialization.py`. Keep `true` to ensure correct round-trip serialization across Ray actor boundaries. |

### `players` and `topology` sections

```yaml
players: !include players.yml
topology: !include topology.yml
```

These are YAML includes — not inline values. See the players.yml and topology.yml
sections below.

### `communication` section

| Field          | Type   | Description                                                                                                                                                                                   |
|----------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `storage_path` | string | Directory where the `GeneralCommunicationChannel` logs all inter-player messages. Each dispatched message is serialized to a JSON file here. Used for post-simulation communication analysis. |

---

## players.yml

Defines all players in the simulation. Each top-level key is a `player_id` (e.g.,
`market`, `investor_1`). The framework reads this file and instantiates one
`PlayerPersona` Ray actor per entry.

### Per-player structure

```yaml
player_id:
  name: "Display Name"        # human-readable label
  class: "module.path:Class"  # Python class to instantiate as the player
  config:
    identity: "player_id"     # must match the top-level key
    role: coordinator | player
    steps_per_turn: 1
    group_tags: [tag1, tag2]
    extras:
      record_path: ...
      custom_state_hot_limit: 3
      # domain-specific parameters
  persona: !include persona.yml
```

| Field                                  | Type   | Description                                                                                                                                                                                                                                                                                                                                                           |
|----------------------------------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `name`                                 | string | Human-readable display name. Used in logs and diagrams.                                                                                                                                                                                                                                                                                                               |
| `class`                                | string | Python import path to the player class in format `"module.path:ClassName"`. The framework calls `load_class(path)` (`masim/simulator/general.py:load_class`) to dynamically import and instantiate the class.                                                                                                                                                         |
| `config.identity`                      | string | The player's own ID string. Must exactly match the top-level key (e.g., `market` entry must have `identity: "market"`). Used for self-identification in messages and logs.                                                                                                                                                                                            |
| `config.role`                          | string | `"coordinator"` = Level 0 (executes first each round, before all investors). `"player"` = Level 1+ (executes after coordinators, in parallel with other level-1 players). Execution level is also determined by topology distance from `sources`.                                                                                                                     |
| `config.steps_per_turn`                | int    | Number of internal decision steps the player performs per `operate()` call. `1` = single perceive→decide→act cycle per round. Reserved for multi-step agent architectures.                                                                                                                                                                                            |
| `config.group_tags`                    | list   | Membership tags for group-based operations (e.g., `["investors"]`). Used by the simulator to address messages to a group. The market coordinator typically has `["market"]`.                                                                                                                                                                                          |
| `config.extras`                        | dict   | All domain-specific parameters for this player's logic. **No hardcoded defaults allowed** — players.py must read every parameter directly from `extras` and fail fast if missing. Never use `.get()` with default values.                                                                                                                                             |
| `config.extras.record_path`            | string | Output directory for this player's per-turn records. Must match `setting.record_path` in simulation.yml. Used by the StorageProxy to write TurnResult JSON files.                                                                                                                                                                                                     |
| `config.extras.custom_state_hot_limit` | int    | Max entries kept in hot RAM for each `HistoryBuffer` stored in `custom_state` (e.g., `price_history`, `return_history`). Scope: `custom_state`-level HistoryBuffer hot deque. Entries exceeding this limit are flushed to disk automatically. Separate from `round_history_limit` (round-level) and `monitor_hot_limit` (monitoring-level). Set 3 for RAM efficiency. |
| `persona`                              | dict   | Persona configuration loaded from `!include persona.yml`. Configures the proxy subsystems for this player (storage, monitoring, communication, resources). All players in the scenario share the same persona.yml.                                                                                                                                                    |

---

## persona.yml

Shared across all players in a scenario (every player entry includes this file).
Configures the four proxy subsystems inside each `PlayerPersona` actor.

### Top-level fields

| Field             | Type | Description                                                                                                                                                                                             |
|-------------------|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `auto_checkpoint` | bool | Auto-save full actor state after each round to `proxy.storage.checkpoint_dir`. Enables resuming interrupted runs. Keep `false` in normal runs — checkpoint serialization adds I/O overhead every round. |
| `debug_mode`      | bool | Enable verbose per-turn logging inside each actor. Writes to Ray actor stdout (forwarded to driver if `log_to_driver: true`). Keep `true` during development; set `false` in long production runs.      |

### `proxy.storage` sub-section

| Field             | Type   | Description                                                                                                                                                                                                                                                   |
|-------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `checkpoint_dir`  | string | Directory for full actor state snapshots (when `auto_checkpoint: true`).                                                                                                                                                                                      |
| `record_path`     | string | Root path for per-turn JSON record files. Must match `setting.record_path` (simulation.yml) and `extras.record_path` (players.yml). The StorageProxy writes individual turn files under `record_path/turns/` and message files under `record_path/messages/`. |
| `record_rounds`   | bool   | Write each player's `TurnResult` to disk after every round. Produces `N_players` JSON files per round. Set `false` to disable disk writes entirely (useful for memory/I/O profiling). Disabling means analysis scripts cannot access per-round detail.        |
| `turn_block_size` | int    | Number of consecutive turns grouped into one block file on disk. Controls write granularity: `3` = flush to disk every 3 turns. Only the current unflushed block is in hot RAM; completed blocks remain on disk and are loaded on-demand.                     |

### `proxy.monitoring` sub-section

| Field               | Type   | Description                                                                                                                                                                                                                                               |
|---------------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `record_path`       | string | Directory for monitoring output files (metrics, events, performance counters per turn).                                                                                                                                                                   |
| `monitor_hot_limit` | int    | Max monitoring entries kept in hot RAM in the monitoring HistoryBuffer. Scope: monitoring proxy hot deque only — separate from `round_history_limit` (simulator-level) and `custom_state_hot_limit` (player-level). Entries exceeding this spill to disk. |

### `proxy.communication` sub-section

| Field                | Type | Description                                                                                                                                                                         |
|----------------------|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `message_timeout_ms` | int  | Max milliseconds to wait for a message send/receive operation to complete. Rule-based: `5000` ms (local Ray calls are fast). LLM: `10000` ms (LLM API inference takes 2–8 seconds). |
| `enable_compression` | bool | Compress message payloads before storing in Ray object store. Reduces object store memory usage at the cost of CPU time for compress/decompress.                                    |

### `proxy.resource` sub-section

| Field            | Type | Description                                                                                                                                                                                                                                     |
|------------------|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `mcp_servers`    | list | List of MCP (Model Context Protocol) server configurations, each as `{name, endpoint, capabilities}`. Used for tool-calling players that need web search, code execution, or other external capabilities. Leave `[]` for all current scenarios. |
| `enable_caching` | bool | Cache responses from external resource calls (MCP servers, APIs). Avoids redundant requests when multiple players query the same source per round.                                                                                              |

---

## topology.yml

Defines the communication graph between players and the execution level ordering.

| Field         | Type   | Description                                                                                                                                                                                                                                                                                                                                   |
|---------------|--------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `type`        | string | Graph pattern: `"star"` (hub-and-spoke), `"mesh"` (fully connected), `"ring"` (sequential chain). All current scenarios use `"star"` with market as hub.                                                                                                                                                                                      |
| `sources`     | list   | Player IDs that execute at Level 0 (first). Typically the market coordinator. The `TopologyGraph` (`masim/utils/topology.py`) performs BFS from sources to assign execution levels.                                                                                                                                                           |
| `connections` | dict   | Adjacency list: `sender_id → [target_id, ...]`. Defines which players send messages to which others each round. In star topology: `market → [all investors]` (price broadcast) and `each investor → [market]` (order submission). The topology also determines execution levels: players reachable from sources in N hops execute at Level N. |

### Execution level derivation from topology

The `TopologyGraph` computes execution levels via BFS from `sources`:
- Level 0: all nodes in `sources`
- Level 1: all nodes reachable from Level 0 via `connections`
- Level N: all nodes reachable from Level N-1

Within a level, all players execute in parallel (`phase_execute` in
`masim/simulator/general.py`). Between levels, execution is sequential —
Level N fully completes (execute + collect + dispatch) before Level N+1 starts.
This guarantees that messages sent at Level N arrive before Level N+1 actors run.

---

## Hot RAM budget: three separate limits

The framework has three independent HistoryBuffer hot-deque limits. They are
separate fields controlling different subsystems:

| Field                    | Location                         | Scope                                            | What it limits                                                                                                                               |
|--------------------------|----------------------------------|--------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `round_history_limit`    | simulation.yml → `setting`       | Simulator-level                                  | Round results returned by `simulator.run()`. Older entries spill to `record_path/history/`.                                                  |
| `custom_state_hot_limit` | players.yml → `extras`           | Player-level (per HistoryBuffer in custom_state) | Entries in each named HistoryBuffer inside a player's `custom_state` (e.g., `price_history`, `return_history`). Older entries spill to disk. |
| `monitor_hot_limit`      | persona.yml → `proxy.monitoring` | Monitoring proxy                                 | Monitoring metrics/events kept in RAM before spilling.                                                                                       |

These three numbers are independent. Changing one does not affect the others.
