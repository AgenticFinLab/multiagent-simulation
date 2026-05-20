# AssetBubble LLM — Implementation Explanation

## §1 Overview

| Item                                   | Description                                                                                                                                                                         |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | LLM                                                                                                                                                                                 |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                                            |
| **Phenomenon**                         | Asset Bubbles (资产泡沫) — LLM-driven speculation and positive feedback dynamics                                                                                                    |
| **Decision Logic**                     | LLM prompts (persona only) — market data in user prompt; LLM reasons to JSON decision                                                                                               |
| **Key Difference from Other Variants** | Investor decision logic replaced by LLM reasoning; market mechanism identical to Rule variant                                                                                       |
| **Primary Research Contribution**      | Tests whether LLM agents, guided only by personality and market data, can reproduce realistic investor psychology and emergent bubble phenomena without explicit quantitative rules |

## §2 Theory → Implementation Mapping

### Market: Theory → Implementation
*(Theory defined in `../simulation-bases.md §3`)*

| Theoretical Design Element                                                       | Implementation                                                                   |
|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Price formation model → `simulation-bases.md §3.1`                               | Identical to Rule variant — `Market.decide()` in `players.py`; unchanged formula |
| Bubble-prone parameters (high λ, low γ) → `simulation-bases.md §3.1`             | Same config values: `price_impact = 0.15`, `mean_reversion = 0.005`              |
| Information broadcast design → `simulation-bases.md §3.3`                        | `market_data` dict with all fields; same payload as Rule                         |
| Price floor, margin call, short-selling constraints → `simulation-bases.md §3.2` | All mechanisms identical to Rule variant                                         |

### LLM Investors: Theory → Implementation
*(Theory per investor defined in `../simulation-bases.md §4`)*

| Investor               | Theory → `simulation-bases.md §4`                | Prompt Constant                      | LLM Persona Source                     |
|------------------------|--------------------------------------------------|--------------------------------------|----------------------------------------|
| LLMGreaterFoolSpec     | Greater Fool Theory → `§4 — MomentumSpeculator`  | `LLMGREATERFOOL_SYS` in `prompts.py` | `simulation-bases.md §4 — LLM Persona` |
| LLMRationalArbitrageur | Limits to Arbitrage → `§4 — RationalArbitrageur` | `LLMARBITRAGEUR_SYS` in `prompts.py` | `simulation-bases.md §4 — LLM Persona` |
| LLMSentimentTrader     | Noise Trader Risk → `§4 — NoiseTrader`           | `LLMSENTIMENT_SYS` in `prompts.py`   | `simulation-bases.md §4 — LLM Persona` |
| LLMValueInvestor       | Value Investing → `§4 — FundamentalInvestor`     | `LLMVALUE_SYS` in `prompts.py`       | `simulation-bases.md §4 — LLM Persona` |
| LLMLeveragedSpec       | Leverage amplification → `§4 — LeveragedBuyer`   | `LLMLEVERAGED_SYS` in `prompts.py`   | `simulation-bases.md §4 — LLM Persona` |

**Core construction rule**: System prompts define **personality only** — they must NOT name the phenomenon ("asset bubble"), mention the price formula, or hint at the market event. The LLM discovers market dynamics from user prompt data alone. Output format: `<analysis>...</analysis><decision>...</decision>` with JSON `{action, bid_price, quantity, reasoning}`.

---

## §3 Rule-Based vs LLM-Based Comparison

| Aspect               | AssetBubble (Rule-Based)                 | AssetBubble LLM (LLM-Based)                  |
|----------------------|------------------------------------------|----------------------------------------------|
| **Decision Logic**   | Fixed mathematical formulas              | LLM interprets market data via prompts       |
| **Investor Types**   | 6 types with hardcoded strategies        | 5 types with personality-defining prompts    |
| **Behavior**         | Deterministic (same input → same output) | Stochastic (LLM may vary responses)          |
| **Market**           | Rule-based order clearing                | **Same** rule-based order clearing           |
| **Bubble Formation** | From positive feedback formulas          | From LLM "FOMO" and "greater fool" reasoning |
| **Research Value**   | Mechanism validation                     | LLM behavioral realism + emergent bubbles    |

> **核心差异**：AssetBubble 用公式模拟投资者行为，AssetBubble LLM 用大模型通过 prompt 定义的"投机心理"来推理决策。

## §4 Architecture

```
                    ┌──────────────────────────────────────────┐
                    │        AssetBubble LLM Architecture       │
                    └──────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────────────┐
   │                         Market (Rule-Based)                         │
   │   - NOT LLM: uses deterministic price formula                       │
   │   - P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε                       │
   │   - Bubble-prone: High λ=0.15, Low γ=0.005                          │
   └─────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Broadcast: {price, bubble_ratio, fundamental}
                                     ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    LLM Investors (5 Types)                          │
   │                                                                     │
   │   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐            │
   │   │GreaterFool    │ │RationalArb    │ │SentimentTrader│            │
   │   │(⭐ bubble     │ │(weak anchor)  │ │(⭐ amplify)   │            │
   │   │  driver)      │ │               │ │               │            │
   │   └───────┬───────┘ └───────┬───────┘ └───────┬───────┘            │
   │           │                 │                 │                     │
   │   ┌───────────────┐ ┌───────────────┐                              │
   │   │ValueInvestor  │ │LeveragedSpec  │                              │
   │   │(slow anchor)  │ │(⭐ amplify    │                              │
   │   │               │ │  + crash)     │                              │
   │   └───────┬───────┘ └───────┬───────┘                              │
   │           │                 │                                       │
   │           ▼                 ▼                                       │
   │   ┌─────────────────────────────────────────────────────────────┐  │
   │   │               ByteDance Doubao API (via lmbase)             │  │
   │   │   System Prompt (personality) + User Prompt (market data)   │  │
   │   │                      → JSON Decision                        │  │
   │   └─────────────────────────────────────────────────────────────┘  │
   └─────────────────────────────────────────────────────────────────────┘
```

## §5 LLM Provider: ByteDance Doubao via lmbase

| Configuration         | Value                                             |
|-----------------------|---------------------------------------------------|
| **Library**           | `lmbase.inference.api_call.LangChainAPIInference` |
| **Model Format**      | `lm_name: "ark/ep-xxxx"`                          |
| **Auth**              | `ARK_API_KEY` environment variable                |
| **Generation Config** | `temperature: 0.3`, `max_new_tokens: 500`         |

## §6 5 LLM Investor Types

### Investor Type Summary

| Type                       | Strategy           | Market Effect       | System Prompt Focus             |
|----------------------------|--------------------|---------------------|---------------------------------|
| **LLMGreaterFoolSpec**     | Momentum/FOMO      | ⭐ BUBBLE DRIVER     | "Sell to a greater fool"        |
| **LLMRationalArbitrageur** | Short overvalued   | WEAK STABILIZING    | "Limits to arbitrage"           |
| **LLMSentimentTrader**     | Follow crowd       | ⭐ AMPLIFYING        | "Go with the flow"              |
| **LLMValueInvestor**       | Fundamental anchor | SLOW STABILIZING    | "Price returns to fundamentals" |
| **LLMLeveragedSpec**       | Leveraged momentum | ⭐ EXTREME AMPLIFIER | "Go big with leverage"          |

### 1. LLMGreaterFoolSpeculator (⭐ Primary Bubble Driver)

**Theory**: Greater Fool Theory - Buy expensive expecting to sell to someone else at higher price.

| Aspect       | Description                          |
|--------------|--------------------------------------|
| **Effect**   | BUBBLE DRIVER - ignores fundamentals |
| **Behavior** | FOMO, buys at 2x-4x fundamental      |
| **Risk**     | Extreme - drives bubble formation    |

### 2. LLMRationalArbitrageur (Weak Anchor)

**Theory**: Limits to Arbitrage (Shleifer & Vishny, 1997) - Cannot fully correct mispricings.

| Aspect       | Description                             |
|--------------|-----------------------------------------|
| **Effect**   | WEAK STABILIZING - constrained          |
| **Behavior** | Short overvalued, but cautiously        |
| **Risk**     | Medium - timing and capital constraints |

### 3. LLMSentimentTrader (Herding)

**Theory**: De Long et al. (1990) Noise Trader Risk

| Aspect       | Description                   |
|--------------|-------------------------------|
| **Effect**   | AMPLIFYING - follows crowd    |
| **Behavior** | Buy bullish, sell bearish     |
| **Risk**     | High - amplifies market moves |

### 4. LLMValueInvestor (Slow Anchor)

**Theory**: Traditional value investing

| Aspect       | Description                      |
|--------------|----------------------------------|
| **Effect**   | SLOW STABILIZING                 |
| **Behavior** | Buy undervalued, sell overvalued |
| **Risk**     | Low - patient, small positions   |

### 5. LLMLeveragedSpeculator (⭐ Extreme Amplifier)

**Theory**: Leverage amplifies gains AND losses, can trigger crashes.

| Aspect       | Description                              |
|--------------|------------------------------------------|
| **Effect**   | EXTREME AMPLIFIER - both directions      |
| **Behavior** | Large positions, forced selling on drops |
| **Risk**     | Extreme - can cause market dislocations  |

## §7 Market Clearing (Rule-Based)

```
Bubble-Prone Price Model:

  P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε
  
  Where:
    λ = 0.15  (HIGH - strong demand impact)
    γ = 0.005 (LOW - slow mean reversion)
    F = 100.0 (fundamental value with 0.1% growth)
    ε ~ N(0, 0.3)

Key: High λ + Low γ = Bubble-prone dynamics
```

## §8 Topology (Star Network)

```
                         ┌───────────────────┐
                         │      market       │ ◄── Level 0 (bubble-prone clearing)
                         └─────────┬─────────┘
                                   │
         ┌───────────┬─────────────┼─────────────┬───────────┐
         ▼           ▼             ▼             ▼           ▼
  llm_greater_fool llm_arbitrageur llm_sentiment llm_value llm_leveraged
  (⭐ driver)      (weak anchor)   (⭐ amplify)  (anchor)   (⭐ extreme)
```

## §9 Files

| File                                         | Purpose                          |
|----------------------------------------------|----------------------------------|
| `examples/AssetBubble/LLM/players.py`        | Market + 5 LLM investor classes  |
| `examples/AssetBubble/LLM/prompts.py`        | System and user prompt templates |
| `examples/AssetBubble/LLM/run_bubble_llm.py` | Entry point                      |
| `configs/AssetBubble/LLM/simulation.yml`     | Main config (rounds, paths)      |
| `configs/AssetBubble/LLM/players.yml`        | Player definitions + LLM config  |
| `configs/AssetBubble/LLM/topology.yml`       | Star topology                    |

## §10 Running

```bash
# Set API key
export ARK_API_KEY='your-bytedance-doubao-api-key'

# Run simulation
python examples/AssetBubble/LLM/run_bubble_llm.py -c configs/AssetBubble/LLM/simulation.yml
```

## §11 Expected LLM Behavior Patterns

| Phase    | Rounds | LLM Behavior                                              |
|----------|--------|-----------------------------------------------------------|
| Initial  | 1-3    | LLMs "assess" market, mixed decisions                     |
| Build-up | 4-7    | Greater Fool detects rising prices, starts buying heavily |
| Euphoria | 8-12   | Sentiment + Leveraged join, bubble ratio > 1.2x           |
| Peak     | 13-15  | Arbitrageur shorts cautiously, Value sells                |
| Collapse | 16-20  | Leveraged forced selling triggers cascade                 |

## §12 Research Questions

| Question                                                | How to Test                                       |
|---------------------------------------------------------|---------------------------------------------------|
| Can LLMs exhibit "greater fool" behavior realistically? | Track reasoning when buying at high bubble ratios |
| Do limits to arbitrage emerge from LLM constraints?     | Observe arbitrageur's cautious shorting behavior  |
| Can LLM leverage traders trigger crashes?               | Monitor forced selling dynamics                   |
| Is LLM bubble more realistic than rule-based?           | Compare price dynamics with historical bubbles    |

## §13 Configuration Reference

Key parameters from `configs/AssetBubble/LLM/players.yml`:

| Parameter        | Config Path                                              | Value                                      | Design Justification                              |
|------------------|----------------------------------------------------------|--------------------------------------------|---------------------------------------------------|
| `lm_name`        | `{investor}.extras.llm.lm_name`                          | `ark/doubao-seed-1-6-lite-251015`          | ByteDance Doubao API; low cost, fast response     |
| `temperature`    | `{investor}.extras.llm.generation_config.temperature`    | 0.3                                        | Low stochasticity for consistent persona behavior |
| `max_new_tokens` | `{investor}.extras.llm.generation_config.max_new_tokens` | 500                                        | Sufficient for `<analysis>` + `<decision>` JSON   |
| `sys_message`    | `{investor}.extras.llm.sys_message`                      | `examples.AssetBubble.LLM.prompts:{CONST}` | Dynamic prompt loading via `importlib`            |
| Market config    | Same as Rule variant                                     | See `simulation-bases.md §6`               | Market mechanism unchanged                        |

---

## §14 References

> Do NOT re-read full citations — these theories are fully documented in `../simulation-bases.md §2`.

- Greater Fool Theory → `simulation-bases.md §2`, `§4 — MomentumSpeculator / LLMGreaterFoolSpec`
- Limits to Arbitrage → `simulation-bases.md §2`, `§4 — RationalArbitrageur / LLMRationalArbitrageur`
- Noise Trader Risk → `simulation-bases.md §2`, `§4 — NoiseTrader / LLMSentimentTrader`
- Synchronization Risk → `simulation-bases.md §2`, `§4 — LeveragedBuyer / LLMLeveragedSpec`
- Historical calibration → `simulation-bases.md §8`
- Parameter values → `simulation-bases.md §6`
