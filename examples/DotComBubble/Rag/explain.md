# DotComBubble Rag — Implementation Explanation

## 1. Overview

The Rag variant keeps the five investor archetypes and market mechanism from
`simulation-bases.md`, but grounds each LLM decision with retrieved historical
or academic context. The implementation is fail-fast: missing config fields,
invalid market prices, unavailable processed documents, and malformed LLM
decisions raise explicit errors rather than silently becoming hold orders.

| Aspect | Implementation |
|---|---|
| Entry point | `run_dotcombubble_rag.py` |
| Market | `Market`, reused from `Rule/players.py` |
| Investor base | `RagLLMInvestor` in `players.py` |
| Decision contract | `action`, `bid_price`, `quantity`, `reasoning`, `analysis` |
| Retrieval record | `rag_context`, with `_RAG_FALLBACK` for empty retrieval |
| Design anchors | `simulation-bases.md §3–§7`; `analysis-bases.md §2` |

## 2. Theory → Implementation Mapping

| Design block | Implementing class | Prompt / mechanism |
|---|---|---|
| `§4.1 NewEconomyEvangelist` | `RagLLMNewEconomyEvangelist` | Narrative-buyer rules plus retrieved dot-com history |
| `§4.2 IPOFlipper` | `RagLLMIPOFlipper` | Dip-buy/pop-sell rules plus IPO evidence |
| `§4.3 MomentumFollower` | `RagLLMMomentumFollower` | Trend rules plus momentum-crash evidence |
| `§4.4 SkepticalValueInvestor` | `RagLLMSkepticalValueInvestor` | Fundamental thresholds plus recovery evidence |
| `§4.5 ShortSeller` | `RagLLMShortSeller` | Synchronisation-risk rules plus short-squeeze evidence |

All five classes inherit the same retrieval, prompt construction, parsing,
portfolio constraint, and recording path. Their config-selected system prompts
provide the archetype-specific behavior.

## 3. Environment Mechanism Implementation

`Market` implements the model from `simulation-bases.md §3`:

```text
P(t+1) = max(P(t) + λD(t) + γ(F-P(t)) + ε(t), 0.01)
```

The Rag config uses the documented baseline: initial price and fundamental
`100.0`, price impact `0.01`, mean reversion `0.005`, and noise standard
deviation `1.0`. Each round broadcasts `price`, `fundamental`, `deviation`, and
`round`. Investors return canonical orders to the market.

## 4. Rag Variant-Specific Features

`ResourceManager` resolves shared and agent-local resources. `KnowledgeStore`
loads an existing local index, copies a shared index when available, or builds
an index from processed documents. Before inference, `_build_prompt()` queries:

```text
dot-com bubble trading: price=..., fundamental=..., deviation=...
```

The retrieved text is injected into `RAG_USER_TEMPLATE`. Empty retrieval uses
the exact `_RAG_FALLBACK` marker shared by runtime and analysis. Provider or
parser errors are retried three times; exhaustion raises `RuntimeError`.
Required API fields are accessed directly and validated before an order is
recorded.

## 5. Architecture Diagram

```text
Market broadcast
      │
      ▼
RagLLMInvestor ── query ──► KnowledgeStore
      │                         │
      └──── market state ◄──── retrieved context
                    │
                    ▼
             system + user prompt
                    │
                    ▼
            LangChainAPIInference
                    │
                    ▼
      validated order + analysis + rag_context
                    │
                    └────────────► Market
```

## 6. Configuration Reference

| File | Purpose |
|---|---|
| `configs/DotComBubble/Rag/simulation.yml` | rounds, records, Ray, includes |
| `players.yml` | market, five archetypes, LLM and knowledge settings |
| `topology.yml` | bidirectional market-centered star |
| `persona.yml` | checkpoint, monitoring, and communication settings |

The shipped embedding and inference endpoints use `ARK_API_KEY`. The embedding
model is the Ark endpoint `ep-20260418161108-k2pxb`, called through the native
`/embeddings/multimodal` API by the `ark_multimodal` knowledge-store backend.
No credential is embedded in source.

## 7. Running Instructions

From the repository root:

```powershell
.venv\Scripts\python.exe -m examples.DotComBubble.Rag.run_dotcombubble_rag `
  -c configs/DotComBubble/Rag/simulation.yml
```

Run post-analysis after simulation records exist:

```powershell
.venv\Scripts\python.exe -m examples.DotComBubble.Rag.analysis `
  -c configs/DotComBubble/Rag/simulation.yml
```

Simulation records are written below `EXPERIMENT/DotComBubble/Rag/records`;
analysis writes `summary.json`, `rag_stats.json`, and
`dotcombubble_rag_dynamics.png` below the analysis directory.

## 8. Expected Behavior Patterns

- Narrative and momentum agents can amplify the run-up.
- Value and short-selling agents provide constrained stabilising pressure.
- Retrieved crash evidence may moderate demand, but this is a hypothesis to
  test across repeated seeded runs, not a guaranteed outcome.
- Economic metrics are accepted only when AQR shows structurally valid API
  decisions and auditable retrieval coverage.

## 9. References

Theory and empirical references are maintained in `simulation-bases.md §2` and
`§8`. Metric definitions and validation criteria are maintained in
`analysis-bases.md §2` and `§6`; this variant document does not duplicate or
invent citations.
