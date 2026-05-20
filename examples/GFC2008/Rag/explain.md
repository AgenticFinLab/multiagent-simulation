# GFC2008 — Rag Variant

## §1 Overview

| Aspect             | Detail                                         |
|--------------------|------------------------------------------------|
| Variant            | Rag                                            |
| Simulation         | GFC2008                                        |
| Decision Mechanism | RAG-augmented LLM                              |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`   |
| Price Model        | `P(t+1) = P(t) + λ·NetDemand + γ·(F−P(t)) + ε` |

---

## §2 Theory → Implementation Mapping

### §2.1 RagLLMMBSOriginator (`simulation-bases.md §4.1`)
| Theory Component              | Implementation                                                                                          |
|-------------------------------|---------------------------------------------------------------------------------------------------------|
| Originate-to-distribute model | System prompt: mortgage originator; RAG retrieves Keys et al. (2010), subprime origination case studies |
| Lax screening                 | Retrieved documents reinforce origination-volume maximization bias                                      |
| Historical anchoring          | RAG may retrieve 2004–2006 origination ramp-up data, amplifying sell pressure                           |

### §2.2 RagLLMRatingAgency (`simulation-bases.md §4.2`)
| Theory Component     | Implementation                                                                                |
|----------------------|-----------------------------------------------------------------------------------------------|
| Issuer-pays conflict | System prompt: rating analyst; RAG retrieves Bolton et al. (2012), Moody's CDO rating history |
| Inflated fundamental | Retrieved historical overrating cases reinforce buy at inflated prices                        |
| BBI amplification    | Retrieved CDO overvaluation studies may push perceived_fundamental higher                     |

### §2.3 RagLLMLeveragedInvestor (`simulation-bases.md §4.3`)
| Theory Component        | Implementation                                                                        |
|-------------------------|---------------------------------------------------------------------------------------|
| Leverage cycle          | System prompt: leveraged fund; RAG retrieves LTCM collapse, Lehman deleveraging cases |
| Fire sale amplification | Retrieved panic-selling case studies may trigger larger or earlier sell decisions     |
| Crisis memory           | RAG knowledge of historical cascade dynamics may paradoxically accelerate fear        |

### §2.4 RagLLMDistressedBuyer (`simulation-bases.md §4.4`)
| Theory Component     | Implementation                                                                          |
|----------------------|-----------------------------------------------------------------------------------------|
| Deep discount buying | System prompt: distressed buyer; RAG retrieves Griffin & Xu (2009), Paulson trade cases |
| Entry timing         | Retrieved successful distressed trades reinforce conviction at deep discounts           |
| Better RRI           | RAG context about recovery timing may improve deployment efficiency                     |

### §2.5 RagLLMRegulator (`simulation-bases.md §4.5`)
| Theory Component         | Implementation                                                                   |
|--------------------------|----------------------------------------------------------------------------------|
| Systemic risk monitor    | System prompt: central bank; RAG retrieves TARP, Fed intervention records        |
| Intervention calibration | Retrieved bailout sizes anchor rescue quantity decisions                         |
| Policy confidence        | Historical intervention success/failure calibrates stochastic rescue probability |

---

## §3 Rag-Specific Notes

- **BBI amplification**: Retrieved CDO overvaluation studies may push BBI above Rule range.
- **CII deepening**: If RAG retrieves Lehman collapse data, LeveragedInvestor may fire-sell more aggressively.
- **RRI improvement**: Retrieved TARP/bailout data helps Regulator calibrate intervention size.
- **Corpus dependency**: All metrics shift toward retrieved historical GFC values — key confound for research.

---

## §4 Expected Ranges (Rag vs. Rule Baseline)

| Metric | Rag Expected Range | vs. Rule | Basis                                                      |
|--------|--------------------|----------|------------------------------------------------------------|
| BBI    | 0.08–0.28          | Higher   | Retrieved CDO overvaluation cases amplify rating inflation |
| CII    | 0.12–0.45          | Higher   | Retrieved panic-selling cases amplify fire sales           |
| FSI    | 2–10 rounds        | Longer   | Historical crisis memory prolongs leveraged selling        |
| RRI    | 0.25–0.70          | Higher   | Retrieved bailout data improves Regulator calibration      |
| OSP    | 0.60–0.92          | Similar  | Origination driven by historical origination cases         |
| WDI    | 0.12–0.35          | Higher   | Larger crisis → more wealth transfer                       |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity,
retrieval health, LLM parse/fallback rates, and crisis-phase patterns before
accepting a sample.

## §6 Running Instructions

```bash
python examples/GFC2008/Rag/run_gfc2008_rag.py \
  -c configs/GFC2008/Rag/simulation.yml
```

## §7 Expected Behavior

RAG agents should preserve RuleLLM-style decision rules while retrieved crisis
context changes confidence, intervention timing, and distressed-buyer behavior.

## §8 Cross-Variant Role

RAG isolates the marginal effect of external financial-crisis knowledge relative
to RuleLLM.

## §9 Implementation Traceability

The user prompt must inject `{rag_context}` or the no-context marker, and sample
acceptance requires retrieval-health and parse-quality review.
