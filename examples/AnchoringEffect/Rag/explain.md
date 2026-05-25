# AnchoringEffect Rag — Implementation Explanation

## §1 Overview

| Item                               | Description                                                                                                                                                            |
|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Variant                            | Rag                                                                                                                                                                    |
| Implements                         | `../simulation-bases.md`                                                                                                                                               |
| Decision Logic                     | RAG-augmented LLM: RuleLLM dual-section prompts extended with per-agent knowledge retrieval injected as `{rag_context}`                                                |
| Key Difference from Other Variants | Each agent builds a personal `KnowledgeStore` from domain documents; at every decision round, top-k retrieved chunks are injected into the user prompt before LLM call |
| Primary Research Contribution      | Tests whether access to retrieved anchoring/behavioral finance literature changes decision quality and phenomenon intensity compared to RuleLLM baseline               |

---

## §2 How Theoretical Design Is Implemented

Theory for each investor type is defined in `simulation-bases.md §4`. Below: how each theory is encoded in the Rag variant via RAG-augmented dual-section prompts.

### AnchoredTrader: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4.1 — AnchoredTrader)

| Theoretical Design Element                            | Implementation                                                                                                                      |
|-------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.1          | System prompt `== PERSONA ==` section (identical to RuleLLM); `KnowledgeStore` seeded with Tversky & Kahneman (1974) paper excerpts |
| Rule-based behavior → sim-bases §4.1     | System prompt `== DECISION RULES ==` section (identical to RuleLLM): `perceived_target = anchor + (F − anchor) × 0.3`               |
| RAG knowledge source → sim-bases §8                   | Historical case: analyst forecast anchoring; resolved from `extras.private_knowledge` and shared `knowledge` resources                         |
| `{rag_context}` injection                             | `_build_prompt()` calls `_query_rag()` with current price/deviation → top-k chunks → appended to user message                       |
| Parameter values → simulation-bases.md §6             | Identical to RuleLLM; plus `private_knowledge.rag.top_k`, `private_knowledge.rag.embed_model`, and resolved local index directories from `players.yml`                                 |
| Market impact → simulation-bases.md §4.1 | Same destabilizing role; RAG context may reinforce or counteract anchoring depending on retrieved documents                         |

### HistoricalAnchor: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4.2 — HistoricalAnchor)

| Theoretical Design Element                          | Implementation                                                                                                                        |
|-----------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.2        | System prompt `== PERSONA ==`; `KnowledgeStore` seeded with Northcraft & Neale (1987) excerpts and real estate appraisal case studies |
| Rule-based behavior → sim-bases §4.2 | System prompt `== DECISION RULES ==`: `perceived_dev = (price − hist_avg) / hist_avg × (1 − 0.5)`                                     |
| RAG knowledge source → sim-bases §8                 | Historical case: real estate appraisal anchoring; HistoricalAnchor-specific document collection                                       |
| Parameter values → simulation-bases.md §6           | `anchor_weight` = 0.5; `lookback` = 60; RAG configuration per agent in `players.yml`                                                  |

### RationalUpdater: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4.3 — RationalUpdater)

| Theoretical Design Element                         | Implementation                                                                                                     |
|----------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.4       | System prompt `== PERSONA ==`; `KnowledgeStore` seeded with rational expectations and market efficiency literature |
| Rule-based behavior → sim-bases §4.3 | System prompt `== DECISION RULES ==`: deviation-based trading with 2% threshold                                    |
| RAG knowledge source                               | Academic papers on rational arbitrage and price discovery; helps reinforce rational updating behavior              |
| Parameter values → simulation-bases.md §6          | Threshold = 0.02; base size = 25 units                                                                             |

### MomentumTrader: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4.4 — MomentumTrader)

| Theoretical Design Element                        | Implementation                                                                                                              |
|---------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.5      | System prompt `== PERSONA ==`; `KnowledgeStore` seeded with momentum strategy literature (Jegadeesh & Titman 1993 excerpts) |
| Rule-based behavior → sim-bases §4.4 | System prompt `== DECISION RULES ==`: `return_pct`-based entry with 2% threshold                                            |
| RAG knowledge source                              | Momentum trading case studies; provides context on trend-following in anchoring environments                                |
| Parameter values → simulation-bases.md §6         | `entry_threshold` = 0.02                                                                                                    |

### NoiseTrader: Theory → Implementation Mapping
(Theory defined in simulation-bases.md §4.5 — NoiseTrader)

| Theoretical Design Element                     | Implementation                                                                                        |
|------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Theoretical basis → simulation-bases.md §2.6   | System prompt `== PERSONA ==`; `KnowledgeStore` seeded with noise trader risk literature (Black 1986) |
| Rule-based behavior → sim-bases §4.5 | System prompt `== DECISION RULES ==`: random trading with 5% probability                              |
| RAG knowledge source                           | Noise trading examples; impact of uninformed order flow on price efficiency                           |
| Parameter values → simulation-bases.md §6      | `trade_probability` = 0.05; `min_order` = 100; `max_order` = 500                                      |

---

## §3 Market Mechanism Implementation

Formula source: `simulation-bases.md §3.1`

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `examples.AnchoringEffect.Rule.players.Market` (imported by `Rag/players.py`)

Code translation (identical to Rule and RuleLLM variants):
```
sim-bases variable  →  Python variable     →  config path
λ (price_impact)    →  price_impact        →  extras["price_impact"]       = 0.01
γ (mean_reversion)  →  mean_reversion      →  extras["mean_reversion"]     = 0.01
F (fundamental)     →  self._fundamental   →  extras["fundamental_value"]  = 100.0
ε (noise)           →  noise               →  random.gauss(0, noise_std)   σ = extras["noise_std"]
D(t) (net demand)   →  net_demand          →  sum(buy_qty) − sum(sell_qty)
```

Additional mechanisms: `simulation-bases.md §3.2`
- Price floor: `new_price = max(new_price, 0.01)`
- `Rag/players.py` imports `Market` from `examples.AnchoringEffect.Rule.players` — zero code duplication

Deviations from simulation-bases.md design: None — market implementation is identical to Rule/RuleLLM.

---

## §4 Variant-Specific Features

What is unique to Rag versus other variants — motivated by `simulation-bases.md §8` (Historical Case Studies) and `simulation-bases.md §9`:

**Per-Agent KnowledgeStore** (cite sim-bases §8):
- Each agent class initializes its own `KnowledgeStore` via `_initialize_rag()` in `perceive()` on first round.
- Knowledge base content is agent-type-specific:
  - AnchoredTrader: Tversky & Kahneman (1974), Campbell & Sharpe (2009), analyst forecast anchoring case studies
  - HistoricalAnchor: Northcraft & Neale (1987), real estate appraisal anchoring cases
  - RationalUpdater: rational expectations literature, market efficiency theory
  - MomentumTrader: Jegadeesh & Titman (1993), momentum strategy papers
  - NoiseTrader: Black (1986), noise trader risk literature
- Index persistence: built on first run, loaded from `private_knowledge.rag.local_index_dir` on subsequent runs.

**`{rag_context}` Injection in User Prompt**:
Every round, `_build_prompt()` calls `_query_rag(query_text)` where `query_text` is constructed from current market state. Retrieved chunks are injected as:
```
Retrieved Knowledge:
{rag_context}
```
If no documents retrieved: `"(No relevant knowledge retrieved this round.)"` is injected instead.

**RAG Configuration in `players.yml`**:
Each agent has a `rag:` block:
```yaml
rag:
  docs_dir: path/to/agent_specific_docs
  private_knowledge.rag.local_index_dir: EXPERIMENT/AnchoringEffect/Rag/{agent_type}/index
  embed_model: openai/hunyuan-embedding
  top_k: 5
```

**Query Strategy**:
- Query text constructed as: `f"price deviation {deviation:.1%} from fundamental, round {round_num}"`
- Retrieves chunks most relevant to the current market state
- Retrieved context may contain historical examples of anchoring behavior, reinforcing or challenging the agent's current inclination

---

## §5 Architecture Diagram

```
Rag Simulation Flow
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
First Run Only:
  Each agent: _initialize_rag()
  ┌──────────────────────────────────────────────────────────┐
  │  KnowledgeLoader.load(docs_dir / url_csv)                │
  │  → KnowledgeStore.build_index()                          │
  │  → persist to private_knowledge.rag.local_index_dir/                           │
  └──────────────────────────────────────────────────────────┘

Round N:

  Market (Rule-based, imported from Rule variant)
  ┌──────────────────────────────────────────────────┐
  │  broadcast {price, fundamental, deviation, ...}  │
  └──────────────────────┬───────────────────────────┘
                         │
                         ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │  RAG Investor (e.g., AnchoredTrader)                             │
  │                                                                  │
  │  perceive(): store market_data                                   │
  │                                                                  │
  │  decide():                                                       │
  │    query_text = f"deviation {dev:.1%} round {n}"                 │
  │    ┌─────────────────────────────────────────────┐              │
  │    │  KnowledgeStore.query(query_text, top_k=5)  │              │
  │    │  → rag_context (retrieved chunks)           │              │
  │    └──────────────────────┬──────────────────────┘              │
  │                           │                                      │
  │    user_msg = RULELLM_USER_TEMPLATE.format(                      │
  │        ...market_data..., rag_context=rag_context                │
  │    )                                                             │
  │    ┌──────────────────────────────────────────────┐             │
  │    │  LLM API (LangChainAPIInference)             │             │
  │    │  system: PERSONA + DECISION RULES            │             │
  │    │  user:   market_state + rag_context          │             │
  │    │  output: <analysis>...</analysis>            │             │
  │    │          <decision>JSON</decision>           │             │
  │    └──────────────────────────────────────────────┘             │
  │    parse → action, bid_price, quantity, reasoning               │
  │  act(): execute trade                                            │
  └────────────────────────────────────────────── order → Market    │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## §6 Configuration Reference

Key Configuration Parameters (`configs/AnchoringEffect/Rag/players.yml`):

| Parameter             | Config Path                  | Value                             | Design Justification                                |
|-----------------------|------------------------------|-----------------------------------|-----------------------------------------------------|
| `initial_price`       | `extras.initial_price`       | 105.0                             | Seeds 5% initial mispricing — sim-bases §3.1        |
| `fundamental_value`   | `extras.fundamental_value`   | 100.0                             | Rational benchmark — sim-bases §3.1                 |
| `price_impact`        | `extras.price_impact`        | 0.01                              | Low λ sustains mispricings — sim-bases §3.1         |
| `mean_reversion`      | `extras.mean_reversion`      | 0.01                              | Low γ — sim-bases §2.3                              |
| `adjustment_factor`   | `extras.adjustment_factor`   | 0.3                               | AnchoredTrader α — matches DECISION RULES           |
| `anchor_weight`       | `extras.anchor_weight`       | 0.5                               | HistoricalAnchor dampening — matches DECISION RULES |
| `private_knowledge.rag.top_k`           | `extras.private_knowledge.rag.top_k`           | 5                                 | Number of retrieved chunks per round                |
| `private_knowledge.rag.embed_model`     | `extras.private_knowledge.rag.embed_model`     | openai/hunyuan-embedding                  | Embedding model for knowledge index                 |
| `private_knowledge.rag.local_index_dir` | `extras.private_knowledge.rag.local_index_dir` | `EXPERIMENT/.../Rag/{type}/index` | Where to persist/load knowledge index               |
| `lm_name`             | `extras.llm.lm_name`         | ark/doubao-seed-2-0-mini-260428                    | LLM model for RAG agents                            |

---

## §7 Running Instructions

```
Execution:
  python examples/AnchoringEffect/Rag/run_anchoringeffect_rag.py \
      -c configs/AnchoringEffect/Rag/simulation.yml

Required environment variables:
  ARK_API_KEY: ByteDance Doubao API key — set in project root .env file

First run: RAG indices are built from docs and persisted (~2-5 min per agent type)
Subsequent runs: indices loaded from private_knowledge.rag.local_index_dir (~1-2 min per agent type)

Expected runtime: API-latency dependent for the 200-round full experiment (RAG retrieval + 9 LLM investor calls per round)
Output location:  EXPERIMENT/AnchoringEffect/Rag/
```

---

## §8 Expected Behavior Patterns

| Phase                         | Rounds      | Expected Agent Behavior                                                                                                                                     | Expected Price Dynamics                                                          |
|-------------------------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------|
| Index Build                   | Pre-round 1 | Each agent builds/loads personal KnowledgeStore; index verification logged                                                                                  | No price movement; setup phase                                                   |
| Early Anchoring               | 1–15        | RAG context retrieves anchoring bias examples; reinforces anchored decision-making; AnchoredTrader anchors to first price                                   | Price near 105; anchoring-reinforced demand creates mild mispricing              |
| Knowledge-Modulated Decisions | 16–60       | Retrieved context may include historical examples of anchoring overcoming vs. persisting; rational-case retrieval by RationalUpdater accelerates correction | Price path may diverge from RuleLLM depending on knowledge quality and relevance |
| Resolution                    | 61–100      | RationalUpdater consistently corrects with fundamental-anchored knowledge support; AnchoredTrader may persist longer if knowledge reinforces anchoring      | Convergence toward fundamental; pace varies by knowledge effect                  |

---

## §9 References

No new theories are introduced in this variant. All theoretical foundations are defined in `simulation-bases.md §2`.

Cross-references:
- Anchoring and Insufficient Adjustment → `simulation-bases.md §2.1`, §4 — AnchoredTrader
- Expert Anchoring (knowledge base source) → `simulation-bases.md §2.2`, §8 — Historical Case Study: Real Estate Appraisal
- Consensus Forecast Anchoring (knowledge base source) → `simulation-bases.md §2.3`, §8 — Historical Case Study: Analyst Forecast Anchoring
- Rational Expectations → `simulation-bases.md §2.4`, §4 — RationalUpdater
- RAG pipeline design → `create-example-skill.md` — Rag variant section
- `{rag_context}` injection requirement (fallback string) → `create-example-skill.md` — Rag Core construction rule
- Historical case studies used as knowledge sources → `simulation-bases.md §8`
