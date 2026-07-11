# Asset Bubble Rag Variant Explanation

## §1 Overview

| Field              | Value                                                                                        |
|--------------------|----------------------------------------------------------------------------------------------|
| Variant            | Rag                                                                                          |
| Simulation         | Asset Bubble                                                                                 |
| Decision Mechanism | RAG-augmented trading orders using retrieved domain knowledge and the canonical order schema |
| Theory Reference   | `examples/AssetBubble/simulation-bases.md`                                                   |
| Market Broadcast   | `configs/AssetBubble/Rag/topology.yml`                                                       |

This is a trading-schema scenario. API decisions emit action, bid_price, quantity, and reasoning fields consumed by players.py.

## §2 Theory -> Implementation Mapping

The Rag variant uses the same RuleLLM rule/persona structure and injects
retrieved domain context into `{rag_context}` before each LLM decision. All
investors use the same canonical trading order schema as the other API modes.

| Investor                    | Theory reference           | Code implementation                                                                                                                                           | Prompt/config mapping                                                           | RAG mapping                                                                                       |
|-----------------------------|----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------|
| `RagLLMMomentumSpeculator`  | `simulation-bases.md §4.1` | `players.py::RagLLMInvestor.decide()` retrieves context, calls the configured prompt, parses `<decision>` JSON, applies constraints, and validates the order. | `ragllm_momentum.config.extras.llm.sys_message -> RAGLLM_MOMENTUM_SYS`          | Queries momentum, price/fundamental ratio, and demand context against the shared knowledge store. |
| `RagLLMRationalArbitrageur` | `simulation-bases.md §4.2` | Shared RAG decision path.                                                                                                                                     | `ragllm_arbitrageur.config.extras.llm.sys_message -> RAGLLM_ARBITRAGEUR_SYS`    | Retrieves limits-to-arbitrage and short-selling context.                                          |
| `RagLLMNoiseTrader`         | `simulation-bases.md §4.3` | Shared RAG decision path.                                                                                                                                     | `ragllm_noise.config.extras.llm.sys_message -> RAGLLM_NOISE_SYS`                | Retrieves sentiment, herding, and crowd-psychology context.                                       |
| `RagLLMFundamentalInvestor` | `simulation-bases.md §4.4` | Shared RAG decision path.                                                                                                                                     | `ragllm_fundamental_investor.config.extras.llm.sys_message -> RAGLLM_VALUE_SYS` | Retrieves value-investing and fundamental-analysis context.                                       |
| `RagLLMLeveragedBuyer`      | `simulation-bases.md §4.5` | Shared RAG decision path.                                                                                                                                     | `ragllm_leveraged.config.extras.llm.sys_message -> RAGLLM_LEVERAGED_SYS`        | Retrieves leverage-cycle and margin-call context.                                                 |
| `RagLLMConservativeHolder`  | `simulation-bases.md §4.6` | Shared RAG decision path; added to topology as `ragllm_conservative`.                                                                                         | `ragllm_conservative.config.extras.llm.sys_message -> RAGLLM_CONSERVATIVE_SYS`  | Retrieves strategic allocation and stabilizing-demand context.                                    |

## §3 Market Mechanism

The coordinator is `players.py::Market`, matching the Rule price equation and
broadcast schema. `RagLLMInvestor._build_prompt()` formulates a `KnowledgeQuery`
from price, price/fundamental ratio, round return, and net demand; the retrieved
text is injected into `RAGLLM_USER_TEMPLATE` and recorded as `rag_context` for
post-run retrieval-quality analysis.

## §4 Variant Architecture

| Component      | Implementation                                                                                                                                                                                               |
|----------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Player classes | `examples/AssetBubble/Rag/players.py`                                                                                                                                                                        |
| Prompt module  | `examples/AssetBubble/Rag/prompts.py`                                                                                                                                                                        |
| Inference      | Uses the project ARK LLM policy for decisions and Hunyuan/LiteLLM embedding policy for retrieval.                                                                                                            |
| Output parsing | `parse_llm_response_with_thinking()` requires `<analysis>` and `<decision>`; parsed orders include `action`, `bid_price`, `quantity`, `reasoning`, and recorded `rag_context`, then pass `validate_order()`. |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited.                                                        |

## §5 Config Reference

| Config                                   | Purpose                                                             |
|------------------------------------------|---------------------------------------------------------------------|
| `configs/AssetBubble/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/AssetBubble/Rag/players.yml`    | Player class paths, extras, and model or retrieval configuration.   |
| `configs/AssetBubble/Rag/topology.yml`   | Message routing between coordinator and agents.                     |
| `configs/AssetBubble/Rag/persona.yml`    | Turn recording and persona metadata.                                |

## §6 Running Instructions

```bash
python examples/AssetBubble/Rag/run_bubble_ragllm.py -c configs/AssetBubble/Rag/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/AssetBubble/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/AssetBubble/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
