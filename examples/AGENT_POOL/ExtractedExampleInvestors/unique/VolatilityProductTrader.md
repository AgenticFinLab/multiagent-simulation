# Volatility-product, volatility-management, and equity de-risking agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Volatility-product, volatility-management, and equity de-risking agents |
| Merged profiles | 5 |
| Scenarios | VolatilityClustering, Volmageddon |
| Observed names | Equity Trader, Long Vol Hedger, Slow Adapter, Vol ETN Manager, Volatility Trader |

## Consolidated Definition and Goals

- **VolatilityClustering / Slow Adapter**: **Summary**: Updates perceived value gradually after market moves. **Theoretical and Empirical Basis**: Adaptive expectations and delayed information processing. **Design Purpose**: Extend the effect of shocks over several rounds. **Behavioral Framework**: Uses `lookback_window`, `update_weight`, and `base_position_size`. **Decision Process**: Blend fundamental value with a long moving average; trade only when the deviation is material. **Worked Numerical Example**: After a price shock, the moving average remains away from fundamental and influences orders for multiple rounds. **Academic References**: Hommes (2006); Brock and Hommes (1998), DOI: 10.1016/S0165-1889(98)00011-6.
- **VolatilityClustering / Volatility Trader**: **Summary**: Changes exposure based on volatility regime. **Theoretical and Empirical Basis**: Volatility timing and volatility mean-reversion strategies. **Design Purpose**: Make volatility state directly affect order flow. **Behavioral Framework**: Uses `vol_lookback`, `high_vol_threshold`, `low_vol_threshold`, and `base_position_size`. **Decision Process**: Sell or reduce exposure when volatility is high relative to its moving average; buy or increase exposure in low-volatility regimes. **Worked Numerical Example**: If current volatility is 1.8 times its recent average and the high threshold is 1.5, the trader sells. **Academic References**: Engle (1982), DOI: 10.2307/1912773; Bollerslev (1986), DOI: 10.1016/0304-4076(86)90063-1; volatility timing literature.
- **Volmageddon / Equity Trader**: **Summary**: An equity-market participant that de-risks when volatility stress breaches risk limits and buys when prices are deeply below fundamental value.
- **Volmageddon / Long Vol Hedger**: **Summary**: A portfolio-insurance investor that owns volatility exposure as a hedge and can take profits after spikes.
- **Volmageddon / Vol ETN Manager**: **Summary**: A mechanical inverse-volatility product manager whose rebalancing creates procyclical volatility demand.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.4.
- LLM SlowAdapter. Theory: simulation-bases.md Section 4.4.
- Hybrid SlowAdapter. Theory: simulation-bases.md Section 4.4.
- RAG SlowAdapter. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.5.
- LLM VolatilityTrader. Theory: simulation-bases.md Section 4.5.
- Hybrid VolatilityTrader. Theory: simulation-bases.md Section 4.5.
- RAG VolatilityTrader. Theory: simulation-bases.md Section 4.5.
- Theory: simulation-bases.md Section 4.5
- Theory: simulation-bases.md Section 4.3
- Theory: simulation-bases.md Section 4.2

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| VolatilityClustering | Slow Adapter | [VolatilityClustering__SlowAdapter.md](../VolatilityClustering__SlowAdapter.md) |
| VolatilityClustering | Volatility Trader | [VolatilityClustering__VolatilityTrader.md](../VolatilityClustering__VolatilityTrader.md) |
| Volmageddon | Equity Trader | [Volmageddon__EquityTrader.md](../Volmageddon__EquityTrader.md) |
| Volmageddon | Long Vol Hedger | [Volmageddon__LongVolHedger.md](../Volmageddon__LongVolHedger.md) |
| Volmageddon | Vol ETN Manager | [Volmageddon__VolETNManager.md](../Volmageddon__VolETNManager.md) |

