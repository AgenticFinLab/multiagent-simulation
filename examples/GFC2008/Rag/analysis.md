# GFC2008 — Rag Variant Analysis

## §1 Overview

| Aspect    | Detail                       |
|-----------|------------------------------|
| Variant   | Rag                          |
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

## §3 Rag-Specific Notes

### §3.1 RagLLMMBSOriginator
- Retrieved origination cases may push OSP higher; watch for OSP > 0.90 (over-origination).

### §3.2 RagLLMRatingAgency
- BBI likely above Rule if corpus contains CDO overvaluation cases (15–30% overrating literature).
- BBI > 0.25 indicates strong rating inflation retrieval — calibrate corpus if too high.

### §3.3 RagLLMLeveragedInvestor
- CII and FSI may be higher than Rule if Lehman/LTCM scenarios retrieved.
- Key finding: RAG amplifies crisis severity vs. Rule via historical panic memory.

### §3.4 RagLLMDistressedBuyer
- RRI improves vs. LLM: retrieved Paulson/Tepper case studies anchor better entry timing.
- Expect RRI = 0.30–0.70 (vs. Rule 0.20–0.60).

### §3.5 RagLLMRegulator
- TARP/bailout retrieval anchors intervention size at 3000–5000 units.
- Effective rescue_probability higher than Rule's stochastic 0.30.

---

## §4 Expected Ranges (Rag vs. Rule Baseline)

| Metric | Rag Expected Range | vs. Rule | Basis                                       |
|--------|--------------------|----------|---------------------------------------------|
| BBI    | 0.08–0.28          | Higher   | Retrieved CDO overvaluation literature      |
| CII    | 0.12–0.45          | Higher   | Retrieved crisis panic cases                |
| FSI    | 2–10 rounds        | Longer   | Historical leverage cascade memory          |
| RRI    | 0.25–0.70          | Higher   | Retrieved bailout data anchors intervention |
| OSP    | 0.60–0.92          | Similar  | Origination history retrieval               |
| WDI    | 0.12–0.35          | Higher   | Deeper crisis → greater wealth transfer     |

## §5 References

Metric definitions are inherited from `analysis-bases.md §2`; RAG investor roles
trace to `simulation-bases.md §4.1-§4.5`.

## §6 Cross-Variant Comparison

Compare RAG against RuleLLM to measure the marginal effect of retrieved
financial-crisis knowledge.

## §7 Quality Checks

- Confirm the run completed 200 configured rounds.
- Confirm RAG assets and embedding configuration were available.
- Confirm `{rag_context}` was populated or explicitly replaced by the no-context marker.
- Audit parse failures, fallback holds, and retrieval-health records before acceptance.
