# MentalAccounting RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Simulation | MentalAccounting |
| Decision Mechanism | LLM reasoning constrained by explicit mental-accounting decision rules |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `net_demand`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 MentalAccountant (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Segregated accounts | `RULELLM_MENTAL_ACCOUNTANT_SYS` requires per-account position reasoning. |
| Gain/loss thresholds | The prompt states winner and loser realization rules. |
| Bounded order | `RuleLLMInvestor.decide()` validates and constrains the parsed action. |

### §2.2 HouseMoneyTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| House-money risk | `RULELLM_HOUSE_MONEY_SYS` switches risk appetite by P&L sign. |
| Value direction | The prompt trades undervaluation/overvaluation only beyond threshold. |
| Position constraints | Buy/sell quantities are bounded by cash and inventory. |

### §2.3 RationalPortfolioManager (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Holistic valuation | `RULELLM_RATIONAL_PORTFOLIO_SYS` compares price and fundamental value. |
| Stabilizing behavior | Buys undervaluation and sells overvaluation. |
| Risk-scaled sizing | Prompt rules constrain sizing with risk aversion and base size. |

### §2.4 SunkCostHolder (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Loss holding | `RULELLM_SUNK_COST_SYS` holds unless gain threshold is reached. |
| Winner realization | Positive P&L can trigger a configured sell fraction. |
| Commitment effect | Explanation should reference entry price and prior investment. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Background random flow | `RULELLM_NOISE_TRADER_SYS` describes probabilistic trading. |
| Weak signal basis | Reasoning remains brief and noisy. |
| Bounded order size | Parsed quantity is constrained by portfolio state. |

## §3 Market Mechanism

RuleLLM reuses the Rule market and sends canonical investor orders into the same price update equation.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | Rule market imported from the Rule variant |
| Investors | `RuleLLMInvestor` subclasses |
| Prompt Structure | Exact `== PERSONA ==` and `== DECISION RULES ==` blocks |
| Parser | `parse_llm_response_with_thinking()` |
| Output Contract | Required `action`, `bid_price`, `quantity`, `reasoning`, and `analysis` |
| Error Policy | Retryable provider errors are retried; invalid final decision contracts raise. |

## §5 Config Reference

Primary config: `configs/MentalAccounting/RuleLLM/simulation.yml`. Investor extras and model settings live in `configs/MentalAccounting/RuleLLM/players.yml`.

## §6 Running Instructions

```bash
python examples/MentalAccounting/RuleLLM/run_mentalaccounting.py \
  -c configs/MentalAccounting/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- RuleLLM preserves deterministic rule direction while allowing natural-language calculations.
- Orders use the same schema as Rule and LLM.
- Analysis remains comparable across variants.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
