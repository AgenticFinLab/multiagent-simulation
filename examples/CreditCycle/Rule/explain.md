# Credit Cycle Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Credit Cycle |
| Decision Mechanism | deterministic rule-based trading orders |
| Theory Reference | `examples/CreditCycle/simulation-bases.md` |
| Market Broadcast | `configs/CreditCycle/Rule/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 ProCyclicalLender (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `ProCyclicalLender.decide()` reads `market_data["deviation"]`; buys when `deviation > expansion_threshold`, sells when `deviation < contraction_threshold`, and sizes with `order_size * credit_multiplier`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rule/players.yml:procyclicallender.config.extras` supplies `expansion_threshold`, `contraction_threshold`, `credit_multiplier`, and `order_size`. |
| Variant-specific decision mechanism | Deterministic threshold order construction with no remote model call. |
### §2.2 MinskyBorrower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `MinskyBorrower.decide()` tracks `stable_rounds`; buys after stability accumulation and sells aggressively when `deviation < crisis_threshold`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rule/players.yml:minskyborrower.config.extras` supplies `crisis_threshold`, phase sizes, leverage parameters, and `order_size`. |
| Variant-specific decision mechanism | Deterministic stability-counter and crisis-threshold logic. |
### §2.3 CounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `CounterCyclicalLender.decide()` buys below `crisis_buy_threshold` and sells above `boom_sell_threshold`, opposing the pro-cyclical agents. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rule/players.yml:countercyclicallender.config.extras` supplies `crisis_buy_threshold`, `boom_sell_threshold`, and `order_size`. |
| Variant-specific decision mechanism | Deterministic contrarian threshold orders. |
### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `ValueInvestor.decide()` buys when `deviation < -value_discount` and sells when `deviation > value_discount`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rule/players.yml:valueinvestor.config.extras` supplies `value_discount` and `order_size`. |
| Variant-specific decision mechanism | Deterministic fundamental-value threshold orders. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `NoiseTrader.decide()` samples whether to trade using `trade_probability` and chooses buy/sell randomly within available cash/position constraints. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rule/players.yml:noisetrader.config.extras` supplies `trade_probability` and `noise_size`. |
| Variant-specific decision mechanism | Deterministic code path with stochastic random sampling; no LLM is involved. |

## §3 Market Mechanism

`Market.decide()` in `examples/CreditCycle/Rule/players.py` aggregates inbound buy/sell quantities, computes net demand, applies `P(t+1) = P(t) + 0.05 * D(t) + 0.02 * [100-P(t)] + epsilon(t)`, and broadcasts `price`, `fundamental`, and `deviation` to all investors through `configs/CreditCycle/Rule/topology.yml`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/CreditCycle/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/CreditCycle/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/CreditCycle/Rule/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/CreditCycle/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/CreditCycle/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/CreditCycle/Rule/run_creditcycle.py -c configs/CreditCycle/Rule/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- ProCyclicalLender and MinskyBorrower should create boom and deleveraging pressure.
- CounterCyclicalLender and ValueInvestor should supply offsetting orders during bust or mispricing phases.
- A successful full experiment must pass Level-1 execution review and Level-2 structural quality review using `summary.json` and fixed PNG outputs from `Rule/analysis.py`.

## §8 References

See `examples/CreditCycle/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/CreditCycle/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
