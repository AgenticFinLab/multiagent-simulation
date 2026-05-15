# EuropeanDebtCrisis LLM — Implementation Explanation

## §1 Overview

The LLM variant replaces threshold rules with persona-driven LLM reasoning for crisis decision-making. Each investor embeds a behavioral persona (panic-prone, flight-to-safety, central bank, etc.) in a system prompt. LLMs reason about crisis severity and decide on action and quantity without fixed thresholds.

| Aspect             | Detail                                               |
|--------------------|------------------------------------------------------|
| Variant            | LLM (language-model persona)                         |
| Simulation         | EuropeanDebtCrisis                                   |
| Decision Mechanism | LLM persona system prompts — no hardcoded thresholds |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                      |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round`         |

## §2 Theory → Implementation Mapping

### §2.1 LLMPeripheryBondSeller (simulation-bases.md §4.1)

| Theory Component                              | Implementation                                                                                                                             |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Self-fulfilling speculation (De Grauwe, 2011) | System prompt: "You are a foreign creditor; if you see the bond price falling significantly below fair value, panic and sell aggressively" |
| Amplifying behavior                           | LLM reasons about severity of deviation and decides quantity; may sell larger amounts than Rule at extreme deviations                      |
| Recovery reentry                              | Persona allows rebuying when LLM judges price has stabilized                                                                               |

### §2.2 LLMCreditorPanicker (simulation-bases.md §4.2)

| Theory Component                            | Implementation                                                                                            |
|---------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Sovereign-bank nexus (Acharya et al., 2014) | System prompt: "You are a creditor to peripheral banks; withdraw funding when sovereign stress is severe" |
| Cascading panic                             | LLM reasons about banking system risk; may trigger earlier or later than Rule based on narrative          |
| Contagion reasoning                         | LLM may factor in broader eurozone context from prompt                                                    |

### §2.3 LLMCoreBondBuyer (simulation-bases.md §4.3)

| Theory Component                         | Implementation                                                                       |
|------------------------------------------|--------------------------------------------------------------------------------------|
| Flight-to-quality (De Grauwe & Ji, 2012) | System prompt: "You seek safety; rotate to core bonds when periphery stress is high" |
| Counter-cyclical buying                  | LLM judges when periphery stress justifies rotation; quantity is adaptive            |
| Recovery unwinding                       | LLM persona reverses rotation when stress subsides                                   |

### §2.4 LLMECBIntervenor (simulation-bases.md §4.4)

| Theory Component                     | Implementation                                                                                                       |
|--------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Central bank backstop (Draghi, 2012) | System prompt: "You are the ECB; provide unlimited support when self-fulfilling crisis threatens eurozone stability" |
| Credible commitment                  | LLM models "whatever it takes" determination; may buy more aggressively than Rule at crisis depths                   |
| LLM market narrative                 | LLM may reason about whether the crisis is self-fulfilling vs. fundamental before intervening                        |

### §2.5 LLMHedgedFund (simulation-bases.md §4.5)

| Theory Component                              | Implementation                                                                                               |
|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------|
| Limits to arbitrage (Shleifer & Vishny, 1997) | System prompt: "You exploit spread dislocations but face capital constraints; be cautious at extreme stress" |
| Adaptive position sizing                      | LLM adjusts quantity based on perceived risk/reward; may be more conservative than Rule's symmetric 500      |
| Exit on extreme volatility                    | LLM persona may exit position during highest crisis intensity (limits-to-arbitrage behavior)                 |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Market class is imported from `Rule/players.py` (shared). All LLM investors send orders to the same Market.

## §4 Variant Architecture

| Component      | Detail                                                                    |
|----------------|---------------------------------------------------------------------------|
| Base class     | `LLMInvestor` → `GeneralPlayer`                                           |
| Inference      | `LangChainAPIInference` (3-attempt retry)                                 |
| Context        | `price`, `fundamental`, `deviation`, `cash`, `position`, `round`          |
| Output parsing | `parse_llm_response_with_thinking()` → `{"action": ..., "quantity": ...}` |
| Retry logic    | 3 attempts; falls back to hold on failure                                 |

## §5 Config Reference

Config file: `configs/EuropeanDebtCrisis/LLM/simulation.yml`

LLM config under `extras.llm`:
- `lm_name`: model identifier
- `generation_config`: temperature, max_tokens etc.

## §6 Running Instructions

```bash
python -m examples.EuropeanDebtCrisis.LLM.run_edc_llm \
    -c configs/EuropeanDebtCrisis/LLM/simulation.yml
```

## §7 Expected Behavior

- **Stochastic crisis onset**: LLM may trigger crisis at slightly different deviations each run; CDI more variable than Rule
- **ECB credibility modeling**: LLMECBIntervenor may model commitment more authentically than Rule threshold — IER variable but can exceed Rule
- **CD range**: 5–40 rounds (wider than Rule; depends on LLM crisis narrative)
- **AR range**: 0.5–2.0 (creditor panic can be more or less severe than Rule)

## §8 References

See `simulation-bases.md §2` for full DOI citations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
