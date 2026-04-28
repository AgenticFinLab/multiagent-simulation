# CreditCycle Rule Variant — analysis.md

## §1 Metrics and Functions

| Metric                               | Function                                                       | analysis-bases.md Ref |
|--------------------------------------|----------------------------------------------------------------|-----------------------|
| Leverage Amplitude Index (LAI)       | `leverage_amplitude_index(price_history, fundamental)`         | §2.1                  |
| Minsky Fragility Score (MFS)         | `minsky_fragility_score(stable_rounds_history, crisis_events)` | §2.2                  |
| Credit Contraction Speed (CCS)       | `credit_contraction_speed(price_history)`                      | §2.3                  |
| Counter-Cyclical Offset Ratio (CCOR) | `counter_cyclical_offset_ratio(agent_volume_by_type)`          | §2.4                  |
| Phase Duration Ratio (PDR)           | `phase_duration_ratio(price_history, fundamental)`             | §2.5                  |
| Noise Trader Contamination (NTC)     | `noise_trader_contamination(noise_orders, deviations)`         | §2.6                  |
| Wealth Redistribution Index (WRI)    | `wealth_redistribution_index(agent_final_states)`              | §2.7                  |

## §2 Rule Variant Notes

**Analysis script**: `CreditCycle/Rule/analysis.py`

The Rule variant produces fully deterministic outputs for a given random seed. Key variant-specific analysis notes:

- **MFS precision**: Since `stable_rounds` is tracked mechanically, MFS can be measured exactly for each crisis event.
- **CCOR baseline**: Rule variant establishes the CCOR baseline (expected ≈ 0.4–0.6) for comparison against LLM variants.
- **LAI determinism**: LAI values cluster around the same range across runs (primary variance from Market noise term only).
- **NTC = 0 expected**: NoiseTrader is purely random; any NTC deviation indicates simulation artifact.

## §3 Output Files

Rule variant produces the following output files in `outputs/CreditCycle/Rule/`:

| File                   | Content                                   |
|------------------------|-------------------------------------------|
| `price_history.csv`    | Round-by-round price and deviation        |
| `agent_orders.csv`     | Per-agent order action, quantity, round   |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round |
| `metrics_summary.json` | LAI, MFS, CCS, CCOR, PDR, NTC, WRI        |

## §4 Phase Attribution

For each bust event (δ < −0.05), compute per-agent contribution:

```python
bust_sellers = {
    "ProCyclicalLender": sum_sell_volume_during_bust,
    "MinskyBorrower": sum_sell_volume_during_bust,
}
bust_buyers = {
    "CounterCyclicalLender": sum_buy_volume_during_bust,
    "ValueInvestor": sum_buy_volume_during_bust,
}
```

This attribution links directly to CCOR (analysis-bases.md §2.4).

## §5 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
