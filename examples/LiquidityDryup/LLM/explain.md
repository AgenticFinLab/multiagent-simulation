# Liquidity Dry-up LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Liquidity Dry-up |
| Decision Mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning |
| Theory Reference | `examples/LiquidityDryup/simulation-bases.md` |
| Market Broadcast | `configs/LiquidityDryup/LLM/topology.yml` |

This is a trading-schema scenario. API decisions emit `action`, `bid_price`, `quantity`, numeric `provides_liquidity`, and `reasoning`; `players.py` consumes those fields directly after the shared parser succeeds.

## §2 Theory -> Implementation Mapping

### §2.1 MarketMaker (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `LLMMarketMaker` uses `LLM_MARKET_MAKER_SYS` to reason about stress, withdrawal, and numeric liquidity provision. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/LLM/players.yml:llm_market_maker.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-driven API output parsed into the numeric liquidity order schema. |
### §2.2 LiquiditySeeker (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `LLMLiquiditySeeker` uses `LLM_LIQUIDITY_SEEKER_SYS` to scale demand by available liquidity. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/LLM/players.yml:llm_liquidity_seeker.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-driven constrained execution order. |
### §2.3 ValueTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `LLMValueTrader` uses `LLM_VALUE_TRADER_SYS` to seek price dislocations and provide liquidity when others withdraw. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/LLM/players.yml:llm_value_trader.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-driven value/liquidity-provider order. |
### §2.4 MomentumTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `LLMMomentumTrader` uses `LLM_MOMENTUM_TRADER_SYS` to implement momentum-trader behavior. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/LLM/players.yml:llm_value.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-driven trend-following order. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `LLMNoiseTrader` uses `LLM_NOISE_TRADER_SYS` to implement noise-trader behavior. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/LLM/players.yml:llm_noise_trader.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-driven uninformed order flow. |

## §3 Market Mechanism

The LLM market uses the same liquidity-amplified price equation as the Rule baseline. It sums numeric `provides_liquidity` from API orders, computes `liquidity_factor = 100 / max(total_liquidity, 10)`, and broadcasts price, return, liquidity, liquidity factor, and fundamental value.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/LiquidityDryup/LLM/players.py` |
| Prompt module | `examples/LiquidityDryup/LLM/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference` and `ark/doubao-seed-2-0-mini-260428`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks; malformed responses are retried three times. |
| Error handling | Deterministic config/schema/API errors fail fast; this variant does not silently fallback after malformed decisions. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/LiquidityDryup/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/LiquidityDryup/LLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/LiquidityDryup/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/LiquidityDryup/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/LiquidityDryup/LLM/run_liquidity_llm.py -c configs/LiquidityDryup/LLM/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/LiquidityDryup/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/LiquidityDryup/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
