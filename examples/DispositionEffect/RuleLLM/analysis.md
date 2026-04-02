# DispositionEffect RuleLLM Analysis Methodology

## Overview

This document describes the evaluation metrics for the **hybrid Rule+LLM disposition effect** simulation. The analysis methodology is identical to the rule-based version, as both simulate the same financial phenomenon.

For detailed metric definitions and financial theory, see: **`../DispositionEffect/analysis.md`**

---

## Hybrid Rule+LLM Observable Phenomena

### Emergent Behaviors Unique to Hybrid Agents

| Phenomenon                   | Hybrid Behavior                                            | Contrast with Pure Rule-Based           |
|------------------------------|------------------------------------------------------------|-----------------------------------------|
| **Rule Grounding**           | LLM receives Prospect Theory formulas in prompt            | Rule-based executes thresholds directly |
| **Interpretive Flexibility** | LLM may adjust sell fractions ±20% based on market context | Rule-based applies fixed fractions      |
| **Reasoning Transparency**   | Decision reasoning visible in `<analysis>` tags            | Rule-based has no reasoning trace       |
| **Rule Compliance**          | LLM should follow rule sign (sell/hold/buy)                | Rule-based guaranteed compliance        |

### Expected Differences from Rule-Based

1. **PGR/PLR Ratio**: Similar directional pattern, may show variation in magnitude
2. **Sell Timing**: LLM may delay sells based on qualitative market assessment
3. **Loss Aversion**: May show stronger/weaker loss aversion based on LLM personality
4. **Reference Point Behavior**: LLM "understands" psychological anchoring

---

## Hybrid Agent Design

Each agent's system prompt contains:
- **PERSONA section**: Identity, style, risk attitude, behavioral traits
- **DECISION RULES section**: Explicit quantitative rules from DispositionEffect counterpart

Agent types with their theoretical foundations:
- **RuleLLMDispositionBiased**: Prospect Theory gain/loss asymmetry rules
- **RuleLLMRationalInvestor**: Expected utility rebalancing rules
- **RuleLLMTaxAwareInvestor**: Tax-loss harvesting optimization rules
- **RuleLLMInstitutionalInvestor**: Professional symmetric rules
- **RuleLLMLossAverse**: Extreme loss aversion (λ ≈ 2.25) rules

---

## Key Metrics (Summary)

All metrics from `../DispositionEffect/analysis.md` apply:

| Metric                  | Purpose                                     |
|-------------------------|---------------------------------------------|
| PGR (Proportion Gains)  | Realized gains / (realized + paper gains)   |
| PLR (Proportion Losses) | Realized losses / (realized + paper losses) |
| Disposition Coefficient | DC = PGR - PLR                              |
| Sell Event Distribution | Gain/loss % at each sell event              |

---

## Validation Criteria

| Criterion            | Target                         | Source                        |
|----------------------|--------------------------------|-------------------------------|
| **PGR > PLR**        | Required for DispositionBiased | DispositionEffect/analysis.md |
| **DC = PGR - PLR**   | > 0.10 for DispositionBiased   | DispositionEffect/analysis.md |
| **Sell cluster >0%** | Median sell in gain domain     | DispositionEffect/analysis.md |

---

## Using Centralized Evaluation Module

```python
from masim.evaluation.finance import (
    calculate_pgr_plr,
    calculate_disposition_coefficient,
    plot_disposition_analysis,
)

# Same analysis as rule-based version
trades = {...}  # Load from simulation records
pgr, plr = calculate_pgr_plr(trades)
dc = calculate_disposition_coefficient(pgr, plr)
```

---

## References

See `../DispositionEffect/analysis.md` for complete academic references including:
- Kahneman & Tversky (1979) Prospect Theory
- Shefrin & Statman (1985) Disposition Effect
- Odean (1998) PGR/PLR Methodology
