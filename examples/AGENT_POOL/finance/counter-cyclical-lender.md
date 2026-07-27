# Counter-cyclical credit lender

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Counter-cyclical credit lender |
| Theory Family         | Macroprudential Policy / Counter-cyclical Buffering |
| Behavioral Tendency   | **Converging** — extends credit during downturns and tightens during booms, stabilising the credit cycle |
| Time Horizon          | long |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a policy-oriented lender — such as a development bank, state-backed credit institution, or counter-cyclical buffer fund — that deliberately extends credit during economic downturns and tightens lending during booms. The real-world counterpart is the counter-cyclical lending institution advocated by the Bank for International Settlements (BIS) macroprudential framework, documented in Borio (2014) and the Basel III counter-cyclical capital buffer regulations.

The decision goal is to buy assets (extend credit / provide liquidity) when the market is below its trend (negative credit gap) and sell (tighten/withdraw credit) when the market is above trend (positive credit gap). The agent computes a credit gap signal as the deviation of price from a smoothed trend and sizes its intervention proportionally to the gap magnitude, acting as a buffer that leans against the cycle.

Inside the simulation this agent acts as a powerful stabilising mechanism that dampens boom-bust credit cycles by providing counter-cyclical liquidity. During stress it injects capital that prevents fire-sale cascades; during exuberance it withdraws capital that constrains bubble formation. Non-goals: (1) the agent must NOT follow the cycle pro-cyclically (it must never lend more in booms and less in busts); (2) the agent must NOT pursue profit maximisation — its objective is cycle stabilisation, not return optimisation.

## Theoretical Foundation

**Counter-cyclical macroprudential policy (Borio 2014)**:
- Theory / Study: The financial cycle and macroeconomics.
- Citation: Borio, C. (2014). The financial cycle and macroeconomics: What have we learnt? *Journal of Banking and Finance*, 45, 182-198. https://doi.org/10.1016/j.jbankfin.2013.07.031
- Core Insight: Financial cycles are longer and more pronounced than business cycles. Pro-cyclical credit expansion amplifies booms and deepens busts. Counter-cyclical policy — building buffers in good times and releasing them in bad — can dampen these cycles. The credit-to-GDP gap is the canonical indicator for timing counter-cyclical action.
- Mathematical Formulation: `credit_gap = (price - trend) / trend; if credit_gap < -gap_threshold then buy (extend credit); if credit_gap > gap_threshold then sell (tighten credit)`
- Empirical Evidence: Borio (2014) shows credit-to-GDP gap signals banking crises with 60-70% accuracy 2-3 years ahead (N=34 countries, 1980-2012, AUC = 0.85). Drehmann & Tsatsaronis (2014) validate the indicator with Basel III calibration data.
- Relevance to This Agent: The agent operationalises counter-cyclical policy by computing a trend-deviation gap and intervening against the cycle — buying below trend and selling above trend.
- Calibration Source: gap_threshold 0.02-0.10 from Basel III credit-to-GDP gap threshold (2%); base_size 500-2000 from BIS buffer release calibration; smoothing_factor 0.05-0.20 for trend computation.
- Falsification Conditions: If the agent buys when credit_gap > gap_threshold (pro-cyclical lending in boom) or sells when credit_gap < -gap_threshold (withdrawing in bust), the counter-cyclical mechanism is falsified.
- Alternative Theories: Time-varying capital requirements (Basel III CCyB); Minsky financial instability hypothesis; Brunnermeier & Sannikov (2014) I-theory of money.

## Design Purpose and Activation Triggers

Purpose: Extend credit during downturns and tighten during booms by trading against the credit-gap signal.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- own `cash` and `position` available

Missing-Signal Policy: hold when price is unavailable; retain current trend estimate.

Activation Triggers:
- `credit_gap < -gap_threshold`: buy (extend credit) sized by `base_size * abs(credit_gap) * gap_scale`.
- `credit_gap > gap_threshold`: sell (tighten credit) sized by `min(position, base_size * credit_gap * gap_scale)`.
- `<Default>`: hold.

Deactivation Conditions:
- cash insufficient for minimum credit extension during downturn.
- position is zero and credit_gap > gap_threshold (nothing to tighten).

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Deep downturn (credit_gap < -2x gap_threshold) | Increases lending intensity by crisis_boost factor | Emergency credit provision per BIS crisis-response framework |
| Sustained boom (credit_gap > 2x gap_threshold for > 10 ticks) | Increases tightening rate to brake bubble formation | Escalating macroprudential tightening |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price (proxy for credit conditions) |
| `cash` | own state | float | yes | available capital for credit extension |
| `position` | own state | float | yes | current credit outstanding (for tightening) |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | credit direction (buy = extend, sell = tighten) |
| `quantity` | float | `>= 0` | units | yes | credit size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining credit gap and cycle position |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: buy quantity clamped to cash / price; sell quantity clamped to position.
- Units: quantity in credit units; price in market currency.
- Determinism: fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining trend computation, credit gap, and counter-cyclical action...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | current price for gap computation and trend update |
| `cash` | State | persistent | credit extension capacity |
| `position` | State | persistent | credit outstanding for tightening |
| `trend` | State | persistent | exponentially smoothed price trend |

Does NOT use: private credit data, individual borrower quality, peer lending volumes, sentiment indicators.

#### Core Behavioral Mechanism

1. **Read** `price`, `cash`, `position`, `trend`. (implementation convenience)
2. **Update** trend: `trend_new = (1 - smoothing_factor) * trend + smoothing_factor * price`. Read: trend, smoothing_factor, price. Write: trend. (Traces to Borio 2014 — EMA trend for credit gap)
3. **Compute** credit gap: `credit_gap = (price - trend) / trend`. Read: price, trend. Write: credit_gap. (Traces to Borio 2014 — credit-to-GDP gap analog)
4. **Evaluate** buy condition: if `credit_gap < -gap_threshold`, extend credit. Read: credit_gap, gap_threshold. Write: direction. (Traces to Borio 2014 — counter-cyclical lending in bust)
5. **Evaluate** sell condition: if `credit_gap > gap_threshold`, tighten credit. Read: credit_gap, gap_threshold. Write: direction. (Traces to Borio 2014 — counter-cyclical tightening in boom)
6. **Compute** quantity: buy: `q = min(base_size * abs(credit_gap) * gap_scale, cash / price)`; sell: `q = min(base_size * credit_gap * gap_scale, position)`. Read: base_size, credit_gap, gap_scale, cash, price, position. Write: q. (Traces to Borio 2014 — proportional intervention)
7. **Emit** decision object with action, quantity, reasoning.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `base_size * abs(credit_gap) * gap_scale`, clamped by cash or position |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0 (cannot go short on credit) |
| Resource cap | buy quantity <= cash / price; sell quantity <= position |
| Exit rule | none — continuously evaluates cycle position |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
trend = (1 - smoothing_factor) * trend + smoothing_factor * price
credit_gap = (price - trend) / trend

if credit_gap < -gap_threshold:
    action = buy
    q = min(base_size * abs(credit_gap) * gap_scale, cash / price)
elif credit_gap > gap_threshold:
    action = sell
    q = min(base_size * credit_gap * gap_scale, position)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `trend` | float | price at first tick |
| `cash` | float | scenario-assigned |
| `position` | float | scenario-assigned |

**State evolution:** `trend` updated pre-decision via EMA. `cash` and `position` updated post-execution by environment.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `smoothing_factor` | EMA weight for trend update | 0.10 | Borio (2014) credit cycle periodicity |
| `gap_threshold` | minimum credit gap to trigger action | 0.03 | Basel III CCyB 2% threshold (scaled) |
| `base_size` | base credit quantity | 600.0 | Scenario normalization |
| `gap_scale` | gap-to-quantity multiplier | 8000.0 | Scenario normalization |

#### Behavioral Properties

- Time horizon: long — counter-cyclical policy operates over full credit cycles (multiple years in real time).
- Risk tolerance: medium — extends credit into downturns (accepting default risk) but sizes conservatively.
- Information asymmetry: partial — observes market price as cycle proxy but not individual borrower quality.
- Psychological profile: rational policy-implementing agent; no cognitive biases; rule-following counter-cyclical mandate per BIS/Basel III framework.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `smoothing_factor` | float | 0.10 | [0.02, 0.30] | high | EMA weight for trend computation | Higher -> trend responds faster, smaller gaps | Borio (2014) cycle periodicity |
| `gap_threshold` | float | 0.03 | [0.01, 0.10] | high | minimum credit gap magnitude to act | Higher -> fewer interventions, requires larger deviation | Basel III CCyB calibration |
| `base_size` | float | 600.0 | [200, 1500] | medium | base credit quantity per intervention | Higher -> larger counter-cyclical impact | Scenario normalization |
| `gap_scale` | float | 8000.0 | [3000, 15000] | medium | gap-to-quantity multiplier | Higher -> more aggressive response per unit gap | Scenario normalization |

## Worked Numerical Examples

### Case 1 — Buy (extend credit in downturn)
System state: price = 92.0, trend = 100.0 (before update), cash = 300000, position = 500.
Calculation:
  trend_new = (1 - 0.10) * 100.0 + 0.10 * 92.0 = 90.0 + 9.2 = 99.2
  credit_gap = (92 - 99.2) / 99.2 = -0.0726
  credit_gap (-0.0726) < -gap_threshold (-0.03) → buy
  raw_q = 600 * 0.0726 * 8000 = 348480 → clamped: min(348480, 300000/92) = min(348480, 3260.9) = 3260.9
Decision: buy 3260.9 units (extend credit).
State update: trend = 99.2.

### Case 2 — Sell (tighten credit in boom)
System state: price = 115.0, trend = 100.0 (before update), cash = 200000, position = 2000.
Calculation:
  trend_new = 0.9 * 100.0 + 0.1 * 115.0 = 90.0 + 11.5 = 101.5
  credit_gap = (115 - 101.5) / 101.5 = 0.1330
  credit_gap (0.1330) > gap_threshold (0.03) → sell
  raw_q = 600 * 0.1330 * 8000 = 638400 → clamped: min(638400, 2000) = 2000
Decision: sell 2000 units (tighten credit).
State update: trend = 101.5.

### Case 3 — Hold (gap within threshold)
System state: price = 101.0, trend = 100.0 (before update), cash = 250000, position = 800.
Calculation:
  trend_new = 0.9 * 100.0 + 0.1 * 101.0 = 90.0 + 10.1 = 100.1
  credit_gap = (101 - 100.1) / 100.1 = 0.009
  abs(credit_gap) (0.009) < gap_threshold (0.03) → hold
Decision: hold, quantity = 0.
State update: trend = 100.1.

### Edge Case — Cash exhausted during deep downturn
System state: price = 70.0, trend = 100.0 (before update), cash = 500, position = 1000.
Calculation:
  trend_new = 0.9 * 100.0 + 0.1 * 70.0 = 90.0 + 7.0 = 97.0
  credit_gap = (70 - 97) / 97 = -0.2784
  credit_gap (-0.2784) < -gap_threshold (-0.03) → buy
  raw_q = 600 * 0.2784 * 8000 = 1336320 → clamped: min(1336320, 500/70) = min(1336320, 7.14) = 7.14
Decision: buy 7.14 units (cash nearly exhausted, minimal intervention possible).
State update: trend = 97.0.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `smoothing_factor` <- Borio (2014): financial cycles 15-20 years; EMA with alpha=0.10 approximates multi-year trend in tick-based simulation.
- `gap_threshold` <- Basel III CCyB activation at 2% credit-to-GDP gap; scaled to 3% for simulation price units.
- `base_size`, `gap_scale` <- scenario normalization to produce counter-cyclical flows of 1-5% of total market volume.

**Expected individual behaviour:**
- Given credit_gap = -0.05 (below -threshold), agent MUST buy (extend credit).
- Given credit_gap = 0.08 (above threshold), agent MUST sell (tighten) if position > 0.
- Given credit_gap = 0.01 (within threshold), agent MUST hold.
- Given missing price, agent MUST hold per missing-signal policy.

**Sanity bounds:**
- IF agent sells when credit_gap < -gap_threshold THEN broken — counter-cyclical logic inverted (pro-cyclical).
- IF agent buys when credit_gap > gap_threshold THEN broken — pro-cyclical behavior.
- IF agent produces negative quantity THEN broken — valid range violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| fast-trend | `smoothing_factor = 0.30` | faster trend reduces measured gap | decrease in average abs(credit_gap) | mean abs(credit_gap) per 100 ticks |
| tight-threshold | `gap_threshold = 0.01` | lower threshold increases intervention frequency | increase in trade count | trades per 100 ticks |
| reduced-scale | `gap_scale = 3000` | lower scale reduces intervention magnitude | decrease in average trade size | mean quantity per trade |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Borio, C. (2014). The financial cycle and macroeconomics: What have we learnt? *Journal of Banking and Finance*, 45, 182-198. https://doi.org/10.1016/j.jbankfin.2013.07.031 | Core counter-cyclical policy theory |
| 2 | Drehmann, M. & Tsatsaronis, K. (2014). The credit-to-GDP gap and countercyclical capital buffers. *BIS Quarterly Review*, March 2014. | Basel III CCyB calibration |
| 3 | Basel Committee on Banking Supervision (2010). Guidance for national authorities operating the countercyclical capital buffer. Bank for International Settlements. | Regulatory framework |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-counter-cyclical-lender.png) |
| Status | draft |
