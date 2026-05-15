# BlackMonday1987 LLM — Implementation Explanation

## Overview

| Item                                   | Description                                                                                                                                                                                |
|----------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | LLM (persona-driven stochastic)                                                                                                                                                            |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                                                   |
| **Decision Logic**                     | LLM prompts with behavioral personas — no explicit rules; all decisions from LLM reasoning                                                                                                 |
| **Key Difference from Other Variants** | Crash timing and depth are stochastic; key question is whether LLM mechanical-trading personas reproduce the disciplined automated selling of portfolio insurance and program trading      |
| **Primary Research Contribution**      | Do LLM-simulated automated strategy personas replicate the mechanical discipline of 1987 portfolio insurance and program trading, or do they introduce hesitation that prevents the crash? |

---

## 1. How Theoretical Design Is Implemented

### PortfolioInsurer: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — PortfolioInsurer)*

| Theoretical Design Element                                       | Implementation                                                                                                          |
|------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Capital protection mandate psychology → sim-bases §4 LLM Persona | `LLM_PORTFOLIO_INSURER_SYS`: "capital protection through dynamic rebalancing is more important than maximizing returns" |
| Mechanical, emotionally detached → sim-bases §4 LLM Persona      | "mechanical and risk-averse"; "emotionally detached from market narratives"                                             |
| Proportional sell sizing → sim-bases §4 LLM Persona              | "trades are proportional to how far prices have moved from reference point"                                             |
| Position size range 100–1500 → sim-bases §4 LLM Persona          | Prompt specifies ranges; LLM infers exact quantity from deviation context                                               |
| Prompt constant                                                  | `LLM_PORTFOLIO_INSURER_SYS` in `prompts.py`                                                                             |

### IndexArbitrageur: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — IndexArbitrageur)*

| Theoretical Design Element                                    | Implementation                                                         |
|---------------------------------------------------------------|------------------------------------------------------------------------|
| Speed-driven arbitrage psychology → sim-bases §4 LLM Persona  | `LLM_INDEX_ARBITRAGEUR_SYS`: "speed and decisiveness define your edge" |
| Systematic mispricing exploitation → sim-bases §4 LLM Persona | "scan for price dislocations"; "act decisively"                        |
| Position size range 50–800 → sim-bases §4 LLM Persona         | Prompt: "large opportunity: 400–800 shares"; "small signal: 50–200"    |

### ProgramTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — ProgramTrader)*

| Theoretical Design Element                                  | Implementation                                                                        |
|-------------------------------------------------------------|---------------------------------------------------------------------------------------|
| No emotional override → sim-bases §4 LLM Persona            | `LLM_PROGRAM_TRADER_SYS`: "emotional override is not in your programming"             |
| Amplify trends, never fight them → sim-bases §4 LLM Persona | "you amplify trends because your system is designed to follow momentum, not fight it" |
| Large position sizes → sim-bases §4 LLM Persona             | "you are designed for impact, not precision"; "800–1500 shares" for strong signal     |

### ValueInvestor: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — ValueInvestor)*

| Theoretical Design Element                                  | Implementation                                                                                |
|-------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Contrarian conviction → sim-bases §4 LLM Persona            | `LLM_VALUE_INVESTOR_SYS`: "market panics are your best opportunity, not your worst nightmare" |
| Margin of safety position sizing → sim-bases §4 LLM Persona | "maintain a margin of safety — never fully commit all capital at once"                        |
| Position size range 50–1000 → sim-bases §4 LLM Persona      | "extreme discount: 600–1000 shares"; "slight discount: 50–200"                                |

### NoiseTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4 — NoiseTrader)*

| Theoretical Design Element                                | Implementation                                                                            |
|-----------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Uninformed random-like trading → sim-bases §4 LLM Persona | `LLM_NOISE_TRADER_SYS`: "you do not have a clear strategy"; "trade based on gut instinct" |
| Background liquidity → sim-bases §4                       | "your behavior adds randomness and baseline liquidity"                                    |
| Small position sizes → sim-bases §4 LLM Persona           | "typical trade: 50–200 shares"; "larger impulse: 200–500"                                 |

---

## 2. Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py → Market` class (re-used from `Rule.players` via import)

User template variables (from `LLM_USER_TEMPLATE`): `{round}`, `{price}`, `{fundamental}`, `{deviation}`, `{cash}`, `{position}`, `{portfolio_value}` — note: no `{prev_price}` in BlackMonday1987 user template.

JSON parsing: `parse_llm_response_with_thinking()` extracts `<decision>{...}</decision>`.

Deviations from simulation-bases.md design: None in market mechanics. Investor decisions stochastic.

---

## 3. Variant-Specific Features

*(Reference: simulation-bases.md §9 — LLM variant entry)*

**Persona-only prompts**: No explicit thresholds in any system prompt. Tests whether "mechanical discipline" described in natural language reproduces threshold-like behavior organically.

**Critical LLM test**: ProgramTrader's persona says "emotional override is not in your programming." If the LLM genuinely treats this as mechanical, crash depth should be near-Rule. If LLM introduces judgment-based hesitation, crash will be shallower or delayed.

**Simultaneous decisions**: All 5 agents independently call the LLM each round — 5 API calls per round. Decision quality depends on each agent processing its own persona without coordination.

**API key**: `ARK_API_KEY` required.

---

## 4. Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market (Rule-identical) → broadcasts {price, fundamental,            ║
║                             deviation, round}                         ║
║                                                                       ║
║  Each LLMInvestor.decide():                                           ║
║    → builds user_message from LLM_USER_TEMPLATE                      ║
║    → calls LangChainAPIInference(sys_prompt, user_message)  ──→ LLM  ║
║    → parses <decision>{"action","bid_price","quantity",...}</decision> ║
║                                                                       ║
║  PortfolioInsurer:  "follow protection discipline" → SELL/BUY         ║
║  IndexArbitrageur:  "act decisively on mispricings" → SELL/BUY       ║
║  ProgramTrader:     "emotional override = none" → SELL large         ║
║  ValueInvestor:     "panics are opportunities" → BUY on dip          ║
║  NoiseTrader:       "gut instinct" → random direction                ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 5. Configuration Reference

Key Configuration Parameters (`configs/BlackMonday1987/LLM/players.yml`):

| Parameter         | Config Path              | Value                                            | Design Justification                                    |
|-------------------|--------------------------|--------------------------------------------------|---------------------------------------------------------|
| `price_impact`    | `extras.price_impact`    | 0.002                                            | Same as Rule — comparable crash mechanics               |
| `mean_reversion`  | `extras.mean_reversion`  | 0.02                                             | Same as Rule — comparable recovery dynamics             |
| `sys_prompt_path` | `extras.sys_prompt_path` | `examples.BlackMonday1987.LLM.prompts:LLM_*_SYS` | Module path for LLM personas                            |
| `llm.temperature` | `extras.llm.temperature` | 0.7                                              | Moderate stochasticity — reproduces persona variability |

---

## 6. Running Instructions

```bash
export ARK_API_KEY="your-bytedance-ark-api-key"
python examples/BlackMonday1987/LLM/run_blackmonday1987_llm.py \
    -c configs/BlackMonday1987/LLM/simulation.yml
```

Required environment variables:
- `ARK_API_KEY`: ByteDance Doubao API key

Expected runtime: ~5–20 minutes for 100 rounds (5 LLM calls per round)

Output location: `EXPERIMENT/BlackMonday1987/LLM/`

---

## 7. Expected Behavior Patterns

| Phase            | Rounds | Expected Agent Behavior                                                             | Expected Price Dynamics                                       |
|------------------|--------|-------------------------------------------------------------------------------------|---------------------------------------------------------------|
| Pre-Crash        | 1–15   | All agents hold or make small adjustments; ProgramTrader may have early triggers    | Price near 100; normal LLM-noise variation                    |
| Feedback Onset   | 5–20   | PortfolioInsurer begins selling; IndexArbitrageur joins; ProgramTrader may hesitate | First wave of selling; more gradual than Rule if hesitation   |
| Crash Escalation | 15–30  | ProgramTrader "algorithm fires"; PortfolioInsurer sells larger quantities           | Sharp decline; crash depth variable across runs               |
| Crash Peak       | 25–45  | ValueInvestor "excited by discount"; begins buying; NoiseTrader reacts variably     | Maximum drawdown; variable depth vs Rule                      |
| Recovery         | 40–100 | ValueInvestor continues buying; LLM agents begin "reassessing" positions            | Recovery variable; LLM may recover faster or slower than Rule |

---

## 8. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Portfolio insurance mechanical discipline psychology → `simulation-bases.md §2, §4 — PortfolioInsurer LLM Persona`
- Program trading "no override" persona → `simulation-bases.md §2, §4 — ProgramTrader LLM Persona`
- ValueInvestor contrarian conviction → `simulation-bases.md §2, §4 — ValueInvestor LLM Persona`
- Price formula → `simulation-bases.md §3.1`
- LLM variant stochastic crash dynamics → `simulation-bases.md §9 (LLM column)`
