# VolatilityClustering LLM - LLM-Powered Volatility Clustering Simulation

## What is This?

| Item               | Description                                                                  |
|--------------------|------------------------------------------------------------------------------|
| **Phenomenon**     | 波动率聚集 (Volatility Clustering) - LLM-driven GARCH-like dynamics          |
| **Model**          | LLM-based investors with volatility sensitivity + Rule-based market          |
| **Key Feature**    | LLMs adjust trading behavior based on perceived volatility regime            |
| **Academic Value** | Tests whether LLMs can reproduce Mandelbrot (1963) / Engle (1982) clustering |

## Rule-Based vs LLM Comparison

| Aspect              | Rule-Based (VolatilityClustering) | LLM Version                        |
|---------------------|-----------------------------------|------------------------------------|
| Volatility Response | Formula-based scaling             | LLM "volatility means opportunity" |
| Adaptation Speed    | Fixed parameters                  | LLM chooses reaction speed         |
| Position Sizing     | Deterministic                     | LLM reasons about risk/reward      |
| Emergence           | GARCH-like autocorrelation        | Emergent clustering patterns       |

## LLM Provider

- **Provider**: ByteDance Doubao (豆包) via `lmbase.LangChainAPIInference`
- **Model**: `doubao-pro-256k`

## 5 LLM Investor Types

| Type              | Count | Role                 | Volatility Response       |
|-------------------|-------|----------------------|---------------------------|
| Fundamentalist    | 2     | Stabilizer (Slow)    | Ignores volatility        |
| Trend Follower    | 2     | Amplifier (Fast)     | High vol → larger trades  |
| Noise Trader      | 2     | Shock Provider       | Random                    |
| Slow Adapter      | 1     | Stabilizer (Delayed) | High vol → more cautious  |
| Volatility Trader | 1     | Stabilizer           | Mean-reverts vol exposure |

### Trend Follower (Volatility Amplifier)

```
CORE BELIEF: "The trend is your friend - momentum drives markets."

VOLATILITY RESPONSE:
- When volatility is HIGH: INCREASE position sizes (more opportunity)
- When volatility is LOW: DECREASE position sizes (boring market)
- You AMPLIFY volatility through your trading

RISK PROFILE: High - you amplify market moves
```

### Fundamentalist (Slow Stabilizer)

```
CORE BELIEF: "Price always returns to fundamental value (100) - be patient."

VOLATILITY RESPONSE:
- You do NOT react to volatility spikes - they are temporary
- High volatility might create buying opportunities
- You are the "anchor" that eventually pulls price back to fundamentals
```

### Volatility Trader (Vol Mean-Reversion)

```
CORE BELIEF: "Volatility mean reverts - sell high vol, buy low vol."

VOLATILITY RESPONSE:
- High volatility → SELL (expecting vol to decrease, price to stabilize)
- Low volatility → BUY (expecting calm to continue, prices to rise)
- You help DAMPEN extreme volatility spikes
```

## Key Mechanism: Volatility Clustering

```
┌─────────────────────────────────────────────────────────┐
│              VOLATILITY CLUSTERING DYNAMICS              │
│                                                          │
│   ┌─────────────┐          ┌─────────────┐              │
│   │  FAST       │          │  SLOW       │              │
│   │  AMPLIFIERS │          │  STABILIZERS│              │
│   │  (Trend     │          │  (Value     │              │
│   │   Followers)│          │   Investors)│              │
│   └──────┬──────┘          └──────┬──────┘              │
│          │                        │                      │
│          │ React QUICKLY          │ React SLOWLY         │
│          │ to volatility          │ to volatility        │
│          │                        │                      │
│          ▼                        ▼                      │
│   ┌─────────────────────────────────────────┐           │
│   │                                         │           │
│   │   Short-term: AMPLIFIERS dominate       │           │
│   │   → Volatility PERSISTS (clustering)    │           │
│   │                                         │           │
│   │   Long-term: STABILIZERS catch up       │           │
│   │   → Volatility eventually DECAYS        │           │
│   │                                         │           │
│   └─────────────────────────────────────────┘           │
│                                                          │
│   Result: GARCH(1,1)-like autocorrelation in volatility │
│   σ²(t) = ω + α·ε²(t-1) + β·σ²(t-1)                    │
└─────────────────────────────────────────────────────────┘
```

## Theoretical Basis: GARCH / Mandelbrot

**Volatility Clustering** (Mandelbrot 1963, Engle 1982):
- "Large changes tend to be followed by large changes, of either sign"
- Key empirical fact: |r_t| and |r_{t-1}| are positively correlated
- GARCH model captures this through conditional variance autoregression
- **Mechanism in this simulation**:
  - Fast traders (trend followers) react immediately → amplify initial shock
  - Slow traders (fundamentalists) react gradually → provide delayed stabilization
  - Speed difference creates the clustering pattern

## Files

| File          | Purpose                                                  |
|---------------|----------------------------------------------------------|
| `players.py`  | LLM investor implementations with volatility sensitivity |
| `prompts.py`  | 5 system prompts defining volatility response patterns   |
| `run_llm.py`  | LLM simulation runner                                    |
| `analysis.py` | Volatility autocorrelation metrics                       |

## Running

```bash
cd examples/VolatilityClustering/LLM
python run_llm.py
```

## Expected LLM Behavior Patterns

1. **Amplification Phase**: Trend followers increase position sizes during high volatility
2. **Persistence**: Volatility remains elevated for multiple rounds
3. **Gradual Decay**: Fundamentalists slowly pull price back to fundamentals
4. **Regime Switching**: Clear distinction between high-vol and low-vol periods
5. **Autocorrelation**: |r_t| correlated with |r_{t-1}| through |r_{t-5}|

## Research Questions

1. Do LLMs correctly perceive volatility regimes from price history?
2. Can LLM trading produce GARCH-like autocorrelation without explicit programming?
3. How do LLM reaction speeds compare to rule-based investor parameters?
4. Does the fundamentalist "anchor" successfully mean-revert prices?

## References

- Mandelbrot, B. (1963). The Variation of Certain Speculative Prices. Journal of Business.
- Engle, R. F. (1982). Autoregressive Conditional Heteroscedasticity. Econometrica.
- Bollerslev, T. (1986). Generalized Autoregressive Conditional Heteroskedasticity. JoE.
