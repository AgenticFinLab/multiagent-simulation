# CurrencyCrisis Rag Variant — analysis.md

## §1 Metrics and Functions

| Metric                                      | Function                                                                      | analysis-bases.md Ref |
|---------------------------------------------|-------------------------------------------------------------------------------|-----------------------|
| Attack Intensity Index (AII)                | `attack_intensity_index(price_history, fundamental)`                          | §2.1                  |
| Peg Survival Duration (PSD)                 | `peg_survival_duration(price_history, fundamental, breach_threshold=-0.05)`   | §2.2                  |
| Defense Exhaustion Rate (DER)               | `defense_exhaustion_rate(defender_cash_history, initial_cash, crisis_rounds)` | §2.3                  |
| Self-Fulfilling Amplification Factor (SFAF) | `self_fulfilling_amplification_factor(agent_volume_by_type)`                  | §2.4                  |
| Fundamental Anchor Strength (FAS)           | `fundamental_anchor_strength(hedger_orders, attack_phase_rounds)`             | §2.5                  |
| Recovery Speed (RS)                         | `recovery_speed(price_history, fundamental, recovery_threshold=0.03)`         | §2.6                  |
| Wealth Transfer Index (WTI)                 | `wealth_transfer_index(agent_final_states, final_price, initial_wealth)`      | §2.7                  |

## §2 Rag Variant Notes

**Analysis script**: `CurrencyCrisis/Rag/analysis.py`

Key Rag-variant-specific analysis notes:

- **RAG moderation of AII**: Compare AII(Rag) vs. AII(LLM); lower AII in Rag confirms historical case retrieval moderates attack aggressiveness.
- **FAS enhancement**: Rag FAS expected highest across variants; lower FAS in Rag than LLM indicates knowledge store retrieval is not improving anchor strength.
- **SFAF knowledge effect**: Rag SFAF < LLM SFAF confirms RAG coordination failure cases reduce self-fulfilling amplification.
- **DER historical patterns**: Plot DER curve; Rag DER may show gradual exhaustion matching retrieved historical patterns rather than step-function (Rule) or irregular (LLM).
- **Retrieved context logging**: Log `retrieved_context` per agent per round; analyze which historical cases were retrieved during attack and crisis phases.

## §3 Output Files

Rag variant produces the following output files in `outputs/CurrencyCrisis/Rag/`:

| File                   | Content                                              |
|------------------------|------------------------------------------------------|
| `price_history.csv`    | Round-by-round price and deviation                   |
| `agent_orders.csv`     | Per-agent order action, quantity, round              |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round            |
| `metrics_summary.json` | AII, PSD, DER, SFAF, FAS, RS, WTI                    |
| `llm_responses.jsonl`  | Raw LLM outputs with retrieved context and decisions |
| `retrieval_log.jsonl`  | Per-round retrieved knowledge chunks per agent       |

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
