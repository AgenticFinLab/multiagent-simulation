# GFC2008 — RuleLLM Variant Analysis

## §1 Overview

| Aspect    | Detail                       |
|-----------|------------------------------|
| Variant   | RuleLLM                      |
| Metrics   | BBI, CII, FSI, RRI, OSP, WDI |
| Reference | `analysis-bases.md`          |
| Baseline  | Rule variant                 |

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

## §3 RuleLLM-Specific Notes

### §3.1 RuleLLMMBSOriginator
- OSP stays close to Rule; LLM modulations bounded by `origination_rate` floor.

### §3.2 RuleLLMRatingAgency
- BBI expected close to Rule upper bound; LLM may push slightly higher.

### §3.3 RuleLLMLeveragedInvestor
- CII lower than Rule: LLM-modulated fire-sale quantity typically less than Rule's full 50%.
- FSI similar duration but smaller per-round impact.

### §3.4 RuleLLMDistressedBuyer
- RRI slightly higher than Rule: LLM may deploy capital more aggressively when reasoning about recovery.

### §3.5 RuleLLMRegulator
- Stochastic intervention still present; LLM narrative bias pushes effective rescue_probability upward.

---

## §4 Expected Ranges (RuleLLM vs. Rule Baseline)

| Metric | RuleLLM Expected Range | vs. Rule | Basis                      |
|--------|------------------------|----------|----------------------------|
| BBI    | 0.05–0.22              | Similar  | Rule threshold preserved   |
| CII    | 0.08–0.30              | Lower    | Moderated fire sales       |
| FSI    | 2–7 rounds             | Similar  | Rule trigger kept          |
| RRI    | 0.25–0.65              | Higher   | Active LLM Regulator       |
| OSP    | 0.60–0.90              | Similar  | Origination rate-dominated |
| WDI    | 0.10–0.28              | Similar  | Crisis arc driven by Rule  |

## §5 References

Metric definitions are inherited from `analysis-bases.md §2`; RuleLLM prompt
rules trace to `simulation-bases.md §4.1-§4.5`.

## §6 Cross-Variant Comparison

Compare RuleLLM against Rule to measure language-mediated quantity and timing
effects under explicit decision rules.

## §7 Quality Checks

- Confirm the run completed 200 configured rounds.
- Confirm prompts contain both `== PERSONA ==` and `== DECISION RULES ==`.
- Confirm parse failures do not silently become hold decisions; deterministic contract failures must fail fast.
- Confirm accepted orders preserve canonical `action`, `bid_price`, `quantity`, and `reasoning`.
