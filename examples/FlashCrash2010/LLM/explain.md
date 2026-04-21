# FlashCrash2010 Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 2010 Flash Crash - High-frequency trading induced market collapse |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Order book depth dynamics, HFT liquidity withdrawal, feedback loops |
| **Academic Value** | Market microstructure fragility, algorithmic trading risks |

## Theoretical Foundation

### Primary Theory: Market Microstructure and Liquidity

**Kirilenko, Kyle, Samadi & Tuzun (2017)** - "The Flash Crash: High-Frequency Trading in an Electronic Market"
- *Journal of Finance*, 72(3), 967-998

Key Insight: High-frequency traders (HFTs) initially provide liquidity but withdraw it during stress,
creating a "hot potato" effect where intermediaries rapidly pass inventory among themselves
without absorbing it, leading to liquidity evaporation.

### Supporting Theories

1. **Order Book Dynamics** (Biais, Foucault & Moinas, 2015)
   - Bid-ask spread expansion under stress
   - Market depth disappearance

2. **Feedback Trading** (De Long et al., 1990)
   - Positive feedback loops amplify price movements
   - Momentum chasing by automated systems

3. **Synchronization Risk** (Abreu & Brunnermeier, 2003)
   - Coordinated withdrawal of liquidity
   - Strategic complementarity among HFTs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MARKET (Order Book)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Bid Side   │  │   Mid Price  │  │   Ask Side   │      │
│  │  (Buyers)    │  │              │  │  (Sellers)   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │  HFT    │           │  HFT    │           │  HFT    │
   │Market   │◄─────────►│Market   │◄─────────►│Market   │
   │Maker    │           │Maker    │           │Maker    │
   └────┬────┘           └────┬────┘           └────┬────┘
        │                     │                     │
   ┌────▼────┐           ┌────▼────┐           ┌────▼────┐
   │Fundamental│          │Momentum │           │StopLoss │
   │Trader    │          │Chaser   │           │Trader   │
   └─────────┘           └─────────┘           └─────────┘
```

## Agent Descriptions

### Market (Order Book Mechanism)

**Mechanism**: Continuous double auction with order book depth

**Price Formation**:
```
P(t+1) = P(t) + λ × NetOrderFlow / Depth(t) + ε

Where:
- Depth(t) = f(Spread, Recent Volatility, HFT Participation)
- λ = Price impact coefficient (increases as depth decreases)
- ε = Noise term
```

**Key Features**:
- Dynamic order book depth (shrinks during stress)
- Bid-ask spread widening
- Trade-through protection

### Agent Types

#### 1. HFT Market Maker
**Theoretical Basis**: Kirilenko et al. (2017)

**Behavior**:
- Provides liquidity via limit orders
- Tight spreads in normal conditions
- **Withdraws liquidity when**:
  - Price velocity exceeds threshold
  - Inventory builds up beyond limit
  - Spread widens beyond comfort zone

**Parameters**:
- Normal spread: 0.01% of price
- Stress spread: 0.5% of price
- Inventory limit: 1000 shares
- Withdrawal threshold: 2% price change in 1 minute

#### 2. Momentum Chaser (HFT)
**Theoretical Basis**: Feedback trading models

**Behavior**:
- Detects price trends using short-term signals
- Accelerates moves by chasing momentum
- Creates positive feedback loops

**Parameters**:
- Lookback window: 10 seconds
- Entry threshold: 0.1% move
- Position size: Proportional to velocity

#### 3. Fundamental Trader
**Theoretical Basis**: Value investing

**Behavior**:
- Knows true fundamental value
- Buys when price < 0.95 × fundamental
- Sells when price > 1.05 × fundamental
- Provides stabilizing force

**Parameters**:
- Fundamental value: $40.00
- Trigger threshold: ±5%
- Order size: 500 shares

#### 4. Stop-Loss Trader
**Theoretical Basis**: Predatory trading (Brunnermeier & Pedersen, 2005)

**Behavior**:
- Places stop-loss orders at -3% from entry
- When triggered, converts to market orders
- Creates "magnet effect" near stop levels

**Parameters**:
- Stop level: -3% from average entry
- Position size: 1000 shares
- Entry price: $40.00

#### 5. Noise Trader
**Theoretical Basis**: Black (1986)

**Behavior**:
- Random buy/sell decisions
- Creates background trading activity
- Represents uninformed flow

**Parameters**:
- Trade probability: 5% per round
- Order size: Random 100-500 shares

## Variant Comparison

| Variant | HFT Behavior | Key Difference |
|---------|-------------|----------------|
| **Rule** | Deterministic algorithms | Fixed thresholds, predictable withdrawal |
| **LLM** | LLM-driven decisions | Adaptive behavior based on market context |
| **RuleLLM** | Rules + LLM judgment | Can override rules based on qualitative assessment |
| **RAG** | Rules + LLM + Knowledge | Access to historical flash crash cases |

## Usage

### Rule Variant
```bash
python examples/FlashCrash2010/Rule/run_flashcrash2010.py \
    -c configs/FlashCrash2010/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/FlashCrash2010/LLM/run_flashcrash2010_llm.py \
    -c configs/FlashCrash2010/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/FlashCrash2010/RuleLLM/run_flashcrash2010_rulellm.py \
    -c configs/FlashCrash2010/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/FlashCrash2010/Rag/run_flashcrash2010_rag.py \
    -c configs/FlashCrash2010/Rag/simulation.yml
```

## Expected Results

### Stylized Facts to Observe

1. **Order Book Depth Collapse**: Depth should decrease by 80-90% during crash
2. **Spread Widening**: Bid-ask spread should expand 10-50x
3. **Price Cascade**: Sharp decline followed by rapid recovery
4. **HFT Withdrawal**: HFT participation drops during stress
5. **Volume Spike**: Trading volume increases dramatically

### Typical Metric Ranges

| Metric | Normal | Crash | Recovery |
|--------|--------|-------|----------|
| Bid-Ask Spread | 0.01-0.02% | 0.5-2.0% | 0.05-0.1% |
| Order Book Depth | 5000-10000 | 500-1000 | 2000-5000 |
| Price Change/Min | ±0.1% | -5% to -10% | +3% to +5% |
| HFT Participation | 60-70% | 10-20% | 40-50% |

## References

1. Kirilenko, A., Kyle, A. S., Samadi, M., & Tuzun, T. (2017). "The Flash Crash: High-Frequency Trading in an Electronic Market." *Journal of Finance*, 72(3), 967-998.

2. CFTC-SEC (2010). "Findings Regarding the Market Events of May 6, 2010." Report.

3. Biais, B., Foucault, T., & Moinas, S. (2015). "Equilibrium Fast Trading." *Journal of Financial Economics*, 116(2), 292-313.

4. Brunnermeier, M. K., & Pedersen, L. H. (2005). "Predatory Trading." *Journal of Finance*, 60(4), 1825-1863.

5. Abreu, D., & Brunnermeier, M. K. (2003). "Bubbles and Crashes." *Econometrica*, 71(1), 173-204.

6. De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). "Positive Feedback Investment Strategies and Destabilizing Rational Speculation." *Journal of Finance*, 45(2), 379-395.

7. Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543.
