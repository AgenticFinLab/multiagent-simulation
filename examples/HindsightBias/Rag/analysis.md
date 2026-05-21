# HindsightBias Rag — Analysis Guide

## §1 Analysis Objectives

The Rag variant analysis measures the **self-correction effect** of behavioral finance literature on hindsight bias dynamics. The core research question: does providing biased agents with literature documenting their own bias reduce HBI, and does providing rational agents with arbitrage literature improve NCE?

1. Quantify HBI reduction vs. Rule baseline (self-correction signature)
2. Measure NCE improvement (rational correction efficiency with literature support)
3. Assess OBI moderation (OutcomeLearner cost literature may reduce bull-phase dominance)
4. Document the "bias acknowledgment" phenomenon: Rag biased agents may explicitly cite bias literature

Analysis objectives:
- HBI target 0.015–0.05: lowest across all variants (self-correction expected)
- NCE target 0.45–0.75: highest across all variants (literature-supported correction)
- OBI in 0.7–1.2: moderated bull-phase dominance
- VAF in 1.2–2.8: lower due to self-correction of biased agents
- OWP in 0.02–0.18: smallest wealth penalty (biased agents better calibrated)
- WDI in 0.07–0.22: lowest inequality (reduced wealth transfer)

---

## §2 Metric → Function Mapping

| Metric | Full Name                       | analysis-bases.md | Python Function                     | Primary Input                  |
|--------|---------------------------------|-------------------|-------------------------------------|--------------------------------|
| HBI    | Hindsight Bias Index            | §2.1              | `hindsight_bias_index()`            | price_history, fundamental     |
| OBI    | Outcome Bias Index              | §2.2              | `outcome_bias_index()`              | price_history, fundamental     |
| NCE    | Narrative Correction Efficiency | §2.3              | `narrative_correction_efficiency()` | dev_history                    |
| VAF    | Volatility Amplification Factor | §2.4              | `volatility_amplification_factor()` | price_history, dev_history     |
| OWP    | Overconfidence Wealth Penalty   | §2.5              | `overconfidence_wealth_penalty()`   | biased_wealth, rational_wealth |
| WDI    | Wealth Distribution Index       | §2.6              | `wealth_distribution_index()`       | agent_wealth                   |

All functions defined in `Rag/analysis.py`. Inputs sourced from simulation output JSON.

---

## §3 Rag-Specific Notes

- **Knowledge base composition is critical**: If the knowledge base contains primarily bias-documenting papers (Fischhoff 1975, Roese & Vohs 2012), self-correction should be strong — HBI lower than LLM. If it contains momentum/trend papers, HBI may be higher than expected. Document KB composition when reporting results.
- **Bias acknowledgment tracking**: Monitor whether biased agent (§4.1, §4.2) LLM responses include phrases like "I recognize this may be hindsight bias" — this is the key research signal. Count acknowledgment frequency across seeds.
- **NCE is the key diagnostic**: Rag NCE > Rule NCE confirms that retrieved correction literature is improving rational agent performance. NCE = Rag confirms hypothesis.
- **OBI moderation**: If RAG retrieves Barber & Odean (2000) overtrading cost evidence for OutcomeLearner, OBI should decrease toward 1.0. If OBI remains > 1.2, the KB is not surfacing cost evidence adequately.
- **Multi-seed averaging required**: Run ≥5 seeds; report mean ± std and document which papers were retrieved most frequently.

---

## §4 Expected Ranges

| Metric | Rag Expected | vs. Rule | vs. LLM | Notes                                           |
|--------|--------------|----------|---------|-------------------------------------------------|
| HBI    | 0.015–0.05   | Lower    | Lower   | Self-correction from retrieved bias literature  |
| OBI    | 0.7–1.2      | Lower    | Lower   | Cost evidence reduces attribution asymmetry     |
| NCE    | 0.45–0.75    | Higher   | Higher  | Literature-supported rational correction        |
| VAF    | 1.2–2.8      | Lower    | Similar | Biased agent self-correction reduces volatility |
| OWP    | 0.02–0.18    | Lower    | Lower   | Less systematic bias exploitation               |
| WDI    | 0.07–0.22    | Lower    | Lower   | Reduced wealth gap under self-correction        |

---

## §5 References

- `analysis-bases.md §2.1` — HBI definition, formula, interpretation
- `analysis-bases.md §2.2` — OBI definition, formula, interpretation
- `analysis-bases.md §2.3` — NCE definition, formula, interpretation
- `analysis-bases.md §2.4` — VAF definition, formula, interpretation
- `analysis-bases.md §2.5` — OWP definition, formula, interpretation
- `analysis-bases.md §2.6` — WDI definition, formula, interpretation
- `simulation-bases.md §4.1–§4.5` — Investor parameter definitions
- `analysis-bases.md §5` — Cross-variant comparison table
- Fischhoff (1975) `doi:10.1037/0096-1523.1.3.288` — self-correction baseline
- Roese & Vohs (2012) `doi:10.1177/1745691612454303` — bias meta-analysis retrieved

## §6 Expected Results and Validation

The accepted RAG sample should complete 200 rounds with clean parse quality and usable retrieval context. Retrieval review should report success rate, fallback rate, and whether retrieved hindsight-bias literature moderates biased-agent behavior.

## §7 Visualization Catalogue

`Rag/analysis.py → main()` uses the standard analysis output contract:
`summary.json`, `00_investor_bids.png`, `01_hindsightbias_dynamics.png`,
`02_hindsightbias_analysis.png`, and `03_summary.png`. It also writes
`rag_stats.json` and adds `rag_knowledge_effect` to `summary.json`.
