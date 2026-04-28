# EquityPremium RuleLLM — Analysis Documentation

## §1 Analysis Objectives

Measure whether embedded allocation rules constrain LLM variance while preserving the behavioral premium. Key questions:
- Does rule embedding narrow the SEP range compared to pure LLM?
- Do embedded rebalancing constraints maintain allocation stability?
- How does RuleLLM compare to Rule (lower bound) and LLM (upper bound) on PWE?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                                    | analysis-bases.md ref |
|----------------------------------------|---------------------------------------------------------------------------------------------|-----------------------|
| Simulated Equity Premium (SEP)         | `simulated_equity_premium(stock_returns, bond_return, rounds_per_year=12)`                  | §2.1                  |
| Equity Allocation Deviation (EAD)      | `equity_allocation_deviation(agent_stock_values, agent_portfolio_values, neutral_pct=0.50)` | §2.2                  |
| Evaluation Frequency Sensitivity (EFS) | `evaluation_frequency_sensitivity(window_sizes, mean_equity_allocations)`                   | §2.3                  |
| Stock Return Volatility Ratio (SRVR)   | `stock_return_volatility_ratio(stock_returns, bond_return)`                                 | §2.4                  |
| Loss Probability Index (LPI)           | `loss_probability_index(stock_returns, evaluation_window=5)`                                | §2.5                  |
| Portfolio Wealth Efficiency (PWE)      | `portfolio_wealth_efficiency(agent_terminal_wealth, buy_and_hold_terminal_wealth)`          | §2.6                  |

## §3 RuleLLM-Specific Notes

- **RuleLLMMyopicLossAverse (§4.1)**: Evaluation formula is embedded; perceived_risk cannot be overridden — EAD tightly bounded near Rule baseline
- **RuleLLMLongTermInvestor (§4.2)**: Rebalancing speed (0.2× gap) is embedded; prevents LLM panic — allocation more stable than pure LLM
- **RuleLLMInstitutionalInvestor (§4.3)**: Excess-return proportionality is embedded; LLM only adjusts narrative — EAD near Rule baseline
- **RuleLLMRiskAverseSaver (§4.4)**: Low target (25%) and slow rebalancing (0.1×) are locked — persistent under-allocation maintained; EAD similar to Rule
- **RuleLLMRationalOptimizer (§4.5)**: Noise bounds are embedded; LLM may use directional signal within bounds — slightly better SEP contribution than Rule's pure NoiseTrader
- **vs. LLM**: SEP range narrower by ~30%; PWE higher floor (0.85 vs. 0.80)

## §4 Expected Ranges

| Metric         | RuleLLM Expected Range | vs. Rule Baseline | vs. LLM Baseline  |
|----------------|------------------------|-------------------|-------------------|
| SEP            | 0.04–0.07              | Within ±5%        | Narrower range    |
| EAD (MyopicLA) | 0.14–0.28              | Similar           | Lower upper bound |
| LPI            | 0.40–0.55              | Within ±5%        | Similar           |
| SRVR           | 3–8                    | Similar           | Similar           |
| PWE (MyopicLA) | 0.85–0.97              | Within ±3%        | Higher floor      |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.
