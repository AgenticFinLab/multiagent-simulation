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

---

## §4 Variant-Specific Observable Phenomena

LLM is the persona-only variant. `LLMMyopicLossAverse`,
`LLMLongTermInvestor`, `LLMInstitutionalInvestor`, `LLMRiskAverseSaver`, and
`LLMRationalOptimizer` decide their `stock_qty` allocation from prompts with
no embedded formulas. Analysis looks for LLM-driven variance that widens the
Rule reference bands.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Wider SEP distribution | `summary.json → equity_premium` shifts 20–50 % more across seeds | Rule reproducible; LLM is not |
| Occasional equity abandonment | `01_equitypremium_dynamics.png` — `LLMMyopicLossAverse` allocation collapses to near zero in bad periods | Rule EAD is capped at ~0.30; LLM may exceed 0.40 |
| Persona drift under stress | `LLMLongTermInvestor` allocation drifts down under persistent losses | Rule LongHorizon holds target stably |
| Noisier EFS curve | `02_equitypremium_analysis.png` — allocation vs. `evaluation_window` shows scatter around the Rule trend | Rule curve is monotonic |
| Reasoning-string diversity | Order payload `reasoning` field present and non-empty; content varies across rounds | Rule payloads carry no reasoning text |

There is no `== DECISION RULES ==` block enforcing the schema, so the
analysis must audit `stock_qty` field validity before treating aggregate
metrics as trustworthy.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 50 (short) | Persona effects visible but SEP variance large | Low | Prompt tuning |
| 200 | Full myopic → steady-state arc; SEP central tendency stable | Medium | Standard runs |
| 500 | LLM tail effects averaged out; robust variant comparison against Rule | High | Persona-effect research; watch API cost |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~3 per archetype) | Aggregate SEP direction correct; per-archetype EAD very noisy | LLM stochasticity dominates |
| Recommended (5–10 per archetype) | Stable per-archetype EAD; clean radar plot | Full LLM variance visible against Rule |
| Large (20+ per archetype) | Tight LLM distributions; LLM cost the binding constraint | Cost-limited regime |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| LLM temperature | +50% | Wider SEP distribution; higher EAD upper bound; more allocation abandonment |
| LLM temperature | −50% | LLM behavior converges toward persona centroid; closer to Rule |
| Persona intensity (`== PERSONA ==`) | +50% verbosity | Sharper archetype separation; larger MyopicLA EAD |
| Persona intensity | −50% verbosity | LLM defaults dominate; archetypes flatten toward neutral |
| Market volatility (news σ) | +50% | LLM allocation drops more sharply under losses; SEP rises |

---

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/EquityPremium/LLM/analysis/`.

| Output File | Generated By | Contents | Interpretation |
|---|---|---|---|
| `summary.json` | `main()` (Rule analyze reused) | Rounds, price statistics, per-investor SEP / EAD / LPI / SRVR / PWE, validation, plus LLM action-distribution audit | Persona effects show up as widened SEP / EAD relative to Rule |
| `00_investor_bids.png` | `plot_equity_premium_analysis()` (imported from Rule) | Per-round investor allocation panel | LLM allocation should still respect `stock_qty` schema; abandonment events show as spikes to zero |
| `01_equitypremium_dynamics.png` | `plot_equity_premium_analysis()` | Stock price + rolling SEP | Overlay against Rule to see persona-driven SEP drift |
| `02_equitypremium_analysis.png` | `plot_equity_premium_analysis()` | LPI × evaluation window and allocation analytics | Curve noisier than Rule; still positively sloped |
| `03_summary.png` | `plot_equity_premium_analysis()` | Compact wealth/allocation summary panel | Compare wealth outcomes vs. Rule buy-and-hold baseline |

Raw LLM completion artifacts under `EXPERIMENT/EquityPremium/LLM/records/`
supply the `reasoning` strings used for the action-distribution audit.
