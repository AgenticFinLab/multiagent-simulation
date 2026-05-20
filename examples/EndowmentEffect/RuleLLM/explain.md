# EndowmentEffect RuleLLM — Implementation Explanation

## §1 Overview

The RuleLLM variant embeds explicit numerical trading rules directly into the LLM system prompts. The LLM cannot override the encoded thresholds, but provides contextual reasoning about market conditions within the rule constraints. This hybrid approach combines the consistency of Rule-based thresholds with LLM's capacity for nuanced market narrative.

| Aspect             | Detail                                                                         |
|--------------------|--------------------------------------------------------------------------------|
| Variant            | RuleLLM (rule-embedded LLM)                                                    |
| Simulation         | EndowmentEffect                                                                |
| Decision Mechanism | Numerical thresholds embedded in system prompt; LLM reasons within constraints |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`                                                |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `cash`, `position`, `round`               |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMEndowedHolder (simulation-bases.md §4.1)

| Theory Component                          | Implementation                                                                                                       |
|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| Endowment premium (Kahneman et al., 1990) | System prompt embeds: "Sell only when deviation > endowment_premium + 0.05; otherwise hold or buy on undervaluation" |
| Sell reluctance factor                    | Rule instructs use of `sell_reluctance` parameter; LLM selects quantity within that constraint                       |
| LLM contextualisation                     | LLM reasons about narrative strength of attachment but cannot override the sell threshold                            |

### §2.2 RuleLLMStatusQuoSeller (simulation-bases.md §4.2)

| Theory Component                               | Implementation                                                                         |
|------------------------------------------------|----------------------------------------------------------------------------------------|
| Status quo bias (Samuelson & Zeckhauser, 1988) | System prompt embeds: "Sell only if deviation > status_quo_threshold; default to hold" |
| Inertia in holding decisions                   | LLM is instructed to justify inaction unless the embedded threshold is breached        |
| Buy on deep undervaluation                     | Rule exception encoded: "Buy if deviation < −0.08"                                     |

### §2.3 RuleLLMRationalArbitrageur (simulation-bases.md §4.3)

| Theory Component                             | Implementation                                                                               |
|----------------------------------------------|----------------------------------------------------------------------------------------------|
| Rational expectations benchmark (Muth, 1961) | System prompt embeds: "Buy if deviation < −arb_threshold; sell if deviation > arb_threshold" |
| Symmetric arbitrage                          | Rules enforce symmetric response; LLM reasons about market depth and timing                  |
| No endowment distortion                      | Prompt explicitly states no ownership bias; LLM confirms arbitrage logic                     |

### §2.4 RuleLLMNewBuyer (simulation-bases.md §4.4)

| Theory Component                                         | Implementation                                                                     |
|----------------------------------------------------------|------------------------------------------------------------------------------------|
| Rational WTP equals market value (Kahneman et al., 1990) | System prompt embeds: "Buy if deviation < buy_threshold; sell if deviation > 0.10" |
| No ownership premium                                     | Prompt states no prior ownership; LLM applies rule mechanically                    |
| LLM contextualisation                                    | LLM may adjust quantity within rule bounds based on confidence in the signal       |

### §2.5 RuleLLMNoiseTrader (simulation-bases.md §4.5)

| Theory Component                       | Implementation                                                                   |
|----------------------------------------|----------------------------------------------------------------------------------|
| Uninformed noise trading (Black, 1986) | System prompt embeds trade_probability threshold; LLM randomly selects direction |
| Stochastic activation                  | Prompt instructs: "Trade with probability trade_probability; direction random"   |
| Portfolio constraint                   | Rule limits quantity to affordable/available; LLM selects within that range      |

## §3 Market Mechanism

*Formula source: simulation-bases.md §3.1*

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Market class is imported from `Rule/players.py` (shared). All RuleLLM investors submit orders to the same Market.

## §4 Variant Architecture

| Component        | Detail                                                                              |
|------------------|-------------------------------------------------------------------------------------|
| Base class       | `RuleLLMInvestor` → `GeneralPlayer`                                                 |
| Inference        | `LangChainAPIInference` (3-attempt retry)                                           |
| Context          | `price`, `fundamental`, `deviation`, `cash`, `position`, `portfolio_value`, `round` |
| Output parsing   | `parse_llm_response_with_thinking()` → `{"action": ..., "bid_price": ..., "quantity": ..., "reasoning": ..., "analysis": ...}` |
| Rule enforcement | Thresholds in system prompt; LLM cannot violate without failing retry               |

## §5 Config Reference

Config file: `configs/EndowmentEffect/RuleLLM/simulation.yml`

All Rule parameters (endowment_premium, sell_reluctance, etc.) plus LLM config under `extras.llm`:
- `lm_name`: model identifier
- `generation_config`: temperature, max_tokens etc.

## §6 Running Instructions

```bash
python -m examples.EndowmentEffect.RuleLLM.run_endowment_effect \
    -c configs/EndowmentEffect/RuleLLM/simulation.yml
```

## §7 Expected Behavior

- **More consistent than pure LLM**: Embedded thresholds prevent LLM from overriding key rules; MAD closer to Rule baseline
- **More nuanced than pure Rule**: LLM selects quantities more adaptively within threshold constraints
- **MAD target**: 0.03–0.12 (similar to Rule; see analysis-bases.md §2.2)
- **VSR**: Similar to Rule (0.40–0.65); RuleLLM EndowedHolder holds due to encoded threshold

## §8 References

See `simulation-bases.md §2` for full DOI citations for all theoretical foundations.

## §9 Variant Comparison

See `simulation-bases.md §9` for Rule / LLM / RuleLLM / Rag comparison table.
