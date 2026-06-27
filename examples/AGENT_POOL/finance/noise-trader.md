# Random noise trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Random noise trader |
| Theory Family         | Behavioral Finance |
| Market Role           | **Context-dependent** - supplies liquidity and volatility with zero-mean order flow |
| Time Horizon          | short |
| Risk Tolerance        | high |
| Information Asymmetry | none |
| Determinism           | stochastic-given-seed |

## Definition and Goals

This agent models an uninformed liquidity participant whose orders are random rather than signal-driven. The real-world counterpart is a noise trader, retail flow participant, or uninformed liquidity demander.

The decision goal is to randomly emit buy, sell, or hold orders with bounded quantity. It follows a stochastic activation and direction draw, not a valuation or trend criterion.

In simulation this agent helps produce fat-tailed return distributions, volume-volatility co-movement, and baseline liquidity. Non-goals: it must not use fundamentals, anchors, momentum, or cost basis.

## Theoretical Foundation

**Noise Trading**:
- Theory / Study: Noise as a necessary component of market liquidity.
- Citation: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x; DeLong et al. (1990). Citation coverage for DeLong et al. is limited to the short citation explicitly present in the source scenario file.
- Core Insight: Uninformed order flow creates liquidity but also volatility and mispricing risk. Rational arbitrage is limited when noise demand can move price further away from value before correction.
- Mathematical Formulation: `trade ~ Bernoulli(p)`; conditional direction is `buy` or `sell` with equal probability.
- Empirical Evidence: Market microstructure studies decompose order flow into informed and uninformed components.
- Relevance to This Agent: The agent creates random demand shocks and liquidity background.
- Calibration Source: Black (1986); DeLong et al. (1990).
- Falsification Conditions: If order direction is correlated with `fundamental` or `momentum`, the agent is not pure noise.
- Alternative Theories: Liquidity provision; sentiment trading.

## Design Purpose and Activation Triggers

Purpose: Add stochastic background order flow that prevents deterministic price paths.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- seeded random source available

Missing-Signal Policy: hold if price or seed-bearing random source is unavailable.

Activation Triggers:
- `Bernoulli(trade_probability) = 1`: draw direction and quantity, then submit order.
- `Bernoulli(trade_probability) = 0`: hold.
- `<Default>`: hold.

Deactivation Conditions:
- Cash floor breached: hibernate buy side.
- Inventory cap reached: hibernate constrained side.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Stabilising | Supplies two-sided random liquidity on average. |
| Stress | Destabilising | Large random orders can amplify volatility. |

Interaction with other agents: Provides liquidity and noise that informed traders trade against.

## Behavioral Framework

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Execution reference |
| `rng_state` | State | persistent | Reproducible random activation |

Does NOT use: `fundamental`, `anchor`, `momentum`, `cost_basis`, peer flow.

#### Core Behavioral Mechanism

1. Draw activation from `Bernoulli(trade_probability)`.
2. Hold if activation is zero.
3. Draw direction uniformly from buy and sell.
4. Draw quantity from a bounded distribution.
5. Clip buy orders by cash.
6. Clip sell orders by inventory.
7. Update random state after each draw.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q ~ Uniform(min_order, max_order)` conditional on activation |
| Order lifetime | 1 tick |
| Cancellation policy | unfilled orders expire at end of tick |
| Inventory constraint | inventory bounded by `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed random quantity `Q*(t)`.
- Trigger function:
  ```
  active ~ Bernoulli(p)
  if not active: hold
  direction ~ Bernoulli(0.5)
  ```
- Sizing function:
  ```
  abs(Q) ~ Uniform(min_order, max_order)
  sign(Q) = +1 for buy, -1 for sell
  ```
- State variables: `rng_state`; `position`; `cash`.
- State-update rule: update RNG state pre-decision; update position and cash post-fill.
- Determinism contract: stochastic-given-seed.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `p` | activation probability | 0.05 | Black (1986) |
| `Q` | random order size | Uniform(100, 500) | Standardised |

#### Behavioral Properties

- Time horizon: short and memoryless.
- Risk tolerance: high, because orders ignore value and trend.
- Information asymmetry: none.
- Psychological profile: uninformed random trading, no systematic bias.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `trade_probability` | float | 0.05 | [0, 1] | high | Per-tick activation probability. | Higher -> more volume and volatility. | Black (1986) |
| `min_order` | float | 100.0 | > 0 | medium | Minimum random order quantity. | Higher -> larger volatility floor. | Standardised |
| `max_order` | float | 500.0 | > `min_order` | high | Maximum random order quantity. | Higher -> fatter return tails. | Standardised |
| `inventory_max` | float | 1000.0 | > 0 | medium | Inventory cap. | Higher -> fewer clipped sell/buy decisions. | Standardised |
| `seed` | int | 1 | int >= 0 | low | Random seed. | Higher -> changes path, not distribution. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | iid seeded draws |
| Heterogeneity per parameter | `trade_probability -> Uniform(0.03, 0.08)` |
| Cross-agent correlation | none unless scenario shares seed streams |
| Identity persistence | re-drawn every episode when seed changes |

## Worked Numerical Examples

### Case 1 - Random buy
```text
Market state: P=100, activation draw=0.02, p=0.05, direction=buy, quantity=250.
Calculation: active because 0.02 < 0.05.
Decision: buy 250 at P=100.
State update: position +250; cash -25000; RNG advances.
```

### Case 2 - Random sell
```text
Market state: P=101, activation draw=0.01, direction=sell, quantity=180, inventory=150.
Calculation: sell clipped to 150 by inventory.
Decision: sell 150 at P=101.
State update: position 0; cash +15150.
```

### Case 3 - Hold
```text
Market state: P=102, activation draw=0.80.
Calculation: 0.80 > 0.05.
Decision: hold.
State update: only RNG advances.
```

### Edge Case - Missing seed
```text
Market state: P=100, rng_state unavailable.
Calculation: random contract unavailable.
Decision: hold.
State update: unchanged.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `trade_probability` <- scenario liquidity calibration.
- `min_order`, `max_order` <- order-flow volatility calibration.

**Expected stylized facts** when this agent dominates the population:
- Nonzero volume with zero expected signed demand.
- Fat-tailed short-run returns when order size is large.
- Volatility without fundamental information.

**Sanity bounds (red flags during simulation)**:
- Mean signed demand is persistently one-sided under iid mode.
- Direction depends on `fundamental`.
- Orders exceed the declared size support.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_noise` | `trade_probability = 0` | Removing noise makes prices overly deterministic. |
| `large_noise` | `max_order = 2000` | Larger random orders increase tail thickness. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x | Noise trading |
| 2 | DeLong et al. (1990) | Noise-trader risk; only short citation available in source file |
| 3 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3 | Source scenario cites this for informed vs. uninformed order flow fractions |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author |  |
| Reviewed by |  |
| Created | 2026-06-27 |
| Version | 1.0.0 |
| Change log | 1.0.0 - Created from AnchoringEffect Agent Design Summary row 4.5 |
| Status | draft |
