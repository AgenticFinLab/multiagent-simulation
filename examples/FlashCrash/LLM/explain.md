# Flash Crash LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Flash Crash |
| Decision Mechanism | LLM-generated trading orders with numeric action fields |
| Theory Reference | `examples/FlashCrash/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash/LLM/topology.yml` |

This variant replaces deterministic investor formulas with LLM decisions while retaining the FlashCrash coordinator. The order schema is `action`, `bid_price`, `quantity`, and `reasoning`; the LLM coordinator tracks liquidity internally from volume and net demand rather than reading a `provides_liquidity` order field.

## §2 Theory -> Implementation Mapping

### §2.1 HighFrequencyTrader

| Theory Component | Implementation |
|---|---|
| HFT positive-feedback trading | `LLMHighFrequencyTrader` receives HFT persona/rules from `LLM_HFT_SYS` and may buy or sell rapidly based on return, liquidity, and crash mode. |
| Market effect | The LLM can amplify fast momentum without a hard formula. |
| Config source | `configs/FlashCrash/LLM/players.yml` with `LLM_HFT_SYS` and `LLM_USER_TEMPLATE`. |

### §2.2 MarketMaker

| Theory Component | Implementation |
|---|---|
| Liquidity provision and withdrawal | `LLMFlashMarketMaker` receives stress/withdrawal instructions in `LLM_MARKET_MAKER_SYS`; withdrawal is expressed in `reasoning` and order size, while the market uses its internal liquidity update. |
| Market effect | Market stress is represented by lower internal liquidity after high net demand or volume. |
| Config source | `configs/FlashCrash/LLM/players.yml` with `LLM_MARKET_MAKER_SYS`. |

### §2.3 AlgorithmicTrader

| Theory Component | Implementation |
|---|---|
| Trend-following algorithm | `LLMAlgorithmicTrader` receives mechanical momentum thresholds in `LLM_ALGO_SYS`. |
| Market effect | It supplies LLM-generated continuation orders when the return signal is strong. |
| Config source | `configs/FlashCrash/LLM/players.yml` with `LLM_ALGO_SYS`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `LLMStopLossTrader` receives fixed price-level risk rules in `LLM_STOP_LOSS_SYS` and can liquidate position when thresholds are breached. |
| Market effect | It creates sell pressure during price declines, with stochastic timing from LLM judgment. |
| Config source | `configs/FlashCrash/LLM/players.yml` with `LLM_STOP_LOSS_SYS`. |

### §2.5 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Fundamental recovery force | `LLMFundamentalTrader` receives value-investing instructions in `LLM_FUNDAMENTAL_SYS` and can buy sharp undervaluation. |
| Market effect | It supplies recovery demand after deep drops. |
| Config source | `configs/FlashCrash/LLM/players.yml` with `LLM_FUNDAMENTAL_SYS`. |

### §2.6 RetailTrader

| Theory Component | Implementation |
|---|---|
| Noise-trader background flow | The LLM variant does not instantiate a separate RetailTrader class; stochastic background is represented by the coordinator's internal liquidity/noise update and by LLM order dispersion among the five configured API roles. |
| Market effect | Background variation exists without adding a sixth API role. |
| Config source | `configs/FlashCrash/LLM/players.yml` configured players. |

## §3 Market Mechanism

`Market.decide()` collects numeric LLM orders, calculates net demand and total volume, updates an internal liquidity state, applies high-impact mode when liquidity falls below threshold, and broadcasts the next `market_data`. This variant intentionally uses an internal liquidity state rather than requiring LLM orders to emit `provides_liquidity`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash/LLM/players.py` |
| Prompt module | `examples/FlashCrash/LLM/prompts.py` |
| Inference | Uses the project ARK LLM policy. |
| Output parsing | `_parse_response()` extracts `<decision>` JSON and requires numeric `bid_price` and `quantity`. |
| Error handling | API parse failures are retried; deterministic schema/config errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash/LLM/players.yml` | Player class paths, prompt paths, model name, and market parameters. |
| `configs/FlashCrash/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash/LLM/run_flash_crash_llm.py -c configs/FlashCrash/LLM/simulation.yml
```

## §7 Expected Behavior

- LLM agents preserve the five core crash roles while producing stochastic sizing and reasoning.
- The market can enter high-impact mode as internal liquidity falls.
- Stop-loss and value-investor behavior should still appear in the order stream.
- A successful full experiment must pass Level-1 execution and Level-2 structural quality review.

## §8 References

See `examples/FlashCrash/simulation-bases.md §2` for the cited market microstructure and flash-crash literature.

## §9 Variant Comparison

See `examples/FlashCrash/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
