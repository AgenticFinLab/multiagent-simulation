# FlashCrash2010 Rule — Analysis

## §1 Objectives

Evaluate whether the rule-based FlashCrash2010 simulation reproduces:
1. Order-book depth collapse consistent with May 6, 2010 event (~90 % depth reduction)
2. Spread widening (10–50 × normal)
3. Multi-wave stop-loss cascade
4. Fundamental-trader-led price recovery

## §2 Metric → Function Mapping

| Metric                 | Function                                                  | Source               |
|------------------------|-----------------------------------------------------------|----------------------|
| Max drawdown           | `max_drawdown(price_history)`                             | analysis-bases.md §2 |
| Depth collapse ratio   | `depth_collapse_ratio(depth_history, base_depth)`         | analysis-bases.md §2 |
| Spread widening factor | `spread_widening_factor(spread_history, normal_spread)`   | analysis-bases.md §2 |
| HFT withdrawal rounds  | `hft_withdrawal_rounds(hft_orders_by_round)`              | analysis-bases.md §2 |
| Cascade trigger rounds | `cascade_trigger_rounds(stoploss_orders_by_round)`        | analysis-bases.md §2 |
| Recovery time          | `recovery_time(price_history, trough_round, fundamental)` | analysis-bases.md §2 |

## §3 Variant-Specific Notes (Rule)

- All thresholds fixed → `max_drawdown` and `recovery_time` are reproducible given the same config
- `depth_collapse_ratio` is determined by `stress_factor` formula (volatility + hft_participation)
- `spread_widening_factor` can reach 50 × at peak stress if both `hft_participation < 0.30` and `volatility > 0.02`
- `cascade_trigger_rounds` shows discrete waves: each StopLossTrader fires at its own `stop_percentage` level
- HFTMarketMaker withdrawal is abrupt (quantity 500 → 0); no gradual retreat

## §4 Expected Ranges (Rule)

| Metric                   | Expected range | Historical benchmark |
|--------------------------|----------------|----------------------|
| `max_drawdown`           | 0.05–0.12      | ~0.09 (DJIA May 6)   |
| `depth_collapse_ratio`   | 0.05–0.20      | ~0.10                |
| `spread_widening_factor` | 5–50 ×         | 10–50 ×              |
| `hft_withdrawal_rounds`  | 5–20 rounds    | ~36 min              |
| Cascade wave count       | 2–5            | Multi-wave           |
| `recovery_time`          | 10–25 rounds   | ~20 min              |

## §5 References

- simulation-bases.md §4 — investor taxonomy and parameter definitions
- analysis-bases.md §2 — metric function signatures
- Kirilenko et al. (2017) doi:10.1111/jofi.12498
- Biais et al. (2015) doi:10.1016/j.jfineco.2015.03.004
