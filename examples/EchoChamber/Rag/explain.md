# EchoChamber Rag Variant Explanation

## §1 Overview

The Rag variant augments RuleLLM-style social-action decisions with retrieved
social-science context. It preserves the special `social_action` schema and does
not use financial order fields.

## §2 Theory -> Implementation Mapping

| Social Role | Theory Component | Implementation Trace |
|---|---|---|
| `RagLLMIdeologue` | `simulation-bases.md §4.1` | `players.py:RagLLMIdeologue`; `prompts.py:RAG_IDEOLOGUE_SYS`; shared `RagLLMSocialAgent.decide`. |
| `RagLLMConformist` | `simulation-bases.md §4.2` | `players.py:RagLLMConformist`; `prompts.py:RAG_CONFORMIST_SYS`; shared `RagLLMSocialAgent.decide`. |
| `RagLLMCriticalThinker` | `simulation-bases.md §4.3` | `players.py:RagLLMCriticalThinker`; `prompts.py:RAG_CRITICAL_SYS`; shared `RagLLMSocialAgent.decide`. |
| `RagLLMBridgeBuilder` | `simulation-bases.md §4.4` | `players.py:RagLLMBridgeBuilder`; `prompts.py:RAG_BRIDGE_SYS`; shared `RagLLMSocialAgent.decide`. |
| `RagLLMPassiveFollower` | `simulation-bases.md §4.5` | `players.py:RagLLMPassiveFollower`; `prompts.py:RAG_PASSIVE_SYS`; shared `RagLLMSocialAgent.decide`. |

## §3 Environment Mechanism

The environment is the same opinion-dynamics coordinator as Rule. RAG affects
only model reasoning, not the environment update equation.

## §4 Variant Architecture

`RagLLMSocialAgent._initialize_rag` initializes or loads a per-agent index;
`_build_prompt` retrieves context; `_parse_echo_chamber_response` enforces the
canonical tagged JSON contract; and `decide` records `rag_context` and emits
`social_action`. `OpinionEnvironment` is reused from the Rule variant so the
state transition remains identical across variants.

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
