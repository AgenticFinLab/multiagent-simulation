# EquityPremium Rag — Analysis Documentation

## §1 Analysis Objectives

Measure how RAG-retrieved behavioral finance knowledge affects the simulated equity premium compared to Rule and LLM baselines. Key questions:
- Does retrieved loss aversion literature amplify the equity premium above Rule baseline?
- Does knowledge retrieval reduce LLM variance in allocation decisions?
- Which investor types benefit most from retrieved academic evidence?

## §2 Metric → Function Mapping

| Metric                                 | Function                                                                                    | analysis-bases.md ref |
|----------------------------------------|---------------------------------------------------------------------------------------------|-----------------------|
| Simulated Equity Premium (SEP)         | `simulated_equity_premium(stock_returns, bond_return, rounds_per_year=12)`                  | §2.1                  |
| Equity Allocation Deviation (EAD)      | `equity_allocation_deviation(agent_stock_values, agent_portfolio_values, neutral_pct=0.50)` | §2.2                  |
| Evaluation Frequency Sensitivity (EFS) | `evaluation_frequency_sensitivity(window_sizes, mean_equity_allocations)`                   | §2.3                  |
| Stock Return Volatility Ratio (SRVR)   | `stock_return_volatility_ratio(stock_returns, bond_return)`                                 | §2.4                  |
| Loss Probability Index (LPI)           | `loss_probability_index(stock_returns, evaluation_window=5)`                                | §2.5                  |
| Portfolio Wealth Efficiency (PWE)      | `portfolio_wealth_efficiency(agent_terminal_wealth, buy_and_hold_terminal_wealth)`          | §2.6                  |

## §3 Rag-Specific Notes

- **RagLLMMyopicLossAverse (§4.1)**: Retrieved Benartzi & Thaler passages may amplify perceived loss probability — SEP slightly higher than Rule; EAD may be more extreme than pure LLM in bad periods
- **RagLLMLongTermInvestor (§4.2)**: Retrieved long-horizon literature prevents panic selling — allocation stability comparable to Rule; EAD lower than pure LLM
- **RagLLMInstitutionalInvestor (§4.3)**: Retrieved efficiency literature grounds excess-return computation; EAD near Rule baseline; more consistent than pure LLM
- **RagLLMRiskAverseSaver (§4.4)**: Retrieved prospect theory passages reinforce extreme bond preference — EAD can exceed 0.35 in loss periods; contributes most to SEP elevation
- **RagLLMRationalOptimizer (§4.5)**: Context-aware signal use reduces noise contribution to SRVR — SRVR slightly lower than Rule; more directional trading
- **vs. Rule**: SEP central tendency similar; RAG retrieval of loss aversion evidence may push upper bound higher
- **vs. LLM**: Lower variance; retrieved knowledge anchors allocation decisions; PWE floor higher

## §4 Expected Ranges

| Metric         | Rag Expected Range | vs. Rule Baseline | vs. LLM Baseline |
|----------------|--------------------|-------------------|------------------|
| SEP            | 0.03–0.08          | Similar or +5–10% | Narrower range   |
| EAD (MyopicLA) | 0.14–0.35          | Similar or higher | Lower variance   |
| LPI            | 0.38–0.55          | Similar           | Similar          |
| SRVR           | 2.5–7              | Slightly lower    | Lower            |
| PWE (MyopicLA) | 0.83–0.97          | Similar           | Higher floor     |

## §5 References

See `analysis-bases.md §2` for full metric derivations and Python function signatures.
See `simulation-bases.md §2` for theoretical foundations.

## §6 Validation Criteria

Rag samples must preserve the `stock_qty` allocation schema, record `rag_context`
on each investor order, write `rag_stats.json`, and produce the fixed PNG output
set from the Rule analysis contract.

## §7 Cross-Variant Use

Compare Rag against RuleLLM to isolate the effect of retrieved equity-premium and
loss-aversion knowledge while holding the allocation schema constant.
