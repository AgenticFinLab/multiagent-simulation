# ConfirmationBias RuleLLM Variant — Analysis Guide

## §1 Analysis Overview

This guide covers interpretation of results from the **ConfirmationBias RuleLLM** variant.
Key question: *Do LLM agents with explicit decision rules produce more structured
and consistent behavior? Does rule-guided behavior reproduce the Rule variant's bias dynamics?*

---

## §2 Metric Implementation (`RuleLLM/analysis.py`)

Imports the shared metric and visualization functions from `Rule/analysis.py`
(DRY pattern). No additional variant-specific analysis function is required:
the embedded rules serve as deeper investor characterization, not executable
mandates to be measured against. Metrics map to `analysis-bases.md §2.1`
through `analysis-bases.md §2.7`.

| Metric | Implementation | Reference |
|---|---|---|
| `bias_amplitude_pct` | `analyze_confirmation_bias()` | `analysis-bases.md §2.1` |
| `bias_persistence` | `analyze_confirmation_bias()` | `analysis-bases.md §2.2` |
| `mean_absolute_deviation_pct` | Shared price-deviation calculations | `analysis-bases.md §2.3` |
| `belief_flip_count` | Rule-guided reasoning/action proxy interpretation | `analysis-bases.md §2.4` |
| `correction_ratio` | `analyze_confirmation_bias()` | `analysis-bases.md §2.5` |
| `return_autocorrelation_ac1` | `analyze_confirmation_bias()` | `analysis-bases.md §2.6` |
| `annualized_vol_pct` | Shared return-volatility calculations | `analysis-bases.md §2.7` |

---

## §3 RuleLLM-Specific Output Files

Running `RuleLLM/analysis.py` writes to `EXPERIMENT/ConfirmationBias/RuleLLM/records/analysis/`:

| File                               | Contents                                  |
|------------------------------------|-------------------------------------------|
| `summary.json`                     | Metrics and validation result             |
| `00_investor_bids.png`             | Market price and per-agent bid traces     |
| `01_confirmationbias_dynamics.png` | Price/fundamental and deviation dynamics  |
| `02_confirmationbias_analysis.png` | Volatility and cumulative bias diagnostics|
| `03_summary.png`                   | Agent VWAP and trading-volume summary     |

---

## §4 Variant-Specific Observable Phenomena

| Phenomenon                              | Description                                                                                                     | How to Observe                                                                | Contrast with Rule Baseline                     |
|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------|
| Rule-guided threshold behaviour         | Embedded `== DECISION RULES ==` anchor BeliefAnchor and SelectiveScanner to fixed deviation thresholds          | Timing of buy/sell events tighter than pure LLM; MAD close to Rule            | Rule uses compounding belief state              |
| BeliefAnchor simplification gap         | RuleLLM BeliefAnchor uses a deviation-threshold rule instead of compounding `belief` scalar                     | `bias_amplitude_pct` lower than Rule; higher than LLM                          | Rule locks direction via belief > 2.0           |
| Structured reasoning                    | LLM `<analysis>` tags cite embedded rule vocabulary alongside persona narrative                                 | Grep `analysis` for rule keywords ("threshold 2 %", "trigger 5 %")             | Rule payloads carry no reasoning                |
| Rule-fidelity drift signal              | If reasoning ignores rule text, RuleLLM metrics drift toward LLM                                                | Compare per-agent action distributions with rule-implied action counts         | Rule cannot drift; LLM has no anchor            |
| Deeper characterization                 | Embedded rules act as investor knowledge/habit; not enforced but shape decision framing                         | Cross-check `reasoning` for rule-consistent overrides                          | Rule cannot override; LLM has no rule anchor    |

RuleLLM sits between Rule (deterministic) and LLM (fully unanchored). Embedded rules serve as **deeper investor characterization** rather than executable mandates. Expected positions: `bias_amplitude_pct` between Rule and LLM; `bias_persistence_rounds` closer to Rule; `belief_flip_count` closer to LLM.

**Rule-fidelity improvement strategies** (when RuleLLM diverges from Rule):
1. Add explicit numerical thresholds in `== DECISION RULES ==`.
2. Reduce ambiguity: "If deviation > 0.02, you MUST buy exactly {order_size} units".
3. Reduce temperature to 0.1 for more deterministic outputs.
4. Add few-shot examples in the user template.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                    | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------------|--------------------|------------------|
| 100          | Bias signature visible but seed variance elevated                      | Low                | Smoke testing    |
| 200          | Full Baseline → Correction arc; RuleLLM anchoring visible              | Medium             | Standard runs    |
| 500          | Rule-anchored MAD stabilizes; LLM quantity variance averages out       | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                    | Environment Dynamics                                |
|-------------|------------------------------------------------------------------------|-----------------------------------------------------|
| 20          | Bias measurable but LLM cost dominates                                 | Sparse orders; `belief_flip_count` variance elevated |
| 40          | Recommended: clean phase separation with tractable LLM budget          | Full mechanism observable                           |
| 80          | Reduced variance across seeds; suitable for rule-fidelity studies      | Baseline dynamics with statistical mass             |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                            |
|----------------------------------------|--------|---------------------------------------------------------------------------------------|
| Prompt rule wording (paraphrase)       | Test   | Rule adherence drifts; `bias_amplitude_pct` migrates toward LLM baseline              |
| LLM temperature                        | +50 %  | `belief_flip_count` rises; `bias_persistence_rounds` shortens                         |
| `confirmation_strength` (in rule text) | +50 %  | Rule-anchored `bias_amplitude_pct` rises toward Rule                                  |
| `analysis_threshold`                   | −50 %  | Stabilizers engage earlier; `correction_ratio` rises                                  |
| Rule-embedded `order_size`             | +50 %  | Higher price pressure per rule-triggered order; MAD grows                             |

---

## §6 Cross-Variant Comparison

| Metric                    | Expected Position          |
|---------------------------|----------------------------|
| `bias_amplitude_pct`      | Rule > RuleLLM > LLM       |
| `bias_persistence_rounds` | Rule > RuleLLM ≈ LLM       |
| `correction_ratio`        | LLM ≈ Rag > RuleLLM ≈ Rule |

Compare `summary.json` across variants to identify where embedded rules
most effectively characterize investor behavior.

---

## §7 References

- Base metric definitions: `analysis-bases.md §2`.
- Phase interpretation and expected calibration ranges: `analysis-bases.md §3` and `analysis-bases.md §6`.
- Shared implementation: `examples/ConfirmationBias/Rule/analysis.py`.
- RuleLLM-specific behavior: `examples/ConfirmationBias/RuleLLM/players.py` and `examples/ConfirmationBias/RuleLLM/prompts.py`.
