# CreditCycle Rag Variant — explain.md

## §1 Overview

The Rag variant augments LLM inference with retrieved knowledge from a per-agent private knowledge store. Before each decision, the agent queries its knowledge store with the current market context and receives relevant passages that are injected into the prompt as `{rag_context}`. This allows agents to draw on credit-cycle theory, historical cases, and Minsky literature during reasoning.

| Aspect             | Detail                                                 |
|--------------------|--------------------------------------------------------|
| Variant            | Rag                                                    |
| Simulation         | CreditCycle                                            |
| Decision Mechanism | LLM persona + RAG-retrieved context                    |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                        |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`           |
| RAG Architecture   | Per-agent `KnowledgeStore`; per-round `KnowledgeQuery` |
| Prompt Location    | `CreditCycle/Rag/prompts.py`                           |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMProCyclicalLender (simulation-bases.md §4.1)

| Theory Component                            | Rag Implementation                                        |
|---------------------------------------------|-----------------------------------------------------------|
| Pro-cyclical leverage (Adrian & Shin, 2010) | Persona + retrieved passages on leverage cycles           |
| RAG query                                   | `KnowledgeQuery("pro-cyclical lending credit expansion")` |
| Context injection                           | `{rag_context}` slot in user prompt                       |

### §2.2 RagLLMMinskyBorrower (simulation-bases.md §4.2)

| Theory Component                 | Rag Implementation                                            |
|----------------------------------|---------------------------------------------------------------|
| Minsky trajectory (Minsky, 1986) | RAG may retrieve Minsky's hedge/speculative/Ponzi taxonomy    |
| RAG query                        | `KnowledgeQuery("Minsky fragility leverage accumulation")`    |
| Unique benefit                   | RAG-retrieved Minsky theory may improve fragility recognition |

### §2.3 RagLLMCounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component         | Rag Implementation                                                |
|--------------------------|-------------------------------------------------------------------|
| Counter-cyclical buffers | RAG retrieves Basel CCyB rationale and historical cases           |
| RAG query                | `KnowledgeQuery("counter-cyclical capital buffer credit crisis")` |

### §2.4 RagLLMValueInvestor (simulation-bases.md §4.4)

| Theory Component | Rag Implementation                                              |
|------------------|-----------------------------------------------------------------|
| Margin of safety | RAG retrieves Graham-style distressed credit analysis           |
| RAG query        | `KnowledgeQuery("value investing credit discount fundamental")` |

### §2.5 RagLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | Rag Implementation                            |
|------------------|-----------------------------------------------|
| Random trading   | RAG context minimally used; persona dominates |

## §3 RAG Architecture

```
RagLLMInvestor._initialize_rag():
    KnowledgeStore(agent_id) → loads agent-specific documents
    shared fallback store → general credit-cycle knowledge

RagLLMInvestor.decide():
    query = KnowledgeQuery(market_context_summary)
    rag_context = KnowledgeStore.retrieve(query, top_k=3)
    user_prompt = template.format(..., rag_context=rag_context)
    response = LangChainAPIInference.infer(system_prompt, user_prompt)
```

Per-agent private index ensures persona-relevant passages are prioritized.

## §4 Variant-Specific Features

- **Minsky theory retrieval**: RagLLMMinskyBorrower uniquely benefits from retrieved Minsky passages — may exhibit more accurate hedge→Ponzi trajectory.
- **Historical case grounding**: Counter-cyclical decisions grounded in retrieved GFC / Basel CCyB case studies.
- **Dynamic context**: Different market conditions trigger different RAG queries; boom vs. bust phases retrieve different passages.
- **`{rag_context}` slot**: Injected between system context and decision request in user prompt.

## §5 Config Reference

Same as Rule variant; adds `rag_store_path`, `top_k_retrieval`, LLM model config.

## §6 Running Instructions

```bash
cd multiagent-simulation
python -m examples.CreditCycle.Rag.run
```

## §7 Expected Behavior

- MinskyBorrower: Earlier fragility recognition from Minsky theory retrieval
- CounterCyclicalLender: More precise crisis timing from historical case retrieval
- Overall: LAI and CCS may be more moderate than LLM variant (RAG grounds decisions)

## §8 References

See `simulation-bases.md §2` for full DOI citations.  
RAG architecture: `masim` KnowledgeStore / KnowledgeQuery / ResourceManager.
