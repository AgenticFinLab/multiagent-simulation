# Mean-reversion contrarian trader

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Mean-reversion contrarian trader |
| Theory Family         | Behavioral Finance |
| Market Role           | **Stabilising** - fades recent overreaction and supplies counter-flow |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | none |
| Determinism           | deterministic |

## Definition and Goals

This agent models a contrarian or mean-reversion trader who bets against recent overextension. The real-world counterpart is a contrarian / mean-reversion trader.

The decision goal is to emit buy, sell, or hold orders from cumulative recent return. It buys after sufficiently negative cumulative return and sells after sufficiently positive cumulative return.

In simulation this agent helps produce long-run reversal and stabilising counter-flow. Non-goals: it must not chase momentum, use personal cost basis, or quote two-sided as a market maker.

## Theoretical Foundation

**Overreaction and Reversal**:
- Theory / Study: Stock market overreaction.
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Markets can overreact to recent information, creating later reversals. Contrarian traders exploit this by taking positions opposite recent extreme moves.
- Mathematical Formulation: `cum_ret = (P_t - P_{t-L}) / P_{t-L}`; trade opposite sign when `abs(cum_ret) > theta`.
- Empirical Evidence: De Bondt and Thaler document loser-winner reversal patterns.
- Relevance to This Agent: The agent operationalises overreaction correction using a cumulative-return trigger.
- Calibration Source: De Bondt & Thaler (1985).
- Falsification Conditions: If the agent buys after strong positive cumulative return, it is momentum rather than contrarian.
- Alternative Theories: short-horizon momentum; rational expectations.

**Short-Horizon Mean Reversion**:
- Theory / Study: Predictable short-horizon return reversal.
- Citation: Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881-898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
- Core Insight: Returns can reverse at short horizons, making recent cumulative return a useful contrarian signal. This supports a finite lookback window for reversal trading.
- Mathematical Formulation: `cum_ret = (P_t - P_{t-lookback}) / P_{t-lookback}`.
- Empirical Evidence: The source scenario maps `lookback_window = 10` to Jegadeesh's short-horizon reversal evidence.
- Relevance to This Agent: The lookback return is the agent's only signal.
- Calibration Source: Jegadeesh (1990); De Bondt & Thaler (1985).
- Falsification Conditions: If lookback return has no relation to subsequent reversal, the trigger should be disabled.
- Alternative Theories: momentum continuation.

## Design Purpose and Activation Triggers

Purpose: Provide stabilising counter-flow against extended recent price moves.

Call Frequency: every-tick after warm-up.

Prerequisite Signals:
- `price` available
- `price_history` with at least `lookback` observations available

Missing-Signal Policy: hold until the lookback window is available.

Activation Triggers:
- `cum_ret > entry_threshold`: submit sell order.
- `cum_ret < -entry_threshold`: submit buy order.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached: hibernate constrained side.
- Lookback unavailable: hold.

Market Contribution by Regime:
| Regime | Contribution | Mechanism |
|--------|--------------|-----------|
| Calm | Stabilising | Fades small overextensions when threshold is met. |
| Stress | Stabilising | Provides counter-flow against sharp runs or selloffs. |

Interaction with other agents: Directly opposes MomentumTrader and can complement RationalUpdater during overvaluation.

## Behavioral Framework

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current endpoint |
| `price_history` | Series | `lookback` ticks | Start point for cumulative return |

Does NOT use: `fundamental`, `anchor`, `cost_basis`, bid-ask depth.

#### Core Behavioral Mechanism

1. Maintain recent price history.
2. Compute cumulative return over `lookback`.
3. Sell if the cumulative return is sufficiently positive.
4. Buy if the cumulative return is sufficiently negative.
5. Hold inside the threshold.
6. Size order by magnitude of overextension.
7. Clip by inventory and cash constraints.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q = min(base_position_size, abs(cum_ret) * sizing_scale)` |
| Order lifetime | 1 tick |
| Cancellation policy | unfilled orders expire at end of tick |
| Inventory constraint | inventory bounded by `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  cum_ret = (P_t - P_{t-L}) / P_{t-L}
  sell if cum_ret > theta
  buy if cum_ret < -theta
  otherwise hold
  ```
- Sizing function:
  ```
  Q = -sign(cum_ret) * min(base_position_size, abs(cum_ret) * sizing_scale)
  ```
- State variables: `price_history`; `position`; `cash`.
- State-update rule: append price pre-decision; update position and cash post-fill.
- Determinism contract: deterministic given price history and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `L` | lookback window | 10 | Jegadeesh (1990) |
| `theta` | entry threshold | 0.05 | Standardised |

#### Behavioral Properties

- Time horizon: medium, because it uses multi-tick cumulative return.
- Risk tolerance: medium.
- Information asymmetry: none.
- Psychological profile: contrarian belief in overreaction correction.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `lookback` | int | 10 | int >= 1 | high | Window for cumulative return. | Higher -> slower contrarian response. | Jegadeesh (1990) |
| `entry_threshold` | float | 0.05 | [0, 1] | high | Overextension needed to trade. | Higher -> fewer contrarian trades. | Standardised |
| `base_position_size` | float | 20.0 | > 0 | medium | Maximum order size. | Higher -> stronger reversal pressure. | Standardised |
| `sizing_scale` | float | 500.0 | > 0 | medium | Converts cumulative return to quantity. | Higher -> larger counter-flow. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | low | Inventory cap. | Higher -> more contrarian capacity. | Standardised |

## Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | scenario-dependent |
| Parameter heterogeneity policy | iid threshold and lookback draws |
| Heterogeneity per parameter | `lookback -> {5, 10, 20}`, `entry_threshold -> Uniform(0.04, 0.08)` |
| Cross-agent correlation | none |
| Identity persistence | identical across episodes unless redrawn |

## Worked Numerical Examples

### Case 1 - Sell overextension
```text
Market state: P_t=108, P_{t-10}=100.
Calculation: cum_ret=0.08.
Decision: sell min(20, 0.08*500)=20.
State update: position -20; cash +2160.
```

### Case 2 - Buy oversold move
```text
Market state: P_t=92, P_{t-10}=100.
Calculation: cum_ret=-0.08.
Decision: buy 20.
State update: position +20; cash -1840.
```

### Case 3 - Hold
```text
Market state: P_t=103, P_{t-10}=100.
Calculation: cum_ret=0.03.
Decision: hold.
State update: append P_t to history.
```

### Edge Case - Insufficient lookback
```text
Market state: only 4 prices available, lookback=10.
Calculation: cumulative return unavailable.
Decision: hold.
State update: append current price.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `lookback`, `entry_threshold` <- reversal horizon calibration.

**Expected stylized facts** when this agent dominates the population:
- Long-run reversal.
- Dampened momentum overshoot.
- Stabilising buy flow after selloffs.

**Sanity bounds (red flags during simulation)**:
- Agent trades with recent trend.
- Agent uses future prices in cumulative return.
- Agent trades before warm-up.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_contrarian` | `entry_threshold = 1.0` | Removing contrarian flow increases overshoot. |
| `fast_contrarian` | `lookback = 3` | Shorter windows create more frequent reversals. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x | Overreaction and reversal |
| 2 | Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881-898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x | Short-horizon reversal |
| 3 | Chopra, N., Lakonishok, J., & Ritter, J. R. (1992). Measuring abnormal performance. *Journal of Financial Economics*, 31(2), 235-268. https://doi.org/10.1016/0304-405X(92)90005-I | Cross-validates overreaction effects |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author |  |
| Reviewed by |  |
| Created | 2026-06-27 |
| Version | 1.0.0 |
| Change log | 1.0.0 - Created from AnchoringEffect Agent Design Summary row 4.7 |
| Status | draft |
