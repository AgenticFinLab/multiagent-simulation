# DotComBubble LLM Variant — explain.md

## §1 Overview

The LLM variant implements DotComBubble with persona-driven model deliberation. Each investor receives an event-agnostic persona and the current market state. The model proposes buy/sell/hold; executable code then validates the response and enforces cash, inventory, and configured order-size constraints. No rule threshold is embedded in the model decision path.

| Aspect             | Detail                                                   |
|--------------------|----------------------------------------------------------|
| Variant            | LLM                                                      |
| Simulation         | DotComBubble                                             |
| Decision Mechanism | LLM persona reasoning on market state prompt             |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                          |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`             |

## §2 Theory → Implementation Mapping

### §2.1 LLMNewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                                                                         |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | Growth-investor persona weights adoption, network effects, and long-run narratives |
| Persistent buying                   | Persona treats many declines as opportunities without prescribing a numeric trigger |
| Crash capitulation                  | Persona describes reluctant conviction loss; the model must infer action from state |

### §2.2 LLMIPOFlipper (simulation-bases.md §4.2)

| Theory Component                                | Implementation                                                                          |
|-------------------------------------------------|-----------------------------------------------------------------------------------------|
| IPO underpricing flip (Ofek & Richardson, 2003) | New-issue persona seeks temporary mispricing and realizes gains quickly |
| Short-hold arbitrage                            | Persona emphasizes timing and turnover without leaking rule thresholds |

### §2.3 LLMMomentumFollower (simulation-bases.md §4.3)

| Theory Component                    | Implementation                                                                         |
|-------------------------------------|----------------------------------------------------------------------------------------|
| Momentum (Jegadeesh & Titman, 1993) | Trend-following persona treats recent direction as the primary signal |
| 1-period signal                     | User prompt supplies `previous_price` and computed one-period `momentum` |

### §2.4 LLMSkepticalValueInvestor (simulation-bases.md §4.4)

| Theory Component                     | Implementation                                                                    |
|--------------------------------------|-----------------------------------------------------------------------------------|
| Fundamental anchoring (Graham, 1949) | Value persona anchors on fundamental value and a margin of safety |
| Discipline against narrative         | Persona resists stories without embedding a fixed sell threshold |

### §2.5 LLMShortSeller (simulation-bases.md §4.5)

| Theory Component                                  | Implementation                                                                     |
|---------------------------------------------------|------------------------------------------------------------------------------------|
| Synchronisation risk (Abreu & Brunnermeier, 2003) | Skeptical persona recognizes the cost of opposing overvaluation too early |
| Inventory constraint                              | The prompt and code forbid naked shorting; sales cannot exceed current holdings |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t)
λ = 0.01, γ = 0.005 (weak mean-reversion — bubble persistence design)
```

The market broadcasts `price`, `fundamental`, `deviation`, and `round`. The investor derives `previous_price` and one-period `momentum` from its local price history, then adds `cash`, `position`, `portfolio_value`, and `max_order_quantity` to the user prompt.

## §4 LLM Architecture

| Component      | Detail                                                      |
|----------------|-------------------------------------------------------------|
| Base class     | `LLMInvestor` (extends `GeneralPlayer`)                     |
| Inference      | `LangChainAPIInference`                                     |
| Context        | `HistoryBuffer` (last 200 entries)                          |
| Output parsing | `parse_llm_response_with_thinking()` → canonical order fields: `action`, `bid_price`, `quantity`, `reasoning` |
| Retry logic    | `llm.max_retries`; fail fast if the provider or parser cannot produce the required contract |
| Safety layer   | finite-value checks plus cash, inventory, and `order_size` limits |
| Execution      | cash and holdings change in `act()` at the broadcast market price |

## §5 Config Reference

Config files: `configs/DotComBubble/LLM/{simulation.yml,players.yml,topology.yml,persona.yml}`

Key extras: `llm.{sys_message,user_message,lm_name,max_retries,generation_config}`, `initial_cash`, `initial_position`, `order_size`, `record_path`, and `custom_state_hot_limit`. Every value is explicit; required fields have no code defaults.

## §6 Running Instructions

```bash
python -m examples.DotComBubble.LLM.run_dotcombubble_llm

# Five-round smoke run
python -m examples.DotComBubble.LLM.run_dotcombubble_llm --rounds 5
```

## §7 Expected Behavior

- Runs may differ because model sampling is stochastic; compare replicated distributions rather than a single path.
- Narrative and momentum personas should supply destabilizing demand, while value and inventory-constrained skeptical personas should supply counter-pressure.
- A run is analytically acceptable only when recorded decisions satisfy the tagged-output contract and the AQR check reports full compliance.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
