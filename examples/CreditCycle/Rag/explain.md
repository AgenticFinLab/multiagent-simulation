# Credit Cycle Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Credit Cycle |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema |
| Theory Reference | `examples/CreditCycle/simulation-bases.md` |
| Market Broadcast | `configs/CreditCycle/Rag/topology.yml` |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

### §2.1 ProCyclicalLender (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RagLLMProCyclicalLender` uses the RuleLLM pro-cyclical system prompt plus retrieved credit-cycle context. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rag/players.yml:procyclicallender.config.extras` supplies cash/position, order caps, ARK policy, and private knowledge settings. |
| Variant-specific decision mechanism | RAG context is injected into `RAG_USER_TEMPLATE`; ARK output is parsed by `decide_with_llm_contract()` and recorded with `rag_context`. |
### §2.2 MinskyBorrower (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RagLLMMinskyBorrower` uses the RuleLLM Minsky prompt plus retrieved leverage-cycle context. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rag/players.yml:minskyborrower.config.extras` supplies cash/position, order caps, ARK policy, and private knowledge settings. |
| Variant-specific decision mechanism | RAG context is injected into `RAG_USER_TEMPLATE`; parsed decisions are logged with fallback and retrieval-quality fields. |
### §2.3 CounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RagLLMCounterCyclicalLender` uses the RuleLLM counter-cyclical prompt plus retrieved credit-stabilization context. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rag/players.yml:countercyclicallender.config.extras` supplies cash/position, order caps, ARK policy, and private knowledge settings. |
| Variant-specific decision mechanism | Retrieved context should help calibrate crisis liquidity and reserve-building decisions. |
### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RagLLMValueInvestor` uses the RuleLLM value-investor prompt plus retrieved valuation and crisis-context evidence. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rag/players.yml:valueinvestor.config.extras` supplies cash/position, order caps, ARK policy, and private knowledge settings. |
| Variant-specific decision mechanism | Retrieved context should refine fundamental-value reasoning without changing the canonical order schema. |
### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RagLLMNoiseTrader` uses the RuleLLM noise-trader prompt plus retrieved context, but remains a stochastic liquidity source. |
| Behavioral parameters from simulation-bases.md §6 | `configs/CreditCycle/Rag/players.yml:noisetrader.config.extras` supplies cash/position, order caps, ARK policy, and private knowledge settings. |
| Variant-specific decision mechanism | RAG context is available for inspection, but the persona remains intentionally weakly informed. |

## §3 Market Mechanism

The coordinator market is inherited from the Rule implementation. `RagLLMInvestor._initialize_rag()` resolves local or shared indexes from `private_knowledge`, `_build_prompt()` queries top-k credit-cycle passages, and `decide()` emits canonical orders with the retrieved `rag_context` preserved for analysis.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/CreditCycle/Rag/players.py` |
| Prompt module | `examples/CreditCycle/Rag/prompts.py` |
| Inference | ARK LLM via `LangChainAPIInference`; embeddings use Hunyuan/LiteLLM through the project RAG configuration. |
| Output parsing | `examples/CreditCycle/llm_decision.py:decide_with_llm_contract()` parses and clamps canonical order JSON. |
| Error handling | Missing knowledge documents or deterministic schema errors fail fast; stochastic API parse-contract failures become explicit logged hold fallbacks and are quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/CreditCycle/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/CreditCycle/Rag/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/CreditCycle/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/CreditCycle/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/CreditCycle/Rag/run_creditcycle_rag.py -c configs/CreditCycle/Rag/simulation.yml
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
