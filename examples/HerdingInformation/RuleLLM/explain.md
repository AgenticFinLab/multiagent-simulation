# Herding Information Cascade RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Herding Information Cascade |
| Decision Mechanism | LLM-generated trading orders constrained by explicit scenario rules |
| Theory Reference | `examples/HerdingInformation/simulation-bases.md` |
| Market Broadcast | `configs/HerdingInformation/RuleLLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 CascadeFollower (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RuleLLMCascadeFollower` uses `RULELLM_CASCADE_FOLLOWER_SYS`, whose explicit rules encode cascade-count activation and deviation-following orders. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/RuleLLM/players.yml:cascadefollower.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Rule-anchored ARK output parsed into `action`, `bid_price`, `quantity`, and `reasoning`; `players.py` executes the parsed action and quantity. |
### §2.2 ReputationHerder (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RuleLLMReputationHerder` uses `RULELLM_REPUTATION_HERDER_SYS`, whose rules encode reputation-concern following once `abs(deviation) > 0.02`. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/RuleLLM/players.yml:reputationherder.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Rule-anchored ARK output parsed into the shared trading schema. |
### §2.3 IndependentThinker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RuleLLMIndependentThinker` uses `RULELLM_INDEPENDENT_THINKER_SYS`, whose rules encode fundamental-value opposition to cascade mispricing. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/RuleLLM/players.yml:independentthinker.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Rule-anchored ARK output parsed into the shared trading schema. |
### §2.4 Contrarian (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RuleLLMContrarian` uses `RULELLM_CONTRARIAN_SYS`, whose rules encode crowd-opposing trades above the contrarian threshold. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/RuleLLM/players.yml:contrarian.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Rule-anchored ARK output parsed into the shared trading schema. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RuleLLMNoiseTrader` uses `RULELLM_NOISE_TRADER_SYS`, whose rules encode probabilistic uninformed buy/sell orders. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdingInformation/RuleLLM/players.yml:noisetrader.config.extras` supplies portfolio state and ARK model policy. |
| Variant-specific decision mechanism | Rule-anchored ARK output parsed into the shared trading schema. |

## §3 Market Mechanism

The RuleLLM variant reuses the Rule `Market` class. The market broadcasts `price`, `fundamental`, `deviation`, and `round`; RuleLLM investors submit parsed buy/sell/hold orders that are aggregated by the same price equation as the Rule baseline.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdingInformation/RuleLLM/players.py` |
| Prompt module | `examples/HerdingInformation/RuleLLM/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference` and `ark/doubao-seed-2-0-mini-260428`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks; parse failures are retried three times and then fail fast. |
| Error handling | Deterministic config/schema/API errors fail fast; this variant does not silently fallback after malformed decisions. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdingInformation/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdingInformation/RuleLLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdingInformation/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdingInformation/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdingInformation/RuleLLM/run_herdinginformation_rulellm.py -c configs/HerdingInformation/RuleLLM/simulation.yml
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
