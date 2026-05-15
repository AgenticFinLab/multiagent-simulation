# EndowmentEffect LLM — Implementation Explanation

## §1 Overview

The LLM variant replaces deterministic threshold rules with persona-driven LLM reasoning. Each investor class carries a system prompt encoding the behavioral biases from `simulation-bases.md §4.N`. The LLM observes price, fundamental, deviation, cash, and position, and reasons freely within the persona to choose action and quantity.

| Aspect             | Detail                                                           |
|--------------------|------------------------------------------------------------------|
| Variant            | LLM (language-model persona)                                     |
| Simulation         | EndowmentEffect                                                  |
| Decision Mechanism | LLM persona system prompts — no hardcoded thresholds             |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                  |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `cash`, `position`, `round` |

## §2 Theory → Implementation Mapping

### §2.1 LLMEndowedHolder (simulation-bases.md §4.1)

| Theory Component                          | Implementation                                                                                                                                           |
|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Endowment premium (Kahneman et al., 1990) | System prompt encodes ownership attachment: "You are attached to your position and reluctant to sell unless the price is substantially above fair value" |
| Loss aversion suppresses selling          | Persona resists selling; LLM reasons about emotional cost of giving up the asset                                                                         |
| Rational buying at undervaluation         | Prompt does not prohibit buying when price is below fundamental                                                                                          |

### §2.2 LLMStatusQuoSeller (simulation-bases.md §4.2)

| Theory Component                               | Implementation                                                                                                             |
|------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|
| Status quo bias (Samuelson & Zeckhauser, 1988) | System prompt encodes inertia: "You prefer to maintain your current position unless there is a compelling reason to trade" |
| Inertia under moderate deviations              | LLM defaults to hold; only acts on clearly abnormal deviations as reasoned by the persona                                  |
| Selective response to deep undervaluation      | Prompt allows buying on significant price drops as an exception to inertia                                                 |

### §2.3 LLMRationalArbitrageur (simulation-bases.md §4.3)

| Theory Component                             | Implementation                                                                                                    |
|----------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| Rational expectations benchmark (Muth, 1961) | System prompt: "You are a rational arbitrageur with no ownership bias; exploit deviations from fundamental value" |
| Symmetric arbitrage                          | Prompt instructs symmetric buy/sell on negative/positive deviations; LLM sets quantity based on magnitude         |
| No endowment distortion                      | Persona explicitly lacks loss aversion or ownership framing                                                       |

### §2.4 LLMNewBuyer (simulation-bases.md §4.4)

| Theory Component                                         | Implementation                                                                       |
|----------------------------------------------------------|--------------------------------------------------------------------------------------|
| Rational WTP equals market value (Kahneman et al., 1990) | System prompt: "You have no prior ownership; evaluate assets purely at market price" |
| No ownership premium                                     | Persona has no attachment; LLM buys when price appears below fundamental             |
| Sell on significant overvaluation                        | Prompt allows selling when the LLM judges the overvaluation is significant           |

### §2.5 LLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component                       | Implementation                                                                                                   |
|----------------------------------------|------------------------------------------------------------------------------------------------------------------|
| Uninformed noise trading (Black, 1986) | System prompt: "You trade on gut feeling and market noise, not fundamentals; your decisions are somewhat random" |
| Non-fundamental motivation             | Persona explicitly ignores fundamental analysis in favour of mood-driven decisions                               |
| Constrained by portfolio               | LLM is instructed to respect cash and position limits                                                            |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Market class is imported from `Rule/players.py` (shared). All LLM investors send orders to the same Market.

## §4 Variant Architecture

| Component      | Detail                                                                              |
|----------------|-------------------------------------------------------------------------------------|
| Base class     | `LLMInvestor` → `GeneralPlayer`                                                     |
| Inference      | `LangChainAPIInference` (3-attempt retry)                                           |
| Context        | `price`, `fundamental`, `deviation`, `cash`, `position`, `portfolio_value`, `round` |
| Output parsing | `parse_llm_response_with_thinking()` → `{"action": ..., "quantity": ...}`           |
| Retry logic    | 3 attempts; falls back to hold on failure                                           |

## §5 Config Reference

Config file: `configs/EndowmentEffect/LLM/simulation.yml`

LLM config under `extras.llm`:
- `lm_name`: model identifier
- `generation_config`: temperature, max_tokens etc.

## §6 Running Instructions

```bash
python -m examples.EndowmentEffect.LLM.run_endowment_effect \
    -c configs/EndowmentEffect/LLM/simulation.yml
```

## §7 Expected Behavior

- **Stochastic endowment effect**: LLMEndowedHolder may occasionally sell even when holding is expected; introduces variance not seen in Rule variant
- **Emergent strategies**: LLM personas may discover nuanced hold/sell thresholds not encoded in Rule
- **MAD range**: Typically 0.04–0.15 (wider than Rule due to LLM variability)
- **Volume**: 60–90% of Rule baseline depending on LLM temperature

## §8 References

See `simulation-bases.md §2` for full DOI citations for all theoretical foundations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
