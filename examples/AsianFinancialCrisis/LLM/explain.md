# AsianFinancialCrisis LLM — Simulation Documentation

## Overview

| Item                      | Description                                                                                                                                   |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**               | LLM                                                                                                                                           |
| **Implements**            | `../simulation-bases.md`                                                                                                                      |
| **Decision Logic**        | Persona-only LLM prompts; no embedded quantitative rules; behavioral archetypes drive decisions                                               |
| **Key Difference**        | Investors exhibit rich behavioral psychology (panic, patience, opportunism) without formula constraints                                       |
| **Research Contribution** | Tests whether pure behavioral personas — with no numerical rules — can reproduce contagion and crisis dynamics through emergent LLM reasoning |


## 1. How Theoretical Design Is Implemented

### LLMHotMoneyFunder: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §2.1 — Radelet & Sachs, 1998)*

| Theoretical Design Element         | Implementation                                                                        |
|------------------------------------|---------------------------------------------------------------------------------------|
| Opportunistic capital — quick exit | `LLM_HOT_MONEY_FUNDER_SYS`: "At the first whiff of instability...you rapidly reverse" |
| No loyalty to market               | Prompt: "You have no loyalty to any market or asset"                                  |
| Leveraged — cannot hold drawdowns  | Prompt: "You operate with leverage and cannot afford extended drawdowns"              |
| Falling price = contagion signal   | Prompt: "Negative price returns: potential contagion spreading, exit quickly"         |

### LLMContagionTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §2.2 — Kaminsky & Reinhart, 1999)*

| Theoretical Design Element    | Implementation                                                                                      |
|-------------------------------|-----------------------------------------------------------------------------------------------------|
| Dual signal monitoring        | Prompt: "You watch both price deviation from fundamentals AND recent price momentum simultaneously" |
| Front-running contagion       | Prompt: "You detect the first signs of cross-market selling and front-run the contagion wave"       |
| Momentum follower in declines | Prompt: "You are a momentum follower in declining markets — you amplify downward moves"             |
| Re-enter after stabilization  | Prompt: "You re-enter cautiously only after clear stabilization"                                    |

### LLMIMFRescuer: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §2.3 — Corsetti et al., 1999)*

| Theoretical Design Element    | Implementation                                                                                     |
|-------------------------------|----------------------------------------------------------------------------------------------------|
| Patient lender of last resort | Prompt: "You act as a lender of last resort...only deploy capital at extreme dislocations"         |
| No profit motive              | Prompt: "You do not sell during normal volatility — only reduce positions when markets normalized" |
| Deep discount trigger         | Prompt: "Large negative deviation (price well below fundamental): primary trigger for buying"      |
| Market floor signaling        | Prompt: "Your presence signals to other market participants that a floor exists"                   |

### LLMValueContrarian: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §2.4)*

| Theoretical Design Element      | Implementation                                                                     |
|---------------------------------|------------------------------------------------------------------------------------|
| Mean reversion conviction       | Prompt: "You trust that mean reversion is inevitable, even if timing is uncertain" |
| Emotionally detached from panic | Prompt: "You are emotionally detached from short-term noise and panic"             |
| Proportional conviction         | Prompt: "You size positions proportionally to the degree of mispricing"            |
| Buy on panic, sell on euphoria  | Prompt: "Strong negative deviation: attractive buying opportunity, deploy cash"    |

### LLMNoiseTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §2 — Black, 1986 baseline)*

| Theoretical Design Element | Implementation                                                                  |
|----------------------------|---------------------------------------------------------------------------------|
| Uninformed random trader   | Prompt: "You do not have a clear strategy — you trade because you feel like it" |
| Sometimes contrarian       | Prompt: "You might buy in a falling market, or sell in a rising one"            |


## 2. Market Mechanism Implementation

Market mechanism is **identical** to Rule variant — only investor decision logic changes.

*(Full formula: simulation-bases.md §3.1 — P(t+1) = P(t) + 0.04·D + 0.02·(F−P) + ε)*

### LLM User Prompt Variables

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

- **Persona-only prompts**: `LLM_*_SYS` prompts contain behavioral archetypes but zero numerical thresholds — decisions emerge from LLM's interpretation of deviation/price signals through persona lens
- **Variable crisis timing**: HotMoneyFunder may panic before −2% threshold or hold through −5%; ContagionTrader may detect contagion from qualitative reading of deviation alone
- **IMF rescue variation**: LLMIMFRescuer may intervene earlier ("this looks like a crisis") or later ("need deeper confirmation") than the exact −5% threshold
- **Behavioral denial risk**: LLMHotMoneyFunder may rationalize holding a losing position ("this is temporary noise") — contrasts with Rule's immediate mechanical exit
- **Max retries = 3**: If LLM parse fails, agent holds position; ensures simulation completion


## 4. Architecture Diagram

```
Round t:
  ┌─────────────────────────────────────────┐
  │  Market (Rule — identical to Rule)      │
  │  P(t+1) = P(t) + 0.04·D + ε            │
  │  Broadcasts: {price, prev_price,        │
  │               fundamental, deviation}   │
  └─────────────────┬───────────────────────┘
                    │ market_data
        ┌───────────┼───────────────────────┐
        ▼           ▼           ▼           ▼
  ┌────────────┐ ┌──────────┐ ┌────────────┐ ┌──────────────┐
  │LLMHotMoney │ │LLM       │ │LLMIMF      │ │LLMValue      │
  │Funder×2    │ │Contagion │ │Rescuer     │ │Contrarian×2  │
  │(persona    │ │Trader×2  │ │(patient    │ │(fundamentals │
  │ panic exit)│ │(contagion│ │ lender)    │ │ conviction)  │
  │            │ │ awareness│ │            │ │              │
  └─────┬──────┘ └────┬─────┘ └─────┬──────┘ └──────┬───────┘
        │             │             │               │
        └─────────────┴─────────────┴───────────────┘
                      │ investor_bid orders
                      ▼
              Market aggregates
              investor_bid → order (action/quantity)
              LLMNoise×3 also contributes
```


## 5. Configuration Reference

| Config Path                 | Key Parameter  | Value               | Notes                                                                          |
|-----------------------------|----------------|---------------------|--------------------------------------------------------------------------------|
| `*.extras.llm.sys_message`  | System prompt  | per agent           | Behavioral persona only                                                        |
| `*.extras.llm.user_message` | User template  | `LLM_USER_TEMPLATE` | `{round,price,prev_price,deviation,fundamental,cash,position,portfolio_value}` |
| `*.extras.llm.lm_name`      | LLM model name | configured          | e.g., `doubao-pro-32k`                                                         |

Full config: `configs/AsianFinancialCrisis/LLM/players.yml`


## 6. Running Instructions

```bash
# From project root:
python examples/AsianFinancialCrisis/LLM/run_asianfinancialcrisis_llm.py \
    -c configs/AsianFinancialCrisis/LLM/simulation.yml

# Run analysis:
python examples/AsianFinancialCrisis/LLM/analysis.py \
    -c configs/AsianFinancialCrisis/LLM/simulation.yml
```

Output: `EXPERIMENT/AsianFinancialCrisis/LLM/records/`


## 7. Expected Behavior Patterns

| Phase              | Deviation Range | LLM-Specific Behavior                                                         |
|--------------------|-----------------|-------------------------------------------------------------------------------|
| **Stable**         | [−2%, +2%]      | Agents hold; some NoiseTrader activity; LLM agents recognize stability        |
| **Hot Money Exit** | [−5%, −2%]      | LLMHotMoneyFunder triggers panic exit faster or slower than −2% threshold     |
| **Contagion**      | [−10%, −5%]     | LLMContagionTrader begins cross-border selling; qualitative contagion reading |
| **Crisis Peak**    | [−30% to −60%]  | LLMIMFRescuer intervenes at subjective "emergency" level; timing varies       |
| **Recovery**       | Stabilizing     | LLMValueContrarian accumulates; market recovers; high variance vs. Rule path  |


## 8. References

*(Theory sections from simulation-bases.md — cross-reference only)*

- `../simulation-bases.md §2` — Theoretical basis for all 5 agent personas
- `../simulation-bases.md §5` — LLM variant column in agent diversity table
- `../analysis-bases.md §6` — Expected LLM results (highest variance)
- `prompts.py → LLM_*_SYS` — All 5 behavioral persona prompts
- `prompts.py → LLM_USER_TEMPLATE` — Market state variables passed to LLM
