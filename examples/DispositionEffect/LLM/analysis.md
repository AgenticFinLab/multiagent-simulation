# DispositionEffect LLM Variant — analysis.md

## §1 Overview

The LLM variant reuses the shared DispositionEffect analysis functions from
`Rule/analysis.py`. The analysis asks whether persona-only LLM investors exhibit
the same PGR > PLR tendency as the deterministic Rule baseline.

## §2 Metrics and Functions

| Metric | Function | analysis-bases.md Ref |
|---|---|---|
| Proportion of Gains Realized (PGR) | `Rule.analysis.calculate_pgr_plr()` | §2.1 |
| Proportion of Losses Realized (PLR) | `Rule.analysis.calculate_pgr_plr()` | §2.2 |
| Disposition Coefficient (DC) | `Rule.analysis.generate_summary()` | §2.3 |
| PGR/PLR Ratio | `Rule.analysis.calculate_pgr_plr()` | §2.4 |
| Reasoning-trace proxy | LLM response artifacts and order `reasoning` payloads | §3 |
| Performance comparison | `Rule.analysis.plot_fig6_portfolio_evolution()` | §2.6 |
| Cross-variant comparison | `summary.json` against Rule baseline | §5 |

## §3 Data Loading Contract

`LLM/analysis.py` calls `load_simulation_data(config)` from the Rule analysis
module. LLM order payloads must contain the same required trading fields as Rule:
`bid_price`, `quantity`, `strategy`, and `reasoning`. Missing required fields are
analysis failures, not zero-valued observations.

## §4 LLM Variant Notes

- LLM reasoning variance is evaluated through PGR, PLR, DC, and order reasoning
  traces.
- Persona-only prompts may produce stronger or weaker disposition behavior than
  Rule; the analysis does not impose a rule-compliance target.
- `LLMLossAverse` and `LLMDispositionBiased` should be compared for loss-sale
  reluctance.

## §5 Output Files

The LLM variant writes the same `summary.json` and seven figures as the Rule
variant. LLM-specific interpretation should additionally inspect raw LLM response
artifacts and the `reasoning` strings preserved in order payloads.

## §6 Validation Criteria

A valid LLM run completes with 200 rounds, parseable order payloads, and no
analysis field substitution. Scenario validity is assessed by whether PGR > PLR
for disposition-biased investors and by how closely the aggregate behavior
matches the bands in `analysis-bases.md §6`.

## §7 References

Metric definitions and DOI references are centralized in `analysis-bases.md §2`.
Investor theory references are centralized in `simulation-bases.md §4.1–§4.5`.

---

## §4 Variant-Specific Observable Phenomena

LLM is the persona-only variant. `LLMLossAverse`, `LLMDispositionBiased`, and
their rational counterparts decide `buy` / `sell` / `hold` from natural-
language personas without embedded formulas. Analysis should look for
LLM-driven variance that is absent from Rule.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Emotional over-eagerness on gains | `fig7_sell_gain_loss.png` — `LLMDispositionBiased` sells spread from +1 % into deep gain territory; sometimes above +15 % | Rule cluster is tight around `gain_threshold` |
| Extreme loss reluctance | `summary.json → strategy_comparison` — PLR for LLM disposition strategies may collapse below 0.05 | Rule PLR is bounded by loss_threshold |
| Higher HPA under narrative anchoring | `extended_metrics.holding_periods` — `LLMLossAverse` HPA may exceed 2.5 | Rule ceiling is around 2.0 |
| Cross-run instability | Rerunning with different seeds/temperatures shifts PGR by ±0.05 | Rule PGR is reproducible |
| Reasoning-string diversity | Order payload `reasoning` field is non-empty and varies across rounds | Rule payloads carry no reasoning text |

There is no hard rule enforcing the schema in LLM prompts, so the analysis
must additionally check that order payloads contain the required
`bid_price`, `quantity`, `strategy`, and `reasoning` fields before treating
metrics as trustworthy.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 100 | LLM cost manageable; disposition ordering detectable but noisy | Low — LLM tail effects dominate | Prompt tuning |
| 200 | Full arc; PGR/PLR gap resolved on average | Medium | Standard runs |
| 500 | Convergence of DC and HPA distributions; robust comparison to Rule | High | Persona-effect research; watch API cost |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~5 per strategy) | Aggregate PGR/PLR direction correct but strategy-level noise high | LLM stochasticity dominates |
| Recommended (10–20 per strategy) | Stable strategy-level PGR/PLR; readable `fig7` violins | Full LLM variance visible against Rule |
| Large (50+ per strategy) | Tight LLM distributions; LLM cost the binding constraint | Cost-limited regime |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| LLM temperature | +50% | Wider PGR distribution; occasional inversion of PGR/PLR ordering |
| LLM temperature | −50% | LLM behavior converges toward the persona centroid; closer to Rule |
| Persona prompt intensity (`== PERSONA ==`) | +50% verbosity | Stronger disposition signature; higher HPA |
| Persona prompt intensity | −50% verbosity | LLM defaults dominate; PGR–PLR gap shrinks |
| Market volatility (news / noise σ) | +50% | LLM sells more emotionally; HPA and PDI both rise |

---

## §7 Cross-Variant Comparison Notes

Expected relative positions (see `analysis-bases.md §5`):

| Comparison Axis | LLM's Expected Position | Reason |
|---|---|---|
| PGR level | Variable; may be > Rule (emotional eagerness) | Persona pushes eager gain realization |
| PLR level | Variable; may be < Rule (stronger loss aversion) | LLM anchors on prospect-theory losses more strongly |
| PGR/PLR ratio | Wider range than Rule; central tendency ≥ Rule | Persona-only reasoning amplifies asymmetry |
| Disposition coefficient (DC) | Potentially wider range | No embedded rule to bound the effect |
| HPA | May exceed 2.0 ("can't bear to sell") | LLM narrative bias |
| Performance drag (PDI) | Higher variance; may exceed Rule | Emotional trading is costly |
| Schema fidelity | Not guaranteed; must be audited | No `== DECISION RULES ==` block |
| Variance across seeds | High | LLM sampling stochasticity dominates |
