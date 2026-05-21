# Herding Information Cascade Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Herding Information Cascade |
| Decision Mechanism | deterministic rule-based trading orders |
| Theory Reference | `examples/HerdingInformation/simulation-bases.md` |
| Market Broadcast | `configs/HerdingInformation/Rule/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `CascadeFollower.decide()` increments `cascade_count` when `abs(deviation) > 0.03`; once `cascade_count >= cascade_trigger`, it follows deviation direction. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rule/players.yml:cascadefollower.config.extras` supplies `social_weight`, `cascade_trigger`, cash, and position state. |
| Variant-specific decision mechanism | Deterministic buy/sell/hold quantity from `min(800, int(abs(deviation) * social_weight * 5000))`. |
### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `ReputationHerder.decide()` follows deviation direction whenever `abs(deviation) > 0.02`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rule/players.yml:reputationherder.config.extras` supplies `reputation_concern`, cash, and position state. |
| Variant-specific decision mechanism | Deterministic quantity from `min(600, int(abs(deviation) * reputation_concern * 4000))`. |
### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `IndependentThinker.decide()` trades against deviation when `abs(deviation) > 0.03`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rule/players.yml:independentthinker.config.extras` supplies `signal_precision`, cash, and position state. |
| Variant-specific decision mechanism | Deterministic contrarian quantity from `min(500, int(abs(deviation) * signal_precision * 3000))`. |
### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `Contrarian.decide()` trades against deviation when `abs(deviation) > contrarian_threshold * 0.05`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rule/players.yml:contrarian.config.extras` supplies `contrarian_threshold`, cash, and position state. |
| Variant-specific decision mechanism | Deterministic quantity from `min(400, int(abs(deviation) * 2000))`. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `NoiseTrader.decide()` trades randomly with probability `trade_probability`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/Rule/players.yml:noisetrader.config.extras` supplies `trade_probability`, cash, and position state. |
| Variant-specific decision mechanism | Random buy/sell quantity from 100 to 500 shares subject to affordability and holdings. |

## §3 Market Mechanism

`Market.decide()` in `examples/HerdingInformation/Rule/players.py` broadcasts `price`, `fundamental`, `deviation`, and `round`. `Market.perceive()` aggregates buy/sell order quantities and updates price with `price + price_impact * net_demand + mean_reversion * (fundamental - price) + noise`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdingInformation/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic Rule logic has no API fallback path; config/schema errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdingInformation/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdingInformation/Rule/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdingInformation/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdingInformation/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdingInformation/Rule/run_herdinginformation.py -c configs/HerdingInformation/Rule/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/HerdingInformation/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/HerdingInformation/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
