# OverconfidenceBias RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Simulation | OverconfidenceBias |
| Decision Mechanism | Explicit overconfidence rules plus LLM reasoning |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 OverconfidentTrader (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Signal overprecision | `RULELLM_OVERCONFIDENT_TRADER_SYS` states the perceived-signal rule. |
| Excess size | Prompt rules bound direction and size by signal and portfolio limits. |
| Contract validation | Player validates parsed decision fields. |

### §2.2 SelfAttributor (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Self-attribution | Prompt separates persona from explicit decision rules. |
| Confidence boost | Rules describe favorable-state reinforcement and negative-state trimming. |
| Inventory constraints | Player caps orders by portfolio state. |

### §2.3 CalibratedTrader (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Rational threshold | Prompt requires meaningful deviation before action. |
| Value direction | Buys undervaluation and sells overvaluation. |
| Benchmark role | Uses same parser and market path as biased agents. |

### §2.4 ContrarianInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Overreaction correction | Prompt trades against extreme deviations. |
| Stabilizing role | Orders oppose overconfident pressure. |
| Constraint enforcement | Player validates non-negative quantity and bid price. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Random flow | Prompt describes noisy impulse trading. |
| Liquidity role | Orders enter shared market equation. |
| Bounded action | Quantity remains non-negative and portfolio-constrained. |

## §3 Market Mechanism

RuleLLM reuses the Rule market and canonical order schema.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | Rule market |
| Investors | `RuleLLMInvestor` subclasses |
| Prompt Structure | Exact `== PERSONA ==` and `== DECISION RULES ==` blocks |
| Parser | `parse_llm_response_with_thinking()` |
| Error Policy | Retryable provider errors are retried; invalid final decision contracts raise. |

## §5 Config Reference

Primary config: `configs/OverconfidenceBias/RuleLLM/simulation.yml`.

## §6 Running Instructions

```bash
python examples/OverconfidenceBias/RuleLLM/run_overconfidencebias_rulellm.py \
  -c configs/OverconfidenceBias/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- Rule direction is preserved by explicit prompt rules.
- Reasoning text explains overconfidence, attribution, calibration, contrarian, or noise logic.
- Orders remain comparable with Rule and LLM.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
