# Herd Effect Rule Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rule |
| Simulation | Herd Effect |
| Decision Mechanism | deterministic rule-based trading orders |
| Theory Reference | `examples/HerdEffect/simulation-bases.md` |
| Market Broadcast | `configs/HerdEffect/Rule/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumInvestor (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `MomentumInvestor.calculate_bid()` reads `market_data["return"]`, computes `bid_price = price * (1 + lambda_price * return)`, and sizes signed quantity from `beta * return * cash / bid_price`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rule/players.yml:investor_momentum.config.extras` supplies `lambda_price` and `beta`. |
| Variant-specific decision mechanism | Deterministic positive-feedback order construction with signed quantity. |
### §2.2 ContrarianInvestor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `ContrarianInvestor.calculate_bid()` reads `fundamental` from extras, bids around fundamental with noise, and sells when price exceeds fundamental. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rule/players.yml:investor_contrarian.config.extras` supplies `fundamental`, `beta`, and `noise_std`. |
| Variant-specific decision mechanism | Deterministic fundamental-gap order construction with stochastic bid-price noise. |
### §2.3 RiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RiskAverseInvestor.calculate_bid()` computes rolling price variance from `price_history` and trades 30% toward an inverse-variance target position. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rule/players.yml:investor_risk_averse.config.extras` supplies `k` and `lookback`. |
| Variant-specific decision mechanism | Deterministic mean-variance sizing with a ±20 share cap. |
### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `NoiseTrader.calculate_bid()` samples noisy bid prices and signed quantities, then pulls position back toward zero through `position_mean_reversion`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rule/players.yml:investor_noise.config.extras` supplies `price_noise_std`, `qty_noise_std`, and `position_mean_reversion`. |
| Variant-specific decision mechanism | Stochastic noise-trader order generation without a remote model call. |
### §2.5 AggressiveInvestor (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `AggressiveInvestor.calculate_bid()` applies a stronger return multiplier and adds acceleration from the last three prices. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/Rule/players.yml:investor_aggressive.config.extras` supplies `kappa`, `beta`, and `accel_bonus`. |
| Variant-specific decision mechanism | Deterministic acceleration-enhanced momentum order construction with a ±80 share cap. |

## §3 Market Mechanism

`Market.decide()` in `examples/HerdEffect/Rule/players.py` aggregates signed `quantity` orders, computes `net_demand`, updates price with `supply_elasticity * net_demand + mean_reversion * (fundamental_value - price) + noise`, and broadcasts `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, and `round`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdEffect/Rule/players.py` |
| Prompt module | Not applicable for Rule baseline |
| Inference | No remote model call is used in the Rule baseline. |
| Output parsing | Direct deterministic decision construction |
| Error handling | Deterministic Rule logic has no API fallback path; config/schema errors fail fast. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdEffect/Rule/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdEffect/Rule/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdEffect/Rule/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdEffect/Rule/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdEffect/Rule/run_herd.py -c configs/HerdEffect/Rule/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/HerdEffect/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/HerdEffect/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
