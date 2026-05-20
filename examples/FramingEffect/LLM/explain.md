# FramingEffect — LLM Variant

## §1 Overview

The LLM variant implements the Framing Effect simulation using large language model reasoning. Each investor class inherits from `LLMInvestor` and applies a persona-defining system prompt that encodes the behavioral bias described in `simulation-bases.md §4`. The framing effect emerges from LLM persona reasoning rather than deterministic thresholds — the LLM interprets market state and decides whether to buy, sell, or hold based on its injected personality and current market data.

| Aspect             | Detail                                           |
|--------------------|--------------------------------------------------|
| Variant            | LLM                                              |
| Simulation         | FramingEffect                                    |
| Decision Mechanism | LLM persona reasoning via system prompt          |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                  |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`     |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t) |

---

## §2 Theory → Implementation Mapping

### §2.1 LLMGainFrameFollower (`simulation-bases.md §4.1`)

| Theory Component                                        | Implementation                                                                                                                |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------|
| Prospect theory gain framing (Tversky & Kahneman, 1981) | System prompt: persona of a gain-frame-sensitive investor who interprets positive returns as confirmation of continuing gains |
| Momentum following on gain frame                        | Prompt encodes bias: "when price is rising, you feel compelled to buy to capture gains"                                       |
| Cognitive asymmetry                                     | LLM persona emphasises gain salience over loss salience; may exit positions less readily than Rule variant                    |

### §2.2 LLMLossFrameReactor (`simulation-bases.md §4.2`)

| Theory Component                                        | Implementation                                                                                                            |
|---------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Prospect theory loss framing (Tversky & Kahneman, 1981) | System prompt: persona of a loss-averse investor who reacts dramatically to negative return framing                       |
| Risk-seeking in loss domain                             | Prompt encodes: "when facing losses, you take aggressive action to recover, sometimes buying more aggressively on dips"   |
| LLM differentiation from §4.1                           | Unlike Rule variant, LLM variant can express distinct gain vs. loss response asymmetry through natural language reasoning |

### §2.3 LLMFrameInvariantTrader (`simulation-bases.md §4.3`)

| Theory Component                                 | Implementation                                                                                                        |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Frame-invariant rationality (Levin et al., 1998) | System prompt: rational persona that explicitly evaluates equivalent outcomes identically regardless of presentation  |
| Contrarian reasoning                             | Prompt instructs: "you identify when prices deviate significantly from fundamental value and trade against the crowd" |
| LLM advantage                                    | Can articulate reasoning chain explicitly; may detect framing in market context that Rule threshold misses            |

### §2.4 LLMArbitrageFramer (`simulation-bases.md §4.4`)

| Theory Component                    | Implementation                                                                                                            |
|-------------------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Framing arbitrage (Kuhberger, 1998) | System prompt: sophisticated arbitrageur persona who explicitly recognises framing-induced mispricing                     |
| Exploit mispricing                  | Prompt encodes profit motive: "you look for cases where equivalent information has been framed differently by the market" |
| LLM reasoning advantage             | Can reason about framing context explicitly — may outperform Rule variant on complex market states                        |

### §2.5 LLMNoiseTrader (`simulation-bases.md §4.5`)

| Theory Component                 | Implementation                                                                                                 |
|----------------------------------|----------------------------------------------------------------------------------------------------------------|
| Noise trader model (Black, 1986) | System prompt: uninformed retail investor persona with no systematic strategy                                  |
| Stochastic behavior              | Prompt encodes randomness: "you trade based on gut feeling and news snippets, without systematic analysis"     |
| LLM vs. Rule difference          | LLM noise trader may exhibit higher autocorrelation in decisions than Rule (which uses pure `random.random()`) |

---

## §3 LLM-Specific Notes

- **Decision stochasticity**: LLM responses vary across runs even for identical market states (due to LLM temperature > 0). Cross-seed variance is higher than Rule variant.
- **Reasoning transparency**: Each LLM decision includes a `<analysis>` tag with the agent's reasoning, enabling qualitative analysis of framing behavior.
- **Prompt-coded thresholds**: LLM variant does not use explicit `if abs(deviation) > 0.02` conditions. Activation depends on prompt framing and LLM interpretation.
- **Potential for nuance**: LLM agents may express gradations of framing bias (e.g., "slightly bullish") that Rule agents cannot represent with binary buy/sell.
- **Market broadcast**: Identical to Rule variant — agents receive `price`, `fundamental`, `deviation`, `round`.

---

## §4 Expected Ranges (LLM Variant vs. Rule Baseline)

| Metric          | LLM Expected Range | Rule Baseline | Direction      | Basis                                                      |
|-----------------|--------------------|---------------|----------------|------------------------------------------------------------|
| FDI             | 0.015–0.07         | 0.02–0.08     | Slightly lower | LLM reasoning may moderate extreme deviations              |
| FPI             | 2–10 rounds        | 3–12          | Shorter        | LLM occasionally breaks cascade through nuanced reasoning  |
| ACC (§4.1+§4.2) | 40–65%             | 50–70%        | Lower          | LLM biased agents less consistently directional            |
| VAF             | 1.2–3.0            | 1.5–3.5       | Slightly lower | LLM variability dampens systematic amplification           |
| OWP             | 0.03–0.18          | 0.05–0.20     | Lower          | LLM biased agents sometimes reason their way out of losses |
| WDI             | 0.08–0.25          | 0.10–0.30     | Lower          | Less systematic wealth transfer in stochastic LLM regime   |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity, LLM
parse/fallback rates, and agent-level contribution patterns before accepting a
sample.
