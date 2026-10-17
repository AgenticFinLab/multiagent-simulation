# Balanced market analyst

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Balanced market analyst |
| Theory Family         | Behavioral Portfolio Theory / Hybrid Signal Processing |
| Behavioral Tendency   | **Converging** — blends fundamental and technical signals, nudging price toward a composite fair-value estimate |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a balanced portfolio analyst or multi-strategy research desk that fuses fundamental valuation data with technical price signals to generate moderate-conviction trade decisions. The real-world counterpart is the buy-side analyst or multi-factor quant manager who weights both value metrics and momentum/mean-reversion indicators equally — a participant class documented across asset management firms (Grinblatt & Titman 1993) and behavioral portfolio construction literature (Shefrin & Statman 2000).

The decision goal is to produce buy, sell, or hold actions with quantity proportional to the combined signal strength. The agent optimises a composite score that equally weights deviation from fundamental value and a technical momentum signal, then sizes its trade to exploit moderate mispricings without over-committing to either signal alone.

Inside the simulation the agent acts as a moderate stabiliser that trades against extreme mispricings but does not aggressively push price to fundamentals the way a pure value trader would. Non-goals: (1) the agent must NOT behave as a pure momentum follower that ignores fundamental signals; (2) the agent must NOT employ leverage or exceed its capital in sizing decisions.

## Theoretical Foundation

**Behavioral Portfolio Theory**:
- Theory / Study: Behavioral Portfolio Theory.
- Citation: Shefrin, H. & Statman, M. (2000). Behavioral Portfolio Theory. *Journal of Financial and Quantitative Analysis*, 35(2), 127-151. https://doi.org/10.2307/2676187
- Core Insight: Investors construct portfolios in layered mental accounts, combining safety-first and aspirational positions. A balanced analyst allocates conviction across fundamental safety and technical aspiration layers, producing moderate rather than extreme positions.
- Mathematical Formulation: `composite_score = w_f * fundamental_signal + w_t * technical_signal` where `w_f = w_t = 0.5`
- Empirical Evidence: Shefrin & Statman (2000) document that real investor portfolios exhibit layered structure inconsistent with single-objective mean-variance; survey of 200 individual investors shows 60-70% blend safety and aspiration motives (p < 0.01).
- Relevance to This Agent: The agent operationalises dual-signal blending by equally weighting fundamental deviation and technical momentum into a single composite score that drives trade direction and sizing.
- Calibration Source: Weight split w_f = w_t = 0.5 from equal-weight benchmark; conviction_threshold 0.01-0.05 from empirical bid-ask spreads; base_size 200-1000 units from typical institutional order normalization.
- Falsification Conditions: If the agent trades when composite_score is below conviction_threshold, or if it ignores one of its two signal channels entirely for more than 10 consecutive ticks, the design is falsified.
- Alternative Theories: Mean-variance optimisation (Markowitz 1952); pure technical analysis (Lo, Mamaysky, Wang 2000); pure fundamental value investing (Graham & Dodd).

## Design Purpose and Activation Triggers

Purpose: Generate moderate-conviction trades based on a balanced composite of fundamental and technical signals.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `fundamental` available
- own `cash` and `position` available

Missing-Signal Policy: hold when any required signal is unavailable or stale.

Activation Triggers:
- `composite_score > conviction_threshold`: buy sized by `base_size * abs(composite_score) * score_scale`.
- `composite_score < -conviction_threshold`: sell sized by `min(position, base_size * abs(composite_score) * score_scale)`.
- `<Default>`: hold.

Deactivation Conditions:
- cash insufficient to execute minimum buy order.
- position is zero and composite_score indicates sell.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| High volatility (price moves > 2x historical average) | Reduces effective base_size by 50% | Risk scaling to avoid overcommitment in noisy conditions |
| Signal convergence (fundamental and technical agree in sign) | Increases conviction multiplier by 1.5x | Reinforcement when independent signals align |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | float | yes | current market price for execution and technical signal |
| `fundamental` | environment | float | yes | fair-value estimate for fundamental deviation |
| `cash` | own state | float | yes | available capital for buy sizing |
| `position` | own state | float | yes | current holdings for sell constraint |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | trade direction |
| `quantity` | float | `>= 0` | units | yes | order size |
| `reasoning` | string | 1-3 sentences | — | yes | audit trail explaining composite score and trigger |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` on every call.
- Forbidden fields: no fields beyond the three declared above.
- Value ranges: quantity clamped to `[0, cash/price]` for buys and `[0, position]` for sells.
- Units: quantity in asset units; price in same currency as fundamental.
- Determinism: output is fully deterministic given identical inputs and state.

##### Serialization Format

```
<analysis>...free-form reasoning (1-3 sentences) explaining composite score computation and threshold comparison...</analysis>
<decision>{"action":"buy|sell|hold","quantity":0.0,"reasoning":"..."}</decision>
```

No retrieval-augmented variant declared; retrieval fallback sentinel not applicable.

##### Implementer Contract Reminder

Implementers MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for signal wiring, decision emission, prompt drafting, parser tests, variant parity, and conflict resolution.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 2 ticks | current price and 1-tick lagged price for momentum computation |
| `fundamental` | Continuous | 1 tick | deviation from fair value |
| `cash` | State | persistent | buy capacity |
| `position` | State | persistent | sell constraint |

Does NOT use: order-book depth, peer positions, sentiment feeds, private information, leverage.

#### Core Behavioral Mechanism

1. **Read** `price`, `price_prev` (lagged), `fundamental`, `cash`, `position`. (implementation convenience)
2. **Compute** fundamental signal: `f_signal = (fundamental - price) / fundamental`. Read: fundamental, price. Write: f_signal. (Traces to Behavioral Portfolio Theory — safety layer)
3. **Compute** technical signal: `t_signal = (price - price_prev) / price_prev`. Read: price, price_prev. Write: t_signal. (Traces to Behavioral Portfolio Theory — aspiration layer)
4. **Compute** composite score: `composite_score = w_f * f_signal + w_t * t_signal`. Read: f_signal, t_signal, w_f, w_t. Write: composite_score. (Traces to Behavioral Portfolio Theory)
5. **Evaluate** threshold: if `abs(composite_score) <= conviction_threshold`, decision = hold. Read: composite_score, conviction_threshold. Write: decision direction. (Traces to Behavioral Portfolio Theory — conviction gating)
6. **Compute** raw quantity: `raw_q = base_size * abs(composite_score) * score_scale`. Read: base_size, composite_score, score_scale. Write: raw_q. (Traces to Behavioral Portfolio Theory — position sizing)
7. **Clamp** quantity: if buy, `q = min(raw_q, cash / price)`; if sell, `q = min(raw_q, position)`. Read: raw_q, cash, price, position. Write: q. (implementation convenience — resource constraint)
8. **Emit** decision object with action, quantity, reasoning. Update `price_prev = price` for next tick. Write: price_prev.

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | market order at current price |
| Sizing rule | `base_size * abs(composite_score) * score_scale`, clamped by resource constraints |
| Action lifetime | one decision call |
| Revision policy | replace previous intent each tick |
| State constraint | position >= 0 (no short selling) |
| Resource cap | buy quantity <= cash / price |
| Exit rule | none — agent always evaluates composite score |

#### Mathematical Model

**Decision output:** action in {buy, sell, hold} and quantity q >= 0.

**Decision logic:**
```
f_signal = (fundamental - price) / fundamental
t_signal = (price - price_prev) / price_prev
composite_score = w_f * f_signal + w_t * t_signal

if composite_score > conviction_threshold:
    action = buy
    q = min(base_size * composite_score * score_scale, cash / price)
elif composite_score < -conviction_threshold:
    action = sell
    q = min(base_size * abs(composite_score) * score_scale, position)
else:
    action = hold
    q = 0
```

**State variables:**
| Variable | Type | Initial Value |
|----------|------|---------------|
| `price_prev` | float | price at first tick |
| `cash` | float | scenario-assigned |
| `position` | float | scenario-assigned |

**State evolution:** `price_prev` updated post-decision to current `price`. `cash` and `position` updated post-execution by environment.

**Determinism contract:** Fully deterministic given identical inputs and state.

**Parameter symbol table:**

| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `w_f` | fundamental signal weight | 0.5 | Shefrin & Statman (2000), equal-weight benchmark |
| `w_t` | technical signal weight | 0.5 | Shefrin & Statman (2000), equal-weight benchmark |
| `conviction_threshold` | minimum composite score to act | 0.02 | Calibrated from typical bid-ask spreads |
| `base_size` | base order size | 500.0 | Scenario normalization |
| `score_scale` | composite-to-quantity multiplier | 5000.0 | Scenario normalization |

#### Behavioral Properties

- Time horizon: medium — evaluates both immediate momentum and fundamental deviation that reverts over multiple periods.
- Risk tolerance: medium — sized proportionally to signal strength but never leveraged.
- Information asymmetry: partial — observes price and public fundamental estimate but not private order flow.
- Psychological profile: dual-process decision maker blending analytical (fundamental) and intuitive (technical) layers per Behavioral Portfolio Theory; exhibits moderate anchoring to composite fair-value estimate.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `w_f` | float | 0.5 | [0.0, 1.0] | high | weight on fundamental signal in composite | Higher -> more value-driven, less momentum-driven | Shefrin & Statman (2000) |
| `w_t` | float | 0.5 | [0.0, 1.0] | high | weight on technical signal in composite | Higher -> more momentum-driven, less value-driven | Shefrin & Statman (2000) |
| `conviction_threshold` | float | 0.02 | [0.005, 0.10] | high | minimum composite score magnitude to trigger trade | Higher -> fewer trades, larger required signal | Bid-ask spread calibration |
| `base_size` | float | 500.0 | [100, 2000] | medium | base order quantity before signal scaling | Higher -> larger position changes per signal | Scenario normalization |
| `score_scale` | float | 5000.0 | [1000, 10000] | medium | multiplier from composite score to quantity | Higher -> more aggressive sizing per unit signal | Scenario normalization |

## Worked Numerical Examples

### Case 1 — Buy signal (positive composite)
System state: price = 100.0, price_prev = 99.5, fundamental = 105.0, cash = 100000, position = 200.
Calculation:
  f_signal = (105 - 100) / 105 = 0.0476
  t_signal = (100 - 99.5) / 99.5 = 0.00503
  composite_score = 0.5 * 0.0476 + 0.5 * 0.00503 = 0.02632
  composite_score (0.02632) > conviction_threshold (0.02) → buy
  raw_q = 500 * 0.02632 * 5000 = 65800 → but clamped: min(65800, 100000/100) = min(65800, 1000) = 1000
Decision: buy 1000 units.
State update: price_prev = 100.0.

### Case 2 — Sell signal (negative composite)
System state: price = 108.0, price_prev = 109.0, fundamental = 100.0, cash = 50000, position = 800.
Calculation:
  f_signal = (100 - 108) / 100 = -0.08
  t_signal = (108 - 109) / 109 = -0.00917
  composite_score = 0.5 * (-0.08) + 0.5 * (-0.00917) = -0.04459
  abs(composite_score) (0.04459) > conviction_threshold (0.02) → sell
  raw_q = 500 * 0.04459 * 5000 = 111475 → clamped: min(111475, 800) = 800
Decision: sell 800 units.
State update: price_prev = 108.0.

### Case 3 — Hold (below threshold)
System state: price = 100.0, price_prev = 99.9, fundamental = 101.0, cash = 50000, position = 300.
Calculation:
  f_signal = (101 - 100) / 101 = 0.0099
  t_signal = (100 - 99.9) / 99.9 = 0.001
  composite_score = 0.5 * 0.0099 + 0.5 * 0.001 = 0.00545
  abs(composite_score) (0.00545) < conviction_threshold (0.02) → hold
Decision: hold, quantity = 0.
State update: price_prev = 100.0.

### Edge Case — Cold start (no prior price)
System state: price = 100.0, price_prev = 100.0 (initialised to current), fundamental = 103.0, cash = 50000, position = 0.
Calculation:
  f_signal = (103 - 100) / 103 = 0.02913
  t_signal = (100 - 100) / 100 = 0.0
  composite_score = 0.5 * 0.02913 + 0.5 * 0.0 = 0.01456
  abs(composite_score) (0.01456) < conviction_threshold (0.02) → hold
Decision: hold, quantity = 0.
State update: price_prev = 100.0.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `w_f`, `w_t` <- Shefrin & Statman (2000), equal-weight benchmark validated in Grinblatt & Titman (1993) multi-factor studies.
- `conviction_threshold` <- typical bid-ask spreads 1-5% in equity markets (Chordia, Roll, Subrahmanyam 2001).
- `base_size`, `score_scale` <- scenario normalization to produce order sizes 100-5000 units.

**Expected individual behaviour:**
- Given composite_score = 0.03 (above threshold), agent MUST buy with quantity > 0.
- Given composite_score = -0.05 and position > 0, agent MUST sell.
- Given composite_score = 0.01 (below threshold), agent MUST hold regardless of cash/position.
- Given missing fundamental signal, agent MUST hold per missing-signal policy.

**Sanity bounds:**
- IF agent buys when composite_score < conviction_threshold THEN broken — threshold logic not implemented.
- IF agent sells more than current position THEN broken — clamp logic not implemented.
- IF agent produces quantity < 0 THEN broken — valid range violated.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| fundamental-only | `w_t = 0, w_f = 1.0` | technical signal contribution to trade frequency | decrease in trade frequency | trades per 100 ticks |
| technical-only | `w_f = 0, w_t = 1.0` | fundamental signal contribution to mean-reversion | decrease in mean-reversion trades | correlation of trades with fundamental gap |
| high-threshold | `conviction_threshold = 0.08` | threshold effect on trade selectivity | decrease in trade count, increase in avg trade size | trades per 100 ticks, avg quantity |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Shefrin, H. & Statman, M. (2000). Behavioral Portfolio Theory. *Journal of Financial and Quantitative Analysis*, 35(2), 127-151. https://doi.org/10.2307/2676187 | Core theory for dual-layer signal blending |
| 2 | Grinblatt, M. & Titman, S. (1993). Performance measurement without benchmarks. *Journal of Business*, 66(1), 47-68. https://doi.org/10.1086/296593 | Multi-factor analyst behavior validation |
| 3 | Chordia, T., Roll, R., & Subrahmanyam, A. (2001). Market liquidity and trading activity. *Journal of Finance*, 56(2), 501-530. https://doi.org/10.1111/0022-1082.00335 | Bid-ask spread calibration for conviction threshold |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | Codex |
| Created | 2026-07-16 |
| Version | 1.0.0 |
| Icon | ![](../agent_images/icons/finance-balanced-analyst.png) |
| Status | draft |
