# VolatilityClustering Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic volatility-regime, trend, slow-adaptation, noise, and fundamental rules |
| Market | Net-demand price process with realized-volatility state |
| Agents | Fundamentalist, TrendFollower, NoiseTrader, SlowAdapter, VolatilityTrader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 Fundamentalist

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` fundamental anchoring | Reads `value_sensitivity`, `value_noise_std`, `trade_frequency`, `base_position_size` |
| Stabilization | Trades against fundamental deviation |

### §2.2 TrendFollower

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` trend amplification | Reads `lookback_window`, `trend_threshold`, `baseline_volatility`, `volatility_sensitivity`, `base_position_size` |
| Clustering pressure | Trades with trends, scaled by volatility |

### §2.3 NoiseTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` stochastic shocks | Reads `position_volatility`, `mean_reversion_speed` |
| Shock generation | Adds random order flow with reversion |

### §2.4 SlowAdapter

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` slow updating | Reads `lookback_window`, `update_weight`, `base_position_size` |
| Persistence | Updates desired position gradually |

### §2.5 VolatilityTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` volatility-regime response | Reads `vol_lookback`, `low_vol_threshold`, `high_vol_threshold`, `base_position_size` |
| Regime trading | Changes exposure when volatility crosses thresholds |

## §3 Market Mechanism Implementation

The market broadcasts price, returns, volatility, and fundamental state.
Investors submit orders based on value, trend, volatility regime, adaptation, or
noise.

## §4 Variant-Specific Features

Rule is the deterministic baseline for volatility clustering and regime
persistence.

## §5 Architecture Diagram

```text
Market state -> rule agents -> volatility-sensitive orders -> next price/volatility
```

## §6 Configuration Reference

Primary config: `configs/VolatilityClustering/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/VolatilityClustering/Rule/run_volatilityclustering.py \
  -c configs/VolatilityClustering/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Volatility should persist after shocks. TrendFollower, SlowAdapter, and
VolatilityTrader should contribute to clustered high-volatility regimes.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
