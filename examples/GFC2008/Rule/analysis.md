# GFC2008 — Rule Variant Analysis

## §1 Overview

| Aspect    | Detail                       |
|-----------|------------------------------|
| Variant   | Rule                         |
| Metrics   | BBI, CII, FSI, RRI, OSP, WDI |
| Reference | `analysis-bases.md`          |
| Baseline  | This is the Rule baseline    |

---

## §2 Metric → Function Mapping

| Metric | Function Signature                                              | Key Args                                                 |
|--------|-----------------------------------------------------------------|----------------------------------------------------------|
| BBI    | `bubble_build_index(dev_history)`                               | `dev_history: list`                                      |
| CII    | `crisis_intensity_index(dev_history)`                           | `dev_history: list`                                      |
| FSI    | `fire_sale_index(order_history, deviation_history)`             | `order_history: list`, `deviation_history: list`         |
| RRI    | `rescue_response_index(stabilizer_volume, destabilizer_volume)` | `stabilizer_volume: float`, `destabilizer_volume: float` |
| OSP    | `originator_sell_pressure(mbs_sell_volume, total_sell_volume)`  | `mbs_sell_volume: float`, `total_sell_volume: float`     |
| WDI    | `wealth_distribution_index(final_wealth)`                       | `final_wealth: dict`                                     |

---

## §3 Rule-Specific Notes

### §3.1 MBSOriginator
- OSP measures steady origination supply pressure independent of price.
- High OSP (> 0.70) confirms lax screening model activated throughout simulation.

### §3.2 RatingAgency
- BBI driven by RatingAgency buying at inflated perceived_fundamental.
- If BBI = 0, check `overrating_bias` config — may be too low to trigger buy condition.

### §3.3 LeveragedInvestor
- FSI counts consecutive rounds where deviation < -margin_call_trigger.
- Fire sale cascade is the main driver of CII depth.

### §3.4 DistressedBuyer
- RRI = DistressedBuyer + Regulator stabilizing volume / LeveragedInvestor fire-sale volume.
- RRI < 0.20 means stabilizers overwhelmed; RRI > 0.60 means crisis shallow.

### §3.5 Regulator
- Stochastic intervention (rescue_probability = 0.3) creates run-to-run variance in CII.
- High variance in CII across runs is expected behavior, not a bug.

---

## §4 Expected Ranges (Rule Baseline)

| Metric | Rule Expected Range | Interpretation                           |
|--------|---------------------|------------------------------------------|
| BBI    | 0.05–0.20           | Bubble phase overvaluation magnitude     |
| CII    | 0.10–0.35           | Crisis crash depth below fundamental     |
| FSI    | 2–8 rounds          | Fire-sale cascade duration               |
| RRI    | 0.20–0.60           | Partial stabilization ratio              |
| OSP    | 0.60–0.90           | MBSOriginator share of total sell volume |
| WDI    | 0.10–0.30           | Wealth Gini from distressed-buyer gains  |

## §5 References

Metric definitions are inherited from `analysis-bases.md §2`; investor-role
interpretation traces to `simulation-bases.md §4.1-§4.5`.

## §6 Cross-Variant Comparison

Rule metrics provide the deterministic baseline for LLM, RuleLLM, and RAG
comparisons.

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Confirm price and fundamental records are present and non-zero.
- Confirm the analysis raises on missing records instead of fabricating zeros.
- Confirm order payloads preserve valid `action` and numeric `quantity`.
