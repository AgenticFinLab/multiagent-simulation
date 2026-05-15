# CarryTradeUnwind LLM Variant — Design Specification

## 1. Overview

| Item                     | Detail                                                                                               |
|--------------------------|------------------------------------------------------------------------------------------------------|
| **Phenomenon**           | Carry trade unwind dynamics reproduced by LLM-driven agents with carry-trade personas                |
| **Variant**              | LLM — all trader agents replaced by language model decision-makers                                   |
| **Rounds**               | 200 (configurable)                                                                                   |
| **Market**               | Identical deterministic Rule-based Market agent                                                      |
| **Key Feature**          | LLM agents reason under carry-trade personas; stochastic decisions introduce realistic heterogeneity |
| **Difference from Rule** | Decision logic replaced by LLM inference; no hard-coded deviation thresholds in traders              |

---

## 2. Theory → Implementation Mapping

| Theoretical Concept      | Agent / Mechanism                                                | Code Location                           |
|--------------------------|------------------------------------------------------------------|-----------------------------------------|
| Carry trade borrowing    | `LLMCarryTrader` persona: borrows low-yield to invest high-yield | `LLM/prompts.py: LLM_CARRY_TRADER_SYS`  |
| Forced unwinding         | `LLMCarryFund` persona: stops loss under drawdown                | `LLM/prompts.py: LLM_CARRY_FUND_SYS`    |
| Safe-haven demand        | `LLMFundingBuyer` persona: buys funding currency under stress    | `LLM/prompts.py: LLM_FUNDING_BUYER_SYS` |
| Volatility-managed carry | `LLMHedgedTrader` persona: reduces exposure in volatile markets  | `LLM/prompts.py: LLM_HEDGED_TRADER_SYS` |
| Noise trader liquidity   | `LLMNoiseTrader` persona: uninformed random-ish trader           | `LLM/prompts.py: LLM_NOISE_TRADER_SYS`  |
| Price dynamics           | `Market` agent (Rule-based, unchanged)                           | `Rule/players.py: Market`               |

---

## 3. Market Mechanism

Identical to Rule variant. Market broadcasts per round:

```python
{
    "price":       float,   # current FX rate
    "fundamental": float,   # PPP fundamental
    "deviation":   float,   # (price - fundamental) / fundamental
    "round":       int,
}
```

LLM agents receive this plus portfolio state `{cash, position, portfolio_value}` as user prompt.

---

## 4. Variant-Specific Features

### 4.1 LLM Decision Loop

```
for each trader agent each round:
    1. Receive market_data + portfolio state
    2. Build system_prompt (persona) + user_prompt (market state)
    3. Call LangChainAPIInference (3 retry attempts)
    4. Parse JSON response → {action, quantity}
    5. Apply position/cash constraints
    6. Send order to Market
```

### 4.2 Persona System

Each LLM trader is parameterized by a **system prompt** that encodes:
- Trading identity (carry trader / hedged fund / etc.)
- Decision style (aggressive / cautious / contrarian)
- Output format instruction (JSON: `{"action": "buy|sell|hold", "quantity": N}`)

### 4.3 Stochastic Behavior

- Temperature 0.3 by default — low but non-zero, giving slight variation
- Same market state → slightly different quantities per run
- Enables Monte Carlo analysis: run multiple seeds, compare distributions

---

## 5. Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                   Market (Rule)                       │
│  P(t+1) = P(t) + λ·D + γ·(F−P) + ε                  │
│  broadcasts: {price, fundamental, deviation, round}   │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────┼────────────────┐
          │            │                │
   ┌──────▼──────┐ ┌───▼──────────┐ ┌──▼──────────────┐
   │LLMCarry     │ │LLMCarryFund  │ │LLMFunding       │
   │Trader       │ │(forced exit  │ │Buyer (safe-haven│
   │(persona)    │ │ persona)     │ │ persona)        │
   └─────────────┘ └──────────────┘ └─────────────────┘
          │
   ┌──────▼──────┐ ┌──────────────┐
   │LLMHedged    │ │LLMNoise      │
   │Trader       │ │Trader        │
   │(volatility  │ │(random       │
   │  persona)   │ │ persona)     │
   └─────────────┘ └──────────────┘
          │  all agents call LLM → parse JSON → send order → Market
          │
   ┌──────▼──────────────────────────────────────────┐
   │         LangChainAPIInference (shared)           │
   │  InferInput(system_msg, user_msg) → response     │
   └─────────────────────────────────────────────────┘
```

---

## 6. Configuration Reference

Config file: `configs/CarryTradeUnwind/LLM/simulation.yml`

Key LLM parameters in `players.yml` extras:

| Parameter          | Value                   | Description                  |
|--------------------|-------------------------|------------------------------|
| `llm.model`        | `gpt-4o-mini` (default) | LLM model name               |
| `llm.temperature`  | 0.3                     | Controls decision randomness |
| `llm.max_tokens`   | 512                     | Max response length          |
| `initial_cash`     | 100000                  | Starting cash per agent      |
| `initial_position` | 0                       | Starting holdings            |

Market parameters: identical to Rule variant (see Rule/explain.md §6).

---

## 7. Running Instructions

```bash
# Requires LLM API key in .env (OPENAI_API_KEY or equivalent)
python examples/CarryTradeUnwind/LLM/run_carrytradeunwind_llm.py \
    -c configs/CarryTradeUnwind/LLM/simulation.yml

# Analyze results
python examples/CarryTradeUnwind/LLM/analysis.py \
    -c configs/CarryTradeUnwind/LLM/simulation.yml
```

---

## 8. Expected Behavior

- LLM carry trader personas tend to follow the same direction as Rule agents
- Stochastic temperature introduces round-to-round quantity variation
- Crisis may be delayed if LLM agents "reason out" the danger earlier
- recovery_ratio often higher than Rule (LLM agents adapt strategies)
- Comparing to Rule variant reveals how human-like reasoning changes dynamics

---

## 9. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Carry trade borrowing / crash dynamics → `../simulation-bases.md §2, §4 — CarryTrader, LeveragedCarryFund`
- LLM few-shot reasoning → Brown, T. B., et al. (2020). Language models are few-shot learners. *NeurIPS*.
