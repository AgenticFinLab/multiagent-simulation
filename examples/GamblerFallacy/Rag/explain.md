# GamblerFallacy — Rag Variant

## §1 Overview

The Rag variant implements the Gambler's Fallacy simulation using RAG-augmented LLM reasoning. Retrieved documents about gambling studies, streak statistics, and historical market episodes reinforce each agent's behavioral bias. Unlike Rule/RuleLLM, the Rag variant can potentially retrieve evidence that either reinforces or challenges each agent's streak beliefs.

| Aspect             | Detail                                                         |
|--------------------|----------------------------------------------------------------|
| Variant            | Rag                                                            |
| Simulation         | GamblerFallacy                                                 |
| Decision Mechanism | RAG-augmented LLM: retrieved documents + persona system prompt |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                   |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)               |

---

## §2 Theory → Implementation Mapping

### §2.1 RagLLMStreakReversalTrader (`simulation-bases.md §4.1`)

| Theory Component                                | Implementation                                                                                             |
|-------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| Law of small numbers (Tversky & Kahneman, 1971) | System prompt: reversal-expecting persona; RAG retrieves Tversky & Kahneman (1971) on law of small numbers |
| Historical reinforcement                        | Retrieved documents on gambler's fallacy cases (e.g., casino streak data) reinforce reversal expectation   |
| Potential moderation                            | If retrieved documents show streak persistence (hot hand evidence), may reduce reversal conviction         |

### §2.2 RagLLMHotHandTrader (`simulation-bases.md §4.2`)

| Theory Component                         | Implementation                                                                                       |
|------------------------------------------|------------------------------------------------------------------------------------------------------|
| Hot hand fallacy (Gilovich et al., 1985) | System prompt: continuation-expecting persona; RAG retrieves Gilovich et al. (1985) hot hand studies |
| Historical reinforcement                 | Retrieved momentum trading studies reinforce streak-following; NBA shooting data analogy             |
| RAG differentiation                      | Different retrieval corpus from §4.1 creates genuine behavioral differentiation                      |

### §2.3 RagLLMIndependentAssessor (`simulation-bases.md §4.3`)

| Theory Component                       | Implementation                                                                   |
|----------------------------------------|----------------------------------------------------------------------------------|
| Statistical independence (Rabin, 2002) | System prompt: rational persona; RAG retrieves statistical independence evidence |
| Evidence-based contrarian              | Retrieved regression-to-mean studies strengthen contrarian conviction            |

### §2.4 RagLLMArbitrageur (`simulation-bases.md §4.4`)

| Theory Component                              | Implementation                                                              |
|-----------------------------------------------|-----------------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | System prompt: arbitrageur; RAG retrieves historical arbitrage case studies |
| Historical grounding                          | Retrieved examples of streak-driven mispricings and correction timelines    |

### §2.5 RagLLMNoiseTrader (`simulation-bases.md §4.5`)

| Theory Component           | Implementation                                                     |
|----------------------------|--------------------------------------------------------------------|
| Noise trader (Black, 1986) | System prompt: uninformed retail; RAG retrieves random market news |

---

## §3 Rag-Specific Notes

- **Retrieval differentiation**: §4.1 and §4.2 retrieve from different document corpora (reversal vs. continuation evidence), creating genuine behavioral differentiation — key advantage over Rule variant.
- **SAR divergence expected**: RAG retrieval reinforces each bias independently; §4.1 may show SAR < 1 while §4.2 shows SAR > 1.
- **HHM vs. Rag**: If retrieved documents reinforce both biases simultaneously, HHM may be similar to Rule. If they differentiate (as expected), HHM may be lower due to partial cancellation.

---

## §4 Expected Ranges (Rag Variant vs. Rule Baseline)

| Metric | Rag Expected Range | Rule Baseline | Direction               | Basis                                                            |
|--------|--------------------|---------------|-------------------------|------------------------------------------------------------------|
| GFI    | 0.018–0.08         | 0.02–0.08     | Similar/slightly lower  | Opposing bias reinforcement partially cancels                    |
| SAR    | 0.4–2.0            | ≈ 1.0         | More variable           | Retrieved evidence reinforces opposite biases independently      |
| HHM    | 120–450 shares     | 150–500       | Slightly lower          | Partial cancellation when biases oppose                          |
| ACI    | 0.35–0.70          | 0.35–0.65     | Similar/slightly higher | Retrieved mean-reversion evidence strengthens rational agents    |
| VAF    | 1.3–3.2            | 1.5–3.5       | Slightly lower          | Bias cancellation reduces net volatility amplification           |
| WDI    | 0.08–0.30          | 0.10–0.35     | Slightly lower          | Less systematic exploitation with opposing Rag-reinforced biases |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity,
retrieval health, LLM parse/fallback rates, and agent-level contribution
patterns before accepting a sample.
