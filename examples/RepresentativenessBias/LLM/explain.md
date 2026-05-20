# RepresentativenessBias LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Mechanism | Persona-driven representativeness, Bayesian, contrarian, and noise decisions |
| Market | Same price/fundamental market as Rule |
| Agents | LLM pattern matcher, category generalizer, Bayesian updater, contrarian, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 LLM Pattern Matcher

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Persona prompt encourages prototype matching |
| Runtime path | LLM emits structured trading decision from market context |

### §2.2 LLM Category Generalizer

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Persona prompt encourages small-sample category extrapolation |
| Runtime path | Decision reflects category narrative |

### §2.3 LLM Bayesian Updater

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Persona prompt emphasizes base rates and evidence |
| Runtime path | Structured decision acts as rational benchmark |

### §2.4 LLM Contrarian Statistical Trader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Persona prompt trades against pattern-driven mispricing |
| Runtime path | Order is constrained by cash/position |

### §2.5 LLM Noise Trader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Persona prompt supplies random/noisy baseline |
| Runtime path | LLM still emits canonical order schema |

## §3 Market Mechanism Implementation

Market mechanics match Rule. LLM changes the decision generator from explicit
rules to persona reasoning.

## §4 Variant-Specific Features

LLM tests whether representativeness narratives emerge from persona prompts
without explicit formula anchoring.

## §5 Architecture Diagram

```text
Market state -> persona prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/RepresentativenessBias/LLM/players.yml`.

## §7 Running Instructions

```bash
python examples/RepresentativenessBias/LLM/run_representativenessbias_llm.py \
  -c configs/RepresentativenessBias/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Biased LLM agents should overreact to salient patterns while Bayesian and
contrarian personas provide correction.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
