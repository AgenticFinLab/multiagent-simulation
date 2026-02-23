# Herd Effect Simulation

## Overview

| Component | Count | Role                                               |
|-----------|-------|----------------------------------------------------|
| Market    | 1     | Broadcasts price, aggregates demand, adjusts price |
| Investors | 5     | Different strategies, submit bids                  |
| Rounds    | 50    | Price discovery iterations                         |

## Flow Diagram

```
Round N:
┌──────────────────────────────────────────────────────────────────────────┐
│                              MARKET                                       │
│  1. Collect bids from Round N-1                                          │
│  2. Calculate aggregate demand                                            │
│  3. Adjust price: new_price = price + demand × sensitivity + noise        │
│  4. Broadcast new price to all investors                                  │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │ price broadcast
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│    Momentum     │   │   Contrarian    │   │   RiskAverse    │ ...
│  Follow trend   │   │  Counter trend  │   │  Conservative   │
└────────┬────────┘   └────────┬────────┘   └────────┬────────┘
         │                     │                     │
         └─────────────────────┼─────────────────────┘
                               │ bids
                               ▼
                         ┌──────────┐
                         │  MARKET  │
                         └──────────┘
                               │
                               ▼
                          Round N+1
```

## Investor Strategies

| Strategy        | Behavior        | Formula                            | Market Effect        |
|-----------------|-----------------|------------------------------------|----------------------|
| **Momentum**    | Follow trend    | `qty = sensitivity × change%`      | Amplifies volatility |
| **Contrarian**  | Against trend   | `qty = -sensitivity × change%`     | Stabilizes price     |
| **RiskAverse**  | Conservative    | `qty = small, volatility-adjusted` | Minimal impact       |
| **Aggressive**  | Large positions | `qty = amplification × change%`    | High volatility      |
| **NoiseTrader** | Random          | `qty = random()`                   | Adds noise           |

## Market Price Adjustment

```
new_price = current_price
          + SENSITIVITY × aggregate_demand      # Supply-demand
          + MEAN_REVERSION × (fundamental - price)  # Mean reversion
          + random_noise                        # Market noise
```

| Parameter           | Value | Effect                   |
|---------------------|-------|--------------------------|
| `SENSITIVITY`       | 0.1   | Price response to demand |
| `FUNDAMENTAL_VALUE` | 100.0 | Long-term equilibrium    |
| `MEAN_REVERSION`    | 0.02  | Pull towards fundamental |

## Topology

```
                    ┌───────────────────┐
                    │      market       │ ◄── Level 0 (executes first)
                    └─────────┬─────────┘
                              │
        ┌─────────┬───────────┼───────────┬─────────┐
        ▼         ▼           ▼           ▼         ▼
   momentum  contrarian  risk_averse  aggressive  noise  ◄── Level 1
```

| Level | Nodes       | Action                 |
|-------|-------------|------------------------|
| 0     | `market`    | Broadcast price        |
| 1     | 5 investors | Submit bids (parallel) |

## Files

| File                                | Purpose                                |
|-------------------------------------|----------------------------------------|
| `players.py`                        | `Market` + 5 investor strategy classes |
| `run_herd.py`                       | Entry point                            |
| `configs/HerdEffect/simulation.yml` | Main config                            |
| `configs/HerdEffect/players.yml`    | Player definitions                     |
| `configs/HerdEffect/topology.yml`   | Communication graph                    |

## Implementation

### Market.perceive()

```python
# Collect bids from all investors
bids = []
for inb in observation.inbounds:
    bids.append({
        "investor": inb.sender_id,
        "bid_price": inb.payload["bid_price"],
        "quantity": inb.payload["quantity"],
    })
```

### Market.decide()

```python
# Aggregate demand
total_demand = sum(b["quantity"] for b in bids)

# Price adjustment
price_change = SENSITIVITY * total_demand
mean_reversion = 0.02 * (FUNDAMENTAL - price)
new_price = price + price_change + mean_reversion + noise

# Broadcast
return {
    "outbound_messages": [{"payload": {"price": new_price, ...}}]
}
```

### Investor.perceive()

```python
# Get market price
market_data = observation.inbounds[0].payload
price = market_data["price"]
change_pct = market_data["change_pct"]
```

### Investor.decide() (Momentum example)

```python
# Follow the trend
quantity = SENSITIVITY * change_pct / 100 * 10
bid_price = price * (1 + change_pct / 100 * 0.5)

return {
    "outbound_messages": [{"payload": {"bid_price": bid_price, "quantity": quantity}}]
}
```

## Running

```bash
python examples/HerdEffect/run_herd.py -c configs/HerdEffect/simulation.yml
```

## Expected Behavior

| Phase   | Rounds | Observation                                    |
|---------|--------|------------------------------------------------|
| Initial | 1-5    | Price fluctuates as strategies interact        |
| Middle  | 6-30   | Herd behavior may cause price bubbles/crashes  |
| Late    | 31-50  | Price tends to mean-revert towards fundamental |

## Herd Behavior Indicators

| Indicator             | Description                                         |
|-----------------------|-----------------------------------------------------|
| Price momentum        | Sustained price movements in one direction          |
| Volatility clustering | High volatility periods followed by more volatility |
| Correlation           | Momentum and aggressive investors move together     |
