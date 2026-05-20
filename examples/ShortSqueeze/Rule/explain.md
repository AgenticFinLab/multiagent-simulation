# ShortSqueeze Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic short-covering, momentum, retail, value, and float-constraint rules |
| Market | Price, fundamental value, short interest, and squeeze-pressure state |
| Agents | ShortSeller, MomentumBuyer, RetailTrader, ValueInvestor, InstitutionalHolder |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 ShortSeller

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` forced covering | Reads `short_entry_price`, `short_initial_position`, `cover_threshold` |
| Squeeze pressure | Buys to cover after losses breach threshold |

### §2.2 MomentumBuyer

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` positive feedback | Reads `momentum_threshold`, `momentum_multiplier`, `base_size`, `max_quantity` |
| Amplification | Buys into rising prices |

### §2.3 RetailTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` retail bullish demand | Reads `bullish_bias`, `min_quantity`, `max_quantity`, `noise_std` |
| Crowd pressure | Biased random buying/selling with bullish tilt |

### §2.4 ValueInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` value resistance | Reads `value_threshold`, `value_multiplier`, `base_size`, `max_quantity` |
| Stabilization | Sells or avoids buying at extreme overvaluation |

### §2.5 InstitutionalHolder

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` float constraint | Holds sticky supply |
| Squeeze intensity | Reduced available float increases price sensitivity |

## §3 Market Mechanism Implementation

The market broadcasts price, fundamental, short interest, and squeeze pressure.
Orders update price and covering pressure.

## §4 Variant-Specific Features

Rule is the deterministic short-squeeze baseline.

## §5 Architecture Diagram

```text
Market squeeze state -> rule agents -> covering/buy/sell orders -> next squeeze state
```

## §6 Configuration Reference

Primary config: `configs/ShortSqueeze/Rule/players.yml`.

## §7 Running Instructions

```bash
python examples/ShortSqueeze/Rule/run_shortsqueeze.py \
  -c configs/ShortSqueeze/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

Rising prices should trigger covering and momentum/retail demand; value
investors should resist overvaluation; institutional holders should constrain
float.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
