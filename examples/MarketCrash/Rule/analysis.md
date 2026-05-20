# MarketCrash Rule — Analysis Documentation

## §1 Analysis Objectives

Evaluate the deterministic crash baseline: drawdown, velocity, forced selling,
liquidity withdrawal, panic selling, and bottom-fishing stabilization.

## §2 Metric → Function Mapping

| Metric | Function | analysis-bases.md Ref | Rule Notes |
|---|---|---|---|
| Maximum Drawdown | `compute_max_drawdown()` | `analysis-bases.md §2.1` | Primary crash severity |
| Crash Velocity | `compute_crash_velocity()` | `analysis-bases.md §2.2` | Largest one-round decline |
| Volatility Spike | `compute_volatility_spike()` | `analysis-bases.md §2.3` | Stress regime intensity |
| Forced-Selling Share | `compute_forced_selling_share()` | `analysis-bases.md §2.4` | RiskParity/Leveraged attribution |
| Liquidity Withdrawal | `compute_liquidity_withdrawal()` | `analysis-bases.md §2.5` | MarketMaker quote-depth reduction |
| Panic-Selling Volume | `compute_panic_selling_volume()` | `analysis-bases.md §2.6` | PanicSeller contribution |
| Stabilization Ratio | `compute_stabilization_ratio()` | `analysis-bases.md §2.7` | BottomFisher demand vs sell pressure |

## §3 Dimension-by-Dimension Analysis

Rule output should show mechanically interpretable phases: volatility onset,
forced selling, liquidity withdrawal, behavioral panic, and delayed value
support.

## §4 Variant-Specific Observable Phenomena

| Phenomenon | Expected Observation |
|---|---|
| Mechanical deleveraging | RiskParityFund and LeveragedHedgeFund sell during stress |
| Liquidity drought | MarketMaker depth falls when volatility rises |
| Panic acceleration | PanicSeller adds sell volume after trigger |
| Stabilization attempt | BottomFisher buys after deep discount |

## §5 References

Metrics derive from `../analysis-bases.md §2`; mechanisms derive from
`../simulation-bases.md §4`.
