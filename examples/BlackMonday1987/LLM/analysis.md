# BlackMonday1987 LLM — Analysis Documentation

## Overview

| Item                                | Description                                                                                                                                                        |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                                             |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                                    |
| **Output Location**                 | `EXPERIMENT/BlackMonday1987/LLM/records/analysis/`                                                                                                                 |
| **Variant-Specific Considerations** | Stochastic LLM decisions — key question is whether LLM "mechanical" personas maintain automated strategy discipline or introduce hesitation that dampens the crash |

---

## 1. Metric Implementation

LLM `analysis.py` imports core functions from `Rule/analysis.py` (DRY pattern):

```python
from examples.BlackMonday1987.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
```

| Metric                     | Function              | analysis-bases.md Ref | LLM-Specific Notes                                                                       |
|----------------------------|-----------------------|-----------------------|------------------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()` | `§2.1`                | Higher variance than Rule; depends on whether LLM maintains mechanical discipline        |
| **Maximum Drawdown**       | `calculate_metrics()` | `§2.2`                | Variable; LLM hesitation may reduce crash depth                                          |
| **Crash Velocity**         | `calculate_metrics()` | `§2.3`                | May be lower than Rule if ProgramTrader LLM doesn't amplify mechanically                 |
| **Return Autocorrelation** | `calculate_metrics()` | `§2.4`                | May show weaker positive AC1 if LLM disrupts feedback self-reinforcement                 |
| **Agent-Type Volume**      | `calculate_metrics()` | `§2.5`                | PortfolioInsurer LLM may sell less than Rule formula; ProgramTrader may be more variable |
| **Crash Onset Round**      | `calculate_metrics()` | `§2.6`                | Variable across runs; LLM may delay or accelerate initial trigger                        |

---

## 2. Dimension-by-Dimension Analysis

### Dimension 1: Price Crash Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Functions: imported from Rule; LLM-specific title in visualization
- Output: `blackmonday1987_llm_analysis.png` — LLM-titled 4-panel chart

**Variant-Specific Interpretation:**
Critical test: does LLM PortfolioInsurer sell systematically (like Rule), or introduce judgment-based hesitation? If crash depth < Rule by >30%, LLM personas are not faithfully reproducing automated strategy mechanics.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Variant-Specific Interpretation:**
ProgramTrader's LLM reasoning logs should show "algorithm fires" language without emotional override. If logs show "I'm concerned about systemic impact," the LLM is departing from the mechanical trading persona — scientifically interesting but means smaller crash.

---

### Dimension 3: Feedback Loop Intensity
*(Objective from analysis-bases.md §3.3)*

**Variant-Specific Interpretation:**
LLM feedback loop may be weaker than Rule if agents exercise judgment. Return distribution should still show left tail, but may be less extreme than Rule baseline.

---

### Dimension 4: Cross-Variant Comparison

- Crash onset: LLM may be later (hesitation) or earlier (panic amplification)
- Crash depth: Lower than Rule if LLM introduces caution; higher if LLM amplifies with additional justification

---

## 3. Variant-Specific Observable Phenomena

| Phenomenon                        | Description                                                               | How to Observe                            | Contrast with Rule       |
|-----------------------------------|---------------------------------------------------------------------------|-------------------------------------------|--------------------------|
| **Mechanical vs Reflective Sell** | LLM may add "I note this could worsen the situation" in reasoning         | ProgramTrader reasoning logs              | Rule: no reasoning       |
| **Hesitation Phase**              | PortfolioInsurer may "hold" a round before selling per protection mandate | Order records: holds when Rule would sell | Rule: sells immediately  |
| **Run-to-Run Crash Variability**  | Same parameters produce different crash depths                            | Multiple run comparison                   | Rule: identical each run |

---

## 4. Output Files Reference

All outputs written to `EXPERIMENT/BlackMonday1987/LLM/records/analysis/`.

| Output File                        | Generated By | Contents                                               | Interpretation                 |
|------------------------------------|--------------|--------------------------------------------------------|--------------------------------|
| `blackmonday1987_llm_analysis.png` | `main()`     | 4-panel LLM-titled crash visualization                 | LLM variant crash dynamics     |
| `summary.json`                     | `main()`     | `{"variant": "LLM", price_metrics, deviation_metrics}` | Cross-variant comparison input |

---

## 5. Cross-Variant Comparison Notes

- **Crash emergence speed**: LLM typically later (hesitation) or comparable (if mechanical personas hold)
- **Crash intensity**: Lower than Rule if LLM introduces judgment; variable
- **Behavioral realism**: Depends on LLM's ability to maintain mechanical discipline without explicit rules
- **Decision quality**: Ambiguous — less crash depth is "better" for ValueInvestor but means LLM failed to reproduce 1987 mechanical dynamics

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

## References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §4 LLM Persona` — mechanical strategy personas
- `Rule/analysis.py` — imported metric functions
