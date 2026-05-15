# FlashCrash Rule — Analysis

## §1 Objectives

Evaluate whether the rule-based flash crash simulation reproduces:
1. A distinct crash-cascade-recovery profile
2. Liquidity vacuum driven by MarketMaker withdrawal
3. Multi-wave stop-loss cascade
4. Fundamental-trader-led recovery

## §2 Metric → Function Mapping

| Metric                    | Function                                                                      | Source               |
|---------------------------|-------------------------------------------------------------------------------|----------------------|
| Crash depth               | `crash_depth(price_history, fundamental)`                                     | analysis-bases.md §2 |
| Liquidity vacuum duration | `liquidity_vacuum_duration(liquidity_history, low_threshold=2)`               | analysis-bases.md §2 |
| Stop-loss cascade volume  | `stop_loss_cascade_volume(orders_history)`                                    | analysis-bases.md §2 |
| Recovery speed            | `recovery_speed(price_history, trough_round, fundamental)`                    | analysis-bases.md §2 |
| HFT withdrawal fraction   | `hft_withdrawal_fraction(provides_liquidity_history, crash_start, crash_end)` | analysis-bases.md §2 |
| Price amplification ratio | `price_amplification_ratio(observed_max_drop, baseline_max_drop)`             | analysis-bases.md §2 |

## §3 Variant-Specific Notes (Rule)

- All thresholds are fixed → `crash_depth` and `recovery_speed` are reproducible given the same config
- `liquidity_vacuum_duration` is determined entirely by `volatility_threshold` distribution across MarketMaker instances
- Stop-loss cascade waves are discrete: each `StopLossTrader` with a different `stop_loss_percent` fires at a predictable price level
- `price_amplification_ratio` is highest in Rule variant (no agent can override the multiplier)
- Recovery onset is deterministic: FundamentalTrader entry fires when `deviation > value_threshold`

## §4 Expected Ranges (Rule)

| Metric                      | Expected range       |
|-----------------------------|----------------------|
| `crash_depth`               | 0.05–0.12 (5–12 %)   |
| `liquidity_vacuum_duration` | 5–20 rounds          |
| `stop_loss_cascade_volume`  | 500–3000 shares      |
| `recovery_speed`            | 10–30 rounds         |
| `hft_withdrawal_fraction`   | 0.6–1.0 during crash |
| `price_amplification_ratio` | 1.5–4.0 ×            |

## §5 References

- simulation-bases.md §4 — investor taxonomy and parameter definitions
- analysis-bases.md §2 — metric function signatures
- Kirilenko et al. (2017) doi:10.1111/jofi.12498
- Grossman & Miller (1988) doi:10.1111/j.1540-6261.1988.tb02607.x
