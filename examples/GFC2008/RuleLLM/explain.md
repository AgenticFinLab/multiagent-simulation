# GFC2008 — RuleLLM Variant

## §1 Overview

| Aspect             | Detail                                         |
|--------------------|------------------------------------------------|
| Variant            | RuleLLM                                        |
| Simulation         | GFC2008                                        |
| Decision Mechanism | Rule screening + LLM commentary                |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`   |
| Price Model        | `P(t+1) = P(t) + λ·NetDemand + γ·(F−P(t)) + ε` |

---

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMMBSOriginator (`simulation-bases.md §4.1`)
| Theory Component              | Implementation                                                                  |
|-------------------------------|---------------------------------------------------------------------------------|
| Originate-to-distribute model | Rule layer: `sell_qty = int(abs(position) * origination_rate)`                  |
| LLM commentary                | LLM provides narrative on origination pace; may override quantity within bounds |
| Hybrid stability              | Rule prevents full LLM freestyle — origination floor maintained                 |

### §2.2 RuleLLMRatingAgency (`simulation-bases.md §4.2`)
| Theory Component     | Implementation                                                             |
|----------------------|----------------------------------------------------------------------------|
| Issuer-pays conflict | Rule layer: `perceived_fundamental = fundamental * (1 + overrating_bias)`  |
| LLM reasoning        | LLM elaborates on rating decision; may adjust buy threshold interpretation |
| Conservative bound   | Rule threshold (price < perceived_fundamental × 0.95) acts as hard guard   |

### §2.3 RuleLLMLeveragedInvestor (`simulation-bases.md §4.3`)
| Theory Component | Implementation                                                                |
|------------------|-------------------------------------------------------------------------------|
| Leverage cycle   | Rule layer: fire-sale trigger at `deviation < -margin_call_trigger`           |
| LLM commentary   | LLM provides risk assessment narrative; quantity modulated within Rule bounds |
| Reduced panic    | LLM reasoning may modulate sell quantity downward vs. pure Rule fire sale     |

### §2.4 RuleLLMDistressedBuyer (`simulation-bases.md §4.4`)
| Theory Component     | Implementation                                                             |
|----------------------|----------------------------------------------------------------------------|
| Deep discount buying | Rule layer: `deviation < -discount_threshold` triggers 30% cash deployment |
| LLM commentary       | LLM adds recovery timing reasoning; may adjust deployment fraction         |
| Better entry timing  | LLM context awareness allows more strategic capital deployment             |

### §2.5 RuleLLMRegulator (`simulation-bases.md §4.5`)
| Theory Component      | Implementation                                                            |
|-----------------------|---------------------------------------------------------------------------|
| Systemic risk monitor | Rule layer: threshold check + `rescue_probability`                        |
| LLM commentary        | LLM provides policy rationale; may increase intervention probability      |
| Hybrid intervention   | Rule stochasticity remains but LLM narrative may bias toward intervention |

---

## §3 RuleLLM-Specific Notes

- **Rule as safety net**: Rule thresholds prevent LLM from ignoring crisis signals entirely.
- **LLM as modulator**: Within rule-permitted bounds, LLM adjusts quantity and timing — produces intermediate metrics between Rule and LLM extremes.
- **Expected CII**: Lower than pure Rule because LLM-modulated fire sales are more restrained.

---

## §4 Expected Ranges (RuleLLM vs. Rule Baseline)

| Metric | RuleLLM Expected Range | vs. Rule | Basis                                         |
|--------|------------------------|----------|-----------------------------------------------|
| BBI    | 0.05–0.22              | Similar  | Rule threshold preserved; LLM minor inflation |
| CII    | 0.08–0.30              | Lower    | LLM moderates fire-sale quantity              |
| FSI    | 2–7 rounds             | Similar  | Rule trigger preserved; LLM may shorten       |
| RRI    | 0.25–0.65              | Higher   | LLM boosts Regulator intervention             |
| OSP    | 0.60–0.90              | Similar  | Rule origination rate dominates               |
| WDI    | 0.10–0.28              | Similar  | Crisis arc similar to Rule                    |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity, LLM
parse and retry rates, and rule-adherence patterns before acceptance.

## §6 Running Instructions

```bash
python examples/GFC2008/RuleLLM/run_gfc2008_rulellm.py \
  -c configs/GFC2008/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM agents should preserve the Rule variant's directional triggers while
allowing language-mediated reasoning and quantity variation.

## §8 Cross-Variant Role

RuleLLM isolates the effect of LLM reasoning when each agent receives explicit
decision rules.

## §9 Implementation Traceability

System prompts must contain `== PERSONA ==` and `== DECISION RULES ==` sections;
order parsing must emit valid trading payloads.
