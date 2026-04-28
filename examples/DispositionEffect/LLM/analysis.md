# DispositionEffect LLM Variant — analysis.md

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

## §2 LLM Variant Notes

**Analysis script**: `DispositionEffect/LLM/analysis.py`

Key LLM-variant-specific analysis notes:

- **PGR/PLR variance**: LLM threshold drift produces higher variance; report mean ± std across multiple runs.
- **DC emergent strength**: LLM DC may exceed Rule DC (emotional "can't sell" reasoning) or be weaker (LLM capitulates under pressure). Compare to Rule DC ≈ 0.05.
- **Reasoning trace analysis**: Extract `<analysis>` tags from LLM outputs; count mentions of "purchase price", "loss", "pain" as proxy for anchoring strength.
- **LLMLossAverse vs. LLMDispositionBiased**: Compare PLR between these two agents; LLMLossAverse should have lower PLR.
- **Emergent rationality**: Check if LLMRationalInvestor shows non-zero DC (emergent disposition from LLM training data).

## §3 Output Files

LLM variant produces the following output files in `outputs/DispositionEffect/LLM/`:

| File                   | Content                                            |
|------------------------|----------------------------------------------------|
| `price_history.csv`    | Round-by-round price, return, news shock           |
| `agent_orders.csv`     | Per-agent action, quantity, strategy, round        |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round          |
| `metrics_summary.json` | PGR, PLR, DC, PGR/PLR ratio, HPA, PDI, TRI         |
| `llm_responses.jsonl`  | Raw LLM outputs with thinking and parsed decisions |

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
