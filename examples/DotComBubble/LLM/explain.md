# DotComBubble LLM Variant — explain.md

## §1 Overview

The LLM variant implements DotComBubble with persona-driven LLM decision-making. Each investor receives a natural-language persona description and market state prompt; the LLM generates buy/sell/hold decisions without embedded rule code. Bubble dynamics emerge from the interaction of narrative-driven personas under genuine language model reasoning.

| Aspect             | Detail                                                   |
|--------------------|----------------------------------------------------------|
| Variant            | LLM                                                      |
| Simulation         | DotComBubble                                             |
| Decision Mechanism | LLM persona reasoning on market state prompt             |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                          |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`, `momentum` |

## §2 Theory → Implementation Mapping

### §2.1 LLMNewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                                                                         |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | System prompt: "You believe in the new internet economy paradigm and the irrelevance of traditional valuation metrics" |
| Persistent buying                   | Persona instructs buying unless crash is extreme; maps to δ > −0.20 equivalent through language                        |
| Crash capitulation                  | Prompt encodes reluctance to sell; only exits on deep negative deviation                                               |

### §2.2 LLMIPOFlipper (simulation-bases.md §4.2)

| Theory Component                                | Implementation                                                                          |
|-------------------------------------------------|-----------------------------------------------------------------------------------------|
| IPO underpricing flip (Ofek & Richardson, 2003) | System prompt: "You buy at undervaluation and flip quickly once premium is established" |
| Short-hold arbitrage                            | Persona targets δ > 0.05 as sell signal in language; buys on dip                        |

### §2.3 LLMMomentumFollower (simulation-bases.md §4.3)

| Theory Component                    | Implementation                                                                         |
|-------------------------------------|----------------------------------------------------------------------------------------|
| Momentum (Jegadeesh & Titman, 1993) | System prompt: "You follow price trends — buy when price is rising, sell when falling" |
| 1-period signal                     | Prompt includes `price_change` field; persona uses this as primary decision input      |

### §2.4 LLMSkepticalValueInvestor (simulation-bases.md §4.4)

| Theory Component                     | Implementation                                                                    |
|--------------------------------------|-----------------------------------------------------------------------------------|
| Fundamental anchoring (Graham, 1949) | System prompt: "You only buy when price is significantly below fundamental value" |
| Discipline against narrative         | Persona explicitly resists hype; sells on overvaluation above 20%                 |

### §2.5 LLMShortSeller (simulation-bases.md §4.5)

| Theory Component                                  | Implementation                                                                     |
|---------------------------------------------------|------------------------------------------------------------------------------------|
| Synchronisation risk (Abreu & Brunnermeier, 2003) | System prompt: "You bet against overvalued assets but must survive short squeezes" |
| Risk management                                   | Persona balances short entry at high deviation with cover at negative deviation    |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t)
λ = 0.01, γ = 0.005 (weak mean-reversion — bubble persistence design)
```

Prompt includes: `price`, `fundamental`, `deviation`, `cash`, `position`, `portfolio_value`, `price_change`.

## §4 LLM Architecture

| Component      | Detail                                                      |
|----------------|-------------------------------------------------------------|
| Base class     | `LLMInvestor` (extends `GeneralPlayer`)                     |
| Inference      | `LangChainAPIInference`                                     |
| Context        | `HistoryBuffer` (last 200 entries)                          |
| Output parsing | `parse_llm_response_with_thinking()` → canonical order fields: `action`, `bid_price`, `quantity`, `reasoning` |
| Retry logic    | 3 attempts; fail fast if the provider or parser cannot produce the required contract |

## §5 Config Reference

Config files: `configs/DotComBubble/LLM/{simulation.yml,players.yml,topology.yml,persona.yml}`

Key extras: `llm.lm_name`, `llm.generation_config`, `initial_cash`, `initial_position`, `order_size`; system prompt loaded from `prompts.py`.

## §6 Running Instructions

```bash
python -m examples.DotComBubble.LLM.run_dotcombubble_llm
```

## §7 Expected Behavior

- LLM variant typically shows more volatile bubble trajectories than Rule — personas can over-commit to narrative or momentum.
- LLMNewEconomyEvangelist may buy later into the bubble than Rule equivalent (language nuance delays exit decisions).
- LLMShortSeller shows variable SSR — LLM occasionally exits shorts prematurely on language-level fear signals.
- BAI and BD broadly similar to Rule but with higher round-to-round variance.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
