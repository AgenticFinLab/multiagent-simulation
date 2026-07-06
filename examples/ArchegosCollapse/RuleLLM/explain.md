# ArchegosCollapse RuleLLM — Implementation Explanation

## §1 Overview

| Item                                   | Description                                                                                                                                                             |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | RuleLLM (formula-anchored hybrid)                                                                                                                                       |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                                |
| **Decision Logic**                     | LLM with embedded quantitative decision rules — LLM follows formula-determined sign, adjusts quantity ±20% via persona judgment                                         |
| **Key Difference from Other Variants** | Combines Rule predictability with LLM narrative reasoning; rules constrain the LLM's direction but LLM controls magnitude within bounds                                 |
| **Primary Research Contribution**      | Does quantitative rule grounding constrain LLM behavior to near-deterministic outcomes, or does persona judgment introduce meaningful deviation from the Rule baseline? |

---

## §2 Theory → Implementation Mapping

### ConcentratedFund: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.1 — ConcentratedFund)*

| Theory Component                                                      | Implementation                                                                                   |
|-----------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| TRS leverage / margin call → sim-bases §4.N.5.4 Mathematical Model         | `RULELLM_CONCENTRATED_FUND_SYS` `== DECISION RULES ==`: Step 2 `IF deviation < -0.15 → SELL 50%` |
| Embedded rule threshold = −0.15 → sim-bases §6                        | Hard-coded in prompt: "IF deviation < -0.15 (price dropped >15% below fundamental)"              |
| Sell 50% base, ±20% PERSONA range → sim-bases §4 RuleLLM Hybrid Notes | "Step 3: PERSONA may adjust quantity ±20% (40%–60% of position)"                                 |
| Denial psychology → sim-bases §4 LLM Persona                          | `== PERSONA ==`: "denial is your first response"; emotionally resistant to acknowledging margin  |
| Prompt constant                                                       | `RULELLM_CONCENTRATED_FUND_SYS` in `prompts.py`                                                  |

### PrimeBroker1: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.2 — PrimeBroker1)*

| Theory Component                                        | Implementation                                                                     |
|---------------------------------------------------------|------------------------------------------------------------------------------------|
| Lower threshold (first-mover) = −0.10 → sim-bases §4    | `== DECISION RULES ==`: "IF deviation < -0.10 → SELL 40% of position"              |
| Sell 40% base, ±20% → sim-bases §4 RuleLLM Hybrid Notes | "Step 3: PERSONA (speed urgency) may adjust quantity ±20% (32%–48%)"               |
| Aggressive / unsentimental → sim-bases §4 LLM Persona   | `== PERSONA ==`: "decisive, competitive, unsentimental about client relationships" |

### PrimeBroker2: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.3 — PrimeBroker2)*

| Theory Component                                                   | Implementation                                                                                   |
|--------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|
| Higher threshold (second-mover) = −0.15 → sim-bases §4             | `== DECISION RULES ==`: "IF deviation < -0.15 → SELL 35%"; "effective_bid_price = market × 0.97" |
| Price penalty embedded in rule → sim-bases §4 RuleLLM Hybrid Notes | Rule instructs: "effective_bid_price = market_price × 0.97"                                      |
| Delayed but deliberate persona → sim-bases §4 LLM Persona          | `== PERSONA ==`: "slower and more conservative, but equally unsentimental once you decide"       |

### BlockTradeBuyer: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.4 — BlockTradeBuyer)*

| Theory Component                                         | Implementation                                                                       |
|----------------------------------------------------------|--------------------------------------------------------------------------------------|
| Buy at −10% discount → sim-bases §4.N.5.4 Mathematical Model  | `== DECISION RULES ==`: "IF deviation < -0.10 → BUY: quantity = 0.30 × cash / price" |
| Deploy 30% cash base, ±20% → sim-bases §4 RuleLLM Hybrid | "Step 3: PERSONA (deep-pocket buyer) may adjust ±20% (24%–36%)"                      |
| Deep-pocket patience persona → sim-bases §4 LLM Persona  | `== PERSONA ==`: "you have deep pockets and patience — wait for forced sellers"      |

### InformationTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.5 — InformationTrader)*

| Theory Component                                                  | Implementation                                                                                      |
|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| Detect at −0.05, probability 0.50 → sim-bases §4 Mathematical Model       | `== DECISION RULES ==`: "IF deviation < -0.05 AND detection probability 0.50 → SELL min(1000, pos)" |
| Cover at −0.03 → sim-bases §4                                     | `== DECISION RULES ==`: buy up to 500 shares when recovery conditions indicate prior front-run exposure should be covered |
| Front-runner / fast analytical persona → sim-bases §4 LLM Persona | `== PERSONA ==`: "fast, analytical, and unafraid of being early"                                    |

---

## §3 Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py` — same `Market` class imported from `Rule.players`:
```python
from examples.ArchegosCollapse.Rule.players import Market
```

Code translation: Identical to Rule variant. See Rule `explain.md §2` for variable mapping.

User template: `RULELLM_USER_TEMPLATE` explicitly instructs "Apply your DECISION RULES step-by-step. Show your calculations in `<analysis>...</analysis>`." This reinforces the quantitative rule-following behavior.

Deviations from simulation-bases.md design: None in market mechanics.

---

## §4 Variant-Specific Features

*(Reference: simulation-bases.md §9 — RuleLLM variant entry)*

**Dual-section prompt structure**: Every system prompt has mandatory `== PERSONA ==` and `== DECISION RULES ==` sections. The DECISION RULES section contains the exact quantitative formula from Rule variant, embedded directly in the prompt. The LLM must execute Steps 1–3 in sequence.

**Rule-sign binding**: Step 2 in each DECISION RULES section determines buy/sell/hold. Step 3 allows only ±20% quantity adjustment. This means the cascade direction is deterministic (same as Rule), but intensity may vary.

**User template reinforcement**: `RULELLM_USER_TEMPLATE` ends with "Apply your DECISION RULES step-by-step. Show your calculations in `<analysis>...</analysis>`." — forces explicit step-by-step calculation visible in output.

**Rule adherence measurement**: `analysis.py → analyze_rule_adherence()` measures whether LLM directional decisions match the expected Rule formula direction. Target ≥80% directional alignment per agent.

**Semi-deterministic cascade timing**: Unlike LLM variant, ConcentratedFund must sell when `deviation < -0.15` is embedded as a rule. The LLM cannot "choose to hold" based on denial psychology alone — the rule overrides.

---

## §5 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market (Rule-identical) → broadcasts market state                    ║
║                                                                       ║
║  Each RuleLLMInvestor.decide():                                       ║
║    → builds user_message from RULELLM_USER_TEMPLATE                  ║
║    → calls LangChainAPIInference(sys_prompt, user_message)  ──→ LLM  ║
║    → LLM executes Steps 1-2 (rule formula) in <analysis>             ║
║    → LLM adjusts quantity ±20% based on persona in <analysis>        ║
║    → outputs <decision>{"action","bid_price","quantity",...}</decision>║
║                                                                       ║
║  Rule-sign binding:                                                   ║
║    deviation < threshold? → SELL [±20% quantity]                     ║
║    deviation ≥ threshold? → HOLD                                     ║
║    (BlockTradeBuyer: deviation < -0.10? → BUY [±20%])               ║
╚══════════════════════════════════════════════════════════════════════╝

Prompt Structure:
  == PERSONA ==           (who the agent is, emotional profile)
  == DECISION RULES ==    (exact formula: Step 1 → Step 2 → Step 3)
  OUTPUT FORMAT           (canonical JSON)
```

---

## §6 Configuration Reference

Key Configuration Parameters (`configs/ArchegosCollapse/RuleLLM/players.yml`):

| Parameter | Config Path | Value | Design Justification |
|---|---|---|---|
| `price_impact` | `extras.price_impact` | 0.03 | Identical to Rule — comparable market dynamics |
| `mean_reversion` | `extras.mean_reversion` | 0.01 | Same low gamma — cascade persistence |
| `sys_message` | `extras.llm.sys_message` | `examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_*_SYS` | Module path for dual-section prompts |
| `user_message` | `extras.llm.user_message` | `examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE` | Module path for market-state user template |
| `lm_name` | `extras.llm.lm_name` | `ark/doubao-seed-2-0-mini-260428` | ByteDance Ark Doubao model |
| `temperature` | `extras.llm.generation_config.temperature` | 0.4-0.5 | Low temperature — closer to deterministic rule-following |

---

## §7 Running Instructions

```bash
export ARK_API_KEY="your-bytedance-ark-api-key"
python examples/ArchegosCollapse/RuleLLM/run_archegsoscollapse_rulellm.py \
    -c configs/ArchegosCollapse/RuleLLM/simulation.yml
```

Required environment variables:
- `ARK_API_KEY`: ByteDance Doubao API key

Expected runtime: ~5–20 minutes for 200 rounds

Output location: `EXPERIMENT/ArchegosCollapse/RuleLLM/`

---

## §8 Expected Behavior Patterns

| Phase         | Rounds | Expected Agent Behavior                                                             | Expected Price Dynamics                                       |
|---------------|--------|-------------------------------------------------------------------------------------|---------------------------------------------------------------|
| Pre-Cascade   | 1–15   | All agents hold; rules not triggered; LLM confirms hold with formula verification   | Price near 100; normal noise                                  |
| Cascade Onset | 10–20  | ConcentratedFund triggers at −15% per rule; PrimeBroker1 at −10%; LLM ±20% quantity | Near-Rule cascade timing; slightly variable cascade magnitude |
| Peak Cascade  | 20–35  | PrimeBroker2 triggers at −15%; quantity within 28%–42% range; BlockTradeBuyer BUYs  | Similar depth to Rule; ±20% magnitude variation               |
| Recovery      | 35–100 | BlockTradeBuyer absorbs; InformationTrader covers per rule; mean reversion          | Comparable recovery to Rule                                   |

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Rule formula thresholds embedded in prompts → `simulation-bases.md §4.N.5.4 Mathematical Model per investor type`
- RuleLLM hybrid quantity range → `simulation-bases.md §4 (RuleLLM Hybrid Notes per investor type)`
- Rule adherence analysis → `analysis.py → analyze_rule_adherence()` (target ≥80%)
- Dual-section prompt requirement → `implement-simulation-skill.md §{RuleLLM Prompts Design}`
- Price formula → `simulation-bases.md §3.1`
- Full parameter table → `simulation-bases.md §6`
