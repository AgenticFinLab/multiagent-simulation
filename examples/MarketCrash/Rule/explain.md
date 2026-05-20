# MarketCrash Rule — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Mechanism | Deterministic crash-feedback rules |
| Market | Net-demand price impact with mean reversion and volatility state |
| Agents | RiskParityFund, LeveragedHedgeFund, MarketMaker, PassiveInvestor, PanicSeller, BottomFisher |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 RiskParityFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` volatility targeting | `RiskParityFund` reads `target_volatility`, `rebalance_speed`, `base_position` |
| Mechanical deleveraging | Sells exposure when volatility exceeds target |

### §2.2 LeveragedHedgeFund

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` margin spiral | `LeveragedHedgeFund` reads `margin_call_level`, `liquidation_level`, `momentum_sensitivity` |
| Forced selling | Larger sell pressure as losses approach liquidation |

### §2.3 MarketMaker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` liquidity withdrawal | `MarketMaker` reads `inventory_limit`, `normal_quote_size`, `volatility_withdraw_threshold` |
| Endogenous liquidity | Quote size falls in high volatility |

### §2.4 PassiveInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` slow rebalancing | `PassiveInvestor` reads `target_position`, `rebalance_frequency` |
| Stabilizing demand | Periodically trades toward target |

### §2.5 PanicSeller

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` behavioral selling | `PanicSeller` reads `loss_threshold`, `crash_trigger`, `panic_sell_fraction` |
| Panic flow | Sells fraction of holdings after trigger |

### §2.6 BottomFisher

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` contrarian value buying | `BottomFisher` reads `discount_threshold`, `crash_buy_threshold`, `buy_size`, `lookback` |
| Stabilization | Buys after deep discount/crash condition |

## §3 Market Mechanism Implementation

The market aggregates buy and sell volume, computes net demand, updates price,
and broadcasts market state to all investors. The Rule variant uses no LLM or
RAG calls.

## §4 Variant-Specific Features

Rule is the deterministic baseline. All actions come from thresholds and
formulas loaded from config.

## §5 Architecture Diagram

```text
Market update -> Rule investors -> order messages -> Market aggregation -> next price
```

## §6 Configuration Reference

Primary config: `configs/MarketCrash/Rule/players.yml`. The market and all
investor parameters are loaded from `extras`.

## §7 Running Instructions

```bash
python examples/MarketCrash/Rule/run_marketcrash.py \
  -c configs/MarketCrash/Rule/simulation.yml
```

## §8 Expected Behavior Patterns

RiskParityFund and LeveragedHedgeFund should increase sell pressure during
stress. MarketMaker should withdraw liquidity. BottomFisher and PassiveInvestor
should provide delayed stabilization.

## §9 References

See `../simulation-bases.md §2` and `../simulation-bases.md §4`.
