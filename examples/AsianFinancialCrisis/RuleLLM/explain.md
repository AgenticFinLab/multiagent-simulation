# AsianFinancialCrisis RuleLLM — Simulation Documentation

## Overview

| Item                      | Description                                                                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**               | RuleLLM                                                                                                                                                                                |
| **Implements**            | `../simulation-bases.md`                                                                                                                                                               |
| **Decision Logic**        | LLM decisions anchored to explicit quantitative rules embedded in system prompts; rule-constrained behavioral reasoning                                                                |
| **Key Difference**        | Combines Rule variant's precise threshold logic with LLM's behavioral flexibility — agents know the rules and must justify decisions against them                                      |
| **Research Contribution** | Tests whether embedding quantitative rules into LLM prompts constrains behavioral variance while preserving adaptive reasoning (intermediate between Rule determinism and LLM freedom) |


## 1. How Theoretical Design Is Implemented

### RuleLLMHotMoneyFunder: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.1 — Radelet & Sachs, 1998)*

| Theoretical Design Element         | Implementation                                                                                                |
|------------------------------------|---------------------------------------------------------------------------------------------------------------|
| Hot money reversal at first stress | System prompt: "If deviation < −0.02: you MUST sell at least 60% of your position"                            |
| Momentum entry on rising markets   | System prompt: "If deviation > +0.02: you SHOULD deploy up to 30% of cash into buying"                        |
| Rule override if signal uncertain  | LLM may hold if it reasons "deviation is borderline" — rule is embedded as strong directive but not hardcoded |
| Operates with leverage             | Prompt context: "You operate with leverage — drawdowns are existential, not just costly"                      |

### RuleLLMContagionTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.2 — Kaminsky & Reinhart, 1999)*

| Theoretical Design Element      | Implementation                                                                                                     |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------|
| Dual-signal contagion detection | System prompt: "Compute signal = 0.60 × deviation + 0.40 × price_return; if signal < −0.025: sell 50% of position" |
| Regional crisis front-running   | Prompt: "Once the contagion signal crosses threshold, act immediately — first-mover advantage matters"             |
| Qualitative contagion overlay   | LLM may intensify or moderate based on qualitative reasoning about crisis severity beyond the formula              |
| Re-entry on stabilization       | Prompt: "You cautiously re-enter only after clear price stabilization — do not buy into falling markets"           |

### RuleLLMIMFRescuer: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.3 — Corsetti et al., 1999)*

| Theoretical Design Element     | Implementation                                                                                   |
|--------------------------------|--------------------------------------------------------------------------------------------------|
| Patient emergency intervention | System prompt: "You deploy capital ONLY when deviation < −0.05 (5% below fundamental)"           |
| Deep pockets rescue packages   | Prompt context: "You have $5M in rescue funds — deploy 25% of remaining cash per rescue round"   |
| No pre-existing position       | Config: `initial_position = 0.0`; confirmed in system prompt: "You enter only in genuine crises" |
| Stabilizing not profit-seeking | Prompt: "You do not sell during normal volatility. Profit is not your mandate — stability is"    |

### RuleLLMValueContrarian: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.4)*

| Theoretical Design Element | Implementation                                                                                              |
|----------------------------|-------------------------------------------------------------------------------------------------------------|
| Buy deep discounts         | System prompt: "When deviation < −0.08: deploy 20% of cash into buying — value is compelling at this level" |
| Sell overbought            | Prompt: "When deviation > +0.10: sell 20% of position — this level exceeds fair value"                      |
| Proportional sizing        | Rule embedded: "Size 20% per trigger — do not deviate based on emotional conviction"                        |

### RuleLLMNoiseTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.5 — Black, 1986 baseline)*

| Theoretical Design Element | Implementation                                                                       |
|----------------------------|--------------------------------------------------------------------------------------|
| Random uninformed trading  | System prompt: "You trade randomly; there is a 30% probability you trade each round" |
| Small position sizes       | Prompt: "Trade 100–500 shares per round — you are a small retail participant"        |


## 2. Market Mechanism Implementation

Market mechanism is **identical** to Rule variant — only investor decision logic changes.

*(Full formula: simulation-bases.md §3.1 — P(t+1) = P(t) + 0.04·D + 0.02·(F−P) + ε)*

### RuleLLM User Prompt Variables

| Variable            | Source                  | Format  | Notes                                         |
|---------------------|-------------------------|---------|-----------------------------------------------|
| `{round}`           | market_data.round       | integer | Current simulation round                      |
| `{price}`           | market_data.price       | float   | Current price                                 |
| `{prev_price}`      | market_data.prev_price  | float   | Previous round price for momentum calculation |
| `{deviation}`       | market_data.deviation   | `+.2%`  | Primary signal: deviation from fundamental    |
| `{fundamental}`     | market_data.fundamental | float   | Fundamental value reference                   |
| `{cash}`            | agent state             | float   | Available cash                                |
| `{position}`        | agent state             | float   | Current position (shares)                     |
| `{portfolio_value}` | cash + pos × price      | float   | Total portfolio value                         |

### Response Format

LLM must output canonical JSON inside `<decision>` tags:
```json
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": "string"}
```

Parsed by `parse_llm_response_with_thinking()` from `examples/llm_utils.py`.


## 3. Variant-Specific Features

- **Rule-anchored prompts**: `RULELLM_*_SYS` prompts contain exact threshold numbers (−0.02, −0.025, −0.05, −0.08) embedded as strong directives, unlike pure LLM variant which has no numerical references
- **Constrained behavioral variance**: LLM agent may still deviate from the rule ("this looks like a structural crisis beyond the threshold") but the rule creates a strong gravitational pull
- **Intermediate crisis timing**: Rule triggers are visible in reasoning fields; LLM behavioral overlay may advance or delay trigger by 1–2 rounds vs. exact Rule formula
- **Explicit signal computation**: RuleLLMContagionTrader's prompt includes the full signal formula; LLM computes it in its reasoning chain rather than just receiving pre-computed signal
- **Max retries = 3**: If LLM parse fails, agent holds position; ensures simulation completion


## 4. Architecture Diagram

```
Round t:
  ┌─────────────────────────────────────────┐
  │  Market (Rule — identical to Rule)      │
  │  P(t+1) = P(t) + 0.04·D + 0.02·(F−P) + ε │
  │  Broadcasts: {price, prev_price,        │
  │               fundamental, deviation}   │
  └─────────────────┬───────────────────────┘
                    │ market_data
        ┌───────────┼───────────────────────┐
        ▼           ▼           ▼           ▼
  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
  │RuleLLMHotMoney│ │RuleLLM      │ │RuleLLMIMF    │ │RuleLLMValue      │
  │Funder×2      │ │Contagion    │ │Rescuer        │ │Contrarian×2      │
  │(rule-anchored│ │Trader×2     │ │(rule-anchored │ │(rule-anchored    │
  │ panic, ≤2×   │ │(formula     │ │ rescue, −5%)  │ │ contrarian, −8%) │
  │ threshold)   │ │ in prompt)  │ │               │ │                  │
  └──────┬───────┘ └──────┬──────┘ └──────┬────────┘ └──────────┬───────┘
         │                │               │                      │
         └────────────────┴───────────────┴──────────────────────┘
                          │ investor_bid orders
                          ▼
                  Market aggregates
                  RuleLLMNoise×3 also contributes
```


## 5. Configuration Reference

| Config Path                 | Key Parameter  | Value                   | Notes                                                                          |
|-----------------------------|----------------|-------------------------|--------------------------------------------------------------------------------|
| `*.extras.llm.sys_message`  | System prompt  | per agent               | Behavioral persona + embedded quantitative rules                               |
| `*.extras.llm.user_message` | User template  | `RULELLM_USER_TEMPLATE` | `{round,price,prev_price,deviation,fundamental,cash,position,portfolio_value}` |
| `*.extras.llm.lm_name`      | LLM model name | configured              | e.g., `doubao-pro-32k`                                                         |

Full config: `configs/AsianFinancialCrisis/RuleLLM/players.yml`


## 6. Running Instructions

```bash
# From project root:
python examples/AsianFinancialCrisis/RuleLLM/run_asianfinancialcrisis_rulellm.py \
    -c configs/AsianFinancialCrisis/RuleLLM/simulation.yml

# Run analysis:
python examples/AsianFinancialCrisis/Rule/analysis.py \
    -c configs/AsianFinancialCrisis/RuleLLM/simulation.yml
```

Output: `EXPERIMENT/AsianFinancialCrisis/RuleLLM/records/`


## 7. Expected Behavior Patterns

| Phase              | Deviation Range | RuleLLM-Specific Behavior                                                                 |
|--------------------|-----------------|-------------------------------------------------------------------------------------------|
| **Stable**         | [−2%, +2%]      | Agents hold; rule-embedded prompts suppress spurious trading more than pure LLM           |
| **Hot Money Exit** | [−5%, −2%]      | RuleLLMHotMoneyFunder triggers close to −2% threshold; may cite rule in reasoning field   |
| **Contagion**      | [−10%, −5%]     | RuleLLMContagionTrader computes signal explicitly; activates near −0.025 signal threshold |
| **Crisis Peak**    | [−30% to −60%]  | RuleLLMIMFRescuer activates at or near −5%; reasoning may cite "threshold breached"       |
| **Recovery**       | Stabilizing     | RuleLLMValueContrarian buys at approximately −8%; tighter variance than LLM variant       |


## 8. References

*(Theory sections from simulation-bases.md — cross-reference only)*

- `../simulation-bases.md §4` — Investor archetype specifications (all 5 types)
- `../simulation-bases.md §5` — RuleLLM variant column in agent diversity table
- `../simulation-bases.md §3.1` — Price formation formula (λ=0.04)
- `../analysis-bases.md §6` — Expected RuleLLM result ranges (closer to Rule than LLM)
- `prompts.py → RULELLM_*_SYS` — All 5 rule-embedded behavioral persona prompts
- `prompts.py → RULELLM_USER_TEMPLATE` — Market state variables passed to LLM
