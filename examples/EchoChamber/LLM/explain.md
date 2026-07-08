# EchoChamber LLM — Implementation Guide

## 1. Overview

| Item | Description |
|---|---|
| Implements | `../simulation-bases.md` |
| Variant | Persona-only LLM decisions over the EchoChamber social-action schema |
| Entry point | `run_echo_chamber_llm.py` |
| Players | `players.py` |
| Prompts | `prompts.py` |
| Configuration | `configs/EchoChamber/LLM/` |
| Output | `EXPERIMENT/EchoChamber/LLM/` |

This is an opinion-dynamics scenario. Its action payload is `social_action`; it
must not be translated into a finance-style order schema.

## 2. Theory → Implementation Mapping

| Social role | Design source | Class and method | Prompt | Observable effect |
|---|---|---|---|---|
| Ideologue | `simulation-bases.md §4.1` | `LLMIdeologue`, inherited `LLMSocialAgent.decide()` | `LLM_IDEOLOGUE_SYS` | Persona favors `polarize` under aligned or divided conditions. |
| Conformist | `simulation-bases.md §4.2` | `LLMConformist`, inherited `decide()` | `LLM_CONFORMIST_SYS` | Persona follows the perceived group direction. |
| Critical thinker | `simulation-bases.md §4.3` | `LLMCriticalThinker`, inherited `decide()` | `LLM_CRITICAL_SYS` | Persona resists groupthink and favors moderation. |
| Bridge builder | `simulation-bases.md §4.4` | `LLMBridgeBuilder`, inherited `decide()` | `LLM_BRIDGE_SYS` | Persona favors `depolarize` as cluster separation rises. |
| Passive follower | `simulation-bases.md §4.5` | `LLMPassiveBystander`, inherited `decide()` | `LLM_BYSTANDER_SYS` | Persona usually remains neutral. |

All five classes intentionally share one implementation path. Their behavioral
difference comes from the configured system prompt, not hidden class-specific
rules.

## 3. State Dynamics Implementation

The coordinator implements `simulation-bases.md §3`:

```text
p(t+1) = clamp(
  p(t) + polarization_impact * (Σ polarize intensity − Σ depolarize intensity)
       + centripetal_force * (0.3 − p(t)) + noise,
  0, 1
)
```

Implemented by `players.py → OpinionEnvironment.decide()`.

| Design symbol | Python name | Config path | Value |
|---|---|---|---:|
| `p(0)` | `initial_polarization` | `environment.config.extras.initial_polarization` | 0.15 |
| action impact | `polarization_impact` | `environment.config.extras.polarization_impact` | 0.12 |
| center pull | `centripetal_force` | `environment.config.extras.centripetal_force` | 0.01 |
| noise scale | `noise_std` | `environment.config.extras.noise_std` | 0.02 |

The environment also derives mean opinion, left/right cluster separation, and
the share of submitted opinions within `(-0.3, 0.3)` as cross-cutting exposure.
There are no intentional deviations from the state-update equation.

## 4. LLM Variant-Specific Features

The prompts expose personality and current social signals but do not embed the
Rule variant's decision formulas. This preserves the comparison described in
`simulation-bases.md §9`: the LLM must express the role from its persona.

The required response is:

```text
<analysis>non-empty reasoning</analysis>
<decision>{"action_type":"polarize|neutral|depolarize",
"intensity":0.0,"reasoning":"brief public reason"}</decision>
```

`LLMSocialAgent._parse_llm_response()` rejects missing tags, missing fields,
empty reasoning, invalid action types, booleans, non-finite numbers, and
intensity outside `[0, 1]`. Parse errors and retryable API errors are retried up
to configured `max_retries`; final failure is explicit and produces no silent
behavioral fallback.

Personal opinion evolves after a valid decision:

```text
polarize:   o(t+1) = clamp(o(t) + sign(o(t)) * polarize_opinion_step * intensity)
depolarize: o(t+1) = clamp(o(t) * (1 - depolarize_opinion_step * intensity))
neutral:    o(t+1) = o(t)
```

## 5. Architecture Diagram

```text
OpinionEnvironment
  │ broadcasts {polarization, previous value, mean opinion,
  │             cluster separation, exposure, action counts, round}
  ├──────────► LLMIdeologue ──────────┐
  ├──────────► LLMConformist ─────────┤
  ├──────────► LLMCriticalThinker ────┤ social_action
  ├──────────► LLMBridgeBuilder ──────┤ payloads
  └──────────► LLMPassiveBystander ───┘
                    │
                    └── prompt → LLM API → strict tagged parser
                                      │
                                      └────────► OpinionEnvironment
```

`topology.yml` implements this bidirectional star. The environment is the sole
coordinator; agents do not message one another directly.

## 6. Configuration Reference

| Parameter | Config path | Value | Design role |
|---|---|---:|---|
| Initial opinion | `*.extras.initial_opinion` | role-specific | Seeds personal state from `simulation-bases.md §4`. |
| Polarizing step | `*.extras.polarize_opinion_step` | 0.05 | Scales personal extremization by returned intensity. |
| Depolarizing step | `*.extras.depolarize_opinion_step` | 0.05 | Scales center movement by returned intensity. |
| Model | `*.extras.llm.lm_name` | `ark/doubao-seed-2-0-mini-260428` | API model used by every role. |
| Retry limit | `*.extras.llm.max_retries` | 3 | Bounds parse/API retries; no fallback action is emitted. |
| Temperature | `*.extras.llm.generation_config.temperature` | 0.3 | Allows limited reasoning variation. |
| Token cap | `*.extras.llm.generation_config.max_new_tokens` | 500 | Bounds one response. |

Required keys are read with fail-fast indexing; the implementation does not
inject hidden defaults.

## 7. Running Instructions

Full run (makes LLM API calls):

```bash
python examples/EchoChamber/LLM/run_echo_chamber_llm.py \
  -c configs/EchoChamber/LLM/simulation.yml
```

Initialization smoke test (no rounds and no LLM API calls):

```bash
python examples/EchoChamber/LLM/run_echo_chamber_llm.py \
  -c configs/EchoChamber/LLM/simulation.yml --setup-only
```

| Environment variable | Purpose |
|---|---|
| `ARK_API_KEY` | Authenticates the configured Ark/Doubao model for full runs. |

A full configured run is 200 rounds with 20 social agents plus one environment.
Outputs go to `EXPERIMENT/EchoChamber/LLM/records`, `communication`,
`monitoring`, and `analysis`.

## 8. Expected Behavior Patterns

| Phase | Expected agent behavior | Expected environment behavior |
|---|---|---|
| Initialization | Personas receive a low-polarization state. | Polarization starts at 0.15. |
| Reinforcement | Ideologues and conformists supply polarizing actions. | Polarization and separation may rise. |
| Counter-response | Critical thinkers and bridge builders increasingly depolarize. | Center pull and counter-actions can slow or reverse growth. |
| Persistence | Passive agents mostly remain neutral; LLM variation remains visible. | State stays finite and bounded in `[0, 1]`. |

Compared with Rule, onset and intensity may vary between runs because decisions
are sampled from persona prompts. Schema validity must not vary.

## 9. References

No references are unique to this implementation variant. See
`simulation-bases.md §2` for the shared theoretical foundation and
`simulation-bases.md §4` for role-level design provenance.
