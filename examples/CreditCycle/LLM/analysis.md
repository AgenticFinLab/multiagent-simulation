# CreditCycle LLM Variant — analysis.md

## §1 Metrics and Functions

| Metric                               | Function                                                       | analysis-bases.md Ref                          |
|--------------------------------------|----------------------------------------------------------------|------------------------------------------------|
| Leverage Amplitude Index (LAI)       | `leverage_amplitude_index(price_history, fundamental)`         | §2.1                                           |
| Minsky Fragility Score (MFS)         | `minsky_fragility_score(stable_rounds_history, crisis_events)` | §2.2 — Note: MFS from price-inferred stability |
| Credit Contraction Speed (CCS)       | `credit_contraction_speed(price_history)`                      | §2.3                                           |
| Counter-Cyclical Offset Ratio (CCOR) | `counter_cyclical_offset_ratio(agent_volume_by_type)`          | §2.4                                           |
| Phase Duration Ratio (PDR)           | `phase_duration_ratio(price_history, fundamental)`             | §2.5                                           |
| Noise Trader Contamination (NTC)     | `noise_trader_contamination(noise_orders, deviations)`         | §2.6                                           |
| Wealth Redistribution Index (WRI)    | `wealth_redistribution_index(agent_final_states)`              | §2.7                                           |

## §2 LLM Variant Notes

**Analysis script**: Uses same `analysis.py` as Rule variant — no separate analysis.py needed.

Key LLM-specific analysis notes:

- **MFS approximation**: LLM variant lacks `stable_rounds` counter; MFS is approximated from runs of low-deviation rounds in price_history.
- **LAI variance**: Expect higher cross-run variance in LAI due to LLM stochasticity (multiple runs required for statistical significance).
- **CCOR comparison**: Compare LLM CCOR to Rule baseline to assess whether LLM counter-cyclical agents behave more or less effectively.
- **NTC check**: LLM NoiseTrader should still show NTC ≈ 0 despite natural language generation; verify persona randomness.
- **LLM reasoning log**: If `HistoryBuffer` captures LLM responses, analyze qualitative reasoning during Minsky trajectory phases.

## §3 Cross-Run Statistical Analysis

For LLM variants, run ≥10 seeds and compute:

```python
import numpy as np

lai_samples = [leverage_amplitude_index(...) for run in runs]
print(f"LAI mean={np.mean(lai_samples):.3f}, std={np.std(lai_samples):.3f}")
```

Compare mean ± std against Rule variant single-seed values for each metric.

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
