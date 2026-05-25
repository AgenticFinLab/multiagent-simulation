# StatusQuoBias RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether explicit rule guidance keeps LLM decisions closer to the Rule
baseline while still allowing language-model reasoning.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | RuleLLM Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Rule-guided hold behavior. |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Optional allocation-state diagnostic. |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Active rule-guided volume. |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | Signal-price response delay. |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend pressure under prompt rules. |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed order pressure by class. |

## §3 Dimension-By-Dimension Analysis

Compare RuleLLM to both Rule and LLM. The primary question is whether the
explicit `== DECISION RULES ==` prompt block improves behavioral alignment and
schema stability.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Rule guidance | Decisions reference inertia, default drift, rebalancing, or trend rules. |
| Schema stability | Parser receives all canonical fields. |
| Behavioral alignment | Quantities and action directions are closer to Rule than LLM. |

## §5 References

Metric definitions come from `../analysis-bases.md §2`; prompt-rule design
comes from `../simulation-bases.md §4` and `../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured 200 rounds for final samples.
- Confirm `summary.json.validation.is_valid` is true.
- Audit parse retries and invalid-decision failures.
- Compare action direction and quantity scale with the deterministic Rule
  variant.

## §7 Reporting Notes

Report RuleLLM as the formula-guided language condition. Any stochastic API
issues must be separated from deterministic prompt/parser contract failures.
