# EchoChamber LLM Variant — explain.md

## §1 Overview

The LLM variant implements EchoChamber with LLM-powered agents. Each agent type receives the current opinion environment state and produces action decisions through LLM reasoning guided by a persona system prompt. This variant captures heterogeneous, qualitatively-reasoned opinion dynamics and emergent behavioral patterns not possible with fixed formulas.

| Aspect             | Detail                                                                                                                                                                           |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Variant            | LLM                                                                                                                                                                              |
| Simulation         | EchoChamber                                                                                                                                                                      |
| Decision Mechanism | LLM reasoning from persona + current `env_data`; outputs `{action_type, intensity, reasoning, analysis}`                                                                         |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                                                                                                                  |
| Market Broadcast   | `polarization`, `prev_polarization`, `mean_opinion`, `cluster_separation`, `cross_cutting_exposure`, `num_polarizers`, `num_depolarizers`, `net_polarization_intensity`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 LLMIdeologue (simulation-bases.md §4.1)

| Theory Component                           | Implementation                                                               |
|--------------------------------------------|------------------------------------------------------------------------------|
| In-group amplification (Sunstein, 2001)    | Persona: strong ideological conviction; rejects opposing views in reasoning  |
| Out-group rejection                        | LLM generates low-intensity or neutral response when opposing views dominate |
| Polarizing intensity from opinion strength | LLM infers intensity from `                                                  |

### §2.2 LLMConformist (simulation-bases.md §4.2)

| Theory Component               | Implementation                                                                  |
|--------------------------------|---------------------------------------------------------------------------------|
| Social conformity (Asch, 1951) | Persona: susceptible to social influence; reasoning tracks group mean direction |
| Group proximity                | LLM responds to `mean_opinion` signal; high conformity when group is nearby     |

### §2.3 LLMCriticalThinker (simulation-bases.md §4.3)

| Theory Component                      | Implementation                                                             |
|---------------------------------------|----------------------------------------------------------------------------|
| Persuasive arguments (Isenberg, 1986) | Persona: evidence-evaluating; reasoning justifies depolarization on merits |
| Depolarization when polarization high | LLM uses `polarization` field to assess urgency of depolarizing action     |

### §2.4 LLMBridgeBuilder (simulation-bases.md §4.4)

| Theory Component                        | Implementation                                                                   |
|-----------------------------------------|----------------------------------------------------------------------------------|
| Deliberative democracy (Sunstein, 2001) | Persona: cross-group engager; reasoning explicitly references cluster separation |
| Centering tendency                      | LLM maintains near-neutral opinion in reasoning; depolarizes when clusters wide  |

### §2.5 LLMPassiveBystander (simulation-bases.md §4.5)

| Theory Component                            | Implementation                                                              |
|---------------------------------------------|-----------------------------------------------------------------------------|
| Mass communication drift (Lazarsfeld, 1954) | Persona: low-engagement; reasoning reflects uncertainty and passive drift   |
| Random engagement                           | LLM may choose neutral action frequently; less consistent than Rule variant |

## §3 Market Mechanism

Same as Rule variant. OpinionEnvironment is shared from `examples.EchoChamber.Rule.players`:

```
P(t+1) = P(t) + alpha * NetPolarization(t) + beta * CentripetalForce(t) + epsilon(t)
```

## §4 Variant Architecture

| Component      | Detail                                                                                                       |
|----------------|--------------------------------------------------------------------------------------------------------------|
| Base class     | `LLMSocialAgent(GeneralPlayer)`                                                                              |
| Inference      | `LangChainAPIInference(lm_name=..., generation_config=...)`                                                  |
| Context        | `env_data` from OpinionEnvironment; persona via `sys_message` prompt                                         |
| Output parsing | `parse_llm_response_with_thinking(response)` → `{action_type, intensity, reasoning, analysis}`               |
| Retry logic    | Up to 3 attempts; on persistent failure → neutral action with `reasoning="LLM parse failed: stayed neutral"` |
| Ray support    | `__getstate__`/`__setstate__` in `LLMSocialAgent` excludes `llm_client` from pickle                          |

## §5 Config Reference

Config file: `configs/EchoChamber/LLM/simulation.yml`

Key LLM extras per agent:
- `llm.lm_name`: LLM model identifier (e.g., `ark/doubao-seed-1-6-lite-251015`)
- `llm.generation_config`: `{temperature, max_new_tokens}`
- `llm.sys_message`: Module path to system prompt (e.g., `examples.EchoChamber.LLM.prompts:IDEOLOGUE_SYS`)
- `llm.user_message`: Module path to user template (e.g., `examples.EchoChamber.LLM.prompts:LLM_USER_TEMPLATE`)

## §6 Running Instructions

```bash
export ARK_API_KEY=<your_key>
python examples/EchoChamber/LLM/run_echo_chamber_llm.py -c configs/EchoChamber/LLM/simulation.yml
```

## §7 Output Artifacts

Same as Rule variant plus:
- `reasoning` and `analysis` fields in each action payload for interpretability analysis

## §8 Known Limitations

- LLM may produce out-of-range intensity values; clamped to [0, 1] by `_apply_intensity_constraints()`
- Persona bleeding: LLM may deviate from assigned persona under certain prompt configurations
- Opinion update is hardcoded (same formula as Rule): LLM only controls `action_type` and `intensity`
- Higher cost and latency per round compared to Rule variant

## §9 References

See `simulation-bases.md §4` for agent parameter sources and theoretical derivations.
See `analysis-bases.md §2` for metric definitions and Python function signatures.
