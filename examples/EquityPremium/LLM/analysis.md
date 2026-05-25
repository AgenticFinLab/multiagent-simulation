# EquityPremium LLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether LLM personas reproduce myopic loss aversion and the equity premium puzzle relative to the Rule baseline. Key questions:
- Do LLM personas generate comparable equity premiums to Rule-encoded loss aversion?
- Does LLM stochasticity amplify or compress the premium variance?
- How does LLM reasoning compare to deterministic formulas in producing allocation biases?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                                    | analysis-bases.md ref |
|----------------------------------------|---------------------------------------------------------------------------------------------|-----------------------|
| Simulated Equity Premium (SEP)         | `simulated_equity_premium(stock_returns, bond_return, rounds_per_year=12)`                  | §2.1                  |
| Equity Allocation Deviation (EAD)      | `equity_allocation_deviation(agent_stock_values, agent_portfolio_values, neutral_pct=0.50)` | §2.2                  |
| Evaluation Frequency Sensitivity (EFS) | `evaluation_frequency_sensitivity(window_sizes, mean_equity_allocations)`                   | §2.3                  |
| Stock Return Volatility Ratio (SRVR)   | `stock_return_volatility_ratio(stock_returns, bond_return)`                                 | §2.4                  |
| Loss Probability Index (LPI)           | `loss_probability_index(stock_returns, evaluation_window=5)`                                | §2.5                  |
| Portfolio Wealth Efficiency (PWE)      | `portfolio_wealth_efficiency(agent_terminal_wealth, buy_and_hold_terminal_wealth)`          | §2.6                  |

## §3 LLM-Specific Notes

- **LLMMyopicLossAverse (§4.1)**: LLM may overreact to single bad rounds more dramatically than Rule formula; EAD higher variance; occasional abandonment of equity position
- **LLMLongTermInvestor (§4.2)**: Persona is strong but LLM may drift under persistent negative returns — DPHL shorter than Rule's stable 60% allocation
- **LLMInstitutionalInvestor (§4.3)**: LLM rational optimizer may not consistently apply excess-return formula; EAD varies more than Rule's RiskNeutralInvestor
- **LLMRiskAverseSaver (§4.4)**: Very strong persona effect — may refuse equities entirely in bad periods; EAD can reach 0.40+ (extreme under-allocation)
- **LLMRationalOptimizer (§4.5)**: Adaptive reasoning means this investor is more responsive to context than Rule's NoiseTrader; less pure noise, more signal exploitation
- **vs. Rule**: SEP range is 20–50% wider in LLM due to persona inconsistency; PWE lower on average

## §4 Expected Ranges

| Metric         | LLM Expected Range | vs. Rule Baseline                            |
|----------------|--------------------|----------------------------------------------|
| SEP            | 0.03–0.09          | Wider range, similar central tendency        |
| EAD (MyopicLA) | 0.12–0.40          | Higher upper bound                           |
| LPI            | 0.38–0.58          | Similar                                      |
| SRVR           | 3–9                | Slightly higher due to LLM-driven volatility |
| PWE (MyopicLA) | 0.80–1.00          | Lower floor (more extreme under-allocation)  |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Validation Criteria

LLM samples must preserve the `stock_qty` allocation schema and should have no
unrecorded parser fallback. Accepted outputs must include `summary.json` and the
four fixed PNG files from the Rule analysis contract.

## §7 Cross-Variant Use

Compare LLM against Rule to isolate persona-only reasoning effects while holding
the stock-bond market mechanism constant.
