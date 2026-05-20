# ArchegosCollapse LLM — Analysis Documentation

## §1 Analysis Objectives

| Item                                | Description                                                                                                                                       |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                            |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                   |
| **Output Location**                 | `EXPERIMENT/ArchegosCollapse/LLM/records/analysis/`                                                                                               |
| **Variant-Specific Considerations** | Stochastic LLM decisions — cascade timing and depth vary across runs; key question is whether LLM personas reproduce denial-then-panic psychology |

---

## §2 Metric → Function Mapping

All metrics are defined in `../analysis-bases.md §2`. LLM `analysis.py` imports core functions from `Rule/analysis.py` (DRY pattern) and adds LLM-specific visualization title.

```python
from examples.ArchegosCollapse.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
)
```

| Metric                     | Function              | analysis-bases.md Ref | LLM-Specific Notes                                                                |
|----------------------------|-----------------------|-----------------------|-----------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()` | `analysis-bases.md §2.1` | Higher variance than Rule; denial phase may delay or flatten cascade onset        |
| **Maximum Drawdown**       | `calculate_metrics()` | `analysis-bases.md §2.2` | More variable across runs; deeper if denial extends selling pressure              |
| **Cascade Volatility**     | `calculate_metrics()` | `analysis-bases.md §2.3` | Expect higher volatility than Rule due to LLM decision unpredictability           |
| **Return Autocorrelation** | `calculate_metrics()` | `analysis-bases.md §2.4` | May show weaker AC1 pattern if LLM decisions disrupt cascade self-reinforcement   |
| **Agent-Type Volume**      | `calculate_metrics()` | `analysis-bases.md §2.5` | ConcentratedFund may hold longer (denial) before large block sell                 |
| **Cascade Onset Round**    | `calculate_metrics()` | `analysis-bases.md §2.6` | Highly variable across runs (LLM denial psychology); compare distribution to Rule |
| **Recovery Half-Life**     | `calculate_metrics()` | `analysis-bases.md §2.7` | Recovery timing may vary with LLM hesitation and opportunistic-buy timing         |

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Cascade Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Functions: `load_simulation_data()` + `calculate_metrics()` (imported from Rule)
- Input data: `EXPERIMENT/ArchegosCollapse/LLM/records/market/price/`
- Output: `archegsoscollapse_llm_analysis.png` — 4-panel with LLM-specific title and orange return color

**Variant-Specific Interpretation:**
LLM variant may show a delayed cascade onset (denial phase in ConcentratedFund) or a compressed one-round panic sell (if LLM suddenly "capitulates"). Both patterns are valid LLM behaviors. Expect cascade onset to be 5–15 rounds later than Rule baseline on average.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Functions: `calculate_metrics()` (from Rule) applied to LLM output records
- Input data: `EXPERIMENT/ArchegosCollapse/LLM/records/{agent_id}/` order histories
- Output: `summary.json` with `{"variant": "LLM", ...metrics}`

**Variant-Specific Interpretation:**
Key LLM-specific observable: ConcentratedFund reasoning logs (in `records/`) should show explicit denial language before the eventual sell. PrimeBroker1 may show "competitive urgency" in reasoning. These qualitative LLM reasoning patterns are as important as the quantitative outcomes.

---

### Dimension 3: Cascade Intensity and Lifecycle
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Computation: `returns = np.diff(prices) / prices[:-1]`; rolling std; autocorrelation of returns
- Output: subplot 3 (returns with orange color for LLM variant), subplot 4 (return distribution)

**Variant-Specific Interpretation:**
LLM return distribution should show fatter tails than Rule (due to sudden large sell events from panic) and longer left tail (denial extends holding, then sudden capitulation creates larger price drops). Rolling volatility should spike sharply at cascade onset.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

**LLM's position in cross-variant comparison:**
- Cascade onset speed: LLM onset typically later than Rule (denial phase); occasionally earlier (panic onset)
- Cascade depth: Variable across runs; may be deeper when denial amplifies eventual panic
- Behavioral realism: Highest among all variants if LLM correctly reproduces denial-then-panic
- Decision quality: ConcentratedFund may perform worse than Rule (held too long before forced sell)

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                 | Description                                                       | How to Observe                                       | Contrast with Rule Baseline            |
|----------------------------|-------------------------------------------------------------------|------------------------------------------------------|----------------------------------------|
| **Denial Phase**           | ConcentratedFund "holds" for several rounds when Rule would sell  | ConcentratedFund order history: holds past −15%      | Rule: sells immediately at −15%        |
| **Panic Capitulation**     | Large single-round sell after denial ends                         | ConcentratedFund volume spike; returns histogram     | Rule: gradual threshold-triggered sell |
| **Reasoning Variability**  | PrimeBroker decisions explain different urgency levels each run   | LLM reasoning logs in `records/`                     | Rule: no reasoning, just threshold     |
| **Variable Cascade Onset** | Cascade timing differs across runs; std of onset round > 5 rounds | Run 10 simulations; compute onset round distribution | Rule: same onset round every run       |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                                |
|----------------|------------------------------------------------------------------------------------|
| **50 rounds**  | Cascade may still be in denial/onset phase; insufficient for full lifecycle        |
| **100 rounds** | Most runs complete cascade lifecycle; denial + panic visible                       |
| **200 rounds** | All runs complete recovery; statistical analysis of onset round distribution valid |

### Agent Count Scaling

| Agent Count            | Expected Observable                                                  |
|------------------------|----------------------------------------------------------------------|
| **5 agents (default)** | Balanced LLM personas; denial + competition dynamics both observable |
| **10+ agents**         | More LLM calls per round; higher API cost; more variable outcomes    |

### Parameter Sensitivity

| Parameter      | Change      | Expected Effect on LLM Analysis                                |
|----------------|-------------|----------------------------------------------------------------|
| `temperature`  | 0.7 → 0.9   | Higher randomness; more denial variance; more extreme cascades |
| `temperature`  | 0.7 → 0.3   | More deterministic LLM; closer to Rule timing                  |
| `price_impact` | 0.03 → 0.05 | Same as Rule: deeper cascade; LLM panic more extreme           |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/ArchegosCollapse/LLM/records/analysis/`.

| Output File                          | Generated By | Contents                                                           | Interpretation                    |
|--------------------------------------|--------------|--------------------------------------------------------------------|-----------------------------------|
| `archegsoscollapse_llm_analysis.png` | `main()`     | 4-panel: Price, Deviation, Returns (orange), Distribution          | LLM variant cascade visualization |
| `summary.json`                       | `main()`     | `{"variant": "LLM", price_metrics, deviation_metrics, volatility}` | Cross-variant comparison input    |

---

## §7 Cross-Variant Comparison Notes

- **Phenomenon emergence speed**: LLM onset typically later than Rule (denial phase); occasionally earlier (LLM acts before threshold in panic)
- **Phenomenon intensity**: Potentially deeper than Rule when denial extends — eventual panic sell amplifies cascade
- **Behavioral realism**: Highest — LLM denial-then-panic reproduces actual Archegos psychological dynamics
- **Decision quality**: ConcentratedFund performs worst (held too long); BlockTradeBuyer may perform best (buys at deepest discount if cascade is deeper)

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

### References

- `../analysis-bases.md` — master analysis specification
- `../simulation-bases.md §4 LLM Persona` — denial/panic psychology for each investor type
- `../simulation-bases.md §9` — LLM variant expected behaviors in variant comparison
- `Rule/analysis.py` — imported metric functions (`calculate_metrics`, `load_simulation_data`)
