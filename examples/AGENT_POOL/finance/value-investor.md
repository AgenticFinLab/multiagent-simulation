# Value Investor

## Summary

| Field                 | Content                                                                                                                                                                 |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Archetype             | Value investor                                                                                                                                                          |
| Theory Family         | Value Investing / Margin of Safety                                                                                                                                      |
| Behavioral Tendency   | **Converging — buys when price falls significantly below intrinsic value and sells at premiums; converges on fundamental value and provides a stabilising price floor** |
| Market Role           | **Stabilising** — sole consistent buyer during crashes, providing the price floor that prevents complete market collapse                                                |
| Time Horizon          | long                                                                                                                                                                    |
| Risk Tolerance        | high                                                                                                                                                                    |
| Information Asymmetry | none                                                                                                                                                                    |
| Determinism           | deterministic                                                                                                                                                           |

## Definition and Goals

This agent models a patient institutional value buyer who purchases when the margin of safety is sufficiently large. The real-world counterpart is a Graham-style value investor such as Warren Buffett, who buys aggressively during crashes when prices fall far below intrinsic value.

The decision goal is to buy fixed-size lots when `deviation = (fundamental - price) / fundamental` exceeds the margin-of-safety threshold, and to sell when the premium exceeds the same threshold. The agent does not short-sell.

In simulation this agent provides the crash's price floor mechanism — absorbing supply from cascade sellers and partially stabilising the decline. Non-goals: it must not trade on momentum, must not use leverage, and must not double-down speculatively.

## Theoretical Foundation

**Margin of safety and value investing**:
- Theory / Study: Security Analysis — margin of safety concept.
- Citation: Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill. Also: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.
- Core Insight: An investment should only be made when the purchase price is sufficiently below estimated intrinsic value to provide a buffer against estimation error. For equity portfolios, Graham recommended 15–33% discount to intrinsic value. This creates a price floor: when a sufficient fraction of market participants share value-investing discipline, prices cannot fall indefinitely.
- Mathematical Formulation: Buy if `P < F * (1 - MoS)`; sell if `P > F * (1 + MoS)`. With `F = 250` and `MoS = 0.15`: buy when `P < 212.5`, sell when `P > 287.5`.
- Empirical Evidence: Greenwald et al. (2001) document average excess return of 6–8% annualized for deep-value strategies with 15%+ discount triggers. Buffett disclosed major equity purchases during and after the 1987 crash.
- Relevance to This Agent: `value_discount = 0.15`, `base_size = 40` calibrated to model a single large institutional buyer who activates at the Graham margin of safety threshold.
- Calibration Source: Graham & Dodd (1934); Graham (1949); Greenwald et al. (2001).
- Falsification Conditions: If the agent sells when price is below fundamental, the value mechanism is inverted.
- Alternative Theories: momentum trading; noise-trader risk; rational inattention.

**Limits of arbitrage and stabilising speculation**:
- Theory / Study: Rational stabilising speculation vs. capital constraints.
- Citation: Friedman, M. (1953). "The case for flexible exchange rates." In *Essays in Positive Economics*. University of Chicago Press. Also: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.2307/2329555
- Core Insight: Friedman argued that destabilising speculation is self-eliminating; stabilising speculators who buy low and sell high survive. However, Shleifer & Vishny note that even rational stabilisers face capital constraints — the "limits of arbitrage" means the ValueInvestor cannot fully absorb a crash alone.
- Mathematical Formulation: `expected_profit = F - P - transaction_cost > 0` when buying at discount. Capital constraint: `Q_max = cash / P` limits total absorption.
- Empirical Evidence: During the 1987 crash, value-oriented buyers were active but insufficient to arrest the one-day decline; recovery required Fed intervention.
- Relevance to This Agent: Provides a partial floor — absorbs some supply at deep discounts — but calibrated so cascade selling exceeds absorption capacity during peak crash.
- Calibration Source: Shleifer & Vishny (1997); used as theoretical framework for partial stabilisation.
- Falsification Conditions: If the agent fully arrests the crash alone, the limits-of-arbitrage constraint is not represented.
- Alternative Theories: unlimited arbitrage; perfect market efficiency.

## Design Purpose and Activation Triggers

Purpose: Provide the crash's price floor mechanism — model patient buyers who step in at deep discounts.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available
- `deviation` available

Missing-Signal Policy: hold when any required signal is missing.

Activation Triggers:
- `deviation > value_discount`: buy fixed `base_size` shares (cash-constrained).
- `deviation < -value_discount`: sell fixed `base_size` shares (if position allows).
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: hibernate buy side.
- Position is zero and deviation is negative: hold.

Behavioral Adaptation by Condition:
| Condition                                         | Behavioral change             | Mechanism                                        |
|---------------------------------------------------|-------------------------------|--------------------------------------------------|
| Deep discount (deviation > value_discount)        | Buys fixed base_size          | Cash-constrained: `min(base_size, cash / price)` |
| Deep premium (deviation < -value_discount)        | Takes profit, sells base_size | Position-constrained: `min(base_size, position)` |
| Near fair value (abs(deviation) < value_discount) | Holds patiently               | No action inside margin-of-safety band           |

Environmental Dependencies: Requires a per-tick `price`, `fundamental`, and `deviation` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime          | Contribution | Mechanism                                      |
|-----------------|--------------|------------------------------------------------|
| Crash / cascade | Stabilising  | Buys at deep discounts, providing price floor. |
| Recovery        | Mixed        | Sells at premium, taking profit.               |
| Calm            | Neutral      | Inside no-trade band; minimal activity.        |

Interaction with other agents: Directly opposes PortfolioInsurer and ProgramTrader (buys what they sell); IndexArbitrageur may also buy at deep discounts; NoiseTrader's random buying occasionally reinforces the floor.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                      |
|---------------------|--------------|--------------|-----------|----------------------------|
| `price`             | environment  | `float`      | yes       | Execution reference.       |
| `fundamental`       | environment  | `float`      | yes       | Intrinsic value reference. |
| `deviation`         | environment  | `float`      | yes       | Trigger and sizing signal. |
| `cash`              | agent state  | `float`      | yes       | Buy capacity.              |
| `position`          | agent state  | `float`      | yes       | Sell capacity.             |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata.        |

##### Outputs (per decision call)

| Field         | Type   | Valid Range / Enum        | Unit     | Required?   | Meaning                       |
|---------------|--------|---------------------------|----------|-------------|-------------------------------|
| `action`      | enum   | {"buy", "sell", "hold"}   | —        | yes         | Discrete action.              |
| `quantity`    | float  | `[0, base_position_size]` | shares   | conditional | Order magnitude; 0 when hold. |
| `price_level` | float  | `= price`                 | currency | conditional | Execution reference.          |
| `reasoning`   | string | 1–3 sentences             | —        | yes         | Audit trail.                  |

##### Content Constraints

- Required fields MUST be present; forbidden fields MUST NOT be emitted.
- `quantity` MUST be clamped to `[0, base_position_size]`.
- `quantity` is unsigned; direction is carried by `action`.

##### Serialization Format

    <analysis>...free-form reasoning...</analysis>
    <decision>{"action": "<enum>", "quantity": <float>, "price_level": <float>, "reasoning": "<text>"}</decision>

Rules: Tags are literal ASCII; JSON keys match Outputs table; rule variants may template analysis; model variants MUST include in prompt; retrieval variants MUST declare fallback sentinel.

Retrieval fallback sentinel (for retrieval-augmented variants): `"(No relevant knowledge retrieved this round.)"` — injected verbatim into the `<analysis>` block when retrieval returns empty.

##### Implementer Contract Reminder

Implementers MUST re-open this §3.6.0 I/O Contract during every coding pass as the single source of truth.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                            |
|---------------|------------|---------------|--------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference.                 |
| `fundamental` | Continuous | 1 tick        | Intrinsic value anchor.              |
| `deviation`   | Continuous | 1 tick        | Trigger signal for margin-of-safety. |
| `cash`        | State      | persistent    | Buy constraint.                      |
| `position`    | State      | persistent    | Sell constraint.                     |

Does NOT use: momentum, anchor, volume, peer flow, cost_basis.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `deviation`, `cash`, `position`.
2. If `deviation > value_discount`: buy `q = min(base_position_size, cash / price)`.
3. If `deviation < -value_discount` and `position > 0`: sell `q = min(base_position_size, position)`.
4. Otherwise hold.
5. Emit decision and update state post-fill.

#### Action Space

| Aspect                | Specification                                                         |
|-----------------------|-----------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                    |
| Price level rule      | market order at current price                                         |
| Order quantity rule   | buy: `min(base_size, cash / price)`; sell: `min(base_size, position)` |
| Order lifetime        | 1 tick                                                                |
| Cancellation policy   | unfilled orders expire                                                |
| Inventory constraint  | `position >= 0`; no short-selling                                     |
| Wealth / leverage cap | `cash >= 0`; no margin                                                |
| Stop-loss / kill rule | none — patient value holder                                           |

#### Mathematical Model

```
dev_t = (F_t - P_t) / F_t
if dev_t > theta_value:
    a_t = buy;  q_t = min(Q_base, cash_t / P_t)
elif dev_t < -theta_value and position_t > 0:
    a_t = sell; q_t = min(Q_base, position_t)
else:
    a_t = hold; q_t = 0
```

| Symbol               | Meaning                    | Default Value | Source                 |
|----------------------|----------------------------|---------------|------------------------|
| `theta_value`        | margin-of-safety threshold | 0.15          | Graham & Dodd (1934)   |
| `base_position_size` | fixed order quantity       | 40.0          | Scenario normalization |

#### Behavioral Properties

- Time horizon: long, because the agent is patient and ignores short-term momentum.
- Risk tolerance: high, because the agent deliberately buys during worst drawdowns.
- Information asymmetry: none, all inputs are public.
- Psychological profile: patient, contrarian, high conviction — "be greedy when others are fearful."

## Parameters

| Parameter            | Type  | Default  | Valid Range       | Sensitivity | Description                                       | Impact                                               | Source                 |
|----------------------|-------|----------|-------------------|-------------|---------------------------------------------------|------------------------------------------------------|------------------------|
| `value_discount`     | float | 0.15     | [0.05, 0.33]      | high        | Margin-of-safety threshold for buy/sell triggers. | Higher -> fewer but deeper trades; later activation. | Graham & Dodd (1934)   |
| `base_position_size` | float | 40.0     | [10, 100]         | medium      | Fixed order quantity per trade.                   | Higher -> stronger price floor per round.            | Scenario normalization |
| `initial_cash`       | float | 500000.0 | [100000, 1000000] | medium      | Cash reserves for crash buying.                   | Higher -> longer sustained buying capacity.          | Scenario normalization |

## Population and Heterogeneity

| Aspect                         | Specification           |
|--------------------------------|-------------------------|
| Default population size        | scenario-dependent      |
| Parameter heterogeneity policy | identical parameters    |
| Cross-agent correlation        | none                    |
| Identity persistence           | persistent across ticks |

## Worked Numerical Examples

### Case 1 — Buy at deep discount
System state: `price=195`, `fundamental=250`, `deviation=0.22`, `cash=384000`, `position=2400`.
Calculation: `deviation = 0.22 > 0.15` triggers buy; `q = min(40, 384000/195) = min(40, 1969) = 40`.
Decision: buy 40 at 195.
State update: position +40; cash -7800.

### Case 2 — Hold inside band
System state: `price=230`, `fundamental=250`, `deviation=0.08`.
Calculation: `abs(0.08) < 0.15`; inside no-trade band.
Decision: hold.

### Case 3 — Sell at premium
System state: `price=300`, `fundamental=250`, `deviation=-0.167`, `position=100`.
Calculation: `deviation = -0.167 < -0.15` triggers sell; `q = min(40, 100) = 40`.
Decision: sell 40 at 300.
State update: position -40; cash +12000.

### Edge Case — Cash exhausted
System state: `cash=0`, `price=195`, `deviation=0.22`.
Decision: hold (no buy capacity).

## Validation and Calibration

**Calibration data sources**:
- `value_discount` <- Graham & Dodd (1934) margin-of-safety ranges; 15% is the canonical institutional threshold.
- `base_position_size` <- scenario normalization for institutional scale.

**Expected individual behaviour**:
- Given deviation > 0.15, agent MUST buy fixed base_size.
- Given deviation < -0.15 with position, agent MUST sell fixed base_size.
- Given abs(deviation) < 0.15, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells when price is below fundamental THEN the value mechanism is inverted because value investors buy undervaluation.
- IF the agent uses leverage THEN the design constraint is violated because value investors do not borrow.
- IF `quantity > base_position_size` THEN the fixed-sizing contract is broken.

#### Ablation Hooks

| Ablation name  | Setting                 | Hypothesis tested                                 | Expected direction | Metric             |
|----------------|-------------------------|---------------------------------------------------|--------------------|--------------------|
| no-value-floor | `value_discount = 999`  | Removing value buying eliminates the price floor. | deeper crash       | max drawdown       |
| patient-value  | `value_discount = 0.33` | Higher threshold delays floor activation.         | later floor        | round of first buy |

## Behavioral Verification and Calibration

- Given deviation exceeding 0.15 (value_discount) with available cash, agent must buy exactly base_position_size shares (or remaining cash capacity if less).
- Given deviation below -0.15 with positive position, agent must sell exactly base_position_size shares (or remaining position if less).
- Given abs(deviation) < 0.15, agent must hold with zero quantity regardless of price trajectory or market conditions.
- Given cash fully exhausted during a crash, agent must hold on the buy side even if the discount exceeds 0.15.
- Given both price and fundamental available but deviation = 0, agent must hold with no trade activity.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| shallow-discount | `value_discount = 0.08` | Lower margin-of-safety threshold activates buying earlier, providing stronger price floor. | decrease | max drawdown in crash episode |
| large-orders | `base_position_size = 80` | Doubling fixed order size strengthens per-round absorption capacity during cascades. | decrease | rounds to price stabilisation |

## Academic References

| # | Citation                                                                                                                           | Notes                                                      |
|---|------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1 | Graham, B., & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.                                                                   | Margin of safety concept; basis for value_discount = 0.15  |
| 2 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                                  | Popularization of margin of safety; fixed sizing principle |
| 3 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35–55. https://doi.org/10.2307/2329555 | Why value investor provides partial but incomplete floor   |
| 4 | Greenwald, B., Kahn, J., Sonkin, P. D., & van Biema, M. (2001). *Value Investing: From Graham to Buffett and Beyond*. Wiley.       | Empirical documentation of value discount calibration      |

## Design Provenance and Versioning

| Field       | Content                                                                              |
|-------------|--------------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                        |
| Reviewed by | audit_agent_handbook.py v1                                                           |
| Created     | 2026-07-11                                                                           |
| Version     | 1.1.0                                                                                |
| Status      | conformant                                                                           |
| Icon        | ![](../agent_images/icons/finance-value-investor.png)                                |
