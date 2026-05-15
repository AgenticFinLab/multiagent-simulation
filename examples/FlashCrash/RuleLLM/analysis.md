# FlashCrash RuleLLM — Analysis

## §1 Objectives

Evaluate whether the RuleLLM hybrid correctly:
1. Preserves the crash-cascade-recovery profile relative to the Rule baseline
2. Shows meaningful LLM-induced variability (earlier/later withdrawal, partial cascade)
3. Produces a `provides_liquidity` field correctly sourced from LLM response
4. Demonstrates measurable differences from pure-Rule and pure-LLM variants

## §2 Metric → Function Mapping

| Metric                    | Function                                                                      | Source               |
|---------------------------|-------------------------------------------------------------------------------|----------------------|
| Crash depth               | `crash_depth(price_history, fundamental)`                                     | analysis-bases.md §2 |
| Liquidity vacuum duration | `liquidity_vacuum_duration(liquidity_history, low_threshold=2)`               | analysis-bases.md §2 |
| Stop-loss cascade volume  | `stop_loss_cascade_volume(orders_history)`                                    | analysis-bases.md §2 |
| Recovery speed            | `recovery_speed(price_history, trough_round, fundamental)`                    | analysis-bases.md §2 |
| HFT withdrawal fraction   | `hft_withdrawal_fraction(provides_liquidity_history, crash_start, crash_end)` | analysis-bases.md §2 |
| Price amplification ratio | `price_amplification_ratio(observed_max_drop, baseline_max_drop)`             | analysis-bases.md §2 |

## §3 Variant-Specific Notes (RuleLLM)

- The rule-level threshold provides a lower bound on `crash_depth`; LLM can only reduce (not eliminate) the crash
- `provides_liquidity` must come from `decision["provides_liquidity"]` — not from rule logic directly — to allow LLM override
- LLM override at MarketMaker is the primary differentiator: if LLM delays withdrawal by 2–3 rounds, `liquidity_vacuum_duration` will be shorter
- `stop_loss_cascade_volume` may be reduced if LLM prevents full position liquidation
- Run multiple seeds to assess variability vs Rule variant

## §4 Expected Ranges (RuleLLM)

| Metric                      | Expected range       | vs Rule                         |
|-----------------------------|----------------------|---------------------------------|
| `crash_depth`               | 0.04–0.10            | Slightly smaller                |
| `liquidity_vacuum_duration` | 3–15 rounds          | Shorter (LLM delays withdrawal) |
| `stop_loss_cascade_volume`  | 300–2500 shares      | Smaller                         |
| `recovery_speed`            | 8–25 rounds          | Slightly faster                 |
| `hft_withdrawal_fraction`   | 0.5–0.9 during crash | Slightly lower                  |
| `price_amplification_ratio` | 1.2–3.5 ×            | Smaller than Rule               |

## §5 References

- simulation-bases.md §4 — investor taxonomy and parameter definitions
- analysis-bases.md §2 — metric function signatures
- Kirilenko et al. (2017) doi:10.1111/jofi.12498
- Grossman & Miller (1988) doi:10.1111/j.1540-6261.1988.tb02607.x
