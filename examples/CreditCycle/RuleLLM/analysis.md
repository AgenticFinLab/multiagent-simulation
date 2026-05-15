# CreditCycle RuleLLM Variant — analysis.md

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

## §2 RuleLLM Variant Notes

**Analysis script**: Uses same `analysis.py` as Rule variant — no separate analysis.py needed.

Key RuleLLM-specific notes:

- **Rule-anchored MFS**: `stable_rounds` is tracked in rule logic embedded in prompt; MFS is available via rule-side state tracking.
- **LAI close to Rule**: Expect LAI ≈ Rule baseline (rule anchoring prevents extreme LLM drift).
- **CCOR stability**: Counter-cyclical behavior rule-constrained; CCOR expected close to Rule baseline.
- **Qualitative MFS analysis**: LLM logs during stable phases reveal Minsky narrative richness — analyze textual reasoning for pattern detection.

## §3 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
