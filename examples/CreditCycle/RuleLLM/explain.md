# Credit Cycle RuleLLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | RuleLLM |
| Simulation | Credit Cycle |
| Decision Mechanism | LLM-generated trading orders constrained by explicit scenario rules |
| Theory Reference | `examples/CreditCycle/simulation-bases.md` |
| Market Broadcast | `configs/CreditCycle/RuleLLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 ProCyclicalLender (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RuleLLMProCyclicalLender` uses `RULELLM_PRO_CYCLICAL_LENDER_SYS`, whose `== DECISION RULES ==` encode pro-cyclical expansion and contraction thresholds. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/RuleLLM/players.yml:procyclicallender.config.extras` supplies cash/position, order caps, and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK LLM output parsed by `decide_with_llm_contract()` into the canonical order schema. |
### §2.2 MinskyBorrower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RuleLLMMinskyBorrower` uses `RULELLM_MINSKY_BORROWER_SYS` to bind calm-period leverage and crisis deleveraging to explicit rules. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/RuleLLM/players.yml:minskyborrower.config.extras` supplies cash/position, phase parameters, and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed and clamped by the shared CreditCycle decision helper. |
### §2.3 CounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RuleLLMCounterCyclicalLender` uses `RULELLM_COUNTER_CYCLICAL_LENDER_SYS` to encode crisis-buy and boom-sell stabilizing behavior. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/RuleLLM/players.yml:countercyclicallender.config.extras` supplies cash/position, order caps, and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision with explicit fallback counters for stochastic parse failures. |
### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RuleLLMValueInvestor` uses `RULELLM_VALUE_INVESTOR_SYS` to encode fundamental discount/premium rules. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/RuleLLM/players.yml:valueinvestor.config.extras` supplies cash/position, order caps, and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed into the canonical order schema. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RuleLLMNoiseTrader` uses `RULELLM_NOISE_TRADER_SYS` to keep stochastic liquidity behavior bounded by explicit rules. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/RuleLLM/players.yml:noisetrader.config.extras` supplies cash/position, order caps, and ARK policy. |
| Variant-specific decision mechanism | Rule-anchored ARK decision parsed into the canonical order schema. |

## §3 Market Mechanism

The coordinator market is inherited from the Rule implementation. `RuleLLMInvestor.decide()` formats `RULELLM_USER_TEMPLATE` with price, fundamental, deviation, portfolio state, and maximum single-order quantity; it then calls the configured ARK model and emits canonical trading orders.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/CreditCycle/RuleLLM/players.py` |
| Prompt module | `examples/CreditCycle/RuleLLM/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference` with `ark/doubao-seed-2-0-mini-260428`. |
| Output parsing | `examples/CreditCycle/llm_decision.py:decide_with_llm_contract()` parses and clamps canonical order JSON. |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse-contract failures become explicit logged hold fallbacks and are quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/CreditCycle/RuleLLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/CreditCycle/RuleLLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/CreditCycle/RuleLLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/CreditCycle/RuleLLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/CreditCycle/RuleLLM/run_creditcycle_rulellm.py -c configs/CreditCycle/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/CreditCycle/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/CreditCycle/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
