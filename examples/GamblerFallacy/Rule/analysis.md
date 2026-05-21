# GamblerFallacy Rule — Analysis Guide

## §1 Analysis Objectives

The Rule analysis verifies the deterministic baseline described in `../analysis-bases.md §1`: streak-driven deviation, hot-hand momentum, arbitrage correction, volatility amplification, and wealth redistribution.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Reference |
|---|---|---|
| Gambler's Fallacy Index | `gambler_fallacy_index(price_history, fundamental)` | §2.1 |
| Streak Asymmetry Ratio | `streak_asymmetry_ratio(price_history, fundamental)` | §2.2 |
| Hot Hand Momentum | `hot_hand_momentum(net_demand_history, dev_history, threshold=0.02)` | §2.3 |
| Arbitrage Correction Index | `arbitrage_correction_index(dev_history, lookahead=5, threshold=0.05)` | §2.4 |
| Volatility Amplification Factor | `volatility_amplification_factor(price_history, dev_history, threshold=0.02)` | §2.5 |
| Wealth Distribution Index | `wealth_distribution_index(agent_wealth)` | §2.6 |

## §3 Data Loading and Structural Checks

`analysis.py → load_simulation_data(record_path)` loads JSON records from a record directory. Metric calculation requires a non-empty `price_history` and positive `fundamental`.

## §4 Phase Analysis

Phase analysis follows `analysis-bases.md §4`: streak emergence, biased demand amplification, arbitrage correction, and final wealth redistribution.

## §5 Cross-Variant Comparison

Rule is the comparison anchor for LLM, RuleLLM, and RAG. Later variants should be compared to Rule on GFI, SAR, HHM, ACI, VAF, and WDI.

## §6 Expected Results and Validation

Expected Rule behavior includes nonzero GFI, active biased demand during streak-like deviations, rational correction in some high-deviation episodes, and moderate wealth inequality. Empty price history, missing orders, or zero deviation across all rounds indicates implementation failure.

## §7 Visualization Catalogue

`analysis.py → main()` uses the shared standard analysis contract to create
`summary.json`, a structured validation console report, and fixed PNG outputs:
`00_investor_bids.png`, `01_gamblerfallacy_dynamics.png`,
`02_gamblerfallacy_analysis.png`, and `03_summary.png`. The legacy
`create_visualizations(data, output_dir)` helper remains available for focused
price/fundamental plotting in ad hoc analysis.
