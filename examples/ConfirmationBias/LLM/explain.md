# ConfirmationBias LLM Variant — Design Specification

## 1. Overview

| Item                     | Detail                                                                                       |
|--------------------------|----------------------------------------------------------------------------------------------|
| **Phenomenon**           | Confirmation bias dynamics reproduced by LLM-driven agents with bias-specific personas       |
| **Variant**              | LLM — all trader agents replaced by language model decision-makers                           |
| **Rounds**               | 200 (configurable)                                                                           |
| **Market**               | Identical deterministic Rule-based Market agent                                              |
| **Key Feature**          | LLM agents may spontaneously exhibit confirmation bias without explicit state tracking       |
| **Difference from Rule** | No internal belief state variable; LLM reasoning may implicitly anchor to prior observations |

---

## 2. Theory → Implementation Mapping

| Theoretical Concept          | Agent / Mechanism                                                        | Code Location                               |
|------------------------------|--------------------------------------------------------------------------|---------------------------------------------|
| Belief anchoring             | `LLMBeliefAnchor` persona: strong prior, overweights confirming evidence | `LLM/prompts.py: LLM_BELIEF_ANCHOR_SYS`     |
| Selective information search | `LLMSelectiveScanner` persona: actively seeks confirming signals         | `LLM/prompts.py: LLM_SELECTIVE_SCANNER_SYS` |
| Rational Bayesian updating   | `LLMBalancedAnalyst` persona: equal weight to all evidence               | `LLM/prompts.py: LLM_BALANCED_ANALYST_SYS`  |
| Contrarian exploitation      | `LLMContrarianTrader` persona: fades biased consensus                    | `LLM/prompts.py: LLM_CONTRARIAN_TRADER_SYS` |
| Noise trader liquidity       | `LLMNoiseTrader` persona: uninformed random-ish trader                   | `LLM/prompts.py: LLM_NOISE_TRADER_SYS`      |
| Price dynamics               | `Market` agent (Rule-based, unchanged)                                   | `Rule/players.py: Market`                   |

---

## 3. Market Mechanism

Identical to Rule variant. Market broadcasts per round:

```python
{
    "price":       float,   # current asset price
    "fundamental": float,   # intrinsic value (100.0)
    "deviation":   float,   # (price - fundamental) / fundamental
    "round":       int,
}
```

LLM agents also receive portfolio state `{cash, position, portfolio_value}`.

---

## 4. Variant-Specific Features

### 4.1 Emergent Bias Without State Variable

In the Rule variant, BeliefAnchor has an explicit `belief` variable.
In the LLM variant, `LLMBeliefAnchor` must reproduce this behavior through
LLM reasoning — looking at recent price history and "feeling" anchored to it.

Key LLM behavior to observe:
- Does LLMBeliefAnchor continue buying even when deviation turns negative?
- Does bias show in the reasoning text (stored in HistoryBuffer records)?

### 4.2 Selective Information Processing

`LLMSelectiveScanner`'s prompt is designed to focus on confirming signals.
However, the LLM has access to the full market state including deviation.
Test: Does LLMSelectiveScanner hold more than it should when market contradicts position?

### 4.3 LLM Decision Loop

```
for each trader agent each round:
    1. Receive market_data {price, fundamental, deviation, round}
    2. Build system_prompt (persona) + user_prompt (market state + portfolio)
    3. Call LangChainAPIInference (3 retry attempts)
    4. Parse JSON response → {action, quantity}
    5. Apply constraints (cash/position limits)
    6. Send order to Market
```

---

## 5. Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                  Market (Rule)                        │
│  P(t+1) = P(t) + λ·D + γ·(F−P) + ε                  │
│  broadcasts: {price, fundamental, deviation, round}   │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────┼────────────────────┐
          │            │                    │
   ┌──────▼──────┐ ┌───▼─────────────┐ ┌───▼──────────────┐
   │LLMBelief    │ │LLMSelective     │ │LLMBalanced       │
   │Anchor       │ │Scanner          │ │Analyst           │
   │(bias persona│ │(selective       │ │(rational         │
   │ anchored)   │ │ confirm persona)│ │ persona)         │
   └─────────────┘ └─────────────────┘ └──────────────────┘
          │
   ┌──────▼──────┐ ┌──────────────┐
   │LLMContrarian│ │LLMNoise      │
   │Trader       │ │Trader        │
   │(fades bias) │ │(random)      │
   └─────────────┘ └──────────────┘
          │  LLM inference → parse JSON → send order → Market
          │
   ┌──────▼──────────────────────────────────────────┐
   │         LangChainAPIInference (shared)           │
   └─────────────────────────────────────────────────┘
```

---

## 6. Configuration Reference

Config: `configs/ConfirmationBias/LLM/simulation.yml`

| Parameter          | Value                   | Description             |
|--------------------|-------------------------|-------------------------|
| `llm.model`        | `gpt-4o-mini` (default) | LLM model name          |
| `llm.temperature`  | 0.3                     | Decision randomness     |
| `llm.max_tokens`   | 512                     | Max response length     |
| `initial_cash`     | 100000                  | Starting cash per agent |
| `initial_position` | 0                       | Starting holdings       |

Market parameters: identical to Rule variant (see Rule/explain.md §6).

---

## 7. Running Instructions

```bash
# Requires LLM API key in .env
python examples/ConfirmationBias/LLM/run_confirmationbias_llm.py \
    -c configs/ConfirmationBias/LLM/simulation.yml

# Analyze results
python examples/ConfirmationBias/LLM/analysis.py \
    -c configs/ConfirmationBias/LLM/simulation.yml
```

---

## 8. Expected Behavior

- `LLMBeliefAnchor` may produce weaker bias than Rule (no compounding belief variable)
- `LLMSelectiveScanner` may ignore disconfirming signals depending on prompt engineering
- `LLMContrarianTrader` likely to perform well (clear instruction to fade bias)
- Stochastic decisions → `bias_amplitude_pct` varies across runs (Monte Carlo opportunity)
- `bias_persistence_rounds` typically shorter than Rule (no locked belief state)

---

## 9. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Confirmation bias theory → `../simulation-bases.md §2, §4 — BeliefAnchor, SelectiveScanner`
- LLM few-shot reasoning → Brown, T. B., et al. (2020). Language models are few-shot learners. *NeurIPS*.
