# EchoChamber Rule Variant Explanation

## §1 Overview

The Rule variant is the formula-driven baseline for the EchoChamber special
schema. It models opinion polarization through `social_action` messages rather
than financial orders. Agent decisions follow configured equations; the
environment noise term and passive participation remain explicitly stochastic.

## §2 Theory -> Implementation Mapping

| Social Role | Theory Component | Implementation |
|---|---|---|
| `Ideologue` | `simulation-bases.md §4.1` | In-group amplification and out-group discount in `Ideologue.decide`. |
| `Conformist` | `simulation-bases.md §4.2` | Local-group alignment in `Conformist.decide`. |
| `CriticalThinker` | `simulation-bases.md §4.3` | Evidence-based center pull and depolarizing action in `CriticalThinker.decide`. |
| `BridgeBuilder` | `simulation-bases.md §4.4` | Centering and cluster-separation response in `BridgeBuilder.decide`. |
| `PassiveFollower` | `simulation-bases.md §4.5` | Low-engagement drift and occasional participation in `PassiveFollower.decide`. |

## §3 Environment Mechanism

`OpinionEnvironment` aggregates `polarize`, `neutral`, and `depolarize`
intensities, updates polarization, computes mean opinion and cluster separation,
and broadcasts the next environment state. Every coefficient and behavioral
threshold is loaded fail-fast from `configs/EchoChamber/Rule/players.yml`.

## §4 Variant Architecture

Social agents inherit `BaseSocialAgent`, store personal opinion histories, and
emit `Action(action_type="social_action")` payloads. The output schema is
`action_type`, `intensity`, `agent_role`, `agent_id`, and `opinion`.
Expanded ideologue instances alternate the sign of the configured initial
opinion, producing the balanced left/right seed required by the cluster model.

## §5 Config Reference

`configs/EchoChamber/Rule/players.yml` binds the environment and five social
roles. `simulation.yml` sets the full 200-round experiment and `topology.yml`
routes environment updates and social actions.

## §6 Running Instructions

```bash
python -m examples.EchoChamber.Rule.run_echo_chamber -c configs/EchoChamber/Rule/simulation.yml
```

For a startup smoke test, append `--steps 2`.

## §7 Expected Behavior

Ideologues and conformists should generate polarization pressure, while
critical thinkers and bridge builders should generate depolarizing pressure.
Passive followers should mostly provide background opinion drift.

## §8 References

See `simulation-bases.md §2` for the theoretical basis and
`simulation-bases.md §4` for role-specific mappings.

## §9 Variant Comparison

Rule is the special-schema baseline for LLM, RuleLLM, and Rag comparisons.
