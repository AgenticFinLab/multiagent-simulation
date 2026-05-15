# DispositionEffect RuleLLM Variant — explain.md

## §1 Overview

The RuleLLM variant embeds the deterministic Prospect Theory rules from the Rule variant directly into each agent's system prompt. The LLM must follow the rule as a hard constraint while using language reasoning to contextualize gain/loss states. This tests whether LLM reasoning can faithfully execute and extend Prospect Theory threshold behavior.

| Aspect             | Detail                                                                        |
|--------------------|-------------------------------------------------------------------------------|
| Variant            | RuleLLM                                                                       |
| Simulation         | DispositionEffect                                                             |
| Decision Mechanism | LLM with embedded Prospect Theory rule constraints                            |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                               |
| Market Broadcast   | `price`, `purchase_price`, `gain_loss`, `cash`, `position`, `portfolio_value` |
| Prompt Location    | `DispositionEffect/RuleLLM/prompts.py`                                        |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMDispositionBiased (simulation-bases.md §4.1)

| Theory Component                           | RuleLLM Implementation                                                                       |
|--------------------------------------------|----------------------------------------------------------------------------------------------|
| Prospect Theory (Kahneman & Tversky, 1979) | Rule embedded: "If gain_loss >= 0.03, sell 50% of position. If gain_loss <= -0.10, sell 15%" |
| λ = 2.25 asymmetry                         | Rule embedded: sell fractions 50% vs. 15% encode loss aversion explicitly                    |
| Reference point                            | `{gain_loss}` computed from `{purchase_price}` in prompt; LLM reasons about anchor           |
| LLM edge cases                             | LLM handles boundary gain_loss (e.g., 0.029 near threshold) with reasoning                   |

### §2.2 RuleLLMRationalInvestor (simulation-bases.md §4.2)

| Theory Component        | RuleLLM Implementation                                                            |
|-------------------------|-----------------------------------------------------------------------------------|
| Expected Utility Theory | Rule embedded: "Rebalance when portfolio weight deviates by >10% from 50% target" |
| No reference point      | Rule explicitly states: "ignore purchase price; focus only on portfolio weight"   |

### §2.3 RuleLLMTaxAwareInvestor (simulation-bases.md §4.3)

| Theory Component                           | RuleLLM Implementation                                                           |
|--------------------------------------------|----------------------------------------------------------------------------------|
| Tax-loss harvesting (Constantinides, 1983) | Rule embedded: "Sell 30% if gain_loss <= -0.05; defer sale if gain_loss >= 0.15" |
| Anti-disposition framing                   | LLM articulates tax rationale for selling losers                                 |

### §2.4 RuleLLMInstitutionalInvestor (simulation-bases.md §4.5)

| Theory Component                                  | RuleLLM Implementation                                                                  |
|---------------------------------------------------|-----------------------------------------------------------------------------------------|
| Professional discipline (Shapira & Venezia, 2001) | Rule embedded: "Sell 30% symmetrically at gain_threshold=0.08 AND loss_threshold=-0.08" |
| Symmetric rule                                    | LLM enforces equal treatment of gains and losses                                        |

### §2.5 RuleLLMLossAverse (simulation-bases.md §4.1)

| Theory Component      | RuleLLM Implementation                                                         |
|-----------------------|--------------------------------------------------------------------------------|
| Extreme loss aversion | Rule embedded: extreme hold preference; very high loss_threshold (e.g., −0.20) |
| High λ encoding       | Sell fraction on loss reduced to ~5% to encode extreme reluctance              |

## §3 Prompt Variables

| Variable            | Source           | Example Value         |
|---------------------|------------------|-----------------------|
| `{price}`           | Market broadcast | `97.0`                |
| `{purchase_price}`  | Agent state      | `100.0`               |
| `{gain_loss}`       | Computed         | `-3.0%`               |
| `{cash}`            | Agent state      | `85000.0`             |
| `{position}`        | Agent state      | `600`                 |
| `{portfolio_value}` | Computed         | `143200.0`            |
| `{history}`         | `HistoryBuffer`  | Last 5 rounds summary |

## §4 Variant-Specific Features

- **Rule compliance testing**: Compare RuleLLM PGR/PLR to Rule variant; differences > 5% indicate LLM reasoning override of embedded rules.
- **Reasoning transparency**: LLM provides explicit rationale for each sell/hold decision — traceable via `<analysis>` tags.
- **Threshold boundary behavior**: RuleLLM may delay sell near threshold (e.g., gain_loss = 0.029) through reasoning — soft threshold instead of hard cut.
- **Response parsing**: `parse_llm_response_with_thinking()` extracts `action` and `quantity`; compliance verified post-hoc.

## §5 Architecture

```
Market.decide() → broadcast market_data
RuleLLMInvestor.perceive() → store market_data, purchase_price
RuleLLMInvestor.decide() → LangChainAPIInference.infer(rule-embedded system_prompt, user_prompt)
                         → parse_llm_response_with_thinking() → {action, quantity}
RuleLLMInvestor.act() → update cash/position, submit bid order
```

## §6 Config Reference

Same `config.yaml` as Rule variant; LLM extras: `model_name`, `temperature`, `max_tokens`.

## §7 Running Instructions

```bash
python -m examples.DispositionEffect.RuleLLM.run_disposition_rulellm
```

## §8 Expected Behavior

- PGR/PLR should closely match Rule variant (embedded rules constrain behavior)
- DC may be slightly wider (LLM reasoning amplifies reluctance or eagerness at boundaries)
- HPA should match Rule; deviations indicate LLM soft-threshold behavior
- RuleLLMLossAverse should show lowest PLR across all RuleLLM agents

## §9 References

See `simulation-bases.md §2` for full DOI citations.
