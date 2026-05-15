# BlackMonday1987 Rag — Implementation Explanation

## Overview

| Item                                   | Description                                                                                                                                                                                               |
|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**                            | Rag (RAG-augmented hybrid)                                                                                                                                                                                |
| **Implements**                         | `../simulation-bases.md`                                                                                                                                                                                  |
| **Decision Logic**                     | RuleLLM-identical system prompts augmented with retrieved Black Monday 1987 historical knowledge per round                                                                                                |
| **Key Difference from Other Variants** | `{rag_context}` in user message injects retrieved historical knowledge about portfolio insurance, program trading, and the 1987 crash timeline                                                            |
| **Primary Research Contribution**      | Does knowing about the 1987 Black Monday feedback loop mechanics cause portfolio insurers and program traders to self-reinforce the crash more aggressively, or does historical awareness create caution? |

---

## 1. How Theoretical Design Is Implemented

### All Agents: Theory → Implementation Mapping

| Theoretical Design Element                                             | Implementation                                                                                          |
|------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|
| Rule formulas → sim-bases §4 Rule-Based Behavior                       | System prompts = `RAG_*_SYS` = `RULELLM_*_SYS` aliases (imported from `RuleLLM.prompts`)                |
| Historical 1987 crash knowledge → sim-bases §8 Historical Case Studies | RAG knowledge base sourced from Black Monday event described in sim-bases §8                            |
| `{rag_context}` injection → `RAG_USER_TEMPLATE`                        | User template contains "Relevant Domain Knowledge:\n{rag_context}" between market state and instruction |
| Fallback constant                                                      | `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` in `analysis.py`                      |

Note: `RAG_USER_TEMPLATE` (BlackMonday1987) instructs "Apply your DECISION RULES step-by-step, **incorporating the domain knowledge above**."

---

## 2. Market Mechanism Implementation

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × D(t) + γ × [F − P(t)] + ε(t)
```

Identical to Rule and RuleLLM variants. See Rule `explain.md §2`.

RAG user template note: `{rag_context}` is placed between the market state block and the "Apply DECISION RULES" instruction. Retrieved knowledge modifies LLM reasoning before the formula is applied.

---

## 3. Variant-Specific Features

*(Reference: simulation-bases.md §9 — Rag variant entry)*

**Knowledge base content design**: Inspired by `simulation-bases.md §8 — Historical Case Studies`. The RAG corpus should contain:
- Black Monday timeline (October 19, 1987 intraday events)
- Portfolio insurance mechanics: how selling begets selling
- Program trading feedback loops: Brady Commission findings
- Index arbitrage transmission of futures crash to spot
- ValueInvestor precedents: institutional buying during crash (Buffett)
- Post-crash policy response: Greenspan's liquidity guarantee, circuit breaker introduction

**Retrieval modification hypothesis**: When PortfolioInsurer retrieves knowledge about how portfolio insurance amplified the 1987 crash, it may either:
1. Sell MORE aggressively (historical precedent reinforces mechanical discipline)
2. Become CAUTIOUS (recognizing the systemic harm — unintended consequence awareness)

Both outcomes are scientifically interesting research findings.

**No-retrieval fallback**: Same `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"` as ArchegosCollapse. Agent defaults to pure RuleLLM behavior.

---

## 4. Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║  Market (Rule-identical) → broadcasts {price, fundamental,            ║
║                             deviation, round}                         ║
║                                                                       ║
║  Each RagInvestor.decide():                                           ║
║    ├── retrieve_context(query=f"1987 crash deviation={deviation:.2f}")║
║    │       → VectorStore: 1987 Black Monday / portfolio insurance     ║
║    │       → fallback: "(No relevant knowledge retrieved)"            ║
║    │                                                                  ║
║    ├── RAG_USER_TEMPLATE.format(**state, rag_context=context)         ║
║    │                                                                  ║
║    └── LangChainAPIInference(sys_prompt, user_message)  →  LLM       ║
║          → DECISION RULES + domain knowledge → decision               ║
╚══════════════════════════════════════════════════════════════════════╝
```

---

## 5. Configuration Reference

Key Configuration Parameters (`configs/BlackMonday1987/Rag/players.yml`):

| Parameter            | Config Path                 | Value                                            | Design Justification                              |
|----------------------|-----------------------------|--------------------------------------------------|---------------------------------------------------|
| `price_impact`       | `extras.price_impact`       | 0.002                                            | Identical to Rule/RuleLLM                         |
| `sys_prompt_path`    | `extras.sys_prompt_path`    | `examples.BlackMonday1987.Rag.prompts:RAG_*_SYS` | Aliases to RuleLLM prompts                        |
| `rag.knowledge_base` | `extras.rag.knowledge_base` | Path to 1987 Black Monday vector store           | Historical crash knowledge corpus                 |
| `rag.top_k`          | `extras.rag.top_k`          | 3                                                | 3 most relevant knowledge chunks per round        |
| `llm.temperature`    | `extras.llm.temperature`    | 0.3                                              | Low temperature for rule-following with knowledge |

---

## 6. Running Instructions

```bash
export ARK_API_KEY="your-bytedance-ark-api-key"
python examples/BlackMonday1987/Rag/run_blackmonday1987_rag.py \
    -c configs/BlackMonday1987/Rag/simulation.yml
```

Required environment variables: `ARK_API_KEY`

Expected runtime: ~5–20 minutes for 100 rounds

Output location: `EXPERIMENT/BlackMonday1987/Rag/`

---

## 7. Expected Behavior Patterns

| Phase            | Rounds | Expected Agent Behavior                                                                       | Expected Price Dynamics                                                  |
|------------------|--------|-----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| Pre-Crash        | 1–15   | RAG retrieves context; agents follow rules; historical crash mechanics may be referenced      | Near-identical to RuleLLM                                                |
| Feedback Onset   | 5–20   | PortfolioInsurer may cite historical feedback loop knowledge; ProgramTrader executes per rule | Near-RuleLLM onset; potentially faster if knowledge reinforces urgency   |
| Crash Escalation | 10–25  | Historical amplification knowledge may increase/decrease ProgramTrader sell sizes             | Crash depth near-RuleLLM ± knowledge effect                              |
| Recovery         | 35–100 | ValueInvestor may cite 1987 post-crash recovery to justify larger buys                        | Recovery potentially faster if historical precedent guides ValueInvestor |

---

## 8. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- 1987 Black Monday historical case → `simulation-bases.md §8 — Historical Case Studies`
- RuleLLM prompt structure (reused as RAG_*_SYS) → `BlackMonday1987/RuleLLM/explain.md`
- RAG knowledge effect analysis → `analysis.py → analyze_rag_knowledge_effect()`
- Fallback string → `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`
- Price formula → `simulation-bases.md §3.1`
- Variant comparison → `simulation-bases.md §9 (Rag column)`
