# RumorSpread LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Mechanism | Persona-driven rumor spread, distortion, skepticism, and correction |
| Environment | InformationEnvironment, not a trading market |
| Schema | Scenario-specific information-action schema |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 LLM Gullible Spreader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Persona prompt favors belief and spreading |
| Runtime path | LLM emits rumor action schema, not trading order schema |

### §2.2 LLM Distorting Relayer

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Persona prompt introduces leveling/sharpening |
| Runtime path | Structured action records intensity and reasoning |

### §2.3 LLM Skeptical Evaluator

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Persona prompt evaluates evidence before acceptance |
| Runtime path | May spread, correct, evaluate, or ignore |

### §2.4 LLM Fact Checker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Persona prompt investigates and corrects false claims |
| Runtime path | Correction actions update environment belief |

### §2.5 LLM Uninformed Bystander

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | Persona prompt represents low engagement |
| Runtime path | Usually ignore or weakly spread |

## §3 Market Mechanism Implementation

RumorSpread has no buy/sell market. The InformationEnvironment aggregates
information actions and updates belief/distortion state.

## §4 Variant-Specific Features

LLM tests whether rumor dynamics emerge from personas. This scenario must keep
its special parser contract and must not be forced into canonical trading JSON.

## §5 Architecture Diagram

```text
Rumor state -> persona prompt -> information action -> environment update
```

## §6 Configuration Reference

Primary config: `configs/RumorSpread/LLM/players.yml`.

## §7 Running Instructions

```bash
python examples/RumorSpread/LLM/run_rumorspread_llm.py \
  -c configs/RumorSpread/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Gullible and distorting agents should raise belief and distortion. Skeptical and
fact-checking agents should reduce belief or slow spread.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
