# GameStopShortSqueeze — RuleLLM Variant

## §1 Overview

The RuleLLM variant implements the short squeeze with rule-embedded LLM reasoning. Embedded thresholds anchor squeeze mechanics (cover_threshold for §4.2, sell_threshold for §4.4, buy_pressure for §4.1) to Rule baseline while LLM provides contextualised decision reasoning.

| Aspect             | Detail                                       |
|--------------------|----------------------------------------------|
| Variant            | RuleLLM                                      |
| Simulation         | GameStopShortSqueeze                         |
| Decision Mechanism | Rule-embedded LLM                            |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` |

---

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMRetailCoordinated (`simulation-bases.md §4.1`)
| Theory Component      | Implementation                                                           |
|-----------------------|--------------------------------------------------------------------------|
| Social coordination   | Embedded: "buy when cash > price×50; use buy_pressure = 0.3 of cash"     |
| LLM contextualisation | LLM reasons about social momentum; may amplify buy_pressure in narrative |

### §2.2 RuleLLMShortSellerHF (`simulation-bases.md §4.2`)
| Theory Component | Implementation                                                                    |
|------------------|-----------------------------------------------------------------------------------|
| Forced covering  | Embedded: "cover 50% of short position when deviation > cover_threshold"          |
| LLM framing      | LLM explains covering decision; embedded rule prevents full avoidance of covering |

### §2.3 RuleLLMMarketMakerGamma (`simulation-bases.md §4.3`)
| Theory Component | Implementation                                                              |
|------------------|-----------------------------------------------------------------------------|
| Gamma hedging    | Embedded: "buy hedge_qty shares proportional to deviation × gamma_exposure" |

### §2.4 RuleLLMInstitutionalValue (`simulation-bases.md §4.4`)
| Theory Component          | Implementation                                   |
|---------------------------|--------------------------------------------------|
| Fundamental value selling | Embedded: "sell when deviation > sell_threshold" |

### §2.5 RuleLLMMomentumRetail (`simulation-bases.md §4.5`)
| Theory Component | Implementation                                             |
|------------------|------------------------------------------------------------|
| FOMO buying      | Embedded: "buy ≤50 shares when deviation > fomo_threshold" |

---

## §3 RuleLLM-Specific Notes

- **Near-Rule baseline**: Embedded thresholds anchor squeeze mechanics; SQI, PAR, IEP expected close to Rule baseline.
- **Quantity modulation**: LLM may adjust quantity within allowed range; SCD may vary slightly.

---

## §4 Expected Ranges (RuleLLM Variant)

| Metric | RuleLLM Expected Range | vs. Rule |
|--------|------------------------|----------|
| SQI    | 1.0–5.5                | ≈ Rule   |
| PAR    | 0.2–1.1                | ≈ Rule   |
| SCD    | 2–9 rounds             | ≈ Rule   |
| IEP    | Rounds 3–11            | ≈ Rule   |
| WTI    | 0.10–0.42              | ≈ Rule   |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity, LLM
parse/fallback rates, and rule-adherence patterns before accepting a sample.
