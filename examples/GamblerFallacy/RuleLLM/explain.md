# GamblerFallacy — RuleLLM Variant

## §1 Overview

The RuleLLM variant implements the Gambler's Fallacy simulation with rule-embedded LLM reasoning. The embedded rules anchor both biased agents to threshold 0.02 and the same direction logic as Rule; the LLM provides contextualisation and may express some of the §4.1 vs. §4.2 differentiation through quantity modulation.

| Aspect             | Detail                                                        |
|--------------------|---------------------------------------------------------------|
| Variant            | RuleLLM                                                       |
| Simulation         | GamblerFallacy                                                |
| Decision Mechanism | Rule-embedded LLM: system prompt encodes thresholds + persona |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                               |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                  |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)              |

---

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMStreakReversalTrader (`simulation-bases.md §4.1`)

| Theory Component                                | Implementation                                                                                                           |
|-------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Law of small numbers (Tversky & Kahneman, 1971) | System prompt embeds: "buy when deviation > 0.02; sell when deviation < -0.02; you believe a reversal is coming"         |
| Embedded threshold                              | `abs(deviation) > 0.02` anchors activation to Rule baseline                                                              |
| LLM contextualisation                           | LLM may modulate quantity based on perceived streak length — longer streak → smaller quantity (reversal expected sooner) |

### §2.2 RuleLLMHotHandTrader (`simulation-bases.md §4.2`)

| Theory Component                         | Implementation                                                                                                     |
|------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| Hot hand fallacy (Gilovich et al., 1985) | System prompt embeds: "buy when deviation > 0.02; sell when deviation < -0.02; you believe the streak continues"   |
| Embedded threshold                       | Identical threshold to §4.1; LLM provides opposite narrative framing                                               |
| LLM contextualisation                    | LLM may modulate quantity based on perceived streak strength — stronger streak → larger quantity (hot hand active) |

### §2.3 RuleLLMIndependentAssessor (`simulation-bases.md §4.3`)

| Theory Component                     | Implementation                                                                 |
|--------------------------------------|--------------------------------------------------------------------------------|
| Independence of events (Rabin, 2002) | System prompt embeds: "buy when deviation < -0.05; sell when deviation > 0.05" |
| Contrarian logic                     | Embedded contrarian direction; LLM explains statistical independence reasoning |

### §2.4 RuleLLMArbitrageur (`simulation-bases.md §4.4`)

| Theory Component                              | Implementation                                                        |
|-----------------------------------------------|-----------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | System prompt embeds: "exploit mispricing when abs(deviation) > 0.05" |
| Arbitrage logic                               | Same embedded threshold and direction as §4.3                         |

### §2.5 RuleLLMNoiseTrader (`simulation-bases.md §4.5`)

| Theory Component           | Implementation                                            |
|----------------------------|-----------------------------------------------------------|
| Noise trader (Black, 1986) | No embedded rule; LLM persona of uninformed retail trader |

---

## §3 RuleLLM-Specific Notes

- **SAR ≈ 1.0 expected**: Embedded direction rules mean §4.1 and §4.2 still buy/sell in same direction at default. LLM quantity modulation provides partial differentiation.
- **Near-Rule baseline**: RuleLLM expected to closely track Rule baseline for all metrics due to embedded thresholds.
- **Research value**: RuleLLM vs. LLM comparison shows the effect of rule constraints on bias expression.

---

## §4 Expected Ranges (RuleLLM Variant vs. Rule Baseline)

| Metric | RuleLLM Expected Range | Rule Baseline | Direction                                 |
|--------|------------------------|---------------|-------------------------------------------|
| GFI    | 0.02–0.08              | 0.02–0.08     | ≈ Similar                                 |
| SAR    | 0.8–1.2                | ≈ 1.0         | ≈ Similar (slight LLM quantity asymmetry) |
| HHM    | 140–480 shares         | 150–500       | ≈ Similar                                 |
| ACI    | 0.35–0.65              | 0.35–0.65     | ≈ Similar                                 |
| VAF    | 1.4–3.3                | 1.5–3.5       | ≈ Similar                                 |
| WDI    | 0.09–0.33              | 0.10–0.35     | ≈ Similar                                 |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity, LLM
parse/fallback rates, and rule-adherence patterns before accepting a sample.
