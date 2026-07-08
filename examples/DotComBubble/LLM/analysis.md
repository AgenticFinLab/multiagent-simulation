# DotComBubble LLM Variant — analysis.md

## §1 Analysis Objectives

Measure how LLM persona-driven decision-making shapes bubble amplitude, duration, crash severity, and momentum amplification relative to the Rule baseline. All metrics defined in `analysis-bases.md §2`.

## §2 Metric → Function Mapping

| Metric                              | Function                                                                   | analysis-bases.md ref |
|-------------------------------------|----------------------------------------------------------------------------|-----------------------|
| BAI (Bubble Amplitude Index)        | `bubble_amplitude_index(price_history, fundamental)`                       | §2 BAI                |
| BD (Bubble Duration)                | `bubble_duration(price_history, fundamental, bubble_threshold=0.10)`       | §2 BD                 |
| CS (Crash Severity)                 | `crash_severity(price_history)`                                            | §2 CS                 |
| MAF (Momentum Amplification Factor) | `momentum_amplification_factor(agent_orders, bubble_rounds)`               | §2 MAF                |
| SSR (Short-Seller Resistance)       | `short_seller_resistance(short_seller_orders, overvaluation_rounds)`       | §2 SSR                |
| RT (Recovery Time)                  | `recovery_time(price_history, fundamental, recovery_threshold=0.10)`       | §2 RT                 |
| AQR (API Quality)                   | `api_quality(agent_orders)`                                                | §2 AQR                |

## §3 LLM-Variant-Specific Notes

- **Stochastic paths**: Report replicated distributions rather than treating one sampled path as representative.
- **Persona attribution**: MAF uses recorded momentum-follower buy volume; SSR uses the constrained skeptical seller's recorded sell actions.
- **Fail-fast quality**: Provider or parse failures stop the run after the configured retry count; they are not converted into hidden hold actions.
- **Contract audit**: AQR verifies that every persisted decision has valid action, price, quantity, reasoning, and analysis fields.
- **Cross-run replication**: Re-run at least 3× and report mean ± standard deviation for BAI and BD.

## §4 Diagnostic Interpretation

| Metric | Review signal |
|--------|---------------|
| BAI | `< 0.10` suggests no visible bubble; `> 2.0` requires stability review. |
| BD | `0` means no persistent bubble; a near-full-run value suggests no resolution. |
| CS | `< 0.30` is a mild correction; `> 0.80` requires numerical-stability review. |
| MAF | Near zero means the momentum persona did not materially amplify bubble buying. |
| SSR | Zero means the inventory-constrained skeptical seller supplied no overvaluation sell pressure. |
| RT | `null` means no post-trough recovery within the recorded horizon. |
| AQR | `contract_compliance_rate` must equal `1.0` for an accepted run. |

## §5 References

See `analysis-bases.md §2` for full metric derivations and `simulation-bases.md §4` for agent parameter sources.

## §6 Cross-Variant Comparison

| Comparison | Interpretation |
|---|---|
| LLM vs Rule | Measures narrative-only reasoning effects without embedded formulas. |
| LLM vs RuleLLM | Measures the stabilizing effect of explicit decision rules. |
| LLM vs Rag | Measures whether retrieved historical knowledge changes persona-only behavior. |

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Audit parse failures and retry counts before acceptance; deterministic parser or provider failures should fail fast rather than become hidden holds.
- Confirm accepted decisions produce valid `action` and numeric `quantity` fields.
- Confirm `summary.json` contains BAI, BD, CS, MAF, SSR, RT, and AQR.
- Review action distribution for excessive holds that would indicate unusable output quality.

## §8 Running The Analysis

```bash
python -m examples.DotComBubble.LLM.analysis \
  -c configs/DotComBubble/LLM/simulation.yml
```

Outputs are written to `EXPERIMENT/DotComBubble/LLM/analysis/summary.json` and `dotcombubble_llm_dynamics.png` by default.
