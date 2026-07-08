# EchoChamber RuleLLM Variant Explanation

## §1 Overview

The RuleLLM variant gives each model both a social persona and explicit
formula-like decision rules derived from the Rule implementation. It preserves
the EchoChamber `social_action` schema.

## §2 Theory -> Implementation Mapping

| Social Role | Theory Component | Implementation |
|---|---|---|
| `RuleLLMIdeologue` | `simulation-bases.md §4.1` | Prompt states the in-group/out-group update formula and polarize threshold. |
| `RuleLLMConformist` | `simulation-bases.md §4.2` | Prompt states local-group mean and conformity update rules. |
| `RuleLLMCriticalThinker` | `simulation-bases.md §4.3` | Prompt states evidence signal and depolarization rule. |
| `RuleLLMBridgeBuilder` | `simulation-bases.md §4.4` | Prompt states centering and cluster-separation rules. |
| `RuleLLMPassiveFollower` | `simulation-bases.md §4.5` | Prompt states drift and low-engagement rules. |

## §3 Environment Mechanism

The environment consumes the same `social_action` payload as Rule. RuleLLM
changes only how action type and intensity are chosen.

## §4 Variant Architecture

`RuleLLMSocialAgent` loads role prompts, calls the API model, validates
`action_type`, `intensity`, and `reasoning`, updates personal opinion, and emits
the special-schema action.

## §5 Config Reference

`configs/EchoChamber/RuleLLM/players.yml` binds RuleLLM role classes and prompt
paths. It uses the same environment parameters and topology as Rule.

## §6 Running Instructions

```bash
python -m examples.EchoChamber.RuleLLM.run_echo_chamber_rulellm -c configs/EchoChamber/RuleLLM/simulation.yml
```

For a startup check that does not call the model API:

```bash
python -m examples.EchoChamber.RuleLLM.run_echo_chamber_rulellm -c configs/EchoChamber/RuleLLM/simulation.yml --setup-only
```

## §7 Expected Behavior

RuleLLM should follow Rule-style thresholds more closely than persona-only LLM
while still producing auditable natural-language analysis.

## §8 References

See `simulation-bases.md §2` and role formulas in `simulation-bases.md §4`.

## §9 Variant Comparison

Compare RuleLLM against Rule for formula adherence and against LLM for reduced
behavioral dispersion.
