# Simulation Save Structure

This file documents how a simulation run saves data to disk: how paths are determined from the config file, what directory and file structure is written, what format each file uses, and how to read it back in `analysis.py`.

---

## 1. Config File → Save Paths

All save paths are defined in `simulation.yml` under the `setting` and `communication` sections:

```yaml
# configs/{Scenario}/{Variant}/simulation.yml

setting:
  record_path: "EXPERIMENT/{Scenario}/{Variant}/records"   # ← root for all player records

communication:
  storage_path: "EXPERIMENT/{Scenario}/{Variant}/communication"  # ← message logs
  record_messages: true
  message_block_size: 500
```

Paths are relative to the project root (the working directory when you run the simulation).

In `analysis.py`, these paths are accessed as:

```python
config = load_config(args.config)                       # load the -c YAML file
record_path = config["setting"]["record_path"]          # e.g. "EXPERIMENT/AnchoringEffect/Rule/records"
base_dir    = os.path.dirname(record_path)              # e.g. "EXPERIMENT/AnchoringEffect/Rule"
output_dir  = os.path.join(base_dir, "analysis")        # e.g. "EXPERIMENT/AnchoringEffect/Rule/analysis"
```

---

## 2. EXPERIMENT Directory Structure

After a simulation run completes, the framework writes the following structure under `record_path`:

```
EXPERIMENT/{Scenario}/{Variant}/
├── records/                              ← config: setting.record_path
│   │
│   ├── {coordinator_id}/                 ← e.g. "market"  (role: coordinator)
│   │   ├── {store_name}/                 ← one subdirectory per registered batch store
│   │   │   ├── batch_block_0.json        ← time-series data (see §3)
│   │   │   └── batch-store-information.json   ← internal index, not data
│   │   ├── turns/                        ← market's own per-round turn records
│   │   │   ├── turn_block_0.json         ← (see §4)
│   │   │   ├── turn_block_1.json
│   │   │   └── turn-store-information.json    ← internal index, not data
│   │   └── messages/
│   │       ├── batch_block_0.json
│   │       └── batch-store-information.json
│   │
│   ├── {investor_id_1}/                  ← e.g. "anchored_trader_1"  (role: player)
│   │   ├── turns/                        ← investor's per-round decision records
│   │   │   ├── turn_block_0.json
│   │   │   └── turn-store-information.json
│   │   └── messages/
│   │       ├── batch_block_0.json
│   │       └── batch-store-information.json
│   │
│   ├── {investor_id_2}/
│   └── ...
│
└── communication/                        ← config: communication.storage_path
    └── ...                               ← raw message logs (one file per block)
```

**`{coordinator_id}`**: the `player_id` of the Market class, set in `players.yml` (commonly `"market"`).

**`{store_name}`**: the name passed to the batch store registration in `Market.act()`. Common names:

| Store name      | Type    | What it holds                     |
|-----------------|---------|-----------------------------------|
| `price`         | `float` | Market price each round           |
| `fundamental`   | `float` | Fundamental value each round      |
| `volume`        | `int`   | Total traded volume each round    |
| `bubble_metric` | `float` | Scenario-specific (AssetBubble)   |
| `stock`         | `float` | Scenario-specific (EquityPremium) |

The exact store names are determined by the scenario's `Market` class implementation. To discover them for any completed run:
```python
results = load_results(config)
for pid, p in results.players_by_role("coordinator").items():
    print(pid, "stores:", p.batch_store_names)
```

---

## 3. Batch Store File Format (`batch_block_*.json`)

Used for all numeric time-series (coordinator and investor alike).

### File content

```json
{
  "batch_00000000_00000049": [100.02, 100.03, 100.07, 100.11, ...],
  "batch_00000050_00000099": [100.15, 100.18, 100.22, ...],
  ...
}
```

| Element       | Format                        | Meaning                              |
|---------------|-------------------------------|--------------------------------------|
| Top-level key | `batch_{start:08d}_{end:08d}` | 0-based round-index range, inclusive |
| Value         | `list[float]` or `list[int]`  | One element per round, in order      |

A single `batch_block_0.json` often contains all batches for short simulations (≤ a few hundred rounds). For long simulations multiple `batch_block_N.json` files are written.

`batch-store-information.json` is a metadata index used internally — do not parse it for data.

### Round numbering

Batch lists are **0-based**: element at index 0 corresponds to round 1. Convert with:

```python
def _batch_to_rounds(values: list) -> dict:
    """Convert batch store list → {round_num: value}, round_num is 1-based."""
    return {i + 1: v for i, v in enumerate(values)}
```

### Common mistake

```python
# WRONG — causes KeyError: 'price'
with open(filepath) as f:
    record = json.load(f)
prices.append(record["price"])   # record is {"batch_00000000_...": [...]} not {"price": ...}
```

---

## 4. Turn Record File Format (`turn_block_*.json`)

Used by every player (coordinator and investors) to store per-round decision records.

### File content

```json
{
  "turn_r000001_0423132834": {
    "round_num": 1,
    "timestamp": "2026-04-23T13:28:34.865945",
    "turn_result": {
      "step_results": [
        {
          "decision_payload": {
            "bid_price": 100.02,
            "quantity": 0.0,
            "strategy": "anchored_trader",
            "investor": "anchored_trader_1",
            "reasoning": "Anchor=100.0, Perceived=100.0, Dev=+0.000"
          },
          "action": { "action_type": "investor_bid", ... }
        }
      ],
      "final_action": { ... },
      "tick_turn_count": 1
    }
  },
  "turn_r000002_0423132834": { ... }
}
```

| Element            | Format                                 | Meaning                                                                   |
|--------------------|----------------------------------------|---------------------------------------------------------------------------|
| Top-level key      | `turn_r{round:06d}_{timestamp_suffix}` | Round number + wall-clock suffix                                          |
| `round_num`        | `int`                                  | 1-based round number                                                      |
| `decision_payload` | `dict`                                 | Fields returned by the agent's `_make_decision()` — **scenario-specific** |

`turn-store-information.json` is a metadata index — do not parse it for data.

### Standard `decision_payload` fields (present in most scenarios)

| Field       | Type    | Description                                            |
|-------------|---------|--------------------------------------------------------|
| `bid_price` | `float` | Order price submitted by this agent                    |
| `quantity`  | `float` | Order size (positive = buy, negative = sell, 0 = hold) |
| `strategy`  | `str`   | Agent strategy name string                             |
| `investor`  | `str`   | Agent player_id                                        |
| `reasoning` | `str`   | Free-text reasoning string                             |

Additional fields depend on what each scenario's `_make_decision()` returns. To inspect:
```python
player = list(results.players_by_role("player").values())[0]
print(player.turns.payload(1).keys())   # fields in round 1
```

---

## 5. Reading Saved Data: `load_results` API

Never parse batch/turn JSON files manually. Use `masim.utils.load_results()`.

```python
from masim.utils import load_config, load_results

config  = load_config(args.config)   # reads the -c YAML
results = load_results(config)       # lazy — scans directories, reads nothing yet
```

### API reference

**`SimulationResults`**

| Method / Property                        | Returns                    | Use                      |
|------------------------------------------|----------------------------|--------------------------|
| `results.players`                        | `Dict[str, PlayerResults]` | All players by player_id |
| `results.player(pid)`                    | `PlayerResults`            | One player               |
| `results.players_by_role("coordinator")` | `Dict[str, PlayerResults]` | Market/coordinator only  |
| `results.players_by_role("player")`      | `Dict[str, PlayerResults]` | Investor players only    |

**`PlayerResults`**

| Method / Property          | Returns        | Use                             |
|----------------------------|----------------|---------------------------------|
| `player.batch_store_names` | `List[str]`    | Names of available batch stores |
| `player.batch(name)`       | `BatchStore`   | Accessor for one batch store    |
| `player.turns`             | `TurnStore`    | Accessor for turn records       |
| `player.messages`          | `MessageStore` | Accessor for message records    |

**`BatchStore`**

| Method                    | Returns       | Use                                |
|---------------------------|---------------|------------------------------------|
| `batch.all()`             | `List[float]` | All values, index 0 = round 1      |
| `batch.range(start, end)` | `List[float]` | Slice by 0-based index             |
| `batch.exists`            | `bool`        | Whether the store directory exists |

**`TurnStore`**

| Method                     | Returns           | Use                                   |
|----------------------------|-------------------|---------------------------------------|
| `turns.all()`              | `Dict[int, dict]` | All turns: `{round_num: full_record}` |
| `turns.payload(round_num)` | `dict`            | `decision_payload` for one round      |
| `turns.payloads()`         | `Dict[int, dict]` | All `{round_num: decision_payload}`   |
| `turns.field(name)`        | `Dict[int, Any]`  | One field across all rounds           |

---

## 6. Canonical `_load_data` Pattern for `analysis.py`

Copy this pattern into every `Rule/analysis.py`. Adapt `{store_name}` to the actual batch store names your scenario uses.

```python
from masim.utils import load_config, load_results


def _batch_to_rounds(values: list) -> dict:
    """Convert batch store list to {round_num: value}, round_num is 1-based."""
    return {i + 1: v for i, v in enumerate(values)}


def _load_data(results) -> dict:
    """Load coordinator batch stores and investor turn payloads.

    Coordinator → batch stores (store names depend on Market.act() registration)
    Investors   → turn decision_payload fields (names depend on _make_decision() return)
    """
    market_prices = {}
    fundamentals  = {}
    volumes       = {}

    for player in results.players_by_role("coordinator").values():
        if "price" in player.batch_store_names:
            market_prices.update(_batch_to_rounds(player.batch("price").all()))
        if "fundamental" in player.batch_store_names:
            fundamentals.update(_batch_to_rounds(player.batch("fundamental").all()))
        if "volume" in player.batch_store_names:
            volumes.update(_batch_to_rounds(player.batch("volume").all()))
        # Scenario-specific stores: check player.batch_store_names and add here

    investor_quantities = {}
    investor_bids       = {}
    for pid, player in results.players_by_role("player").items():
        qty = player.turns.field("quantity")
        if qty:
            investor_quantities[pid] = qty
        bid = player.turns.field("bid_price")
        if bid:
            investor_bids[pid] = bid
        # Scenario-specific fields: add player.turns.field("your_field") here

    return {
        "market_prices":       market_prices,
        "fundamentals":        fundamentals,
        "volumes":             volumes,
        "investor_quantities": investor_quantities,
        "investor_bids":       investor_bids,
    }


def main():
    import argparse, json, os
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    args = parser.parse_args()

    config     = load_config(args.config)
    record_path = config["setting"]["record_path"]
    base_dir   = os.path.dirname(record_path)
    output_dir = os.path.join(base_dir, "analysis")
    os.makedirs(output_dir, exist_ok=True)

    results = load_results(config)   # lazy
    data    = _load_data(results)    # actual disk reads happen here
    # ... compute metrics, generate plots, write summary.json ...
```
