# ReversalEffect LLM - LLM-Powered Reversal Effect Simulation

## What is This?

| Item               | Description                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| **Phenomenon**     | **Reversal Effect (反转效应)** - LLM-driven overreaction correction in prices      |
| **Model**          | LLM-based investors with contrarian/overreaction personalities + Rule-based market |
| **Key Feature**    | Investors use LLM reasoning to detect overreaction and trade reversals             |
| **Academic Value** | Tests whether LLMs can simulate De Bondt & Thaler's overreaction hypothesis        |

## Rule-Based vs LLM-Based Comparison

| Aspect             | ReversalEffect (Rule-Based)       | ReversalEffect LLM (LLM-Based)               |
|--------------------|-----------------------------------|---------------------------------------------|
| **Decision Logic** | Fixed cumulative return formulas  | LLM interprets performance patterns         |
| **Investor Types** | 5 types with hardcoded strategies | 5 types with personality-defining prompts   |
| **Behavior**       | Deterministic reversal signals    | Stochastic contrarian reasoning             |
| **Market**         | Rule-based order clearing         | **Same** rule-based order clearing          |
| **Overreaction**   | From mathematical thresholds      | From LLM "market overreacted" reasoning     |
| **Research Value** | Mechanism validation              | LLM contrarian realism + emergent reversals |

## 5 LLM Investor Types

### Investor Type Summary

| Type                  | Strategy            | Market Effect          | System Prompt Focus                 |
|-----------------------|---------------------|------------------------|-------------------------------------|
| **LLMContrarian**     | Long-term reversal  | ⭐ REVERSAL DRIVER      | "Past losers become future winners" |
| **LLMOverconfident**  | Extrapolation       | ⭐ CREATES OVERREACTION | "I know where this is going"        |
| **LLMValue**          | Fundamental anchor  | STABILIZING            | "Price should reflect fundamentals" |
| **LLMMomentumChaser** | Short-term momentum | DESTABILIZING          | "Follow recent returns"             |
| **LLMNoise**          | Random trading      | NEUTRAL LIQUIDITY      | "Trade on gut feelings"             |

### 1. LLMContrarian (⭐ Reversal Driver)

**Theory**: De Bondt & Thaler (1985) - Markets overreact, losers outperform winners.

| Aspect       | Description                           |
|--------------|---------------------------------------|
| **Effect**   | REVERSAL DRIVER - buys past losers    |
| **Strategy** | Cumulative return < -10% → BUY        |
| **Behavior** | Bets against extreme past performance |

### 2. LLMOverconfident (⭐ Creates Overreaction)

**Theory**: Overconfidence leads to extrapolation and overreaction.

| Aspect         | Description                              |
|----------------|------------------------------------------|
| **Effect**     | CREATES OVERREACTION                     |
| **Behavior**   | Positive return → Extrapolate → Buy More |
| **Psychology** | Overweights recent information           |

### 3. LLMValue (Stabilizing)

**Theory**: Value investing - price should reflect fundamentals.

| Aspect       | Description                           |
|--------------|---------------------------------------|
| **Effect**   | STABILIZING - anchors to fundamentals |
| **Behavior** | Buy < 95% fund; Sell > 105% fund      |
| **Focus**    | Patient, ignores short-term noise     |

### 4. LLMMomentumChaser (Short-Term)

**Theory**: Short-term momentum - recent returns continue briefly.

| Aspect       | Description                           |
|--------------|---------------------------------------|
| **Effect**   | DESTABILIZING - follows recent trends |
| **Behavior** | Recent return > 0 → Buy               |
| **Focus**    | Short-term price movements            |

### 5. LLMNoiseTrader (Liquidity)

**Theory**: Uninformed trading provides liquidity and randomness.

| Aspect       | Description                          |
|--------------|--------------------------------------|
| **Effect**   | NEUTRAL LIQUIDITY                    |
| **Behavior** | Somewhat random "gut feeling" trades |
| **Focus**    | Small positions, no conviction       |

## Market Clearing (Rule-Based)

```
Price Model:

  P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε
  
  Reversal emerges from interaction:
    1. LLMOverconfident creates initial overreaction
    2. LLMContrarian detects overreaction, trades against it
    3. Price eventually reverts toward fundamental
```

## Topology (Star Network)

```
                         ┌───────────────────┐
                         │      market       │ ◄── Level 0
                         └─────────┬─────────┘
                                   │
         ┌───────────┬─────────────┼─────────────┬───────────┐
         ▼           ▼             ▼             ▼           ▼
   llm_contrarian llm_overconf   llm_value    llm_momentum  llm_noise
   (⭐ reversal)  (⭐ overreact) (stabilize)  (destabilize) (liquidity)
```

## Files

| File                                             | Purpose                          |
|--------------------------------------------------|----------------------------------|
| `examples/ReversalEffect/LLM/players.py`          | Market + 5 LLM investor classes  |
| `examples/ReversalEffect/LLM/prompts.py`          | System and user prompt templates |
| `examples/ReversalEffect/LLM/run_reversal_llm.py` | Entry point                      |
| `configs/ReversalEffect/LLM/simulation.yml`       | Main config                      |
| `configs/ReversalEffect/LLM/players.yml`          | Player definitions + LLM config  |
| `configs/ReversalEffect/LLM/topology.yml`         | Star topology                    |

## Running

```bash
export ARK_API_KEY='your-bytedance-doubao-api-key'
python examples/ReversalEffect/LLM/run_reversal_llm.py -c configs/ReversalEffect/LLM/simulation.yml
```

## Expected LLM Behavior Patterns

| Phase          | Rounds | LLM Behavior                                               |
|----------------|--------|------------------------------------------------------------|
| Initial        | 1-5    | Random shocks, normal trading                              |
| Overreaction   | 6-10   | LLMOverconfident extrapolates, drives price away from fund |
| Peak           | 11-13  | Price deviation reaches extreme (>10% from fundamental)    |
| Reversal       | 14-17  | LLMContrarian detects overreaction, bets against trend     |
| Mean Reversion | 18-20  | Price reverts toward fundamental value                     |

## Research Questions

| Question                                           | How to Test                                           |
|----------------------------------------------------|-------------------------------------------------------|
| Can LLMs detect market overreaction?               | Track LLMContrarian's detection of extreme deviations |
| Does overconfidence create overreaction in LLMs?   | Monitor LLMOverconfident's extrapolation behavior     |
| Is LLM reversal timing realistic?                  | Compare reversal patterns with De Bondt & Thaler      |
| Can LLM contrarians profit from reversal strategy? | Track contrarian portfolio returns                    |

## References

| Theory                      | Application in ReversalEffect LLM              | Reference                |
|-----------------------------|-----------------------------------------------|--------------------------|
| **Overreaction Hypothesis** | LLMContrarian trades reversal patterns        | De Bondt & Thaler (1985) |
| **Overconfidence**          | LLMOverconfident creates initial overreaction | Daniel et al. (1998)     |
| **Mean Reversion**          | Price eventually returns to fundamental       | Fama & French (1988)     |
| **Contrarian Strategy**     | Buy losers, sell winners                      | (Investment Strategy)    |
