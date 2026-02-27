# AssetBubbleLLM - LLM-Powered Asset Bubble Simulation

## What is This?

| Item               | Description                                                                               |
|--------------------|-------------------------------------------------------------------------------------------|
| **Phenomenon**     | **Asset Bubbles (资产泡沫)** - LLM-driven speculation and positive feedback dynamics      |
| **Model**          | LLM-based investors with prompt-defined bubble personalities + Rule-based market clearing |
| **Key Feature**    | Investors use LLM reasoning to exhibit bubble behaviors (FOMO, limits to arbitrage, etc.) |
| **Academic Value** | Tests whether LLMs can simulate realistic bubble psychology and emergent speculation      |

## Rule-Based vs LLM-Based Comparison

| Aspect               | AssetBubble (Rule-Based)                 | AssetBubbleLLM (LLM-Based)                   |
|----------------------|------------------------------------------|----------------------------------------------|
| **Decision Logic**   | Fixed mathematical formulas              | LLM interprets market data via prompts       |
| **Investor Types**   | 6 types with hardcoded strategies        | 5 types with personality-defining prompts    |
| **Behavior**         | Deterministic (same input → same output) | Stochastic (LLM may vary responses)          |
| **Market**           | Rule-based order clearing                | **Same** rule-based order clearing           |
| **Bubble Formation** | From positive feedback formulas          | From LLM "FOMO" and "greater fool" reasoning |
| **Research Value**   | Mechanism validation                     | LLM behavioral realism + emergent bubbles    |

> **核心差异**：AssetBubble 用公式模拟投资者行为，AssetBubbleLLM 用大模型通过 prompt 定义的"投机心理"来推理决策。

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │        AssetBubbleLLM Architecture       │
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

## LLM Provider: ByteDance Doubao via lmbase

| Configuration         | Value                                             |
|-----------------------|---------------------------------------------------|
| **Library**           | `lmbase.inference.api_call.LangChainAPIInference` |
| **Model Format**      | `lm_name: "ark/ep-xxxx"`                          |
| **Auth**              | `ARK_API_KEY` environment variable                |
| **Generation Config** | `temperature: 0.3`, `max_new_tokens: 500`         |

## 5 LLM Investor Types

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

## Market Clearing (Rule-Based)

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

## Topology (Star Network)

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

## Files

| File                                        | Purpose                          |
|---------------------------------------------|----------------------------------|
| `examples/AssetBubbleLLM/players.py`        | Market + 5 LLM investor classes  |
| `examples/AssetBubbleLLM/prompts.py`        | System and user prompt templates |
| `examples/AssetBubbleLLM/run_bubble_llm.py` | Entry point                      |
| `configs/AssetBubbleLLM/simulation.yml`     | Main config (rounds, paths)      |
| `configs/AssetBubbleLLM/players.yml`        | Player definitions + LLM config  |
| `configs/AssetBubbleLLM/topology.yml`       | Star topology                    |

## Running

```bash
# Set API key
export ARK_API_KEY='your-bytedance-doubao-api-key'

# Run simulation
python examples/AssetBubbleLLM/run_bubble_llm.py -c configs/AssetBubbleLLM/simulation.yml
```

## Expected LLM Behavior Patterns

| Phase    | Rounds | LLM Behavior                                              |
|----------|--------|-----------------------------------------------------------|
| Initial  | 1-3    | LLMs "assess" market, mixed decisions                     |
| Build-up | 4-7    | Greater Fool detects rising prices, starts buying heavily |
| Euphoria | 8-12   | Sentiment + Leveraged join, bubble ratio > 1.2x           |
| Peak     | 13-15  | Arbitrageur shorts cautiously, Value sells                |
| Collapse | 16-20  | Leveraged forced selling triggers cascade                 |

## Research Questions

| Question                                                | How to Test                                       |
|---------------------------------------------------------|---------------------------------------------------|
| Can LLMs exhibit "greater fool" behavior realistically? | Track reasoning when buying at high bubble ratios |
| Do limits to arbitrage emerge from LLM constraints?     | Observe arbitrageur's cautious shorting behavior  |
| Can LLM leverage traders trigger crashes?               | Monitor forced selling dynamics                   |
| Is LLM bubble more realistic than rule-based?           | Compare price dynamics with historical bubbles    |

## References

| Theory                   | Application in AssetBubbleLLM                 | Reference                   |
|--------------------------|-----------------------------------------------|-----------------------------|
| **Greater Fool Theory**  | LLMGreaterFoolSpeculator ignores fundamentals | (Classical)                 |
| **Limits to Arbitrage**  | LLMRationalArbitrageur constrained shorting   | Shleifer & Vishny (1997)    |
| **Noise Trader Risk**    | LLMSentimentTrader follows crowd              | De Long et al. (1990)       |
| **Synchronization Risk** | Timing uncertainty in bubble collapse         | Abreu & Brunnermeier (2003) |
