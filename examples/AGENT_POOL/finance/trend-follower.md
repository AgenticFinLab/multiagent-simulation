# Trend Follower

## 1 Summary

| Field                 | Content |
|-----------------------|---------|
| agent_type            | trend-follower |
| Class name            | TrendFollowerAgent |
| Domain role           | CTA/managed-futures trend strategy that chases momentum with volatility scaling |
| Theory family         | Momentum / Time-Series Momentum |
| Primary signals       | price_history, volatility |
| Population default    | 3 |
| Variant coverage      | Lookback-based trend detection with vol-adjusted sizing |

## 2 Definition and Goals

This agent models a systematic trend-following strategy commonly deployed by CTAs and managed-futures funds. The real-world counterpart is a momentum fund that goes long after price rises and short after price falls, scaling exposure inversely with volatility.

The decision goal is to detect a trend signal from recent price history and trade in the direction of that trend with position size scaled by signal strength and a volatility multiplier. It activates every tick once sufficient history is available.

In simulation this agent amplifies trends and contributes to momentum clustering and volatility persistence. Non-goals: it must not trade on fundamental value or mean-revert.

## 3 Theoretical Foundation

**Time-Series Momentum**:
- Citation: Moskowitz, T. J., Ooi, Y. H. & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228-250. https://doi.org/10.1016/j.jfineco.2011.11.003
- Core Insight: Assets that have risen over the past 1-12 months tend to continue rising, and vice versa. Trend-following strategies profit from this autocorrelation.

**Cross-Sectional Momentum**:
- Citation: Jegadeesh, N. & Titman, S. (1993). Returns to buying winners and selling losers. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
- Core Insight: Relative strength strategies that buy past winners and sell past losers generate significant abnormal returns over 3-12 month horizons.

- Relevance to This Agent: The agent implements the time-series momentum signal with volatility targeting, consistent with CTA practice.
- Falsification Conditions: If the agent mean-reverts or ignores recent returns, it is misspecified.

## 4 Design Purpose and Activation Triggers

Purpose: Inject positive-feedback trading that generates momentum persistence, trend amplification, and herding dynamics.

Call Frequency: every tick (once lookback window filled).

Prerequisite Signals:
- `price_history` of length >= `lookback_window`
- `volatility` estimate available

Missing-Signal Policy: hold if insufficient price history.

Activation Triggers:
- `abs(trend_signal) > trend_threshold`: compute direction and quantity, submit order.
- `abs(trend_signal) <= trend_threshold`: hold (no trend detected).

Deactivation Conditions:
- Insufficient history (first `lookback_window - 1` ticks).
- Cash or inventory constraints binding.

## 5 Behavioral Framework

### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price_history` | Array | lookback_window ticks | Compute return for trend signal |
| `volatility` | Continuous | rolling estimate | Scale position inversely with vol |

Does NOT use: fundamental_value, peer positions, order book depth.

### Core Behavioral Mechanism

1. Compute trend signal: `trend = (price - price[t - lookback_window]) / price[t - lookback_window]`.
2. If `abs(trend) <= trend_threshold`, hold.
3. Determine direction: `direction = sign(trend)`.
4. Compute strength: `strength = abs(trend)`.
5. Compute vol_multiplier: `vol_multiplier = volatility_sensitivity * (baseline_volatility / current_volatility)`.
6. Compute quantity: `quantity = direction * base_position_size * strength * vol_multiplier`.
7. Round to integer, apply cash/inventory constraints.

### Action Space

| Aspect | Specification |
|--------|---------------|
| Order types allowed | market, hold-no-op |
| Price level rule | market order at current price |
| Order quantity rule | `Q = direction * base_position_size * strength * vol_multiplier` |
| Inventory constraint | bounded by cash and short-sale limits |
| Wealth / leverage cap | cash >= 0; configurable leverage |

### Mathematical Model

```
trend = (P_t - P_{t-L}) / P_{t-L}
direction = sign(trend)
strength = abs(trend)
vol_multiplier = volatility_sensitivity * (baseline_volatility / current_volatility)
quantity = round(direction * base_position_size * strength * vol_multiplier)
```

## 6 Parameters

| Parameter | Type | Default | Valid Range | Description |
|-----------|------|---------|-------------|-------------|
| `lookback_window` | int | 3 | >= 2 | Number of ticks for return calculation |
| `trend_threshold` | float | 0.005 | >= 0 | Minimum abs return to trigger trade |
| `base_position_size` | float | 30.0 | > 0 | Base order size multiplier |
| `volatility_sensitivity` | float | 0.8 | > 0 | Scaling factor for vol adjustment |
| `baseline_volatility` | float | 1.0 | > 0 | Reference volatility level |
| `initial_cash` | float | 10000.0 | > 0 | Starting cash endowment |
| `initial_position` | int | 0 | >= 0 | Starting inventory |

## 7 Population and Heterogeneity

| Aspect | Specification |
|--------|---------------|
| Default population size | 3 |
| Parameter heterogeneity policy | lookback_window varied across instances |
| Heterogeneity per parameter | `lookback_window ~ {2, 3, 5}` |
| Cross-agent correlation | correlated via shared price signal |
| Identity persistence | fixed for episode duration |

## 8 Worked Numerical Examples

### Case 1 - Uptrend detected
```text
State: prices=[100, 101, 102, 103], lookback=3, current_vol=1.0.
trend = (103 - 100)/100 = 0.03 > 0.005.
direction = +1, strength = 0.03.
vol_multiplier = 0.8 * (1.0/1.0) = 0.8.
quantity = 1 * 30 * 0.03 * 0.8 = 0.72 -> round to 1.
Decision: buy 1 unit.
```

### Case 2 - Downtrend with high volatility
```text
State: prices=[100, 98, 95, 92], lookback=3, current_vol=2.0.
trend = (92 - 100)/100 = -0.08 > threshold in abs.
direction = -1, strength = 0.08.
vol_multiplier = 0.8 * (1.0/2.0) = 0.4.
quantity = -1 * 30 * 0.08 * 0.4 = -0.96 -> round to -1.
Decision: sell 1 unit.
```

### Case 3 - No trend
```text
State: prices=[100, 100.1, 99.9, 100.2], lookback=3.
trend = (100.2 - 100)/100 = 0.002 < 0.005.
Decision: hold.
```

### Edge Case - Insufficient history
```text
State: tick=1, lookback_window=3.
Only 1 price available, need 4 (current + lookback).
Decision: hold.
```

## 9 Validation and Calibration

**Expected stylized facts** when this agent is present:
- Positive short-lag autocorrelation in returns.
- Momentum crashes after trend reversals.
- Volatility clustering amplified by procyclical sizing.

**Sanity bounds (red flags)**:
- Agent trades against recent trend direction.
- Position size independent of volatility.
- Trades fire before lookback window is filled.

### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_trend` | population = 0 | Removing trend-followers reduces autocorrelation |
| `no_vol_scaling` | `volatility_sensitivity = 0` | Without vol scaling, drawdowns deepen |

## 10 Academic References

| # | Citation | DOI |
|---|----------|-----|
| 1 | Moskowitz, T. J., Ooi, Y. H. & Pedersen, L. H. (2012). Time series momentum. *JFE*, 104(2), 228-250. | 10.1016/j.jfineco.2011.11.003 |
| 2 | Jegadeesh, N. & Titman, S. (1993). Returns to buying winners and selling losers. *JF*, 48(1), 65-91. | 10.1111/j.1540-6261.1993.tb04702.x |
| 3 | Barberis, N., Shleifer, A. & Vishny, R. (1998). A model of investor sentiment. *JFE*, 49(3), 307-343. | 10.1016/S0304-405X(98)00027-0 |

## 11 Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | AgenticFinLab |
| Created | 2025-07-14 |
| Version | 1.0.0 |
| Change log | 1.0.0 - Initial creation based on CTA/momentum archetype |
| Status | draft |
