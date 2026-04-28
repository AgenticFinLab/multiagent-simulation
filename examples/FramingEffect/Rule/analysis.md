# FramingEffect — Rule Variant Analysis

## §1 Overview

This document specifies the analysis methodology for the **Rule variant** of the FramingEffect simulation. All metric definitions are sourced from `analysis-bases.md §2`. This file maps each metric to its Python function, documents Rule-specific behaviors, and provides expected ranges for the deterministic rule-based implementation.

| Aspect             | Detail                  |
|--------------------|-------------------------|
| Variant            | Rule                    |
| Simulation         | FramingEffect           |
| Analysis basis     | `../analysis-bases.md`  |
| Decision mechanism | Threshold rules on δ(t) |

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

## §3 Rule-Specific Notes

- **GainFrameFollower (§4.1)**: In the Rule variant, this agent activates at every |δ| > 0.02 without memory — purely reactive. ACC contribution from §4.1 reflects strict proportionality to deviation magnitude.
- **LossFrameReactor (§4.2)**: Identical logic to §4.1 at default extras; ACC splits evenly between §4.1 and §4.2 in the Rule baseline. Non-default `loss_weight`/`gain_weight` calibration would break this symmetry.
- **FrameInvariantTrader (§4.3)**: Contrarian at |δ| > 0.05; deterministic correction. VAF is partially dampened by this agent's systematic opposition.
- **ArbitrageFramer (§4.4)**: Identical logic to §4.3 at default extras; combined with §4.3, provides double correction force. OWP measures the wealth penalty on §4.1+§4.2 due to this combined rational pressure.
- **NoiseTrader (§4.5)**: 30% random trade probability; adds stochastic background. Contributes ≈15–20% of total volume but with zero directional bias — does not systematically affect FDI.
- **Determinism**: Rule variant is fully deterministic for a fixed random seed (only NoiseTrader uses `random`). Cross-seed variance is entirely from NoiseTrader randomness.

---

## §4 Expected Ranges (Rule Variant)

| Metric          | Rule Expected Range | vs. Calibration Target | Interpretation                                                                     |
|-----------------|---------------------|------------------------|------------------------------------------------------------------------------------|
| FDI             | 0.02–0.08           | Target: 0.02–0.08      | Mean absolute deviation; framing bias active at typical deviation levels           |
| FPI             | 3–12 rounds         | Target: 3–12           | Persistence sustained by biased agent reinforcement before rational correction     |
| ACC (§4.1+§4.2) | 50–70%              | Target: 50–70%         | Biased agents dominate cascade-phase volume; rational agents correct later         |
| VAF             | 1.5–3.5             | Target: 1.5–3.5        | Systematic bias amplifies volatility during framing-active rounds                  |
| OWP             | 0.05–0.20           | Target: 0.05–0.20      | Biased agents lose 5–20% of wealth to rational agents over full simulation         |
| WDI             | 0.10–0.30           | Target: 0.10–0.30      | Moderate Gini; rational agents outperform but do not eliminate biased agent wealth |
