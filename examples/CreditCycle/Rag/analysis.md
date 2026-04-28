# CreditCycle Rag Variant — analysis.md

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

## §2 Rag Variant Notes

**Analysis script**: Uses same `analysis.py` as Rule variant — no separate analysis.py needed.

Key Rag-specific notes:

- **RAG retrieval audit**: Log which passages are retrieved during each bust onset — compare Minsky-related retrieval frequency to cycle timing.
- **MFS with RAG**: If RagLLMMinskyBorrower retrieves Minsky passages early, MFS may be lower (agent reduces leverage proactively).
- **CCOR with historical grounding**: CounterCyclicalLender may time crisis deployment more precisely; expect CCOR ≥ LLM baseline.
- **`{rag_context}` logging**: Capture retrieved passages per round in `HistoryBuffer` for qualitative analysis.

## §3 RAG-Specific Analysis Procedure

```python
# Audit RAG retrieval patterns
rag_log = load_rag_history("CreditCycle/Rag/rag_retrieval_log.jsonl")
minsky_retrievals = [r for r in rag_log if "Minsky" in r["retrieved_content"]]
for r in minsky_retrievals:
    print(f"Round {r['round']}: {r['agent']} retrieved Minsky passage at δ={r['deviation']:.3f}")
```

Cross-reference retrieval round against crisis onset round to measure RAG anticipation lead time.

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
