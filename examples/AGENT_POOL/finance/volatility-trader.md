# Volatility Trader

## Summary

| Field                 | Content                                                                                                                                                    |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Volatility-targeting regime trader                                                                                                                         |
| Theory Family         | GARCH / Volatility Targeting / Risk Parity                                                                                                                 |
| Behavioral Tendency   | **Context-dependent — sells in high-volatility regimes to reduce exposure, buys in low-volatility regimes to rebuild; provides direct vol-to-flow feedback** |
| Market Role           | **Stabilising (partial)** - dampens volatility spikes through mechanical de-risking and re-risks during calm periods                                       |
| Time Horizon          | short to medium                                                                                                                                            |
| Risk Tolerance        | moderate (volatility-managed)                                                                                                                              |
| Information Asymmetry | none (uses publicly observable volatility)                                                                                                                 |
| Determinism           | deterministic                                                                                                                                              |

## Definition and Goals

This agent models a volatility-targeting strategy that reduces exposure when realized volatility is high and increases exposure when volatility is low. The real-world counterpart is a risk-parity fund, volatility-managed portfolio, or institutional risk overlay mandate that mechanically adjusts exposure based on conditional variance.

The decision goal is to sell (reduce risk) when the volatility ratio exceeds a high threshold and buy (add risk) when it drops below a low threshold. Between thresholds, it holds. Order size is proportional to the magnitude of the threshold breach, creating graduated regime response.

In simulation this agent provides direct feedback from the volatility state to order flow. During vol regime transitions it acts as a partial dampener of spikes and a position rebuilder during calm periods. It contributes to the "volatility of volatility" feedback loop by creating mechanical demand that responds to the same state variable (volatility) that the GARCH process generates. Non-goals: it must not trade on price direction, fundamentals, or momentum signals.

## Theoretical Foundation

**ARCH/GARCH Conditional Heteroskedasticity**:
- Theory / Study: Time-varying volatility predictable from past squared returns.
- Citation: Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987-1007. https://doi.org/10.2307/1912773
- Core Insight: Volatility is persistent and predictable, justifying dynamic position sizing rules that condition on recent variance.
- Mathematical Formulation: `sigma^2(t) = omega + alpha * r^2(t-1) + beta * sigma^2(t-1)`.
- Empirical Evidence: ARCH effects are pervasive across equity, FX, and commodity markets.
- Relevance to This Agent: The agent reacts to the volatility state that the market coordinator generates via its GARCH(1,1) update, creating order-flow feedback from the same volatility process.
- Calibration Source: Engle (1982); Bollerslev (1986).
- Falsification Conditions: If the agent ignores volatility or trades based on price direction, it is misspecified.
- Alternative Theories: Stochastic volatility; realized variance estimators.

**Generalized ARCH**:
- Theory / Study: Extension of ARCH to include lagged conditional variance.
- Citation: Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307-327. https://doi.org/10.1016/0304-4076(86)90063-1
- Core Insight: GARCH(1,1) captures both shock response (alpha) and persistence (beta), providing the foundation for the volatility regime detection that the agent performs.
- Relevance to This Agent: The market coordinator broadcasts volatility computed via GARCH(1,1); the agent compares current volatility against its own moving average to identify regime departures.
- Calibration Source: Bollerslev (1986) parameter estimation methodology.

**Volatility-Managed Portfolios**:
- Theory / Study: Scaling exposure inversely with conditional volatility improves risk-adjusted returns.
- Citation: Moreira, A. & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611-1644. https://doi.org/10.1111/jofi.12575
- Core Insight: Expected returns do not increase proportionally with risk; volatility-targeting strategies exploit this by mechanically reducing exposure during high-vol episodes and rebuilding during calm.
- Mathematical Formulation: `w_t = sigma_target / sigma_t` (continuous); this agent implements a discrete threshold approximation.
- Empirical Evidence: Moreira & Muir show improved Sharpe ratios across multiple asset classes with volatility management.
- Relevance to This Agent: The agent implements a simplified discrete-threshold version of the Moreira-Muir mechanism, trading only when volatility departs sufficiently from its own average.
- Calibration Source: Moreira & Muir (2017), Table III threshold analysis.
- Falsification Conditions: If the agent buys during high-vol episodes or sells during low-vol episodes, the regime logic is inverted.
- Alternative Theories: Constant-mix strategies; buy-and-hold without vol adjustment.

## Design Purpose and Activation Triggers

Purpose: Inject volatility-responsive mechanical flows that dampen exposure in stress and rebuild in calm, contributing to vol-clustering dynamics via direct vol-to-order-flow feedback.

Call Frequency: every tick (once `vol_lookback` window is filled).

Prerequisite Signals:
- `volatility` available from market broadcast (`market_data["volatility"]`)
- `volatility_history` of length >= `vol_lookback` for moving average computation
- `price` available for order execution

Missing-Signal Policy: hold if volatility history is insufficient for regime detection. When `len(vol_history) < vol_lookback`, use current volatility as the average proxy (graceful degradation yielding vol_ratio = 1.0 = hold).

Activation Triggers:
- `vol_ratio > high_vol_threshold`: sell (reduce exposure), quantity proportional to excess.
- `vol_ratio < low_vol_threshold`: buy (add exposure), quantity proportional to deficit.
- `low_vol_threshold <= vol_ratio <= high_vol_threshold`: hold.
- `<Default>`: hold.

Deactivation Conditions:
- Insufficient volatility history for moving average computation.
- No position to sell (cannot short beyond zero).
- No cash to buy.
- Vol ratio in neutral zone between thresholds.

Behavioral Adaptation by Condition:
| Condition                | Behavioral change                                          | Mechanism                                                                     |
|--------------------------|------------------------------------------------------------|-------------------------------------------------------------------------------|
| Extreme high volatility  | Larger sell orders, proportional to vol_ratio excess       | `quantity = -base_position_size * (vol_ratio - 1.0)`, clamped at -20          |
| Extreme low volatility   | Larger buy orders, proportional to vol deficit             | `quantity = +base_position_size * (1.0 - vol_ratio)`, clamped at +20          |
| Volatility returning to normal | Orders reduce toward zero as ratio approaches thresholds | Proportional sizing; when vol_ratio just barely breaches, quantity is small  |

Environmental Dependencies: Requires `market_data` broadcast containing `volatility` field (GARCH-updated by market coordinator). Uses `HistoryBuffer` for volatility tracking via `BaseInvestor.perceive()`.

Market Contribution by Regime:
| Regime | Contribution             | Mechanism                                                            |
|--------|--------------------------|----------------------------------------------------------------------|
| Calm   | Position-building        | Low vol_ratio triggers buy orders, adding demand during quiet times. |
| Stress | Partial dampening        | High vol_ratio triggers sell orders, reducing net demand in spikes.  |

Interaction with other agents: Partially offsets TrendFollower amplification during stress (both respond to high-vol but in opposite directions). Complements Fundamentalist in stabilisation but uses volatility rather than price-value deviation. Does not interact directly with SlowAdapter (orthogonal signals).

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input                  | Source          | Type / Shape     | Required? | Notes                                                                                       |
|------------------------|-----------------|------------------|-----------|---------------------------------------------------------------------------------------------|
| `price`                | market_data     | `float`          | yes       | Current market price for order execution.                                                   |
| `volatility`           | market_data     | `float`          | yes       | Current GARCH-updated volatility from market coordinator.                                   |
| `volatility_history`   | agent state     | `HistoryBuffer`  | yes       | Rolling volatility history for regime detection MA.                                         |
| `round_num`            | observation     | `int`            | yes       | Current simulation round.                                                                   |
| `identity`, `round`    | round header    | `str`, `int`     | yes       | Scheduler metadata; identity naming rule per implement-simulation-skill/07-step3-config.md. |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum              | Unit     | Required?   | Meaning                                                                   |
|---------------|--------|---------------------------------|----------|-------------|---------------------------------------------------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}         | —        | yes         | Discrete action selected this call.                                       |
| `quantity`    | float  | `[0, 20]`                       | shares   | conditional | Order magnitude; 0 when `action = hold`.                                  |
| `price_level` | float  | `= price` (market order)        | currency | conditional | Execution reference; equals observed `price` for market orders.           |
| `reasoning`   | string | 1-3 sentences                   | —        | yes         | Audit trail explaining WHY the action was chosen.                         |

##### Content Constraints

- Required fields: every row marked `Required? = yes` in the Outputs table MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, 20]`; out-of-range values MUST be clamped by the implementer before emission.
- Units and sign conventions: `quantity` is unsigned; direction is carried by `action`. `price_level` uses the same currency unit as `price`.
- Determinism markers: the decision determinism class is declared in Summary as `deterministic`; no stochastic element exists in the decision logic.

##### Serialization Format

    <analysis>...free-form reasoning, 1-3 sentences...</analysis>
    <decision>{"action": "<one of the declared enum values>",
                "quantity": <float>,
                "price_level": <float>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template, but the tags and JSON schema MUST still be present.
4. Model-driven variants MUST include this exact tag+JSON requirement in the system or user prompt.
5. Retrieval-augmented variants MUST declare a fallback sentinel for `retrieved_knowledge` (e.g. `"(No relevant knowledge retrieved this round.)"`) and inject it verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and contract-versus-prose conflict resolution.

#### Decision Information Set

| Signal               | Type       | Memory Window        | Rationale                                           |
|----------------------|------------|----------------------|-----------------------------------------------------|
| `volatility`         | Continuous | 1 tick               | Current GARCH volatility for ratio computation      |
| `volatility_history` | Array      | `vol_lookback` ticks | Compute moving average for regime baseline          |
| `price`              | Continuous | 1 tick               | Execution reference for order pricing               |

Does NOT use: `fundamental`, `momentum`, `trend`, price direction, peer positions, cost basis.

#### Core Behavioral Mechanism

1. Retrieve volatility history from agent state (`HistoryBuffer`).
2. Check if sufficient history exists: `len(vol_history) >= vol_lookback`.
3. If insufficient history, set `avg_vol = volatility` (graceful degradation; vol_ratio = 1.0 -> hold).
4. Otherwise compute average volatility: `avg_vol = mean(vol_history[-vol_lookback:])`.
5. Compute volatility ratio: `vol_ratio = volatility / avg_vol` (guard: if avg_vol = 0, vol_ratio = 1.0).
6. Regime detection and order generation:
   - If `vol_ratio > high_vol_threshold`: quantity = `-base_position_size * (vol_ratio - 1.0)` (sell).
   - Elif `vol_ratio < low_vol_threshold`: quantity = `+base_position_size * (1.0 - vol_ratio)` (buy).
   - Else: quantity = 0 (hold).
7. Clamp quantity to `[-20, +20]`.
8. Set `bid_price = price` (market order approximation) if quantity != 0, else `bid_price = 0`.
9. Apply cash constraint for buys; apply position constraint for sells.
10. Execute trade: update `cash` and `position` in state.
11. Emit order payload with `bid_price`, `quantity`, and `strategy` fields.

#### Action Space

| Aspect                | Specification                                                                           |
|-----------------------|-----------------------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                                      |
| Price level rule      | market order at current price                                                           |
| Order quantity rule   | `Q = clamp(proportional_to_threshold_breach, -20, +20)` when regime threshold breached  |
| Order lifetime        | 1 tick (consumed by market coordinator in same round)                                   |
| Cancellation policy   | unfilled orders expire at end of round                                                  |
| Inventory constraint  | cannot sell below position = 0; cannot buy beyond cash / price                          |
| Wealth / leverage cap | cash >= 0; no margin; no short selling                                                  |
| Stop-loss / kill rule | none                                                                                    |

#### Mathematical Model

- Decision variable: signed trade quantity `Q*(t)`.
- Volatility moving average:
  ```
  avg_vol_t = (1/L) * sum(sigma_{t-L+1}, ..., sigma_t)
  ```
- Regime ratio:
  ```
  vol_ratio = sigma_t / avg_vol_t   (if avg_vol_t > 0, else 1.0)
  ```
- Sizing function with threshold gates:
  ```
  if vol_ratio > theta_high:
      Q*(t) = clamp(-Q_base * (vol_ratio - 1.0), -20, 0)   (sell)
  elif vol_ratio < theta_low:
      Q*(t) = clamp(+Q_base * (1.0 - vol_ratio), 0, +20)   (buy)
  else:
      Q*(t) = 0   (hold)
  ```
- State variables: `cash`; `position`; `price_history`; `volatility_history` (HistoryBuffer).
- State-update rule: update position and cash post-fill via `_execute_trade`.
- Determinism contract: deterministic given volatility history and parameters.

| Symbol       | Meaning                      | Default Value | Source                         |
|--------------|------------------------------|---------------|--------------------------------|
| `sigma_t`    | current volatility           | market-given  | Market GARCH(1,1) broadcast    |
| `L`          | vol lookback window          | 5             | Engle (1982)                   |
| `theta_high` | high vol threshold           | 1.5           | Moreira & Muir (2017)          |
| `theta_low`  | low vol threshold            | 0.7           | Moreira & Muir (2017)          |
| `Q_base`     | base position size           | 15.0          | Calibration                    |

#### Behavioral Properties

- Time horizon: short to medium, because it responds to current volatility regime relative to recent history.
- Risk tolerance: moderate (volatility-managed), because it mechanically reduces exposure when risk rises and rebuilds when risk falls.
- Information asymmetry: none, because volatility is publicly observable and broadcast by the market coordinator.
- Psychological profile: mechanical risk-overlay mandate with no directional view; pure regime-responding behavior without discretion or judgment; executes predetermined rules when thresholds breach.

## Parameters

| Parameter            | Type  | Default  | Valid Range | Sensitivity | Description                                                     | Impact                                                                  | Source                                            |
|----------------------|-------|----------|-------------|-------------|-----------------------------------------------------------------|-------------------------------------------------------------------------|---------------------------------------------------|
| `vol_lookback`       | int   | 5        | >= 2        | medium      | Window for computing volatility moving average.                 | Higher -> smoother baseline, fewer triggers, delayed regime detection.  | Engle (1982), 10.2307/1912773                     |
| `high_vol_threshold` | float | 1.5      | > 1.0       | high        | Vol ratio above which agent sells to de-risk.                   | Lower -> more frequent sell triggers, stronger dampening.               | Moreira & Muir (2017), 10.1111/jofi.12575         |
| `low_vol_threshold`  | float | 0.7      | (0, 1.0)    | high        | Vol ratio below which agent buys to re-risk.                    | Higher -> more frequent buy triggers, faster position rebuilding.       | Moreira & Muir (2017), 10.1111/jofi.12575         |
| `base_position_size` | float | 15.0     | > 0         | high        | Base scaling factor for proportional order sizing.              | Higher -> stronger market impact per threshold breach.                  | Calibrated for partial dampening                  |
| `initial_cash`       | float | 10000.0  | > 0         | low         | Starting cash endowment for the agent.                          | Higher -> can sustain more buy cycles during low-vol regimes.           | Normalization (scenario default)                  |
| `initial_position`   | int   | 0        | >= 0        | low         | Starting inventory of the risky asset.                          | Non-zero -> agent has immediate sell capacity in high-vol regime.       | Normalization (scenario default)                  |

## Population and Heterogeneity

| Aspect                         | Specification                                                  |
|--------------------------------|----------------------------------------------------------------|
| Default population size        | 1                                                              |
| Parameter heterogeneity policy | Single canonical instance                                      |
| Heterogeneity per parameter    | N/A at population = 1                                          |
| Cross-agent correlation        | N/A                                                            |
| Identity persistence           | Fixed parameters for episode duration                          |

Population rationale: One volatility trader is sufficient to demonstrate measurable stabilisation pressure during high-vol episodes without fully offsetting the trend-follower amplification. The single instance creates observable but not dominant vol-flow feedback, preserving the volatility-clustering phenomenon while adding the volatility-timing behavioral channel.

## Worked Numerical Examples

### Case 1 - High vol triggers proportional sell
```text
State: current_volatility=3.0, MA_vol(5)=1.8, price=100.0.
vol_ratio = 3.0 / 1.8 = 1.667.
Regime check: 1.667 > 1.5 (high_vol_threshold) -> sell regime.
quantity = -15.0 * (1.667 - 1.0) = -15.0 * 0.667 = -10.0.
Clamp check: -10.0 in [-20, 20] -> passes.
bid_price = 100.0.
Position constraint: position=20, max_sellable=20 -> abs(-10.0) <= 20, passes.
Decision: sell 10.0 units at price 100.0.
State update: cash += 1000.0, position -= 10.0.
```

### Case 2 - Low vol triggers proportional buy
```text
State: current_volatility=0.6, MA_vol(5)=1.2, price=95.0.
vol_ratio = 0.6 / 1.2 = 0.5.
Regime check: 0.5 < 0.7 (low_vol_threshold) -> buy regime.
quantity = +15.0 * (1.0 - 0.5) = +15.0 * 0.5 = +7.5.
Clamp check: 7.5 in [-20, 20] -> passes.
bid_price = 95.0.
Cash constraint: cash=10000, max_affordable=105.3 -> 7.5 <= 105.3, passes.
Decision: buy 7.5 units at price 95.0.
State update: cash -= 712.5, position += 7.5.
```

### Case 3 - Vol in normal range (hold)
```text
State: current_volatility=1.5, MA_vol(5)=1.3, price=100.0.
vol_ratio = 1.5 / 1.3 = 1.154.
Regime check: 0.7 <= 1.154 <= 1.5 -> neutral zone.
Decision: hold (quantity=0.0, bid_price=0.0).
State update: no change to cash or position.
```

### Case 4 - Extreme vol ratio with clamping
```text
State: current_volatility=5.0, MA_vol(5)=1.5, price=100.0.
vol_ratio = 5.0 / 1.5 = 3.333.
Regime check: 3.333 > 1.5 -> sell regime.
quantity_raw = -15.0 * (3.333 - 1.0) = -15.0 * 2.333 = -35.0.
Clamp: max(-20, -35.0) = -20.0.
bid_price = 100.0.
Position constraint: position=15, max_sellable=15 -> abs(-20.0) > 15.
Adjusted quantity = -15.0 (position constraint binds).
Decision: sell 15.0 units at price 100.0.
State update: cash += 1500.0, position -= 15.0 (position now 0).
```

### Edge Case - Insufficient volatility history
```text
State: tick=3, vol_lookback=5, current_volatility=2.0.
Only 3 volatility entries in history; condition len(vol_history) < vol_lookback.
Fallback: avg_vol = volatility = 2.0.
vol_ratio = 2.0 / 2.0 = 1.0.
Regime check: 0.7 <= 1.0 <= 1.5 -> neutral zone.
Decision: hold.
State update: no change.
```

### Edge Case - Zero average volatility guard
```text
State: avg_vol = 0.0 (degenerate case).
Guard: if avg_vol <= 0 then vol_ratio = 1.0.
Regime check: 0.7 <= 1.0 <= 1.5 -> neutral zone.
Decision: hold.
State update: no change.
```

## Validation and Calibration

**Calibration data sources** (per parameter, where applicable):
- `vol_lookback` <- Engle (1982) ARCH lag structure; short window for responsiveness to regime shifts.
- `high_vol_threshold` <- Moreira & Muir (2017) volatility-managed portfolio threshold analysis.
- `low_vol_threshold` <- Moreira & Muir (2017) re-risking threshold calibration.
- `base_position_size` <- calibrated for partial dampening; peak sell of 15 units at price_impact=0.05 produces 0.75-point price impact.

**Expected stylized facts** when this agent is present:
- Position reductions during volatility spikes (procyclical selling in stress episodes).
- Position rebuilding during calm periods (re-risking in low-vol regimes).
- Sell volume is positive during at least 30% of high-volatility rounds.
- Contributes to vol-of-vol dynamics and feedback between flows and the GARCH process.
- Maximum single-round price impact bounded at 0.05 * 20 = 1.0 point (meaningful but not dominant).

**Sanity bounds (red flags during simulation)**:
- IF agent buys during high-vol episodes (vol_ratio > high_vol_threshold) THEN the regime logic is inverted because high vol must trigger sells.
- IF agent sells during low-vol episodes (vol_ratio < low_vol_threshold) THEN the regime logic is inverted because low vol must trigger buys.
- IF trades fire before vol_lookback window is filled AND vol_ratio != 1.0 THEN the graceful degradation is broken because insufficient history must yield vol_ratio=1.0.
- IF position size exceeds 20 THEN the clamp logic is broken because all quantities must be bounded by [-20, +20].
- IF agent responds to price direction rather than volatility magnitude THEN the signal is contaminated because this agent must ignore price trends.

#### Ablation Hooks

| Ablation name        | Setting                            | Hypothesis tested                                                |
|----------------------|------------------------------------|------------------------------------------------------------------|
| `no_vol_trader`      | population = 0                     | Removing vol trader reduces procyclical dampening flow           |
| `tight_thresholds`   | high=1.1, low=0.9                  | Tighter bands increase trading frequency and dampening strength  |
| `wide_thresholds`    | high=2.0, low=0.5                  | Wider bands reduce intervention, letting vol clusters persist    |
| `large_position`     | `base_position_size = 30.0`        | Stronger vol-flow feedback may over-dampen clustering            |

## Academic References

| # | Citation                                                                                                                                                                                                      | Notes                                                             |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------|
| 1 | Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987-1007. https://doi.org/10.2307/1912773              | Foundation of ARCH; justifies dynamic vol-based position sizing   |
| 2 | Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307-327. https://doi.org/10.1016/0304-4076(86)90063-1                                    | GARCH(1,1) extension; market coordinator uses this for vol update |
| 3 | Moreira, A. & Muir, T. (2017). Volatility-managed portfolios. *Journal of Finance*, 72(4), 1611-1644. https://doi.org/10.1111/jofi.12575                                                                    | Volatility-targeting strategy; threshold calibration source       |

## Design Provenance and Versioning

| Field       | Content                      |
|-------------|------------------------------|
| Author      | polish-simulation-pipeline   |
| Created     | 2026-07-15                   |
| Version     | 2.0.0                        |
| Status      | canonical                    |
| Icon        | ![](../agent_images/icons/finance-volatility-trader.png) |
