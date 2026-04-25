# AnchoringEffect RuleLLM — Implementation Explanation

## Overview

| Item                               | Description                                                                                                                                                                                                                    |
|------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Variant                            | RuleLLM                                                                                                                                                                                                                        |
| Implements                         | `../simulation-bases.md`                                                                                                                                                                                                       |
| Decision Logic                     | Hybrid: LLM reasoning anchored to explicit quantitative rules embedded in system prompts                                                                                                                                       |
| Key Difference from Other Variants | Every system prompt has two mandatory sections: `== PERSONA ==` (who the agent is) and `== DECISION RULES ==` (exact Rule-variant formulas in plain text); LLM may adjust quantities ±20% but must follow sign (buy/sell/hold) |
| Primary Research Contribution      | Isolates the effect of language reasoning: with identical quantitative constraints, does LLM reasoning alter anchoring dynamics compared to the pure Rule baseline?                                                            |

---

## 2. How Theoretical Design Is Implemented

Theory for each investor type is defined in `simulation-bases.md §4`. Below: how each theory is encoded in the RuleLLM hybrid via dual-section prompts.

### AnchoredTrader: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4 — AnchoredTrader)

| Theoretical Design Element                            | Implementation                                                                                                                                                                              |
|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.1          | `== PERSONA ==` section: describes anchoring psychology; cites Tversky & Kahneman (1974) as CORE BELIEF                                                                                     |
| Rule-based behavior → sim-bases §4 AnchoredTrader     | `== DECISION RULES ==` section: step-by-step plain-text version of `perceived_target = anchor_price + (fundamental − anchor_price) × 0.3`; threshold: `if perceived_deviation < -0.03: BUY` |
| LLM Persona → simulation-bases.md §4 LLM Persona      | Persona section conveys anchoring psychology without naming the phenomenon; anchors to "first price you observed"                                                                           |
| RuleLLM Hybrid Notes → sim-bases §4 RuleLLM           | LLM follows rule sign strictly; may adjust quantity by ±20%; `adjustment_factor` = 0.3 hardcoded in prompt (mirror of Rule)                                                                 |
| Parameter values → simulation-bases.md §6             | `adjustment_factor` = 0.3; trade threshold = 3%; base size = 20 units; from `RULELLM_ANCHORED_TRADER_SYS`                                                                                   |
| Market impact → simulation-bases.md §4 AnchoredTrader | Same destabilizing role as Rule variant; anchoring-induced perceived target creates persistent demand/supply imbalance                                                                      |

### HistoricalAnchor: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4 — HistoricalAnchor)

| Theoretical Design Element                              | Implementation                                                                                                                            |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.2            | `== PERSONA ==` section: historical average as reference; cites Northcraft & Neale (1987)                                                 |
| Rule-based behavior → sim-bases §4 HistoricalAnchor     | `== DECISION RULES ==` section: `perceived_deviation = (price − hist_avg) / hist_avg × (1 − 0.5)`; 60-round rolling average; 3% threshold |
| LLM Persona → simulation-bases.md §4 LLM Persona        | Persona: "you give excessive weight to the historical average price" — instills underreaction to current signals                          |
| Parameter values → simulation-bases.md §6               | `anchor_weight` = 0.5; `lookback` = 60; base size = 20 units                                                                              |
| Market impact → simulation-bases.md §4 HistoricalAnchor | Same momentum-dampening destabilizing role as Rule variant                                                                                |

### RationalUpdater: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4 — RationalUpdater)

| Theoretical Design Element                             | Implementation                                                                                                                       |
|--------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.4           | `== PERSONA ==` section: "disciplined Bayesian investor" — rational expectations benchmark; Muth (1961)                              |
| Rule-based behavior → sim-bases §4 RationalUpdater     | `== DECISION RULES ==` section: `if deviation < -0.02: BUY`; `if deviation > +0.02: SELL`; quantity = min(25, abs(deviation) × 1000) |
| LLM Persona → simulation-bases.md §4 LLM Persona       | Persona emphasizes unbiased updating; "you do not anchor to past prices"                                                             |
| Parameter values → simulation-bases.md §6              | Threshold = 0.02; base size = 25 units; `deviation` from market broadcast                                                            |
| Market impact → simulation-bases.md §4 RationalUpdater | Stabilizing force; with rule-constrained behavior, stabilization is expected to be very close to Rule baseline                       |

### MomentumTrader: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4 — MomentumTrader)

| Theoretical Design Element                            | Implementation                                                                                                      |
|-------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.5          | `== PERSONA ==` section: "trend-following"; cites Jegadeesh & Titman (1993)                                         |
| Rule-based behavior → sim-bases §4 MomentumTrader     | `== DECISION RULES ==` section: `return_pct = (price − prev_price) / prev_price`; if > +0.02: BUY; if < −0.02: SELL |
| Parameter values → simulation-bases.md §6             | `entry_threshold` = 0.02; base size = 20 units                                                                      |
| Market impact → simulation-bases.md §4 MomentumTrader | Neutral amplifier; with rule-constrained behavior, same trend-amplifying role as Rule                               |

### NoiseTrader: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4 — NoiseTrader)

| Theoretical Design Element                         | Implementation                                                                                       |
|----------------------------------------------------|------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.6       | `== PERSONA ==` section: uninformed random trader; cites Black (1986)                                |
| Rule-based behavior → sim-bases §4 NoiseTrader     | `== DECISION RULES ==` section: trade probability 0.05; random buy/sell; quantity uniform [100, 500] |
| LLM Persona → simulation-bases.md §4 LLM Persona   | Persona: "your decisions are driven by sentiment and random impulses"                                |
| Parameter values → simulation-bases.md §6          | `trade_probability` = 0.05; `min_order` = 100; `max_order` = 500                                     |
| Market impact → simulation-bases.md §4 NoiseTrader | Background liquidity; same stochastic volatility contribution as Rule variant                        |

---

## 3. Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `examples.AnchoringEffect.Rule.players.Market._clear_market()` (imported by `RuleLLM/players.py`)

Code translation (identical to Rule variant — RuleLLM does not modify market logic):
```
sim-bases variable  →  Python variable     →  config path
λ (price_impact)    →  price_impact        →  extras["price_impact"]        = 0.01
γ (mean_reversion)  →  mean_reversion      →  extras["mean_reversion"]       = 0.01
F (fundamental)     →  self._fundamental   →  extras["fundamental_value"]    = 100.0
ε (noise)           →  noise               →  random.gauss(0, noise_std)     σ = extras["noise_std"]
D(t) (net demand)   →  net_demand          →  sum(buy_qty) − sum(sell_qty)
```

Additional mechanisms: `simulation-bases.md §3.2`
- Price floor → `new_price = max(new_price, 0.01)` in `Market.perceive()`
- All `RuleLLM/players.py` imports `Market` directly from `examples.AnchoringEffect.Rule.players` — no market-side code duplication

Deviations from simulation-bases.md design: None — market implementation is identical to Rule variant.

---

## 4. Variant-Specific Features

What is unique to RuleLLM versus other variants — motivated by `simulation-bases.md §9`:

**Dual-Section Prompt Structure** (cite sim-bases §4 RuleLLM Hybrid Notes):
Every system prompt in `prompts.py` must contain exactly two labeled sections:
1. `== PERSONA ==` — who the agent is, risk style, emotional traits. Same psychological content as LLM variant but condensed.
2. `== DECISION RULES ==` — the exact Rule-variant formulas re-expressed in step-by-step plain text. LLM must follow the sign (buy/sell/hold) from these rules; may adjust quantity by ±20% based on its judgment.

**Rule–Judgment Balance**:
- LLM is instructed: "Follow the trading rules exactly for direction (buy/sell/hold). You may adjust quantity by up to ±20% based on your judgment."
- This constrains the LLM to bounded deviation rather than free-form reasoning.
- Enables direct comparison: any metric differences from Rule are attributable to ±20% quantity adjustments and LLM reasoning variability, not formula departures.

**Prompt Rule Synchronization Requirement**:
- The numeric values in `== DECISION RULES ==` sections MUST match the parameters in `configs/AnchoringEffect/RuleLLM/players.yml`.
- If config parameters change, the embedded prompt rules must be updated to match.
- Current values (from Rule variant, sim-bases §6): `adjustment_factor = 0.3`, `anchor_weight = 0.5`, `entry_threshold = 0.02`, `trade_probability = 0.05`.

**LLM Call Flow for RuleLLM Investors**:
```
perceive() → extract market_data from inbounds
decide()   → build system prompt (PERSONA + DECISION RULES) + user template
           → LLM API call (LangChainAPIInference)
           → parse <analysis>...</analysis><decision>JSON</decision>
           → extract action, bid_price, quantity, reasoning
act()      → execute trade; update cash/position
```

---

## 5. Architecture Diagram

```
RuleLLM Simulation Flow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Round N:

  Market (Rule-based, identical to Rule variant)
  ┌──────────────────────────────────────────────────┐
  │  perceive(): collect orders from all agents      │
  │  decide():  P(t+1) = P(t) + λD + γ(F-P) + ε     │
  │  act():     broadcast {price, fundamental, ...}  │
  └────────────────┬─────────────────────────────────┘
                   │ broadcast market_data
                   ▼
  ┌────────────────────────────────────────────────────────────────┐
  │  RuleLLM Investor (e.g., AnchoredTrader)                       │
  │                                                                │
  │  perceive(): store market_data                                 │
  │  decide():                                                     │
  │    system_prompt = "== PERSONA ==\n...\n== DECISION RULES ==\n..." │
  │    user_msg = RULELLM_USER_TEMPLATE.format(market_data)        │
  │    ┌──────────────────────────────────────────────┐           │
  │    │  LLM API (LangChainAPIInference)             │           │
  │    │  Input:  system_prompt + user_msg            │           │
  │    │  Output: <analysis>...</analysis>            │           │
  │    │          <decision>{"action":..., ...}</decision>        │
  │    └──────────────────────────────────────────────┘           │
  │    parse JSON → action, bid_price, quantity, reasoning         │
  │  act(): execute trade; update portfolio                        │
  └─────────────────────────────────────────────────── order ──►  │
                                                        to Market  │
                                                                   │
  (×5 agent types: AnchoredTrader, HistoricalAnchor,               │
    RationalUpdater, MomentumTrader, NoiseTrader)                  │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. Configuration Reference

Key Configuration Parameters (`configs/AnchoringEffect/RuleLLM/players.yml`):

| Parameter           | Config Path                | Value                        | Design Justification                                          |
|---------------------|----------------------------|------------------------------|---------------------------------------------------------------|
| `initial_price`     | `extras.initial_price`     | 105.0                        | Seeds 5% initial mispricing — implements sim-bases §3.1       |
| `fundamental_value` | `extras.fundamental_value` | 100.0                        | Rational price benchmark — sim-bases §3.1                     |
| `price_impact`      | `extras.price_impact`      | 0.01                         | Low λ sustains anchoring mispricings — sim-bases §3.1         |
| `mean_reversion`    | `extras.mean_reversion`    | 0.01                         | Low γ allows mispricings to persist — sim-bases §2.3          |
| `adjustment_factor` | `extras.adjustment_factor` | 0.3                          | AnchoredTrader α — must match DECISION RULES prompt           |
| `anchor_weight`     | `extras.anchor_weight`     | 0.5                          | HistoricalAnchor dampening — must match DECISION RULES prompt |
| `lookback`          | `extras.lookback`          | 60                           | Rolling average window — must match DECISION RULES prompt     |
| `entry_threshold`   | `extras.entry_threshold`   | 0.02                         | MomentumTrader signal threshold — must match prompt           |
| `trade_probability` | `extras.trade_probability` | 0.05                         | NoiseTrader activity level — must match prompt                |
| `lm_name`           | `extras.llm.lm_name`       | doubao-pro-32k               | LLM model for RuleLLM agents                                  |
| `sys_message`       | `extras.llm.sys_message`   | `prompts:RULELLM_{TYPE}_SYS` | Path to dual-section prompt constant                          |

---

## 7. Running Instructions

```
Execution:
  python examples/AnchoringEffect/RuleLLM/run_anchoringeffect_rulellm.py \
      -c configs/AnchoringEffect/RuleLLM/simulation.yml

Required environment variables:
  ARK_API_KEY: ByteDance Doubao API key (obtain from volcengine.com)
               Must be set in project root .env file

Expected runtime: ~5-15 minutes for 100 rounds (5 LLM agents × 100 rounds × API latency)
Output location:  EXPERIMENT/AnchoringEffect/RuleLLM/
```

---

## 8. Expected Behavior Patterns

| Phase                | Rounds    | Expected Agent Behavior                                                                                                            | Expected Price Dynamics                                                                 |
|----------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| Initialization       | 1–5       | AnchoredTrader sets anchor = first price (~105); all agents begin applying DECISION RULES                                          | Price near 105; LLM reasoning establishes rule understanding                            |
| Active Anchoring     | 6–40      | AnchoredTrader and HistoricalAnchor generating buy/sell pressure from biased targets; LLM follows rules with ±20% quantity freedom | Anchoring-induced deviation maintained; LLM quantity variance visible vs. Rule baseline |
| Rule Override Events | Scattered | Occasional rounds where LLM judgment departs from rule recommendation (quantity outside ±20% band or different action)             | Visible as outlier points on the LLM vs. Rule comparison chart                          |
| Convergence          | 60–100    | RationalUpdater consistently corrects mispricings; LLM rule adherence typically ≥80% of rounds                                     | Price drifts toward fundamental; deviation declines; close to Rule trajectory           |

---

## 9. References

No new theories are introduced in this variant. All theoretical foundations are defined in `simulation-bases.md §2`.

Cross-references:
- Anchoring and Insufficient Adjustment → `simulation-bases.md §2.1`, §4 — AnchoredTrader
- Expert Anchoring → `simulation-bases.md §2.2`, §4 — HistoricalAnchor
- Rational Expectations → `simulation-bases.md §2.4`, §4 — RationalUpdater
- Momentum → `simulation-bases.md §2.5`, §4 — MomentumTrader
- Noise Trading → `simulation-bases.md §2.6`, §4 — NoiseTrader
- Dual-section prompt format → `create-example-skill.md` — RuleLLM section
- Rule–judgment balance (±20%) → `simulation-bases.md §9` — Variant Comparison Preview (RuleLLM column)
