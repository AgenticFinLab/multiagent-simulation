# ConfirmationBias Rag Variant — Design Specification

## 1. Overview

| Item            | Detail                                                                                                      |
|-----------------|-------------------------------------------------------------------------------------------------------------|
| **Phenomenon**  | Confirmation bias dynamics modulated by retrieved knowledge about cognitive biases                          |
| **Variant**     | Rag — RAG-augmented LLM agents; knowledge retrieved from KnowledgeStore per round                           |
| **Rounds**      | 200 (configurable)                                                                                          |
| **Market**      | Identical deterministic Rule-based Market agent                                                             |
| **Key Feature** | KnowledgeStore retrieves bias-relevant documents; agents may overcome their own bias with retrieved insight |
| **Target**      | Retrieval success rate ≥ 70% per agent                                                                      |

---

## 2. Theory → Implementation Mapping

| Theoretical Concept            | Agent / Mechanism                                             | Code Location                               |
|--------------------------------|---------------------------------------------------------------|---------------------------------------------|
| Belief anchoring + knowledge   | `RagBeliefAnchor` — retrieves docs on confirmation bias       | `Rag/prompts.py: RAG_BELIEF_ANCHOR_SYS`     |
| Selective scanning + knowledge | `RagSelectiveScanner` — retrieves docs on selective attention | `Rag/prompts.py: RAG_SELECTIVE_SCANNER_SYS` |
| Rational analysis + knowledge  | `RagBalancedAnalyst` — retrieves docs on rational updating    | `Rag/prompts.py: RAG_BALANCED_ANALYST_SYS`  |
| Contrarian + knowledge         | `RagContrarianTrader` — retrieves docs on market correction   | `Rag/prompts.py: RAG_CONTRARIAN_TRADER_SYS` |
| Noise + knowledge              | `RagNoiseTrader` — retrieves docs, minimal effect expected    | `Rag/prompts.py: RAG_NOISE_TRADER_SYS`      |
| Price dynamics                 | `Market` agent (Rule-based, unchanged)                        | `Rule/players.py: Market`                   |

---

## 3. Market Mechanism

Identical to Rule variant. Market broadcasts per round:

```python
{"price": float, "fundamental": float, "deviation": float, "round": int}
```

---

## 4. Variant-Specific Features

### 4.1 RAG Pipeline

```
For each agent each round:
    1. Build KnowledgeQuery from current market state
    2. Query KnowledgeStore → retrieve top-k documents
    3. If retrieved: rag_context = document text
    4. If not retrieved: rag_context = _RAG_FALLBACK string
    5. Inject rag_context into LLM user prompt
    6. LLM decision includes retrieved context
```

### 4.2 Fallback Constant

```python
_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"
```

When `rag_context == _RAG_FALLBACK`: agent makes pure LLM decision (no knowledge).
High fallback rate → KnowledgeStore needs more relevant documents.

### 4.3 Hypothesis: Knowledge Reduces Bias

Hypothesis: If `BalancedAnalyst` and `ContrarianTrader` retrieve documents
about confirmation bias mechanisms, they may more effectively counter the
BeliefAnchor's biased buying.

Observable: `correction_ratio` (Rag) > `correction_ratio` (LLM)
if knowledge retrieval is effective.

### 4.4 Counter-Hypothesis: Bias Agents Override Knowledge

`BeliefAnchor` persona is strongly biased. Even with retrieved documents
acknowledging confirmation bias, it may ignore them ("I know about the bias,
but this time the evidence really is confirming"). Track BeliefAnchor's
`rag_context` + `action` correlation across rounds.

---

## 5. Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                  Market (Rule)                        │
└──────────────────────┬───────────────────────────────┘
                       │
   ┌────────────┬───────┼────────────┬─────────────┐
   │            │       │            │             │
┌──▼───────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐
│RagBelief │ │RagSelect│ │RagBalanc│ │RagContr │ │RagNoise │
│Anchor    │ │Scanner  │ │Analyst  │ │Trader   │ │Trader   │
└──────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
      │             │         │           │            │
      └─────────────┴─────────┴───────────┴────────────┘
                             │
                    ┌────────▼────────┐
                    │  KnowledgeStore  │
                    │  (per-agent     │
                    │   query)        │
                    └────────┬────────┘
                             │ rag_context or _RAG_FALLBACK
                    ┌────────▼────────┐
                    │LangChain API    │
                    │Inference        │
                    └─────────────────┘
```

---

## 6. Configuration Reference

Config: `configs/ConfirmationBias/Rag/simulation.yml`

| Parameter         | Value                                     | Description                   |
|-------------------|-------------------------------------------|-------------------------------|
| `llm.model`       | `gpt-4o-mini` (default)                   | LLM model name                |
| `llm.temperature` | 0.3                                       | Decision randomness           |
| `llm.max_tokens`  | 512                                       | Max response length           |
| `knowledge_path`  | `configs/ConfirmationBias/Rag/knowledge/` | Document directory            |
| `top_k`           | 2                                         | Documents retrieved per query |

---

## 7. Running Instructions

```bash
# Ensure knowledge documents exist in configs/ConfirmationBias/Rag/knowledge/
python examples/ConfirmationBias/Rag/run_confirmationbias_rag.py \
    -c configs/ConfirmationBias/Rag/simulation.yml

# Analyze results
python examples/ConfirmationBias/Rag/analysis.py \
    -c configs/ConfirmationBias/Rag/simulation.yml
```

---

## 8. Expected Behavior

- `retrieval_success_rate` ≥ 70% requires KnowledgeStore populated with
  documents about confirmation bias, cognitive biases, and market behavior
- `correction_ratio` (Rag) > `correction_ratio` (LLM) if stabilizing agents
  benefit from retrieved bias-correction knowledge
- `bias_amplitude_pct` may be lower than LLM if BeliefAnchor is moderated
  by retrieved self-awareness about confirmation bias
- BeliefAnchor retrieval effect: ambiguous (may strengthen or reduce bias)

---

## 9. References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Confirmation bias theory → `../simulation-bases.md §2, §4 — BeliefAnchor, SelectiveScanner`
- Retrieval-augmented generation → Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS*.
