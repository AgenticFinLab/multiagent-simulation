# CreditCycle RuleLLM Variant — explain.md

## §1 Overview

The RuleLLM variant embeds deterministic threshold rules directly into the LLM system prompt. The LLM must follow these rules while also leveraging its language understanding to narrate reasoning. This hybrid approach combines the mechanical precision of the Rule variant with the interpretability of LLM-generated explanations.

| Aspect             | Detail                                             |
|--------------------|----------------------------------------------------|
| Variant            | RuleLLM                                            |
| Simulation         | CreditCycle                                        |
| Decision Mechanism | LLM with embedded threshold rules in system prompt |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                    |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`       |
| Prompt Location    | `CreditCycle/RuleLLM/prompts.py`                   |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMProCyclicalLender (simulation-bases.md §4.1)

| Theory Component      | RuleLLM Implementation                                              |
|-----------------------|---------------------------------------------------------------------|
| Pro-cyclical leverage | Rule in prompt: "If deviation > 0.03, buy {order_size × 2.0} units" |
| Credit contraction    | Rule in prompt: "If deviation < −0.03, sell {order_size} units"     |
| LLM role              | Narrate reasoning; confirm rule-derived action                      |

### §2.2 RuleLLMMinskyBorrower (simulation-bases.md §4.2)

| Theory Component       | RuleLLM Implementation                                                                    |
|------------------------|-------------------------------------------------------------------------------------------|
| Fragility accumulation | Rule in prompt: "If market has been stable for multiple rounds, buy to increase leverage" |
| Crisis deleveraging    | Rule in prompt: "If deviation < −0.05, sell {order_size × 2} immediately"                 |
| LLM role               | Provide Minsky narrative; may preemptively reduce leverage if reasoning detects fragility |

### §2.3 RuleLLMCounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component            | RuleLLM Implementation                                                                           |
|-----------------------------|--------------------------------------------------------------------------------------------------|
| Counter-cyclical deployment | Rule in prompt: "If deviation < −0.05, buy {order_size}; if deviation > 0.05, sell {order_size}" |
| LLM role                    | Explain counter-cyclical rationale                                                               |

### §2.4 RuleLLMValueInvestor (simulation-bases.md §4.4)

| Theory Component | RuleLLM Implementation                                               |
|------------------|----------------------------------------------------------------------|
| Value threshold  | Rule in prompt: "Buy if deviation < −0.10; sell if deviation > 0.10" |
| LLM role         | Provide fundamental analysis narrative                               |

### §2.5 RuleLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component | RuleLLM Implementation                                |
|------------------|-------------------------------------------------------|
| Random trading   | Rule in prompt: "Trade randomly with 30% probability" |

## §3 Hybrid Decision Architecture

```
System Prompt: [Persona] + [Embedded Rule: "If δ > 0.03, buy qty × 2"]
User Prompt:   Current market_data + position + history
LLM Response:  action + quantity (must comply with embedded rule) + reasoning
```

The LLM is instructed to follow the rule but may add narrative context or slight modifications when reasoning suggests unusual market conditions.

## §4 Variant-Specific Features

- **Rule anchoring**: Extreme decisions (crisis sell, boom buy) are rule-anchored; LLM variation is mainly in intermediate cases.
- **Minsky narrative**: RuleLLMMinskyBorrower provides the most detailed credit-cycle narrative since the Minsky trajectory is explicitly described in the prompt.
- **Consistency advantage**: Higher cross-run consistency than pure LLM; similar LAI to Rule variant but with richer output logs.

## §5 Config Reference

Same as Rule variant; adds LLM model config extras.

## §6 Running Instructions

```bash
cd multiagent-simulation
python -m examples.CreditCycle.RuleLLM.run
```

## §7 Expected Behavior

- LAI and CCS values close to Rule baseline
- MFS may be slightly lower if LLM anticipates fragility
- LLM logs capture Minsky reasoning — useful for qualitative analysis

## §8 References

See `simulation-bases.md §2` for full DOI citations.
