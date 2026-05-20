# VolatilityClustering RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Explicit volatility-clustering rules embedded in LLM prompts |
| Market | Same volatility-aware market as Rule |
| Agents | RuleLLM fundamentalist, trend follower, noise trader, slow adapter, volatility trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMFundamentalist

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Prompt states fundamental-value correction |
| Runtime path | LLM emits structured order decision |

### §2.2 RuleLLMTrendFollower

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Prompt states trend and volatility-sensitive rule |
| Runtime path | Decision should preserve trend direction under constraints |

### §2.3 RuleLLMNoiseTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Prompt expresses noisy participation |
| Runtime path | Output remains canonical order schema |

### §2.4 RuleLLMSlowAdapter

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Prompt states gradual update rule |
| Runtime path | LLM should reflect lagged adjustment |

### §2.5 RuleLLMVolatilityTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Prompt states high/low-volatility threshold behavior |
| Runtime path | Prompt requests volatility-regime decision fields |

## §3 Market Mechanism Implementation

Market mechanics are unchanged from Rule. RuleLLM changes only investor decision
generation.

## §4 Variant-Specific Features

RuleLLM tests whether volatility-regime rules remain stable under LLM reasoning.

## §5 Architecture Diagram

```text
Market volatility state -> rule prompt + context -> LLM decision -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/VolatilityClustering/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/VolatilityClustering/RuleLLM/run_volatilityclustering_rulellm.py \
  -c configs/VolatilityClustering/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should preserve high-volatility persistence and threshold responses
while allowing explanation and quantity variation.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
