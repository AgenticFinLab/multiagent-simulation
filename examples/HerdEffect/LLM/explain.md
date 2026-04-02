# HerdEffect LLM - LLM-Powered Emergent Herding Simulation

## What is This?

| Item               | Description                                                                         |
|--------------------|-------------------------------------------------------------------------------------|
| **Phenomenon**     | **Emergent Herding (涌现型羊群效应)** - 无预设模仿者的自发行为趋同                  |
| **Model**          | LLM-based investors with prompt-defined personalities + Rule-based market clearing  |
| **Key Feature**    | Investors use LLM reasoning to make decisions, herding EMERGES from their behavior  |
| **Academic Value** | Tests whether LLMs can simulate realistic investor psychology and emergent behavior |

## Rule-Based vs LLM-Based Comparison

| Aspect               | HerdEffect (Rule-Based)                  | HerdEffect LLM (LLM-Based)                   |
|----------------------|------------------------------------------|---------------------------------------------|
| **Decision Logic**   | Fixed mathematical formulas              | LLM interprets market data via prompts      |
| **Investor Types**   | 5 types with hardcoded strategies        | 5 types with personality-defining prompts   |
| **Behavior**         | Deterministic (same input → same output) | Stochastic (LLM may vary responses)         |
| **Market**           | Rule-based order clearing                | **Same** rule-based order clearing          |
| **Emergent Herding** | From positive feedback formulas          | From LLM "reasoning" about market           |
| **Research Value**   | Mechanism validation                     | LLM behavioral realism + emergent phenomena |

> **核心差异**：HerdEffect 用公式模拟投资者行为，HerdEffect LLM 用大模型通过 prompt 定义的"性格"来推理决策。

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │          HerdEffect LLM Architecture       │
                    └──────────────────────────────────────────┘

   ┌─────────────────────────────────────────────────────────────────────┐
   │                         Market (Rule-Based)                          │
   │   - NOT LLM: uses deterministic price formula                       │
   │   - P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε                       │
   │   - Collects orders, clears market, broadcasts price                │
   └─────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Broadcast: {price, volume, return}
                                     ▼
   ┌─────────────────────────────────────────────────────────────────────┐
   │                    LLM Investors (5 Types)                          │
   │                                                                     │
   │   ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
   │   │ Momentum  │  │Contrarian │  │RiskAverse │  │Aggressive │  │  Noise    │
   │   │   LLM     │  │   LLM     │  │   LLM     │  │   LLM     │  │   LLM     │
   │   └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
   │         │              │              │              │              │
   │         ▼              ▼              ▼              ▼              ▼
   │   ┌─────────────────────────────────────────────────────────────┐   │
   │   │               ByteDance Doubao API (via lmbase)             │   │
   │   │   System Prompt (personality) + User Prompt (market data)   │   │
   │   │                      → JSON Decision                        │   │
   │   └─────────────────────────────────────────────────────────────┘   │
   └─────────────────────────────────────────────────────────────────────┘
                                     │
                                     │ Orders: {bid_price, quantity, reasoning}
                                     ▼
                           ┌─────────────────┐
                           │  Market Clearing│
                           └─────────────────┘
```

## LLM Provider: ByteDance Doubao via lmbase

| Configuration         | Value                                             |
|-----------------------|---------------------------------------------------|
| **Library**           | `lmbase.inference.api_call.LangChainAPIInference` |
| **Model Format**      | `lm_name: "ark/ep-xxxx"`                          |
| **Auth**              | `ARK_API_KEY` environment variable                |
| **Generation Config** | `temperature: 0.3`, `max_new_tokens: 500`         |

### lmbase Inference Flow

```python
from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

# Initialize
llm_client = LangChainAPIInference(
    lm_name="ark/ep-20250218212539-7r2k9",
    generation_config={"temperature": 0.3, "max_new_tokens": 500}
)

# Call
infer_input = InferInput(system_msg=SYSTEM_PROMPT, user_msg=USER_PROMPT)
infer_output = llm_client.run(infer_input)
response = infer_output.response  # JSON string
```

## LLM Input/Output Format

### User Prompt (Market Data)

```
Current Market Data:
- Price: $105.23
- Previous Price: $103.50
- Return: +1.67%
- Volume: 45.00
- Net Demand: +12.30
- Fundamental Value: $100.00
- Recent Prices: [100.0, 101.2, 102.8, 103.5, 105.23]

Your Portfolio:
- Cash: $8500.00
- Position: 15.00 shares
- Portfolio Value: $10078.45

Make your trading decision. Respond with ONLY valid JSON:
{
    "action": "buy" | "sell" | "hold",
    "bid_price": <your limit price>,
    "quantity": <number of shares, positive for buy, negative for sell>,
    "reasoning": "<brief explanation>"
}
```

### LLM Output (JSON Decision)

```json
{
    "action": "buy",
    "bid_price": 105.50,
    "quantity": 20.0,
    "reasoning": "Price momentum is strong (+1.67%), trend following signals suggest buying"
}
```

### Retry on Parse Failure

```
If LLM output is not valid JSON → Retry up to 3 times
If all retries fail → RuntimeError (no default values, no fallbacks)
```

## 5 LLM Investor Types

### Investor Type Summary

| Type              | Strategy           | Market Effect             | System Prompt Focus                 |
|-------------------|--------------------|---------------------------|-------------------------------------|
| **LLMMomentum**   | Trend Following    | ⭐ DESTABILIZING           | "The trend is your friend"          |
| **LLMAggressive** | Leveraged Momentum | ⭐ EXTREMELY DESTABILIZING | "Go big or go home"                 |
| **LLMContrarian** | Value Investing    | STABILIZING               | "Be fearful when others are greedy" |
| **LLMRiskAverse** | Volatility Avoid   | EARLY EXIT                | "Protect your capital"              |
| **LLMNoise**      | Random/Retail      | ⭐ TRIGGER SOURCE          | "Trade on gut feelings"             |

---

### 1. LLMMomentumInvestor (⭐ Primary Positive Feedback)

**System Prompt:**
```
You are a MOMENTUM INVESTOR following trend-following strategy.

CORE BELIEF: "The trend is your friend" - prices that rise will continue to rise.

YOUR TRADING RULES:
1. If price is RISING (positive return): BUY aggressively
2. If price is FALLING (negative return): SELL to cut losses
3. The stronger the trend, the larger your position

BEHAVIOR:
- You believe in price momentum and market trends
- You react QUICKLY to price movements
- You are NOT concerned with fundamental value
- You follow the crowd when trends are strong

RISK PROFILE: High - you buy high and sell low if trend reverses
```

| Aspect            | Description                            |
|-------------------|----------------------------------------|
| **Effect**        | DESTABILIZING - amplifies price trends |
| **Risk**          | High - buys at peaks, sells at bottoms |
| **Emergent Role** | Core driver of positive feedback loop  |

---

### 2. LLMAggressiveInvestor (⭐ Extreme Amplifier)

**System Prompt:**
```
You are an AGGRESSIVE/LEVERAGED MOMENTUM INVESTOR.

CORE BELIEF: "Go big or go home - maximize gains in strong trends."

YOUR TRADING RULES:
1. If price is rising AND accelerating: BUY HEAVILY (large position)
2. If price is falling AND accelerating down: SELL EVERYTHING
3. Look for "price acceleration" - when the rate of change is increasing

BEHAVIOR:
- You use LEVERAGE mentally - take larger positions than others
- You look for ACCELERATION signals (price rising faster and faster)
- You are EXTREMELY reactive to market movements
- You aim for maximum profit, accepting maximum risk

RISK PROFILE: Very High - can cause flash crashes
```

| Aspect            | Description                                       |
|-------------------|---------------------------------------------------|
| **Effect**        | EXTREMELY DESTABILIZING - leverage + acceleration |
| **Risk**          | Very High - can trigger flash crashes             |
| **Emergent Role** | Amplifies momentum signals, accelerates bubbles   |

---

### 3. LLMContrarianInvestor (Value Anchor)

**System Prompt:**
```
You are a CONTRARIAN/VALUE INVESTOR.

CORE BELIEF: "Be fearful when others are greedy, greedy when others are fearful."

YOUR TRADING RULES:
1. If price > fundamental value (100): SELL - market is overvalued
2. If price < fundamental value (100): BUY - market is undervalued
3. The larger the deviation from fundamental, the larger your position

BEHAVIOR:
- You believe prices always return to fundamental value
- You buy when everyone else is selling (market panic)
- You sell when everyone else is buying (market euphoria)
- You are PATIENT and wait for value opportunities

RISK PROFILE: Medium - may buy into falling markets too early
```

| Aspect            | Description                              |
|-------------------|------------------------------------------|
| **Effect**        | STABILIZING - dampens price deviations   |
| **Risk**          | Medium - may catch falling knives        |
| **Emergent Role** | Mean reversion force, limits bubble size |

---

### 4. LLMRiskAverseInvestor (Early Warning)

**System Prompt:**
```
You are a RISK-AVERSE INVESTOR focused on capital preservation.

CORE BELIEF: "Protect your capital - high volatility means high risk."

YOUR TRADING RULES:
1. If recent prices are VOLATILE (large swings): REDUCE position
2. If market is CALM (small price changes): May increase position
3. Always maintain a large cash buffer for safety

BEHAVIOR:
- You HATE losing money more than you like making money
- You watch price swings closely - erratic markets scare you
- You prefer small, steady gains over risky big wins
- You EXIT early when you sense trouble brewing

RISK PROFILE: Low - you sacrifice returns for safety
```

| Aspect            | Description                        |
|-------------------|------------------------------------|
| **Effect**        | EARLY EXIT - triggers before crash |
| **Risk**          | Low - sacrifices upside for safety |
| **Emergent Role** | Can trigger domino exit cascade    |

---

### 5. LLMNoiseTrader (⭐ Initial Trigger)

**System Prompt:**
```
You are a NOISE TRADER - an uninformed retail investor.

CORE BELIEF: You trade based on gut feelings, rumors, and random impulses.

YOUR TRADING RULES:
1. You don't follow any strict strategy
2. You make decisions based on "feelings" about the market
3. Sometimes you buy randomly, sometimes you sell randomly
4. You tend to gradually reduce extreme positions (mean revert)

BEHAVIOR:
- You are NOT sophisticated - you don't analyze deeply
- You react to news and rumors (even if they're noise)
- You provide LIQUIDITY to the market
- Your trades are somewhat RANDOM but not completely

RISK PROFILE: Random - you're the "average retail investor"
```

| Aspect            | Description                                   |
|-------------------|-----------------------------------------------|
| **Effect**        | TRIGGER SOURCE - random signal starts cascade |
| **Risk**          | Random - provides liquidity                   |
| **Emergent Role** | Accidental catalyst for positive feedback     |

## LLM-Based Emergent Herding Mechanism

```
                    ┌──────────────────────────────────────────┐
                    │   LLM-Based Emergent Herding Mechanism   │
                    │   (大模型推理产生的行为趋同)              │
                    └──────────────────────────────────────────┘

  Phase 1: TRIGGER (触发)
  ─────────────────────────
  LLMNoiseTrader "feels like buying" → Random buy order
                 │
                 ▼
  Price微涨 (ΔP > 0)
                 │
                 ▼
  Phase 2: LLM REASONING (大模型推理)
  ────────────────────────────────────
  LLMMomentumInvestor receives: "Return: +0.5%"
  LLM thinks: "Trend is positive, my rule is to BUY"
                 │
                 ▼
  LLM outputs: {"action": "buy", "quantity": 15, "reasoning": "following uptrend"}
                 │
                 ▼
  Phase 3: FEEDBACK AMPLIFICATION (反馈放大)
  ──────────────────────────────────────────
  Price further rises → LLMAggressive sees acceleration
  LLM thinks: "Price accelerating, go big or go home"
                 │
                 ▼
  LLM outputs: {"action": "buy", "quantity": 50, "reasoning": "strong momentum"}
                 │
                 ▼
  Phase 4: BEHAVIORAL CONVERGENCE (行为趋同)
  ──────────────────────────────────────────
  Even LLMContrarian's stabilizing effect is overwhelmed
  All LLM investors independently "reason" into similar BUY decisions
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   EMERGENT RESULT (涌现结果)    │
         │   LLM推理导致行为趋同 → 买入    │
         │   无显式模仿，涌现于推理过程！  │
         └─────────────────────────────────┘
```

### Why LLM Herding is Emergent (为什么LLM羊群是涌现的)

| Traditional Rule-Based   | LLM-Based                                      |
|--------------------------|------------------------------------------------|
| Fixed formula: Q = f(P)  | LLM "reasons" about market data                |
| Same input → Same output | Same input → Varied reasoning, similar outcome |
| Herding from math        | Herding from LLM "psychology"                  |
| Mechanism is explicit    | Mechanism is **implicit in LLM reasoning**     |

> **研究价值**: LLM是否能通过prompt定义的"性格"产生符合金融理论的涌现行为？

## Market Clearing (Rule-Based, Not LLM)

```
Order-Based Clearing:

  1. Collect all orders (P_i, Q_i) from LLM investors
  2. Calculate net demand: D = Σ(buy_qty) - Σ(sell_qty)
  3. Price update:
  
     P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε
     
     Where:
       λ = 0.1   (supply elasticity / market depth)
       γ = 0.02  (mean reversion speed)
       F = 100.0 (fundamental value)
       ε ~ N(0, 0.5)
```

| Parameter             | Value  | Financial Meaning                         |
|-----------------------|--------|-------------------------------------------|
| λ (Supply Elasticity) | 0.1    | Higher = less liquid, more price impact   |
| γ (Mean Reversion)    | 0.02   | Speed of price correction to fundamentals |
| F (Fundamental)       | 100.0  | True intrinsic value                      |
| Initial Cash          | 10,000 | Per-investor starting capital             |
| Initial Position      | 0      | No initial holdings                       |

## Topology (Star Network)

```
                         ┌───────────────────┐
                         │      market       │ ◄── Level 0 (rule-based clearing)
                         └─────────┬─────────┘
                                   │
         ┌───────────┬─────────────┼─────────────┬───────────┐
         ▼           ▼             ▼             ▼           ▼
   llm_momentum  llm_contrarian llm_risk_averse llm_aggressive llm_noise
   (⭐ feedback) (stabilize)    (early exit)   (⭐ amplify)   (⭐ trigger)
         │           │             │             │           │
         └───────────┴─────────────┴─────────────┴───────────┘
                                   │
                          ┌────────┴────────┐
                          │ ByteDance Doubao│
                          │ LLM API (lmbase)│
                          └─────────────────┘
```

## Files

| File                                     | Purpose                                    |
|------------------------------------------|--------------------------------------------|
| `examples/HerdEffect/LLM/players.py`      | Market + 5 LLM investor classes            |
| `examples/HerdEffect/LLM/run_herd_llm.py` | Entry point                                |
| `examples/HerdEffect/LLM/analysis.py`     | Numerical + Text interpretability analysis |
| `configs/HerdEffect/LLM/simulation.yml`   | Main config (rounds, paths)                |
| `configs/HerdEffect/LLM/players.yml`      | Player definitions + LLM config            |
| `configs/HerdEffect/LLM/topology.yml`     | Star topology                              |

## Configuration

### simulation.yml

```yaml
setting:
  name: "herd_effect_llm_simulation"
  description: "LLM-based investors simulating emergent herding behavior"
  total_rounds: 10
  entry_limit: 100
  record_path: "EXPERIMENT/HerdEffect/LLM/records"
```

### players.yml (LLM Config)

```yaml
llm_api:
  lm_name: "ark/ep-20250218212539-7r2k9"
  generation_config:
    temperature: 0.3
    max_new_tokens: 500
```

## Running

```bash
# Set API key
export ARK_API_KEY='your-bytedance-doubao-api-key'

# Run simulation
python examples/HerdEffect/LLM/run_herd_llm.py -c configs/HerdEffect/LLM/simulation.yml

# Analyze results (numerical + text interpretability)
python examples/HerdEffect/LLM/analysis.py -c configs/HerdEffect/LLM/simulation.yml
```

## Analysis Output

### Numerical Charts

| Chart                          | Description                        |
|--------------------------------|------------------------------------|
| `00_summary_panel.png`         | 6-panel comprehensive summary      |
| `01_price_chart.png`           | Price & LLM investor bids          |
| `02_quantity_chart.png`        | Trading quantities per investor    |
| `03_bid_convergence.png`       | Bid CV (herding indicator)         |
| `04_directional_agreement.png` | Behavioral alignment detection     |
| `05_reasoning_keywords.png`    | LLM reasoning keyword distribution |

### Text Interpretability Report (`text_analysis.md`)

Unique to LLM-based simulation:

```markdown
# HerdEffect LLM - Per-Round Interpretability Report

## Round 1
### Market State
- Price: $100.50
- Return: +0.50%

### LLM Investor Decisions
| Investor   | Strategy       | Bid    | Qty   | Action | Reasoning                                             |
|------------|----------------|--------|-------|--------|-------------------------------------------------------|
| momentum   | llm_momentum   | 101.00 | +15.0 | BUY    | Positive trend detected, following upward momentum... |
| contrarian | llm_contrarian | 99.50  | -5.0  | SELL   | Price above fundamental, market overvalued...         |
...

### Behavioral Summary
- BUY: 3/5 (60%)
- SELL: 1/5 (20%)
- HOLD: 1/5 (20%)

---

## Emergent Herding Interpretation
**STRONG EMERGENT HERDING DETECTED**
LLM investors independently converged on similar decisions...
```

### Reasoning Chain Analysis

Traces each investor's reasoning evolution:

```markdown
## investor_momentum (llm_momentum)

### Round 1
- Action: BUY
- Reasoning: "Positive return signals uptrend, buying according to trend-following rule"

### Round 2  
- Action: BUY
- Reasoning: "Momentum continues, price acceleration detected"
...
```

## Expected LLM Behavior Patterns

| Phase    | Rounds | LLM Behavior                                         |
|----------|--------|------------------------------------------------------|
| Initial  | 1-3    | LLMs "learn" market state, mixed decisions           |
| Build-up | 4-6    | LLMMomentum detects trend, starts buying             |
| Cascade  | 7-8    | LLMAggressive amplifies, LLMContrarian overwhelmed   |
| Peak     | 9-10   | Behavioral convergence - all LLMs reasoning into BUY |

## Research Questions

| Question                                            | How to Test                                         |
|-----------------------------------------------------|-----------------------------------------------------|
| Can LLMs simulate realistic investor personalities? | Compare LLM decisions with theoretical expectations |
| Does emergent herding arise from LLM reasoning?     | Analyze bid convergence and directional agreement   |
| How do LLM "personalities" interact?                | Track reasoning chains across investor types        |
| Is LLM herding more realistic than rule-based?      | Compare price dynamics with real market bubbles     |

## Comparison: HerdEffect vs HerdEffect LLM

| Metric               | HerdEffect (Rule)    | HerdEffect LLM           |
|----------------------|----------------------|-------------------------|
| Decision Time        | Instant (formula)    | ~1-2s per LLM call      |
| Reproducibility      | 100% deterministic   | Stochastic (LLM varies) |
| Reasoning Visibility | None (just numbers)  | Full reasoning strings  |
| Behavior Realism     | Theoretical          | Potentially more human  |
| Research Novelty     | Mechanism validation | LLM behavioral finance  |

## References

| Theory                     | Application in HerdEffect LLM                           | Reference                  |
|----------------------------|--------------------------------------------------------|----------------------------|
| **Momentum**               | LLMMomentumInvestor prompt: "trend is your friend"     | Jegadeesh & Titman (1993)  |
| **Contrarian**             | LLMContrarianInvestor prompt: "be fearful when greedy" | De Bondt & Thaler (1985)   |
| **Noise Trader**           | LLMNoiseTrader prompt: "gut feelings and impulses"     | De Long et al. (1990)      |
| **Information Cascade**    | Emergent from LLM reasoning convergence                | Bikhchandani et al. (1992) |
| **LLM Behavioral Finance** | New research direction                                 | (This work)                |
