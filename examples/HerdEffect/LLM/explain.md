# HerdEffect LLM — Implementation Explanation

## §1 Overview

| Aspect             | Detail                                                                         |
|--------------------|--------------------------------------------------------------------------------|
| Variant            | LLM                                                                            |
| Simulation         | HerdEffect                                                                     |
| Decision Mechanism | LLM-driven bid formation via LangChainAPIInference                             |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                |
| Market Broadcast   | `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, `round` |
| Price Model        | Same order-book clearing as Rule — Market agent unchanged                      |

The LLM variant replaces hard-coded `calculate_bid()` formulas with LLM-generated bid prices and quantities. Each investor has a behavioral persona in the system prompt encoding its theoretical role. The same order-book market mechanism is preserved — the LLM must still output `bid_price` and signed `quantity` for the clearing process.

## §2 Theory → Implementation Mapping

### §2.1 LLMMomentumInvestor (simulation-bases.md §4.1)

| Theory Component                 | Implementation                                                                           |
|----------------------------------|------------------------------------------------------------------------------------------|
| Shiller (1984) positive feedback | System prompt: trend-following momentum persona; `return` and `return_pct` in context    |
| Graduated conviction             | LLM can express strong signal → large quantity; weak signal → hold; not possible in Rule |
| Bid formation                    | LLM outputs `bid_price` and `quantity`; treated as order-book bid                        |
| Emergent herding                 | LLM momentum agents may exhibit higher variance in activation threshold than Rule        |

### §2.2 LLMContrarianInvestor (simulation-bases.md §4.2)

| Theory Component                        | Implementation                                                                                      |
|-----------------------------------------|-----------------------------------------------------------------------------------------------------|
| De Bondt & Thaler (1985) mean reversion | System prompt: contrarian/value investor persona                                                    |
| Fundamental reference                   | Fundamental value provided in system prompt context — not in market broadcast                       |
| Nuanced judgment                        | LLM can distinguish temporary trend vs. sustained overvaluation — more flexible than Rule threshold |
| Sell signal                             | LLM reasons about overvaluation from `price` + `return_pct` trend narrative                         |

### §2.3 LLMRiskAverseInvestor (simulation-bases.md §4.3)

| Theory Component               | Implementation                                                                       |
|--------------------------------|--------------------------------------------------------------------------------------|
| Markowitz (1952) risk aversion | System prompt: risk-averse investor; narratively responds to recent volatility       |
| Dynamic precaution             | LLM may exit earlier than Rule's variance formula in very volatile narrative context |
| Position dampening             | LLM risk-averse behavior may reduce MDD by precautionary position reduction          |

### §2.4 LLMNoiseTrader (simulation-bases.md §4.4)

| Theory Component                    | Implementation                                                                                         |
|-------------------------------------|--------------------------------------------------------------------------------------------------------|
| De Long et al. (1990) noise trading | System prompt: uninformed trader; no clear directional strategy                                        |
| Stochastic behavior                 | LLM-induced noise has different distribution from Rule's Gaussian — different cascade trigger patterns |

### §2.5 LLMAggressiveInvestor (simulation-bases.md §4.5)

| Theory Component       | Implementation                                                                 |
|------------------------|--------------------------------------------------------------------------------|
| Leveraged momentum     | System prompt: aggressive leveraged trader persona                             |
| Acceleration narrative | LLM interprets acceleration narrative from `return_pct` trend in reasoning     |
| Amplification          | LLM may generate larger quantities than Rule's ±80 cap in high-conviction runs |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3*

```
P(t+1) = P(t) + α × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Same order-book clearing as Rule variant. LLM outputs are interpreted as `(bid_price, quantity)` pairs. No `fundamental` in market broadcast — LLMContrarianInvestor must reason from system prompt context.

## §4 Variant Architecture

| Component      | Detail                                              |
|----------------|-----------------------------------------------------|
| Base class     | `BaseInvestor` (LLM subclass)                       |
| Inference      | `LangChainAPIInference`                             |
| Context        | Market broadcast + behavioral system prompt         |
| Output parsing | LLM returns `bid_price` + signed `quantity`         |
| Retry logic    | 3 retries on parse failure; fallback to neutral bid |
| Temperature    | Configurable; higher → more stochastic herding      |

## §5 Config Reference

Config file: `configs/HerdEffect/LLM/simulation.yml`

Key extras:
- `lm_name`: LLM model identifier
- `system_prompt`: behavioral persona per investor
- `fundamental` in ContrarianInvestor extras (passed to system prompt)
- Market config unchanged from Rule variant

## §6 Running Instructions

```bash
python -m examples.HerdEffect.LLM.run_herd_effect \
    -c configs/HerdEffect/LLM/simulation.yml
```

Or via Streamlit UI: select "HerdEffect" → "LLM" variant.

## §7 Expected Behavior

- **Wider variance**: EMI range wider than Rule due to LLM stochasticity — run ≥ 10 seeds for reliable estimates
- **Softer momentum**: LLM momentum agents may dampen positive feedback due to risk-aware narrative reasoning
- **Earlier contrarian**: LLMContrarianInvestor may sell sooner when narrative detects overvaluation
- **Temperature sensitivity**: Higher temperature → more frequent herding onset; lower → closer to Rule
- **Same market structure**: Order-book dynamics preserved; no fundamental in broadcast

## §8 References

See `simulation-bases.md §2` for full DOI citations.

- Shiller (1984) `doi:10.2307/2534436` — LLMMomentumInvestor behavioral basis
- De Bondt & Thaler (1985) `doi:10.1111/j.1540-6261.1985.tb05004.x` — LLMContrarianInvestor basis
- Markowitz (1952) `doi:10.1111/j.1540-6261.1952.tb01525.x` — LLMRiskAverseInvestor basis

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
