# MarketCrashLLM - LLM-Powered Market Crash Simulation

## What is This?

| Item               | Description                                                                          |
|--------------------|--------------------------------------------------------------------------------------|
| **Phenomenon**     | **Market Crash (市场崩盘)** - LLM-driven panic selling and liquidity spiral dynamics |
| **Model**          | LLM-based investors with crash-prone personalities + Rule-based market clearing      |
| **Key Feature**    | Investors use LLM reasoning to exhibit panic, margin calls, and liquidity withdrawal |
| **Academic Value** | Tests whether LLMs can simulate realistic crash psychology and cascade dynamics      |

## Rule-Based vs LLM-Based Comparison

| Aspect              | MarketCrash (Rule-Based)           | MarketCrashLLM (LLM-Based)                 |
|---------------------|------------------------------------|--------------------------------------------|
| **Decision Logic**  | Fixed mathematical formulas        | LLM interprets market stress via prompts   |
| **Investor Types**  | 5 types with hardcoded strategies  | 5 types with personality-defining prompts  |
| **Behavior**        | Deterministic crash triggers       | Stochastic panic responses                 |
| **Market**          | Rule-based with liquidity dynamics | **Same** rule-based clearing               |
| **Crash Mechanism** | From margin call formulas          | From LLM "fear" and "forced selling" logic |
| **Research Value**  | Mechanism validation               | LLM panic realism + emergent crashes       |

> **核心差异**：MarketCrash 用公式触发崩盘，MarketCrashLLM 用大模型通过 prompt 定义的"恐慌心理"来推理决策。

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │        MarketCrashLLM Architecture       │
                    └──────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────────────┐
   │                         Market (Rule-Based)                         │
   │   - Crash-prone dynamics with liquidity feedback                    │
   │   - P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε                       │
   │   - Liquidity factor amplifies price impact during stress           │
   └─────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Broadcast: {price, liquidity, volatility}
                                     ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    LLM Investors (5 Types)                          │
   │                                                                     │
   │   ┌───────────────┐ ┌───────────────┐ ┌───────────────┐            │
   │   │PanicSeller    │ │RiskParity     │ │LeveragedFund  │            │
   │   │(⭐ cascade    │ │(vol targeting)│ │(⭐ margin     │            │
   │   │  trigger)     │ │               │ │   calls)      │            │
   │   └───────┬───────┘ └───────┬───────┘ └───────┬───────┘            │
   │           │                 │                 │                     │
   │   ┌───────────────┐ ┌───────────────┐                              │
   │   │MarketMaker    │ │BottomFisher   │                              │
   │   │(withdraws in  │ │(stabilizing)  │                              │
   │   │ stress)       │ │               │                              │
   │   └───────┬───────┘ └───────┬───────┘                              │
   │           ▼                 ▼                                       │
   │   ┌─────────────────────────────────────────────────────────────┐  │
   │   │               ByteDance Doubao API (via lmbase)             │  │
   │   └─────────────────────────────────────────────────────────────┘  │
   └─────────────────────────────────────────────────────────────────────┘
```

## 5 LLM Investor Types

### Investor Type Summary

| Type                  | Strategy             | Market Effect        | System Prompt Focus                       |
|-----------------------|----------------------|----------------------|-------------------------------------------|
| **LLMPanicSeller**    | Fear-driven exit     | ⭐ CASCADE TRIGGER    | "I can't afford to lose any more!"        |
| **LLMRiskParityFund** | Volatility targeting | FORCED DELEVERAGING  | "Maintain constant portfolio risk"        |
| **LLMLeveragedFund**  | Margin-constrained   | ⭐ FORCED LIQUIDATION | "Leverage amplifies returns...and losses" |
| **LLMMarketMaker**    | Liquidity provider   | WITHDRAWAL → CRISIS  | "Won't catch falling knives"              |
| **LLMBottomFisher**   | Value buying         | STABILIZING          | "Be greedy when others are fearful"       |

### 1. LLMPanicSeller (⭐ Cascade Trigger)

**Theory**: Loss aversion + Herding under stress

| Aspect         | Description                             |
|----------------|-----------------------------------------|
| **Effect**     | CASCADE TRIGGER - starts selling domino |
| **Behavior**   | Panic on price drops, sell at any price |
| **Psychology** | Losses hurt 3x more than gains          |

### 2. LLMRiskParityFund (Volatility-Triggered)

**Theory**: Risk parity funds must sell when volatility rises to maintain target risk.

| Aspect       | Description                          |
|--------------|--------------------------------------|
| **Effect**   | FORCED DELEVERAGING                  |
| **Behavior** | Mechanical selling when vol > target |
| **Rules**    | Vol > 2.0 → reduce; Vol > 3.0 → sell |

### 3. LLMLeveragedFund (⭐ Margin Calls)

**Theory**: Leverage amplifies losses, triggers forced liquidation.

| Aspect         | Description                           |
|----------------|---------------------------------------|
| **Effect**     | FORCED LIQUIDATION                    |
| **Behavior**   | Must sell when portfolio < thresholds |
| **Thresholds** | <$7500 → 50% sell; <$5000 → sell all  |

### 4. LLMMarketMaker (Liquidity Withdrawal)

**Theory**: Market makers withdraw during extreme stress, worsening crisis.

| Aspect       | Description                              |
|--------------|------------------------------------------|
| **Effect**   | LIQUIDITY WITHDRAWAL → AMPLIFICATION     |
| **Behavior** | Withdraw when liquidity < 0.5 or vol > 3 |
| **State**    | ACTIVE (stabilizing) or WITHDRAWN        |

### 5. LLMBottomFisher (Stabilizing)

**Theory**: Value investors buy during panic, providing stabilizing demand.

| Aspect         | Description                         |
|----------------|-------------------------------------|
| **Effect**     | STABILIZING - eventual price floor  |
| **Behavior**   | Buy when price < 0.8 × fundamental  |
| **Psychology** | "Be greedy when others are fearful" |

## Market Clearing (Rule-Based)

```
Crash-Prone Price Model:

  P(t+1) = P(t) + λ×L(t)×D(t) + γ×[F - P(t)] + ε
  
  Where:
    λ = 0.1   (base price impact)
    L(t) = liquidity factor (>1 in stress)
    γ = 0.02  (mean reversion)
    F = 100.0 (fundamental value)

Liquidity Spiral:
  Low liquidity → Higher L(t) → Bigger price impact → More selling → Lower liquidity
```

## Topology (Star Network)

```
                         ┌───────────────────┐
                         │      market       │ ◄── Level 0 (crash-prone clearing)
                         └─────────┬─────────┘
                                   │
         ┌───────────┬─────────────┼─────────────┬───────────┐
         ▼           ▼             ▼             ▼           ▼
   llm_panic     llm_risk_parity llm_leveraged llm_mm    llm_bottom
   (⭐ cascade)  (vol trigger)   (⭐ margin)   (withdraw) (stabilize)
```

## Files

| File                                       | Purpose                          |
|--------------------------------------------|----------------------------------|
| `examples/MarketCrashLLM/players.py`       | Market + 5 LLM investor classes  |
| `examples/MarketCrashLLM/prompts.py`       | System and user prompt templates |
| `examples/MarketCrashLLM/run_crash_llm.py` | Entry point                      |
| `configs/MarketCrashLLM/simulation.yml`    | Main config (rounds, paths)      |
| `configs/MarketCrashLLM/players.yml`       | Player definitions + LLM config  |
| `configs/MarketCrashLLM/topology.yml`      | Star topology                    |

## Running

```bash
# Set API key
export ARK_API_KEY='your-bytedance-doubao-api-key'

# Run simulation
python examples/MarketCrashLLM/run_crash_llm.py -c configs/MarketCrashLLM/simulation.yml
```

## Expected LLM Behavior Patterns

| Phase        | Rounds | LLM Behavior                                      |
|--------------|--------|---------------------------------------------------|
| Stable       | 1-3    | Normal trading, mixed decisions                   |
| Stress Build | 4-6    | Volatility rises, RiskParity starts reducing      |
| Trigger      | 7-8    | PanicSeller detects drop, starts cascade          |
| Cascade      | 9-12   | LeveragedFund margin calls, MarketMaker withdraws |
| Capitulation | 13-15  | Maximum selling pressure, minimum liquidity       |
| Recovery     | 16-20  | BottomFisher buying provides floor                |

## Research Questions

| Question                                            | How to Test                                        |
|-----------------------------------------------------|----------------------------------------------------|
| Can LLMs exhibit realistic panic behavior?          | Track reasoning during price drops                 |
| Do margin call dynamics emerge naturally from LLMs? | Monitor LeveragedFund's portfolio calculations     |
| Does liquidity withdrawal amplify crashes?          | Track MarketMaker's ACTIVE/WITHDRAWN state changes |
| Can LLM bottom fishers stabilize crashes?           | Measure price floor formation timing               |

## References

| Theory               | Application in MarketCrashLLM             | Reference                      |
|----------------------|-------------------------------------------|--------------------------------|
| **Minsky Moment**    | Transition from stability to instability  | Minsky (1986)                  |
| **Liquidity Spiral** | LLMMarketMaker withdrawal amplifies crash | Brunnermeier & Pedersen (2009) |
| **Fire Sales**       | LLMLeveragedFund forced liquidation       | Shleifer & Vishny (2011)       |
| **Loss Aversion**    | LLMPanicSeller's extreme fear response    | Kahneman & Tversky (1979)      |
