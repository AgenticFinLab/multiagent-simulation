# FlashCrash2010 RuleLLM — Analysis

## §1 Objectives

Evaluate whether the RuleLLM hybrid:
1. Preserves the depth-collapse and spread-widening profile relative to Rule baseline
2. Shows LLM-induced attenuation of crash severity (delayed withdrawal, partial stop-loss)
3. Correctly sources `provides_liquidity` from LLM response for depth computation
4. Provides measurable improvement in recovery speed vs pure Rule

## §2 Metric → Function Mapping

| Metric                 | Function                                                  | Source               |
|------------------------|-----------------------------------------------------------|----------------------|
| Max drawdown           | `max_drawdown(price_history)`                             | analysis-bases.md §2 |
| Depth collapse ratio   | `depth_collapse_ratio(depth_history, base_depth)`         | analysis-bases.md §2 |
| Spread widening factor | `spread_widening_factor(spread_history, normal_spread)`   | analysis-bases.md §2 |
| HFT withdrawal rounds  | `hft_withdrawal_rounds(hft_orders_by_round)`              | analysis-bases.md §2 |
| Cascade trigger rounds | `cascade_trigger_rounds(stoploss_orders_by_round)`        | analysis-bases.md §2 |
| Recovery time          | `recovery_time(price_history, trough_round, fundamental)` | analysis-bases.md §2 |

## §3 Variant-Specific Notes (RuleLLM)

- LLM override of `provides_liquidity` at HFTMarketMaker is the key differentiator vs Rule
- `provides_liquidity` must come from `decision["provides_liquidity"]` not rule logic
- LLM hesitation in withdrawal → `hft_withdrawal_rounds` shorter than Rule
- StopLossTrader LLM hold → `cascade_trigger_rounds` spread over more rounds but total volume smaller
- Run ≥3 seeds; compare mean and std to Rule baseline

## §4 Expected Ranges (RuleLLM)

| Metric                   | Expected range | vs Rule                       |
|--------------------------|----------------|-------------------------------|
| `max_drawdown`           | 0.04–0.10      | Slightly smaller              |
| `depth_collapse_ratio`   | 0.08–0.25      | Slightly higher minimum depth |
| `spread_widening_factor` | 4–40 ×         | Slightly lower peak           |
| `hft_withdrawal_rounds`  | 3–15 rounds    | Shorter                       |
| Cascade wave count       | 2–4            | Similar structure             |
| `recovery_time`          | 8–20 rounds    | Faster                        |

## §5 References

- simulation-bases.md §4 — investor taxonomy and parameter definitions
- analysis-bases.md §2 — metric function signatures
- Kirilenko et al. (2017) doi:10.1111/jofi.12498
- Biais et al. (2015) doi:10.1016/j.jfineco.2015.03.004
