# Herd Effect LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Herd Effect |
| Decision Mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning |
| Theory Reference | `examples/HerdEffect/simulation-bases.md` |
| Market Broadcast | `configs/HerdEffect/LLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumInvestor (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `LLMMomentumInvestor` uses `LLM_MOMENTUM_SYS` and `LLM_USER_TEMPLATE` to interpret return, recent prices, cash, and position. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/LLM/players.yml:llm_momentum.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | ARK LLM emits `<decision>` JSON with `action`, `bid_price`, `quantity`, and `reasoning`; `LLMInvestor.decide()` parses and clamps cash/position. |
### §2.2 ContrarianInvestor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `LLMContrarianInvestor` uses `LLM_CONTRARIAN_SYS` to express value/mean-reversion reasoning against current price. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/LLM/players.yml:llm_contrarian.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-only ARK decision parsed into signed `quantity` and `bid_price`. |
### §2.3 RiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `LLMRiskAverseInvestor` uses `LLM_RISK_AVERSE_SYS` to reason about volatility and reduce exposure in unstable markets. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/LLM/players.yml:llm_risk_averse.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-only ARK decision parsed into the order-book trading schema. |
### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `LLMNoiseTrader` uses `LLM_NOISE_SYS` to produce unsystematic signed orders. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/LLM/players.yml:llm_noise.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-only ARK decision parsed into the order-book trading schema. |
### §2.5 AggressiveInvestor (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `LLMAggressiveInvestor` uses `LLM_AGGRESSIVE_SYS` to express high-conviction acceleration-based momentum. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/LLM/players.yml:llm_aggressive.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Persona-only ARK decision parsed into the order-book trading schema. |

## §3 Market Mechanism

The coordinator market is implemented in `examples/HerdEffect/LLM/players.py` with the same order-book price equation as the Rule baseline. LLM investors submit signed `quantity` orders with `bid_price`, `reasoning`, `cash`, and `position` fields through `configs/HerdEffect/LLM/topology.yml`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdEffect/LLM/players.py` |
| Prompt module | `examples/HerdEffect/LLM/prompts.py` |
| Inference | ARK LLM via `examples.llm_utils.call_llm` and `ark/doubao-seed-2-0-mini-260428`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks; parse failures are retried up to three times and then fail fast. |
| Error handling | Deterministic config/schema/API errors fail fast; this variant does not silently fallback after malformed decisions. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdEffect/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdEffect/LLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdEffect/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdEffect/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdEffect/LLM/run_herd_llm.py -c configs/HerdEffect/LLM/simulation.yml
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
