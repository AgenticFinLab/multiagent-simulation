# RumorSpread Rag Variant Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Implements | `../simulation-bases.md` |
| Decision Logic | RuleLLM prompt plus retrieved misinformation/correction knowledge |
| Schema | Special `social_action`; includes recorded `rag_context` |
| Files | `players.py`, `prompts.py`, `run_rumor_rag.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Role | Theory Component | Implementation |
|---|---|---|
| `RagLLMGullibleSpreader` | `simulation-bases.md §4.1` | RuleLLM gullible rules plus retrieved contagion context. |
| `RagLLMDistortingRelayer` | `simulation-bases.md §4.2` | RuleLLM distortion rules plus retrieved serial-transmission context. |
| `RagLLMSkepticalEvaluator` | `simulation-bases.md §4.3` | RuleLLM skepticism rules plus retrieved correction context. |
| `RagLLMFactChecker` | `simulation-bases.md §4.4` | RuleLLM fact-check rules plus retrieved debunking evidence. |
| `RagLLMUninformedBystander` | `simulation-bases.md §4.5` | RuleLLM low-engagement rules plus retrieved context if available. |

## §3 Environment Mechanism

The environment update equations are unchanged from Rule. RAG affects only the
information available to LLM agents before they emit `social_action` payloads.

## §4 Variant Architecture

`RagLLMSocialAgent` initializes or loads a per-agent `KnowledgeStore`, retrieves
top-k context each round, injects it into `RAG_USER_TEMPLATE`, records
`rag_context` in the action payload, validates output with `parse_rumor_response()`,
and raises after repeated parse or provider failures.

## §5 Config Reference

`configs/RumorSpread/Rag/players.yml` defines shared document sources, Hunyuan
embedding settings, local RAG index directories, top-k retrieval, and the ARK
LLM model policy.

## §6 Running Instructions

```bash
python examples/RumorSpread/Rag/run_rumor_rag.py -c configs/RumorSpread/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve RuleLLM action schema while using retrieved evidence to
support skeptical and fact-check reasoning. Retrieval quality is audited through
`rag_stats.json`.

## §8 References

See `simulation-bases.md §2`, `analysis-bases.md §2`, and the document corpus
configured under `configs/RumorSpread/Rag/players.yml`.

## §9 Variant Comparison

Compare Rag against RuleLLM to isolate the effect of retrieved knowledge on
spread/correction intensity, belief persistence, and explanation quality.
