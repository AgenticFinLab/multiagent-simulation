# DotComBubble Rule Variant — analysis.md

## §1 Analysis Objectives

Quantify bubble formation, persistence, crash severity, momentum amplification,
short-seller resistance, and recovery in the Rule variant. Definitions and
interpretation thresholds come from `analysis-bases.md §2`.

## §2 Metric → Function Mapping

| Metric | Function | Analysis basis |
|---|---|---|
| Bubble Amplitude Index (BAI) | `bubble_amplitude_index()` | `analysis-bases.md §2`, BAI |
| Bubble Duration (BD) | `bubble_duration()` | `analysis-bases.md §2`, BD |
| Crash Severity (CS) | `crash_severity()` | `analysis-bases.md §2`, CS |
| Momentum Amplification Factor (MAF) | `momentum_amplification_factor()` | `analysis-bases.md §2`, MAF |
| Short-Seller Resistance (SSR) | `short_seller_resistance()` | `analysis-bases.md §2`, SSR |
| Recovery Time (RT) | `recovery_time()` | `analysis-bases.md §2`, RT |
| API and RAG Quality (AQR) | `rule_order_quality()` records `applicable_to_api_or_rag: false` and validates the common order contract | `analysis-bases.md §2`, AQR |

`calculate_metrics()` computes all seven reported entries and raises when no
market records exist. The Rule variant has no API or retrieval calls, so its AQR
entry is explicitly non-applicable rather than inventing API/RAG statistics.

## §3 Rule-Variant-Specific Notes

- `NewEconomyEvangelist` supplies persistent narrative demand until a deep crash.
- `IPOFlipper` begins with inventory so its profit-taking branch is observable.
- `MomentumFollower` contributes to MAF only in rounds above the 10% bubble threshold.
- `SkepticalValueInvestor` and `ShortSeller` begin with the inventories used by
  the design-basis worked examples, allowing their stabilizing sell rules to run.

## §4 Variant-Specific Observable Phenomena

| Phenomenon                            | Description                                                                                            | How to Observe                                                                | Contrast with Baseline Variant |
|---------------------------------------|--------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|--------------------------------|
| Deterministic narrative demand        | NewEconomyEvangelist bids until price exceeds crash trigger; no reasoning-driven hesitation            | Bid volume of Evangelist strictly non-zero until deep-crash round             | This is the baseline           |
| Threshold-locked momentum surge       | MomentumFollower contributes exactly when `deviation > 0.10`                                           | `summary.json → metrics.momentum_amplification_factor` (MAF ≈ 0.20–0.50)      | This is the baseline           |
| Constrained short-seller resistance   | ShortSeller sells only when position remains within borrow limits; SSR non-zero but bounded            | `metrics.short_seller_resistance` > 0                                         | This is the baseline           |
| Analytic crash severity               | CS matches the peak-to-trough drop implied by decision rules; reproducible seed-to-seed                | `metrics.crash_severity` in [0.30, 0.80]                                      | This is the baseline           |
| IPO flip signature                    | IPOFlipper starts with inventory and unloads once profit-taking threshold trips                        | Bid trace shows a clear post-peak sell pulse                                  | This is the baseline           |

Rule is the deterministic reference for DotComBubble: every threshold is hard, every bubble/crash phase transition fires exactly at the calibrated boundary. AQR (API/RAG Quality) is explicitly non-applicable because Rule makes no API or retrieval calls.

**Rule expected metric ranges** (calibration anchors):

| Metric | Primary validation signal                                                     |
|--------|-------------------------------------------------------------------------------|
| BAI    | > 0.10 indicates a visible normalized bubble                                  |
| BD     | > 15 rounds indicates meaningful persistence                                  |
| CS     | 0.30–0.80 is the broad meaningful-crash band                                  |
| MAF    | 0.20–0.50 indicates mixed momentum amplification                              |
| SSR    | Non-zero values show active constrained arbitrage                             |
| RT     | `null` allowed when recovery is incomplete within the run                     |
| AQR    | Common order-contract compliance = 1.0 (API/RAG marked non-applicable)        |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                    | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------------|--------------------|------------------|
| 100          | Bubble formation + crash visible; recovery truncated                   | Low                | Quick testing    |
| 200          | Full Bubble → Crash → Recovery arc; MAF and SSR stably estimated       | Medium             | Standard runs    |
| 500          | Multiple bubble cycles; RT/CS distributions tighten across seeds       | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                | Environment Dynamics                        |
|-------------|--------------------------------------------------------------------|---------------------------------------------|
| 20          | Bubble still visible; noisier MAF                                  | Sparse order flow; BAI variance elevated    |
| 40          | Clean phase separation; stable estimates for all seven §2 metrics  | Full mechanism observable                   |
| 80          | Reduced per-seed variance; suitable for parameter sweeps           | Baseline mechanism with statistical mass    |

### Parameter Sensitivity (Variant-Specific)

| Parameter                                | Change | Expected Effect on This Variant's Analysis                                          |
|------------------------------------------|--------|-------------------------------------------------------------------------------------|
| `NewEconomyEvangelist.narrative_strength`| +50 %  | BAI rises above 0.15; BD lengthens; CS deepens                                      |
| `NewEconomyEvangelist.narrative_strength`| −50 %  | BAI drops below 0.10; bubble may fail to form                                       |
| `MomentumFollower.momentum_threshold`    | +50 %  | MAF drops; fewer rounds trigger amplification                                       |
| `ShortSeller.borrow_limit`               | +50 %  | SSR rises; crash severity dampens; recovery begins earlier                          |
| `SkepticalValueInvestor` share           | +50 %  | BAI compresses; CS softens; BD shortens                                             |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/DotComBubble/Rule/analysis/`.

| Output File                          | Generated By                    | Contents                                                             | How to Interpret                                                                     |
|--------------------------------------|---------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `summary.json`                       | `main()`                        | Metrics (BAI/BD/CS/MAF/SSR/RT/AQR) + validation + order-contract QA  | Compare against calibration anchors above; AQR should carry `applicable_to_api_or_rag: false` |
| `dotcombubble_rule_dynamics.png`     | `create_visualizations()`       | Price vs fundamental with bubble/crash phase annotations             | Visual sanity check: bubble peak, trough, recovery arc                               |

Missing records must be treated as an error; the pipeline does not substitute zero-valued metrics. Every order must present a valid `action`, positive `bid_price`, non-negative `quantity`, `reasoning`, and `strategy` (agent type) — checked by `rule_order_quality()`.

## §7 Cross-Variant Comparison

| Variant | Expected comparison |
|---|---|
| LLM | Persona reasoning can change action timing and quantities |
| RuleLLM | Explicit rules are mediated through language-model decisions |
| Rag | Retrieved historical context can change valuation discipline and timing |

### Quality Checks

- Confirm the number of market records equals the configured round count.
- Confirm every market record contains positive `price` and `fundamental` values.
- Confirm every order has a valid action, positive bid price, non-negative quantity, reasoning, and agent type.
- Confirm `summary.json` and `dotcombubble_rule_dynamics.png` are produced.
- Treat missing records as an error; do not substitute zero-valued metrics.
