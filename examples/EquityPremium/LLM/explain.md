# EquityPremium LLM - LLM-Powered Equity Premium Puzzle Simulation

## What is This?

| Item               | Description                                                            |
|--------------------|------------------------------------------------------------------------|
| **Phenomenon**     | 股权溢价之谜 (Equity Premium Puzzle) - LLM-driven myopic loss aversion |
| **Model**          | LLM-based investors with psychological biases + Rule-based market      |
| **Key Feature**    | LLMs exhibit loss aversion and myopic evaluation like real investors   |
| **Academic Value** | Tests whether LLMs can reproduce Benartzi & Thaler (1995) MLA theory   |

## Rule-Based vs LLM Comparison

| Aspect             | Rule-Based (EquityPremium) | LLM Version                      |
|--------------------|----------------------------|----------------------------------|
| Loss Aversion      | Formula-based λ=2.25       | LLM "losses hurt 2.25x more"     |
| Evaluation Horizon | Fixed frequency            | LLM chooses evaluation frequency |
| Rebalancing        | Deterministic rules        | LLM reasons about allocation     |
| Emergence          | Predictable premium        | Emergent risk aversion           |

## LLM Provider

- **Provider**: ByteDance Doubao (豆包) via `lmbase.LangChainAPIInference`
- **Model**: `doubao-pro-256k`

## 5 LLM Investor Types

| Type               | Count | Role           | Stock Target |
|--------------------|-------|----------------|--------------|
| Myopic Loss-Averse | 3     | Premium Driver | 30-50%       |
| Long-Term Investor | 2     | Stabilizer     | 60-80%       |
| Institutional      | 1     | Benchmark      | 60%          |
| Risk-Averse Saver  | 1     | Extreme MLA    | 20-30%       |
| Rational Optimizer | 1     | Theoretical    | 50-70%       |

### Myopic Loss-Averse Investor (Key Type)

```
PSYCHOLOGY:
- Evaluate EVERY round (myopic)
- Losses hurt 2.25x more than gains (λ=2.25)
- Stocks look VERY risky
- Target: 30-50% stocks

After negative return: Reduce stocks
```

### Long-Term Investor (Counter-Type)

```
PSYCHOLOGY:
- Daily volatility = noise
- Focus on long-term returns
- Maintain HIGH stock allocation (60-80%)
- Buy when others panic
```

### Risk-Averse Saver (Extreme MLA)

```
- HATE volatility
- Target: 20-30% stocks maximum
- Any drop → reduce stocks
```

## Key Mechanism: Myopic Loss Aversion

```
┌─────────────────────────────────────────────────────────┐
│                 MLA EVALUATION CYCLE                     │
│                                                          │
│    Frequent Evaluation    +    Loss Aversion (λ=2.25)   │
│           │                         │                    │
│           ▼                         ▼                    │
│   ┌───────────────┐         ┌───────────────┐           │
│   │ More Loss     │         │ Losses Hurt   │           │
│   │ Observations  │         │ More Than     │           │
│   │               │         │ Gains Feel    │           │
│   └───────┬───────┘         └───────┬───────┘           │
│           │                         │                    │
│           └──────────┬──────────────┘                    │
│                      │                                   │
│                      ▼                                   │
│           ┌─────────────────────┐                        │
│           │  Stocks Appear      │                        │
│           │  TOO RISKY          │                        │
│           │  (even though       │                        │
│           │   they're not)      │                        │
│           └──────────┬──────────┘                        │
│                      │                                   │
│                      ▼                                   │
│           ┌─────────────────────┐                        │
│           │  Demand Higher      │                        │
│           │  Risk Premium       │                        │
│           │  (~6% vs 1% bonds)  │                        │
│           └─────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## Theoretical Basis: Benartzi & Thaler (1995)

**Myopic Loss Aversion (MLA)**:
- Combines two behavioral factors:
  1. **Loss Aversion** (Kahneman & Tversky): Losses weigh ~2.25x more than equivalent gains
  2. **Myopic Evaluation**: Frequent portfolio checking makes volatility salient
- Result: Investors perceive stocks as riskier than rational analysis suggests
- Explains why equity premium (~6%) is "too high" relative to bond returns (~1%)
- LLMs model this by explicitly stating psychological evaluation patterns

## Files

| File          | Purpose                                          |
|---------------|--------------------------------------------------|
| `players.py`  | LLM investor implementations with MLA psychology |
| `prompts.py`  | 5 system prompts defining loss aversion patterns |
| `run_llm.py`  | LLM simulation runner                            |
| `analysis.py` | Premium and allocation metrics                   |

## Running

```bash
cd examples/EquityPremium/LLM
python run_llm.py
```

## Expected LLM Behavior Patterns

1. **Myopic Evaluation**: MLA investors check portfolio every round
2. **Loss Over-Reaction**: Stock drops trigger immediate selling
3. **Under-Allocation**: MLA investors hold <50% stocks despite higher returns
4. **Long-Term Stability**: Long-horizon investors maintain high allocation
5. **Premium Emergence**: Market-clearing requires higher expected returns for stocks

## Research Questions

1. Do LLMs exhibit genuine loss aversion in their reasoning?
2. Can LLMs reproduce the ~6% equity premium through behavioral biases?
3. How do LLM evaluation frequencies compare to human investor behavior?
4. Does the mix of MLA and long-term investors produce realistic allocations?

## References

- Benartzi, S., & Thaler, R. H. (1995). Myopic Loss Aversion and the Equity Premium Puzzle. QJE.
- Kahneman, D., & Tversky, A. (1979). Prospect Theory. Econometrica.
- Mehra, R., & Prescott, E. C. (1985). The Equity Premium: A Puzzle. JME.
