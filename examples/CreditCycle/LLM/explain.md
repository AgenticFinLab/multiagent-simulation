# Credit Cycle LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | Credit Cycle |
| Decision Mechanism | LLM-generated trading orders with action, bid_price, quantity, and reasoning |
| Theory Reference | `examples/CreditCycle/simulation-bases.md` |
| Market Broadcast | `configs/CreditCycle/LLM/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 ProCyclicalLender (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `LLMProCyclicalLender` uses persona prompt `LLM_PRO_CYCLICAL_LENDER_SYS` and current `market_data` to choose credit-cycle-amplifying orders. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/LLM/players.yml:procyclicallender.config.extras` supplies cash/position and LLM policy; `llm_decision.infer_max_order_size()` derives the single-order cap. |
| Variant-specific decision mechanism | ARK LLM output is parsed by `decide_with_llm_contract()` into `action`, `bid_price`, `quantity`, and `reasoning`; stochastic parse failures are logged as conservative hold fallbacks. |
### §2.2 MinskyBorrower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `LLMMinskyBorrower` uses `LLM_MINSKY_BORROWER_SYS` to express calm-period leverage accumulation and crisis deleveraging. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/LLM/players.yml:minskyborrower.config.extras` supplies cash/position and LLM policy; order caps are inferred from phase/order-size extras. |
| Variant-specific decision mechanism | ARK LLM output is parsed by `decide_with_llm_contract()` and clamped against cash, position, and max-order constraints. |
### §2.3 CounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `LLMCounterCyclicalLender` uses `LLM_COUNTER_CYCLICAL_LENDER_SYS` to provide crisis liquidity and reserve-building behavior. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/LLM/players.yml:countercyclicallender.config.extras` supplies cash/position and LLM policy. |
| Variant-specific decision mechanism | Persona-only ARK decision, canonical JSON parser, and explicit fallback counters in `llm_fallback_counts`. |
### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `LLMValueInvestor` uses `LLM_VALUE_INVESTOR_SYS` to anchor decisions on fundamental mispricing. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/LLM/players.yml:valueinvestor.config.extras` supplies cash/position and LLM policy. |
| Variant-specific decision mechanism | Persona-only ARK decision parsed into the canonical trading schema. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `LLMNoiseTrader` uses `LLM_NOISE_TRADER_SYS` to provide unsystematic trading pressure. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/LLM/players.yml:noisetrader.config.extras` supplies cash/position and LLM policy. |
| Variant-specific decision mechanism | Persona-only ARK decision parsed into the canonical trading schema. |

## §3 Market Mechanism

The coordinator market is inherited from `examples.CreditCycle.Rule.players:Market` and uses the same price-impact/mean-reversion equation as the Rule baseline. LLM investors receive the broadcast state, format `LLM_USER_TEMPLATE`, call the configured ARK model, and submit canonical order payloads through `configs/CreditCycle/LLM/topology.yml`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/CreditCycle/LLM/players.py` |
| Prompt module | `examples/CreditCycle/LLM/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference` with `ark/doubao-seed-2-0-mini-260428`. |
| Output parsing | `examples/CreditCycle/llm_decision.py:decide_with_llm_contract()` parses exactly one `<decision>{...}</decision>` block. |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse-contract failures become explicit logged hold fallbacks and are quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/CreditCycle/LLM/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/CreditCycle/LLM/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/CreditCycle/LLM/topology.yml` | Message routing between coordinator and agents. |
| `configs/CreditCycle/LLM/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/CreditCycle/LLM/run_creditcycle_llm.py -c configs/CreditCycle/LLM/simulation.yml
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
