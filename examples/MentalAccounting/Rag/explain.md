# MentalAccounting Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Simulation | MentalAccounting |
| Decision Mechanism | RuleLLM-style decisions augmented with retrieved mental-accounting knowledge |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `net_demand`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 MentalAccountant (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Account segregation | Uses `RULELLM_MENTAL_ACCOUNTANT_SYS` with retrieved context. |
| Reference dependence | User prompt provides entry price, P&L, and relevant knowledge. |
| Decision contract | Parsed output must include action, bid price, quantity, reasoning, and analysis. |

### §2.2 HouseMoneyTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| House-money effect | Uses house-money decision rules plus retrieved examples. |
| Risk sensitivity | Retrieved context may inform reasoning but not change schema constraints. |
| Cash discipline | Player code caps orders by available cash and inventory. |

### §2.3 RationalPortfolioManager (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Whole-portfolio view | Uses rational portfolio RuleLLM prompt. |
| Fundamental anchor | RAG query includes price, fundamental, and deviation. |
| Stabilization | Orders enter the shared market equation. |

### §2.4 SunkCostHolder (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Sunk-cost inertia | Uses sunk-cost RuleLLM prompt with retrieved context. |
| Winner realization | Keeps explicit gain-threshold reasoning. |
| Context trace | Each accepted order stores `rag_context` for analysis. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity | Uses noisy RuleLLM prompt. |
| Weak information | Retrieved context is available but action remains schema-bounded. |
| Bounded random flow | Portfolio constraints are enforced after parsing. |

## §3 Market Mechanism

Rag reuses the Rule market. Retrieved knowledge affects only investor reasoning and order choice; price formation remains the shared MentalAccounting market equation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | Rule market imported from `examples.MentalAccounting.Rule.players` |
| Investors | `RagLLMInvestor` subclasses |
| Retrieval | `ResourceManager`, `KnowledgeStore`, and per-round `KnowledgeQuery` |
| Prompt Structure | RuleLLM system prompt plus `RAG_USER_TEMPLATE` with `{rag_context}` |
| Output Contract | Required `action`, `bid_price`, `quantity`, `reasoning`, `analysis`, and recorded `rag_context` |
| Error Policy | Missing documents or invalid final decision contracts raise; provider retries are bounded. |

## §5 Config Reference

Primary config: `configs/MentalAccounting/Rag/simulation.yml`. RAG knowledge and embedding settings live in `configs/MentalAccounting/Rag/players.yml` and the project document-source directories.

## §6 Running Instructions

```bash
python examples/MentalAccounting/Rag/run_mentalaccounting.py \
  -c configs/MentalAccounting/Rag/simulation.yml
```

## §7 Expected Behavior

- Retrieved knowledge is recorded in each accepted order as `rag_context`.
- The standard order schema remains identical to RuleLLM.
- `Rag/analysis.py` writes the standard analysis outputs plus `rag_stats.json`.
- Retrieval failures are visible through the RAG statistics rather than hidden in the market state.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
