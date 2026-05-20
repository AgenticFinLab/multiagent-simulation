# ReversalEffect Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic overreaction and reversal rules |
| Market | Net-demand price impact with fundamental reference and recent history |
| Agents | ContrarianInvestor, MomentumInvestor, OverconfidentTrader, NoiseTrader, ValueInvestor, IndexTracker |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 ContrarianInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` reversal pressure | Reads `lookback_window`, `reversal_threshold`, `value_sensitivity`, `base_position_size` |
| Corrective flow | Buys after excessive declines and sells after excessive rises |

### §2.2 MomentumInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` delayed reversal | Reads `momentum_threshold`, `momentum_multiplier`, `base_position_size` |
| Continuation pressure | Trades with recent trend |

### §2.3 OverconfidentTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` signal overreaction | Reads `reaction_threshold`, `overconfidence_factor`, `overconfidence_multiplier` |
| Overreaction | Inflates perceived signal and order size |

### §2.4 NoiseTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` random liquidity | Reads `position_volatility`, `mean_reversion` |
| Noise | Adds stochastic pressure |

### §2.5 ValueInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` fundamental anchor | Reads `value_threshold`, `value_sensitivity`, `value_noise`, `base_position_size` |
| Reversal support | Trades against fundamental mispricing |

### §2.6 IndexTracker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` passive rebalancing | Reads `target_position`, `rebalance_threshold` |
| Stabilization | Rebalances toward benchmark position |

## §3 Market Mechanism Implementation

The market broadcasts price, fundamental value, deviation, and recent history.
Rule investors compute deterministic trend, reversal, value, and noise signals.

## §4 Variant-Specific Features

Rule is the baseline for measuring overshoot followed by reversal.

## §5 Architecture Diagram

```text
Market state -> rule investor decisions -> orders -> net demand -> reversal path
```

## §6 Configuration Reference

Primary config: `configs/ReversalEffect/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/ReversalEffect/Rule/run_reversaleffect.py \
  -c configs/ReversalEffect/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Overconfident and momentum agents should extend overshoot; contrarian and value
agents should create reversal pressure.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
