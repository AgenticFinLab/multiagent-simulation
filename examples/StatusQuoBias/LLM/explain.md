# StatusQuoBias LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona-only LLM prompts with canonical trading JSON |
| Key Difference from Other Variants | Investor behavior is produced by language-model reasoning rather than hard-coded thresholds. |
| Primary Research Contribution | Tests whether status quo and default rationalizations emerge from investor personas. |
| Files | `players.py`, `prompts.py`, `run_statusquobias_llm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

### LLMInertialHolder

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.1`; class docstring cites `simulation-bases.md §4.1`. |
| Persona | `LLM_INERTIAL_HOLDER_SYS` describes resistance to changing current holdings. |
| Runtime state | `LLMInvestor._build_prompt()` supplies price, fundamental, deviation, cash, and position. |
| Output contract | `_validate_decision()` requires `action`, `bid_price`, `quantity`, and `reasoning`. |

### LLMDefaultFollower

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.2`; class docstring cites `simulation-bases.md §4.2`. |
| Persona | `LLM_DEFAULT_FOLLOWER_SYS` emphasizes passive default adherence. |
| Runtime state | Same market and portfolio prompt fields as §4.1. |
| Output contract | Same canonical JSON parser and validator as other LLM investors. |

### LLMActiveRebalancer

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.3`; class docstring cites `simulation-bases.md §4.3`. |
| Persona | `LLM_ACTIVE_REBALANCER_SYS` describes rational rebalancing and active adjustment. |
| Runtime state | Same prompt fields; no hidden information. |
| Output contract | Same canonical JSON parser and validator. |

### LLMMomentumTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.4`; class docstring cites `simulation-bases.md §4.4`. |
| Persona | `LLM_MOMENTUM_TRADER_SYS` emphasizes trend response. |
| Runtime state | Same prompt fields; deviation is the trend proxy. |
| Output contract | Same canonical JSON parser and validator. |

### LLMNoiseTrader

| Design Element | Implementation in This Variant |
|---|---|
| Theoretical basis | `simulation-bases.md §4.5`; class docstring cites `simulation-bases.md §4.5`. |
| Persona | `LLM_NOISE_TRADER_SYS` represents low-information liquidity supply. |
| Runtime state | Same prompt fields; stochasticity comes from LLM behavior and temperature. |
| Output contract | Same canonical JSON parser and validator. |

## §3 Market Mechanism Implementation

The LLM variant reuses `Market` from `StatusQuoBias.Rule.players`, so price
formation is identical to `simulation-bases.md §3.1`. Only the investor decision
generator changes.

## §4 LLM Variant-Specific Features

Prompts contain `== PERSONA ==` and `== DECISION RULES ==` blocks. In this
variant the decision rules are qualitative behavioral guidance rather than
deterministic formulas. The user prompt always repeats the canonical decision
schema, and parse failures are retried a bounded number of times before the row
fails fast.

## §5 Architecture Diagram

```text
Market broadcast
        |
        v
LLMInvestor._build_prompt(market + portfolio state)
        |
        v
LangChainAPIInference -> parse_llm_response_with_thinking()
        |
        v
_validate_decision() -> canonical investor order -> Market
```

## §6 Configuration Reference

| Parameter | Config Path | Purpose |
|---|---|---|
| `lm_name` | `*.extras.llm.lm_name` | ARK model used for all LLM investors. |
| `generation_config.temperature` | `*.extras.llm.generation_config.temperature` | Persona-specific stochasticity. |
| `generation_config.max_tokens` | `*.extras.llm.generation_config.max_tokens` | Bounds response length. |
| `initial_cash` / `initial_position` | `*.extras` | Portfolio constraints. |

## §7 Running Instructions

```bash
python examples/StatusQuoBias/LLM/run_statusquobias_llm.py \
  -c configs/StatusQuoBias/LLM/simulation.yml
```

## §8 Expected Behavior Patterns

Inertial and default personas should explain holding or conservative trading
more often than active and momentum personas. Invalid schema output should fail
after bounded retries rather than silently entering the market.

## §9 References

Persona design traces to `../simulation-bases.md §4` and variant rationale to
`../simulation-bases.md §9`. Analysis uses `../analysis-bases.md §2`.
