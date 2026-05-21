# Liquidity Dry-up RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Liquidity Dry-up |
| Decision Mechanism | LLM-generated trading orders constrained by explicit scenario rules |
| Theory Reference | `examples/LiquidityDryup/simulation-bases.md` |
| Market Broadcast | `configs/LiquidityDryup/RuleLLM/topology.yml` |

This is a trading-schema scenario. API decisions emit `action`, `bid_price`, `quantity`, numeric `provides_liquidity`, and `reasoning`; the market consumes numeric liquidity depth rather than a boolean flag.

## §2 Theory -> Implementation Mapping

### §2.1 MarketMaker (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RuleLLMMarketMaker` uses `RULELLM_MARKET_MAKER_SYS`, whose `== DECISION RULES ==` section encodes volatility withdrawal and numeric liquidity provision. |
| Mathematical model from simulation-bases.md §4.1 | Prompt requires withdrawal when absolute return exceeds 2%, normal depth around 30, and inventory rebalance around 30% stress / 20% normal. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/RuleLLM/players.yml:rulellm_market_maker.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Formula-anchored API output parsed into the numeric liquidity order schema. |
### §2.2 LiquiditySeeker (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RuleLLMLiquidityDemander` uses `RULELLM_LIQUIDITY_SEEKER_SYS` to encode liquidity-scaled demand. |
| Mathematical model from simulation-bases.md §4.2 | Prompt instructs normal demand around +/-15 shares, scaled down by liquidity / 100, with zero liquidity provision. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/RuleLLM/players.yml:rulellm_liquidity_demander.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Formula-anchored constrained-execution order. |
### §2.3 ValueTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RuleLLMArbitrageur` uses `RULELLM_VALUE_TRADER_SYS` to encode deviation-based value trading and crisis liquidity provision. |
| Mathematical model from simulation-bases.md §4.3 | Prompt instructs liquidity around 20 when `abs(deviation) > 5%` and quantity about `deviation * 30` when `abs(deviation) > 3%`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/RuleLLM/players.yml:rulellm_arbitrageur.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Formula-anchored stabilizing value order. |
### §2.4 MomentumTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RuleLLMValueInvestor` is a legacy class name whose prompt `RULELLM_MOMENTUM_TRADER_SYS` implements momentum-trader behavior. |
| Mathematical model from simulation-bases.md §4.4 | Prompt instructs hold below 1% absolute return and trend-following quantity about `return * 200` above that threshold. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/RuleLLM/players.yml:rulellm_value.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Formula-anchored trend-following order. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RuleLLMForcedSeller` is a legacy class name whose prompt `RULELLM_NOISE_TRADER_SYS` implements noise-trader behavior. |
| Mathematical model from simulation-bases.md §4.5 | Prompt instructs small noisy orders, quantity below about 15 shares, and zero liquidity provision. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/RuleLLM/players.yml:rulellm_forced_seller.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Formula-anchored uninformed order flow. |

## §3 Market Mechanism

The RuleLLM market uses the liquidity-amplified price equation with `base_price_impact`, `low_liquidity_threshold`, and `high_impact_multiplier`. It now sums numeric `order["provides_liquidity"]`, aligning the hybrid mode with the Rule/LLM liquidity-depth contract.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/LiquidityDryup/RuleLLM/players.py` |
| Prompt module | `examples/LiquidityDryup/RuleLLM/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference` and `ark/doubao-seed-2-0-mini-260428`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks; malformed responses are retried three times. |
| Error handling | Deterministic config/schema/API errors fail fast; this variant does not silently fallback after malformed decisions. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/LiquidityDryup/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/LiquidityDryup/RuleLLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/LiquidityDryup/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/LiquidityDryup/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/LiquidityDryup/RuleLLM/run_liquidity_dryup_rulellm.py -c configs/LiquidityDryup/RuleLLM/simulation.yml
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
