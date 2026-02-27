# MomentumEffectLLM - LLM-Powered Momentum Effect Simulation

## What is This?

| Item               | Description                                                                         |
|--------------------|-------------------------------------------------------------------------------------|
| **Phenomenon**     | **Momentum Effect (动量效应)** - LLM-driven price continuation patterns             |
| **Model**          | LLM-based investors with trend-following personalities + Rule-based market clearing |
| **Key Feature**    | Investors use LLM reasoning to detect and trade momentum signals                    |
| **Academic Value** | Tests whether LLMs can replicate Jegadeesh & Titman's momentum findings             |

## Rule-Based vs LLM-Based Comparison

| Aspect                 | MomentumEffect (Rule-Based)         | MomentumEffectLLM (LLM-Based)               |
|------------------------|-------------------------------------|---------------------------------------------|
| **Decision Logic**     | Fixed momentum calculation formulas | LLM interprets price patterns via prompts   |
| **Investor Types**     | 5 types with hardcoded strategies   | 5 types with personality-defining prompts   |
| **Behavior**           | Deterministic momentum signals      | Stochastic trend interpretation             |
| **Market**             | Rule-based order clearing           | **Same** rule-based order clearing          |
| **Momentum Detection** | From mathematical lookback formulas | From LLM "chart reading" reasoning          |
| **Research Value**     | Mechanism validation                | LLM pattern recognition + emergent momentum |

## 5 LLM Investor Types

### Investor Type Summary

| Type                  | Strategy            | Market Effect      | System Prompt Focus                |
|-----------------------|---------------------|--------------------|------------------------------------|
| **LLMMomentumTrader** | Jegadeesh-Titman    | ⭐ TREND AMPLIFIER  | "Winners keep winning"             |
| **LLMContrarian**     | Mean reversion      | STABILIZING        | "What goes up must come down"      |
| **LLMTechnical**      | Price patterns      | TREND FOLLOWING    | "Price patterns predict future"    |
| **LLMTrendFollower**  | Aggressive momentum | ⭐ STRONG AMPLIFIER | "The trend is your friend"         |
| **LLMFundamental**    | Value anchor        | STABILIZING        | "Price should reflect fundamental" |

### 1. LLMMomentumTrader (⭐ Primary Driver)

**Theory**: Jegadeesh & Titman (1993) - Winners continue winning for 3-12 months.

| Aspect       | Description                              |
|--------------|------------------------------------------|
| **Effect**   | TREND AMPLIFIER - buys winners           |
| **Signals**  | Momentum_5 > 3% → Buy; < -3% → Sell      |
| **Behavior** | Classic momentum strategy implementation |

### 2. LLMContrarian (Stabilizing)

**Theory**: De Bondt & Thaler (1985) - Markets overreact, mean reversion follows.

| Aspect       | Description                                    |
|--------------|------------------------------------------------|
| **Effect**   | STABILIZING - fades trends                     |
| **Behavior** | Sell overbought, buy oversold                  |
| **Signals**  | Momentum_5 > 5% → Overbought; < -5% → Oversold |

### 3. LLMTechnicalTrader (Pattern-Based)

**Theory**: Technical analysis - price patterns contain predictive information.

| Aspect       | Description                            |
|--------------|----------------------------------------|
| **Effect**   | TREND FOLLOWING (moderate)             |
| **Behavior** | Golden cross → Buy; Death cross → Sell |
| **Focus**    | Short-term vs long-term price averages |

### 4. LLMTrendFollower (⭐ Aggressive)

**Theory**: Trend following - ride the trend until it ends.

| Aspect       | Description                              |
|--------------|------------------------------------------|
| **Effect**   | STRONG AMPLIFIER - large positions       |
| **Behavior** | momentum_10 > 0 → BULLISH; < 0 → BEARISH |
| **Risk**     | High - aggressive position sizing        |

### 5. LLMFundamentalInvestor (Anchor)

**Theory**: Fundamental analysis - price should reflect intrinsic value.

| Aspect       | Description                       |
|--------------|-----------------------------------|
| **Effect**   | STABILIZING - ignores momentum    |
| **Behavior** | Buy below fundamental, sell above |
| **Focus**    | Value, not price trends           |

## Market Clearing (Rule-Based)

```
Price Model:

  P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε
  
  Where:
    λ = 0.1   (price impact)
    γ = 0.02  (mean reversion)
    F = 100.0 (fundamental value)

Momentum enables price continuation through positive feedback:
  Price rises → LLMMomentum buys → More price rise → More buying
```

## Topology (Star Network)

```
                         ┌───────────────────┐
                         │      market       │ ◄── Level 0
                         └─────────┬─────────┘
                                   │
         ┌───────────┬─────────────┼─────────────┬───────────┐
         ▼           ▼             ▼             ▼           ▼
   llm_momentum  llm_contrarian  llm_technical llm_trend   llm_fund
   (⭐ amplify)  (stabilize)     (follow)      (⭐ amplify) (anchor)
```

## Files

| File                                             | Purpose                          |
|--------------------------------------------------|----------------------------------|
| `examples/MomentumEffectLLM/players.py`          | Market + 5 LLM investor classes  |
| `examples/MomentumEffectLLM/prompts.py`          | System and user prompt templates |
| `examples/MomentumEffectLLM/run_momentum_llm.py` | Entry point                      |
| `configs/MomentumEffectLLM/simulation.yml`       | Main config                      |
| `configs/MomentumEffectLLM/players.yml`          | Player definitions + LLM config  |
| `configs/MomentumEffectLLM/topology.yml`         | Star topology                    |

## Running

```bash
export ARK_API_KEY='your-bytedance-doubao-api-key'
python examples/MomentumEffectLLM/run_momentum_llm.py -c configs/MomentumEffectLLM/simulation.yml
```

## Expected LLM Behavior Patterns

| Phase         | Rounds | LLM Behavior                                           |
|---------------|--------|--------------------------------------------------------|
| Build-up      | 1-5    | Random shocks start small trends                       |
| Detection     | 6-8    | LLMMomentum detects positive momentum_5, starts buying |
| Amplification | 9-12   | LLMTrendFollower joins, trend strengthens              |
| Peak          | 13-15  | LLMContrarian sells, momentum slows                    |
| Reversal      | 16-20  | Mean reversion begins, LLMFundamental buys dips        |

## Research Questions

| Question                                                | How to Test                                        |
|---------------------------------------------------------|----------------------------------------------------|
| Can LLMs detect momentum patterns like academics found? | Compare LLM momentum signals with rule-based       |
| Does LLM trend following amplify momentum?              | Measure price continuation after LLM buying        |
| Can LLM contrarians dampen momentum?                    | Track contrarian effect on trend reversal          |
| Is LLM momentum more realistic than rule-based?         | Compare autocorrelation patterns with real markets |

## References

| Theory                 | Application in MomentumEffectLLM        | Reference                 |
|------------------------|-----------------------------------------|---------------------------|
| **Momentum Effect**    | LLMMomentumTrader follows winners       | Jegadeesh & Titman (1993) |
| **Overreaction**       | LLMContrarian fades extreme moves       | De Bondt & Thaler (1985)  |
| **Technical Analysis** | LLMTechnicalTrader reads price patterns | (Classical)               |
| **Trend Following**    | LLMTrendFollower rides momentum         | (Practitioner Strategy)   |
