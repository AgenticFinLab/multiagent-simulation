# GFC2008 — LLM Variant

## §1 Overview

| Aspect             | Detail                                                        |
|--------------------|---------------------------------------------------------------|
| Variant            | LLM                                                           |
| Simulation         | GFC2008                                                       |
| Decision Mechanism | LLM-driven (LangChainAPIInference)                            |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                               |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                  |
| Price Model        | `P(t+1) = P(t) + λ·NetDemand + γ·(F−P(t)) + ε` (same as Rule) |

---

## §2 Theory → Implementation Mapping

### §2.1 LLMMBSOriginator (`simulation-bases.md §4.1`)
| Theory Component              | Implementation                                                                              |
|-------------------------------|---------------------------------------------------------------------------------------------|
| Originate-to-distribute model | System prompt: mortgage originator persona; LLM decides sell quantity based on market state |
| Lax screening bias            | Prompt encodes origination pressure: "maximize origination volume" narrative                |
| Supply shock                  | LLM output parsed for buy/sell/quantity via `parse_llm_response_with_thinking`              |

### §2.2 LLMRatingAgency (`simulation-bases.md §4.2`)
| Theory Component     | Implementation                                                              |
|----------------------|-----------------------------------------------------------------------------|
| Issuer-pays conflict | System prompt: rating analyst with inflated valuation bias                  |
| Inflated fundamental | Prompt encodes overrating tendency; LLM may override strict threshold logic |
| Variability          | LLM can express nuanced overrating: partial buy, conditional hold           |

### §2.3 LLMLeveragedInvestor (`simulation-bases.md §4.3`)
| Theory Component | Implementation                                                               |
|------------------|------------------------------------------------------------------------------|
| Leverage cycle   | System prompt: highly leveraged fund under margin pressure                   |
| Fire sale        | LLM may sell preemptively (before margin call) vs. Rule's strict threshold   |
| Dynamic fear     | Temperature > 0 adds panic variability — fire sales may be larger or smaller |

### §2.4 LLMDistressedBuyer (`simulation-bases.md §4.4`)
| Theory Component        | Implementation                                                          |
|-------------------------|-------------------------------------------------------------------------|
| Deep discount buying    | System prompt: distressed asset buyer; LLM evaluates discount depth     |
| Capital deployment      | LLM may deploy capital more opportunistically than fixed 30% Rule logic |
| Contrarian intelligence | LLM can reason about expected recovery — partial vs. full deployment    |

### §2.5 LLMRegulator (`simulation-bases.md §4.5`)
| Theory Component      | Implementation                                                                             |
|-----------------------|--------------------------------------------------------------------------------------------|
| Systemic risk monitor | System prompt: central bank / regulator persona                                            |
| Intervention decision | LLM reasons about systemic threshold; may intervene more/less than Rule's stochastic logic |
| Policy nuance         | Can express graduated response (moderate buy vs. large rescue)                             |

---

## §3 LLM-Specific Notes

- **Prompt-driven differentiation**: Unlike Rule where §4.1/§4.3/§4.4 share threshold logic, LLM expresses genuinely different reasoning per agent persona.
- **Temperature effect**: Higher temperature → more variable crisis arcs; lower temperature → more deterministic, closer to Rule behavior.
- **Fire sale timing**: LLMLeveragedInvestor may preemptively sell before reaching Rule threshold — produces earlier but potentially shallower CII.

---

## §4 Expected Ranges (LLM vs. Rule Baseline)

| Metric | LLM Expected Range | vs. Rule | Basis                                               |
|--------|--------------------|----------|-----------------------------------------------------|
| BBI    | 0.03–0.25          | Wider    | LLM RatingAgency may over- or under-inflate         |
| CII    | 0.05–0.40          | Wider    | Preemptive or delayed fire sales vs. Rule threshold |
| FSI    | 1–10 rounds        | Wider    | LLM fire-sale timing more variable                  |
| RRI    | 0.15–0.70          | Variable | LLM Regulator may intervene more actively           |
| OSP    | 0.50–0.90          | Similar  | Origination pattern LLM-modulated                   |
| WDI    | 0.08–0.35          | Similar  | Wealth transfer depends on crisis arc               |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity, LLM
parse and retry rates, and crisis-phase patterns before acceptance.

## §6 Running Instructions

```bash
python examples/GFC2008/LLM/run_gfc2008_llm.py \
  -c configs/GFC2008/LLM/simulation.yml
```

## §7 Expected Behavior

LLM agents should preserve the investor-role direction while allowing more
variation in timing, quantities, and crisis reasoning than the Rule baseline.

## §8 Cross-Variant Role

The LLM variant tests whether persona-only language agents reproduce GFC crisis
dynamics without explicit formula instructions.

## §9 Implementation Traceability

Prompts and parsed orders must remain consistent with `players.py`; acceptance
requires canonical order fields and clean parse-quality logs.
