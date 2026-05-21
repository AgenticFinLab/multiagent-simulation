# CurrencyCrisis RuleLLM Variant — explain.md

## §1 Overview

The RuleLLM variant embeds the deterministic threshold rules from the Rule variant directly into each agent's system prompt. The LLM must follow the rule as a hard constraint while using language reasoning to handle edge cases and ambiguous states. This tests whether LLM reasoning can faithfully execute and extend rule-based crisis behavior.

| Aspect             | Detail                                              |
|--------------------|-----------------------------------------------------|
| Variant            | RuleLLM                                             |
| Simulation         | CurrencyCrisis                                      |
| Decision Mechanism | LLM with embedded rule constraints in system prompt |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                     |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`        |
| Prompt Location    | `CurrencyCrisis/RuleLLM/prompts.py`                 |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMSpeculativeAttacker (simulation-bases.md §4.1)

| Theory Component                         | RuleLLM Implementation                                                             |
|------------------------------------------|------------------------------------------------------------------------------------|
| Reserve depletion attack (Krugman, 1979) | Rule embedded: "If deviation < −0.03, sell up to order_size"                       |
| Short-cover rule                         | Rule embedded: "If deviation > +0.03, buy up to order_size"                        |
| LLM edge cases                           | LLM handles ambiguous deviation near threshold; may scale more/less than pure rule |

### §2.2 RuleLLMSelfFulfillingTrader (simulation-bases.md §4.2)

| Theory Component                        | RuleLLM Implementation                                          |
|-----------------------------------------|-----------------------------------------------------------------|
| Deviation coordination rule (Obstfeld, 1996) | Rule embedded: "Sell if deviation < −0.01"                    |
| Recovery condition                          | Rule embedded: "Buy cautiously if deviation > +0.02"          |
| Coordination edge case                  | LLM may reason about whether momentum is building or reversing  |

### §2.3 RuleLLMCentralBankDefender (simulation-bases.md §4.3)

| Theory Component      | RuleLLM Implementation                                                   |
|-----------------------|--------------------------------------------------------------------------|
| Peg defense rule     | Rule embedded: "Buy up to 500 if δ < −0.05; sell up to 500 if δ > +0.05" |
| Reserve constraint   | Rule embedded: "Do not buy if cash < quantity × price"                   |
| LLM credibility       | LLM may articulate defense commitment reasoning alongside rule execution |

### §2.4 RuleLLMFundamentalHedger (simulation-bases.md §4.4)

| Theory Component                        | RuleLLM Implementation                              |
|-----------------------------------------|-----------------------------------------------------|
| 5% threshold rule (Morris & Shin, 1998) | Rule embedded: "Buy if δ < −0.05; sell if δ > +0.05" |
| Fundamental value                       | `{fundamental}` and `{deviation}` in prompt         |
| LLM reasoning                           | Provides rationale for fundamental-anchored trade   |

### §2.5 RuleLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component                | RuleLLM Implementation                                                |
|---------------------------------|-----------------------------------------------------------------------|
| Random trade rule (Black, 1986) | Rule embedded: "trade_probability = 0.3; qty ~ Uniform(100, 500)"     |
| LLM stochastic simulation       | LLM simulates randomness; may exhibit slight non-uniform distribution |

## §3 Prompt Variables

| Variable        | Source           | Example Value         |
|-----------------|------------------|-----------------------|
| `{price}`       | Market broadcast | `0.94`                |
| `{fundamental}` | Market broadcast | `1.00`                |
| `{deviation}`   | Market broadcast | `-0.06`               |
| `{round}`       | Market broadcast | `18`                  |
| `{cash}`        | Agent state      | `75000.0`             |
| `{position}`    | Agent state      | `1200`                |

## §4 Variant-Specific Features

- **Rule fidelity testing**: Compare RuleLLM outputs to Rule variant to measure LLM's rule-following accuracy.
- **Edge-case handling**: RuleLLM is expected to behave identically to Rule near thresholds; divergence indicates LLM reasoning override.
- **Hybrid SFAF**: If RuleLLM SFAF > Rule SFAF, LLM reasoning amplifies the self-fulfilling channel beyond the mechanical rule.
- **Response parsing**: `parse_llm_response_with_thinking()` extracts canonical `action`, `bid_price`, `quantity`, and `reasoning`; schema failures fail after bounded retries.

## §5 Architecture

```
Market.decide() → broadcast market_data
RuleLLMInvestor.perceive() → store market_data
RuleLLMInvestor.decide() → LangChainAPIInference.infer(rule-embedded system_prompt, user_prompt)
                         → parse_llm_response_with_thinking()
                         → validate {action, bid_price, quantity, reasoning}
RuleLLMInvestor.act() → submit canonical order
```

## §6 Config Reference

The variant uses `configs/CurrencyCrisis/RuleLLM/players.yml`; LLM extras include
`sys_message`, `user_message`, `lm_name`, `temperature`, and `max_tokens`.

## §7 Running Instructions

```bash
python examples/CurrencyCrisis/RuleLLM/run_currencycrisis_rulellm.py \
  -c configs/CurrencyCrisis/RuleLLM/simulation.yml
```

## §8 Expected Behavior

- AII and PSD should closely match Rule baseline; deviations indicate LLM reasoning override
- SFAF may be slightly higher (LLM amplifies coordination via reasoning)
- DER should track Rule central-bank intervention around the defense threshold
- FAS should match Rule; LLMFundamentalHedger persona reinforces the 5% threshold

## §9 References

See `simulation-bases.md §2` for full DOI citations.
