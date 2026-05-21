# CarryTradeUnwind LLM Variant — Design Specification

## §1 Overview

| Item                     | Detail                                                                                               |
|--------------------------|------------------------------------------------------------------------------------------------------|
| **Phenomenon**           | Carry trade unwind dynamics reproduced by LLM-driven agents with carry-trade personas                |
| **Variant**              | LLM — all trader agents replaced by language model decision-makers                                   |
| **Rounds**               | 200 (configurable)                                                                                   |
| **Market**               | Identical deterministic Rule-based Market agent                                                      |
| **Key Feature**          | LLM agents reason under carry-trade personas; stochastic decisions introduce realistic heterogeneity |
| **Difference from Rule** | Decision logic replaced by LLM inference; no hard-coded deviation thresholds in traders              |

---

## §2 Theory → Implementation Mapping

### §2.1 LLMCarryTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Carry-premium investor from simulation-bases.md §4.1 | `LLM_CARRY_TRADER_SYS` defines a return-seeking, leverage-aware FX carry persona without hard-coded thresholds. |
| Shared order contract | `LLMInvestor.decide()` parses `action`, `bid_price`, `quantity`, and `reasoning`, then clamps quantity to cash or position. |

### §2.2 LLMLeveragedCarryFund (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Highly leveraged forced-risk reducer from simulation-bases.md §4.2 | `LLM_LEVERAGED_CARRY_FUND_SYS` defines a margin-pressure persona that reduces risk rapidly when funding-currency appreciation threatens limits. |
| Shared order contract | Same parser and portfolio-constraint enforcement as `LLMInvestor.decide()`. |

### §2.3 LLMFundingCurrencyBuyer (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Safe-haven counterflow from simulation-bases.md §4.3 | `LLM_FUNDING_CURRENCY_BUYER_SYS` defines a defensive macro investor who buys funding currencies during risk-off conditions. |
| Shared order contract | Same canonical decision JSON and cash/position clamping as all LLM investors. |

### §2.4 LLMHedgedCarryTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Volatility-adjusted carry from simulation-bases.md §4.4 | `LLM_HEDGED_CARRY_TRADER_SYS` defines a disciplined hedged carry persona focused on downside risk control. |
| Shared order contract | Same canonical parser and order payload fields as other LLM investors. |

### §2.5 LLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background non-systematic liquidity from simulation-bases.md §4.5 | `LLM_NOISE_TRADER_SYS` defines a retail FX persona driven by headlines and short-term intuition. |
| Shared order contract | Valid output is still constrained to `buy`, `sell`, or `hold` with numeric `bid_price` and `quantity`. |

---

## §3 Market Mechanism

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

## §4 Variant-Specific Features

### 4.1 LLM Decision Loop

```
for each trader agent each round:
    1. Receive market_data + portfolio state
    2. Build system_prompt (persona) + user_prompt (market state)
    3. Call LangChainAPIInference (3 retry attempts)
    4. Parse JSON response → {action, bid_price, quantity, reasoning}
    5. Apply position/cash constraints
    6. Send order to Market
```

### 4.2 Persona System

Each LLM trader is parameterized by a **system prompt** that encodes:
- Trading identity (carry trader / hedged fund / etc.)
- Decision style (aggressive / cautious / contrarian)
- Output format instruction with canonical JSON:
  `{"action": "buy|sell|hold", "bid_price": number, "quantity": number, "reasoning": string}`

### 4.3 Stochastic Behavior

- Temperature 0.3 by default — low but non-zero, giving slight variation
- Same market state → slightly different quantities per run
- Enables Monte Carlo analysis: run multiple seeds, compare distributions

---

## §5 Architecture Diagram

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

## §6 Configuration Reference

Config file: `configs/CarryTradeUnwind/LLM/simulation.yml`

Key LLM parameters in `players.yml` extras:

| Parameter          | Value                   | Description                  |
|--------------------|-------------------------|------------------------------|
| `llm.lm_name`      | `ark/doubao-seed-2-0-mini-260428` | LLM model name |
| `llm.generation_config.temperature` | 0.3 | Controls decision randomness |
| `llm.generation_config.max_tokens` | 512 | Max response length |
| `initial_cash`     | 100000                  | Starting cash per agent      |
| `initial_position` | 0                       | Starting holdings            |

Market parameters: identical to Rule variant (see Rule/explain.md §6).

---

## §7 Running Instructions

```bash
# Requires LLM API key in .env (OPENAI_API_KEY or equivalent)
python examples/CarryTradeUnwind/LLM/run_carrytradeunwind_llm.py \
    -c configs/CarryTradeUnwind/LLM/simulation.yml

# Analyze results
python examples/CarryTradeUnwind/LLM/analysis.py \
    -c configs/CarryTradeUnwind/LLM/simulation.yml
```

---

## §8 Expected Behavior

- LLM carry trader personas tend to follow the same direction as Rule agents
- Stochastic temperature introduces round-to-round quantity variation
- Crisis may be delayed if LLM agents "reason out" the danger earlier
- recovery_ratio often higher than Rule (LLM agents adapt strategies)
- Comparing to Rule variant reveals how human-like reasoning changes dynamics

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Carry trade borrowing / crash dynamics → `../simulation-bases.md §2, §4 — CarryTrader, LeveragedCarryFund`
- LLM few-shot reasoning → Brown, T. B., et al. (2020). Language models are few-shot learners. *NeurIPS*.
