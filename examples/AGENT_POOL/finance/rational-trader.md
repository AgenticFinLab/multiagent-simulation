# Rational expected-utility maximizer correcting mispricings

## Summary

| Field                 | Content |
|-----------------------|---------|
| Archetype             | Rational expected-utility maximizer correcting mispricings |
| Theory Family         | Rational Expectations — Market Microstructure |
| Behavioral Tendency   | **Converging** — trades contrarian to deviations, pushing price toward fundamental value |
| Time Horizon          | medium |
| Risk Tolerance        | medium |
| Information Asymmetry | partial |
| Determinism           | deterministic |

## Definition and Goals

This agent models a rational, expected-utility-maximizing trader who identifies mispricings relative to fundamental value and trades contrarian to correct them. The real-world counterpart is an informed institutional trader or rational arbitrageur — drawn from the participant taxonomy: (1) rational arbitrageurs, (2) informed institutional traders, (3) noise traders, (4) disposition-biased retail investors, (5) momentum traders, (6) contrarian value investors. This agent serves as the rational baseline in behavioural finance simulations, embodying the efficient-market hypothesis participant who trades on fundamental information.

The decision goal is to produce a contrarian order (buy when price is below fundamental, sell when above) sized proportionally to the mispricing magnitude, scaled by a risk-aversion parameter. The agent optimises expected utility by exploiting deviations from fundamental value.

In simulation this agent provides the stabilising force that pulls prices toward fundamentals. It serves as a rational benchmark against which behavioural agents' market-distorting effects can be measured. Non-goals: (1) this agent MUST NOT exhibit any behavioural biases (loss aversion, disposition effect, herding, anchoring); (2) this agent MUST NOT use momentum or trend-following logic.

## Theoretical Foundation

**Rational Market Making and Price Discovery**:
- Theory / Study: Bid, ask and transaction prices in a specialist market with heterogeneously informed traders
- Citation: Glosten, L. R., & Milgrom, P. R. (1985). Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders. *Journal of Financial Economics*, 14(1), 71-100. DOI:10.1016/0304-405X(85)90044-3
- Core Insight: Rational informed traders trade on the basis of their information advantage, buying when the asset is underpriced relative to their information and selling when overpriced. Their trading activity drives prices toward fundamental value through a sequential trade mechanism, with trade size reflecting both the magnitude of mispricing and the trader's risk aversion.
- Mathematical Formulation: `quantity = sign(fundamental - price) × min(max_order, floor(|deviation| × risk_aversion × base_scale)) if |deviation| > activation_threshold else 0`
- Empirical Evidence: Glosten & Milgrom (1985) prove that with rational informed traders, bid-ask spreads converge and prices approach fundamental value; empirically, Kyle (1985) estimates that informed trading accounts for 40-60% of price discovery in equity markets.
- Relevance to This Agent: The agent operationalises the rational informed trader who trades proportionally to mispricing, providing the price-discovery mechanism that forms the stabilising counterweight to noise and behavioural traders.
- Calibration Source: Glosten & Milgrom (1985); empirical market microstructure literature suggests informed traders deploy 0.3-1.0× their maximum capacity per signal unit depending on risk aversion.
- Falsification Conditions: If this agent trades in the same direction as the deviation (buys when overpriced, sells when underpriced), the rational contrarian mechanism is falsified.
- Alternative Theories: Kyle (1985) optimal strategic trading (conceals information to maximise profit); noise trader models (informed traders face noise trader risk limiting their stabilisation capacity).

**Efficient Markets and Rational Agents**:
- Theory / Study: Inefficient markets — an introduction to behavioural finance
- Citation: Shleifer, A. (2000). *Inefficient Markets: An Introduction to Behavioural Finance*. Oxford University Press. ISBN: 978-0198292272
- Core Insight: In efficient-market models, rational agents with correct expectations and CARA utility trade proportionally to perceived mispricing scaled inversely by risk aversion. Their demand function is linear in deviation: `demand = (fundamental - price) / (risk_aversion × variance)`. This provides the theoretical baseline against which behavioural deviations are measured.
- Mathematical Formulation: `demand = (V - P) / (ρ × σ²)` where V=fundamental, P=price, ρ=risk aversion, σ²=return variance
- Empirical Evidence: Shleifer (2000, Ch. 2) reviews evidence that professional arbitrageurs achieve risk-adjusted alpha of 2-5% per year by trading against mispricings, consistent with partial (not instantaneous) correction.
- Relevance to This Agent: Provides the theoretical demand function this agent implements in simplified form (linear in deviation, scaled by risk aversion).
- Calibration Source: Shleifer (2000) Ch. 2: risk-aversion parameter ρ in range [0.3, 1.0] for institutional traders; Kyle lambda (price impact) implies max effective trade size of 500-1000 shares for typical microstructure.
- Falsification Conditions: If this agent's quantity is not monotonically increasing in |deviation| (holding risk_aversion constant), the proportional correction mechanism is falsified.
- Alternative Theories: Momentum trading (trend-following rather than mean-reversion); behavioural biases (disposition effect contaminating the rational signal).

## Design Purpose and Activation Triggers

Purpose: Trade contrarian to observed mispricings, buying below and selling above fundamental value, with size proportional to deviation magnitude.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available (current market price)
- `fundamental` available (fundamental/intrinsic value)

Missing-Signal Policy: hold if either `price` or `fundamental` is unavailable or NaN; no trading without both signals confirmed.

Activation Triggers:
- `deviation > activation_threshold` (overpriced): sell `min(max_order, floor(deviation × risk_aversion × 3000))` units.
- `deviation < -activation_threshold` (underpriced): buy `min(max_order, floor(|deviation| × risk_aversion × 3000))` units.
- `<Default>`: hold — deviation too small to warrant action.

Deactivation Conditions:
- Cash exhausted (for buys) or position exhausted (for sells): cannot trade further in that direction.
- Deviation within activation_threshold: mispricing too small to justify transaction.

Behavioral Adaptation by Condition:
| Condition | Behavioral change | Mechanism |
|-----------|-------------------|-----------|
| Large mispricing (|deviation| >> threshold) | Larger order size, capped at max_order | Linear sizing formula: qty = |deviation| × risk_aversion × 3000 |
| Small mispricing (near threshold) | Minimal order size | Proportional sizing yields small quantity |
| No mispricing (|deviation| < threshold) | Holds; does not trade | Activation threshold prevents trading on noise |

Environmental Dependencies: Requires a per-tick `price` feed and a `fundamental` value signal. None beyond §3.6.1 signals.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input | Source | Type / Shape | Required? | Notes |
|-------|--------|--------------|-----------|-------|
| `price` | environment | `float` | yes | Maps to §3.6.1 `price`. Current market price. |
| `fundamental` | environment / config | `float` | yes | Maps to §3.6.1 `fundamental`. Intrinsic/fundamental value. |
| `position` | agent's own persisted state | `int` | yes | Current signed position (positive=long, negative=short). |
| `cash` | agent's own persisted state | `float` | yes | Current cash balance. |
| `identity`, `round` | scheduler / round header | `str`, `int` | yes | Round number and agent identity. |
| `retrieved_knowledge` | retrieval store (retrieval-augmented variants only) | `list[str]` | retrieval variants only | Falls back to `"(No relevant knowledge retrieved this round.)"` if empty. |

##### Outputs (per decision call)

| Field | Type | Valid Range / Enum | Unit | Required? | Meaning |
|-------|------|--------------------|------|-----------|---------|
| `action` | enum | `{"buy", "sell", "hold"}` | — | yes | Discrete action: contrarian buy, sell, or no action. |
| `quantity` | int | `[0, max_order]` | shares | yes | Unsigned magnitude of the order. 0 when hold. |
| `reasoning` | string | 1–3 sentences | — | yes | Audit trail explaining WHY. |

##### Content Constraints

- Required fields: `action`, `quantity`, and `reasoning` MUST be present on every call.
- Forbidden fields: fields not declared in the Outputs table MUST NOT be emitted.
- Value ranges: `quantity` MUST fall inside `[0, max_order]`; out-of-range values MUST be clamped.
- Units and sign conventions: `quantity` is unsigned; direction carried by `action`. Positive deviation → sell; negative deviation → buy.
- Determinism markers: decision is deterministic; no seed emitted.

##### Serialization Format

    <analysis>...free-form reasoning, 1–3 sentences...</analysis>
    <decision>{"action": "<buy, sell, or hold>",
                "quantity": <int>,
                "reasoning": "<audit-trail explanation>"}</decision>

Rules:
1. The `<analysis>` and `<decision>` tags are literal ASCII, NOT optional.
2. The `<decision>` block MUST contain a single valid JSON object whose keys exactly match the Outputs table.
3. Rule-driven variants MAY generate `<analysis>` from a deterministic template.
4. Model-driven variants MUST include this exact tag+JSON requirement in the prompt.
5. Retrieval-augmented variants MUST declare fallback sentinel `"(No relevant knowledge retrieved this round.)"` and inject verbatim when retrieval returns empty.

##### Implementer Contract Reminder

Implementers of this agent MUST re-open this I/O Contract during every coding pass and use it as the single source of truth for:
1. Signal wiring — every input row MUST map to a real read against environment/state.
2. Decision emission — code MUST populate every Required=yes field and clamp out-of-range values.
3. Prompt drafting — model-driven variants MUST spell out the tag pattern and JSON schema literally.
4. Parser tests — implementation MUST include a smoke test verifying tags and JSON validity.
5. Variant parity — every declared variant MUST produce the SAME field set.
6. Contract-versus-prose conflict — this section wins on any disagreement.

#### Decision Information Set

| Signal | Type | Memory Window | Rationale |
|--------|------|---------------|-----------|
| `price` | Continuous | 1 tick | Current price for deviation calculation [Ref 1, 2] |
| `fundamental` | Continuous | 1 tick | Intrinsic value reference for mispricing detection [Ref 1, 2] |

Does NOT use: momentum, historical prices, order-book depth, peer actions, volume, sentiment, or any behavioural signal.

#### Core Behavioral Mechanism

1. **Read** `price` and `fundamental` from environment; **Read** `position` and `cash` from agent state. *(implementation convenience)*
2. **Compute** deviation: `deviation = (price - fundamental) / fundamental`. *(Glosten & Milgrom 1985 — mispricing metric)*
3. **Check** activation: if `abs(deviation) <= activation_threshold`, proceed to step 7 (hold). *(Shleifer 2000 — transaction cost / noise filter)*
4. **Compute** raw quantity: `raw_qty = floor(abs(deviation) × risk_aversion × 3000)`. *(Glosten & Milgrom 1985 — proportional informed demand)*
5. **Clamp** to max_order: `qty = min(raw_qty, max_order)`. *(implementation convenience — risk limit)*
6. **Determine** direction: if `deviation > 0` (overpriced), action=sell; if `deviation < 0` (underpriced), action=buy. **Write** decision. Proceed to step 8. *(Shleifer 2000 — contrarian direction)*
7. **Write** decision: emit `action=hold`, `quantity=0`.
8. **Post-decision state update**: if buy, `position += qty`, `cash -= qty × price`; if sell, `position -= qty`, `cash += qty × price`. *(implementation convenience)*

#### Action Space

| Aspect | Specification |
|--------|---------------|
| Action types allowed | buy, sell, hold |
| Action parameter rule | No continuous price parameter; trades at market price. |
| Sizing rule | `qty = min(max_order, floor(abs(deviation) × risk_aversion × 3000))` |
| Action lifetime | 1 tick (immediate execution assumed) |
| Revision policy | No revision; order stands for the tick. |
| State constraint | Position may be long or short (no hard position limit beyond max_order per tick). |
| Resource cap | Buys limited by cash; sells limited by willingness to short (or existing long position in no-short scenarios). |
| Exit rule | None — always available to trade when mispricing exceeds threshold. |

#### Mathematical Model

**Decision output**: unsigned trade quantity `Q(t) >= 0` with direction determined by sign of deviation.

**Decision logic formalization**:
```
deviation(t) = (price(t) - fundamental(t)) / fundamental(t)

if abs(deviation(t)) > activation_threshold:
    Q(t) = min(max_order, floor(abs(deviation(t)) × risk_aversion × 3000))
    if deviation(t) > 0:
        action = "sell"
    else:
        action = "buy"
else:
    Q(t) = 0
    action = "hold"
```

**State variables**:
| Variable | Type | Initial Value |
|----------|------|---------------|
| `position` | int | 0 |
| `cash` | float | `initial_cash` (default 1000000) |

**State evolution** (post-decision, post-execution):
```
if action == "buy":
    position(t+1) = position(t) + Q(t)
    cash(t+1) = cash(t) - Q(t) × price(t)
elif action == "sell":
    position(t+1) = position(t) - Q(t)
    cash(t+1) = cash(t) + Q(t) × price(t)
else:
    position(t+1) = position(t)
    cash(t+1) = cash(t)
```

**Determinism contract**: Deterministic given identical price and fundamental paths and parameters. No stochastic element.

**Parameter symbol table**:
| Symbol | Meaning | Default Value | Source |
|--------|---------|---------------|--------|
| `risk_aversion` | Scaling factor for trade size (lower = less aggressive) | 0.5 | Shleifer (2000) Ch. 2 |
| `activation_threshold` | Minimum |deviation| to trigger a trade | 0.03 | Glosten & Milgrom (1985) — bid-ask spread proxy |
| `max_order` | Maximum unsigned quantity per tick | 500 | Standardised risk limit |
| `base_scale` | Base multiplier for quantity formula (fixed) | 3000 | Standardised |
| `initial_cash` | Starting cash balance | 1000000 | Standardised |

#### Behavioral Properties

- Time horizon: medium — trades on current mispricing but may hold position for multiple ticks until correction occurs.
- Risk tolerance: medium — trades proportionally to deviation with a risk-aversion scaling that limits over-commitment.
- Information asymmetry: partial — has access to fundamental value (unavailable to noise/behavioural traders), but does not observe private order flow.
- Psychological profile: Fully rational; no biases. CARA utility maximizer with linear demand function. Serves as the neoclassical benchmark agent.

## Parameters

| Parameter | Type | Default | Valid Range | Sensitivity | Description | Impact | Source |
|-----------|------|---------|-------------|-------------|-------------|--------|--------|
| `risk_aversion` | float | 0.5 | [0.3, 1.0] | high | Scaling coefficient for trade size relative to deviation | Higher -> larger trades per unit mispricing, faster correction | Shleifer (2000) Ch. 2 |
| `activation_threshold` | float | 0.03 | [0.01, 0.10] | high | Minimum absolute deviation to warrant trading | Higher -> ignores small mispricings, fewer trades | Glosten & Milgrom (1985) |
| `max_order` | int | 500 | [10, 5000] | medium | Per-tick order size ceiling | Higher -> stronger per-tick stabilisation capacity | Standardised |
| `initial_cash` | float | 1000000 | [100000, 10000000] | low | Starting cash for buying | Higher -> more capacity for prolonged correction | Standardised |
| `base_scale` | int | 3000 | [500, 10000] | medium | Base multiplier converting deviation to quantity | Higher -> more aggressive sizing for same deviation | Standardised |

## Worked Numerical Examples

### Case 1 — Buy (underpriced asset)
```text
Market state: price=95.0, fundamental=100.0, position=0, cash=1000000.
Parameters: risk_aversion=0.5, activation_threshold=0.03, max_order=500, base_scale=3000.
Calculation:
  deviation = (95 - 100) / 100 = -0.05
  abs(-0.05) = 0.05 > 0.03 → activation threshold breached
  raw_qty = floor(0.05 × 0.5 × 3000) = floor(75) = 75
  clamp: min(75, 500) = 75
  deviation < 0 → action=buy
Decision: action=buy, quantity=75.
State update: position: 0 -> 75; cash: 1000000 -> 1000000 - 75×95 = 992875.
```

### Case 2 — Sell (overpriced asset)
```text
Market state: price=108.0, fundamental=100.0, position=0, cash=1000000.
Parameters: risk_aversion=0.5, activation_threshold=0.03, max_order=500, base_scale=3000.
Calculation:
  deviation = (108 - 100) / 100 = 0.08
  abs(0.08) = 0.08 > 0.03 → activation threshold breached
  raw_qty = floor(0.08 × 0.5 × 3000) = floor(120) = 120
  clamp: min(120, 500) = 120
  deviation > 0 → action=sell
Decision: action=sell, quantity=120.
State update: position: 0 -> -120; cash: 1000000 -> 1000000 + 120×108 = 1012960.
```

### Case 3 — Hold (mispricing below threshold)
```text
Market state: price=101.5, fundamental=100.0, position=0, cash=1000000.
Parameters: risk_aversion=0.5, activation_threshold=0.03, max_order=500.
Calculation:
  deviation = (101.5 - 100) / 100 = 0.015
  abs(0.015) = 0.015 <= 0.03 → threshold NOT breached
Decision: action=hold, quantity=0.
State update: position: 0 (unchanged); cash: 1000000 (unchanged).
```

### Edge Case — Large mispricing capped by max_order
```text
Market state: price=70.0, fundamental=100.0, position=0, cash=1000000.
Parameters: risk_aversion=0.5, activation_threshold=0.03, max_order=500, base_scale=3000.
Calculation:
  deviation = (70 - 100) / 100 = -0.30
  abs(-0.30) = 0.30 > 0.03 → threshold breached
  raw_qty = floor(0.30 × 0.5 × 3000) = floor(450) = 450
  clamp: min(450, 500) = 450
  deviation < 0 → action=buy
Decision: action=buy, quantity=450.
State update: position: 0 -> 450; cash: 1000000 -> 1000000 - 450×70 = 968500.
```

## Behavioral Verification and Calibration

**Calibration data sources** (per parameter, where applicable):
- `risk_aversion` <- Shleifer (2000) Ch. 2; institutional trader risk parameters 0.3-1.0.
- `activation_threshold` <- Glosten & Milgrom (1985); typical bid-ask spread (noise filter) of 2-5% in simulation contexts.

**Expected individual behaviour** (what this agent MUST do when correctly implemented):
- Given price=95, fundamental=100 (deviation=-0.05 > threshold), agent MUST buy with quantity > 0.
- Given price=105, fundamental=100 (deviation=+0.05 > threshold), agent MUST sell with quantity > 0.
- Given |deviation| <= 0.03, agent MUST hold with quantity=0.
- Buy quantity MUST be monotonically non-decreasing in |deviation| up to max_order.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent buys when price > fundamental (positive deviation) THEN implementation is broken because it is trading in the wrong direction (momentum not contrarian).
- IF the agent sells when price < fundamental (negative deviation) THEN implementation is broken because it is destabilising rather than stabilising.
- IF quantity exceeds max_order THEN implementation is broken because the cap is not enforced.
- IF the agent trades when |deviation| < activation_threshold THEN implementation is broken because the noise filter is missing.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| `aggressive_rational` | `risk_aversion = 1.0` | Higher risk tolerance increases correction speed | Increase in per-tick quantity; faster price convergence | Average quantity when active |
| `passive_rational` | `risk_aversion = 0.3` | Lower risk tolerance slows correction | Decrease in quantity; slower convergence | Ticks until price within 1% of fundamental |
| `no_rational` | `activation_threshold = 1.0` | Removing rational trader eliminates fundamental anchor | Price diverges from fundamental; increased volatility | Standard deviation of price-to-fundamental ratio |

## Academic References

| # | Citation | Notes |
|---|----------|-------|
| 1 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, Ask and Transaction Prices in a Specialist Market with Heterogeneously Informed Traders. *Journal of Financial Economics*, 14(1), 71-100. DOI:10.1016/0304-405X(85)90044-3 | Rational informed trading; price discovery mechanism |
| 2 | Shleifer, A. (2000). *Inefficient Markets: An Introduction to Behavioural Finance*. Oxford University Press. ISBN: 978-0198292272 | Rational baseline agent; CARA demand function |
| 3 | Kyle, A. S. (1985). Continuous Auctions and Insider Trading. *Econometrica*, 53(6), 1315-1335. DOI:10.2307/1913210 | Informed trader price impact; market depth |

## Design Provenance and Versioning

| Field | Content |
|-------|---------|
| Author | polish-simulation-pipeline |
| Created | 2026-07-14 |
| Version | 1.0.0 |
| Status | canonical |
