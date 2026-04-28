# HerdEffect Rag — Analysis Documentation

## §1 Analysis Objectives

This variant tests whether document retrieval enhances emergent herding fidelity beyond Rule and LLM baselines. Objectives:
1. Determine if retrieved momentum literature increases EMI vs. Rule (better grounded conviction)
2. Test if retrieved crash histories enable earlier RiskAverseInvestor exit (lower MDD)
3. Measure if retrieved value-investing evidence improves ContrarianInvestor timing (higher REI)
4. Validate that document grounding reduces run-to-run variance vs. pure LLM

## §2 Metric → Function Mapping

| Metric                               | Function                                                           | analysis-bases.md ref |
|--------------------------------------|--------------------------------------------------------------------|-----------------------|
| Emergent Momentum Index (EMI)        | `emergent_momentum_index(price_history)`                           | §2.1                  |
| Maximum Drawdown (MDD)               | `maximum_drawdown(price_history)`                                  | §2.2                  |
| Agent Convergence Contribution (ACC) | `agent_convergence_contribution(agent_quantities, return_history)` | §2.3                  |
| Risk-Averse Early Exit Index (REI)   | `risk_averse_early_exit_index(ra_position_history, price_history)` | §2.4                  |
| Herding Volatility Ratio (HVR)       | `herding_volatility_ratio(return_history)`                         | §2.5                  |
| Wealth Distribution Index (WDI)      | `wealth_distribution_index(agent_wealth)`                          | §2.6                  |

## §3 Rag-Specific Notes

- **RagMomentumInvestor**: EMI may be slightly higher than RuleLLM due to retrieved momentum evidence reinforcing buy conviction; monitor for over-amplification (EMI > 0.35).
- **RagContrarianInvestor**: REI expected higher than Rule and LLM — retrieved De Bondt & Thaler evidence provides specific reversal timing cues; `fundamental` still from own `extras`.
- **RagRiskAverseInvestor**: MDD expected slightly lower than Rule — retrieved crash history knowledge triggers precautionary exit before variance spikes.
- **RagNoiseTrader**: Noise pattern anchored to retrieved microstructure literature; less extreme than pure LLM noise.
- **RagAggressiveInvestor**: Rule ±80 cap preserved — no unbounded quantity risk; document context may strengthen conviction but not quantity limit.
- **Corpus quality**: RAG performance directly dependent on document corpus relevance; verify corpus contains Jegadeesh-Titman (1993), De Bondt-Thaler (1985), Nofsinger-Sias (1999).

## §4 Expected Ranges

| Metric            | Rag Expected Range | vs. Rule Baseline | Theoretical Basis                               |
|-------------------|--------------------|-------------------|-------------------------------------------------|
| EMI               | 0.08 – 0.28        | Slightly higher   | Retrieved momentum evidence reinforces herding  |
| MDD               | 0.07 – 0.25        | Slightly lower    | Crash history knowledge enables earlier exits   |
| ACC (§4.1 + §4.5) | ≥ 50 %             | Similar/higher    | Retrieved patterns improve momentum attribution |
| REI               | 0.45 – 0.78        | Higher            | Retrieved value-investing cases improve timing  |
| HVR               | 1.3 – 4.5          | Similar           | RAG amplifies or dampens depending on corpus    |
| WDI               | 0.05 – 0.28        | Similar           | Wealth distribution follows crisis arc          |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.
