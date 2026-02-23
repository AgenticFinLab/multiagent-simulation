# Random Value Averaging Demo

## What This Demo Demonstrates

| Feature                   | How It's Shown                                          |
|---------------------------|---------------------------------------------------------|
| Topology-driven messaging | Coordinator → Players → Coordinator routing             |
| Level-based execution     | Level 0 (coordinator) executes before Level 1 (players) |
| Message sending           | `outbound_messages` in `decide()` return value          |
| Message receiving         | `observation.inbounds` in `perceive()`                  |
| State persistence         | `self.state.custom_state` across methods                |
| Multi-round simulation    | 3 rounds with value propagation                         |

## Algorithm

```
Round 1:
┌─────────────┐    value=random(0,1000)    ┌──────────┐
│ Coordinator │ ─────────────────────────► │ Player 1 │
│             │                            └────┬─────┘
│             │                                 │ avg = (value + local) / 2
│             │    value=random(0,1000)    ┌────┴─────┐
│             │ ─────────────────────────► │ Player 2 │
└──────┬──────┘                            └────┬─────┘
       │                                        │
       │ ◄──────────────────────────────────────┘
       │         avg values from players

Round 2+:
┌─────────────┐    value=avg(received)     ┌──────────┐
│ Coordinator │ ─────────────────────────► │ Player 1 │
│             │                            └────┬─────┘
│             │                                 │ avg = (value + local) / 2
│             │    value=avg(received)     ┌────┴─────┐
│             │ ─────────────────────────► │ Player 2 │
└──────┬──────┘                            └────┬─────┘
       │                                        │
       │ ◄──────────────────────────────────────┘
```

## Files

| File                          | Purpose                                                |
|-------------------------------|--------------------------------------------------------|
| `players.py`                  | `SimpleCoordinator` and `SimplePlayer` implementations |
| `run_demo.py`                 | Entry point script                                     |
| `configs/Demo/simulation.yml` | Main configuration                                     |
| `configs/Demo/players.yml`    | Player definitions                                     |
| `configs/Demo/topology.yml`   | Communication graph                                    |

## Implementation Walkthrough

### SimpleCoordinator

```python
class SimpleCoordinator(GeneralPlayer):
```

#### perceive()

**Purpose**: Receive average values from players (Round 2+)

```python
async def perceive(self, observation, prev_result):
    # Get round number
    round_num = observation.round
    self.state.custom_state["round"] = round_num
    
    # Collect values from player responses
    received_values = []
    for inb in observation.inbounds:
        value = inb.payload["average_value"]    # Access payload directly
        received_values.append(value)
    
    self.state.custom_state["received_values"] = received_values
```

**Why**: 
- Must store `round` in state because `decide()` needs it
- Must store `received_values` because `decide()` computes new broadcast value from them

#### decide()

**Purpose**: Generate value and declare broadcast message

```python
async def decide(self):
    round_num = self.state.custom_state["round"]
    received_values = self.state.custom_state["received_values"]
    
    if round_num == 1:
        value = random.randint(0, 1000)      # Initial random
    else:
        value = int(sum(received_values) / len(received_values))  # Average
    
    return {
        "outbound_messages": [
            {"payload": {"value": value, "round": round_num}, "content_type": "value_broadcast"}
        ],
        "broadcast_value": value,
    }
```

**Why**:
- Round 1: No inputs yet, generate random seed value
- Round 2+: Compute average of received player values
- `outbound_messages`: Framework routes to all topology targets (`player_1`, `player_2`)

#### act()

**Purpose**: Create Action for logging

```python
async def act(self, decision_payload):
    return Action(
        action_type="coordinator_broadcast",
        payload=decision_payload,
        source_id=self.identity,
    )
```

**Why**: Action records what happened for observability/debugging

---

### SimplePlayer

```python
class SimplePlayer(GeneralPlayer):
```

#### perceive()

**Purpose**: Receive value from coordinator

```python
async def perceive(self, observation, prev_result):
    round_num = observation.round
    self.state.custom_state["round"] = round_num
    
    for inb in observation.inbounds:
        received_value = inb.payload["value"]       # Extract coordinator's value
        self.state.custom_state["received_value"] = received_value
```

**Why**:
- Topology guarantees inbound is from coordinator
- Store value for `decide()` to use

#### decide()

**Purpose**: Generate local value, compute average, send response

```python
async def decide(self):
    received_value = self.state.custom_state["received_value"]
    
    local_value = random.randint(0, 1000)           # Local observation
    average_value = (received_value + local_value) / 2
    
    response = {
        "received_value": received_value,
        "local_value": local_value,
        "average_value": average_value,
    }
    
    return {
        **response,
        "outbound_messages": [
            {"payload": response, "content_type": "value_response"}
        ],
    }
```

**Why**:
- Generate local random (simulates local observation/sensor)
- Compute average of (received + local)
- `outbound_messages`: Framework routes to topology target (coordinator only)

#### act()

**Purpose**: Create Action for logging

```python
async def act(self, decision_payload):
    return Action(
        action_type="player_response",
        payload=decision_payload,
        source_id=self.identity,
    )
```

## Topology

```yaml
# configs/Demo/topology.yml
sources:
  - coordinator

connections:
  coordinator:    # Coordinator sends to both players
    - player_1
    - player_2
  player_1:       # Player 1 sends only to coordinator
    - coordinator
  player_2:       # Player 2 sends only to coordinator
    - coordinator
```

**Execution Order**:

| Level | Nodes              | What Happens                          |
|-------|--------------------|---------------------------------------|
| 0     | coordinator        | Broadcasts value to players           |
| 1     | player_1, player_2 | Receive value, respond to coordinator |

## Running

```bash
python examples/Demo/run_demo.py -c configs/Demo/simulation.yml
```

## Expected Output

```
[Coordinator] === Round 1 ===
[Coordinator] Generated initial value: 547
[Coordinator] Broadcasting value: 547

[player_1] Round 1
[player_1] Received value from coordinator: 547
[player_1] Generated local value: 823
[player_1] Average of (547 + 823) / 2 = 685.00
[player_1] Sending average 685.00 to coordinator

[player_2] Round 1
[player_2] Received value from coordinator: 547
[player_2] Generated local value: 291
[player_2] Average of (547 + 291) / 2 = 419.00
[player_2] Sending average 419.00 to coordinator

[Coordinator] === Round 2 ===
[Coordinator] Received 2 responses:
  - From player_1: average = 685.00
  - From player_2: average = 419.00
[Coordinator] Computed average of [685.0, 419.0]: 552
[Coordinator] Broadcasting value: 552
...
```

## Key Takeaways

| Concept         | Demo Implementation                                 |
|-----------------|-----------------------------------------------------|
| Send message    | Return `{"outbound_messages": [...]}` in `decide()` |
| Receive message | Read `observation.inbounds` in `perceive()`         |
| Access payload  | `inb.payload["key"]` (auto-unwrapped)               |
| Store state     | `self.state.custom_state["key"] = value`            |
| Routing         | Automatic via topology connections                  |
| Execution order | Automatic via topology levels                       |
