# HerdEffect Rule — Analysis Documentation

## §1 Analysis Objectives

This variant establishes the deterministic baseline for HerdEffect. Objectives:
1. Verify that rule-encoded positive feedback produces measurable momentum episodes (EMI ≥ 0.08)
2. Confirm that both MomentumInvestor and AggressiveInvestor contribute to herding (ACC §4.1 + §4.5 ≥ 50 %)
3. Validate that RiskAverseInvestor exits before price peak in ≥ 40 % of episodes (REI ≥ 0.40)
4. Establish HVR target [1.5–4.0] as calibration anchor for LLM/RuleLLM/Rag comparison
5. Confirm emergent herding without explicit imitator — no agent directly copies another

## §2 Metric → Function Mapping

| Metric                               | Function                                                           | analysis-bases.md ref |
|--------------------------------------|--------------------------------------------------------------------|-----------------------|
| Emergent Momentum Index (EMI)        | `emergent_momentum_index(price_history)`                           | §2.1                  |
| Maximum Drawdown (MDD)               | `maximum_drawdown(price_history)`                                  | §2.2                  |
| Agent Convergence Contribution (ACC) | `agent_convergence_contribution(agent_quantities, return_history)` | §2.3                  |
| Risk-Averse Early Exit Index (REI)   | `risk_averse_early_exit_index(ra_position_history, price_history)` | §2.4                  |
| Herding Volatility Ratio (HVR)       | `herding_volatility_ratio(return_history)`                         | §2.5                  |
| Wealth Distribution Index (WDI)      | `wealth_distribution_index(agent_wealth)`                          | §2.6                  |

## §3 Rule-Specific Notes

- **MomentumInvestor (§4.1)**: Deterministic formula → tight EMI band; EMI > 0.30 expected in Rule baseline.
- **ContrarianInvestor (§4.2)**: Must read `fundamental` from own `extras` — verify config sets it; if missing, REI = 0.
- **RiskAverseInvestor (§4.3)**: `lookback=5` default — sensitivity test recommended; shorter lookback → higher REI.
- **NoiseTrader (§4.4)**: Run-to-run HVR variance expected due to stochastic trigger; run ≥ 10 seeds.
- **AggressiveInvestor (§4.5)**: Primary MDD driver; MDD > 0.20 almost always linked to high AggressiveInvestor activity; check `kappa` and `accel_bonus`.
- **MAD is not a HerdEffect metric**: HerdEffect measures momentum (EMI) not fundamental deviation (PD/MAD) — different from EndowmentEffect.

## §4 Expected Ranges

| Metric            | Rule Expected Range    | Interpretation                                               |
|-------------------|------------------------|--------------------------------------------------------------|
| EMI               | 0.08 – 0.25            | Emergent momentum index; target calibration range            |
| MDD               | 0.10 – 0.30            | Peak-to-trough drawdown; momentum then reversal              |
| ACC (§4.1 + §4.5) | ≥ 50 % during momentum | Both momentum agents active                                  |
| REI               | 0.40 – 0.70            | RiskAverseInvestor exits before peak in majority of episodes |
| HVR               | 1.5 – 4.0              | Bubble-phase volatility 1.5–4× quiet-phase                   |
| WDI               | 0.05 – 0.25            | Gini of final wealth; ContrarianInvestor modest winner       |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.
