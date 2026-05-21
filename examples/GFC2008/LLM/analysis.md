# GFC2008 — LLM Variant Analysis

## §1 Overview

| Aspect    | Detail                       |
|-----------|------------------------------|
| Variant   | LLM                          |
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

## §3 LLM-Specific Notes

### §3.1 LLMMBSOriginator
- OSP may vary more than Rule due to LLM modulating origination volume based on narrative.
- Watch for OSP < 0.50: LLM originator restraining supply (not representing lax-screening theory).

### §3.2 LLMRatingAgency
- BBI driven by LLM's willingness to buy at inflated prices.
- LLM may produce BBI > 0.20 if model narrativizes overconfidence strongly.

### §3.3 LLMLeveragedInvestor
- FSI more variable vs. Rule: LLM may panic-sell early (shorter FSI, smaller CII) or delay (longer FSI).
- Check FSI < 2 rounds: may indicate LLM pre-liquidating — valid crisis variant.

### §3.4 LLMDistressedBuyer
- RRI may be higher than Rule if LLM deploys more capital per crisis round.
- Context: LLM can deploy >30% cash vs. Rule's fixed fraction.

### §3.5 LLMRegulator
- Stochastic Rule rescue_probability replaced by LLM reasoning — may intervene more reliably.
- RRI upper bound shifts higher (> 0.70) in LLM variant.

---

## §4 Expected Ranges (LLM vs. Rule Baseline)

| Metric | LLM Expected Range | vs. Rule       | Basis                            |
|--------|--------------------|----------------|----------------------------------|
| BBI    | 0.03–0.25          | Wider          | LLM rating inflation variability |
| CII    | 0.05–0.40          | Wider          | Preemptive or delayed fire sale  |
| FSI    | 1–10 rounds        | Wider          | LLM fire-sale timing variance    |
| RRI    | 0.15–0.70          | Higher ceiling | More active LLM intervention     |
| OSP    | 0.50–0.90          | Similar        | LLM-modulated origination        |
| WDI    | 0.08–0.35          | Similar        | Crisis arc dependent             |

## §5 References

Metric definitions are inherited from `analysis-bases.md §2`; LLM investor
roles trace to `simulation-bases.md §4.1-§4.5`.

## §6 Cross-Variant Comparison

Compare LLM results against Rule to measure persona-only crisis reasoning, and
against RuleLLM/RAG to isolate explicit-rule and knowledge effects.

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Audit parse failures and retry counts before acceptance; deterministic parser/provider failures must fail fast.
- Confirm accepted decisions produce canonical `action`, `bid_price`, `quantity`, and `reasoning`.
- Review action distribution for excessive holds or one-sided behavior.
