# StatusQuoBias RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona plus explicit rule guidance in LLM prompts |
| Key Difference from Other Variants | The LLM receives both behavioral identity and decision-rule descriptions. |
| Primary Research Contribution | Tests whether explicit rule text improves LLM alignment with the deterministic baseline. |
| Files | `players.py`, `prompts.py`, `run_statusquobias_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

### RuleLLMInertialHolder

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.1`; class docstring cites `simulation-bases.md §4.1`. |
| Persona | `RULELLM_INERTIAL_HOLDER_SYS` states a passive investor identity. |
| Rule guidance | Prompt describes only acting when evidence strongly overcomes inertia. |
| Output contract | `_validate_decision()` enforces canonical order JSON. |

### RuleLLMDefaultFollower

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.2`; class docstring cites `simulation-bases.md §4.2`. |
| Persona | `RULELLM_DEFAULT_FOLLOWER_SYS` states default-following behavior. |
| Rule guidance | Prompt emphasizes staying near default unless allocation drift is large. |
| Output contract | Same parser and validator as other RuleLLM investors. |

### RuleLLMActiveRebalancer

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.3`; class docstring cites `simulation-bases.md §4.3`. |
| Persona | `RULELLM_ACTIVE_REBALANCER_SYS` states active rebalancing behavior. |
| Rule guidance | Prompt links undervaluation to buys and overvaluation to sells. |
| Output contract | Same canonical schema. |

### RuleLLMMomentumTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.4`; class docstring cites `simulation-bases.md §4.4`. |
| Persona | `RULELLM_MOMENTUM_TRADER_SYS` states trend-following behavior. |
| Rule guidance | Prompt uses visible price deviation as the trend signal. |
| Output contract | Same canonical schema. |

### RuleLLMNoiseTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.5`; class docstring cites `simulation-bases.md §4.5`. |
| Persona | `RULELLM_NOISE_TRADER_SYS` states low-information trading behavior. |
| Rule guidance | Prompt bounds noise behavior to small liquidity orders. |
| Output contract | Same canonical schema. |

## §3 Market Mechanism Implementation

The market is re-exported from `StatusQuoBias.Rule.players`. The formula,
configuration paths, and order aggregation match `simulation-bases.md §3.1`.

## §4 RuleLLM Variant-Specific Features

Every system prompt separates persona text from explicit decision-rule guidance.
The embedded rules are behavioral guidance, not executable code; the simulator
still validates the returned decision JSON before mutating cash and positions.

## §5 Architecture Diagram

```text
Market broadcast
        |
        v
RuleLLMInvestor._build_prompt(market + portfolio state)
        |
        v
System prompt: persona + decision rules
        |
        v
LLM response -> parser -> _validate_decision() -> order -> Market
```

## §6 Configuration Reference

| Parameter | Config Path | Purpose |
|---|---|---|
| `lm_name` | `*.extras.llm.lm_name` | ARK model for RuleLLM decisions. |
| `generation_config.temperature` | `*.extras.llm.generation_config.temperature` | Role-specific stochasticity. |
| `generation_config.max_tokens` | `*.extras.llm.generation_config.max_tokens` | Response-length guard. |
| Strategy parameters | `*.extras` | Included so prompts and role configs remain traceable to `simulation-bases.md §6`. |

## §7 Running Instructions

```bash
python examples/StatusQuoBias/RuleLLM/run_statusquobias_rulellm.py \
  -c configs/StatusQuoBias/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should be closer to Rule than LLM in action direction and quantity scale
while still producing natural-language reasoning.

## §9 References

Prompt design traces to `../simulation-bases.md §4` and `../simulation-bases.md §9`.
Metrics trace to `../analysis-bases.md §2`.
