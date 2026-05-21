# LUNACollapse Rag — Implementation Explanation

## §1 Variant Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RuleLLM prompts plus retrieved stablecoin/depeg context |
| Key Difference | Tests whether crisis knowledge changes death-spiral behavior |

## §2 Theory To Implementation Mapping

| Design Element | Implementation |
|---|---|
| StablecoinHolder (`simulation-bases.md §4.1`) | `RagLLMStablecoinHolder` uses RuleLLM stablecoin prompt plus retrieved context |
| Arbitrageur (`simulation-bases.md §4.2`) | `RagLLMArbitrageur` uses RuleLLM arbitrage prompt plus retrieved context |
| DeFiLender (`simulation-bases.md §4.3`) | `RagLLMDeFiLender` uses RuleLLM liquidation prompt plus retrieved context |
| AnchorDepositor (`simulation-bases.md §4.4`) | `RagLLMAnchorDepositor` uses RuleLLM yield-exit prompt plus retrieved context |
| ValueBuyer (`simulation-bases.md §4.5`) | `RagLLMValueBuyer` uses RuleLLM value-buyer prompt plus retrieved context |

## §3 Market Mechanism Implementation

Rag imports the same `Market` class as Rule. Investors build a prompt from the
RuleLLM system prompt and `RAG_USER_TEMPLATE`, which injects `{rag_context}`.

## §4 Variant-Specific Features

Rag resolves local or shared knowledge indexes through `ResourceManager`, queries
`KnowledgeStore` each round, records `rag_context` on every accepted order, and
fails loudly if the LLM response cannot satisfy the decision contract after
bounded retries.

## §5 Architecture Diagram

```text
Market state -> retrieve context -> RuleLLM-style prompt -> LLM decision JSON -> order
```

## §6 Configuration Reference

Primary config: `configs/LUNACollapse/Rag/players.yml`.

## §7 Expected Behavior Patterns

Retrieved context may amplify panic, liquidation urgency, or value-buyer caution.
The action schema should remain the same as RuleLLM.

## §8 Validation Checklist

Review full-round completion, retrieval health, parser retry/failure quality,
`rag_stats.json`, and scenario metrics.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
