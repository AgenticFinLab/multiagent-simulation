# RepresentativenessBias RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Explicit representativeness/base-rate rules embedded in LLM prompts |
| Market | Same market as Rule |
| Agents | RuleLLM pattern matcher, category generalizer, Bayesian updater, contrarian, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLM Pattern Matcher

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Prompt states pattern sensitivity and base-rate neglect |
| Runtime path | LLM decision parsed into canonical order |

### §2.2 RuleLLM Category Generalizer

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Prompt states category-weight and sample-bias behavior |
| Runtime path | Structured decision records reasoning |

### §2.3 RuleLLM Bayesian Updater

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Prompt states base-rate/evidence weighting |
| Runtime path | Rational benchmark remains formula anchored |

### §2.4 RuleLLM Contrarian Statistical

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Prompt states contrarian threshold behavior |
| Runtime path | Order constrained by state and market price |

### §2.5 RuleLLM Noise Trader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Prompt states noisy baseline behavior |
| Runtime path | Emits valid order schema |

## §3 Market Mechanism Implementation

Market mechanics are unchanged. RuleLLM changes only the investor decision path.

## §4 Variant-Specific Features

RuleLLM tests whether explicit base-rate and representativeness rules remain
stable under LLM reasoning.

## §5 Architecture Diagram

```text
Market state -> rule prompt + context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/RepresentativenessBias/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/RepresentativenessBias/RuleLLM/run_representativenessbias_rulellm.py \
  -c configs/RepresentativenessBias/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should preserve the Rule bias/correction structure while adding bounded
natural-language variation.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
