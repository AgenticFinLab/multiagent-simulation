# RumorSpread RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Explicit rumor-action rules embedded in LLM prompts |
| Environment | InformationEnvironment |
| Schema | Scenario-specific `action_type`, `intensity`, `reasoning` style contract |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLM Gullible Spreader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Prompt states credulity/spread eagerness rules |
| Runtime path | LLM emits information action, not order |

### §2.2 RuleLLM Distorting Relayer

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Prompt states leveling/sharpening rules |
| Runtime path | Distortion action updates environment |

### §2.3 RuleLLM Skeptical Evaluator

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Prompt states skepticism/correction rules |
| Runtime path | Evaluation/correction action uses special parser |

### §2.4 RuleLLM Fact Checker

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Prompt states fact-check strength and correction |
| Runtime path | Correction action reduces belief/distortion |

### §2.5 RuleLLM Uninformed Bystander

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | Prompt states low engagement |
| Runtime path | Usually ignore or weakly spread |

## §3 Market Mechanism Implementation

There is no trading market. The environment aggregates information actions and
updates rumor state.

## §4 Variant-Specific Features

RuleLLM keeps explicit rumor rules but uses LLM output. This special schema is a
documented exception to the canonical trading output contract.

## §5 Architecture Diagram

```text
Rumor state -> rule prompt + context -> LLM information action -> environment
```

## §6 Configuration Reference

Primary config: `configs/RumorSpread/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/RumorSpread/RuleLLM/run_rumorspread_rulellm.py \
  -c configs/RumorSpread/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should follow explicit spread/distort/correct thresholds while allowing
natural-language reasoning.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
