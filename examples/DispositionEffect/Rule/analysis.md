# DispositionEffect Rule Variant — analysis.md

## §1 Overview

The Rule variant uses `Rule/analysis.py` as the authoritative analysis module
for all DispositionEffect variants. It loads market prices and per-player order
payloads, computes PGR/PLR-style disposition metrics, writes `summary.json`, and
generates seven diagnostic figures. This file maps the concrete implementation
back to `analysis-bases.md`.

## §2 Metrics and Functions

| Metric | Function | analysis-bases.md Ref |
|---|---|---|
| Proportion of Gains Realized (PGR) | `calculate_pgr_plr()` | §2.1 |
| Proportion of Losses Realized (PLR) | `calculate_pgr_plr()` | §2.2 |
| Disposition Coefficient (DC) | `generate_summary()` | §2.3 |
| PGR/PLR Ratio | `calculate_pgr_plr()` | §2.4 |
| Holding Period Asymmetry (HPA) | `holding_period_asymmetry()` | §2.5 |
| Performance Drag Index (PDI) | `calculate_extended_metrics()` and `terminal_wealth()` | §2.6 |
| Tax Reversal Index (TRI) | `calculate_extended_metrics()` | §2.7 |

## §3 Data Loading Contract

`load_simulation_data(config)` reads the coordinator `price` batch and every
player turn payload. Each trade record must contain `bid_price`, `quantity`,
`strategy`, and an injected `round`. Missing required fields raise errors rather
than being silently replaced.

## §4 Rule Variant Notes

- PGR/PLR are derived from the deterministic threshold behavior implemented in
  `Rule/players.py`.
- Initial cash, position, purchase price, and fundamental value are loaded from
  the expanded player configuration; analysis contains no scenario defaults.
- DispositionInvestor keeps its configured initial purchase-price anchor,
  matching `move_reference=False`; other buying strategies use average cost.
- The Rule output is the comparison baseline for LLM, RuleLLM, and Rag.
- Market stochasticity comes from news and noise; investor rules remain
  deterministic for a given observed state.

## §5 Output Files

| File | Content |
|---|---|
| `summary.json` | Price statistics, PGR, PLR, DC, ratio, HPA, PDI, TRI, wealth, and validation score |
| `fig1_price_dynamics.png` | Price path, fundamental level, returns, rolling volatility |
| `fig2_pgr_plr_comparison.png` | PGR/PLR and DC by strategy |
| `fig3_trading_activity.png` | Buy/sell counts and traded volume |
| `fig4_return_distribution.png` | Return distribution and summary statistics |
| `fig5_disposition_ratio.png` | PGR/PLR ratio and realized/paper gain-loss pools |
| `fig6_portfolio_evolution.png` | Position and equity value trajectory |
| `fig7_sell_gain_loss.png` | Sell events by gain/loss territory |

## §6 Validation Criteria

`generate_summary()` calls `validate_disposition_effect()` with the
DispositionInvestor PGR, PLR, and DC. A valid Rule run should show PGR > PLR and
roughly match the Odean-inspired calibration bands in `analysis-bases.md §6`.

## §7 References

Metric definitions and DOI references are centralized in `analysis-bases.md §2`.
Investor theory references are centralized in `simulation-bases.md §4.1–§4.5`.
