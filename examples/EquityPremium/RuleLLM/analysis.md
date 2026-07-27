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

## §6 Validation Criteria

RuleLLM samples must preserve the `stock_qty` allocation schema, use prompts with
`== PERSONA ==` and `== DECISION RULES ==`, and write the same fixed analysis
outputs as Rule.

## §7 Cross-Variant Use

Compare RuleLLM against Rule to measure language-reasoning effects under explicit
allocation rules, and against LLM to measure whether rule anchoring reduces
allocation variance.

---

## §4 Variant-Specific Observable Phenomena

RuleLLM is the hybrid variant for EquityPremium. Prompts include a
`== DECISION RULES ==` block that hard-codes the allocation formula while the
LLM still supplies the reasoning narrative. Analysis should verify that hard
rules bound the observable dynamics but do not fully suppress LLM variance.

| Phenomenon | How to Observe | Contrast with Baseline |
|---|---|---|
| Rule-anchored SEP | `summary.json → equity_premium` sits within ±5 % of Rule's SEP central value | Narrower band than LLM |
| Bounded MyopicLA EAD | `01_equitypremium_dynamics.png` — MyopicLA allocation stays within Rule's ±0.05 corridor | LLM allocation can wander outside this corridor |
| Stable LongHorizon target adherence | LongHorizonInvestor allocation tracks target within ±0.03 | Pure LLM drifts under persistent losses |
| Preserved schema validity | `stock_qty` field non-null on every order payload | LLM without rules may drop or malform this field |
| Reasoning-driven residual jitter | Small round-to-round variation in Rule-flat regions | Rule has none; LLM has more |

RuleLLM should sit between Rule (deterministic) and LLM (persona-only) on
every quantitative axis in `analysis-bases.md §5`.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable | Phenomenon Clarity | Recommended for |
|---|---|---|---|
| 50 (short) | Rule anchoring visible; LLM tail effects unresolved | Low | Prompt / rule tuning |
| 200 | Full arc; rule adherence measurable against LLM residual | Medium | Standard runs |
| 500 | Tight comparison against Rule; robust variance decomposition | High | Rule-anchoring studies |

### Agent Count Scaling

| Agent Count | Expected Observable | Environment Dynamics |
|---|---|---|
| Minimum viable (~3 per archetype) | Aggregate SEP centered on Rule; per-archetype residual noisy | Small-sample LLM noise |
| Recommended (5–10 per archetype) | Clean central tendency around Rule with visible LLM residual | Population averages stabilize |
| Large (20+ per archetype) | Very tight adherence to Rule mean; LLM cost dominates budget | Cost-limited regime |

### Parameter Sensitivity (Variant-Specific)

| Parameter | Change | Expected Effect on This Variant's Analysis |
|---|---|---|
| Rule-block strictness (`== DECISION RULES ==` verbosity) | +50% | RuleLLM curve pulled tighter to Rule; residual jitter shrinks |
| Rule-block strictness | −50% | Behavior drifts toward LLM; SEP band widens |
| `MyopicLossAverseInvestor.loss_aversion` (embedded) | +50% | SEP rises in step with Rule; residual jitter constant |
| LLM temperature | +50% | Higher jitter around Rule mean; occasional schema violations |
| LLM temperature | −50% | RuleLLM converges toward Rule almost exactly |

---

## §6 Output Files Reference

All outputs are written to `EXPERIMENT/EquityPremium/RuleLLM/analysis/`.

| Output File | Generated By | Contents | Interpretation |
|---|---|---|---|
| `summary.json` | `main()` → `analyze_equity_premium()` (imported from Rule) | Rounds, price statistics, per-investor SEP / EAD / LPI / SRVR / PWE, validation | Compare against Rule's `summary.json` to detect rule-anchored LLM drift |
| `00_investor_bids.png` | `plot_equity_premium_analysis()` (imported from Rule) | Per-round investor allocation panel | Panel should closely track Rule's version; small LLM-driven ripples visible |
| `01_equitypremium_dynamics.png` | `plot_equity_premium_analysis()` | Stock price + rolling SEP | Overlay with Rule to see rule-anchored drift band |
| `02_equitypremium_analysis.png` | `plot_equity_premium_analysis()` | LPI × evaluation window and allocation analytics | Curve should be near-monotonic (EFS ≥ 0.7) |
| `03_summary.png` | `plot_equity_premium_analysis()` | Compact wealth/allocation summary panel | Compare PWE against LLM to quantify rule anchoring benefit |

Raw LLM completion artifacts under `EXPERIMENT/EquityPremium/RuleLLM/records/`
supply the reasoning strings that accompany each rule-anchored decision.
