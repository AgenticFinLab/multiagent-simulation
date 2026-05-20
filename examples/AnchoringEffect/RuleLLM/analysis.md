# AnchoringEffect RuleLLM — Analysis Documentation

## §1 Overview

| Item                            | Description                                                                                                                                           |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Implements                      | `../analysis-bases.md`                                                                                                                                |
| Analysis Script                 | `analysis.py` in this directory                                                                                                                       |
| Output Location                 | `EXPERIMENT/AnchoringEffect/RuleLLM/analysis/`                                                                                                        |
| Variant-Specific Considerations | Embedded DECISION RULES serve as deeper investor characterization — the LLM uses them as guidance alongside its persona to make intelligent decisions |

---

## §2 Metric Implementation

All 8 metrics are defined in `analysis-bases.md §2`. Below: how each is implemented in the RuleLLM variant.

### Metric: Price Deviation

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_price_deviation()`
- Data source: `EXPERIMENT/AnchoringEffect/RuleLLM/records/market/price/*.json`
- Variant-specific notes: Price path should be very close to Rule baseline (anchoring dynamics preserved by embedded DECISION RULES). Small deviations from Rule are attributable to LLM ±20% quantity adjustments.
- Expected range for this variant: MAD [3%, 11%] — narrow overlap with Rule [3%, 10%]

### Metric: Mean Absolute Deviation (MAD)

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_mean_abs_deviation()`
- Data source: market price records + fundamental value from config
- Variant-specific notes: Expected to be within 1–2 percentage points of Rule MAD in most runs. Validation criterion: if RuleLLM MAD differs from Rule by >5 percentage points, check rule adherence rate.
- Expected range for this variant: [2.5%, 12%]

### Metric: Anchoring Persistence (Half-Life)

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_anchoring_persistence()`
- Data source: deviation time series
- Variant-specific notes: Half-life should be close to Rule variant. LLM quantity adjustments (±20%) can modestly extend or shorten the half-life by altering cumulative anchoring demand. Large deviations from Rule half-life indicate rule override events.
- Expected range for this variant: [18, 65] rounds — slight expansion of Rule [20, 60]

### Metric: Rolling Volatility

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_rolling_volatility()`
- Data source: price return series
- Variant-specific notes: Expect slightly higher volatility than Rule when LLM adjusts quantity upward (+20%), and slightly lower when it adjusts downward (−20%). Volatility spikes may coincide with rule override events.
- Expected range for this variant: [0.5%, 2.2%] per round

### Metric: Return Autocorrelation

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_autocorrelation()`
- Data source: price return series
- Variant-specific notes: Autocorrelation pattern should mirror Rule variant closely. Rule override events may slightly reduce autocorrelation by injecting uncorrelated price moves.
- Expected range for this variant: lag-1 AC in [0.05, 0.25]

### Metric: Max Drawdown

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_max_drawdown()`
- Data source: cumulative price series
- Variant-specific notes: Similar to Rule; LLM sell-side quantity amplification (+20%) may deepen occasional drawdown events. If max drawdown significantly exceeds Rule, check for rule override concentrated in sell direction.
- Expected range for this variant: [4%, 21%]

### Metric: Agent-Type Trading Volume

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_agent_volumes()`
- Data source: `EXPERIMENT/AnchoringEffect/RuleLLM/records/{agent_id}/*.json`
- Variant-specific notes: Total volume per agent type should be within ±20% of Rule baseline (reflecting the allowed quantity adjustment). Larger departures indicate rule override events affecting quantity scale.
- Expected range for this variant: ±20% of Rule baseline volumes

### Metric: Anchoring Bias Magnitude

- Defined in: `analysis-bases.md §2`
- Implemented in: `analysis.py → calculate_anchoring_bias_magnitude()`
- Data source: LLM agent records (price, perceived_target derived from reasoning, bid_price)
- Variant-specific notes: Anchoring bias should be close to Rule since DECISION RULES embed the exact `adjustment_factor = 0.3` formula. If LLM's stated reasoning shows different adjustment factors, this indicates prompt-rule drift.
- Expected range for this variant: [0.1, 0.55] — similar to Rule [0.1, 0.6]

---

## §3 Dimension-by-Dimension Analysis

### Dimension 1: Price Dynamics Analysis

Objective (from analysis-bases.md): Measure how anchoring-induced demand creates and sustains price deviations from fundamental value.

Implementation in analysis.py:
- Function: `analyze_price_dynamics()`
- Input data: market price records, fundamental value from config
- Computation: deviation series, MAD, half-life, rolling volatility; overlay Rule baseline for direct comparison
- Output: `price_dynamics.png`, contribution to `summary.json`

Variant-Specific Interpretation:
- The primary question: do embedded DECISION RULES successfully reproduce Rule-variant price dynamics?
- Success: RuleLLM price path visually overlaps Rule price path; MAD within 2 percentage points.
- Failure mode: price path drifts significantly from Rule → review embedded DECISION RULES clarity and LLM reasoning traces.

Expected Output Sample:
```
Price chart overlaying RuleLLM (colored) and Rule (dashed grey) paths.
Expected: near-overlap with occasional small divergences; deviation path similar shape.
```

---

### Dimension 2: Rule-Adherence Analysis (RuleLLM-Specific)

Objective: Measure directional alignment between LLM decisions and Rule-variant decisions at each round. Target: ≥80% directional alignment.

Implementation in analysis.py:
- Function: `analyze_rule_adherence()`
- Input data: RuleLLM agent decision records + Rule simulation records (both must be available)
- Computation: for each round and agent, compare RuleLLM action (buy/sell/hold) to Rule action for same market state; compute adherence rate = matching_rounds / total_rounds
- Output: `rule_adherence.png`, `adherence_stats.json`

Variant-Specific Interpretation:
- Rule adherence rate ≥80% validates the RuleLLM design (embedded rules are followed).
- Rule adherence rate <80%: check for rule override patterns — do overrides cluster in specific market states? Are they systematic (e.g., LLM always overrides when deviation < 1%)?
- Quantity deviation analysis: compute ratio `RuleLLM_quantity / Rule_quantity` per agent per round. Should cluster around [0.8, 1.2] (±20% tolerance). Outliers indicate quantity override.

Expected Output Sample:
```
Stacked bar chart: rule-aligned vs. override rounds by agent type.
Expected: ≥80% aligned (green) across all 5 agent types.
```

---

### Dimension 3: Investor Behavior Analysis

Objective (from analysis-bases.md): Characterize how each investor type's decisions contribute to anchoring dynamics.

Implementation in analysis.py:
- Function: `analyze_investor_behavior()`
- Input data: per-agent decision records
- Computation: buy/sell/hold counts; portfolio value; reasoning keyword analysis
- Output: `investor_behavior.png`

Variant-Specific Interpretation:
- RuleLLM agents' reasoning traces should show explicit rule application (e.g., "computed perceived_target = 105 + (100 − 105) × 0.3 = 103.5").
- Rounds where LLM reasoning diverges from the formula are override candidates — log and count these.
- Portfolio performance should be close to Rule variant.

---

### Dimension 4: Cross-Variant Comparison

Objective (from analysis-bases.md): Position RuleLLM results relative to Rule, LLM, and Rag.

Implementation in analysis.py:
- Function: `generate_comparison_table()`
- Input data: RuleLLM summary.json + Rule/LLM/Rag summary.json (if available)
- Output: `cross_variant_comparison.png`, updated `summary.json`

Variant-Specific Interpretation:
- RuleLLM vs. Rule: the central research comparison. Small differences → rules are sufficient to drive anchoring dynamics; LLM reasoning adds minimal value. Large differences → LLM reasoning meaningfully modulates the phenomenon.
- RuleLLM vs. LLM: isolates the rule-constraint effect. If RuleLLM ≈ LLM in metrics, the free-form persona alone was sufficient. If significantly different, rules are necessary for behavioral alignment.

---

## §4 Variant-Specific Observable Phenomena

Phenomena unique to the RuleLLM variant not present in other variants:

| Phenomenon                  | Description                                                                                                                                  | How to Observe                                                                                              | Contrast with Rule-Based                        |
|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| Rule Override Event         | LLM chooses a different action (buy vs. sell vs. hold) than the DECISION RULES specify                                                       | Action mismatch in rule-adherence analysis; rounds where RuleLLM action ≠ Rule action for same market state | Impossible in Rule — formulas are deterministic |
| Quantity Adjustment Pattern | LLM consistently adjusts quantity up or down from rule recommendation (asymmetric ±20% usage)                                                | Distribution of `RuleLLM_qty / Rule_qty` ratio — skewed left or right indicates systematic bias             | Rule quantity is always exactly formula output  |
| Rule Verbalization          | LLM explicitly states the formula in its reasoning (e.g., "I compute perceived_target as anchor + (F − anchor) × 0.3")                       | Search `<analysis>` text for formula keywords; high rate = good rule embedding                              | Rule has no reasoning traces                    |
| Rule Misinterpretation      | LLM applies formula incorrectly due to misreading the prompt (e.g., uses wrong `adjustment_factor`)                                          | Computed implied `adjustment_factor` from LLM's stated perceived_target diverges from 0.3                   | Rule always uses correct config value           |
| Hybrid Reasoning Path       | LLM applies rule for direction but adds qualitative judgment for timing (e.g., "rule says buy but market sentiment is uncertain, I'll wait") | Action = hold when rule says buy/sell; reasoning contains uncertainty language                              | Rule has no uncertainty states                  |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds          | Expected Observable                                                                 | Phenomenon Clarity                                                     |
|-----------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------|
| 50 rounds             | Rule adherence measurable; insufficient for half-life                               | Partial — adherence rate meaningful but persistence metrics incomplete |
| 100 rounds (standard) | Full anchoring lifecycle; rule adherence statistics stable                          | Good — all 8 metrics + adherence dimension computable                  |
| 200 rounds            | Longitudinal rule adherence drift detectable (does LLM drift from rules over time?) | Excellent — enables temporal analysis of rule-following behavior       |

### Agent Count Scaling

| Agent Count            | Expected Observable                                       | Market Dynamics                                        |
|------------------------|-----------------------------------------------------------|--------------------------------------------------------|
| 5 agents (1 per type)  | Clean type-level adherence rates; LLM API cost manageable | Standard — one trace per type                          |
| 10 agents (2 per type) | Intra-type rule adherence variance visible                | Better statistics — enables per-type variance analysis |

### Parameter Sensitivity

| Parameter                                       | Change           | Expected Effect on Analysis                                                                            |
|-------------------------------------------------|------------------|--------------------------------------------------------------------------------------------------------|
| `adjustment_factor` in config                   | +0.1 (0.3 → 0.4) | DECISION RULES prompt MUST be updated to match; MAD decreases (stronger updating)                      |
| `adjustment_factor` in config only (not prompt) | +0.1             | Rule–RuleLLM divergence: LLM still using 0.3 from old prompt; demonstrates synchronization requirement |
| LLM temperature                                 | Higher           | More override events; lower adherence rate                                                             |
| System prompt DECISION RULES removed            | N/A              | RuleLLM degrades to LLM variant behavior; test as ablation                                             |

---

## §6 Output Files Reference

All outputs written to: `EXPERIMENT/AnchoringEffect/RuleLLM/analysis/`

| Output File                    | Generated By                  | Contents                                                                | Interpretation                                   |
|--------------------------------|-------------------------------|-------------------------------------------------------------------------|--------------------------------------------------|
| `price_dynamics.png`           | `analyze_price_dynamics()`    | Price vs. fundamental; deviation series; Rule baseline overlay          | Primary evidence for rule-constrained anchoring  |
| `rule_adherence.png`           | `analyze_rule_adherence()`    | Adherence rate by agent type and round; override heatmap                | Validates ≥80% directional alignment criterion   |
| `adherence_stats.json`         | `analyze_rule_adherence()`    | Per-agent adherence rates; override counts; quantity ratio distribution | Quantitative validation of RuleLLM design        |
| `investor_behavior.png`        | `analyze_investor_behavior()` | Buy/sell/hold counts; portfolio values; rule verbalization rate         | Shows rule application patterns in LLM reasoning |
| `cross_variant_comparison.png` | `generate_comparison_table()` | Side-by-side metric comparison with Rule/LLM/Rag                        | Positions RuleLLM in variant comparison          |
| `summary.json`                 | `main()`                      | All 8 metrics + adherence rate; variant label                           | Cross-variant comparison input                   |

---

## §7 Cross-Variant Comparison Notes

This variant's expected position in cross-variant comparison (from `analysis-bases.md §5`):

- **Phenomenon emergence speed**: Same as Rule — embedded rules trigger anchoring dynamics immediately from round 1; no warm-up needed.
- **Phenomenon intensity**: Expected to be within ±2 percentage points of Rule MAD in most runs. The ±20% quantity freedom produces bounded deviation from Rule.
- **Behavioral realism**: Higher than Rule (LLM produces reasoning traces); lower than pure LLM (constrained by explicit rules). The key contribution: demonstrating that rule-constrained LLM can reproduce anchoring at Rule-level fidelity while adding interpretable reasoning.
- **Decision quality**: RationalUpdater (RuleLLM) performance expected to be very close to Rule baseline. Overall portfolio performance distribution should overlap significantly with Rule variant.

See also: `simulation-bases.md §9` — Variant Comparison Preview
