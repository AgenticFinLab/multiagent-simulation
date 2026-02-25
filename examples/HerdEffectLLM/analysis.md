# HerdEffectLLM Analysis - Metrics Documentation

## Overview

This document describes all analysis metrics used to detect and measure **emergent herding behavior** in the HerdEffectLLM simulation. This extends the base HerdEffect metrics with **LLM-specific interpretability analysis**.

---

## Metrics Categories

| Category          | Metrics                                                      | Purpose                             |
|-------------------|--------------------------------------------------------------|-------------------------------------|
| **Numerical**     | CV, DA, ICM, CSSD, PD, Volatility, AC                        | Same as HerdEffect                  |
| **Text Analysis** | Keyword Distribution, Reasoning Chain, Action Classification | LLM interpretability                |
| **Behavioral**    | Per-Round Consensus, Reasoning Convergence                   | Emergent herding from LLM reasoning |

---

## Part 1: Numerical Metrics (Imported from HerdEffect)

All numerical metrics are identical to HerdEffect. See [HerdEffect/analysis.md](../HerdEffect/analysis.md) for detailed definitions:

| Metric                     | Formula              | Herding Threshold          |
|----------------------------|----------------------|----------------------------|
| Bid Convergence (CV)       | σ(bids) / μ(bids)    | CV < 0.05 = Strong Herding |
| Directional Agreement (DA) | \|Σ sign(ΔBid)\| / N | DA > 0.8 = Strong Herding  |
| Information Cascade (ICM)  | contrarian_ratio     | ICM > 0.6 = Strong Cascade |
| Cross-Sectional Std (CSSD) | σ(bids)              | Lower = More Herding       |
| Price Deviation (PD)       | (P - F) / F          | PD > 20% = Bubble          |
| Rolling Volatility         | σ(P[-w:])            | Spike = Market Stress      |
| Autocorrelation (AC)       | corr(r_t, r_{t-lag}) | AC > 0.3 = Momentum        |
| Bubble Magnitude           | Σ(P - F)             | Rise-Peak-Fall Pattern     |

---

## Part 2: LLM Text Analysis Metrics (NEW)

### 2.1 Reasoning Keyword Distribution

**Definition**: Count of category-specific keywords in LLM reasoning text.

```python
Categories:
- buy_keywords: ["buy", "bullish", "uptrend", "rising", "momentum", "opportunity", "long"]
- sell_keywords: ["sell", "bearish", "downtrend", "falling", "decline", "exit", "short"]
- trend_keywords: ["trend", "momentum", "pattern", "signal", "continuation", "accelerat"]
- value_keywords: ["fundamental", "overvalued", "undervalued", "fair value", "intrinsic"]
- risk_keywords: ["risk", "volatil", "uncertain", "caution", "protect", "safe"]
```

**Purpose**: Verify LLM investors are reasoning according to their defined personalities.

**Expected Results by Investor Type**:

| Investor Type         | Expected Dominant Keywords                |
|-----------------------|-------------------------------------------|
| LLMMomentumInvestor   | trend_keywords, buy_keywords (in uptrend) |
| LLMContrarianInvestor | value_keywords                            |
| LLMRiskAverseInvestor | risk_keywords                             |
| LLMAggressiveInvestor | trend_keywords, buy_keywords (amplified)  |
| LLMNoiseTrader        | Mixed, no clear pattern                   |

**Success Criteria**: Keyword distribution matches investor personality defined by system prompt.

---

### 2.2 Reasoning Action Classification

**Definition**: Classify each LLM reasoning into BUY/SELL/HOLD based on text content.

```python
def classify_reasoning_action(reasoning: str) -> str:
    buy_signals = ["buy", "long", "bullish", "rising", "uptrend", "opportunity"]
    sell_signals = ["sell", "short", "bearish", "falling", "downtrend", "exit"]
    hold_signals = ["hold", "wait", "observe", "uncertain", "no action"]
    
    # Count matches and return dominant action
```

**Purpose**: Verify LLM reasoning aligns with actual trading action.

**Success Criteria**: Reasoning classification matches actual quantity sign (>0 = BUY, <0 = SELL).

---

### 2.3 Per-Round Behavioral Consensus

**Definition**: Percentage of investors taking the same action each round.

```
Consensus_t = max(BUY_count, SELL_count, HOLD_count) / N
```

**Interpretation**:
| Consensus | Interpretation                                                |
|-----------|---------------------------------------------------------------|
| > 80%     | **Herding** - LLMs independently reasoning to same conclusion |
| 60-80%    | Moderate alignment                                            |
| < 60%     | Diverse behavior                                              |

**Success Criteria**: Consensus rises during herding phases.

---

### 2.4 Reasoning Convergence Index

**Definition**: Semantic similarity of LLM reasoning texts across investors.

```
Analysis method:
1. Extract key reasoning phrases from each investor
2. Count common keywords/themes
3. Higher commonality = reasoning convergence
```

**Purpose**: Detect if LLMs are "thinking alike" despite different prompts.

**Success Criteria**: Reasoning convergence increases during herding (independent LLMs arrive at similar conclusions).

---

## Part 3: Success Criteria for LLM Emergent Herding

The simulation successfully demonstrates **emergent herding from LLM reasoning** if:

### Numerical Criteria (Same as HerdEffect)

| Criterion             | Target                           |
|-----------------------|----------------------------------|
| Bid CV                | < 0.10 for ≥3 consecutive rounds |
| Directional Agreement | > 0.8 for ≥3 rounds              |
| Information Cascade   | > 0.5 during bubble              |
| Price Deviation       | Peak > 15%                       |

### LLM-Specific Criteria (NEW)

| Criterion                        | Target                                                 | Evidence                                    |
|----------------------------------|--------------------------------------------------------|---------------------------------------------|
| **Keyword Alignment**            | Each investor type shows expected keyword distribution | LLMs following their system prompts         |
| **Reasoning-Action Consistency** | > 90% match                                            | LLMs acting on their reasoning              |
| **Behavioral Consensus**         | > 80% for ≥3 rounds                                    | LLMs converging independently               |
| **Reasoning Convergence**        | Increasing during bubble                               | Similar reasoning despite different prompts |

### Key Research Question

> **Can LLMs, with different personality prompts, independently reason their way into herd behavior without explicit imitation?**

**Evidence for "Yes"**:
1. Different system prompts → Different reasoning keywords
2. But same market data → Converging actions
3. Behavioral consensus rises during bubble
4. No explicit "follow the crowd" instruction, yet crowd behavior emerges

---

## Running Analysis

```bash
# Set API key
export ARK_API_KEY='your-bytedance-doubao-api-key'

# Run simulation
python examples/HerdEffectLLM/run_herd_llm.py -c configs/HerdEffectLLM/simulation.yml

# Run analysis (generates both charts and text report)
python examples/HerdEffectLLM/analysis.py -c configs/HerdEffectLLM/simulation.yml
```

## Output Files

### Numerical Charts (Same as HerdEffect)

| File                           | Description                      |
|--------------------------------|----------------------------------|
| `00_summary_panel.png`         | 6-panel comprehensive summary    |
| `01_price_chart.png`           | Market price & LLM investor bids |
| `02_quantity_chart.png`        | Trading quantities               |
| `03_bid_convergence.png`       | **KEY**: Bid CV                  |
| `04_directional_agreement.png` | **KEY**: Behavioral alignment    |

### LLM-Specific Outputs (NEW)

| File                        | Description                            |
|-----------------------------|----------------------------------------|
| `05_reasoning_keywords.png` | Keyword distribution per investor type |
| `text_analysis.md`          | **Complete interpretability report**   |

### Text Analysis Report Structure

```markdown
# text_analysis.md

## Per-Round Interpretability Report
- Round N market state
- Table of all LLM decisions with full reasoning
- Behavioral summary (BUY/SELL/HOLD counts)
- Herding detection alerts

## Reasoning Chain Analysis
- Each investor's reasoning evolution across rounds
- Action + bid + quantity + reasoning per round

## Emergent Herding Interpretation
- Numerical herding indicators
- Keyword analysis summary
- Behavioral pattern interpretation
- Conclusion: strength of emergent herding
```

---

## Expected LLM Behavior Patterns

### Phase 1: Initial (Rounds 1-3)

```
Market: Price ≈ 100, low volume
LLM Behavior:
- LLMMomentum: "No clear trend, holding"
- LLMContrarian: "Price near fundamental, holding"
- LLMRiskAverse: "Low volatility, cautious buy"
- LLMAggressive: "Waiting for acceleration signal"
- LLMNoise: Random activity

Metrics:
- CV: 0.15-0.20 (dispersed)
- DA: 0.4-0.6 (random)
- Consensus: < 60%
```

### Phase 2: Trigger (Rounds 4-6)

```
Market: NoiseTrader causes small price increase
LLM Behavior:
- LLMMomentum: "Detecting positive trend, buying" ← KEY
- Others: Mixed responses

Metrics:
- CV: Starting to decrease
- DA: Starting to increase
- Consensus: 50-70%
```

### Phase 3: Cascade (Rounds 7-8)

```
Market: Price rising, volume increasing
LLM Behavior:
- LLMMomentum: "Strong uptrend, buying more"
- LLMAggressive: "Acceleration detected, heavy buy" ← KEY
- LLMContrarian: "Overvalued but trend too strong"
- LLMRiskAverse: "Volatility rising, cautious"
- LLMNoise: Following trend (by chance)

Metrics:
- CV: < 0.10 (converging)
- DA: > 0.8 (aligning)
- ICM: > 0.5 (cascade)
- Consensus: > 80%
```

### Phase 4: Peak (Rounds 9-10)

```
Market: Price peaks, maximum bubble
LLM Behavior:
- ALL LLMs reasoning into similar BUY decisions
- Even LLMContrarian overwhelmed by trend

Metrics:
- CV: < 0.05 (highly converged)
- DA: > 0.9 (extreme alignment)
- **HERDING DETECTED**
```

---

## Comparison: HerdEffect vs HerdEffectLLM

| Aspect             | HerdEffect           | HerdEffectLLM             |
|--------------------|----------------------|---------------------------|
| Decision Mechanism | Fixed formulas       | LLM reasoning             |
| Reproducibility    | Deterministic        | Stochastic                |
| Interpretability   | Numbers only         | Full reasoning text       |
| Herding Evidence   | Numerical metrics    | Numerical + text patterns |
| Research Value     | Mechanism validation | LLM behavioral finance    |

---

## Research Questions Answered

| Question                               | How to Verify         | Success Indicator                |
|----------------------------------------|-----------------------|----------------------------------|
| Do LLMs follow their prompts?          | Keyword distribution  | Keywords match investor type     |
| Is LLM reasoning consistent?           | Action classification | Reasoning matches action > 90%   |
| Does herding emerge without imitation? | DA + CV + consensus   | All metrics show convergence     |
| Can we trace herding formation?        | Per-round reasoning   | Clear reasoning chain to herding |

---

## References

### Numerical Metrics
See [HerdEffect/analysis.md](../HerdEffect/analysis.md) for full academic references.

### LLM Behavioral Finance (Emerging Field)

1. This simulation contributes to the emerging field of **LLM-based behavioral finance**:
   - Can LLMs simulate realistic investor psychology?
   - Do LLM agents exhibit emergent collective behavior?
   - How interpretable is LLM decision-making in financial contexts?

2. Related work in LLM agent simulation:
   - Park, J.S., et al. (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. arXiv:2304.03442
   - Multi-agent LLM simulations for social/economic phenomena
