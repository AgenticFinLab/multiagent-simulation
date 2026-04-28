# HerdEffect LLM — Analysis Documentation

## §1 Analysis Objectives

This variant compares LLM-driven emergent herding against the deterministic Rule baseline. Objectives:
1. Measure how LLM narrative reasoning changes EMI magnitude and variance vs. Rule
2. Determine whether LLM ContrarianInvestor corrects overvaluation more or less effectively (REI)
3. Test if LLM AggressiveInvestor produces wider MDD range due to unbounded quantity generation
4. Validate that all four variants exhibit the fundamental emergent herding signature (EMI ≥ 0.05)

## §2 Metric → Function Mapping

| Metric                               | Function                                                           | analysis-bases.md ref |
|--------------------------------------|--------------------------------------------------------------------|-----------------------|
| Emergent Momentum Index (EMI)        | `emergent_momentum_index(price_history)`                           | §2.1                  |
| Maximum Drawdown (MDD)               | `maximum_drawdown(price_history)`                                  | §2.2                  |
| Agent Convergence Contribution (ACC) | `agent_convergence_contribution(agent_quantities, return_history)` | §2.3                  |
| Risk-Averse Early Exit Index (REI)   | `risk_averse_early_exit_index(ra_position_history, price_history)` | §2.4                  |
| Herding Volatility Ratio (HVR)       | `herding_volatility_ratio(return_history)`                         | §2.5                  |
| Wealth Distribution Index (WDI)      | `wealth_distribution_index(agent_wealth)`                          | §2.6                  |

## §3 LLM-Specific Notes

- **LLMMomentumInvestor**: EMI may be wider than Rule — LLM generates both stronger and weaker momentum signals; if EMI < 0.05 consistently, review system prompt phrasing for momentum persona.
- **LLMContrarianInvestor**: REI variability higher; LLM must infer overvaluation from `price` + `return_pct` trend — no broadcast `deviation`; if REI < 0.20, strengthen contrarian persona prompt.
- **LLMRiskAverseInvestor**: MDD potentially lower than Rule as LLM exits earlier via qualitative risk assessment; MDD < 0.03 indicates over-cautious LLM preventing bubble formation entirely.
- **LLMNoiseTrader**: HVR run-to-run variance higher than Rule due to LLM non-Gaussian noise patterns.
- **LLMAggressiveInvestor**: Quantities not bounded by Rule's ±80 — LLM may express extreme bullishness; MDD and HVR can exceed Rule bounds.
- **Run count**: Minimum 10 seeds required for reliable LLM metric estimates due to stochasticity.

## §4 Expected Ranges

| Metric            | LLM Expected Range | vs. Rule Baseline | Theoretical Basis                        |
|-------------------|--------------------|-------------------|------------------------------------------|
| EMI               | 0.05 – 0.30        | Wider variance    | LLM momentum conviction varies by run    |
| MDD               | 0.03 – 0.35        | Wider             | LLM aggressive may exceed Rule ±80 cap   |
| ACC (§4.1 + §4.5) | 40 – 80 %          | Variable          | Prompt quality and temperature dependent |
| REI               | 0.20 – 0.75        | Variable          | Inferred deviation vs. Rule formula      |
| HVR               | 1.2 – 5.0          | Wider             | Temperature-driven herding variance      |
| WDI               | 0.05 – 0.30        | Similar           | Wealth distribution follows crisis arc   |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.
