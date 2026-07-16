# Systematic Analyst

## Summary

| Field                 | Content                                                                                                      |
|-----------------------|--------------------------------------------------------------------------------------------------------------|
| Archetype             | Systematic analyst                                                                                           |
| Theory Family         | Rational Expectations / Bayesian Updating                                                                    |
| Behavioral Tendency   | **Converging — uses objective Bayesian weighting of all available data; converges on fundamental value**     |
| Market Role           | **Stabilising** — provides rational price-discovery pressure that counteracts availability-bias overreaction |
| Time Horizon          | medium                                                                                                       |
| Risk Tolerance        | low-medium                                                                                                   |
| Information Asymmetry | none                                                                                                         |
| Determinism           | deterministic                                                                                                |

## Definition and Goals

This agent models a rational, systematic analyst who processes all available information using objective evidence-based methods without availability bias. The real-world counterpart is a sell-side analyst or institutional researcher who updates beliefs via Bayes' rule and trades when the posterior estimate diverges from market price.

The decision goal is to emit a buy, sell, or hold order based on the deviation between the Bayesian posterior estimate of fundamental value and the current market price. The agent weights signals by their precision (inverse variance), not by recency or salience.

In simulation this agent serves as the rational benchmark against which availability-biased agents are compared — it accelerates price discovery toward fundamental value. Non-goals: it must not overweight recent or vivid signals, ignore base rates, or exhibit recency bias.

## Theoretical Foundation

**Rational Bayesian updating**:
- Theory / Study: Bayesian belief updating under rational expectations.
- Citation: Mullainathan, S., & Thaler, R. H. (2002). Behavioral economics. In *The International Encyclopedia of the Social & Behavioral Sciences* (pp. 1094–1100). Pergamon. Also: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.
- Core Insight: A rational agent combines prior beliefs with new signals weighted by signal precision (inverse variance). Unlike availability-biased agents, the systematic analyst does not overweight vivid or recent information — the posterior is proportional to the likelihood function times the prior.
- Mathematical Formulation: `posterior_mean = (prior_precision * prior_mean + signal_precision * signal) / (prior_precision + signal_precision)`.
- Empirical Evidence: Rational-expectations benchmarks consistently eliminate mispricing in controlled experiments; professional analysts who follow disciplined processes outperform heuristic-driven peers (Graham 1949; Fama 1970).
- Relevance to This Agent: The agent's estimate is the precision-weighted Bayesian posterior; trades when `|posterior_mean - price| / price > threshold`.
- Calibration Source: Mullainathan & Thaler (2002); Graham (1949).
- Falsification Conditions: If the agent overweight the most recent signal relative to its precision, availability bias is present — the posterior must equal the Bayesian optimum.
- Alternative Theories: Bounded rationality (Simon 1955); availability heuristic (Tversky & Kahneman 1973).

**Bounded rationality as contrast**:
- Theory / Study: Bounded rationality framework defining the rational benchmark.
- Citation: Simon, H. A. (1955). A behavioral model of rational choice. *Quarterly Journal of Economics*, 69(1), 99–118. https://doi.org/10.2307/1884852
- Core Insight: Simon's bounded rationality describes agents who satisfice rather than optimise. The systematic analyst represents the opposite pole — an agent that *does* optimise using all available information, serving as the control against which bounded-rationality agents are measured.
- Mathematical Formulation: `estimate_Bayesian = E[V | all signals, precision-weighted]`; contrasted with `estimate_heuristic = f(recent_salient_signals)`.
- Empirical Evidence: When both agent types co-exist, the Bayesian agent earns positive expected returns by trading against heuristic-driven mispricing (Fama 1970).
- Relevance to This Agent: Provides the theoretical contrast that defines the AvailabilityBias scenario — systematic analyst vs. availability-biased agents.
- Calibration Source: Simon (1955); used as theoretical benchmark, not directly calibrated.
- Falsification Conditions: If the systematic analyst's estimate deviates from the precision-weighted posterior, the rational benchmark is contaminated.
- Alternative Theories: Heuristic-based decision making; fast-and-frugal heuristics (Gigerenzer & Goldstein 1996).

## Design Purpose and Activation Triggers

Purpose: Provide rational price-discovery pressure that counteracts availability-bias overreaction.

Call Frequency: every-tick.

Prerequisite Signals:
- `price` available
- `fundamental` available

Missing-Signal Policy: hold when either signal is missing.

Activation Triggers:
- `|posterior_mean - price| / price > buy_threshold`: buy if price below posterior.
- `|posterior_mean - price| / price > sell_threshold`: sell if price above posterior.
- `<Default>`: hold.

Deactivation Conditions:
- Cash exhausted: hibernate buy side.
- Position is zero and price is above posterior: hold.

Behavioral Adaptation by Condition:
| Condition                 | Behavioral change                                    | Mechanism                                  |
|---------------------------|------------------------------------------------------|--------------------------------------------|
| Noisy signal environment  | Down-weights the noisy signal via Bayesian precision | Posterior variance rises with signal noise |
| Stable signal environment | Tightens the posterior around the signal             | Posterior variance falls                   |

Environmental Dependencies: Requires a per-tick `price` and `fundamental` feed. None beyond §3.6.1 signals.

Market Contribution by Regime:
| Regime                         | Contribution | Mechanism                                                  |
|--------------------------------|--------------|------------------------------------------------------------|
| Availability-bias overreaction | Stabilising  | Trades against mispricing caused by recency/salience bias. |
| Crash                          | Stabilising  | Buys when availability-biased agents oversell.             |
| Calm                           | Neutral      | Price near fundamental; minimal trading.                   |

Interaction with other agents: Trades against availability-biased agents (recent-event-overweighter, media-influenced-trader); does not interact strategically with other rational agents.

## Behavioral Framework

#### I/O Contract

##### Inputs (per decision call)

| Input               | Source       | Type / Shape | Required? | Notes                 |
|---------------------|--------------|--------------|-----------|-----------------------|
| `price`             | environment  | `float`      | yes       | Execution reference.  |
| `fundamental`       | environment  | `float`      | yes       | True value reference. |
| `cash`              | agent state  | `float`      | yes       | Buy capacity.         |
| `position`          | agent state  | `float`      | yes       | Sell capacity.        |
| `identity`, `round` | round header | `str`, `int` | yes       | Scheduler metadata.   |

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

##### Implementer Contract Reminder

Implementers MUST re-open this §3.6.0 I/O Contract during every coding pass as the single source of truth.

#### Decision Information Set

| Signal        | Type       | Memory Window | Rationale                            |
|---------------|------------|---------------|--------------------------------------|
| `price`       | Continuous | 1 tick        | Execution reference.                 |
| `fundamental` | Continuous | 1 tick        | Value anchor for Bayesian posterior. |
| `cash`        | State      | persistent    | Buy constraint.                      |
| `position`    | State      | persistent    | Sell constraint.                     |

Does NOT use: recent_events, media_salience, anchor, momentum, peer flow.

#### Core Behavioral Mechanism

1. Read `price`, `fundamental`, `cash`, `position`.
2. Compute `posterior_mean = fundamental` (the agent treats the fundamental signal as the Bayesian optimum with full precision).
3. Compute `deviation = (posterior_mean - price) / price`.
4. If `deviation > buy_threshold`, compute buy quantity: `q = min(base_position_size, deviation * sizing_scale)`, clamped by `cash / price`.
5. If `deviation < -sell_threshold` and `position > 0`, sell: `q = min(position, base_position_size)`.
6. Otherwise hold.
7. Emit decision and update state post-fill.

#### Action Space

| Aspect                | Specification                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------|
| Order types allowed   | market, hold-no-op                                                                                |
| Price level rule      | market order at current price                                                                     |
| Order quantity rule   | buy: `min(base_size, deviation * sizing_scale)` clamped by cash; sell: `min(position, base_size)` |
| Order lifetime        | 1 tick                                                                                            |
| Cancellation policy   | unfilled orders expire                                                                            |
| Inventory constraint  | `position >= 0`; no short-selling                                                                 |
| Wealth / leverage cap | `cash >= 0`; no margin                                                                            |
| Stop-loss / kill rule | none — patient rationalist                                                                        |

#### Mathematical Model

```
posterior_t = F_t
dev_t = (posterior_t - P_t) / P_t
if dev_t > theta_buy:
    a_t = buy;  q_t = min(Q_max, dev_t * k_q); clamped by cash/P_t
elif dev_t < -theta_sell and position_t > 0:
    a_t = sell; q_t = min(position_t, Q_max)
else:
    a_t = hold; q_t = 0
```

| Symbol               | Meaning                  | Default Value | Source                 |
|----------------------|--------------------------|---------------|------------------------|
| `theta_buy`          | buy deviation threshold  | 0.03          | Graham (1949)          |
| `theta_sell`         | sell deviation threshold | 0.05          | Scenario calibration   |
| `sizing_scale`       | quantity scale           | 3000.0        | Scenario normalization |
| `base_position_size` | max order                | 200.0         | Scenario normalization |

#### Behavioral Properties

- Time horizon: medium, because the agent trades to correct mispricing without long-term commitment.
- Risk tolerance: low-medium, because the agent avoids leverage and short-selling.
- Information asymmetry: none, all inputs are public.
- Psychological profile: disciplined, objective, Bayesian.

## Parameters

| Parameter            | Type  | Default | Valid Range  | Sensitivity | Description                      | Impact                            | Source                 |
|----------------------|-------|---------|--------------|-------------|----------------------------------|-----------------------------------|------------------------|
| `buy_threshold`      | float | 0.03    | [0.01, 0.10] | high        | Discount required before buying. | Higher -> fewer but deeper buys.  | Graham (1949)          |
| `sell_threshold`     | float | 0.05    | [0.02, 0.15] | medium      | Premium required before selling. | Higher -> more patient holding.   | Scenario calibration   |
| `sizing_scale`       | float | 3000.0  | [500, 8000]  | medium      | Converts deviation to quantity.  | Higher -> larger orders.          | Scenario normalization |
| `base_position_size` | float | 200.0   | [50, 500]    | medium      | Maximum order quantity.          | Higher -> larger per-tick impact. | Scenario normalization |

## Population and Heterogeneity

| Aspect                         | Specification           |
|--------------------------------|-------------------------|
| Default population size        | scenario-dependent      |
| Parameter heterogeneity policy | identical parameters    |
| Cross-agent correlation        | none                    |
| Identity persistence           | persistent across ticks |

## Worked Numerical Examples

### Case 1 — Buy undervalued
System state: `price=95`, `fundamental=100`, `cash=50000`, `position=0`.
Calculation: `deviation = (100-95)/95 = 0.0526`; `0.0526 > 0.03` triggers buy; `q = min(200, 0.0526*3000) = min(200, 157.9) = 157`; cash clamp: `min(157, 50000/95) = 157`.
Decision: buy 157 at 95.
State update: position +157; cash -14915.

### Case 2 — Hold at fair value
System state: `price=100`, `fundamental=100`.
Calculation: `deviation = 0`; inside no-trade band.
Decision: hold.

### Case 3 — Sell overvalued
System state: `price=110`, `fundamental=100`, `position=100`.
Calculation: `deviation = (100-110)/110 = -0.0909`; `-0.0909 < -0.05` triggers sell; `q = min(100, 200) = 100`.
Decision: sell 100 at 110.
State update: position -100; cash +11000.

### Edge Case — Missing fundamental
Decision: hold.

## Validation and Calibration

**Calibration data sources**:
- `buy_threshold` <- Graham (1949) margin-of-safety discipline; tighter than value-trader because the systematic analyst has no cognitive bias.
- `sell_threshold` <- scenario calibration for profit-taking timing.

**Expected individual behaviour**:
- Given price below fundamental by >3%, agent MUST buy.
- Given price above fundamental by >5% with position, agent MUST sell.
- Given price near fundamental, agent MUST hold.

**Sanity bounds (red flags indicating broken implementation)**:
- IF the agent sells when price is below fundamental THEN the rational mechanism is inverted because systematic analysts buy undervaluation.
- IF the agent overweight recent signals relative to precision THEN availability bias is contaminating the rational benchmark.
- IF `quantity > base_position_size` THEN the sizing constraint is broken.

#### Ablation Hooks

| Ablation name       | Setting                | Hypothesis tested                                                          | Expected direction | Metric                         |
|---------------------|------------------------|----------------------------------------------------------------------------|--------------------|--------------------------------|
| no-rational-counter | `buy_threshold = 999`  | Removing rational pressure allows availability-bias mispricing to persist. | larger mispricing  | mean absolute deviation from F |
| tight-threshold     | `buy_threshold = 0.01` | Faster rational response reduces mispricing duration.                      | shorter mispricing | half-life of price deviation   |

## Behavioral Verification and Calibration

- Given price 3% or more below the Bayesian posterior (fundamental), agent must emit a buy order with quantity proportional to the deviation magnitude.
- Given price 5% or more above the Bayesian posterior with positive position, agent must emit a sell order capped at base_position_size.
- Given price within the no-trade band (deviation < buy_threshold and deviation > -sell_threshold), agent must hold with zero quantity regardless of cash or position levels.
- Given a missing or NaN fundamental signal, agent must hold and emit no order.
- Given two signals of differing precision, agent must weight them by inverse variance without overweighting the more recent signal.

#### Ablation Hooks

| Ablation name | Setting | Hypothesis tested | Expected direction | Metric |
|---------------|---------|-------------------|--------------------|--------|
| wide-band | `buy_threshold = 0.08, sell_threshold = 0.12` | Wider no-trade band reduces rational correction frequency, allowing mispricing to persist longer. | increase | mean absolute price-fundamental deviation |
| high-sizing-scale | `sizing_scale = 6000` | Doubling sizing aggressiveness accelerates convergence toward fundamental. | decrease | half-life of price deviation from fundamental |

## Academic References

| # | Citation                                                                                                                                                           | Notes                                                  |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| 1 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                                                                                                  | Disciplined fundamental analysis as rational benchmark |
| 2 | Mullainathan, S., & Thaler, R. H. (2002). Behavioral economics. In *The International Encyclopedia of the Social & Behavioral Sciences* (pp. 1094–1100). Pergamon. | Rational vs. heuristic decision making                 |
| 3 | Simon, H. A. (1955). A behavioral model of rational choice. *Quarterly Journal of Economics*, 69(1), 99–118. https://doi.org/10.2307/1884852                       | Bounded rationality contrast                           |
| 4 | Fama, E. F. (1970). Efficient capital markets. *Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486                                               | Rational expectations and price discovery              |

## Design Provenance and Versioning

| Field       | Content                                                                               |
|-------------|---------------------------------------------------------------------------------------|
| Author      | AGenticFinLab                                                                         |
| Reviewed by | audit_agent_handbook.py v1                                                            |
| Created     | 2026-07-11                                                                            |
| Version     | 1.1.0                                                                                 |
| Status      | conformant                                                                            |
| Icon        | ![](../agent_images/icons/finance-systematic-analyst.png)                             |
