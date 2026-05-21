# Herd Effect RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Herd Effect |
| Decision Mechanism | LLM-generated trading orders constrained by explicit scenario rules |
| Theory Reference | `examples/HerdEffect/simulation-bases.md` |
| Market Broadcast | `configs/HerdEffect/RuleLLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 MomentumInvestor (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RuleLLMMomentumInvestor` uses `RULELLM_MOMENTUM_SYS`, whose `== DECISION RULES ==` encode the MomentumInvestor return-following formula. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/RuleLLM/players.yml:rulellm_momentum.config.extras` supplies portfolio state and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed into signed order-book fields. |
### §2.2 ContrarianInvestor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RuleLLMContrarianInvestor` uses `RULELLM_CONTRARIAN_SYS`, whose rules encode the fundamental-gap contrarian formula. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/RuleLLM/players.yml:rulellm_contrarian.config.extras` supplies `fundamental`, portfolio state, and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed into signed order-book fields. |
### §2.3 RiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RuleLLMRiskAverseInvestor` uses `RULELLM_RISK_AVERSE_SYS`, whose rules encode inverse-variance target sizing. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/RuleLLM/players.yml:rulellm_risk_averse.config.extras` supplies portfolio state and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed into signed order-book fields. |
### §2.4 NoiseTrader (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RuleLLMNoiseTrader` uses `RULELLM_NOISE_SYS`, whose rules encode noisy bid and mean-reverting quantity behavior. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/RuleLLM/players.yml:rulellm_noise.config.extras` supplies portfolio state and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed into signed order-book fields. |
### §2.5 AggressiveInvestor (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RuleLLMAggressiveInvestor` uses `RULELLM_AGGRESSIVE_SYS`, whose rules encode acceleration-enhanced momentum. |
| Behavioral parameters from simulation-bases.md §6 | `configs/HerdEffect/RuleLLM/players.yml:rulellm_aggressive.config.extras` supplies portfolio state and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed into signed order-book fields. |

## §3 Market Mechanism

The coordinator market is implemented in `examples/HerdEffect/RuleLLM/players.py` with the same order-book price equation as the Rule baseline. `BaseLLMInvestor.decide()` formats `RULELLM_USER_TEMPLATE`, calls ARK through `examples.llm_utils.call_llm`, and records `bid_price`, signed `quantity`, `reasoning`, `cash`, and `position`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/HerdEffect/RuleLLM/players.py` |
| Prompt module | `examples/HerdEffect/RuleLLM/prompts.py` |
| Inference | ARK LLM via `examples.llm_utils.call_llm` and `ark/doubao-seed-2-0-mini-260428`. |
| Output parsing | `parse_llm_response_with_thinking()` parses `<analysis>` and `<decision>` blocks; retryable API failures may produce explicit hold fallback metadata. |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/HerdEffect/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/HerdEffect/RuleLLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/HerdEffect/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/HerdEffect/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/HerdEffect/RuleLLM/run_herd_rulellm.py -c configs/HerdEffect/RuleLLM/simulation.yml
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
