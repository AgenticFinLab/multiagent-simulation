# CarryTradeUnwind RuleLLM — Implementation Explanation

## §1 Overview

| Item                              | Description                                                                                                                                              |
|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                       | RuleLLM (hybrid: LLM reasoning anchored to explicit quantitative rules)                                                                                  |
| **Implements**                    | `../simulation-bases.md`                                                                                                                                 |
| **Decision Logic**                | LLM agents with carry trade personas + explicit numerical rules embedded in `== DECISION RULES ==` section of every system prompt                        |
| **Key Difference from LLM**       | Every system prompt contains exact thresholds and formulas from Rule variant; LLM must follow rule sign (buy/sell/hold) with ≤ ±20% quantity adjustment  |
| **Primary Research Contribution** | Isolate effect of language reasoning: with identical quantitative constraints embedded in prompt, does LLM reasoning alter carry trade cascade dynamics? |

---

## §2 How Theoretical Design Is Implemented

### §2.1 CarryTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Threshold response from simulation-bases.md §4.1.4 | `RULELLM_CARRY_TRADER_SYS` embeds buy when deviation > +0.02, sell when deviation < -0.02, otherwise hold. |
| Quantity model from simulation-bases.md §4.1.4.3 | Prompt uses `min(800, deviation×5000)` / `min(800, |deviation|×5000)` and player clamps to cash or position. |
| RuleLLM quantity discretion from simulation-bases.md §9 | Prompt permits at most ±20% quantity adjustment while preserving the rule-implied action sign. |

### §2.2 LeveragedCarryFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Forced liquidation from simulation-bases.md §4.2.4 | `RULELLM_LEVERAGED_CARRY_FUND_SYS` embeds immediate sell when deviation breaches stop-loss. |
| Position cap from simulation-bases.md §4.2.4.3 | Prompt states `min(800×leverage, position)` and player clamps to current position. |
| Forced-exit discipline from simulation-bases.md §4.2.3 | Prompt allows quantity judgment but forbids overriding the forced-sell sign. |

### §2.3 FundingCurrencyBuyer (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Safe-haven activation from simulation-bases.md §4.3.4 | `RULELLM_FUNDING_CURRENCY_BUYER_SYS` embeds buy when deviation < -0.05 and sell when deviation > +0.05. |
| Stabilizer capacity from simulation-bases.md §6 | Prompt uses position size around 500 and player enforces cash/position constraints. |

### §2.4 HedgedCarryTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Volatility-adjusted carry from simulation-bases.md §4.4.4 | `RULELLM_HEDGED_CARRY_TRADER_SYS` acts only when absolute deviation exceeds the 0.05 threshold. |
| Hedge-ratio sizing from simulation-bases.md §4.4.4.3 | Prompt uses `500 × (1 - hedge_ratio) ≈ 350`, then player clamps to cash or position. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Non-systematic FX flow from simulation-bases.md §4.5.4 | `RULELLM_NOISE_TRADER_SYS` encodes random low-conviction participation around 30% of rounds. |
| Bounded order size from simulation-bases.md §6 | Prompt uses 100-500 unit orders and player enforces cash/position constraints. |

---

## §3 Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1 — identical to Rule variant.*

Market is copied from `examples.CarryTradeUnwind.Rule.players:Market`. No changes.

Broadcast: `{price, fundamental, deviation, round}` — no `return_pct` (see simulation-bases.md §7).

---

## §4 Variant-Specific Features

*(Reference: simulation-bases.md §9 — RuleLLM variant entry)*

**Dual-section system prompt structure**: Every system prompt has two mandatory labeled sections:
```
== PERSONA ==
[Carry trade personality — who the agent is, risk style, behavioral tendencies]

== DECISION RULES ==
[Exact formulas and thresholds from Rule variant, expressed in plain text]
[Step-by-step decision procedure]
[Quantity adjustment instructions: ±20% allowed]
```

**Rule fidelity enforcement**: The `== DECISION RULES ==` section explicitly states:
- "You MUST follow the BUY/SELL/HOLD sign from the rules above"
- "You may adjust quantity by at most ±20% based on your judgment"
- For LeveragedCarryFund: "The FORCED SELL condition must be followed strictly — no overrides"

**Prompt source**: `examples/CarryTradeUnwind/RuleLLM/prompts.py`
- `RULELLM_CARRY_TRADER_SYS`
- `RULELLM_LEVERAGED_CARRY_FUND_SYS`
- `RULELLM_FUNDING_CURRENCY_BUYER_SYS`
- `RULELLM_HEDGED_CARRY_TRADER_SYS`
- `RULELLM_NOISE_TRADER_SYS`

**No `return_pct` in rules**: Since market doesn't broadcast `return_pct`, all embedded rules use only `deviation` — consistent with Rule variant formulas.

---

## §5 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market (Rule) → broadcast {price, fundamental, deviation, round}    ║
║                                                                       ║
║  RuleLLMCarryTrader:                                                  ║
║    [== PERSONA ==] carry trader personality                           ║
║    [== DECISION RULES ==] |deviation| > 0.02 → BUY/SELL formula     ║
║    LLM reasons within rule constraints → {action, quantity}           ║
║                                                                       ║
║  RuleLLMLeveragedCarryFund:                                           ║
║    [== DECISION RULES ==] FORCED SELL at deviation < -0.02           ║
║    LLM must comply — ±20% qty adjustment only                         ║
║                                                                       ║
║  [Same pattern for FCB, HCT, NT]                                      ║
║         │                                                             ║
║         └──── send orders → Market.perceive() [next round]           ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## §6 Configuration Reference

Key RuleLLM-specific parameters (`configs/CarryTradeUnwind/RuleLLM/players.yml`):

| Parameter     | Config Path              | Value  | Notes                                                  |
|---------------|--------------------------|--------|--------------------------------------------------------|
| `model`       | `extras.llm.model`       | varies | Same LLM as LLM variant                                |
| `temperature` | `extras.llm.temperature` | 0.3    | Low temperature ensures rule compliance                |
| `max_tokens`  | `extras.llm.max_tokens`  | 512    | Sufficient for rule + reasoning + decision             |
| Market params | same as Rule             | same   | Identical market dynamics to Rule baseline             |
| Agent params  | same as Rule             | same   | Same initial cash/position as Rule for fair comparison |

---

## §7 Running Instructions

```bash
python examples/CarryTradeUnwind/RuleLLM/run_carrytradeunwind_rulellm.py \
    -c configs/CarryTradeUnwind/RuleLLM/simulation.yml
```

Then analyze:
```bash
python examples/CarryTradeUnwind/RuleLLM/analysis.py \
    -c configs/CarryTradeUnwind/RuleLLM/simulation.yml
```

Required environment variables: LLM API key

Expected runtime: ~5–30 minutes for 100 rounds

Output location: `EXPERIMENT/CarryTradeUnwind/RuleLLM/records/`

---

## §8 Expected Behavior Patterns

| Phase        | Rounds | Expected RuleLLM Agent Behavior                                                | Expected Price Dynamics                                |
|--------------|--------|--------------------------------------------------------------------------------|--------------------------------------------------------|
| Pre-Unwind   | 1–10   | Agents hold; rule says hold; LLM concurs with reasoning                        | Price near 1.0; similar to Rule baseline               |
| Early Unwind | 10–20  | LeveragedCarryFund rule triggers; LLM executes forced sell (rule compliance)   | Cascade onset similar to Rule; may be 1–3 rounds later |
| Peak Cascade | 20–35  | All agents follow embedded rules; LLM adds narrative to confirm rule execution | Similar depth to Rule; ≤ ±20% quantity deviation       |
| Recovery     | 35–100 | FundingCurrencyBuyer rule triggers at −5%; LLM may buy slightly more or less   | Near-Rule recovery speed                               |

**Expected adherence**: ≥ 80% directional alignment per agent (buy/sell/hold) with Rule baseline decisions.

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- RuleLLM construction principles → `create-example-skill.md § RuleLLM`
- Carry trade formulas embedded in prompts → `simulation-bases.md §5 — all agents`
- Dual-section prompt structure → `prompts.py` (PERSONA + DECISION RULES)
- Core analysis via Rule/analysis.py
- No `return_pct` in rules → `simulation-bases.md §7`
