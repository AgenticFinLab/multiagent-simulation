# ArchegosCollapse Rule — Analysis Documentation

## §1 Analysis Objectives

| Item                                | Description                                                                                                                                    |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| **Implements**                      | `../analysis-bases.md`                                                                                                                         |
| **Analysis Script**                 | `analysis.py` in this directory                                                                                                                |
| **Output Location**                 | `EXPERIMENT/ArchegosCollapse/Rule/records/analysis/`                                                                                           |
| **Variant-Specific Considerations** | Deterministic baseline (only stochasticity from `InformationTrader` detection probability); provides ground truth for cross-variant comparison |

---

## §2 Metric → Function Mapping

All metrics are defined in `../analysis-bases.md §2`. The Rule variant's `analysis.py` is the authoritative implementation — all other variants import from it.

| Metric                     | Function              | analysis-bases.md Ref | Rule-Specific Notes                                                            |
|----------------------------|-----------------------|-----------------------|--------------------------------------------------------------------------------|
| **Price Deviation**        | `calculate_metrics()` | `analysis-bases.md §2.1` | Deterministic cascade; deviation follows predictable plunge-then-recovery      |
| **Maximum Drawdown**       | `calculate_metrics()` | `analysis-bases.md §2.2` | Calibration target 20–50%; Rule shows cleanest drawdown matching cascade rules |
| **Cascade Volatility**     | `calculate_metrics()` | `analysis-bases.md §2.3` | Rolling std of returns; expect 2%–8% per round during cascade phase            |
| **Return Autocorrelation** | `calculate_metrics()` | `analysis-bases.md §2.4` | AC1 > 0 during cascade (self-reinforcing); AC1 < 0 during recovery             |
| **Agent-Type Volume**      | `calculate_metrics()` | `analysis-bases.md §2.5` | PrimeBroker1 sells earlier/higher prices than PrimeBroker2; verifiable         |
| **Cascade Onset Round**    | `calculate_metrics()` | `analysis-bases.md §2.6` | First round `deviation < -0.10`; Rule: expected rounds 10–30                   |
| **Recovery Half-Life**     | `calculate_metrics()` | `analysis-bases.md §2.7` | Recovery after trough; validates BlockTradeBuyer and mean-reversion dynamics   |

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Cascade Dynamics
*(Objective from analysis-bases.md §3.1)*

**Implementation in analysis.py:**
- Function: `load_simulation_data()` → loads price and fundamental arrays from `records/market/*.json`
- Input data: `EXPERIMENT/ArchegosCollapse/Rule/records/market/price/` (HistoryBuffer JSON)
- Computation: `deviation = (prices − fundamentals) / fundamentals × 100`
- Output: `01_archegoscollapse_dynamics.png` (price vs fundamental and deviation)

**Variant-Specific Interpretation:**
Rule variant shows a clean, threshold-triggered plunge followed by gradual recovery. The cascade onset round is deterministic (modulo `InformationTrader` detection randomness). If deviation never crosses −10%, check `margin_threshold` and `liquidation_threshold` parameters.

---

### Dimension 2: Agent Behavior Analysis
*(Objective from analysis-bases.md §3.2)*

**Implementation in analysis.py:**
- Function: `calculate_metrics()` → computes volumes from order records per agent
- Input data: `EXPERIMENT/ArchegosCollapse/Rule/records/{agent_id}/` order histories
- Computation: sum of `|quantity|` per agent type across all rounds
- Output: subplot 3 (Returns), subplot 4 (Return distribution); `metrics.json`

**Variant-Specific Interpretation:**
In Rule variant, PrimeBroker1 sells at higher prices than PrimeBroker2 (provable from round-over-round records). BlockTradeBuyer's activation is exact — always starts at the round where `deviation < -0.10`. InformationTrader activity is variable (probabilistic detection).

---

### Dimension 3: Cascade Intensity and Lifecycle
*(Objective from analysis-bases.md §3.3)*

**Implementation in analysis.py:**
- Function: `calculate_metrics()` → `returns = np.diff(prices) / prices[:-1]`
- Computation: rolling std window=10; lag-1 autocorrelation of returns
- Output: Return time series plot; return distribution histogram

**Variant-Specific Interpretation:**
Rule variant shows sharp negative returns during cascade onset (rounds 10–20), then gradual positive returns during recovery. Return distribution should show negative skew (large left tail from cascade). Max drawdown: expected 20%–50% consistent with Archegos stylized facts.

---

### Dimension 4: Cross-Variant Comparison
*(Objective from analysis-bases.md §3.4)*

**Rule's position in cross-variant comparison:**
Rule is the deterministic reference. All other variants are evaluated relative to Rule:
- Cascade onset round: Rule is the baseline timing
- Max drawdown depth: Rule shows calibrated, consistent depth
- Recovery speed: Rule recovery driven purely by mean reversion (no LLM hesitation)

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                       | Description                                                               | How to Observe                                   | Contrast with LLM/RuleLLM                  |
|----------------------------------|---------------------------------------------------------------------------|--------------------------------------------------|--------------------------------------------|
| **Clean Threshold Activation**   | PrimeBroker1 sells exactly at deviation = −0.10 round                     | Order records: first PrimeBroker1 sell round     | LLM: sells earlier or later due to persona |
| **Deterministic Cascade Shape**  | Price drop follows same curve in each run (given same initial conditions) | Price vs fundamental chart overlay across runs   | LLM: variable cascade shape across runs    |
| **First-Mover Price Advantage**  | PrimeBroker1 avg sell price > PrimeBroker2 avg sell price                 | Per-agent effective price in order records       | Both Rule and LLM should show this pattern |
| **BlockTradeBuyer Floor Effect** | Price reversal visible exactly at BlockTradeBuyer activation round        | Returns turn positive; Block buyer volume spikes | LLM: floor timing more variable            |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds   | Expected Observable                                                                       |
|----------------|-------------------------------------------------------------------------------------------|
| **50 rounds**  | Cascade occurs and bottoms; partial recovery visible; max drawdown observable             |
| **100 rounds** | Full cascade lifecycle: onset → trough → partial recovery; BlockTradeBuyer effect visible |
| **200 rounds** | Near-full price recovery to fundamental; mean reversion completes                         |

### Agent Count Scaling

| Agent Count            | Expected Observable                                             |
|------------------------|-----------------------------------------------------------------|
| **3–5 total**          | Insufficient destabilizing pressure; cascade may not develop    |
| **5 agents (default)** | Calibrated — clean cascade; PrimeBroker1/2 asymmetry observable |
| **10+ agents**         | Amplified cascade; deeper drawdown; recovery slower             |

### Parameter Sensitivity

| Parameter               | Change              | Expected Effect on Analysis                                          |
|-------------------------|---------------------|----------------------------------------------------------------------|
| `price_impact` (λ)      | 0.03 → 0.06         | Deeper cascade; higher drawdown; faster cascade onset                |
| `margin_threshold`      | −0.15 → −0.10       | Earlier ConcentratedFund sell; cascade starts sooner                 |
| `liquidation_threshold` | −0.10 → −0.15 (PB1) | PrimeBroker1 delays; first-mover advantage weakens                   |
| `mean_reversion` (γ)    | 0.01 → 0.03         | Faster recovery; shorter cascade duration                            |
| `discount_threshold`    | −0.10 → −0.20       | BlockTradeBuyer activates later; deeper trough before floor kicks in |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/ArchegosCollapse/Rule/records/analysis/`.

| Output File                      | Generated By              | Contents                                           | Interpretation                                  |
|----------------------------------|---------------------------|----------------------------------------------------|-------------------------------------------------|
| `summary.json` | `analyze_archegos_collapse()` | Metrics, validation score, criteria, and interpretation | Machine-readable cross-variant comparison input |
| `00_investor_bids.png` | `_create_visualizations()` | Market price and investor bid curves | Headline order-path visualization |
| `01_archegoscollapse_dynamics.png` | `_create_visualizations()` | Price, fundamental value, and deviation | Cascade path verification |
| `02_archegoscollapse_analysis.png` | `_create_visualizations()` | Rolling volatility and autocorrelation | Self-reinforcement analysis |
| `03_summary.png` | `_create_visualizations()` | Agent VWAP and volume summary | First-mover advantage and participation check |

---

## §7 Cross-Variant Comparison Notes

This variant is the **ground truth baseline** for all cross-variant comparisons.

- **Phenomenon emergence speed**: Rule shows fastest, most predictable cascade (rules trigger immediately at threshold)
- **Phenomenon intensity**: Max drawdown in Rule is the calibration target; all other variants compared against this
- **Behavioral realism**: Rule is least realistic (no psychology, no knowledge) but most interpretable and reproducible
- **Decision quality**: BlockTradeBuyer achieves best buying price because it activates precisely at discount threshold

Cross-variant comparison protocol: `../analysis-bases.md §5`.

---

### References

- `../analysis-bases.md` — master analysis specification (metrics, dimensions, validation targets)
- `../simulation-bases.md §3.1` — price formula implementation
- `../simulation-bases.md §4` — all investor type specs and rule-based behavior
- `../simulation-bases.md §6` — parameter calibration table with source citations
