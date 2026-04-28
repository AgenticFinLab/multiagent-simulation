# CurrencyCrisis LLM Variant — analysis.md

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

## §2 LLM Variant Notes

**Analysis script**: `CurrencyCrisis/LLM/analysis.py`

Key LLM-variant-specific analysis notes:

- **AII variance**: LLM attack depth is non-deterministic; run AII across multiple seeds and report mean ± std.
- **SFAF narrative analysis**: Compare SFAF to Rule baseline (≈ 0.6–0.9); SFAF > 1.5 in LLM indicates emergent expectation coordination.
- **DER adaptive defence**: LLMCentralBankDefender may not follow two-tier rule; DER may be smoother or front-loaded depending on LLM reasoning.
- **FAS consistency**: Check FAS across runs; if LLMFundamentalHedger breaks persona and sells during attacks, FAS < Rule baseline signals persona fragility.
- **WTI attacker advantage**: LLM SpeculativeAttacker may reason more aggressively and produce positive WTI (attackers profit) more often.

## §3 Output Files

LLM variant produces the following output files in `outputs/CurrencyCrisis/LLM/`:

| File                   | Content                                            |
|------------------------|----------------------------------------------------|
| `price_history.csv`    | Round-by-round price and deviation                 |
| `agent_orders.csv`     | Per-agent order action, quantity, round            |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round          |
| `metrics_summary.json` | AII, PSD, DER, SFAF, FAS, RS, WTI                  |
| `llm_responses.jsonl`  | Raw LLM outputs with thinking and parsed decisions |

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
