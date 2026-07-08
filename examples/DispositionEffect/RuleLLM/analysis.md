# DispositionEffect RuleLLM — Analysis Documentation

## 1. Overview

`RuleLLM/analysis.py` reuses the validated functions in `Rule/analysis.py`, so all variants calculate the same quantities from the same record schema. RuleLLM adds one interpretation question: whether bounded LLM sizing preserves the direction and approximate magnitude of the deterministic benchmark.

## 2. Metric Implementation

| analysis-bases.md | Metric | Function path used by `calculate_metrics()` | Required data |
|---|---|---|---|
| §2.1 | PGR | `calculate_pgr_plr()` | trades, prices, purchase prices |
| §2.2 | PLR | `calculate_pgr_plr()` | trades, prices, purchase prices |
| §2.3 | Disposition coefficient | `generate_summary()` (`pgr - plr`) | aggregated strategy results |
| §2.4 | PGR/PLR ratio | `aggregate_strategy_results()` | realized and paper gains/losses |
| §2.5 | Holding-period asymmetry | `holding_period_asymmetry()` via `calculate_extended_metrics()` | FIFO lots and trade rounds |
| §2.6 | Performance drag index | `terminal_wealth()` via `calculate_extended_metrics()` | trades, final price, endowments |
| §2.7 | Tax reversal index | `calculate_extended_metrics()` | tax-aware and disposition PLR |

`RuleLLM/analysis.py` invokes the shared loader, metrics, and visualization functions directly. If a resumed run's `HistoryBuffer` contains fewer prices than the coordinator turn log, its local loader reconstructs the ordered price series from required `market_data.price` fields. Missing required records or archetypes still fail loudly instead of producing fallback statistics.

## 3. Dimension-by-Dimension Analysis

| analysis-bases.md dimension | Comparison |
|---|---|
| Investor type | disposition, rational, tax-aware, passive, institutional |
| Gain/loss domain | paper and realized gains versus losses |
| Time | price path, holding rounds, and trading activity |
| Performance | terminal mark-to-market wealth and PDI |
| Variant | RuleLLM results against the Rule baseline |

## 4. Variant-Specific Observable Phenomena

- Rule direction compliance: non-zero order signs should match `_rule_quantity()`.
- Sizing envelope: before solvency constraints, magnitude should remain within 80–120% of the Rule quantity.
- Explanation fidelity: `<analysis>` should name the active rule branch and configured trigger.
- Passive invariant: `RuleLLMIndexHolder` should never create a non-zero order.
- Bias preservation: disposition PGR should exceed PLR, while tax-aware PLR should be relatively higher.

## 5. Scaling and Sensitivity Analysis

For smoke tests use 5 rounds; substantive PGR/PLR estimates require the configured 200 rounds or more. Report denominator counts with each rate because short runs may contain no gain or loss opportunities.

Recommended sweeps vary one sourced parameter at a time: `gain_threshold`, `loss_threshold`, sell fractions, `rebalance_threshold`, `tax_loss_threshold`, and the institutional thresholds. Keep the ±20% RuleLLM clamp fixed when comparing prompt fidelity.

## 6. Output Files Reference

Analysis writes `summary.json` plus seven standard figures under `EXPERIMENT/DispositionEffect/RuleLLM/analysis/`. The figures cover price dynamics, PGR/PLR, trading activity, returns, disposition ratios, portfolio evolution, and sell gain/loss states.

## 7. Cross-Variant Comparison Notes

Use identical seeds, rounds, population composition, and market parameters when comparing RuleLLM with Rule, LLM, or Rag. Differences should be attributed to the decision mechanism only after verifying equal opportunity denominators and successful response parsing. Definitions and empirical benchmarks remain those in `analysis-bases.md` §2.
