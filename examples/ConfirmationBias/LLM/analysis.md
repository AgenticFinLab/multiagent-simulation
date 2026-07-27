# ConfirmationBias LLM Variant — Analysis Guide

## §1 Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias LLM** variant.
Key question: *Do LLM agents with confirmation bias personas spontaneously produce
bias-like behavior without an explicit belief state variable?*

---

## §2 Metric Implementation (`LLM/analysis.py`)

Imports the shared metric and visualization functions from `Rule/analysis.py`
(DRY pattern). All 7 core metrics from `analysis-bases.md §2.1` through
`analysis-bases.md §2.7` apply identically.
See `Rule/analysis.md §2` for metric formulas.

| Metric | Implementation | Reference |
|---|---|---|
| `bias_amplitude_pct` | `analyze_confirmation_bias()` | `analysis-bases.md §2.1` |
| `bias_persistence` | `analyze_confirmation_bias()` | `analysis-bases.md §2.2` |
| `mean_absolute_deviation_pct` | Shared price-deviation calculations | `analysis-bases.md §2.3` |
| `belief_flip_count` | LLM reasoning/action proxy interpretation | `analysis-bases.md §2.4` |
| `correction_ratio` | `analyze_confirmation_bias()` | `analysis-bases.md §2.5` |
| `return_autocorrelation_ac1` | `analyze_confirmation_bias()` | `analysis-bases.md §2.6` |
| `annualized_vol_pct` | Shared return-volatility calculations | `analysis-bases.md §2.7` |

---

## §3 LLM-Specific Output Files

Running `LLM/analysis.py` writes to `EXPERIMENT/ConfirmationBias/LLM/records/analysis/`:

| File                               | Contents                                  |
|------------------------------------|-------------------------------------------|
| `summary.json`                     | Metrics and validation result             |
| `00_investor_bids.png`             | Market price and per-agent bid traces     |
| `01_confirmationbias_dynamics.png` | Price/fundamental and deviation dynamics  |
| `02_confirmationbias_analysis.png` | Volatility and cumulative bias diagnostics|
| `03_summary.png`                   | Agent VWAP and trading-volume summary     |

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                             | Description                                                                                                | How to Observe                                                                | Contrast with Rule Baseline                     |
|----------------------------------------|------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------|
| Implicit belief from persona           | LLMBeliefAnchor has no `belief` state variable; bullish tilt emerges from prompt vocabulary                | Predominantly "buy" action in early rounds; `bias_amplitude_pct` lower        | Rule compounds an explicit belief scalar        |
| Higher belief-flip frequency           | LLM reasoning switches direction more readily than Rule's `belief > 2.0` lock-in                           | `belief_flip_count` LLM > Rule; more sign changes in deviation series          | Rule locks direction until noise flips it       |
| Rationalization toward fundamental     | LLM stabilizers "reason toward" the prompted `fundamental = 100`; correction_ratio rises                   | `correction_ratio` LLM > Rule; contrarian sells appear before deviation caps  | Rule stabilizers wait until 5 % threshold       |
| Persona-consistent reasoning coherence | Each agent's `reasoning` field cites persona-appropriate vocabulary ("confirmation", "belief")             | Grep `reasoning` for persona keywords per agent class                          | Rule payloads carry no reasoning                |
| Temperature-driven quantity variance   | At temperature = 0.3, LLMBeliefAnchor emits varying quantities even with identical deviation               | Compare quantity distributions across seeds under fixed market state           | Rule quantities are deterministic in deviation  |

**Dimension-by-dimension diagnostic notes**:
- **Price vs Fundamental**: LLM bias amplitude typically lower than Rule (no compounding belief state). If LLM amplitude ≈ Rule, LLM personas successfully replicate the bias mechanism.
- **Deviation series**: Watch for oscillating deviation (LLM agents reversing more readily); `bias_persistence_rounds` LLM < Rule expected.
- **Action distribution**: `LLMBeliefAnchor` should show predominantly "buy" in early rounds; high "hold" counts indicate the persona is not effectively inducing bias. `LLMContrarianTrader` should predominantly "sell" when deviation > 0.
- **Rationality tendency**: LLM stabilizers with access to `fundamental` often reason toward it — this makes correction faster than in Rule.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                | Phenomenon Clarity | Recommended for  |
|--------------|--------------------------------------------------------------------|--------------------|------------------|
| 100          | Bias signature present but noisy; `belief_flip_count` unreliable   | Low                | Smoke testing    |
| 200          | Full Baseline → Correction arc; parse quality stable               | Medium             | Standard runs    |
| 500          | Multiple bias episodes; persona replication signal tightens         | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                    | Environment Dynamics                                |
|-------------|------------------------------------------------------------------------|-----------------------------------------------------|
| 20          | Bias measurable but LLM cost dominates run time                        | Sparse orders; MAD variance elevated                |
| 40          | Recommended: clean phase separation with tractable LLM budget          | Full mechanism observable                           |
| 80          | Reduced variance across seeds; suitable for prompt-variation runs      | Baseline dynamics with statistical mass             |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                            |
|----------------------------------------|--------|---------------------------------------------------------------------------------------|
| LLM temperature (sampling)             | +50 %  | Quantity variance widens; `belief_flip_count` rises further above Rule                |
| Prompt persona strength                | Test   | Stronger confirmation vocabulary → `bias_amplitude_pct` approaches Rule               |
| `analysis_threshold` (LLM stabilizer)  | −50 %  | LLM stabilizers engage earlier; `correction_ratio` rises further above Rule           |
| `order_size` (LLMBeliefAnchor)         | +50 %  | Higher price pressure; `bias_amplitude_pct` grows even without belief compounding      |
| Fundamental exposure in prompt         | Hide   | LLM "rationality tendency" weakens; `correction_ratio` drops toward Rule              |

---

## §6 Cross-Variant Comparison

| Metric                    | Expected vs Rule                             |
|---------------------------|----------------------------------------------|
| `bias_amplitude_pct`      | Lower (no belief compounding)                |
| `bias_persistence_rounds` | Shorter                                      |
| `belief_flip_count`       | Higher                                       |
| `correction_ratio`        | Higher (LLM rationalizes toward fundamental) |
| `annualized_vol_pct`      | Similar or slightly higher                   |

Use `summary.json` from each variant to build comparison table.

---

## §7 References

- Base metric definitions: `analysis-bases.md §2`.
- Phase interpretation and expected calibration ranges: `analysis-bases.md §3` and `analysis-bases.md §6`.
- Shared implementation: `examples/ConfirmationBias/Rule/analysis.py`.
- LLM-specific observable behavior: `examples/ConfirmationBias/LLM/players.py` and `examples/ConfirmationBias/LLM/prompts.py`.
