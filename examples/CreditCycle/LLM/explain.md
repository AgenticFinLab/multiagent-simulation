# CreditCycle LLM Variant — explain.md

## §1 Overview

The LLM variant replaces rule-based decisions with LLM inference. Each investor receives a persona system prompt describing their credit-cycle archetype and responds to market broadcasts with a structured buy/sell/hold decision. This tests whether LLMs exhibit plausible credit-cycle behavior through persona alone.

| Aspect             | Detail                                       |
|--------------------|----------------------------------------------|
| Variant            | LLM                                          |
| Simulation         | CreditCycle                                  |
| Decision Mechanism | LLM persona prompt + market broadcast        |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` |
| Prompt Location    | `CreditCycle/LLM/prompts.py`                 |

## §2 Theory → Implementation Mapping

### §2.1 LLMProCyclicalLender (simulation-bases.md §4.1)

| Theory Component                            | LLM Implementation                                                                |
|---------------------------------------------|-----------------------------------------------------------------------------------|
| Pro-cyclical leverage (Adrian & Shin, 2010) | Persona: "You are a bank that expands lending in booms and tightens in downturns" |
| Deviation signal                            | `{deviation}` in user prompt triggers boom/bust reasoning                         |
| Credit multiplier concept                   | Persona narrative; no hard multiplier enforced                                    |

### §2.2 LLMMinskyBorrower (simulation-bases.md §4.2)

| Theory Component                          | LLM Implementation                                                                    |
|-------------------------------------------|---------------------------------------------------------------------------------------|
| Stability breeds fragility (Minsky, 1986) | Persona: "You increase leverage during calm markets; you are caught in Ponzi finance" |
| Forced deleveraging                       | LLM triggered by large negative deviation in user prompt                              |
| `stable_rounds` concept                   | Conveyed via `{round}` context; LLM infers calm duration                              |

### §2.3 LLMCounterCyclicalLender (simulation-bases.md §4.3)

| Theory Component                | LLM Implementation                                                             |
|---------------------------------|--------------------------------------------------------------------------------|
| Counter-cyclical capital buffer | Persona: "You accumulate reserves during booms and deploy liquidity in crises" |
| Crisis detection                | `{deviation}` < −0.05 in prompt signals crisis                                 |

### §2.4 LLMValueInvestor (simulation-bases.md §4.4)

| Theory Component                | LLM Implementation                                                   |
|---------------------------------|----------------------------------------------------------------------|
| Margin of safety (Graham, 1949) | Persona: "You buy only at significant discount to fundamental value" |
| Fundamental reference           | `{fundamental}` and `{price}` provided in broadcast                  |

### §2.5 LLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component                       | LLM Implementation                                         |
|----------------------------------------|------------------------------------------------------------|
| Random uninformed trader (Black, 1986) | Persona: "You trade randomly without fundamental analysis" |

## §3 Prompt Variables

| Variable        | Source           | Example Value         |
|-----------------|------------------|-----------------------|
| `{price}`       | Market broadcast | `102.5`               |
| `{fundamental}` | Market broadcast | `100.0`               |
| `{deviation}`   | Market broadcast | `0.025`               |
| `{round}`       | Market broadcast | `15`                  |
| `{cash}`        | Agent state      | `85000.0`             |
| `{position}`    | Agent state      | `500`                 |
| `{history}`     | `HistoryBuffer`  | Last 5 rounds summary |

## §4 Variant-Specific Features

- **No `stable_rounds` counter**: LLM infers leverage accumulation from round number and market context; may not exhibit Minsky cycle as precisely as Rule.
- **Narrative boom-bust**: LLM agents may exhibit richer crisis language and anticipate turning points through reasoning.
- **Consistency risk**: LLM agents may randomly switch behavior; lower consistency than Rule variant.
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
cd multiagent-simulation
python -m examples.CreditCycle.LLM.run
```

## §8 Expected Behavior

- LLM boom-bust may be more variable in timing
- MinskyBorrower LLM may recognize fragility earlier and reduce leverage
- CounterCyclicalLender LLM may provide more nuanced crisis deployment
- Larger standard deviation in LAI and CCS compared to Rule variant

## §9 References

See `simulation-bases.md §2` for full DOI citations.
