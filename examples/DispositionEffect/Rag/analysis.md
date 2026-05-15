# DispositionEffect Rag Variant — analysis.md

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

## §2 Rag Variant Notes

**Analysis script**: `DispositionEffect/Rag/analysis.py`

Key Rag-variant-specific analysis notes:

- **Calibration test**: Compare Rag PGR/PLR to Odean (1998) empirical benchmark (PGR ≈ 0.148, PLR ≈ 0.098); Rag should be closest to empirical values if RAG retrieval succeeds.
- **Bias awareness effect**: RagDispositionInvestor DC vs. LLMDispositionBiased DC — if RAG reduces DC, academic self-awareness moderates bias.
- **Retrieved context logging**: Log retrieved chunks per agent per round; analyze which papers were retrieved during high-gain and high-loss rounds.
- **TRI RAG enhancement**: Check if RagTaxAwareInvestor TRI is higher than LLMTaxAwareInvestor TRI (RAG reinforces tax-harvesting literature).
- **Note on coverage**: Only 3 investor types (no IndexHolder, InstitutionalInvestor); PDI compares RagDispositionInvestor to RagRationalInvestor.

## §3 Output Files

Rag variant produces the following output files in `outputs/DispositionEffect/Rag/`:

| File                   | Content                                              |
|------------------------|------------------------------------------------------|
| `price_history.csv`    | Round-by-round price, return, news shock             |
| `agent_orders.csv`     | Per-agent action, quantity, strategy, round          |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round            |
| `metrics_summary.json` | PGR, PLR, DC, PGR/PLR ratio, HPA, PDI, TRI           |
| `llm_responses.jsonl`  | Raw LLM outputs with retrieved context and decisions |
| `retrieval_log.jsonl`  | Per-round retrieved knowledge chunks per agent       |

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
