# MentalAccounting LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Simulation | MentalAccounting |
| Decision Mechanism | Persona-only LLM decisions constrained by the canonical trading schema |
| Theory Reference | `simulation-bases.md §2` and `simulation-bases.md §4` |
| Market Broadcast | `price`, `fundamental`, `deviation`, `net_demand`, `volume`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 MentalAccountant (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Account segregation | `LLM_MENTAL_ACCOUNTANT_PROMPT` frames each position as a separate account. |
| Reference dependence | The user prompt supplies entry price and unrealized P&L. |
| Realization behavior | The model decides within the required buy/sell/hold JSON schema. |

### §2.2 HouseMoneyTrader (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Gains change risk appetite | `LLM_HOUSE_MONEY_PROMPT` asks the model to reason about recent gains. |
| Losses reduce risk appetite | The same prompt asks for cautious behavior after losses. |
| Cash discipline | `players.py` applies affordability constraints after parsing. |

### §2.3 RationalPortfolioManager (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Whole-portfolio evaluation | `LLM_RATIONAL_PORTFOLIO_PROMPT` frames the agent as the stabilizing benchmark. |
| Fundamental comparison | The user prompt provides current price and fundamental value. |
| Risk control | The player validates action, price, quantity, and reasoning. |

### §2.4 SunkCostHolder (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Commitment to losers | `LLM_SUNK_COST_PROMPT` emphasizes reluctance to sell losing positions. |
| Winner trimming | The prompt allows gains to create flexibility. |
| Inventory discipline | Sell quantities are capped by current position. |

### §2.5 NoiseTrader (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Weak idiosyncratic signals | `LLM_NOISE_TRADER_PROMPT` models noisy motives. |
| Liquidity provision | Parsed actions enter the same market order path. |
| Bounded action | Quantity must be a non-negative integer and is constrained by cash/inventory. |

## §3 Market Mechanism

The LLM variant reuses the Rule `Market` and its price equation `P(t+1) = max(0.01, P(t) + lambda * net_demand + gamma * (F - P(t)) + epsilon)`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Coordinator | Rule market imported from `examples.MentalAccounting.Rule.players` |
| Investors | `LLMInvestor` subclasses with persona-only system prompts |
| Inference | `LangChainAPIInference` using config-provided model settings |
| Parser | `parse_llm_response_with_thinking()` extracts `<analysis>` and `<decision>` |
| Output Contract | `action`, `bid_price`, `quantity`, `reasoning`, and `analysis` are required |
| Error Policy | API calls retry for retryable provider errors; invalid final decision contracts raise. |

## §5 Config Reference

Primary config: `configs/MentalAccounting/LLM/simulation.yml`. LLM model settings and prompt references live in `configs/MentalAccounting/LLM/players.yml`.

## §6 Running Instructions

```bash
python examples/MentalAccounting/LLM/run_mentalaccounting.py \
  -c configs/MentalAccounting/LLM/simulation.yml
```

## §7 Expected Behavior

- LLM personas express mental-accounting reasoning in `analysis`.
- All accepted orders keep the canonical trading schema.
- Market dynamics remain comparable to Rule because the coordinator is shared.
- Full runs produce standard analysis outputs through `LLM/analysis.py`.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison.
