# FlashCrash2010 Rag — Analysis

## §1 Objectives

Evaluate whether the RAG-augmented FlashCrash2010 simulation:
1. Reproduces the depth collapse and spread widening with historically grounded decisions
2. Shows reduced crash severity or faster recovery compared to Rule/RuleLLM
3. Correctly sources `provides_liquidity` from LLM response for depth computation
4. Demonstrates RAG-specific value: earlier FT entry, moderated cascade

## §2 Metric → Function Mapping

| Metric                 | Function                                                  | Source               |
|------------------------|-----------------------------------------------------------|----------------------|
| Max drawdown           | `max_drawdown(price_history)`                             | analysis-bases.md §2 |
| Depth collapse ratio   | `depth_collapse_ratio(depth_history, base_depth)`         | analysis-bases.md §2 |
| Spread widening factor | `spread_widening_factor(spread_history, normal_spread)`   | analysis-bases.md §2 |
| HFT withdrawal rounds  | `hft_withdrawal_rounds(hft_orders_by_round)`              | analysis-bases.md §2 |
| Cascade trigger rounds | `cascade_trigger_rounds(stoploss_orders_by_round)`        | analysis-bases.md §2 |
| Recovery time          | `recovery_time(price_history, trough_round, fundamental)` | analysis-bases.md §2 |

## §3 Variant-Specific Notes (Rag)

- RAG-retrieved May 6, 2010 cases should inform FundamentalTrader to buy at higher price deviation → shorter `recovery_time`
- `provides_liquidity` field must come from `decision["provides_liquidity"]` in LLM response
- Historical cases of HFT withdrawal may lead HFTMarketMaker to withdraw earlier (anticipatory) — test whether this increases or decreases `max_drawdown`
- Compare `hft_withdrawal_rounds` against RuleLLM to measure RAG incremental value
- `depth_collapse_ratio` may be slightly higher (shallower collapse) if RAG prevents full withdrawal

## §4 Expected Ranges (Rag)

| Metric                   | Expected range | vs Rule          | vs RuleLLM         |
|--------------------------|----------------|------------------|--------------------|
| `max_drawdown`           | 0.03–0.09      | Smaller          | Similar or smaller |
| `depth_collapse_ratio`   | 0.08–0.30      | Higher min depth | Similar            |
| `spread_widening_factor` | 3–35 ×         | Lower peak       | Lower              |
| `hft_withdrawal_rounds`  | 2–12 rounds    | Fewer            | Fewer              |
| Cascade wave count       | 1–4            | Fewer waves      | Similar            |
| `recovery_time`          | 5–18 rounds    | Fastest          | Faster             |

## §5 References

- simulation-bases.md §4 — investor taxonomy and parameter definitions
- analysis-bases.md §2 — metric function signatures
- Kirilenko et al. (2017) doi:10.1111/jofi.12498
- CFTC-SEC Joint Report (2010)
- Biais et al. (2015) doi:10.1016/j.jfineco.2015.03.004
