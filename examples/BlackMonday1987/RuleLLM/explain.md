# BlackMonday1987 RuleLLM — Implementation Explanation

## Overview

| Item                                   | Description                                                                                                                                                                            |
|----------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | RuleLLM (formula-anchored hybrid)                                                                                                                                                      |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                                               |
| **Decision Logic**                     | LLM with embedded quantitative decision rules — LLM follows formula-determined sign, adjusts quantity ±20% via persona judgment                                                        |
| **Key Difference from Other Variants** | Combines Rule feedback amplification with LLM reasoning; crash direction is rule-determined, but cascade magnitude has ±20% LLM variance                                               |
| **Primary Research Contribution**      | Does quantitative rule anchoring constrain LLM portfolio insurance to near-deterministic crash behavior, or does persona judgment introduce meaningful variation in cascade magnitude? |

---

## 1. How Theoretical Design Is Implemented

### PortfolioInsurer: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — PortfolioInsurer)*

| Theoretical Design Element                                   | Implementation                                                                                    |
|--------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| Dynamic hedging formula → sim-bases §4 Rule-Based Behavior   | `RULELLM_PORTFOLIO_INSURER_SYS` `== DECISION RULES ==`: Step 2 sell proportional to hedge_ratio × |
| rebalance_threshold = ±0.02 → sim-bases §6                   | Hard-coded in prompt: "IF deviation < -0.02 → SELL"; "IF deviation > +0.02 → BUY"                 |
| Cap at 1500 sell, 500 buy → sim-bases §4 Rule-Based Behavior | Rule: "Cap at 1500 shares. Never sell more than position"; "Cap at 500 shares"                    |
| PERSONA: protection discipline → sim-bases §4 LLM Persona    | `== PERSONA ==`: "mechanical and disciplined — capital protection overrides all concerns"         |
| ±20% quantity range → sim-bases §4 RuleLLM Hybrid Notes      | Step 3 in prompt: "PERSONA may adjust quantity ±20%"                                              |

### IndexArbitrageur: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — IndexArbitrageur)*

| Theoretical Design Element                                | Implementation                                                                                         |
|-----------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| Fixed position_size rule → sim-bases §4                   | `RULELLM_INDEX_ARBITRAGEUR_SYS`: "IF deviation > +0.005 → SELL ≈500; IF deviation < -0.005 → BUY ≈500" |
| ±20% → 400–600 shares range → sim-bases §4 RuleLLM Hybrid | Step 3: "PERSONA (speed urgency) may adjust quantity ±20% (400–600 shares)"                            |

### ProgramTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — ProgramTrader)*

| Theoretical Design Element                                | Implementation                                                                 |
|-----------------------------------------------------------|--------------------------------------------------------------------------------|
| Feedback amplification formula → sim-bases §4 Rule-Based  | `RULELLM_PROGRAM_TRADER_SYS`: "sell_qty = sell_size × (1 + feedback_strength × |
| trigger_threshold = 0.01 → sim-bases §6                   | Hard-coded: "IF deviation < -0.01 → SELL [amplified formula]"                  |
| PERSONA: no emotional override → sim-bases §4 LLM Persona | `== PERSONA ==`: "no emotional override; systematic; momentum-following"       |

### ValueInvestor: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — ValueInvestor)*

| Theoretical Design Element                                | Implementation                                                         |
|-----------------------------------------------------------|------------------------------------------------------------------------|
| value_discount = 0.15, order_size = 800 → sim-bases §6    | `RULELLM_VALUE_INVESTOR_SYS`: "IF deviation < -0.15 → BUY ≈800 shares" |
| ±20% → 640–960 shares range → sim-bases §4 RuleLLM Hybrid | Step 3: "PERSONA (contrarian conviction) may adjust ±20% (640–960)"    |

### NoiseTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — NoiseTrader)*

| Theoretical Design Element                        | Implementation                                                          |
|---------------------------------------------------|-------------------------------------------------------------------------|
| 5% trade probability rule → sim-bases §4          | `RULELLM_NOISE_TRADER_SYS`: "IF random draw < 5% → trade; ELSE → HOLD"  |
| Random direction, 100–500 quantity → sim-bases §6 | Step 2: "quantity = random.randint(100, 500); direction = random 50/50" |

---

## 2. Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Market class identical to Rule variant (imported). See Rule `explain.md §2` for variable mapping.

`RULELLM_USER_TEMPLATE` instructs: "Apply your DECISION RULES step-by-step."

---

## 3. Variant-Specific Features

*(Reference: simulation-bases.md §9 — RuleLLM variant entry)*

**Feedback amplification preserved**: ProgramTrader's amplification formula is embedded in the DECISION RULES section. The LLM must execute it step-by-step, ensuring the feedback loop is maintained even in the hybrid variant.

**Rule adherence target**: `analysis.py → analyze_rule_adherence()` measures directional agreement. Target ≥80%. ProgramTrader and PortfolioInsurer should show near-perfect adherence (clear threshold formulas). IndexArbitrageur may show lower adherence near the threshold boundary.

**Cascade depth variation**: ±20% quantity adjustment on each agent creates compound variation in cascade depth. If all agents adjust +20%, crash is 20% deeper than Rule; if all adjust −20%, 20% shallower.

---

## 4. Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║  Market (Rule-identical) → broadcasts market state                    ║
║                                                                       ║
║  Each RuleLLMInvestor.decide():                                       ║
║    → builds message from RULELLM_USER_TEMPLATE                       ║
║    → LLM executes Steps 1-2 (rule formula) in <analysis>             ║
║    → LLM adjusts quantity ±20% via persona in <analysis>             ║
║    → outputs <decision>{"action","bid_price","quantity",...}</decision>║
║                                                                       ║
║  == PERSONA == + == DECISION RULES == → semi-deterministic cascade   ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 5. Configuration Reference

Key Configuration Parameters (`configs/BlackMonday1987/RuleLLM/players.yml`):

| Parameter         | Config Path              | Value                                                    | Design Justification                       |
|-------------------|--------------------------|----------------------------------------------------------|--------------------------------------------|
| `price_impact`    | `extras.price_impact`    | 0.002                                                    | Identical to Rule                          |
| `sys_prompt_path` | `extras.sys_prompt_path` | `examples.BlackMonday1987.RuleLLM.prompts:RULELLM_*_SYS` | Dual-section prompt module path            |
| `llm.temperature` | `extras.llm.temperature` | 0.3                                                      | Low temperature — closer to rule-following |

---

## 6. Running Instructions

```bash
export ARK_API_KEY="your-bytedance-ark-api-key"
python examples/BlackMonday1987/RuleLLM/run_blackmonday1987_rulellm.py \
    -c configs/BlackMonday1987/RuleLLM/simulation.yml
```

Required environment variables: `ARK_API_KEY`

Expected runtime: ~5–20 minutes for 100 rounds

Output location: `EXPERIMENT/BlackMonday1987/RuleLLM/`

---

## 7. Expected Behavior Patterns

| Phase            | Rounds | Expected Agent Behavior                                                        | Expected Price Dynamics                                   |
|------------------|--------|--------------------------------------------------------------------------------|-----------------------------------------------------------|
| Pre-Crash        | 1–10   | All agents hold per rules; LLM confirms with Step 1-2 calculation visible      | Price near 100; identical to Rule baseline                |
| Feedback Onset   | 5–15   | PortfolioInsurer triggers at −2% per rule; ProgramTrader at −1%; ±20% quantity | Near-Rule crash onset; slight cascade magnitude variation |
| Crash Escalation | 10–25  | ProgramTrader feedback amplification executed in reasoning; ±20% range active  | Crash depth within ±20% of Rule; pattern similar          |
| Recovery         | 35–100 | ValueInvestor BUYs at −15% per rule; mean reversion; recovery near-Rule        | Recovery trajectory near-Rule                             |

---

## 8. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Feedback amplification formula embedded in prompts → `simulation-bases.md §4 (Rule-Based Behavior — ProgramTrader)`
- RuleLLM quantity ranges → `simulation-bases.md §4 (RuleLLM Hybrid Notes per investor type)`
- Rule adherence analysis → `analysis.py → analyze_rule_adherence()` (target ≥80%)
- Price formula → `simulation-bases.md §3.1`
