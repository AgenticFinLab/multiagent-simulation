# DispositionEffect Rule Variant — analysis.md

## §1 Overview

The Rule variant uses `Rule/analysis.py` as the authoritative analysis module
for all DispositionEffect variants. It loads market prices and per-player order
payloads, computes PGR/PLR-style disposition metrics, writes `summary.json`, and
generates seven diagnostic figures. This file maps the concrete implementation
back to `analysis-bases.md`.

## §2 Metrics and Functions

| Metric | Function | analysis-bases.md Ref |
|---|---|---|
| Proportion of Gains Realized (PGR) | `calculate_pgr_plr()` | §2.1 |
| Proportion of Losses Realized (PLR) | `calculate_pgr_plr()` | §2.2 |
| Disposition Coefficient (DC) | `generate_summary()` | §2.3 |
| PGR/PLR Ratio | `calculate_pgr_plr()` | §2.4 |
| Holding Period Asymmetry (HPA) | `holding_period_asymmetry()` | §2.5 |
| Performance Drag Index (PDI) | `calculate_extended_metrics()` and `terminal_wealth()` | §2.6 |
| Tax Reversal Index (TRI) | `calculate_extended_metrics()` | §2.7 |

## §3 Data Loading Contract

`load_simulation_data(config)` reads the coordinator `price` batch and every
player turn payload. Each trade record must contain `bid_price`, `quantity`,
`strategy`, and an injected `round`. Missing required fields raise errors rather
than being silently replaced.

## §4 Rule Variant Notes

- PGR/PLR are derived from the deterministic threshold behavior implemented in
  `Rule/players.py`.
- Initial cash, position, purchase price, and fundamental value are loaded from
  the expanded player configuration; analysis contains no scenario defaults.
- DispositionInvestor keeps its configured initial purchase-price anchor,
  matching `move_reference=False`; other buying strategies use average cost.
- The Rule output is the comparison baseline for LLM, RuleLLM, and Rag.
- Market stochasticity comes from news and noise; investor rules remain
  deterministic for a given observed state.

## §5 Output Files

| File | Content |
|---|---|
| `summary.json` | Price statistics, PGR, PLR, DC, ratio, HPA, PDI, TRI, wealth, and validation score |
| `fig1_price_dynamics.png` | Price path, fundamental level, returns, rolling volatility |
| `fig2_pgr_plr_comparison.png` | PGR/PLR and DC by strategy |
| `fig3_trading_activity.png` | Buy/sell counts and traded volume |
| `fig4_return_distribution.png` | Return distribution and summary statistics |
| `fig5_disposition_ratio.png` | PGR/PLR ratio and realized/paper gain-loss pools |
| `fig6_portfolio_evolution.png` | Position and equity value trajectory |
| `fig7_sell_gain_loss.png` | Sell events by gain/loss territory |

## §6 Validation Criteria

`generate_summary()` calls `validate_disposition_effect()` with the
DispositionInvestor PGR, PLR, and DC. A valid Rule run should show PGR > PLR and
roughly match the Odean-inspired calibration bands in `analysis-bases.md §6`.

## §7 References

Metric definitions and DOI references are centralized in `analysis-bases.md §2`.
Investor theory references are centralized in `simulation-bases.md §4.1–§4.5`.

---

## §4 Variant-Specific Observable Phenomena

Rule is the deterministic reference variant for DispositionEffect. Given a
fixed seed, `DispositionInvestor`, `RationalInvestor`, `TaxAwareInvestor`,
`IndexHolder`, and `InstitutionalInvestor` execute threshold policies with no
LLM-driven variance and no retrieval side-channel.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Reproducible PGR > PLR ordering | `fig2_pgr_plr_comparison.png` — DispositionInvestor green (PGR) bar strictly above red (PLR) bar | This is the baseline; LLM may invert on some seeds |
| Threshold-locked sell spike | `fig3_trading_activity.png` and `fig7_sell_gain_loss.png` — sells cluster in the +2 %…+8 % gain territory (DispositionInvestor `gain_threshold`) | Rule cluster is tight; LLM smears across ±10 % |
| Symmetric InstitutionalInvestor sells | `fig7_sell_gain_loss.png` — Institutional sells at ±8 % symmetrically | Reference for anti-disposition tax behavior |
| Analytic HPA plateau | `summary.json → extended_metrics.holding_periods` per DispositionInvestor gives `holding_period_asymmetry` in the 1.5–2.5 band | Rule sets the analytic band |
| Deterministic PDI drag | `summary.json → extended_metrics.performance_drag_index` is stable across reruns at fixed seed | LLM PDI has higher variance |

Rule agents produce identical decisions given identical observed market state;
market stochasticity comes only from news and noise processes upstream of the
investor policies.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 100 | Enough gain/loss cycles for DC to be measurable; HPA thin | Low — few sell events | Quick smoke test |
| 200 | Full disposition arc; PGR/PLR pools well populated | Medium | Standard runs |
| 500 | Stable PDI and TRI; robust cross-strategy contrast | High | Odean-benchmark studies |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~5 per strategy) | DC and PGR/PLR ratio identifiable but noisy | Sparse strategy-level pools |
| Recommended (10–20 per strategy) | Clean PGR–PLR gap; readable violin plots in `fig7` | Full disposition mechanism visible |
| Large (50+ per strategy) | Tight distributions; small-effect strategies (Tax, Institutional) statistically separable | Diminishing marginal insight per agent |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| `DispositionInvestor.gain_threshold` | +50% | Fewer gain-side sells → lower PGR; PGR/PLR ratio compressed |
| `DispositionInvestor.gain_threshold` | −50% | More sells in small-gain territory; higher PGR; larger DC |
| `DispositionInvestor.loss_threshold` | −50% (more negative) | Even fewer loss realizations; PLR falls; TRI rises |
| `TaxAwareInvestor` population share | +50% | Higher aggregate loss realization; TRI more pronounced |
| Market volatility (news / noise σ) | +50% | Wider gain/loss excursions; HPA rises for DispositionInvestor; PDI grows |

---

## §7 Cross-Variant Comparison Notes

Rule is the deterministic reference variant against which LLM, RuleLLM, and
Rag are compared. Expected relative positions come from `analysis-bases.md §5`:

| Comparison Axis | Rule's Expected Position | Reason |
|---|---|---|
| PGR level | ≈ 0.148 (Odean-calibrated) | Threshold rule fires exactly at `gain_threshold` |
| PLR level | ≈ 0.098 (Odean-calibrated) | Loss holding rule is symmetric-deterministic |
| PGR/PLR ratio | 1.4–1.7 (Odean benchmark) | Analytic upper anchor for behavioral tests |
| Disposition coefficient (DC) | ≈ 0.05, tight | No reasoning noise |
| HPA | 1.5–2.0, reproducible | Deterministic holding logic |
| Performance drag (PDI) | 0.03–0.06 | Analytic lower bound for behavioral drag |
| Tax reversal (TRI) | 2.0–4.0 | Rule-based tax harvesting is decisive |
| Variance across seeds | Lowest | Only exogenous stochasticity contributes |
