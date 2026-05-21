# RumorSpread Rule Variant Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rule |
| Implements | `../simulation-bases.md` |
| Decision Logic | Deterministic formulas over public belief, distortion, and truth value |
| Schema | Special `social_action`: `action_type`, `intensity`, `agent_role`, `agent_id` |
| Files | `players.py`, `run_rumor.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Role | Theory Component | Implementation |
|---|---|---|
| `GullibleSpreader` | `simulation-bases.md §4.1` | `decide()` updates belief by `credulity` and emits `spread` when `my_belief > 0.2`. |
| `DistortingRelayer` | `simulation-bases.md §4.2` | `decide()` applies sharpening and leveling before relaying with `relay_eagerness`. |
| `SkepticalEvaluator` | `simulation-bases.md §4.3` | `decide()` anchors belief to truth and emits `correct` below `belief_threshold`. |
| `FactChecker` | `simulation-bases.md §4.4` | `decide()` applies professional truth pull and discounted correction intensity. |
| `UninformedBystander` | `simulation-bases.md §4.5` | `decide()` weakly drifts toward public belief and stochastically spreads or ignores. |

## §3 Environment Mechanism

`InformationEnvironment` consumes `social_action` payloads and updates belief
and distortion using the equations in `simulation-bases.md §3`. It records
`belief`, `distortion`, `spread_count`, and `correction_count`.

## §4 Variant Architecture

Every rule agent initializes state from `configs/RumorSpread/Rule/players.yml`,
reads the latest environment broadcast from `observation.inbounds`, computes one
action, and returns it as `content_type="social_action"`.

## §5 Config Reference

Key config paths are `environment.extras.spread_impact`,
`environment.extras.truth_correction`, `gullible_spreader.extras.credulity`,
`distorting_relayer.extras.sharpening_factor`,
`skeptical_evaluator.extras.skepticism`,
`fact_checker.extras.credibility_discount`, and
`uninformed_bystander.extras.engagement_probability`.

## §6 Running Instructions

```bash
python examples/RumorSpread/Rule/run_rumor.py -c configs/RumorSpread/Rule/simulation.yml
```

## §7 Expected Behavior

Belief should initially rise under spreader pressure, distortion should
accumulate while spread activity dominates, and correction should appear after a
lag through skeptical and fact-checking roles.

## §8 References

See `simulation-bases.md §2` for theory references and `analysis-bases.md §2`
for metric definitions.

## §9 Variant Comparison

Rule is the deterministic baseline used to compare LLM, RuleLLM, and Rag
reasoning effects without changing the special social-action schema.
