# DotComBubble RuleLLM Variant — explain.md

## §1 Overview

The RuleLLM variant combines deterministic threshold rules with LLM persona reasoning. Structured rules are embedded directly into the system prompt so the LLM can both follow them and contextualise them with narrative judgment. This produces bubble dynamics that are more interpretable than pure LLM but more flexible than pure Rule.

| Aspect             | Detail                                                                   |
|--------------------|--------------------------------------------------------------------------|
| Variant            | RuleLLM                                                                  |
| Simulation         | DotComBubble                                                             |
| Decision Mechanism | Rule-embedded LLM prompt; LLM confirms or adjusts within rule boundaries |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                          |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`, `price_change`             |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMNewEconomyEvangelist (simulation-bases.md §4.1)

| Theory Component                    | Implementation                                                                     |
|-------------------------------------|------------------------------------------------------------------------------------|
| Narrative economics (Shiller, 2000) | System prompt embeds: "Buy when deviation > −0.20; sell only if deviation < −0.30" |
| LLM contextualisation               | LLM reasons about narrative strength but cannot override the embedded thresholds   |
| Crash capitulation                  | Rule boundary prevents premature selling; LLM may narrate conviction to hold       |

### §2.2 RuleLLMIPOFlipper (simulation-bases.md §4.2)

| Theory Component                             | Implementation                                                                                 |
|----------------------------------------------|------------------------------------------------------------------------------------------------|
| IPO flip arbitrage (Ofek & Richardson, 2003) | System prompt embeds: "Flip when deviation > 0.05; buy on any dip (deviation < 0)"             |
| LLM flip timing                              | LLM can choose quantity within rule; may hold slightly longer if narrative context is positive |

### §2.3 RuleLLMMomentumFollower (simulation-bases.md §4.3)

| Theory Component                    | Implementation                                                                            |
|-------------------------------------|-------------------------------------------------------------------------------------------|
| Momentum (Jegadeesh & Titman, 1993) | System prompt embeds: "Buy if price_change > 0.02; sell if price_change < −0.02"          |
| LLM trend assessment                | LLM may override to hold if overall market context contradicts short-term momentum signal |

### §2.4 RuleLLMSkepticalValueInvestor (simulation-bases.md §4.4)

| Theory Component               | Implementation                                                                 |
|--------------------------------|--------------------------------------------------------------------------------|
| Value anchoring (Graham, 1949) | System prompt embeds: "Buy when deviation < −0.10; sell when deviation > 0.20" |
| LLM patience logic             | LLM reasons about whether to increase position size near the lower bound       |

### §2.5 RuleLLMShortSeller (simulation-bases.md §4.5)

| Theory Component                                  | Implementation                                                                           |
|---------------------------------------------------|------------------------------------------------------------------------------------------|
| Synchronisation risk (Abreu & Brunnermeier, 2003) | System prompt embeds: "Short when deviation > 0.15; cover when deviation < −0.05"        |
| LLM squeeze management                            | LLM narrates squeeze risk and may reduce short quantity if momentum is strongly positive |

## §3 Market Mechanism

```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t)
λ = 0.01, γ = 0.005 (weak mean-reversion)
```

Prompt includes: `price`, `fundamental`, `deviation`, `price_change`, `cash`, `position`, `portfolio_value`.

## §4 RuleLLM Architecture

| Component      | Detail                                                      |
|----------------|-------------------------------------------------------------|
| Base class     | `RuleLLMInvestor` (extends `GeneralPlayer`)                 |
| Rule injection | Threshold conditions formatted into system prompt header    |
| Inference      | `LangChainAPIInference`                                     |
| Context        | `HistoryBuffer` (last 200 entries)                          |
| Output parsing | `parse_llm_response_with_thinking()` → `{action, quantity}` |
| Retry logic    | 3 attempts; fall back to hold on failure                    |

## §5 Config Reference

Config file: `DotComBubble/RuleLLM/config.yaml`

Key extras: `llm.lm_name`, `llm.generation_config`, `initial_cash`, `initial_position`; embedded rule thresholds in system prompt strings.

## §6 Running Instructions

```bash
python -m examples.DotComBubble.RuleLLM.run_dotcombubble_rulellm
```

## §7 Expected Behavior

- RuleLLM produces the most consistent bubble trajectories — rule boundaries prevent extreme LLM deviation while personas add narrative depth.
- BAI and BD should closely match Rule baseline with reduced variance versus pure LLM.
- SSR higher than LLM — ShortSeller rule boundary prevents early cover, sustaining squeeze resistance.
- WDI pattern mirrors Rule variant closely; LLM only adjusts quantities within rule-defined direction.

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
