# CurrencyCrisis RuleLLM Variant — analysis.md

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

## §2 RuleLLM Variant Notes

**Analysis script**: `CurrencyCrisis/RuleLLM/analysis.py`

Key RuleLLM-variant-specific analysis notes:

- **Rule fidelity check**: Compute AII and PSD for RuleLLM vs. Rule; differences > 10% indicate LLM is overriding embedded rules.
- **SFAF hybrid signal**: RuleLLM SFAF should bracket Rule (mechanical) and LLM (narrative-driven); values outside this range indicate rule-prompt conflict.
- **DER step vs. smooth**: Plot DER curve and compare step-function shape (Rule) vs. smoother profile (LLM); RuleLLM should resemble Rule with minor smoothing.
- **FAS compliance**: RuleLLM FundamentalHedger should hit 8% threshold reliably; FAS deviation from Rule signals LLM threshold drift.
- **WTI symmetry**: RuleLLM symmetric design should maintain WTI ≈ 0; positive WTI indicates rule-constrained attacker still outperforms.

## §3 Output Files

RuleLLM variant produces the following output files in `outputs/CurrencyCrisis/RuleLLM/`:

| File                   | Content                                       |
|------------------------|-----------------------------------------------|
| `price_history.csv`    | Round-by-round price and deviation            |
| `agent_orders.csv`     | Per-agent order action, quantity, round       |
| `agent_wealth.csv`     | Per-agent cash, position, wealth by round     |
| `metrics_summary.json` | AII, PSD, DER, SFAF, FAS, RS, WTI             |
| `llm_responses.jsonl`  | Raw LLM outputs with embedded rule compliance |

## §4 References

All metric definitions with DOI citations: `analysis-bases.md §2`.  
Investor theory references: `simulation-bases.md §4.1–§4.5`.
