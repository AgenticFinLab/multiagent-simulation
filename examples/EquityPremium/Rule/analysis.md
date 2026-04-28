# EquityPremium Rule — Analysis Documentation

## §1 Analysis Objectives

Establish the deterministic baseline for the EquityPremium simulation. Key questions:
- Does the Rule variant reproduce the ~6% historical equity premium?
- How do each investor's allocation and rebalancing strategy affect the aggregate premium?
- Which parameters (loss_aversion, evaluation_window) most sensitively control the premium?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                                    | analysis-bases.md ref |
|----------------------------------------|---------------------------------------------------------------------------------------------|-----------------------|
| Simulated Equity Premium (SEP)         | `simulated_equity_premium(stock_returns, bond_return, rounds_per_year=12)`                  | §2.1                  |
| Equity Allocation Deviation (EAD)      | `equity_allocation_deviation(agent_stock_values, agent_portfolio_values, neutral_pct=0.50)` | §2.2                  |
| Evaluation Frequency Sensitivity (EFS) | `evaluation_frequency_sensitivity(window_sizes, mean_equity_allocations)`                   | §2.3                  |
| Stock Return Volatility Ratio (SRVR)   | `stock_return_volatility_ratio(stock_returns, bond_return)`                                 | §2.4                  |
| Loss Probability Index (LPI)           | `loss_probability_index(stock_returns, evaluation_window=5)`                                | §2.5                  |
| Portfolio Wealth Efficiency (PWE)      | `portfolio_wealth_efficiency(agent_terminal_wealth, buy_and_hold_terminal_wealth)`          | §2.6                  |

## §3 Rule-Specific Notes

- **MyopicLossAverseInvestor (§4.1)**: Perceived risk formula is deterministic given `stock_history`; EAD is stable across runs; LPI directly controls premium demand
- **LongHorizonInvestor (§4.2)**: No rolling evaluation — EAD is purely a function of `target_stock_pct` vs. realized price path; stable allocation
- **RiskNeutralInvestor (§4.3)**: EAD is small and centered near zero; SEP contribution modest; provides rational anchor
- **ConservativeInvestor (§4.4)**: Very low rebalancing speed (0.1× gap) means actual allocation stays below target for much of the simulation; EAD higher than target deviation
- **NoiseTrader (§4.5)**: SRVR is elevated by noise_std; indirectly raises LPI for MyopicLossAverseInvestor by adding return volatility
- **Rule baseline**: All metrics are deterministic given the random seed; SEP should fall in 4–7% annualized range

## §4 Expected Ranges

| Metric            | Rule Expected Range | Interpretation                             |
|-------------------|---------------------|--------------------------------------------|
| SEP               | 0.04–0.07           | 4–7% annualized; matches historical range  |
| EAD (MyopicLA)    | 0.15–0.30           | Persistent under-allocation by 15–30%      |
| EAD (LongHorizon) | 0.08–0.15           | Moderate over-allocation toward target     |
| LPI (MyopicLA)    | 0.40–0.55           | 40–55% of windows show net loss            |
| SRVR              | 3–8                 | Stock returns 3–8× more volatile than bond |
| PWE (MyopicLA)    | 0.85–0.95           | 5–15% wealth loss vs. buy-and-hold         |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.
