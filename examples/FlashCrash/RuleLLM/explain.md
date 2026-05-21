# Flash Crash RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Flash Crash |
| Decision Mechanism | LLM-generated trading orders constrained by explicit scenario rules |
| Theory Reference | `examples/FlashCrash/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash/RuleLLM/topology.yml` |

This variant keeps the liquidity-sensitive FlashCrash market and gives each API investor a persona plus quantitative rules derived from the deterministic baseline. Its order schema requires `action`, `bid_price`, `quantity`, `reasoning`, and `provides_liquidity`.

## §2 Theory -> Implementation Mapping

### §2.1 HighFrequencyTrader

| Theory Component | Implementation |
|---|---|
| HFT positive-feedback trading | `RuleLLMHighFrequencyTrader` uses `RULELLM_HFT_SYS`, which defines short-window momentum, speed advantage, numeric sizing, and `provides_liquidity=false`. |
| Market effect | It can amplify short-term momentum while still exposing the required liquidity flag. |
| Config source | `configs/FlashCrash/RuleLLM/players.yml` with `RULELLM_HFT_SYS` and `RULELLM_USER_TEMPLATE`. |

### §2.2 MarketMaker

| Theory Component | Implementation |
|---|---|
| Liquidity provision and withdrawal | `RuleLLMMarketMaker` uses `RULELLM_MARKET_MAKER_SYS`, which mandates withdrawal when volatility exceeds threshold and liquidity provision otherwise. |
| Market effect | Its `provides_liquidity` field is consumed directly by `Market.decide()` to compute effective liquidity. |
| Config source | `configs/FlashCrash/RuleLLM/players.yml` with `RULELLM_MARKET_MAKER_SYS`. |

### §2.3 AlgorithmicTrader

| Theory Component | Implementation |
|---|---|
| Trend-following algorithm | `RuleLLMAlgorithmicTrader` uses `RULELLM_ALGO_SYS`, which defines trend-window signal, scaled quantity, and `provides_liquidity=false`. |
| Market effect | It reinforces trend after initial HFT movement. |
| Config source | `configs/FlashCrash/RuleLLM/players.yml` with `RULELLM_ALGO_SYS`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `RuleLLMStopLossTrader` uses `RULELLM_STOP_LOSS_SYS`, which defines recent-high stop logic and full-position liquidation when triggered. |
| Market effect | It creates threshold-driven sell cascades. |
| Config source | `configs/FlashCrash/RuleLLM/players.yml` with `RULELLM_STOP_LOSS_SYS`. |

### §2.5 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Fundamental recovery force | `RuleLLMFundamentalTrader` uses `RULELLM_FUNDAMENTAL_SYS`, which defines value deviation, entry threshold, and liquidity provision. |
| Market effect | It supplies stabilizing demand when price deviates below fundamental value. |
| Config source | `configs/FlashCrash/RuleLLM/players.yml` with `RULELLM_FUNDAMENTAL_SYS`. |

### §2.6 RetailTrader

| Theory Component | Implementation |
|---|---|
| Noise-trader background flow | The RuleLLM variant does not instantiate a separate RetailTrader class; it focuses API calls on the five mechanism-critical flash-crash roles. |
| Market effect | Background variation is represented by market noise and LLM sizing dispersion. |
| Config source | `configs/FlashCrash/RuleLLM/players.yml` configured players. |

## §3 Market Mechanism

`Market.decide()` matches the Rule liquidity accounting: orders with `provides_liquidity=true` add `abs(quantity)` to baseline liquidity, and low effective liquidity activates the high-impact multiplier. The parser validates required fields so missing liquidity decisions fail visibly instead of being silently interpreted.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash/RuleLLM/players.py` |
| Prompt module | `examples/FlashCrash/RuleLLM/prompts.py` |
| Inference | Uses the project ARK LLM policy. |
| Output parsing | `parse_llm_response_with_thinking()` plus explicit required-field checks in `players.py`. |
| Error handling | API parse failures are retried; deterministic schema/config errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash/RuleLLM/players.yml` | Player class paths, prompt paths, model name, and rule parameters. |
| `configs/FlashCrash/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash/RuleLLM/run_flash_crash_rulellm.py -c configs/FlashCrash/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- The RuleLLM agents should preserve the deterministic mechanism signs while allowing bounded LLM judgment in sizing.
- `provides_liquidity` must be present in each decision and should drive liquidity amplification.
- Stop-loss liquidation and value-driven recovery should remain visible in the order stream.
- A successful full experiment must pass Level-1 execution and Level-2 structural quality review.

## §8 References

See `examples/FlashCrash/simulation-bases.md §2` for the cited market microstructure and flash-crash literature.

## §9 Variant Comparison

See `examples/FlashCrash/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
