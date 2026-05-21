# SVBBankRun Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RuleLLM-style prompt plus retrieved banking-crisis context. |
| Key Difference from Other Variants | Each API decision receives `rag_context` and records it for retrieval audit. |
| Primary Research Contribution | Tests whether historical bank-crisis knowledge changes withdrawal/support reasoning. |
| Files | `players.py`, `prompts.py`, `run_svbbankrun_rag.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Theory Component | Implementation |
|---|---|
| Depositor -> `simulation-bases.md §4.1` | `RagLLMDepositor` combines withdrawal rules with retrieved bank-run context. |
| SocialMediaInfluencer -> `simulation-bases.md §4.2` | `RagLLMSocialMediaInfluencer` uses panic-amplification rules and retrieved crisis context. |
| BankManager -> `simulation-bases.md §4.3` | `RagLLMBankManager` uses stabilization rules with retrieved ALM context. |
| Regulator -> `simulation-bases.md §4.4` | `RagLLMRegulator` uses policy-intervention rules and retrieved intervention examples. |
| BondTrader -> `simulation-bases.md §4.5` | `RagLLMBondTrader` uses rate-sensitive proxy rules and retrieved duration-loss context. |

## §3 Market Mechanism Implementation

The market is imported from `Rule.players:Market`. RAG changes information
available to agents, not the proxy market formula.

## §4 Variant-Specific Features

`RagLLMInvestor._build_prompt()` retrieves top-k context, injects it into the
user prompt, stores `last_rag_context`, and includes `rag_context` in each
outbound order. `Rag/analysis.py` writes `rag_stats.json`.

## §5 Architecture Diagram

```text
KnowledgeStore -> rag_context -> RagLLMInvestor
Market -> market_update -> RagLLMInvestor -> investor_order + rag_context -> Market
```

## §6 Configuration Contract

`configs/SVBBankRun/Rag/players.yml` defines `private_knowledge.rag` with
`embed_type`, `embed_model`, `embed_api_base`, and `top_k`, plus the same
cash/position parameters used by the proxy market.

## §7 Run Command

```bash
python examples/SVBBankRun/Rag/run_svbbankrun_rag.py -c configs/SVBBankRun/Rag/simulation.yml
```

## §8 Validation Checklist

- `{rag_context}` is injected before every API decision.
- Each recorded order includes `rag_context`.
- `rag_stats.json` reports retrieval success/failure rates.

## §9 Expected Variant Behavior

The Rag variant should preserve the RuleLLM proxy action schema while retrieved
banking-crisis context changes the reasoning behind panic sensitivity,
stabilization, and intervention choices.
