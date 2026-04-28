# FramingEffect — RuleLLM Variant

## §1 Overview

The RuleLLM variant implements the Framing Effect simulation using LLM reasoning with embedded rule constraints. Each investor inherits from `RuleLLMInvestor` and receives a system prompt that explicitly encodes the quantitative thresholds from `Rule/players.py` alongside the behavioral persona from `simulation-bases.md §4`. The LLM contextualises and reasons about market state, but its decision space is anchored by the embedded rules — it cannot fully override the thresholds.

| Aspect             | Detail                                                        |
|--------------------|---------------------------------------------------------------|
| Variant            | RuleLLM                                                       |
| Simulation         | FramingEffect                                                 |
| Decision Mechanism | Rule-embedded LLM: system prompt encodes thresholds + persona |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                               |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`                  |
| Price Model        | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)              |

---

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMGainFrameFollower (`simulation-bases.md §4.1`)

| Theory Component                                        | Implementation                                                                                     |
|---------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Prospect theory gain framing (Tversky & Kahneman, 1981) | System prompt embeds: "when abs(deviation) > 0.02, you are compelled to act based on gain framing" |
| Momentum following on gain frame                        | Embedded rule: "buy when deviation > 0.02; sell when deviation < -0.02; otherwise hold"            |
| LLM contextualisation                                   | LLM reasons about why the gain frame compels action; may adjust quantity within allowed range      |

### §2.2 RuleLLMLossFrameReactor (`simulation-bases.md §4.2`)

| Theory Component                                        | Implementation                                                                                        |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Prospect theory loss framing (Tversky & Kahneman, 1981) | System prompt embeds: "react strongly to loss-framed information; threshold is abs(deviation) > 0.02" |
| Differentiation from §4.1                               | RuleLLM can express loss_weight vs. gain_weight asymmetry through LLM reasoning about magnitude       |
| LLM override constraint                                 | LLM cannot override direction (buy/sell) but may modulate quantity based on narrative reasoning       |

### §2.3 RuleLLMFrameInvariantTrader (`simulation-bases.md §4.3`)

| Theory Component                                 | Implementation                                                                                |
|--------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Frame-invariant rationality (Levin et al., 1998) | System prompt embeds: "activate contrarian trade when abs(deviation) > 0.05"                  |
| Contrarian reasoning                             | Embedded: "buy when deviation < -0.05 (undervalued); sell when deviation > 0.05 (overvalued)" |
| LLM contextualisation                            | LLM can explain the rational basis for the contrarian trade; adds reasoning transparency      |

### §2.4 RuleLLMArbitrageFramer (`simulation-bases.md §4.4`)

| Theory Component                    | Implementation                                                                                |
|-------------------------------------|-----------------------------------------------------------------------------------------------|
| Framing arbitrage (Kuhberger, 1998) | System prompt embeds: "exploit framing mispricing when abs(deviation) > 0.05"                 |
| Arbitrage logic                     | Embedded rule identical to §4.3; LLM contextualises as framing arbitrage opportunity          |
| LLM advantage                       | Can explain the framing mechanism in output; enables qualitative audit of arbitrage reasoning |

### §2.5 RuleLLMNoiseTrader (`simulation-bases.md §4.5`)

| Theory Component                 | Implementation                                                                     |
|----------------------------------|------------------------------------------------------------------------------------|
| Noise trader model (Black, 1986) | System prompt: uninformed persona; no embedded thresholds                          |
| Stochastic behavior              | LLM may exhibit less pure randomness than Rule variant; slight narrative coherence |

---

## §3 RuleLLM-Specific Notes

- **Rule anchoring**: Embedded thresholds prevent extreme LLM deviation — RuleLLM should produce FDI and FPI closer to Rule baseline than pure LLM variant.
- **Quantity flexibility**: LLM may choose quantity within `[0, cap]` range; the size formula `int(|δ| × 5000)` is embedded as guidance but not a hard constraint.
- **Reasoning output**: Each decision includes LLM reasoning trace; enables qualitative analysis of how agents articulate framing logic.
- **Cross-run consistency**: More consistent than LLM variant due to embedded rules; less consistent than Rule due to LLM stochasticity.

---

## §4 Expected Ranges (RuleLLM Variant vs. Rule Baseline)

| Metric          | RuleLLM Expected Range | Rule Baseline | Direction | Basis                                                           |
|-----------------|------------------------|---------------|-----------|-----------------------------------------------------------------|
| FDI             | 0.02–0.08              | 0.02–0.08     | ≈ Similar | Embedded thresholds anchor activation to Rule levels            |
| FPI             | 3–11 rounds            | 3–12          | ≈ Similar | Embedded rules maintain cascade duration; slight LLM shortening |
| ACC (§4.1+§4.2) | 48–68%                 | 50–70%        | ≈ Similar | Rule anchoring maintains biased agent volume share              |
| VAF             | 1.4–3.3                | 1.5–3.5       | ≈ Similar | Slight reduction from LLM quantity modulation                   |
| OWP             | 0.04–0.19              | 0.05–0.20     | ≈ Similar | Rule anchoring maintains systematic wealth penalty              |
| WDI             | 0.09–0.28              | 0.10–0.30     | ≈ Similar | Near-Rule inequality distribution                               |
