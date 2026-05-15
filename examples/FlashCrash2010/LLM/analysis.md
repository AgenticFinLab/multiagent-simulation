# FlashCrash2010 LLM — Analysis

## §1 Objectives

Evaluate whether the LLM-driven FlashCrash2010 simulation:
1. Reproduces the order-book depth collapse and spread widening pattern
2. Shows LLM-induced variability compared to Rule baseline
3. Correctly outputs `provides_liquidity` and `agent_type` fields for market depth computation
4. Demonstrates emergent qualitative judgment (e.g., "too volatile to provide liquidity")

## §2 Metric → Function Mapping

| Metric                 | Function                                                  | Source               |
|------------------------|-----------------------------------------------------------|----------------------|
| Max drawdown           | `max_drawdown(price_history)`                             | analysis-bases.md §2 |
| Depth collapse ratio   | `depth_collapse_ratio(depth_history, base_depth)`         | analysis-bases.md §2 |
| Spread widening factor | `spread_widening_factor(spread_history, normal_spread)`   | analysis-bases.md §2 |
| HFT withdrawal rounds  | `hft_withdrawal_rounds(hft_orders_by_round)`              | analysis-bases.md §2 |
| Cascade trigger rounds | `cascade_trigger_rounds(stoploss_orders_by_round)`        | analysis-bases.md §2 |
| Recovery time          | `recovery_time(price_history, trough_round, fundamental)` | analysis-bases.md §2 |

## §3 Variant-Specific Notes (LLM)

- `provides_liquidity` sourced from `decision["provides_liquidity"]` — must be boolean in LLM response
- `agent_type` field from LLM response drives `hft_participation` in market depth formula
- High stochasticity: run ≥5 seeds; report mean ± std for all metrics
- LLM may fail to "crash" if it does not recognise stress signals → compare `max_drawdown` distribution
- Check for prompt-induced bias: HFTMarketMaker system prompt must describe the stress-withdrawal behavior

## §4 Expected Ranges (LLM)

| Metric                   | Expected range | vs Rule                          |
|--------------------------|----------------|----------------------------------|
| `max_drawdown`           | 0.04–0.14      | Similar mean; higher variance    |
| `depth_collapse_ratio`   | 0.05–0.30      | Similar mean; higher variance    |
| `spread_widening_factor` | 3–50 ×         | Similar; depends on LLM judgment |
| `hft_withdrawal_rounds`  | 3–25 rounds    | Variable                         |
| Cascade wave count       | 1–5            | Variable                         |
| `recovery_time`          | 8–30 rounds    | Variable                         |

## §5 References

- simulation-bases.md §4 — investor taxonomy and parameter definitions
- analysis-bases.md §2 — metric function signatures
- Kirilenko et al. (2017) doi:10.1111/jofi.12498
- CFTC-SEC Joint Report (2010)
