# Flash Crash Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Flash Crash |
| Decision Mechanism | deterministic liquidity-sensitive trading rules |
| Theory Reference | `examples/FlashCrash/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash/Rule/topology.yml` |

This variant is the deterministic baseline. It emits numeric trading orders with `bid_price`, `quantity`, `strategy`, `investor`, and `provides_liquidity`, and the coordinator uses those orders to update price through the liquidity-sensitive market mechanism in `simulation-bases.md §3`.

## §2 Theory -> Implementation Mapping

### §2.1 HighFrequencyTrader

| Theory Component | Implementation |
|---|---|
| HFT positive-feedback trading | `HighFrequencyTrader.decide()` computes short-window momentum from `price_history`, scales it by `momentum_sensitivity`, `base_position_size`, and `speed_advantage`, clamps the result to `[-60, 60]`, and never provides liquidity. |
| Market effect | Fast directional orders amplify the first negative move before slower agents respond. |
| Config source | `configs/FlashCrash/Rule/players.yml` extras for `momentum_sensitivity`, `base_position_size`, `speed_advantage`, and `short_window`. |

### §2.2 MarketMaker

| Theory Component | Implementation |
|---|---|
| Liquidity provision and withdrawal | `MarketMaker.decide()` compares the one-round absolute return with `volatility_threshold`; calm markets set `provides_liquidity=True`, while stressed markets set it false and reduce inventory. |
| Market effect | The coordinator adds `abs(quantity)` only from liquidity-providing orders, so withdrawal mechanically raises price impact. |
| Config source | `configs/FlashCrash/Rule/players.yml` extras for `volatility_threshold` and inventory sizing. |

### §2.3 AlgorithmicTrader

| Theory Component | Implementation |
|---|---|
| Trend-following algorithm | `AlgorithmicTrader.decide()` computes a medium-window trend, scales it by `trend_sensitivity`, `base_position_size`, and `trend_multiplier`, and clamps the result to `[-40, 40]`. |
| Market effect | It reinforces momentum after HFT orders have moved the price path. |
| Config source | `configs/FlashCrash/Rule/players.yml` extras for `trend_sensitivity`, `trend_multiplier`, and `trend_window`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `StopLossTrader.decide()` tracks recent highs and sells the whole position once `price < recent_high * (1 - stop_loss_percent)`. |
| Market effect | Forced one-shot sell orders create lumpy cascade pressure. |
| Config source | `configs/FlashCrash/Rule/players.yml` extras for `stop_loss_percent` and initial position. |

### §2.5 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Fundamental recovery force | `FundamentalTrader.decide()` compares price with `fundamental_value`; deviations beyond `value_threshold` produce value-motivated buy or sell orders. |
| Market effect | It provides stabilizing liquidity near the trough and supplies recovery demand. |
| Config source | `configs/FlashCrash/Rule/players.yml` extras for `value_threshold`, `value_sensitivity`, and `value_multiplier`. |

### §2.6 RetailTrader

| Theory Component | Implementation |
|---|---|
| Noise-trader background flow | `RetailTrader.decide()` trades only on configured intervals, combining Gaussian noise with a position mean-reversion term. |
| Market effect | It adds low-volume stochastic background activity without becoming the crash driver. |
| Config source | `configs/FlashCrash/Rule/players.yml` extras for `trade_frequency`, `noise_std`, and `position_mean_reversion`. |

## §3 Market Mechanism

`Market.decide()` collects previous-round orders, computes buy volume, sell volume, net demand, and liquidity provision, then updates price with base impact, liquidity amplification, fundamental mean reversion, and Gaussian noise. The Rule market consumes `provides_liquidity` directly; malformed orders that omit required fields should fail fast rather than being silently coerced.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash/Rule/players.yml` | Player class paths and rule parameters. |
| `configs/FlashCrash/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash/Rule/run_flash_crash.py -c configs/FlashCrash/Rule/simulation.yml
```

## §7 Expected Behavior

- HFT and algorithmic orders amplify short-term negative moves.
- Market makers withdraw under volatility stress, reducing effective liquidity.
- Stop-loss traders generate cascade selling after threshold breaches.
- Fundamental traders buy deep undervaluation and support recovery.

## §8 References

See `examples/FlashCrash/simulation-bases.md §2` for the cited market microstructure and flash-crash literature.

## §9 Variant Comparison

See `examples/FlashCrash/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
