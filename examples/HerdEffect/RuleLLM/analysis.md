# HerdEffect RuleLLM — Analysis Documentation

## §1 Analysis Objectives

This variant tests whether the Rule+LLM hybrid preserves the emergent herding dynamics of the Rule baseline while adding narrative interpretability. Objectives:
1. Confirm EMI and HVR remain within Rule baseline range (formula backbone preserved)
2. Test if LLM overlay meaningfully affects REI (ContrarianInvestor qualitative judgment)
3. Validate that RuleLLM provides explainable reasoning for each herding episode
4. Measure residual variance from LLM component vs. pure Rule determinism

## §2 Metric → Function Mapping

| Metric                               | Function                                                           | analysis-bases.md ref |
|--------------------------------------|--------------------------------------------------------------------|-----------------------|
| Emergent Momentum Index (EMI)        | `emergent_momentum_index(price_history)`                           | §2.1                  |
| Maximum Drawdown (MDD)               | `maximum_drawdown(price_history)`                                  | §2.2                  |
| Agent Convergence Contribution (ACC) | `agent_convergence_contribution(agent_quantities, return_history)` | §2.3                  |
| Risk-Averse Early Exit Index (REI)   | `risk_averse_early_exit_index(ra_position_history, price_history)` | §2.4                  |
| Herding Volatility Ratio (HVR)       | `herding_volatility_ratio(return_history)`                         | §2.5                  |
| Wealth Distribution Index (WDI)      | `wealth_distribution_index(agent_wealth)`                          | §2.6                  |

## §3 RuleLLM-Specific Notes

- **Formula backbone**: RuleLLM formulas dominate → EMI should be close to Rule baseline (within ±20 %); deviations > 40 % indicate LLM override is too strong.
- **ContrarianInvestor**: Reads `fundamental` from own `extras` (same as Rule) → REI should be similar; LLM narrative may slightly increase REI by adding qualitative overvaluation judgment.
- **AggressiveInvestor**: Rule ±80 cap preserved → MDD bounded; no unbounded quantity risk as in pure LLM.
- **Variance**: Lower run-to-run variance than LLM; higher than Rule; expect 3–7 seeds for convergence.
- **Research use**: Compare RuleLLM reasoning traces against Rule behavior to identify where LLM adds value beyond formula.

## §4 Expected Ranges

| Metric            | RuleLLM Expected Range | vs. Rule Baseline | Interpretation                               |
|-------------------|------------------------|-------------------|----------------------------------------------|
| EMI               | 0.07 – 0.25            | Similar           | Formula backbone preserves momentum dynamics |
| MDD               | 0.09 – 0.30            | Similar           | Rule ±80 cap bounds maximum drawdown         |
| ACC (§4.1 + §4.5) | ≥ 48 % during momentum | Similar           | Formula drives momentum agent contribution   |
| REI               | 0.38 – 0.72            | Slightly higher   | LLM may reinforce early exit narratively     |
| HVR               | 1.4 – 4.0              | Similar           | Rule formula preserves volatility regime     |
| WDI               | 0.05 – 0.25            | Similar           | Wealth distribution mirrors Rule arc         |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.
