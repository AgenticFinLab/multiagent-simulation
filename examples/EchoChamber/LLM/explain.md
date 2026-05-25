# EchoChamber LLM Variant Explanation

## §1 Overview

The LLM variant keeps the Rule environment but delegates social action selection
to persona prompts. It remains a special-schema scenario using `social_action`
fields, not trading orders.

## §2 Theory -> Implementation Mapping

| Social Role | Theory Component | Implementation |
|---|---|---|
| `LLMIdeologue` | `simulation-bases.md §4.1` | Prompt encodes strong-conviction in-group amplification; parser enforces `action_type/intensity/reasoning`. |
| `LLMConformist` | `simulation-bases.md §4.2` | Prompt encodes conformity and group-alignment psychology. |
| `LLMCriticalThinker` | `simulation-bases.md §4.3` | Prompt encodes evidence evaluation and resistance to groupthink. |
| `LLMBridgeBuilder` | `simulation-bases.md §4.4` | Prompt encodes cross-group engagement and depolarization. |
| `LLMPassiveBystander` | `simulation-bases.md §4.5` | Prompt encodes low-engagement participation. |

## §3 Environment Mechanism

The environment is imported from the same opinion-dynamics design as Rule. LLM
agents affect it only through valid `social_action` payloads.

## §4 Variant Architecture

`LLMSocialAgent` loads configured prompts, calls the API model, extracts
`<analysis>` and `<decision>` sections, validates the special schema, updates
personal opinion, and emits `social_action`.

## §5 Config Reference

`configs/EchoChamber/LLM/players.yml` binds model settings and prompt paths for
each role. `simulation.yml` and `topology.yml` mirror the Rule message flow.

## §6 Running Instructions

```bash
python examples/EchoChamber/LLM/run_echo_chamber_llm.py -c configs/EchoChamber/LLM/simulation.yml
```

## §7 Expected Behavior

LLM agents should preserve role semantics while adding stochastic social
reasoning. Parser failures are fail-fast after retries; they are not converted
into silent fallback actions.

## §8 References

See `simulation-bases.md §2` and role definitions in `simulation-bases.md §4`.

## §9 Variant Comparison

Compare LLM with Rule on polarization path, action distribution, and parser
quality.
