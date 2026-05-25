# Liquidity Dry-up Rag Analysis Plan

## §1 Objectives

This analysis checks whether the Rag variant produces a complete, analyzable Liquidity Dry-up trajectory. It maps recorded price, fundamental, and volume series to the metric catalogue in `analysis-bases.md` and supports cross-variant comparison against the Rule baseline.

## §2 Core Metrics

| Metric | Function Contract | Source |
|---|---|---|
| Liquidity Ratio Index | `def liquidity_ratio_index(liquidity_history: list, base_liquidity: float, n_market_makers: int) -> float` | `analysis-bases.md §2.1` |
| Market Maker Withdrawal Fraction | `def market_maker_withdrawal_fraction(agent_states: dict, round_num: int) -> float` | `analysis-bases.md §2.2` |
| Market Price Impact | `def market_price_impact(price_history: list, trade_history: list) -> float` | `analysis-bases.md §2.3` |
| Price-Amplitude Dislocation | `def price_amplitude_dislocation(price_history: list, fundamental: float, lri_history: list, threshold: float = 0.5) -> float` | `analysis-bases.md §2.4` |
| Liquidity Persistence Duration | `def liquidity_persistence_duration(lri_history: list, threshold: float = 0.5) -> int` | `analysis-bases.md §2.5` |
| Wealth Distribution Index | `def wealth_distribution_index(agent_states: dict, final_price: float) -> float` | `analysis-bases.md §2.6` |
| Liquidity Provider Index | `def liquidity_provider_index(trade_history: list) -> dict` | `analysis-bases.md §2.7` |
| RAG Knowledge Effect | `def analyze_rag_knowledge_effect(records: dict) -> dict` | `analysis-bases.md §7` |

## §3 Analysis Dimensions

Analysis is performed by round, by agent type, by market phase, and by variant. The main comparison is whether Rag preserves price deviation and mechanism intensity while changing the distribution of order flow relative to the deterministic baseline.

## §4 Phase Analysis

The phase framework follows `analysis-bases.md §4`: initialization, mechanism activation, amplification or correction, and terminal stabilization. Each phase should be measured with state, activity, and dispersion metrics listed in §2.

## §5 Cross-Variant Comparison

Compare Rule, LLM, RuleLLM, and Rag on mechanism timing, peak intensity, final state, activity level, and structural quality. LLM-family variants should be reviewed for parse failures, explicit fallback counts, and whether stochastic decisions remain coherent.

## §6 Expected Results and Validation Criteria

Expected ranges and failure signs are defined in `analysis-bases.md §6`. A full experiment should record 200 rounds, finite state values, non-trivial agent activity, and scenario-specific behavior consistent with the mechanism in `simulation-bases.md`.

## §7 Visualization Catalogue

Required outputs are `summary.json`, `00_investor_bids.png`, `01_liquiditydryup_dynamics.png`, `02_liquiditydryup_analysis.png`, `03_summary.png`, and `rag_stats.json`.
