# CarryTradeUnwind Rag — Implementation Explanation

## §1 Overview

| Item                              | Description                                                                                                                                         |
|-----------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                       | Rag (RAG-augmented LLM with carry crisis knowledge base)                                                                                            |
| **Implements**                    | `../simulation-bases.md`                                                                                                                            |
| **Decision Logic**                | RuleLLM base + per-agent KnowledgeStore; historical carry crisis documents retrieved each round and injected as `{rag_context}` in user prompt      |
| **Key Difference from RuleLLM**   | Each agent queries its own knowledge store (carry crisis papers, historical events) before deciding; retrieved context modifies rule interpretation |
| **Primary Research Contribution** | Does access to historical carry crash knowledge (2008 JPY, 2024 unwind) improve crisis detection and decision quality vs. RuleLLM baseline?         |

---

## §2 How Theoretical Design Is Implemented

### Shared Architecture with RuleLLM
*(All agent formulas and rule embedding identical to RuleLLM variant — see `RuleLLM/explain.md §1`)*

The Rag variant extends RuleLLM by adding:
1. `_initialize_rag()` — builds per-agent KnowledgeStore from `docs_dir` on first run
2. `_build_prompt()` — queries store at decision time, injects top-k chunks as `{rag_context}`
3. `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` — always populated

### Knowledge Base Content Design
*(Source: simulation-bases.md §8 — Historical Cases)*

Each agent's knowledge store contains documents relevant to its role:

| Agent                   | Knowledge Base Focus                                                    |
|-------------------------|-------------------------------------------------------------------------|
| RagCarryTrader          | JPY carry crash papers, UIP deviation studies, carry-to-risk ratios     |
| RagLeveragedCarryFund   | Plantin & Shin (2018), forced liquidation mechanics, stop-loss dynamics |
| RagFundingCurrencyBuyer | Safe-haven demand papers, CHF/JPY appreciation during crises            |
| RagHedgedCarryTrader    | Volatility-adjusted carry literature, Menkhoff et al. (2012)            |
| RagNoiseTrader          | General market noise and liquidity provision                            |

---

## §3 Market Mechanism Implementation

*Identical to Rule and RuleLLM variants — see `Rule/explain.md §2`.*

Broadcast: `{price, fundamental, deviation, round}` — no `return_pct`.

---

## §4 Variant-Specific Features

*(Reference: simulation-bases.md §9 — Rag variant entry)*

**Per-agent knowledge isolation**: Each agent has its own `KnowledgeStore` (not shared). At initialization, each agent builds its index from its assigned `docs_dir`. This simulates real-world information asymmetry.

**Retrieval at every decision round**: Before calling the LLM, each agent:
1. Formulates a query based on current market state (deviation, round)
2. Retrieves top-k documents from its KnowledgeStore
3. Injects retrieved text as `{rag_context}` block in user prompt
4. If no relevant documents: injects fallback string

**User prompt structure (Rag extension)**:
```
[Standard RuleLLM user prompt: market data + portfolio]

== RELEVANT KNOWLEDGE ==
{rag_context}

Based on the above market conditions and relevant knowledge, make your decision.
```

**Index persistence**: On first run, vector index is built and saved to `rag_persist_dir`. Subsequent runs load from disk (fast startup).

**RAG fallback handling**: `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` — always set so prompt template never has empty `{rag_context}`.

---

## §5 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market (Rule) → broadcast {price, fundamental, deviation, round}    ║
║                                                                       ║
║  RagCarryTrader:                                                      ║
║    1. KnowledgeStore.query("carry trade deviation=X crisis")         ║
║       → retrieved: [JPY crash 2008 excerpt, UIP paper chunk...]      ║
║       OR → "(No relevant knowledge retrieved this round.)"           ║
║    2. Build user prompt with {rag_context}                           ║
║    3. LLM (PERSONA + DECISION RULES + rag_context) → decision       ║
║                                                                       ║
║  [Same pattern for all Rag agents, each with own KnowledgeStore]     ║
║         │                                                             ║
║         └──── send orders → Market.perceive() [next round]           ║
╚══════════════════════════════════════════════════════════════════════╝

  KnowledgeStore (per agent, persisted to disk):
  ┌────────────────────────────────────────────┐
  │  docs_dir → chunked → embedded → FAISS     │
  │  query → top-k chunks → rag_context string │
  └────────────────────────────────────────────┘
```

---

## §6 Configuration Reference

Key Rag-specific parameters (`configs/CarryTradeUnwind/Rag/players.yml`):

| Parameter         | Config Path                  | Notes                                              |
|-------------------|------------------------------|----------------------------------------------------|
| `docs_dir`        | `extras.rag.docs_dir`        | Per-agent documents directory                      |
| `rag_persist_dir` | `extras.rag.rag_persist_dir` | Where vector index is saved on disk                |
| `embed_model`     | `extras.rag.embed_model`     | Embedding model for vector store                   |
| `top_k`           | `extras.rag.top_k`           | Number of retrieved chunks per round (typically 3) |
| LLM params        | `extras.llm.*`               | Same as RuleLLM variant                            |
| Market params     | same as Rule                 | Identical FX dynamics                              |

---

## §7 Running Instructions

```bash
# First run: builds RAG index (may take a few minutes)
python examples/CarryTradeUnwind/Rag/run_carrytradeunwind_rag.py \
    -c configs/CarryTradeUnwind/Rag/simulation.yml

# Subsequent runs: loads index from disk (faster)
```

Then analyze:
```bash
python examples/CarryTradeUnwind/Rag/analysis.py \
    -c configs/CarryTradeUnwind/Rag/simulation.yml
```

Required environment variables: LLM API key + embedding API key (if cloud embeddings)

Expected runtime: ~10–45 minutes for 100 rounds (RAG retrieval adds per-round latency)

Output location: `EXPERIMENT/CarryTradeUnwind/Rag/records/`

---

## §8 Expected Behavior Patterns

| Phase        | Rounds | Expected Rag Agent Behavior                                               | Expected Price Dynamics                                  |
|--------------|--------|---------------------------------------------------------------------------|----------------------------------------------------------|
| Pre-Unwind   | 1–10   | Agents retrieve general carry trade context; hold or small trades         | Price near 1.0; similar to RuleLLM                       |
| Early Unwind | 10–20  | Historical crisis documents retrieved; agents may recognize pattern early | Possible earlier cascade onset than RuleLLM              |
| Peak Cascade | 20–35  | Rich historical context (2008 JPY, 2024 unwind) informs sell decisions    | Similar or deeper cascade depending on knowledge quality |
| Recovery     | 35–100 | Historical recovery patterns guide stabilizing agents                     | Recovery speed influenced by historical analogies        |

**Key hypothesis**: If carry crisis documents are relevant and well-retrieved, the cascade onset should be earlier than RuleLLM (agents "remember" historical precedents) and recovery should be faster (stabilizing agents recall recovery dynamics).

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Historical carry events used as knowledge base content → `simulation-bases.md §8`
- RuleLLM base (rules embedded in prompts) → `RuleLLM/explain.md §3`
- RAG architecture → `examples/CarryTradeUnwind/Rag/players.py`
- Fallback string handling → `analysis.py → _RAG_FALLBACK`
- Retrieval success target (≥ 70%) → `analysis-bases.md §6`
