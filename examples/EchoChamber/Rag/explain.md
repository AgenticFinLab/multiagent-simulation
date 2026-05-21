# EchoChamber Rag Variant Explanation

## §1 Overview

The Rag variant augments RuleLLM-style social-action decisions with retrieved
social-science context. It preserves the special `social_action` schema and does
not use financial order fields.

## §2 Theory -> Implementation Mapping

| Social Role | Theory Component | Implementation |
|---|---|---|
| `RagLLMIdeologue` | `simulation-bases.md §4.1` | RuleLLM prompt plus retrieved echo-chamber context. |
| `RagLLMConformist` | `simulation-bases.md §4.2` | RuleLLM prompt plus retrieved conformity/herding context. |
| `RagLLMCriticalThinker` | `simulation-bases.md §4.3` | RuleLLM prompt plus retrieved evidence-evaluation context. |
| `RagLLMBridgeBuilder` | `simulation-bases.md §4.4` | RuleLLM prompt plus retrieved cross-cutting exposure context. |
| `RagLLMPassiveFollower` | `simulation-bases.md §4.5` | RuleLLM prompt plus retrieved low-engagement communication context. |

## §3 Environment Mechanism

The environment is the same opinion-dynamics coordinator as Rule. RAG affects
only model reasoning, not the environment update equation.

## §4 Variant Architecture

`RagLLMSocialAgent` initializes or loads a per-agent RAG index, retrieves
context each round, records `rag_context`, validates `action_type`, `intensity`,
and `reasoning`, and emits `social_action`.

## §5 Config Reference

`configs/EchoChamber/Rag/players.yml` defines the RAG knowledge source, Hunyuan
embedding configuration, model settings, and prompt paths.

## §6 Running Instructions

```bash
python examples/EchoChamber/Rag/run_echochamber_rag.py -c configs/EchoChamber/Rag/simulation.yml
```

## §7 Expected Behavior

Rag should preserve RuleLLM-style role behavior while using retrieved context to
support reasoning. Retrieval coverage is audited through `rag_stats.json`.

## §8 References

See `simulation-bases.md §2`, `analysis-bases.md §2`, and the retrieved
document corpus configured under `configs/EchoChamber/Rag/players.yml`.

## §9 Variant Comparison

Compare Rag against RuleLLM to isolate the effect of retrieved context on
action selection and explanation quality.
