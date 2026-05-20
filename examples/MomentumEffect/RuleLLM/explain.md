# MomentumEffect RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Momentum and reversion rules embedded in LLM system prompts |
| Market | Same rule-based market as Rule |
| Agents | RuleLLM momentum, contrarian, technical, trend-following, and fundamental agents |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMMomentumTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Prompt states momentum-threshold behavior |
| Runtime path | `RuleLLMInvestor` sends market context to LLM and parses structured decision |

### §2.2 RuleLLMContrarianTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Prompt states reversion rule |
| Runtime path | Parsed action is constrained before order submission |

### §2.3 RuleLLMTechnicalTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Prompt describes technical moving-average signal |
| Runtime path | LLM returns action, bid price, quantity, and reasoning |

### §2.4 RuleLLMTrendFollower

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Prompt expresses trend-following continuation |
| Runtime path | Decision should preserve trend direction under constraints |

### §2.5 RuleLLMFundamentalAnchor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | Prompt states fundamental-value anchor |
| Runtime path | LLM can explain valuation but must emit valid order schema |

## §3 Market Mechanism Implementation

Market mechanics are unchanged from Rule. RuleLLM changes only investor decision
generation.

## §4 Variant-Specific Features

RuleLLM tests whether explicit signal rules remain stable when mediated through
LLM reasoning.

## §5 Architecture Diagram

```text
Market update -> rule prompt + context -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/MomentumEffect/RuleLLM/players.yml`, especially
`extras.llm.sys_message`, `extras.llm.user_message`, `lm_name`, and
`generation_config`.

## §7 Running Instructions

```bash
python examples/MomentumEffect/RuleLLM/run_momentumeffect_rulellm.py \
  -c configs/MomentumEffect/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should preserve trend-following direction and fundamental anchoring
while allowing modest variation in quantity and explanation.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
