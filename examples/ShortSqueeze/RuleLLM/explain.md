# ShortSqueeze RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Explicit squeeze rules embedded in LLM prompts |
| Market | Same squeeze market as Rule |
| Agents | RuleLLM short seller, retail coordinator, momentum buyer, value investor, institutional holder |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMShortSeller

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Prompt states covering rule |
| Runtime path | LLM decision is parsed and constrained before order |

### §2.2 RuleLLMRetailCoordinator

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Prompt states bullish retail pressure |
| Runtime path | Structured decision records action and reasoning |

### §2.3 RuleLLMMomentumBuyer

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Prompt states momentum-buying rule |
| Runtime path | LLM should preserve trend-following direction |

### §2.4 RuleLLMValueInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Prompt states value resistance |
| Runtime path | Cash/position constraints cap trades |

### §2.5 RuleLLMInstitutionalHolder

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Prompt states sticky-holder behavior |
| Runtime path | Usually holds, constraining float |

## §3 Market Mechanism Implementation

Market mechanics match Rule. RuleLLM changes only the final decision-generation
path for investors.

## §4 Variant-Specific Features

RuleLLM tests whether explicit squeeze mechanics survive LLM reasoning.

## §5 Architecture Diagram

```text
Market squeeze state -> prompt + context -> LLM JSON decision -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/ShortSqueeze/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/ShortSqueeze/RuleLLM/run_shortsqueeze_rulellm.py \
  -c configs/ShortSqueeze/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

Short sellers should cover under stress; retail and momentum agents should add
buy pressure; value agents should resist extreme premiums.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
