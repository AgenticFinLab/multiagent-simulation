# 2010 Flash Crash Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | 2010 Flash Crash |
| Decision Mechanism | deterministic order-book-depth and agent-type rules |
| Theory Reference | `examples/FlashCrash2010/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash2010/Rule/topology.yml` |

This is the deterministic baseline for the May 6, 2010 flash-crash mechanism. Orders emit `bid_price`, `quantity`, `strategy`, `agent_type`, and `provides_liquidity`; the coordinator uses `agent_type == "hft"` to compute HFT participation and depth stress.

## §2 Theory -> Implementation Mapping

### §2.1 HFTMarketMaker

| Theory Component | Implementation |
|---|---|
| HFT liquidity withdrawal | `HFTMarketMaker.decide()` computes recent velocity and switches from `provides_liquidity=True` quantity to zero-quantity withdrawal when velocity exceeds `withdrawal_threshold`. |
| Market effect | Its `agent_type="hft"` controls the market's HFT participation ratio and depth-collapse multiplier. |
| Config source | `configs/FlashCrash2010/Rule/players.yml` extras for `withdrawal_threshold`, spreads, and `mm_qty`. |

### §2.2 MomentumChaser

| Theory Component | Implementation |
|---|---|
| Positive-feedback trading | `MomentumChaser.decide()` computes lookback-window velocity and trades in the direction of the move when `abs(velocity) > entry_threshold`. |
| Market effect | It keeps HFT participation active while adding directional flow during the cascade. |
| Config source | `configs/FlashCrash2010/Rule/players.yml` extras for `entry_threshold`, `lookback_window`, and `position_multiplier`. |

### §2.3 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Value-based stabilization | `FundamentalTrader.decide()` buys undervaluation or sells overvaluation once deviation exceeds `value_trigger`. |
| Market effect | It supplies recovery demand after price falls below fundamental value. |
| Config source | `configs/FlashCrash2010/Rule/players.yml` extras for `value_trigger` and `order_size`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `StopLossTrader.decide()` sells the whole position once price breaches `entry_price * (1 - stop_percentage)`. |
| Market effect | One-shot liquidation adds concentrated sell pressure during the crash. |
| Config source | `configs/FlashCrash2010/Rule/players.yml` extras for `entry_price`, `stop_percentage`, and `position_size`. |

### §2.5 NoiseTrader

| Theory Component | Implementation |
|---|---|
| Background order flow | `NoiseTrader.decide()` trades randomly with configured probability and bounded order size. |
| Market effect | It adds low-volume background flow without driving the crash mechanism. |
| Config source | `configs/FlashCrash2010/Rule/players.yml` extras for `trade_probability`, `min_order`, and `max_order`. |

## §3 Market Mechanism

`Market.decide()` computes net order flow, HFT participation, rolling volatility, stress factor, depth, spread, and the next price. Missing required order fields should fail fast because the depth model depends on `quantity` and `agent_type`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash2010/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash2010/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash2010/Rule/players.yml` | Player class paths and rule parameters. |
| `configs/FlashCrash2010/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash2010/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash2010/Rule/run_flashcrash2010.py -c configs/FlashCrash2010/Rule/simulation.yml
```

## §7 Expected Behavior

- HFT market makers withdraw when recent velocity crosses threshold.
- Momentum chasers reinforce directional moves.
- Stop-loss traders create cascade selling.
- Fundamental traders provide recovery demand.

## §8 References

See `examples/FlashCrash2010/simulation-bases.md §2` for the cited market microstructure and May 6, 2010 sources.

## §9 Variant Comparison

See `examples/FlashCrash2010/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
