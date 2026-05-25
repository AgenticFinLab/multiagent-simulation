# OverconfidenceBias Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Simulation | OverconfidenceBias |
| Decision Mechanism | RuleLLM-style decisions augmented with retrieved behavioral-finance context |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 OverconfidentTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Signal overprecision | Uses RuleLLM prompt plus retrieved overconfidence context. |
| Excess trading | Order schema remains canonical and comparable. |
| Context trace | Accepted orders record `rag_context`. |

### §2.2 SelfAttributor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Self-attribution | Retrieved context may inform the model's explanation of confidence. |
| Reinforcement | Explicit rules still define directional logic. |
| Auditability | RAG statistics record retrieval coverage. |

### §2.3 CalibratedTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Benchmark discipline | Uses calibrated RuleLLM prompt. |
| Knowledge use | Retrieval can support cautious reasoning. |
| Schema validity | Player validates all decision fields. |

### §2.4 ContrarianInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Overreaction fading | Retrieved context can justify contrarian correction. |
| Stabilization | Orders enter the shared Rule market. |
| Context trace | `rag_context` is stored with each order. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background liquidity | Uses noisy RuleLLM prompt. |
| Weak information | Retrieved context is available but not a schema substitute. |
| Bounded action | Quantity remains non-negative and constrained. |

## §3 Market Mechanism

Rag reuses the Rule market. Retrieval affects only investor reasoning and action choice, not the price equation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | Rule market |
| Investors | `RagLLMInvestor` subclasses |
| Retrieval | `ResourceManager`, `KnowledgeStore`, and per-round `KnowledgeQuery` |
| Prompt Structure | RuleLLM system prompt plus `RAG_USER_TEMPLATE` with `{rag_context}` |
| Output Contract | Required `action`, `bid_price`, `quantity`, `reasoning`, `analysis`, and recorded `rag_context` |
| Error Policy | Missing documents or invalid final decision contracts raise; provider retries are bounded. |

## §5 Config Reference

Primary config: `configs/OverconfidenceBias/Rag/simulation.yml`. Embedding and document-source settings use the project RAG configuration convention.

## §6 Running Instructions

```bash
python examples/OverconfidenceBias/Rag/run_overconfidencebias_rag.py \
  -c configs/OverconfidenceBias/Rag/simulation.yml
```

## §7 Expected Behavior

- Retrieved context is recorded in accepted orders.
- `Rag/analysis.py` writes standard outputs plus `rag_stats.json`.
- Market dynamics remain comparable with RuleLLM.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
