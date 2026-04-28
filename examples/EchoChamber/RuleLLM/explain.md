# EchoChamber RuleLLM Variant — explain.md

## §1 Overview

The RuleLLM variant implements EchoChamber with hybrid Rule+LLM agents. Each agent's system prompt embeds BOTH the behavioral persona description AND the exact quantitative formulas from the Rule variant. The LLM reasons about how to apply these rules given the current opinion environment context, maintaining rule compliance while adding qualitative judgment.

| Aspect             | Detail                                                                                                                                                                           |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Variant            | RuleLLM                                                                                                                                                                          |
| Simulation         | EchoChamber                                                                                                                                                                      |
| Decision Mechanism | LLM applies embedded formulas + persona reasoning; outputs `{action_type, intensity, reasoning, analysis}`                                                                       |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                                                                                                                  |
| Market Broadcast   | `polarization`, `prev_polarization`, `mean_opinion`, `cluster_separation`, `cross_cutting_exposure`, `num_polarizers`, `num_depolarizers`, `net_polarization_intensity`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMIdeologue (simulation-bases.md §4.1)

| Theory Component                        | Implementation                                                                                                                                  |
|-----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| In-group amplification (Sunstein, 2001) | System prompt states: "When mean_opinion is same sign as your opinion, apply `in_group_weight * (mean_opinion * extremity_boost − my_opinion)`" |
| Out-group rejection formula             | System prompt states: "For opposing signals, apply `out_group_discount * (mean_opinion − my_opinion)`"                                          |
| Polarizing intensity rule               | System prompt states: "Polarize when `                                                                                                          |

### §2.2 RuleLLMConformist (simulation-bases.md §4.2)

| Theory Component                | Implementation                                                                        |
|---------------------------------|---------------------------------------------------------------------------------------|
| Conformity formula (Asch, 1951) | System prompt embeds: `opinion_update = conformity * (local_group_mean − my_opinion)` |
| Polarize threshold              | System prompt: "Polarize when `                                                       |

### §2.3 RuleLLMCriticalThinker (simulation-bases.md §4.3)

| Theory Component                  | Implementation                                                                              |
|-----------------------------------|---------------------------------------------------------------------------------------------|
| Evidence formula (Isenberg, 1986) | System prompt embeds: `evidence_signal = −my_opinion * evidence_sensitivity * polarization` |
| Depolarize threshold              | System prompt: "Depolarize when `polarization > 0.3`"                                       |

### §2.4 RuleLLMBridgeBuilder (simulation-bases.md §4.4)

| Theory Component             | Implementation                                                                                                  |
|------------------------------|-----------------------------------------------------------------------------------------------------------------|
| Centering formula            | System prompt embeds: `opinion_update = bridge_weight * (0 − my_opinion) * centering_tendency`                  |
| Cluster-based depolarization | System prompt: "Depolarize when `cluster_separation > 0.5`; intensity = `bridge_strength * cluster_separation`" |

### §2.5 RuleLLMPassiveFollower (simulation-bases.md §4.5)

| Theory Component                 | Implementation                                                             |
|----------------------------------|----------------------------------------------------------------------------|
| Drift formula (Lazarsfeld, 1954) | System prompt embeds: `drift = drift_rate * (mean_opinion − my_opinion)`   |
| Engagement probability           | System prompt: "Engage randomly with probability `engagement_probability`" |

## §3 Market Mechanism

Same as Rule variant. OpinionEnvironment is shared from `examples.EchoChamber.Rule.players`:

```
P(t+1) = P(t) + alpha * NetPolarization(t) + beta * CentripetalForce(t) + epsilon(t)
```

## §4 Variant Architecture

| Component      | Detail                                                                                                       |
|----------------|--------------------------------------------------------------------------------------------------------------|
| Base class     | `RuleLLMSocialAgent(GeneralPlayer)`                                                                          |
| Inference      | `LangChainAPIInference(lm_name=..., generation_config=...)`                                                  |
| Context        | `env_data`; system prompt with embedded formulas + persona                                                   |
| Output parsing | `parse_llm_response_with_thinking(response)` → `{action_type, intensity, reasoning, analysis}`               |
| Retry logic    | Up to 3 attempts; on persistent failure → neutral action with `reasoning="LLM parse failed: stayed neutral"` |
| Ray support    | `__getstate__`/`__setstate__` in `RuleLLMSocialAgent` excludes `llm_client` from pickle                      |

## §5 Config Reference

Config file: `configs/EchoChamber/RuleLLM/simulation.yml`

Key LLM extras per agent:
- `llm.lm_name`: LLM model identifier
- `llm.generation_config`: `{temperature, max_new_tokens}`
- `llm.sys_message`: Module path to system prompt (e.g., `examples.EchoChamber.RuleLLM.prompts:RULELLM_IDEOLOGUE_SYS`)
- `llm.user_message`: Module path to user template (e.g., `examples.EchoChamber.RuleLLM.prompts:RULELLM_USER_TEMPLATE`)

## §6 Running Instructions

```bash
export ARK_API_KEY=<your_key>
python examples/EchoChamber/RuleLLM/run_echo_chamber_rulellm.py -c configs/EchoChamber/RuleLLM/simulation.yml
```

## §7 Output Artifacts

Same as LLM variant. Reasoning field includes explicit formula application descriptions.

## §8 Known Limitations

- System prompts with embedded formulas are longer — higher token cost per round
- LLM may interpret formula thresholds loosely under ambiguous environmental conditions
- Opinion update is hardcoded in code: LLM controls only `action_type` and `intensity`

## §9 References

See `simulation-bases.md §4` for agent parameter sources and theoretical derivations.
See `analysis-bases.md §2` for metric definitions and Python function signatures.
