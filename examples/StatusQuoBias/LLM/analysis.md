# StatusQuoBias LLM — Analysis Documentation

## §1 Analysis Objectives

Evaluate whether persona-only LLM agents reproduce status quo inaction and
default adherence while preserving the same structural market outputs as Rule.

## §2 Metric To Function Mapping

| Metric | Function | analysis-bases.md Ref | LLM Notes |
|---|---|---|---|
| Inertia Rate | `compute_inertia_rate()` | `analysis-bases.md §2.1` | Persona-driven hold behavior. |
| Default Adherence | `compute_default_adherence()` | `analysis-bases.md §2.2` | Optional allocation-state diagnostic. |
| Active Rebalance Volume | `compute_active_rebalance_volume()` | `analysis-bases.md §2.3` | Active persona corrective volume. |
| Underreaction Lag | `compute_underreaction_lag()` | `analysis-bases.md §2.4` | LLM-driven adjustment delay. |
| Momentum Offset | `compute_momentum_offset()` | `analysis-bases.md §2.5` | Trend persona pressure. |
| Price Deviation | `compute_price_deviation()` | `analysis-bases.md §2.6` | Fundamental gap. |
| Agent Attribution | `compute_agent_attribution()` | `analysis-bases.md §2.7` | Signed order pressure by class. |

## §3 Dimension-By-Dimension Analysis

Compare the LLM output with Rule on hold rates, price deviation, active
rebalancing volume, and the presence of natural-language reasoning.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Inaction rationalization | Reasoning explains why current holdings or defaults are retained. |
| Persona separation | Active and momentum personas trade more readily than inertial personas. |
| Output quality | Invalid JSON or missing required fields fail after bounded retries. |

## §5 References

Metrics derive from `../analysis-bases.md §2`; persona targets derive from
`../simulation-bases.md §4` and `../simulation-bases.md §9`.

## §6 Quality Checks

- Confirm the run completed the configured 200 rounds for final samples.
- Confirm `summary.json.validation.is_valid` is true.
- Review LLM logs for parse failures, retries, and provider errors.
- Confirm no silent fallback hold path is used for deterministic contract
  failures.

## §7 Reporting Notes

Report LLM as the persona-reasoning condition. If parse failures occur, include
the count and whether the final accepted order remained schema-valid.
