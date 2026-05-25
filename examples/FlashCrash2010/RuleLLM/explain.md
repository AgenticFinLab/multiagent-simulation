# 2010 Flash Crash RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | 2010 Flash Crash |
| Decision Mechanism | LLM-generated trading orders constrained by explicit 2010 flash-crash rules |
| Theory Reference | `examples/FlashCrash2010/simulation-bases.md` |
| Market Broadcast | `configs/FlashCrash2010/RuleLLM/topology.yml` |

This variant keeps the Rule coordinator and gives each LLM investor a persona plus quantitative rules derived from the deterministic baseline. Class mapping preserves the market's `agent_type` contract for HFT participation and depth collapse.

## §2 Theory -> Implementation Mapping

### §2.1 HFTMarketMaker

| Theory Component | Implementation |
|---|---|
| HFT liquidity withdrawal | `RuleLLMHFTMarketMaker` uses `RULELLM_HFT_MARKET_MAKER_SYS`, which defines velocity-based withdrawal and liquidity provision. |
| Market effect | It is class-mapped to `agent_type="hft"` and supplies `provides_liquidity` when the model emits it. |
| Config source | `configs/FlashCrash2010/RuleLLM/players.yml` with `RULELLM_HFT_MARKET_MAKER_SYS`. |

### §2.2 MomentumChaser

| Theory Component | Implementation |
|---|---|
| Positive-feedback trading | `RuleLLMMomentumChaser` uses explicit velocity, threshold, multiplier, and max-size rules. |
| Market effect | It is class-mapped to `agent_type="hft"` and reinforces trend flow. |
| Config source | `configs/FlashCrash2010/RuleLLM/players.yml` with `RULELLM_MOMENTUM_CHASER_SYS`. |

### §2.3 FundamentalTrader

| Theory Component | Implementation |
|---|---|
| Value-based stabilization | `RuleLLMFundamentalTrader` uses deviation and order-size rules for recovery demand. |
| Market effect | It is class-mapped to `agent_type="fundamental"`. |
| Config source | `configs/FlashCrash2010/RuleLLM/players.yml` with `RULELLM_FUNDAMENTAL_SYS`. |

### §2.4 StopLossTrader

| Theory Component | Implementation |
|---|---|
| Stop-loss cascade | `RuleLLMStopLossTrader` uses the non-negotiable stop-level liquidation rule. |
| Market effect | It is class-mapped to `agent_type="stoploss"`. |
| Config source | `configs/FlashCrash2010/RuleLLM/players.yml` with `RULELLM_STOP_LOSS_SYS`. |

### §2.5 NoiseTrader

| Theory Component | Implementation |
|---|---|
| Background order flow | `RuleLLMNoiseTrader` uses random-trade probability and bounded order-size instructions. |
| Market effect | It is class-mapped to `agent_type="noise"`. |
| Config source | `configs/FlashCrash2010/RuleLLM/players.yml` with `RULELLM_NOISE_TRADER_SYS`. |

## §3 Market Mechanism

The coordinator is imported from the Rule variant. RuleLLM investors emit constrained LLM orders, the player code applies portfolio bounds, maps class names to Rule `agent_type`, and sends orders into the same depth/spread/price update.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/FlashCrash2010/RuleLLM/players.py` |
| Prompt module | `examples/FlashCrash2010/RuleLLM/prompts.py` |
| Inference | Uses the project ARK LLM policy. |
| Output parsing | `parse_llm_response_with_thinking()` plus explicit class-based order enrichment in `players.py`. |
| Error handling | API parse failures use explicit logged hold fallback after retries; missing `provides_liquidity` uses a conservative false marker; deterministic config/schema errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/FlashCrash2010/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/FlashCrash2010/RuleLLM/players.yml` | Player class paths, prompt paths, model name, and rule parameters. |
| `configs/FlashCrash2010/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/FlashCrash2010/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/FlashCrash2010/RuleLLM/run_flashcrash2010_rulellm.py -c configs/FlashCrash2010/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- Rule-derived prompt constraints should keep signs and scale close to the deterministic mechanism.
- HFT classes should remain visible as `agent_type="hft"` in the market order stream.
- Level-2 audit should inspect parse-fallback rate and any missing-liquidity markers.

## §8 References

See `examples/FlashCrash2010/simulation-bases.md §2` for the cited market microstructure and May 6, 2010 sources.

## §9 Variant Comparison

See `examples/FlashCrash2010/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
