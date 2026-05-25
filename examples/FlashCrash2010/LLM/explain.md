# 2010 Flash Crash LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | 2010 Flash Crash |
| Decision Mechanism | LLM-generated trading orders with class-mapped market agent types |
| Theory Reference | `examples/FlashCrash2010/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash2010/LLM/topology.yml` |

This variant keeps the Rule coordinator but replaces deterministic investor formulas with LLM decisions. The player code maps each LLM class to the Rule market's `agent_type` taxonomy so the order-book depth formula still sees HFT, fundamental, stop-loss, and noise participants.

## §2 Theory -> Implementation Mapping

### §2.1 HFTMarketMaker

| Theory Component | Implementation |
|---|---|
| HFT liquidity withdrawal | `LLMHFTMarketMaker` receives HFT market-maker stress instructions and emits numeric trading decisions plus `provides_liquidity`. |
| Market effect | `agent_type_for_strategy()` maps the class to `agent_type="hft"` so HFT participation affects depth. |
| Config source | `configs/FlashCrash2010/LLM/players.yml` with `LLM_HFT_MARKET_MAKER_SYS`. |

### §2.2 MomentumChaser

| Theory Component | Implementation |
|---|---|
| Positive-feedback trading | `LLMMomentumChaser` receives momentum-size thresholds and produces trend-following orders. |
| Market effect | It is class-mapped to `agent_type="hft"` and contributes to HFT participation. |
| Config source | `configs/FlashCrash2010/LLM/players.yml` with `LLM_MOMENTUM_CHASER_SYS`. |

### §2.3 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Value-based stabilization | `LLMFundamentalTrader` receives value-deviation instructions and can buy undervaluation. |
| Market effect | It is class-mapped to `agent_type="fundamental"` for recovery diagnostics. |
| Config source | `configs/FlashCrash2010/LLM/players.yml` with `LLM_FUNDAMENTAL_SYS`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `LLMStopLossTrader` receives non-negotiable stop-loss rules and can liquidate position. |
| Market effect | It is class-mapped to `agent_type="stoploss"` so cascade waves remain analyzable. |
| Config source | `configs/FlashCrash2010/LLM/players.yml` with `LLM_STOP_LOSS_SYS`. |

### §2.5 NoiseTrader

| Theory Component | Implementation |
|---|---|
| Background order flow | `LLMNoiseTrader` receives low-probability uninformed trading instructions. |
| Market effect | It is class-mapped to `agent_type="noise"`. |
| Config source | `configs/FlashCrash2010/LLM/players.yml` with `LLM_NOISE_TRADER_SYS`. |

## §3 Market Mechanism

The market mechanism is imported from the Rule variant. LLM outputs are parsed into numeric orders, constrained by cash/position, class-mapped to Rule `agent_type`, and then consumed by the same depth/spread/price update.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash2010/LLM/players.py` |
| Prompt module | `examples/FlashCrash2010/LLM/prompts.py` |
| Inference | Uses the project ARK LLM policy. |
| Output parsing | `parse_llm_response_with_thinking()` extracts `<decision>` JSON and required numeric fields. |
| Error handling | API parse failures are retried; missing `provides_liquidity` uses an explicit conservative false marker; deterministic config/schema errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash2010/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash2010/LLM/players.yml` | Player class paths, prompt paths, model name, and market parameters. |
| `configs/FlashCrash2010/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash2010/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash2010/LLM/run_flashcrash2010_llm.py -c configs/FlashCrash2010/LLM/simulation.yml
```

## §7 Expected Behavior

- HFT classes should remain visible as `agent_type="hft"` in the market order stream.
- LLM sizing and reasoning may vary, but depth collapse should still depend on HFT participation.
- Stop-loss and fundamental roles should remain distinguishable for Level-2 audit.

## §8 References

See `examples/FlashCrash2010/simulation-bases.md §2` for the cited market microstructure and May 6, 2010 sources.

## §9 Variant Comparison

See `examples/FlashCrash2010/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
