# DispositionEffect RuleLLM Variant — analysis.md

## §1 Metrics and Functions

| Metric                              | Function                                                                  | analysis-bases.md Ref |
|-------------------------------------|---------------------------------------------------------------------------|-----------------------|
| Proportion of Gains Realized (PGR)  | `proportion_of_gains_realized(trades, price_history, purchase_prices)`    | §2.1                  |
| Proportion of Losses Realized (PLR) | `proportion_of_losses_realized(trades, price_history, purchase_prices)`   | §2.2                  |
| Disposition Coefficient (DC)        | `disposition_coefficient(pgr, plr)`                                       | §2.3                  |
| PGR/PLR Ratio                       | `pgr_plr_ratio(pgr, plr)`                                                 | §2.4                  |
| Holding Period Asymmetry (HPA)      | `holding_period_asymmetry(sell_events)`                                   | §2.5                  |
| Performance Drag Index (PDI)        | `performance_drag_index(disposition_final_wealth, rational_final_wealth)` | §2.6                  |
| Tax Reversal Index (TRI)            | `tax_reversal_index(tax_plr, disposition_plr)`                            | §2.7                  |

## §2 RuleLLM Variant Notes

**Analysis script**: `DispositionEffect/RuleLLM/analysis.py`

Key RuleLLM-variant-specific analysis notes:

- **Rule compliance check**: Compute PGR/PLR for RuleLLM vs. Rule; differences > 5% indicate LLM is overriding embedded thresholds.
- **DC boundary analysis**: RuleLLM DC should bracket Rule (mechanical) and LLM (narrative); examine sells near threshold (gain_loss = 0.028–0.032) for soft-threshold behavior.
- **Reasoning transparency**: `<analysis>` tag content per trade event records LLM's explicit Prospect Theory reasoning — qualitative analysis opportunity.
- **RuleLLMLossAverse PDI**: Should show highest performance drag among RuleLLM agents (lowest PLR = maximum loser-holding).
- **HPA rule fidelity**: HPA(RuleLLM) vs. HPA(Rule) gap measures how much LLM boundary reasoning extends holding durations.

## §3 Output Files

RuleLLM variant produces the following output files in `outputs/DispositionEffect/RuleLLM/`:

| File                   | Content                                                 |
|------------------------|---------------------------------------------------------|
| `price_history.csv`    | Round-by-round price, return, news shock                |
| `agent_orders.csv`     | Per-agent action, quantity, strategy, round             |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round               |
| `metrics_summary.json` | PGR, PLR, DC, PGR/PLR ratio, HPA, PDI, TRI              |
| `llm_responses.jsonl`  | Raw LLM outputs with embedded rule compliance reasoning |

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
