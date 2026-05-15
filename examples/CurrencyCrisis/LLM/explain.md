# CurrencyCrisis LLM Variant — explain.md

## §1 Overview

The LLM variant replaces rule-based decisions with LLM inference. Each investor receives a persona system prompt describing their currency-crisis archetype and responds to market broadcasts with a structured buy/sell/hold decision. This tests whether LLMs exhibit plausible currency-attack and defense dynamics through persona reasoning alone.

| Aspect             | Detail                                       |
|--------------------|----------------------------------------------|
| Variant            | LLM                                          |
| Simulation         | CurrencyCrisis                               |
| Decision Mechanism | LLM persona prompt + market broadcast        |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` |
| Prompt Location    | `CurrencyCrisis/LLM/prompts.py`              |

## §2 Theory → Implementation Mapping

### §2.1 LLMSpeculativeAttacker (simulation-bases.md §4.1)

| Theory Component                         | LLM Implementation                                                                      |
|------------------------------------------|-----------------------------------------------------------------------------------------|
| Reserve depletion attack (Krugman, 1979) | Persona: "You are a macro hedge fund targeting currencies with depleting reserves"      |
| Scaled attack on weakness                | `{deviation}` in prompt triggers stronger short reasoning at larger negative deviations |
| Short-cover on recovery                  | Persona instructs covering when currency recovers above peg                             |

### §2.2 LLMSelfFulfillingTrader (simulation-bases.md §4.2)

| Theory Component                          | LLM Implementation                                                                      |
|-------------------------------------------|-----------------------------------------------------------------------------------------|
| Expectation coordination (Obstfeld, 1996) | Persona: "You sell when you believe others will sell, creating a self-fulfilling panic" |
| 3-period momentum signal                  | `{price}` history provided; LLM infers trend from multi-round context                   |
| Multiple-equilibria belief                | Persona narrative; LLM may coordinate or defect depending on market context             |

### §2.3 LLMCentralBankDefender (simulation-bases.md §4.3)

| Theory Component             | LLM Implementation                                                            |
|------------------------------|-------------------------------------------------------------------------------|
| Reserve intervention mandate | Persona: "You are a central bank committed to defending the peg at all costs" |
| Two-tier defense threshold   | `{deviation}` < −0.10 escalates persona urgency language                      |
| Reserve constraint awareness | `{cash}` in prompt; LLM may scale back defense when reserves low              |

### §2.4 LLMFundamentalHedger (simulation-bases.md §4.4)

| Theory Component                             | LLM Implementation                                                              |
|----------------------------------------------|---------------------------------------------------------------------------------|
| Global games anchoring (Morris & Shin, 1998) | Persona: "You trade based on fundamental value, not speculative momentum"       |
| 8% fundamental threshold                     | `{deviation}` and `{fundamental}` in prompt; LLM applies fundamentals reasoning |
| Counter-speculation                          | Persona explicitly resists momentum-selling                                     |

### §2.5 LLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component                        | LLM Implementation                                                             |
|-----------------------------------------|--------------------------------------------------------------------------------|
| Random uninformed trading (Black, 1986) | Persona: "You trade randomly based on noise signals unrelated to fundamentals" |

## §3 Prompt Variables

| Variable        | Source           | Example Value         |
|-----------------|------------------|-----------------------|
| `{price}`       | Market broadcast | `0.97`                |
| `{fundamental}` | Market broadcast | `1.00`                |
| `{deviation}`   | Market broadcast | `-0.03`               |
| `{round}`       | Market broadcast | `12`                  |
| `{cash}`        | Agent state      | `90000.0`             |
| `{position}`    | Agent state      | `500`                 |
| `{history}`     | `HistoryBuffer`  | Last 5 rounds summary |

## §4 Variant-Specific Features

- **No scaled attack rule**: LLM does not mechanically scale sell by `|δ| × 10`; attack depth depends on persona strength and market signal interpretation.
- **Expectation narrative**: LLMSelfFulfillingTrader may exhibit richer coordination language; may defect from attack if reasoning diverges.
- **Adaptive defense**: LLMCentralBankDefender may modulate defense more subtly than the two-tier rule threshold.
- **Response parsing**: `parse_llm_response_with_thinking()` extracts `action` and `quantity` from LLM output.

## §5 Architecture

```
Market.decide() → broadcast market_data
LLMInvestor.perceive() → store market_data
LLMInvestor.decide() → LangChainAPIInference.infer(system_prompt, user_prompt)
                     → parse_llm_response_with_thinking() → {action, quantity}
LLMInvestor.act() → update cash/position, submit order
```

## §6 Config Reference

Same `config.yaml` as Rule variant; LLM extras: `model_name`, `temperature`, `max_tokens`.

## §7 Running Instructions

```bash
python -m examples.CurrencyCrisis.LLM.run
```

## §8 Expected Behavior

- LLM attack depth may be more variable; SpeculativeAttacker LLM may escalate or retreat based on reasoning
- SelfFulfillingTrader LLM may exhibit richer expectation-coordination or premature defection
- CentralBankDefender LLM may attempt narrative-based deterrence ("credibility signal")
- Higher variance in AII and SFAF compared to Rule variant

## §9 References

See `simulation-bases.md §2` for full DOI citations.
