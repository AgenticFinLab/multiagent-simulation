# GamblerFallacy — LLM Variant

## §1 Overview

The LLM variant implements the Gambler's Fallacy simulation using LLM persona reasoning. Each investor applies a persona-defining system prompt encoding the behavioral bias from `simulation-bases.md §4`. A key advantage of LLM over Rule: the two biased agents (§4.1 StreakReversalTrader, §4.2 HotHandTrader) can express genuinely opposite strategies through their prompt personas, unlike the default Rule variant where both have identical logic.

| Aspect             | Detail                                           |
|--------------------|--------------------------------------------------|
| Variant            | LLM                                              |
| Simulation         | GamblerFallacy                                   |
| Decision Mechanism | LLM persona reasoning via system prompt          |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                  |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`     |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t) |

---

## §2 Theory → Implementation Mapping

### §2.1 LLMStreakReversalTrader (`simulation-bases.md §4.1`)

| Theory Component                                | Implementation                                                                                            |
|-------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Law of small numbers (Tversky & Kahneman, 1971) | System prompt: "you believe that streaks must end; after several up moves you feel a reversal is overdue" |
| Gambler's fallacy reversal belief               | Prompt encodes: "the longer a streak has run, the more strongly you believe a reversal is imminent"       |
| LLM differentiation from §4.2                   | LLM can express genuine contrarian-to-streak behavior; SAR may deviate from 1.0 unlike Rule variant       |

### §2.2 LLMHotHandTrader (`simulation-bases.md §4.2`)

| Theory Component                         | Implementation                                                                                                  |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Hot hand fallacy (Gilovich et al., 1985) | System prompt: "you believe winning streaks persist; you follow momentum and buy rising prices"                 |
| Streak continuation belief               | Prompt encodes: "a stock that's been going up has momentum — ride the wave"                                     |
| LLM genuine differentiation              | Opposite psychological framing from §4.1; LLM produces divergent decisions, enabling meaningful SAR measurement |

### §2.3 LLMIndependentAssessor (`simulation-bases.md §4.3`)

| Theory Component                                | Implementation                                                                                        |
|-------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Independence of sequential events (Rabin, 2002) | System prompt: "each price move is statistically independent; you do not see patterns in random data" |
| Contrarian reasoning                            | Prompt: "when price deviates significantly from fundamental, you trade toward fair value"             |

### §2.4 LLMArbitrageur (`simulation-bases.md §4.4`)

| Theory Component                              | Implementation                                                                                        |
|-----------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | System prompt: arbitrageur who identifies and exploits streak-driven mispricing                       |
| Exploit bias                                  | Prompt: "you recognize that streak-believers create predictable mispricings that you can profit from" |

### §2.5 LLMNoiseTrader (`simulation-bases.md §4.5`)

| Theory Component           | Implementation                                                |
|----------------------------|---------------------------------------------------------------|
| Noise trader (Black, 1986) | System prompt: uninformed retail trader acting on gut feeling |

---

## §3 LLM-Specific Notes

- **Genuine bias differentiation**: Key LLM advantage — §4.1 and §4.2 can express genuinely opposite biases through prompt personas, unlike the Rule default where both are identical momentum followers.
- **SAR ≠ 1.0 expected**: LLM variant should produce SAR ≠ 1.0 because §4.1 (reversal) and §4.2 (continuation) should trade in opposite directions more often than the Rule default.
- **Stochasticity**: Multi-run averaging required; LLM variance is higher than Rule variant.

---

## §4 Expected Ranges (LLM Variant vs. Rule Baseline)

| Metric | LLM Expected Range | Rule Baseline | Direction               | Basis                                                         |
|--------|--------------------|---------------|-------------------------|---------------------------------------------------------------|
| GFI    | 0.015–0.07         | 0.02–0.08     | Lower                   | Opposite biases partially cancel; net deviation reduced       |
| SAR    | 0.5–1.8            | ≈ 1.0         | More variable           | Genuine bias differentiation: §4.1 and §4.2 trade differently |
| HHM    | 100–400 shares     | 150–500       | Lower                   | Partial cancellation reduces net demand magnitude             |
| ACI    | 0.35–0.70          | 0.35–0.65     | Similar/slightly higher | LLM rational agents may correct more efficiently              |
| VAF    | 1.2–3.0            | 1.5–3.5       | Lower                   | Reduced net bias effect; cancelling biases dampen volatility  |
| WDI    | 0.08–0.28          | 0.10–0.35     | Lower                   | Less systematic wealth redistribution with cancelling biases  |
