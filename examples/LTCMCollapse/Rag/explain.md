# LTCMCollapse Rag — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RuleLLM-style prompts plus retrieved crisis knowledge in `{rag_context}` |
| Key Difference | tests whether historical and domain knowledge changes LTCM-style stress decisions |
| Files | `players.py`, `prompts.py`, `run_ltcmcollapse_rag.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Theory Component | Implementation |
|---|---|
| ConvergenceArbitrageur (`simulation-bases.md §4.1`) | `RagLLMConvergenceArbitrageur` uses `RAG_CONVERGENCEARBITRAGEUR_PROMPT`; retrieved knowledge can contextualize spread widening and convergence risk |
| LeverageTrader (`simulation-bases.md §4.2`) | `RagLLMLeverageTrader` uses `RAG_LEVERAGETRADER_PROMPT`; retrieved knowledge can emphasize funding spirals |
| RiskManager (`simulation-bases.md §4.3`) | `RagLLMRiskManager` uses `RAG_RISKMANAGER_PROMPT`; retrieved knowledge can inform risk-limit urgency |
| LiquidityProvider (`simulation-bases.md §4.4`) | `RagLLMLiquidityProvider` uses `RAG_LIQUIDITYPROVIDER_PROMPT`; retrieved knowledge can inform liquidity withdrawal |
| CentralBank (`simulation-bases.md §4.5`) | `RagLLMCentralBank` uses `RAG_CENTRALBANK_PROMPT`; retrieved knowledge can inform intervention rationale |

## §3 Market Mechanism Implementation

The market is imported from Rule and remains identical to `simulation-bases.md §3.1`.

RAG-specific user messages include:

```text
Relevant crisis knowledge retrieved for this decision:
{rag_context}
```

## §4 Variant-Specific Features

RAG system prompts alias the standardized RuleLLM prompts. This ensures each agent has both `== PERSONA ==` and `== DECISION RULES ==`.

The RAG user template adds retrieved crisis knowledge. If no scenario-specific context is available, `RagLLMInvestor._initialize_rag()` returns an explicit fallback string. This is recorded in the reasoning context rather than silently changing the action schema.

## §5 Architecture Diagram

```text
Rule market broadcast
  -> RagLLMInvestor.perceive()
  -> _initialize_rag()
       -> read private_knowledge.rag / context template
       -> fallback text if no context template is configured
  -> RAG_USER_TEMPLATE.format(..., rag_context=context)
  -> LLM decision parsing
  -> emit standard order
```

## §6 Configuration Reference

| Config Area | File | Notes |
|---|---|---|
| knowledge | `configs/LTCMCollapse/Rag/players.yml` | `private_knowledge.rag` uses Hunyuan embedding config |
| prompts | `examples/LTCMCollapse/Rag/prompts.py` | RuleLLM prompts plus RAG user template |
| model | `configs/LTCMCollapse/Rag/players.yml` | `ark/doubao-seed-2-0-mini-260428` |
| rounds | `configs/LTCMCollapse/Rag/simulation.yml` | 200 configured rounds |

## §7 Expected Behavior Patterns

RAG should preserve the RuleLLM action schema while allowing historical crisis knowledge to influence reasoning. Valid samples should show completed rounds, low malformed-output rates, and reviewed fallback counts.

## §8 Validation Checklist

- `RAG_USER_TEMPLATE` includes `{rag_context}`.
- RAG embedding config uses `litellm` and `openai/hunyuan-embedding`.
- Prompt/parser contract checks should report zero issues.
- Full runs should complete 200 rounds with valid decision JSON and usable retrieval context.

## §9 References

- `../simulation-bases.md`
- `../analysis-bases.md`
- `prompts.py`
- `players.py`
- `configs/LTCMCollapse/Rag/players.yml`
