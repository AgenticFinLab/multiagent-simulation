# MomentumEffect Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic momentum, contrarian, technical, passive, market-making, and fundamental rules |
| Market | Net-demand price impact with fundamental reference and price history |
| Agents | MomentumTrader, ContrarianTrader, IndexFund, MarketMaker, TechnicalTrader, FundamentalTrader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 MomentumTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` price momentum | `MomentumTrader` reads `momentum_threshold`, `scale`, `max_position` |
| Positive feedback | Trades in direction of recent return when threshold is crossed |

### §2.2 ContrarianTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` reversion pressure | `ContrarianTrader` reads `reversion_threshold`, `scale`, `max_position` |
| Anti-momentum | Trades against excessive moves |

### §2.3 IndexFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` passive rebalancing | `IndexFund` reads `target_allocation`, `rebalance_threshold` |
| Stabilization | Rebalances toward target allocation |

### §2.4 MarketMaker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` inventory liquidity | `MarketMaker` reads `inventory_target`, `reversion_speed` |
| Mean-reverting liquidity | Trades toward inventory target |

### §2.5 TechnicalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` moving-average trend | `TechnicalTrader` reads `short_window`, `long_window`, `scale`, `max_position` |
| Technical signal | Buys when short trend exceeds long trend, sells in reverse |

### §2.6 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` fundamental anchoring | `FundamentalTrader` reads `value_threshold`, `scale`, `max_position` |
| Long-run anchor | Buys undervaluation and sells overvaluation |

## §3 Market Mechanism Implementation

The Rule market broadcasts price, fundamental value, deviation, and price
history. Investors compute deterministic signals and send structured orders.

## §4 Variant-Specific Features

Rule is the deterministic baseline for measuring return continuation and later
reversal.

## §5 Architecture Diagram

```text
Market state -> rule signal calculation -> order -> net demand -> next price
```

## §6 Configuration Reference

Primary config: `configs/MomentumEffect/Rule/players.yml`. All thresholds,
windows, scales, and caps are loaded through player `extras`.

## §7 Running Instructions

```bash
python examples/MomentumEffect/Rule/run_momentumeffect.py \
  -c configs/MomentumEffect/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

MomentumTrader and TechnicalTrader should reinforce trends. ContrarianTrader and
FundamentalTrader should reduce overshoot. IndexFund and MarketMaker should add
slower stabilizing flow.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
