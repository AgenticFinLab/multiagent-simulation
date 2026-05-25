# Liquidity Dry-up Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Liquidity Dry-up |
| Decision Mechanism | deterministic rule-based trading orders |
| Theory Reference | `examples/LiquidityDryup/simulation-bases.md` |
| Market Broadcast | `configs/LiquidityDryup/Rule/topology.yml` |

This is a trading-schema scenario. Rule decisions emit `bid_price`, `quantity`, `strategy`, and numeric `provides_liquidity` fields consumed by the market coordinator.

## §2 Theory -> Implementation Mapping

### §2.1 MarketMaker (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `MarketMaker.decide()` computes `volatility = abs(market_data["return"])`; if volatility exceeds `extras["volatility_threshold"]`, it withdraws liquidity. |
| Mathematical model from simulation-bases.md §4.1 | `provides_liquidity = 0` in stress; otherwise `provides_liquidity = extras["base_liquidity"]`; inventory rebalance uses `withdraw_rebalance` or `normal_rebalance`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rule/players.yml:market_maker.config.extras` supplies threshold, base liquidity, and rebalance fractions. |
| Variant-specific decision mechanism | Deterministic numeric liquidity-provision order. |
### §2.2 LiquiditySeeker (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `LiquiditySeeker.decide()` samples desired order flow from `N(0, target_volatility)`. |
| Mathematical model from simulation-bases.md §4.2 | Order size is scaled by `min(1.0, liquidity / liquidity_base)`, modelling constrained execution when liquidity dries up. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rule/players.yml:liquidity_seeker.config.extras` supplies `target_volatility` and `liquidity_base`. |
| Variant-specific decision mechanism | Deterministic execution rule with stochastic target order draw. |
### §2.3 ValueTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `ValueTrader.decide()` computes `deviation = (fundamental - price) / fundamental`. |
| Mathematical model from simulation-bases.md §4.3 | It provides `base_liquidity_provision` when `abs(deviation) > liquidity_threshold` and trades `deviation * value_multiplier` when `abs(deviation) > trade_threshold`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rule/players.yml:value_trader.config.extras` supplies thresholds, liquidity provision, and value multiplier. |
| Variant-specific decision mechanism | Deterministic stabilizing liquidity provision and value trade. |
### §2.4 MomentumTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `MomentumTrader.decide()` reads the current market return. |
| Mathematical model from simulation-bases.md §4.4 | If `abs(return) > momentum_threshold`, order quantity is `return * momentum_multiplier`; otherwise it holds. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rule/players.yml:momentum_trader.config.extras` supplies threshold and multiplier. |
| Variant-specific decision mechanism | Deterministic trend-following amplifier. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `NoiseTrader.decide()` samples order quantity from `N(0, noise_volatility)`. |
| Mathematical model from simulation-bases.md §4.5 | It never provides liquidity and caps quantity to +/-15 shares. |
| Behavioral parameters from simulation-bases.md §6 | `configs/LiquidityDryup/Rule/players.yml:noise_trader.config.extras` supplies `noise_volatility`. |
| Variant-specific decision mechanism | Stochastic uninformed order flow around the deterministic market contract. |

## §3 Market Mechanism

The Rule `Market` uses `P(t+1) = P(t) + price_impact * net_demand * liquidity_factor + mean_reversion * (fundamental - P(t)) + noise`. `liquidity_factor = 100 / max(total_liquidity, 10)`, and `total_liquidity = base_liquidity + sum(order["provides_liquidity"])`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/LiquidityDryup/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast; no API fallback is used. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/LiquidityDryup/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/LiquidityDryup/Rule/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/LiquidityDryup/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/LiquidityDryup/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/LiquidityDryup/Rule/run_liquidity.py -c configs/LiquidityDryup/Rule/simulation.yml
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
