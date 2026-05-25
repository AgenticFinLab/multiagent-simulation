# DispositionEffect LLM Variant — explain.md

## §1 Overview

The LLM variant replaces rule-based decisions with LLM inference. Each investor receives a persona system prompt describing their disposition-effect archetype and responds to market broadcasts with a structured buy/sell/hold decision. This tests whether LLMs can simulate Kahneman & Tversky's Prospect Theory biases through persona alone.

| Aspect             | Detail                                                                        |
|--------------------|-------------------------------------------------------------------------------|
| Variant            | LLM                                                                           |
| Simulation         | DispositionEffect                                                             |
| Decision Mechanism | LLM persona prompt + market broadcast                                         |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                               |
| Market Broadcast   | `price`, `purchase_price`, `gain_loss`, `cash`, `position`, `portfolio_value` |
| Prompt Location    | `DispositionEffect/LLM/prompts.py`                                            |

## §2 Theory → Implementation Mapping

### §2.1 LLMDispositionBiased (simulation-bases.md §4.1)

| Theory Component                           | LLM Implementation                                                             |
|--------------------------------------------|--------------------------------------------------------------------------------|
| Prospect Theory (Kahneman & Tversky, 1979) | Persona: "You feel losses 2.25× more painfully than equivalent gains"          |
| Gain domain sell eagerness                 | Persona instructs selling quickly when gain exceeds ~5%; "lock in profit"      |
| Loss domain reluctance                     | Persona instructs holding losers: "you can't bring yourself to lock in a loss" |
| Reference point anchoring                  | `{purchase_price}` and `{gain_loss}` provided in prompt                        |

### §2.2 LLMRationalInvestor (simulation-bases.md §4.2)

| Theory Component        | LLM Implementation                                                                 |
|-------------------------|------------------------------------------------------------------------------------|
| Expected Utility Theory | Persona: "Past prices are irrelevant; you only care about future expected returns" |
| Fundamental trading     | `{price}` and fundamental context in prompt; LLM rebalances toward fundamental     |
| No reference point      | Persona explicitly ignores purchase price                                          |

### §2.3 LLMTaxAwareInvestor (simulation-bases.md §4.3)

| Theory Component                           | LLM Implementation                                                                                 |
|--------------------------------------------|----------------------------------------------------------------------------------------------------|
| Tax-loss harvesting (Constantinides, 1983) | Persona: "You sell losers specifically to harvest tax losses; hold winners to defer capital gains" |
| Anti-disposition framing                   | Persona explicitly reverses psychological bias via economic rationale                              |

### §2.4 LLMInstitutionalInvestor (simulation-bases.md §4.5)

| Theory Component                                  | LLM Implementation                                                           |
|---------------------------------------------------|------------------------------------------------------------------------------|
| Professional discipline (Shapira & Venezia, 2001) | Persona: "Emotion has no place in your decisions; you apply symmetric rules" |
| Symmetric thresholds                              | Persona conveys equal treatment of gains and losses                          |

### §2.5 LLMLossAverse (simulation-bases.md §4.1)

| Theory Component      | LLM Implementation                                                           |
|-----------------------|------------------------------------------------------------------------------|
| Extreme loss aversion | Persona: "I absolutely cannot afford to lose money; losses are catastrophic" |
| Amplified reluctance  | More extreme version of LLMDispositionBiased persona                         |

## §3 Prompt Variables

| Variable            | Source           | Example Value         |
|---------------------|------------------|-----------------------|
| `{price}`           | Market broadcast | `103.5`               |
| `{purchase_price}`  | Agent state      | `100.0`               |
| `{gain_loss}`       | Computed         | `+3.5%`               |
| `{cash}`            | Agent state      | `80000.0`             |
| `{position}`        | Agent state      | `500`                 |
| `{portfolio_value}` | Computed         | `131750.0`            |
| `{history}`         | `HistoryBuffer`  | Last 5 rounds summary |

## §4 Variant-Specific Features

- **Emotional language**: LLM agents may exhibit "fear of loss" or "excitement of profit" in reasoning traces — testable against Rule's mechanical threshold.
- **Threshold drift**: LLM may sell winners at varying gain levels (not fixed 3%) — produces wider PGR/PLR variance.
- **Loss anchoring**: LLM may reference `{purchase_price}` explicitly in reasoning; may express reluctance more strongly than Rule variant.
- **LLMLossAverse vs. LLMDispositionBiased**: Two disposition-biased LLM archetypes allow testing intensity gradient.
- **Response parsing**: `parse_llm_response_with_thinking()` extracts `action` and `quantity` from LLM output.

## §5 Architecture

```
Market.decide() → broadcast market_data
LLMInvestor.perceive() → store market_data, purchase_price
LLMInvestor.decide() → LangChainAPIInference.infer(system_prompt, user_prompt)
                     → parse_llm_response_with_thinking() → {action, quantity}
LLMInvestor.act() → update cash/position, submit bid order
```

## §6 Config Reference

LLM uses `configs/DispositionEffect/LLM/players.yml` for market parameters, initial reference points, and provider settings.

## §7 Running Instructions

```bash
python -m examples.DispositionEffect.LLM.run_disposition_llm
```

## §8 Expected Behavior

- PGR/PLR variance higher than Rule (threshold drift from LLM reasoning)
- LLMDispositionBiased may exhibit stronger loss reluctance verbally but may capitulate earlier under extreme losses
- LLMLossAverse should produce lowest PLR (extreme reluctance to realize losses)
- LLMRationalInvestor may still exhibit mild disposition effect (emergent from LLM training data)

## §9 References

See `simulation-bases.md §2` for full DOI citations.
