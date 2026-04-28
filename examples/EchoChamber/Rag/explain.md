# EchoChamber Rag Variant — explain.md

## §1 Overview

The Rag variant implements EchoChamber with RAG-augmented LLM agents. Each agent retrieves relevant academic literature about echo chambers, polarization, and group dynamics before making opinion decisions. This grounds LLM reasoning in empirical research rather than persona alone, potentially producing more moderating behavior through literature-informed awareness.

| Aspect             | Detail                                                                                                                                                                           |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Variant            | Rag                                                                                                                                                                              |
| Simulation         | EchoChamber                                                                                                                                                                      |
| Decision Mechanism | RAG context retrieval + LLM reasoning; outputs `{action_type, intensity, reasoning, analysis}`                                                                                   |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                                                                                                                  |
| Market Broadcast   | `polarization`, `prev_polarization`, `mean_opinion`, `cluster_separation`, `cross_cutting_exposure`, `num_polarizers`, `num_depolarizers`, `net_polarization_intensity`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 RagLLMIdeologue (simulation-bases.md §4.1)

| Theory Component                        | Implementation                                                                      |
|-----------------------------------------|-------------------------------------------------------------------------------------|
| In-group amplification (Sunstein, 2001) | RAG retrieves echo chamber literature; may reinforce or moderate ideological stance |
| Out-group rejection                     | LLM reasons with RAG context about group dynamics; rejection may be nuanced         |

### §2.2 RagLLMConformist (simulation-bases.md §4.2)

| Theory Component               | Implementation                                                        |
|--------------------------------|-----------------------------------------------------------------------|
| Social conformity (Asch, 1951) | RAG retrieves conformity research; LLM applies to current group state |

### §2.3 RagLLMCriticalThinker (simulation-bases.md §4.3)

| Theory Component                      | Implementation                                                                       |
|---------------------------------------|--------------------------------------------------------------------------------------|
| Persuasive arguments (Isenberg, 1986) | RAG retrieves counter-polarization literature; CriticalThinker may be more effective |

### §2.4 RagLLMBridgeBuilder (simulation-bases.md §4.4)

| Theory Component                        | Implementation                                                                        |
|-----------------------------------------|---------------------------------------------------------------------------------------|
| Deliberative democracy (Sunstein, 2001) | RAG retrieves bridge-building research; may produce stronger depolarization reasoning |

### §2.5 RagLLMPassiveFollower (simulation-bases.md §4.5)

| Theory Component                            | Implementation                                                                 |
|---------------------------------------------|--------------------------------------------------------------------------------|
| Mass communication drift (Lazarsfeld, 1954) | RAG context about passive audiences; reasoning reflects low-agency perspective |

## §3 Market Mechanism

Same as Rule variant. `OpinionEnvironment` is re-exported from `examples.EchoChamber.Rule.players`:

```
P(t+1) = P(t) + alpha * NetPolarization(t) + beta * CentripetalForce(t) + epsilon(t)
```

## §4 Variant Architecture

| Component      | Detail                                                                                         |
|----------------|------------------------------------------------------------------------------------------------|
| Base class     | `RagLLMSocialAgent(GeneralPlayer)`                                                             |
| Inference      | `LangChainAPIInference(lm_name=..., generation_config=...)`                                    |
| Context        | `env_data` + RAG-retrieved academic context via `_get_rag_context()`                           |
| RAG injection  | `{rag_context}` placeholder in `RAG_USER_TEMPLATE`; filled via `.format(rag_context=...)`      |
| Output parsing | `parse_llm_response_with_thinking(response)` → `{action_type, intensity, reasoning, analysis}` |
| Retry logic    | Up to 3 attempts; on failure → neutral action with `reasoning="LLM failed: stayed neutral"`    |
| Ray support    | `__getstate__`/`__setstate__` in `RagLLMSocialAgent` excludes `llm_client` from pickle         |
| KnowledgeStore | `build()` auto-persists; shared RAG index dirs optionally configured                           |

## §5 Config Reference

Config file: `configs/EchoChamber/Rag/simulation.yml`

Key RAG extras per agent:
- `private_knowledge.rag.docs_dir`: Source documents directory for RAG index
- `private_knowledge.rag.embed_type`: Embedding model type (e.g., `litellm`)
- `private_knowledge.rag.embed_api_key`: API key for embedding model
- `private_knowledge.rag.top_k`: Number of retrieved documents per query
- `private_knowledge.rag.chunk_size`, `chunk_overlap`: RAG index build parameters
- `llm.lm_name`, `llm.generation_config`: LLM inference settings
- `llm.sys_message`: System prompt (e.g., `examples.EchoChamber.Rag.prompts:RAG_IDEOLOGUE_SYS`)
- `llm.user_message`: User template (e.g., `examples.EchoChamber.Rag.prompts:LLM_USER_TEMPLATE`)

## §6 Running Instructions

```bash
export ARK_API_KEY=<your_key>
python examples/EchoChamber/Rag/run_echo_chamber_rag.py -c configs/EchoChamber/Rag/simulation.yml
```

## §7 Output Artifacts

Same as LLM variant. RAG context strings are included in reasoning when RAG retrieval succeeds.

## §8 Known Limitations

- RAG retrieval may return irrelevant passages if document sources lack on-topic content
- First-round RAG index build adds latency; shared indexes reduce this on subsequent runs
- Opinion update formulas are hardcoded — RAG context only influences `action_type` and `intensity`
- Embedding cost adds to total API expenditure per run

## §9 References

See `simulation-bases.md §4` for agent parameter sources and theoretical derivations.
See `analysis-bases.md §2` for metric definitions and Python function signatures.
