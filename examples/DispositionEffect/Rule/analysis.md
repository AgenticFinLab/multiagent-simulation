# DispositionEffect Rule Variant — analysis.md

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

## §2 Rule Variant Notes

**Analysis script**: `DispositionEffect/Rule/analysis.py`

The Rule variant produces fully deterministic outputs for a given random seed. Key variant-specific analysis notes:

- **PGR/PLR determinism**: PGR and PLR are determined exactly by `gain_threshold` and `loss_threshold` parameters; minimal variance across runs (news shock randomness only).
- **DC calibration**: Rule variant DC ≈ 0.05 is the calibration target for all other variants to compare against.
- **HPA precision**: `rounds_held` tracked per position; Rule HPA is the cleanest measurement for Prospect Theory asymmetry validation.
- **PDI benchmark**: Rule variant PDI (3–5%) establishes the performance drag benchmark.
- **TRI anti-disposition**: TaxAwareInvestor PLR should be 2–4× DispositionInvestor PLR due to deliberate tax-loss harvesting.

## §3 Output Files

Rule variant produces the following output files in `outputs/DispositionEffect/Rule/`:

| File                   | Content                                                   |
|------------------------|-----------------------------------------------------------|
| `price_history.csv`    | Round-by-round price, return, news shock                  |
| `agent_orders.csv`     | Per-agent strategy, quantity, bid_price, round            |
| `agent_wealth.csv`     | Per-agent cash, position, purchase_price, wealth by round |
| `metrics_summary.json` | PGR, PLR, DC, PGR/PLR ratio, HPA, PDI, TRI                |

## §4 Phase Attribution

For each sell event, record:

```python
sell_event = {
    "investor_type": "DispositionInvestor",
    "round": t,
    "gain_loss_at_sale": gain_loss,  # positive = winner sold, negative = loser sold
    "rounds_held": t - purchase_round,
    "quantity": abs(quantity),
}
```

PGR/PLR computed by aggregating across all sell events and open positions per round.  
HPA computed from `sell_events` (analysis-bases.md §2.5).

## §5 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
