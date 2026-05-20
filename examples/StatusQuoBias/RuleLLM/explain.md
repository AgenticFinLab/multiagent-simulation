# StatusQuoBias RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Persona reasoning anchored by status quo and rebalancing rules |
| Market | Same price/fundamental market as Rule |
| Agents | RuleLLM inertial holder, default follower, active rebalancer, momentum trader, noise trader |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

| Agent | Root Section | Runtime Implementation |
|---|---|---|
| RuleLLMInertialHolder | `simulation-bases.md §4.1` | Prompt encodes reluctance to change |
| RuleLLMDefaultFollower | `simulation-bases.md §4.2` | Prompt encodes default adherence |
| RuleLLMActiveRebalancer | `simulation-bases.md §4.3` | Prompt encodes active adjustment |
| RuleLLMMomentumTrader | `simulation-bases.md §4.4` | Prompt encodes trend following |
| RuleLLMNoiseTrader | `simulation-bases.md §4.5` | Prompt encodes random baseline behavior |

## §3 Market Mechanism Implementation

Market clearing remains unchanged. RuleLLM supplies persona and quantitative
rule instructions to the LLM before canonical order parsing.

## §4 Variant-Specific Features

This variant tests whether explicit rule text constrains LLM status quo
rationalizations toward the Rule baseline.

## §5 Architecture Diagram

```text
Market state -> persona + rule prompt -> LLM decision JSON -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/StatusQuoBias/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/StatusQuoBias/RuleLLM/run_statusquobias_rulellm.py \
  -c configs/StatusQuoBias/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should preserve status quo underreaction while making threshold logic
more explicit than LLM.

## §9 References

See `../simulation-bases.md §4`, `../simulation-bases.md §9`, and
`../analysis-bases.md §2`.

