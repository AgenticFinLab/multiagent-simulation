# GFC2008 — Rule Variant

## §1 Overview

| Aspect             | Detail                                         |
|--------------------|------------------------------------------------|
| Variant            | Rule                                           |
| Simulation         | GFC2008                                        |
| Decision Mechanism | Deterministic rule-based                       |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`   |
| Price Model        | `P(t+1) = P(t) + λ·NetDemand + γ·(F−P(t)) + ε` |

---

## §2 Theory → Implementation Mapping

### §2.1 MBSOriginator (`simulation-bases.md §4.1`)
| Theory Component              | Implementation                                                                                 |
|-------------------------------|------------------------------------------------------------------------------------------------|
| Originate-to-distribute model | `sell_qty = int(abs(position) * origination_rate)`; sells at constant rate regardless of price |
| Lax screening                 | No threshold check on price vs. fundamental — sells unconditionally while `position > 0`       |
| Supply pressure               | Steady sell orders create downward supply pressure during bubble deflation                     |

### §2.2 RatingAgency (`simulation-bases.md §4.2`)
| Theory Component     | Implementation                                                                            |
|----------------------|-------------------------------------------------------------------------------------------|
| Issuer-pays conflict | `perceived_fundamental = fundamental * (1 + overrating_bias)`                             |
| Inflated buy signal  | Buys when `price < perceived_fundamental * 0.95`; `buy_qty = min(300, int(cash / price))` |
| Bubble inflation     | Demand at overinflated price supports above-fundamental prices                            |

### §2.3 LeveragedInvestor (`simulation-bases.md §4.3`)
| Theory Component      | Implementation                                                                    |
|-----------------------|-----------------------------------------------------------------------------------|
| Leverage cycle        | Holds large initial position; forced sell when `deviation < -margin_call_trigger` |
| Fire sale             | `fire_sale_qty = int(abs(position) * 0.5)`; sells 50% of position per trigger     |
| Cascade amplification | Fire sales drive price further down, triggering further margin calls              |

### §2.4 DistressedBuyer (`simulation-bases.md §4.4`)
| Theory Component     | Implementation                                                                              |
|----------------------|---------------------------------------------------------------------------------------------|
| Deep discount buying | Buys when `deviation < -discount_threshold`; `buy_qty = min(1000, int(cash * 0.3 / price))` |
| Capital deployment   | Deploys 30% of cash per trigger round — partial stabilization                               |
| Opportunistic role   | Enters only at steep discounts, not before panic bottom                                     |

### §2.5 Regulator (`simulation-bases.md §4.5`)
| Theory Component           | Implementation                                                            |
|----------------------------|---------------------------------------------------------------------------|
| Systemic risk monitor      | Triggers when `deviation < -intervention_threshold`                       |
| Probabilistic intervention | `if random.random() < rescue_probability: buy(rescue_size)` — stochastic bailout |
| Partial rescue             | Bounded 500-unit rescue; incomplete correction mirrors real policy delays |

---

## §3 Rule-Specific Notes

- **Two-phase crisis pattern**: RatingAgency buys → bubble (BBI > 0); MBSOriginator sells + LeveragedInvestor fire sales → crash (CII large negative).
- **Cascade trigger sequence**: LeveragedInvestor fires when `deviation < -0.10` (`margin_call_trigger`); DistressedBuyer activates at `deviation < -0.20`; Regulator at `deviation < -0.50`.
- **Stochastic Regulator**: `rescue_probability = 0.6` with `rescue_size = 500` means intervention is relatively likely in extreme stress but each order is bounded.

---

## §4 Expected Ranges (Rule Baseline)

| Metric | Rule Expected Range | Basis                                                        |
|--------|---------------------|--------------------------------------------------------------|
| BBI    | 0.05–0.20           | overrating_bias = 0.20 → ~15–18% sustained overvaluation     |
| CII    | 0.10–0.35           | fire-sale cascade depth; margin_call_trigger = 0.10          |
| FSI    | 2–8 rounds          | Duration of LeveragedInvestor fire-sale rounds               |
| RRI    | 0.20–0.60           | Partial stabilization by DistressedBuyer + Regulator         |
| OSP    | 0.60–0.90           | MBSOriginator origination fraction of total sell volume      |
| WDI    | 0.10–0.30           | Wealth concentration from DistressedBuyer buying at discount |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity, and
crisis-phase patterns before acceptance.

## §6 Running Instructions

```bash
python examples/GFC2008/Rule/run_gfc2008.py \
  -c configs/GFC2008/Rule/simulation.yml
```

## §7 Expected Behavior

The Rule variant should produce deterministic bubble build-up, fire-sale
pressure, partial stabilizer response, and measurable wealth redistribution.

## §8 Cross-Variant Role

Rule output is the baseline for comparing persona-only LLM behavior, explicit
RuleLLM guidance, and RAG knowledge effects.

## §9 Implementation Traceability

Investor behavior maps to `simulation-bases.md §4.1-§4.5`; metrics map to
`analysis-bases.md §2`. No LLM calls are made in this variant.
