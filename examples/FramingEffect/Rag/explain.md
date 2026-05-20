# FramingEffect — Rag Variant

## §1 Overview

The Rag variant implements the Framing Effect simulation using RAG-augmented LLM reasoning. Each investor inherits from `RagLLMInvestor` and retrieves relevant historical documents (framing effect studies, market episodes) to inform its decisions alongside the persona-defining system prompt. Retrieved documents may reinforce or moderate the framing bias described in `simulation-bases.md §4`.

| Aspect             | Detail                                                         |
|--------------------|----------------------------------------------------------------|
| Variant            | Rag                                                            |
| Simulation         | FramingEffect                                                  |
| Decision Mechanism | RAG-augmented LLM: retrieved documents + persona system prompt |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                   |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)               |

---

## §2 Theory → Implementation Mapping

### §2.1 RagLLMGainFrameFollower (`simulation-bases.md §4.1`)

| Theory Component                                        | Implementation                                                                                                        |
|---------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Prospect theory gain framing (Tversky & Kahneman, 1981) | System prompt: gain-frame-sensitive persona; RAG retrieves Tversky & Kahneman (1981) passages on gain framing         |
| Historical reinforcement                                | Retrieved documents provide historical examples of gain-frame-driven market behavior, reinforcing buying impulse      |
| RAG moderation                                          | If retrieved documents include crash evidence, agent may moderate buying — introducing framing correction via context |

### §2.2 RagLLMLossFrameReactor (`simulation-bases.md §4.2`)

| Theory Component                                        | Implementation                                                                                                       |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Prospect theory loss framing (Tversky & Kahneman, 1981) | System prompt: loss-frame-reactive persona; RAG retrieves loss aversion studies and panic selling episodes           |
| Historical grounding                                    | Retrieved panic-selling episodes (e.g., 1987 Black Monday, 2008 crash) reinforce loss-frame reaction                 |
| RAG differentiation from §4.1                           | Different retrieval corpus (loss vs. gain focused) creates empirical differentiation absent in Rule/RuleLLM variants |

### §2.3 RagLLMFrameInvariantTrader (`simulation-bases.md §4.3`)

| Theory Component                                 | Implementation                                                                                                           |
|--------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|
| Frame-invariant rationality (Levin et al., 1998) | System prompt: rational persona; RAG retrieves studies showing frame equivalence and rational valuation examples         |
| Evidence-based contrarian                        | Retrieved evidence strengthens contrarian resolve — historical data shows mean reversion after framing-driven deviations |
| RAG advantage                                    | Access to fundamental analysis documents enables more sophisticated valuation reasoning                                  |

### §2.4 RagLLMArbitrageFramer (`simulation-bases.md §4.4`)

| Theory Component                    | Implementation                                                                                                 |
|-------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Framing arbitrage (Kuhberger, 1998) | System prompt: arbitrageur persona; RAG retrieves framing arbitrage case studies and Kuhberger (1998) findings |
| Historical arbitrage grounding      | Retrieved documents provide examples of framing-induced mispricings and correction timelines                   |
| RAG advantage                       | Historical correction timelines from retrieved documents help calibrate timing of arbitrage entry              |

### §2.5 RagLLMNoiseTrader (`simulation-bases.md §4.5`)

| Theory Component                 | Implementation                                                                                                            |
|----------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Noise trader model (Black, 1986) | System prompt: uninformed retail persona; RAG retrieves random news snippets (generic market news)                        |
| RAG effect                       | Retrieved documents may introduce partial information that makes noise trader slightly less random than Rule/LLM variants |

---

## §3 Rag-Specific Notes

- **Retrieval corpus**: Rag variant retrieves from a domain knowledge base containing behavioral finance research, historical market episodes, and framing effect studies.
- **Retrieval reinforcement**: For biased agents (§4.1, §4.2), retrieved framing studies typically reinforce the bias, potentially increasing FDI and FPI vs. pure LLM variant.
- **Retrieval moderation**: For rational agents (§4.3, §4.4), retrieved evidence of mean reversion may strengthen contrarian conviction, increasing ACC for rational agents.
- **Corpus dependency**: Metric values depend on which documents are retrieved — if retrieval corpus is poor, Rag may resemble LLM variant.

---

## §4 Expected Ranges (Rag Variant vs. Rule Baseline)

| Metric          | Rag Expected Range | Rule Baseline | Direction       | Basis                                                             |
|-----------------|--------------------|---------------|-----------------|-------------------------------------------------------------------|
| FDI             | 0.02–0.09          | 0.02–0.08     | Slightly higher | Historical framing examples reinforce bias in retrieved documents |
| FPI             | 3–13 rounds        | 3–12          | Slightly longer | Retrieved cascade evidence reinforces persistence                 |
| ACC (§4.1+§4.2) | 50–72%             | 50–70%        | Slightly higher | Retrieval reinforces biased agent decisions                       |
| VAF             | 1.5–3.8            | 1.5–3.5       | Slightly higher | Biased retrieval amplifies cascade volatility slightly            |
| OWP             | 0.05–0.22          | 0.05–0.20     | Slightly higher | Biased agents lose more due to retrieval-reinforced errors        |
| WDI             | 0.10–0.32          | 0.10–0.30     | Slightly higher | More systematic wealth redistribution                             |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity,
retrieval health, LLM parse/fallback rates, and agent-level contribution
patterns before accepting a sample.
