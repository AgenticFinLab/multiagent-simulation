# Volmageddon Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Volmageddon |
| Decision Mechanism | Retrieved domain knowledge plus API reasoning over current-market volatility quantities |
| Theory Reference | `examples/Volmageddon/simulation-bases.md` |
| Market Broadcast | `configs/Volmageddon/Rag/topology.yml` |

Rag keeps Volmageddon's current-market quantity schema and adds per-round
retrieval context. Investor payloads include `rag_context` so Level-2 review can
verify whether retrieved knowledge was available rather than assuming RAG was
effective.

## §2 Theory -> Implementation Mapping

### §2.1 ShortVolTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Short-vol carry and stop-loss covering | `RagLLMShortVolTrader` combines retrieved volatility-product context with the short-carry persona. |
| Required config | Portfolio initialization, knowledge config, private RAG config, and `agent_type: short_vol_trader`. |
| Output contract | Quantity-only decision plus `rag_context` and parser fallback metadata. |

### §2.2 VolETNManager (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Mechanical inverse-product rebalance | `RagLLMVolETNManager` retrieves knowledge about ETN mechanics and applies it to rebalance urgency. |
| Required config | Knowledge/RAG config and `agent_type: vol_e_t_n_manager`. |
| Output contract | `action`, `quantity`, `reasoning`, `analysis`, and `rag_context`; no `bid_price`. |

### §2.3 LongVolHedger (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Hedge accumulation and spike profit-taking | `RagLLMLongVolHedger` retrieves historical context on hedging and volatility stress. |
| Required config | Knowledge/RAG config and `agent_type: long_vol_hedger`. |
| Output contract | Quantity-only order constrained by current cash/inventory. |

### §2.4 VolArbitrageur (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Volatility dislocation arbitrage | `RagLLMVolArbitrageur` retrieves term-structure and arbitrage context. |
| Required config | Knowledge/RAG config and `agent_type: vol_arbitrageur`. |
| Output contract | Current-market quantity order plus retrieval audit fields. |

### §2.5 EquityTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Volatility-linked equity de-risking | `RagLLMEquityTrader` retrieves context on equity stress and volatility feedback. |
| Required config | Knowledge/RAG config and `agent_type: equity_trader`. |
| Output contract | Structured API decision with `rag_context` for quality audit. |

## §3 Market Mechanism

The Rag variant reuses the Rule market. Retrieval affects investor reasoning
only; market clearing remains the same net-demand update over `action` and
`quantity`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/Volmageddon/Rag/players.py` |
| Prompt module | `examples/Volmageddon/Rag/prompts.py` |
| Inference | Project ARK model policy plus Hunyuan/LiteLLM embedding policy |
| Retrieval | `KnowledgeStore` over configured document sources with `top_k: 5` |
| Output parsing | Required `action`, `quantity`, and `reasoning` validation |
| Error handling | Missing documents/index failures fail; parse fallback is explicit and auditable |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/Volmageddon/Rag/simulation.yml` | 200-round simulation entry point and record path |
| `configs/Volmageddon/Rag/players.yml` | Class paths, portfolio initialization, LLM config, and RAG config |
| `configs/Volmageddon/Rag/topology.yml` | Market update and investor order routing |
| `configs/Volmageddon/Rag/persona.yml` | Persona and recording metadata |

## §6 Running Instructions

```bash
python examples/Volmageddon/Rag/run_volmageddon_rag.py -c configs/Volmageddon/Rag/simulation.yml
```

## §7 Expected Behavior

- RAG decisions should preserve the Volmageddon quantity schema.
- `rag_context` should be recorded for every investor decision after
  initialization.
- `rag_stats.json` should report retrieval success/failure rates by agent.
- Full samples require both execution success and retrieval-quality review.

## §8 References

See `examples/Volmageddon/simulation-bases.md §2` and `§8`.

## §9 Variant Comparison

Rag is compared with RuleLLM to test whether retrieved historical volatility
knowledge changes urgency or quantity while preserving the same rule-constrained
schema.
