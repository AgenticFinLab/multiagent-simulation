# Volatility Trader

## 1 Summary

| Field                 | Content |
|-----------------------|---------|
| agent_type            | volatility-trader |
| Class name            | VolatilityTraderAgent |
| Domain role           | Volatility-targeting / risk-parity strategy that adjusts exposure based on realized vol |
| Theory family         | GARCH / Volatility Targeting |
| Primary signals       | price_history, realized_volatility |
| Population default    | 1 |
| Variant coverage      | Threshold-based regime switching between risk-on and risk-off |

## 2 Definition and Goals

This agent models a volatility-targeting strategy that reduces exposure when realized volatility is high and increases exposure when volatility is low. The real-world counterpart is a risk-parity fund, volatility-managed portfolio, or institutional risk overlay.

The decision goal is to sell (reduce risk) when the volatility ratio exceeds a high threshold and buy (add risk) when it drops below a low threshold. Between thresholds, it holds. This creates a mechanical dampening effect during stress and position-building during calm.

In simulation this agent acts as a procyclical amplifier during vol regime transitions and contributes to the "volatility of volatility" feedback loop. Non-goals: it must not trade on price direction, fundamentals, or momentum.

## 3 Theoretical Foundation

**ARCH/GARCH Models**:
- Citation: Engle (1982, DOI: 10.2307/1912773); Bollerslev (1986, DOI: 10.1016/0304-4076(86)90063-1).
- Core Insight: Volatility is time-varying and predictable from past squared returns; GARCH(1,1) captures persistence in conditional variance, justifying dynamic position sizing.

**Volatility-Managed Portfolios**:
- Citation: Moreira, A. & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611-1644. https://doi.org/10.1111/jofi.12575
- Core Insight: Scaling exposure inversely with conditional volatility improves Sharpe ratios because expected returns do not increase proportionally with risk.

- Relevance to This Agent: The agent implements a simplified volatility-targeting rule with discrete thresholds rather than continuous inverse-vol scaling.
- Falsification Conditions: If the agent ignores volatility or trades based on price direction, it is misspecified.

## 4 Design Purpose and Activation Triggers

Purpose: Inject volatility-responsive mechanical flows that dampen exposure in stress and rebuild in calm, contributing to vol-clustering dynamics.

Call Frequency: every tick (once vol_lookback window is filled).

Prerequisite Signals:
- `price_history` of length >= `vol_lookback + 1`
- Ability to compute realized volatility

Missing-Signal Policy: hold if insufficient history for vol computation.

Activation Triggers:
- `vol_ratio > high_vol_threshold`: sell (reduce exposure).
- `vol_ratio < low_vol_threshold`: buy (add exposure).
- Otherwise: hold.

Deactivation Conditions:
- Insufficient price history for vol estimate.
- No position to sell (cannot go short beyond constraint).
- No cash to buy.

## 5 Behavioral Framework

### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price_history` | Array | vol_lookback + 1 ticks | Compute realized returns for vol |
| `realized_volatility` | Derived | vol_lookback ticks | Current vol estimate |

Does NOT use: fundamental_value, trend, momentum, peer positions.

### Core Behavioral Mechanism

1. Compute returns over vol_lookback window and their standard deviation.
2. Compute vol_ratio: `realized_vol / baseline_vol`.
3. If `vol_ratio > high_vol_threshold`: sell `base_position_size` units.
4. If `vol_ratio < low_vol_threshold`: buy `base_position_size` units.
5. Otherwise: hold. Apply cash and inventory constraints.

### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | fixed `base_position_size` when threshold breached |
| Inventory constraint | cannot sell below 0 without short permission |
| Wealth / leverage cap | cash >= 0; no margin |

### Mathematical Model

```
returns_t = [P_i/P_{i-1} - 1 for i in (t-L+1, ..., t)]
realized_vol = std(returns_t)
vol_ratio = realized_vol / baseline_vol

if vol_ratio > high_vol_threshold:
    quantity = -base_position_size * (vol_ratio - 1.0)  (proportional sell)
elif vol_ratio < low_vol_threshold:
    quantity = +base_position_size * (1.0 - vol_ratio)  (proportional buy)
else:
    quantity = 0  (hold)

quantity = clamp(quantity, -20, +20)
```

## 6 Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `vol_lookback` | int | 5 | >= 2 | Window for realized vol computation |
| `high_vol_threshold` | float | 1.5 | > 1.0 | Vol ratio above which agent sells |
| `low_vol_threshold` | float | 0.7 | (0, 1.0) | Vol ratio below which agent buys |
| `base_position_size` | float | 15.0 | > 0 | Fixed order size when threshold breached |
| `initial_cash` | float | 10000.0 | > 0 | Starting cash endowment |
| `initial_position` | int | 0 | >= 0 | Starting inventory |

## 7 Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | 1 |
| Parameter heterogeneity policy | single canonical instance |
| Heterogeneity per parameter | N/A at population = 1 |
| Cross-agent correlation | N/A |
| Identity persistence | fixed for episode duration |

## 8 Worked Numerical Examples

### Case 1 - High vol triggers sell
```text
State: recent returns = [0.02, -0.03, 0.04, -0.02, 0.03].
realized_vol = std([0.02,-0.03,0.04,-0.02,0.03]) = 0.029.
baseline_vol = 0.015 (estimated long-run).
vol_ratio = 0.029/0.015 = 1.93 > 1.5.
Decision: sell 15 units (de-risk).
```

### Case 2 - Low vol triggers buy
```text
State: recent returns = [0.001, 0.002, -0.001, 0.001, 0.0].
realized_vol = std(...) = 0.001.
baseline_vol = 0.015.
vol_ratio = 0.001/0.015 = 0.067 < 0.7.
Decision: buy 15 units (re-risk).
```

### Case 3 - Vol in normal range
```text
State: recent returns with realized_vol = 0.014.
baseline_vol = 0.015.
vol_ratio = 0.014/0.015 = 0.93.
0.7 < 0.93 < 1.5.
Decision: hold.
```

### Edge Case - Insufficient history
```text
State: tick=3, vol_lookback=5.
Only 3 returns available, need 5.
Decision: hold.
```

## 9 Validation and Calibration

**Expected stylized facts** when this agent is present:
- Position reductions during volatility spikes (procyclical selling in stress).
- Position rebuilding during calm periods.
- Contributes to vol-of-vol dynamics and feedback between flows and volatility.

**Sanity bounds (red flags)**:
- Agent buys during high-vol episodes.
- Agent sells during low-vol episodes.
- Trades fire before vol_lookback window is filled.
- Position size varies (should be fixed at base_position_size).

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_vol_trader` | population = 0 | Removing vol trader reduces procyclical flow |
| `tight_thresholds` | high=1.1, low=0.9 | Tighter bands increase trading frequency |

## 10 Academic References

| # | Citation | DOI |
|---|----------|-----|
| 1 | Engle, R. F. (1982). Autoregressive conditional heteroscedasticity. *Econometrica*, 50(4), 987-1007. | 10.2307/1912773 |
| 2 | Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *J. Econometrics*, 31(3), 307-327. | 10.1016/0304-4076(86)90063-1 |
| 3 | Moreira, A. & Muir, T. (2017). Volatility-managed portfolios. *JF*, 72(4), 1611-1644. | 10.1111/jofi.12575 |

## 11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AgenticFinLab |
| Created | 2025-07-14 |
| Version | 1.0.0 |
| Change log | 1.0.0 - Initial creation based on vol-targeting/risk-parity archetype |
| Status | draft |
