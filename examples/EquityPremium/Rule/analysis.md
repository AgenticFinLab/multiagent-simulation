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

## §6 Validation Criteria

The run is valid when all configured rounds complete, `summary.json` contains a
validation score, and the fixed PNG set is written:
`00_investor_bids.png`, `01_equitypremium_dynamics.png`,
`02_equitypremium_analysis.png`, and `03_summary.png`.

## §7 Cross-Variant Use

The Rule analysis is the authoritative structural analysis for the stock-bond
allocation schema. LLM, RuleLLM, and Rag analysis reuse the same price, return,
allocation, and validation logic.

---

## §4 Variant-Specific Observable Phenomena

Rule is the deterministic baseline for EquityPremium. Given a fixed seed the
five investor archetypes — `MyopicLossAverseInvestor`,
`LongHorizonInvestor`, `RiskNeutralInvestor`, `ConservativeInvestor`, and
`NoiseTrader` — apply their allocation formulas without reasoning noise or
retrieved knowledge.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Reproducible SEP band | `summary.json → equity_premium` sits in 4–7 % annualized on rerun | This is the baseline; LLM widens the band |
| Threshold-locked MyopicLA under-allocation | `01_equitypremium_dynamics.png` shows Myopic equity share below 50% whenever LPI is high | Reference EAD ≈ 0.15–0.30 |
| Analytic horizon monotonicity | `02_equitypremium_analysis.png` — plotting mean allocation vs. `evaluation_window` yields a strictly increasing curve (EFS > 0.7) | LLM curve is noisier |
| Deterministic PWE ceiling | `summary.json → portfolio_wealth_efficiency` for MyopicLA stable at 0.85–0.95 | LLM PWE has fatter tails |
| Stable SRVR | `stock_return_volatility_ratio` reproducible at fixed seed and typically 3–8 | LLM shifts SRVR upward |

Rule agents therefore anchor the "myopic-loss-aversion premium" at the
Mehra–Prescott region and provide the reference curve for variant contrasts.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 50 (short) | Warm-up + myopic regime only; steady-state SEP unresolved | Low | Quick smoke test |
| 200 | Full arc through §4 phases; stable SEP | Medium | Standard runs |
| 500 | Correction-phase behavior visible; robust PWE | High | Benchmark studies vs. Mehra–Prescott 6.18 % |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~5 per archetype) | Aggregate SEP direction correct; per-archetype EAD noisy | Sparse allocation signal |
| Recommended (10–20 per archetype) | Clean EAD ordering across archetypes; readable radar plots | Full allocation contrast visible |
| Large (50+ per archetype) | Very tight EAD bands; small-effect archetypes separable | Diminishing marginal insight per agent |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| `MyopicLossAverseInvestor.loss_aversion` | +50% | Higher SEP; larger EAD under-allocation; PWE falls |
| `MyopicLossAverseInvestor.loss_aversion` | −50% | Lower SEP; EAD near neutral; PWE rises |
| `evaluation_window` (Myopic) | +50% | Lower LPI; smaller SEP; EFS remains ≈ 0.7+ |
| `evaluation_window` (Myopic) | −50% | Higher LPI; larger SEP |
| `NoiseTrader.noise_std` | +50% | Higher SRVR; secondary lift in SEP |

---

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/EquityPremium/Rule/analysis/`.

| Output File | Generated By | Contents | Interpretation |
|---|---|---|---|
| `summary.json` | `main()` / `analyze_equity_premium()` | Rounds, price statistics, per-investor SEP / EAD / LPI / SRVR / PWE, validation (`validate_equity_premium`) | `validation.is_valid` gates §6 expected-range check; central SEP field ties to Mehra–Prescott benchmark |
| `00_investor_bids.png` | `plot_equity_premium_analysis()` | Per-round investor allocation panel (stock qty by archetype) | Under-weight archetypes stay below the neutral 50% line |
| `01_equitypremium_dynamics.png` | `plot_equity_premium_analysis()` | Stock price + rolling SEP dynamics | Compare to bond baseline (annualized 1 %) |
| `02_equitypremium_analysis.png` | `plot_equity_premium_analysis()` | Loss-probability × evaluation-window and allocation analytics | Curve should be strictly increasing (EFS > 0.7) |
| `03_summary.png` | `plot_equity_premium_analysis()` | Compact wealth/allocation summary panel | Referenced from cross-variant summaries |
