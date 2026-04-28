# FlashCrash Rag — Analysis

## §1 Objectives

Evaluate whether the RAG-augmented flash crash simulation:
1. Reproduces the crash-cascade-recovery profile with historically grounded decisions
2. Shows reduced crash severity or faster recovery compared to Rule/RuleLLM (historical learning effect)
3. Correctly sources `provides_liquidity` from LLM response
4. Demonstrates RAG-specific differentiation: earlier recovery entry, moderated cascade

## §2 Metric → Function Mapping

| Metric                    | Function                                                                      | Source               |
|---------------------------|-------------------------------------------------------------------------------|----------------------|
| Crash depth               | `crash_depth(price_history, fundamental)`                                     | analysis-bases.md §2 |
| Liquidity vacuum duration | `liquidity_vacuum_duration(liquidity_history, low_threshold=2)`               | analysis-bases.md §2 |
| Stop-loss cascade volume  | `stop_loss_cascade_volume(orders_history)`                                    | analysis-bases.md §2 |
| Recovery speed            | `recovery_speed(price_history, trough_round, fundamental)`                    | analysis-bases.md §2 |
| HFT withdrawal fraction   | `hft_withdrawal_fraction(provides_liquidity_history, crash_start, crash_end)` | analysis-bases.md §2 |
| Price amplification ratio | `price_amplification_ratio(observed_max_drop, baseline_max_drop)`             | analysis-bases.md §2 |

## §3 Variant-Specific Notes (Rag)

- RAG-retrieved cases should lead FundamentalTrader to recognise undervaluation earlier → shorter `recovery_speed`
- `provides_liquidity` field must come from `decision["provides_liquidity"]` in LLM response
- Historical cases of cascades may lead StopLossTrader to cut losses earlier (smaller `stop_loss_cascade_volume`) or later (if history suggests holding)
- `price_amplification_ratio` expected lowest among variants if RAG mitigates withdrawal timing
- Compare `liquidity_vacuum_duration` against RuleLLM to test RAG incremental value

## §4 Expected Ranges (Rag)

| Metric                      | Expected range        | vs Rule  | vs RuleLLM         |
|-----------------------------|-----------------------|----------|--------------------|
| `crash_depth`               | 0.04–0.09             | Smaller  | Similar or smaller |
| `liquidity_vacuum_duration` | 3–12 rounds           | Shorter  | Similar            |
| `stop_loss_cascade_volume`  | 200–2000 shares       | Smaller  | Similar            |
| `recovery_speed`            | 6–20 rounds           | Faster   | Slightly faster    |
| `hft_withdrawal_fraction`   | 0.4–0.85 during crash | Lower    | Lower              |
| `price_amplification_ratio` | 1.1–3.0 ×             | Smallest | Lower              |

## §5 References

- simulation-bases.md §4 — investor taxonomy and parameter definitions
- analysis-bases.md §2 — metric function signatures
- Kirilenko et al. (2017) doi:10.1111/jofi.12498
- CFTC-SEC Joint Report (2010)
