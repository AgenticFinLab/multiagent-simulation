# FramingEffect — RuleLLM Variant Analysis

## §1 Overview

Analysis methodology for the **RuleLLM variant** of the FramingEffect simulation. Metric definitions from `../analysis-bases.md §2`. RuleLLM is expected to closely track the Rule baseline due to embedded threshold constraints, with mild LLM-induced variance.

| Aspect             | Detail                 |
|--------------------|------------------------|
| Variant            | RuleLLM                |
| Simulation         | FramingEffect          |
| Analysis basis     | `../analysis-bases.md` |
| Decision mechanism | Rule-embedded LLM      |

---

## §2 Metric → Function Mapping

| Metric                                | Function                                                                      | analysis-bases.md ref |
|---------------------------------------|-------------------------------------------------------------------------------|-----------------------|
| FDI (Framing Deviation Index)         | `framing_deviation_index(price_history, fundamental)`                         | §2.1                  |
| FPI (Framing Persistence Index)       | `framing_persistence_index(price_history, fundamental, threshold=0.02)`       | §2.2                  |
| ACC (Agent Contribution Coefficient)  | `agent_contribution_coefficient(trade_history, price_history, fundamental)`   | §2.3                  |
| VAF (Volatility Amplification Factor) | `volatility_amplification_factor(price_history, fundamental, threshold=0.02)` | §2.4                  |
| OWP (Overconfidence Wealth Penalty)   | `overconfidence_wealth_penalty(agent_states, final_price)`                    | §2.5                  |
| WDI (Wealth Distribution Index)       | `wealth_distribution_index(agent_states, final_price)`                        | §2.6                  |

---

## §3 RuleLLM-Specific Notes

- **RuleLLMGainFrameFollower (§4.1)**: Embedded threshold (0.02) ensures activation matches Rule variant; LLM quantity reasoning may produce slightly different trade sizes, affecting ACC marginally.
- **RuleLLMLossFrameReactor (§4.2)**: Unlike pure LLM, loss_weight vs. gain_weight differentiation is not purely prompt-driven — embedded rule threshold creates similar behavior to Rule baseline.
- **RuleLLMFrameInvariantTrader (§4.3)**: Embedded 0.05 threshold anchors contrarian activation; LLM reasoning adds explanation but does not change core direction logic.
- **RuleLLMArbitrageFramer (§4.4)**: Identical embedded rule to §4.3; combined they provide same corrective pressure as Rule variant.
- **RuleLLMNoiseTrader (§4.5)**: No embedded rule; most similar to pure LLM noise trader — may show slight narrative coherence in trades.
- **Research value**: RuleLLM vs. Rule comparison isolates the effect of LLM reasoning alone (with rules held constant). Differences in metrics represent pure LLM reasoning contribution.

---

## §4 Expected Ranges (RuleLLM Variant)

| Metric          | RuleLLM Expected Range | vs. Rule Baseline        | Interpretation                                             |
|-----------------|------------------------|--------------------------|------------------------------------------------------------|
| FDI             | 0.02–0.08              | ≈ Rule (±10%)            | Embedded thresholds anchor FDI to Rule level               |
| FPI             | 3–11 rounds            | ≈ Rule (−0 to −2 rounds) | Embedded rules maintain persistence; minor LLM shortening  |
| ACC (§4.1+§4.2) | 48–68%                 | ≈ Rule (−2 to −5%)       | Near-identical volume share; LLM quantity modulation small |
| VAF             | 1.4–3.3                | ≈ Rule (−0.1 to −0.2)    | Slight dampening from LLM quantity flexibility             |
| OWP             | 0.04–0.19              | ≈ Rule                   | Systematic wealth penalty maintained by embedded rules     |
| WDI             | 0.09–0.28              | ≈ Rule                   | Near-identical wealth distribution                         |
