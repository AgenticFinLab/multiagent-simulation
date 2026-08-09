# Passive index holder

## Summary

| Field                 | Content                                                                          |
|-----------------------|----------------------------------------------------------------------------------|
| Archetype             | Passive index holder                                                             |
| Theory Family         | Modern Portfolio Theory / Efficient Markets                                      |
| Behavioral Tendency   | **Converging** — maintains stable demand that anchors prices toward long-run equilibrium |
| Time Horizon          | long                                                                             |
| Risk Tolerance        | medium                                                                           |
| Information Asymmetry | none                                                                             |
| Determinism           | deterministic                                                                    |

## Definition and Goals

This agent models a buy-and-hold investor tracking a broad market index with near-zero turnover. The real-world counterparts include index mutual fund managers (e.g. Vanguard Total Stock Market), exchange-traded fund (ETF) authorized participants, and pension funds with passive mandates. These participants collectively hold over 50% of US equity market capitalization as of 2023 and generate minimal active order flow.

The decision goal is to establish and maintain a fixed target position, purchasing shares only upon initialization or when periodic cash contributions arrive. The agent emits buy or hold decisions; it does not sell under any market condition. The optimization criterion is minimizing tracking error relative to a target position level — not maximizing risk-adjusted return.

Inside the simulation this agent provides stable background demand and reduces effective free-float. It represents the inelastic demand documented by Gabaix and Koijen (2021). **Non-goals:** (1) The agent must NOT react to price movements by trading — it does not rebalance, sell on drawdowns, or take profits. (2) The agent must NOT use any fundamental value estimate, momentum signal, or technical indicator. (3) The agent must NOT provide two-sided liquidity (it is not a market maker).

## Theoretical Foundation

**Efficient Market Hypothesis and Passive Investing**:
- Theory / Study: The arithmetic of active management.
- Citation: Sharpe, W. F. (1991). The arithmetic of active management. *Financial Analysts Journal*, 47(1), 7-9. https://doi.org/10.2469/faj.v47.n1.7
- Core Insight: Before costs, the return on the average actively managed dollar equals the return on the average passively managed dollar. After costs, active management underperforms passive on average. This justifies a strategy of simply holding the market portfolio indefinitely.
- Mathematical Formulation: `position_target = initial_position + contribution_rate * floor(tick / contribution_interval)` — the agent's target holding grows only through exogenous cash inflows, never through active trading decisions.
- Empirical Evidence: Sharpe (1991) proves mathematically that net-of-cost active returns must underperform passive returns by exactly the cost differential. Fama & French (2010) confirm: only 2-3% of US equity mutual funds beat their benchmark after fees (alpha < 0 for 97% of funds, t-stat > 2.0).
- Relevance to This Agent: The agent operationalises the optimal passive strategy — hold the target position, add only on inflows, never trade reactively.
- Calibration Source: Sharpe (1991) arithmetic proof; Fama & French (2010) Table 4 — average fund alpha = -0.81% annually. Contribution rate calibrated to typical 401(k) monthly contribution scaled to simulation tick frequency.
- Falsification Conditions: If the agent executes any sell order or any buy order not attributable to initialization or scheduled contribution, the passive mandate is falsified.
- Alternative Theories: Strategic asset allocation with rebalancing (Perold & Sharpe 1988); lifecycle investing (Ayres & Nalebuff 2010).

**Inelastic Markets Hypothesis**:
- Theory / Study: In search of the origins of financial fluctuations: The inelastic markets hypothesis.
- Citation: Gabaix, X. & Koijen, R. S. J. (2021). In search of the origins of financial fluctuations: The inelastic markets hypothesis. *Econometrica*, 90(4), 1369-1420. https://doi.org/10.3982/ECTA17734
- Core Insight: A large share of equity is held by passive/inelastic investors who do not adjust holdings in response to price changes. This means that a relatively small amount of active flow has an outsized price impact (multiplier of approximately 5x).
- Mathematical Formulation: `dP/P = (1/elasticity) * (dFlow/MarketCap)` where elasticity is near zero for passive holders, implying their presence amplifies the price impact of active traders' flow.
- Empirical Evidence: Gabaix & Koijen (2021) estimate aggregate market elasticity of ~0.2 using quarterly flow data from 1993-2019, implying $1 of inflow moves market cap by ~$5. Passive fund share grew from 3% (1995) to 45% (2020).
- Relevance to This Agent: This agent embodies the "inelastic" holder class whose non-response to prices creates the low-elasticity environment that amplifies other agents' price impact.
- Calibration Source: Gabaix & Koijen (2021) Table 1 — passive share 40-50% of market cap; elasticity 0.15-0.25.
- Falsification Conditions: If the agent's holdings change by more than `contribution_rate` per contribution interval (excluding initialization), its inelastic nature is falsified.
- Alternative Theories: Constant-mix rebalancing (contradicts inelasticity); target-date lifecycle (introduces time-varying allocation).

## Design Purpose and Activation Triggers

Purpose: Maintain a fixed long position with near-zero turnover, representing passive institutional demand that does not respond to price signals.

Call Frequency: every-tick.

Prerequisite Signals (must be available for the agent to evaluate):
- `price` available
- `position` available (own state)
- `cash` available (own state)
- `tick` or round counter available

Missing-Signal Policy: hold when any required signal is unavailable.

Activation Triggers:
- Initialization tick (tick = 0 and position < initial_position): buy `initial_position` shares.
- Contribution tick (tick mod contribution_interval == 0 and contribution_rate > 0): buy `contribution_rate` shares.
- `<Default>`: hold.

Deactivation Conditions:
- Cash insufficient for scheduled purchase: skip contribution, resume when cash available.
- Position already at or above target: hold indefinitely.

Behavioral Adaptation by Condition:
| Condition            | Behavioral change                  | Mechanism                           |
|----------------------|------------------------------------|-------------------------------------|
| Market crash         | No change — continues to hold      | Passive mandate ignores price level |
| Market rally         | No change — continues to hold      | Passive mandate ignores price level |
| Cash inflow arrives  | Executes scheduled purchase        | Contribution rule fires             |

Environmental Dependencies: none beyond declared signals and own state.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input      | Source      | Type / Shape | Required? | Notes                        |
|------------|-------------|--------------|-----------|------------------------------|
| `price`    | environment | float        | yes       | execution reference price    |
| `position` | own state   | float        | yes       | current shares held          |
| `cash`     | own state   | float        | yes       | available capital            |
| `round`    | scheduler   | int          | yes       | tick counter for contribution logic |

##### Outputs (per decision call)

| Field       | Type   | Valid Range / Enum        | Unit   | Required? | Meaning                      |
|-------------|--------|---------------------------|--------|-----------|------------------------------|
| `action`    | enum   | `{"buy", "hold"}`         | —      | yes       | order direction (never sell) |
| `quantity`  | float  | `>= 0`                   | shares | yes       | number of shares to buy      |
| `reasoning` | string | 1-3 sentences             | —      | yes       | audit trail                  |

##### Content Constraints

- Required fields: `action`, `quantity`, `reasoning` must be present on every call.
- Forbidden fields: no fields beyond the three declared. Agent MUST NOT emit `"sell"` action.
- Value ranges: `quantity` clamped to `[0, cash / price]`.
- Units: quantity in shares; price in environment currency units.
- Sign conventions: positive quantity only; no short selling.
- Determinism: fully deterministic — no stochastic component.

##### Serialization Format

```
<analysis>...free-form reasoning, 1-3 sentences...</analysis>
<decision>{"action": "buy|hold", "quantity": 0.0, "reasoning": "..."}</decision>
```

Rules: (1) Tags are literal ASCII, not optional. (2) Decision block contains valid JSON matching Outputs table. (3) Rule-driven variants generate analysis from deterministic template. (4) Model-driven variants must include tag+JSON requirement in prompt.

##### Implementer Contract Reminder

**Implementers of this agent MUST re-open this I/O Contract during every coding pass and MUST use it as the single source of truth.** On conflict with prose elsewhere, this section wins. (1) Signal wiring: every input row maps to a real read. (2) Decision emission: populate all required fields, clamp out-of-range values. (3) Prompt drafting: spell out tag pattern and JSON schema literally. (4) Parser tests: verify tags, parse JSON, assert fields in range. (5) Variant parity: all variants produce same field set. (6) Contract wins on conflict.

#### Decision Information Set

| Signal     | Type       | Memory Window | Rationale                                  |
|------------|------------|---------------|--------------------------------------------|
| `price`    | Continuous | 1 tick        | Required for purchase execution pricing    |
| `position` | State      | persistent    | Determines whether initialization is needed |
| `cash`     | State      | persistent    | Determines purchase capacity               |
| `round`    | Discrete   | 1 tick        | Determines contribution schedule           |

Does NOT use: fundamental value, technical indicators, momentum signals, volatility, peer positions, news, analyst estimates, or any active-management signal.

#### Core Behavioral Mechanism

1. **Read inputs.** Read `price`, `position`, `cash`, `round` from environment and own state. (Implementation convenience — no theoretical claim.)
2. **Check initialization.** If `round == 0` and `position < initial_position`, set `buy_qty = min(initial_position, cash / price)`. Read: round, position, initial_position, cash, price. Write: buy_qty. [Traces to Passive Portfolio Theorem — establish market holding.]
3. **Check contribution schedule.** If `round > 0` and `round mod contribution_interval == 0` and `contribution_rate > 0`, set `buy_qty = min(contribution_rate, cash / price)`. Read: round, contribution_interval, contribution_rate, cash, price. Write: buy_qty. [Traces to Passive Portfolio Theorem — periodic DCA inflow.]
4. **Default hold.** If neither initialization nor contribution condition met, set action = hold, quantity = 0. Read: conditions. Write: action, quantity. [Traces to Inelastic Markets Hypothesis — non-response to price.]
5. **Emit decision.** If buy_qty > 0, action = buy, quantity = buy_qty. Otherwise action = hold, quantity = 0. Serialize in canonical format. (Implementation convenience.)

#### Action Space

| Aspect                | Specification                                                     |
|-----------------------|-------------------------------------------------------------------|
| Action types allowed  | buy, hold (no sell permitted under passive mandate)               |
| Action parameter rule | market order at current price                                     |
| Sizing rule           | `min(initial_position, cash / price)` at init; `min(contribution_rate, cash / price)` at contribution |
| Action lifetime       | one decision call (immediate execution)                           |
| Revision policy       | no revision — each tick is independent                            |
| State constraint      | position >= 0; position only increases or stays constant          |
| Resource cap          | buy quantity <= cash / price                                      |
| Exit rule             | none — agent never sells and never exits                          |

#### Mathematical Model

**Decision output:** Action `a` in {buy, hold} and quantity `q >= 0` per tick.

**Decision logic formalization:**

```
If round == 0 AND position < initial_position:
    a = buy
    q = min(initial_position - position, cash / price)
Else if round > 0 AND round mod contribution_interval == 0 AND contribution_rate > 0:
    a = buy
    q = min(contribution_rate, cash / price)
Else:
    a = hold
    q = 0
```

**State variables:**

| Variable   | Type  | Initial Value    |
|------------|-------|------------------|
| `position` | float | 0                |
| `cash`     | float | initial_cash     |

**State evolution:**
- Post-execution:
  - Buy: `position += q_filled`; `cash -= q_filled * fill_price`.
  - Hold: no state change.
- Update phase: post-execution only.

**Determinism contract:** Fully deterministic. No stochastic component.

**Parameter symbol table:**

| Symbol                  | Meaning                          | Default Value | Source               |
|-------------------------|----------------------------------|---------------|----------------------|
| `initial_position`      | Target holding at initialization | 50.0          | Scenario normalization |
| `initial_cash`          | Starting capital endowment       | 10000.0       | Scenario normalization |
| `contribution_rate`     | Shares purchased per contribution | 0.0          | Calibrated to 401(k) inflow |
| `contribution_interval` | Ticks between contributions      | 20            | Monthly at daily-tick scale |

#### Behavioral Properties

- Time horizon: long — holds indefinitely with no exit horizon.
- Risk tolerance: medium — accepts full market risk but does not lever or concentrate.
- Information asymmetry: none — uses only price for execution, makes no inference.
- Psychological profile: no behavioral biases; fully rational within passive mandate. Embodies Sharpe's (1991) arithmetic of passive management.

## Parameters

| Parameter               | Type  | Default  | Valid Range    | Sensitivity | Description                           | Impact                                    | Source                     |
|-------------------------|-------|----------|----------------|-------------|---------------------------------------|-------------------------------------------|----------------------------|
| `initial_position`      | float | 50.0     | [10, 500]      | high        | Target long inventory at start        | Higher -> larger inelastic demand base    | Scenario normalization     |
| `initial_cash`          | float | 10000.0  | [1000, 100000] | medium      | Starting capital endowment            | Higher -> more purchase capacity          | Scenario normalization     |
| `contribution_rate`     | float | 0.0      | [0.0, 50.0]    | medium      | Shares purchased per contribution tick | Higher -> growing inelastic demand over time | Calibrated to 401(k) flow |
| `contribution_interval` | int   | 20       | [1, 100]       | low         | Ticks between scheduled contributions | Higher -> less frequent purchases         | Monthly at daily-tick scale |

## Worked Numerical Examples

### Case 1 — Initialization purchase

System state: round = 0, price = 100.0, position = 0, cash = 10000.0, initial_position = 50.0.
Calculation:
  round == 0 AND position (0) < initial_position (50) -> buy branch
  q = min(50.0 - 0, 10000.0 / 100.0) = min(50.0, 100.0) = 50.0
Decision: buy 50.0 shares at 100.0.
State update: position: 0 -> 50.0; cash: 10000.0 -> 5000.0.

### Case 2 — Contribution purchase

System state: round = 20, price = 105.0, position = 50.0, cash = 5000.0, contribution_rate = 5.0, contribution_interval = 20.
Calculation:
  round (20) mod contribution_interval (20) == 0 AND contribution_rate (5.0) > 0 -> buy branch
  q = min(5.0, 5000.0 / 105.0) = min(5.0, 47.62) = 5.0
Decision: buy 5.0 shares at 105.0.
State update: position: 50.0 -> 55.0; cash: 5000.0 -> 4475.0.

### Case 3 — Hold (no trigger)

System state: round = 15, price = 92.0, position = 50.0, cash = 5000.0, contribution_interval = 20.
Calculation:
  round (15) != 0 -> not initialization
  round (15) mod 20 = 15 != 0 -> not contribution tick
Decision: hold.
State update: no change.

### Edge Case — Insufficient cash for full contribution

System state: round = 40, price = 200.0, position = 55.0, cash = 800.0, contribution_rate = 5.0, contribution_interval = 20.
Calculation:
  round (40) mod 20 == 0 AND contribution_rate > 0 -> buy branch
  q = min(5.0, 800.0 / 200.0) = min(5.0, 4.0) = 4.0
Decision: buy 4.0 shares at 200.0 (cash-constrained).
State update: position: 55.0 -> 59.0; cash: 800.0 -> 0.0.

## Behavioral Verification and Calibration

**Calibration data sources:**
- `initial_position` <- Scenario-defined; represents institutional-scale passive holding
- `contribution_rate` <- Calibrated to median 401(k) contribution of ~$500/month / share price, scaled to simulation tick frequency

**Expected individual behaviour:**
- Given round = 0 and position = 0, agent MUST buy up to initial_position shares.
- Given round divisible by contribution_interval and contribution_rate > 0, agent MUST buy contribution_rate shares (or cash-constrained amount).
- Given any non-trigger tick regardless of price movement, agent MUST hold.
- Given a 50% price crash, agent MUST still hold (no panic selling).

**Sanity bounds (red flags indicating broken implementation):**
- IF agent ever emits action = sell THEN broken: passive mandate violated.
- IF agent buys on a non-initialization, non-contribution tick THEN broken: spurious active trading.
- IF agent's purchase quantity exceeds cash / price THEN broken: resource cap violated.
- IF agent responds to price changes with trading activity THEN broken: violates inelastic nature.

#### Ablation Hooks

| Ablation name        | Setting                    | Hypothesis tested                            | Expected direction | Metric                    |
|----------------------|----------------------------|----------------------------------------------|--------------------|---------------------------|
| no-contribution      | `contribution_rate = 0`    | Periodic inflows add to market stability     | decrease           | Background demand volume  |
| large-initial        | `initial_position = 200`   | Larger passive base reduces free float       | increase           | Inelastic share of market |
| frequent-contribution| `contribution_interval = 5`| More frequent inflows smooth demand          | increase           | Demand regularity (CV)    |

## Academic References

| # | Citation                                                                                                                                           | Notes                              |
|---|----------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------|
| 1 | Sharpe, W. F. (1991). The arithmetic of active management. *Financial Analysts Journal*, 47(1), 7-9. https://doi.org/10.2469/faj.v47.n1.7       | Passive investing arithmetic proof |
| 2 | Gabaix, X. & Koijen, R. S. J. (2021). In search of the origins of financial fluctuations: The inelastic markets hypothesis. *Econometrica*, 90(4), 1369-1420. https://doi.org/10.3982/ECTA17734 | Inelastic demand theory |
| 3 | Fama, E. F. & French, K. R. (2010). Luck versus skill in the cross-section of mutual fund returns. *Journal of Finance*, 65(5), 1915-1947. https://doi.org/10.1111/j.1540-6261.2010.01598.x | Active management underperformance |
| 4 | Malkiel, B. G. (1973). *A Random Walk Down Wall Street*. W. W. Norton. ISBN 978-0393330335.                                                      | Random walk / EMH foundation       |

## Design Provenance and Versioning

| Field   | Content                                             |
|---------|-----------------------------------------------------|
| Author  | Codex                                               |
| Created | 2026-07-16                                          |
| Version | 1.0.0                                               |
| Icon    | ![](../agent_images/icons/finance-index-holder.png) |
| Status  | draft                                               |
