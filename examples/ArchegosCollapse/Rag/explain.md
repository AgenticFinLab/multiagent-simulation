# ArchegosCollapse Rag — Implementation Explanation

## §1 Overview

| Item                                   | Description                                                                                                                                                               |
|----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | Rag (RAG-augmented hybrid)                                                                                                                                                |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                                  |
| **Decision Logic**                     | RuleLLM-identical system prompts augmented with retrieved historical domain knowledge in each user message                                                                |
| **Key Difference from Other Variants** | Each decision round retrieves relevant knowledge from a vector store (historical Archegos case, LTCM precedents) and injects it into the user message via `{rag_context}` |
| **Primary Research Contribution**      | Does access to historical crisis knowledge modify broker and fund behavior vs. the no-RAG baseline? Does recalling LTCM or Archegos precedents change cascade dynamics?   |

---

## §2 Theory → Implementation Mapping

### ConcentratedFund: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.1 — ConcentratedFund)*

| Theory Component                                                   | Implementation                                                                                          |
|--------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| TRS leverage rules → sim-bases §4.N.5.4 Mathematical Model              | System prompt = `RAG_CONCENTRATED_FUND_SYS` = `RULELLM_CONCENTRATED_FUND_SYS` (identical rules/persona) |
| Historical case knowledge → sim-bases §8 (Historical Case Studies) | RAG knowledge base sources from Archegos collapse (March 2021) described in sim-bases §8                |
| `{rag_context}` injection → sim-bases §4 Rag notes                 | `RAG_USER_TEMPLATE` contains `"Relevant Domain Knowledge:\n{rag_context}"` section                      |
| No-retrieval fallback                                              | When retrieval fails: `"(No relevant knowledge retrieved this round.)"` replaces `{rag_context}`        |

### PrimeBroker1: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.2 — PrimeBroker1)*

| Theory Component                                    | Implementation                                                                       |
|-----------------------------------------------------|--------------------------------------------------------------------------------------|
| First-mover rules → sim-bases §4                    | `RAG_PRIME_BROKER1_SYS` = `RULELLM_PRIME_BROKER1_SYS` (deviation < −0.10 → SELL 40%) |
| Historical precedent of broker races → sim-bases §8 | RAG may retrieve LTCM/Archegos prime broker behavior examples                        |
| RAG augmentation modifying urgency                  | Retrieved "first-mover precedents" may reinforce faster/larger liquidation decisions |

### PrimeBroker2: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.3 — PrimeBroker2)*

| Theory Component                                            | Implementation                                                                       |
|-------------------------------------------------------------|--------------------------------------------------------------------------------------|
| Second-mover rules → sim-bases §4                           | `RAG_PRIME_BROKER2_SYS` = `RULELLM_PRIME_BROKER2_SYS` (deviation < −0.15 → SELL 35%) |
| Learning from historical second-mover losses → sim-bases §8 | RAG may retrieve Credit Suisse/Nomura late-liquidation loss examples                 |

### BlockTradeBuyer: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.4 — BlockTradeBuyer)*

| Theory Component                                        | Implementation                                                                            |
|---------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Block trading rules → sim-bases §4                      | `RAG_BLOCK_TRADE_BUYER_SYS` = `RULELLM_BLOCK_TRADE_BUYER_SYS` (deviation < −0.10 → BUY)   |
| Historical block trade recovery examples → sim-bases §8 | RAG may retrieve institutional buyers in Archegos block trades; reinforces buy conviction |

### InformationTrader: Theory → Implementation Mapping
*(Theory defined in simulation-bases.md §4.5 — InformationTrader)*

| Theory Component                                        | Implementation                                                                       |
|---------------------------------------------------------|--------------------------------------------------------------------------------------|
| Detection and front-run rules → sim-bases §4            | `RAG_INFORMATION_TRADER_SYS` = `RULELLM_INFORMATION_TRADER_SYS`                      |
| Historical signal patterns from Archegos → sim-bases §8 | RAG may provide historical context on unusual block flow patterns before the cascade |

---

## §3 Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Implemented in: `players.py` — same `Market` imported from `Rule.players`. Identical to Rule/RuleLLM variants.

RAG user template (`RAG_USER_TEMPLATE`) differs from `RULELLM_USER_TEMPLATE` by adding:
```
Relevant Domain Knowledge:
{rag_context}
```
between the market state and the decision instruction. When RAG retrieval succeeds, `{rag_context}` is filled with retrieved text chunks. When it fails, the fallback string is substituted.

RAG fallback constant (in `analysis.py`):
```python
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"
```

Deviations from simulation-bases.md design: None in market mechanics.

---

## §4 Variant-Specific Features

*(Reference: simulation-bases.md §9 — Rag variant entry)*

**System prompts reuse**: `RAG_*_SYS` constants are aliases for the corresponding `RULELLM_*_SYS` prompts (imported from `RuleLLM.prompts`). The only RAG-specific addition is the knowledge context in the user message.

**Knowledge base content design**: Inspired by `simulation-bases.md §8 — Historical Case Studies`. The RAG corpus should contain:
- Archegos Capital collapse timeline (March 24–29, 2021)
- Prime broker liquidation race: Morgan Stanley first, Credit Suisse/Nomura delayed
- TRS leverage mechanics and margin call dynamics
- Historical parallels: LTCM 1998 (similar prime broker coordination failure)

**Retrieval query strategy**: The query sent to the vector store each round is constructed from the current market state (deviation level, round number) to retrieve contextually relevant historical precedents.

**Fallback behavior**: When the vector store retrieves nothing (low similarity, empty corpus), the `_RAG_FALLBACK` string is injected — the agent then decides based only on rules and state, behaving identically to RuleLLM.

**RAG knowledge effect analysis**: `analysis.py → analyze_rag_knowledge_effect()` classifies each round as retrieval success or fallback, then tests whether decision distributions differ between retrieved vs. non-retrieved rounds.

---

## §5 Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                              ROUND N                                  ║
╠══════════════════════════════════════════════════════════════════════╣
║  Market (Rule-identical) → broadcasts market state                    ║
║                                                                       ║
║  Each RagInvestor.decide():                                           ║
║    ├── retrieve_context(query=f"cascade deviation={deviation:.2f}")   ║
║    │       │                                                          ║
║    │       ├── VectorStore.query(k=3)                                 ║
║    │       │     → top-k chunks from Archegos/LTCM knowledge base    ║
║    │       └── fallback: "(No relevant knowledge retrieved)"          ║
║    │                                                                  ║
║    ├── builds RAG_USER_TEMPLATE.format(**state, rag_context=context)  ║
║    │                                                                  ║
║    └── calls LangChainAPIInference(sys_prompt, user_message)  → LLM  ║
║          → LLM reads rules + historical knowledge                     ║
║          → outputs <decision>{"action","bid_price","quantity",...}</decision>
║                                                                       ║
║  RAG flow: Rules (DECISION RULES) + Knowledge ({rag_context})        ║
║    → combined reasoning → decision near Rule baseline                 ║
║    → but potentially modified by historical precedent recall          ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## §6 Configuration Reference

Key Configuration Parameters (`configs/ArchegosCollapse/Rag/players.yml`):

| Parameter | Config Path | Value | Design Justification |
|---|---|---|---|
| `price_impact` | `extras.price_impact` | 0.03 | Identical to Rule/RuleLLM |
| `mean_reversion` | `extras.mean_reversion` | 0.01 | Identical to Rule/RuleLLM |
| `sys_message` | `extras.llm.sys_message` | `examples.ArchegosCollapse.Rag.prompts:RAG_*_SYS` | Module path for RAG system prompts (aliases to RuleLLM prompts) |
| `user_message` | `extras.llm.user_message` | `examples.ArchegosCollapse.Rag.prompts:RAG_USER_TEMPLATE` | Module path for RAG user template |
| `private_knowledge.rag.top_k` | `extras.private_knowledge.rag.top_k` | 5 | Number of chunks retrieved per round |
| `embed_model` | `extras.private_knowledge.rag.embed_model` | `openai/hunyuan-embedding` | Embedding model for RAG retrieval |
| `temperature` | `extras.llm.generation_config.temperature` | 0.4-0.5 | Low temperature — rules + knowledge |

---

## §7 Running Instructions

```bash
export ARK_API_KEY="your-bytedance-ark-api-key"
python examples/ArchegosCollapse/Rag/run_archegsoscollapse_rag.py \
    -c configs/ArchegosCollapse/Rag/simulation.yml
```

Required environment variables:
- `ARK_API_KEY`: ByteDance Doubao API key

Expected runtime: ~5–20 minutes for 200 rounds (retrieval adds latency per round)

Output location: `EXPERIMENT/ArchegosCollapse/Rag/`

---

## §8 Expected Behavior Patterns

| Phase         | Rounds | Expected Agent Behavior                                                                                                          | Expected Price Dynamics                                                         |
|---------------|--------|----------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| Pre-Cascade   | 1–15   | RAG retrieves contextual knowledge; agents follow rules; historical precedents referenced                                        | Price near 100; behavior near-identical to RuleLLM                              |
| Cascade Onset | 10–20  | Historical Archegos/LTCM context may accelerate broker decisions; rules still binding                                            | Cascade onset similar to RuleLLM; potentially earlier if RAG reinforces urgency |
| Peak Cascade  | 20–35  | PrimeBroker2 recalled Credit Suisse delays → may act more decisively; BlockTradeBuyer more aggressive with historical conviction | Cascade depth near RuleLLM; slight modification from knowledge                  |
| Recovery      | 35–100 | Historical recovery patterns may guide BlockTradeBuyer and InformationTrader cover decisions                                     | Recovery speed may differ from RuleLLM if RAG context is strong                 |

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Historical Archegos case used as RAG knowledge source → `simulation-bases.md §8 — Historical Case Studies`
- RuleLLM system prompt structure (reused as RAG_*_SYS) → `ArchegosCollapse/RuleLLM/explain.md`
- RAG knowledge effect analysis → `analysis.py → analyze_rag_knowledge_effect()`
- RAG fallback string constant → `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`
- Price formula → `simulation-bases.md §3.1`
- Variant comparison → `simulation-bases.md §9 (Rag column)`
