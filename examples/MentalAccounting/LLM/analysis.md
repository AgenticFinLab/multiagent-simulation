# MentalAccounting Analysis Guide

## §1 Metrics

| Metric | Description | Expected Range |
|--------|-------------|----------------|
| Price deviation | Deviation from fundamental | Varies by scenario |
| Max drawdown | Largest peak-to-trough decline | Varies by scenario |
| Volatility | Annualized return volatility | Varies by scenario |

## §2 Visualization Guide

1. **Price vs Fundamental**: Shows whether agents create mispricings
2. **Deviation Plot**: Magnitude and persistence of mispricings
3. **Return Distribution**: Should show fat tails for behavioral scenarios

## §3 Troubleshooting

- **No phenomenon observed**: Adjust agent parameters
- **Too extreme**: Add more stabilizing agents or increase mean reversion
- **Too stable**: Increase destabilizing agent parameters

## §4 References

- Thaler (1999): Mental Accounting Matters
- Thaler (1985): Mental accounting and consumer choice
- Barberis & Huang (2001): Mental accounting, loss aversion, and individual stock returns

## §5 Cross-Variant Comparison

LLM results are compared against Rule to measure whether persona-only reasoning changes mental-accounting behavior and market impact while using the same market structure.

## §6 Expected Results and Validation

Valid LLM outputs should complete 200 rounds with clean parse quality and auditable decision traces.

## §7 Visualization Catalogue

`LLM/analysis.py` reuses the Rule analysis pipeline and creates `mentalaccounting_analysis.png`. Reports may add LLM action-distribution and parse-quality summaries.
