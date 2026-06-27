# Anchoring-bias retail trader

## Summary

| Field                 | Content                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| Archetype             | Anchoring-bias retail trader                                            |
| Theory Family         | Behavioral Finance                                                      |
| Market Role           | **Destabilising** - sustains mispricing around an initial price anchor  |
| Time Horizon          | medium                                                                  |
| Risk Tolerance        | medium                                                                  |
| Information Asymmetry | none                                                                    |
| Determinism           | deterministic                                                           |

## Definition and Goals

This agent models a retail trader or buy-side analyst who anchors on the first salient market price and adjusts insufficiently toward observable fundamental value. The real-world counterpart is a retail trader / individual investor or analyst whose valuation remains pulled toward an initial quote.

The decision goal is to emit a buy, sell, or hold order with quantity determined by the perceived deviation between price and an anchor-biased target. It follows a heuristic criterion rather than expected-value optimization: trade around `anchor + alpha * (fundamental - anchor)`, not around the true fundamental.

In simulation this agent helps produce sustained mispricing relative to fundamentals, slow price discovery, and short-run return persistence. Non-goals: it must not trade directly on momentum, provide two-sided liquidity, or fully converge to fundamental value when `alpha < 1`.

## Theoretical Foundation

**Anchoring and Insufficient Adjustment**:
- Theory / Study: Anchoring heuristic in numerical estimation.
- Citation: Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131. https://doi.org/10.1126/science.185.4157.1124
- Core Insight: People start from a salient anchor and adjust too little, even when the anchor is arbitrary. In markets this creates valuations that remain biased toward first-observed prices.
- Mathematical Formulation: `target = anchor + alpha * (F - anchor)`.
- Empirical Evidence: The classic anchoring experiments show large shifts in median estimates after exposure to arbitrary anchors.
- Relevance to This Agent: The agent operationalises insufficient adjustment by trading around an anchor-biased fair value.
- Calibration Source: Tversky & Kahneman (1974), with financial forecast underreaction interpreted as `alpha < 1`.
- Falsification Conditions: If the agent trades as if `target = F`, anchoring is absent.
- Alternative Theories: Rational expectations; conservatism / underreaction.

**Consensus Forecast Anchoring**:
- Theory / Study: Anchoring bias in consensus forecasts.
- Citation: Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127
- Core Insight: Professional forecasts revise only partially toward new information, leaving predictable forecast errors. The source scenario uses this mechanism to connect individual anchoring to market-level slow price discovery.
- Mathematical Formulation: `forecast_revision = theta * (new_information - prior_forecast)`.
- Empirical Evidence: The source scenario reports under-revision of roughly 30-70% and forecast-error autocorrelation around 0.4.
- Relevance to This Agent: The agent's `alpha` parameter is the trading-rule analogue of partial forecast revision.
- Calibration Source: Campbell & Sharpe (2009), as cited in `simulation-bases.md`.
- Falsification Conditions: If lowering `alpha` does not increase mispricing persistence, forecast anchoring is not represented.
- Alternative Theories: Rational expectations.

## Design Purpose and Activation Triggers

Purpose: Generate persistent upward or downward price support around a biased reference price.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `anchor` initialized from a valid first price

Missing-Signal Policy: hold until `price` and `fundamental` are valid; initialize `anchor` from the first valid price.

Activation Triggers:
- `perceived_dev < -threshold`: submit buy order.
- `perceived_dev > threshold`: submit sell order.
- `<Default>`: hold.

Deactivation Conditions:
- Inventory cap reached: hibernate the side that would increase the breach.
- Cash floor breached: hold buy side until cash recovers.

Market Contribution by Regime:
| Regime | Contribution  | Mechanism |
|--------|---------------|-----------|
| Calm   | Destabilising | Keeps price near the anchor-biased target instead of fundamental value. |
| Stress | Destabilising | Slows correction after shocks because the anchor remains sticky. |

Interaction with other agents: Opposes RationalUpdater and FundamentalAnalyst; can be amplified by MomentumTrader.

## Behavioral Framework

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale |
|---------------|------------|---------------|-----------|
| `price`       | Continuous | 1 tick        | Current tradable price |
| `fundamental` | Continuous | 1 tick        | True value used only through partial adjustment |
| `anchor`      | State      | persistent    | First observed reference price |

Does NOT use: `prev_price`, `momentum`, order-book depth, peer flow.

#### Core Behavioral Mechanism

1. Initialize `anchor` from the first valid market price.
2. Compute `target = anchor + alpha * (fundamental - anchor)`.
3. Compute `perceived_dev = (price - target) / target`.
4. Buy when price is sufficiently below the perceived target.
5. Sell when price is sufficiently above the perceived target.
6. Hold inside the no-trade band.
7. Keep `anchor` fixed unless the scenario explicitly resets the episode.

#### Action Space

| Aspect                | Specification |
|-----------------------|---------------|
| Order types allowed   | market, hold-no-op |
| Price level rule      | market order at current observed price |
| Order quantity rule   | `Q = min(base_position_size, abs(perceived_dev) * sizing_scale)` |
| Order lifetime        | 1 tick |
| Cancellation policy   | unfilled orders expire at end of tick; re-evaluate next tick |
| Inventory constraint  | no order may increase absolute inventory above `inventory_max` |
| Wealth / leverage cap | cash >= 0; no margin |
| Stop-loss / kill rule | none |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Trigger function:
  ```
  target = anchor + alpha * (F - anchor)
  perceived_dev = (P - target) / target
  buy if perceived_dev < -theta
  sell if perceived_dev > theta
  otherwise hold
  ```
- Sizing function:
  ```
  Q = sign(-perceived_dev) * min(base_position_size, abs(perceived_dev) * sizing_scale)
  ```
- State variables: `anchor` float initialized from first valid price; `position` float; `cash` float.
- State-update rule: `anchor` updates pre-decision only at cold start; `position` and `cash` update post-fill.
- Determinism contract: deterministic given signals, state, and parameters.

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `alpha` | adjustment fraction toward fundamental | 0.30 | Tversky & Kahneman (1974) |
| `theta` | perceived deviation threshold | 0.03 | Campbell & Sharpe (2009) |

#### Behavioral Properties

- Time horizon: medium, because the anchor persists across many ticks.
- Risk tolerance: medium, because orders are capped and thresholded.
- Information asymmetry: none; the bias is cognitive, not informational.
- Psychological profile: anchoring and insufficient adjustment.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `alpha` | float | 0.30 | [0, 1] | high | Fraction of the anchor-fundamental gap incorporated into target value. | Higher -> weaker anchoring and faster correction. | Tversky & Kahneman (1974) |
| `threshold` | float | 0.03 | [0, 1] | high | No-trade band around perceived target. | Higher -> fewer trades and more persistent mispricing. | Campbell & Sharpe (2009): 3% noise band cited in source scenario |
| `base_position_size` | float | 20.0 | > 0 | medium | Maximum order size. | Higher -> stronger price pressure from the biased target. | Standardised |
| `sizing_scale` | float | 1000.0 | > 0 | medium | Converts perceived deviation into quantity. | Higher -> more aggressive reaction to perceived cheapness or expensiveness. | Standardised |
| `inventory_max` | float | 200.0 | > 0 | low | Self-imposed inventory cap. | Higher -> longer sustained biased exposure. | Standardised |

## Population and Heterogeneity

| Aspect                         | Specification |
|--------------------------------|---------------|
| Default population size        | scenario-dependent |
| Parameter heterogeneity policy | shared point value or iid narrow draw around `alpha` |
| Heterogeneity per parameter    | `alpha -> Uniform(0.25, 0.40)`, `threshold -> Uniform(0.02, 0.04)` |
| Cross-agent correlation        | none |
| Identity persistence           | identical across episodes unless the scenario redraws parameters |

## Worked Numerical Examples

### Case 1 - Buy below perceived target
```text
Market state: P=98, F=100, anchor=105, alpha=0.30, theta=0.03.
Calculation: target=105+0.30*(100-105)=103.5; perceived_dev=(98-103.5)/103.5=-0.053.
Decision: buy min(20, 0.053*1000)=20 at P=98.
State update: position increases by 20; cash decreases by 1960.
```

### Case 2 - Sell above perceived target
```text
Market state: P=108, F=100, anchor=105.
Calculation: target=103.5; perceived_dev=(108-103.5)/103.5=0.043.
Decision: sell min(20, 0.043*1000)=20 at P=108.
State update: position decreases by 20; cash increases by 2160.
```

### Case 3 - Hold inside band
```text
Market state: P=102, F=100, anchor=105.
Calculation: target=103.5; perceived_dev=-0.0145, which is inside +/-0.03.
Decision: hold.
State update: no inventory or cash change; anchor remains 105.
```

### Edge Case - Cold start
```text
Market state: P=105, F=100, anchor unset.
Calculation: initialize anchor=105, then target=103.5 and perceived_dev=0.0145.
Decision: hold because the signal is inside the band.
State update: anchor becomes persistent state for later ticks.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `alpha` <- Tversky & Kahneman (1974).
- `threshold` <- Campbell & Sharpe (2009): 3% noise band cited in source scenario.

**Expected stylized facts** when this agent dominates the population:
- Sustained mispricing relative to fundamentals.
- Slow decay of price deviations after shocks.
- Positive short-run return persistence when combined with momentum traders.

**Sanity bounds (red flags during simulation)**:
- Agent trades directly toward `F` with no anchor effect.
- `anchor` changes every tick without a reset rule.
- Orders exceed self-imposed inventory or cash caps.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested |
|---------------|---------|-------------------|
| `no_anchor_bias` | `alpha = 1.0` | Removing anchoring collapses persistent mispricing. |
| `strong_anchor` | `alpha = 0.1` | Stronger anchoring increases deviation half-life. |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131. https://doi.org/10.1126/science.185.4157.1124 | Anchoring foundation |
| 2 | Campbell, S. D., & Sharpe, S. A. (2009). Anchoring bias in consensus forecasts and its effect on market prices. *Journal of Financial and Quantitative Analysis*, 44(2), 369-390. https://doi.org/10.1017/S0022109009090127 | Financial forecast anchoring |
| 3 | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185 | Reference-point psychology cited in source scenario |
| 4 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Conservatism and underreaction cited in source scenario |

## Design Provenance and Versioning

| Field       | Content |
|-------------|---------|
| Author      |  |
| Reviewed by |  |
| Created     | 2026-06-27 |
| Version     | 1.0.0 |
| Change log  | 1.0.0 - Created from AnchoringEffect Agent Design Summary row 4.1 |
| Status      | draft |
